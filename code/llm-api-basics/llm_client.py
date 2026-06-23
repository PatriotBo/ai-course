from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field


# OpenAI Chat Completions 的常见 role。
# Literal 会把 role 限制在这几个字符串里，写错时编辑器/类型检查器更容易发现。
Role = Literal["system", "user", "assistant", "tool"]

# 这些 provider 走同一套 OpenAI-compatible 协议：POST /chat/completions。
# GLM 和腾讯混元都支持这种协议，所以只需要换 provider/model/base_url/api_key。
OPENAI_COMPATIBLE_PROVIDERS = {"openai", "openai_compatible", "glm", "hunyuan"}

# 国内常用 OpenAI-compatible base_url 默认值。
# 仍然建议生产环境显式配置 LLM_BASE_URL，避免供应商文档变化导致隐式行为不清楚。
DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "openai_compatible": "https://api.openai.com/v1",
    "glm": "https://open.bigmodel.cn/api/paas/v4/",
    "hunyuan": "https://api.hunyuan.cloud.tencent.com/v1",
}

DEFAULT_LOG_PATH = Path(__file__).with_name("logs") / "llm_calls.jsonl"


def env_first(*names: str, default: str | None = None) -> str | None:
    """按顺序读取环境变量，返回第一个非空值。

    这样既能使用统一变量 LLM_API_KEY，也兼容供应商自己的变量，
    例如 ZAI_API_KEY / HUNYUAN_API_KEY / OPENAI_API_KEY。
    """
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


class Message(BaseModel):
    """传给模型的一条消息。

    system/user/assistant/tool 的职责不同，Lesson 3 的讲义里已经展开：
    - system：角色、边界、输出要求；
    - user：用户目标和输入；
    - assistant：历史模型回答；
    - tool：工具执行结果。
    """

    role: Role
    content: str


class LLMRequest(BaseModel):
    """业务层提交给 LLM Client 的标准请求。

    这里先保持最小字段。后续课程会继续加入 prompt_version、trace_id、
    response_format、stream、tools 等生产级字段。
    """

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str
    messages: list[Message]
    temperature: float = 0.2
    max_tokens: int = 512


class LLMResult(BaseModel):
    """LLM Client 返回给业务层的标准结果。

    不直接把供应商原始响应散落到业务代码里，是为了后续统一做日志、
    成本统计、错误治理和供应商切换。
    """

    request_id: str
    provider: str
    model: str
    text: str
    latency_ms: int
    usage: dict[str, Any] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)


@dataclass
class LLMClient:
    """最小 LLM Client。

    设计目标：业务代码只依赖 LLMClient.generate，不直接依赖 OpenAI、GLM、
    混元等供应商 SDK。这样后续要换模型、加重试、加日志、加流式输出时，
    修改点集中在这个网关层。
    """

    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "mock"))
    api_key: str | None = field(
        default_factory=lambda: env_first("LLM_API_KEY", "OPENAI_API_KEY", "ZAI_API_KEY", "HUNYUAN_API_KEY")
    )
    base_url: str | None = field(default_factory=lambda: env_first("LLM_BASE_URL", "OPENAI_BASE_URL"))
    timeout_seconds: float = field(default_factory=lambda: float(os.getenv("LLM_TIMEOUT_SECONDS", "30")))
    log_path: str = field(default_factory=lambda: os.getenv("LLM_LOG_PATH", str(DEFAULT_LOG_PATH)))

    def __post_init__(self) -> None:
        self.provider = self.provider.lower().strip()
        if not self.base_url:
            self.base_url = DEFAULT_BASE_URLS.get(self.provider, DEFAULT_BASE_URLS["openai_compatible"])

    def generate(self, request: LLMRequest) -> LLMResult:
        """生成一次模型回复，并把调用过程追加写入结构化日志。

        started 用单调时钟记录耗时，避免系统时间调整影响 latency 计算。
        这里记录的是学习用明文日志；生产环境应对 messages/output 做脱敏或采样。
        """
        started = time.perf_counter()

        try:
            if self.provider == "mock":
                result = self._mock_generate(request, started)
            else:
                result = self._openai_compatible_generate(request, started)
        except Exception as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            self._write_call_log(self._build_error_log(request, latency_ms, exc))
            raise

        self._write_call_log(self._build_success_log(request, result))
        return result

    def _write_call_log(self, entry: dict[str, Any]) -> None:
        """以 JSON Lines 格式追加模型调用日志。

        JSONL 的特点是一行一个 JSON 对象，方便 tail、grep，也方便后续导入日志系统。
        """
        log_file = Path(self.log_path).expanduser()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

    def _base_log_entry(self, request: LLMRequest, latency_ms: int) -> dict[str, Any]:
        """构造成功/失败日志的公共字段。不要记录 api_key。"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request.request_id,
            "provider": self.provider,
            "model": request.model,
            "base_url": self.base_url,
            "parameters": {
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "timeout_seconds": self.timeout_seconds,
            },
            "input": {
                "messages": [message.model_dump() for message in request.messages],
            },
            "latency_ms": latency_ms,
        }

    def _build_success_log(self, request: LLMRequest, result: LLMResult) -> dict[str, Any]:
        """构造一次成功模型调用的结构化日志。"""
        entry = self._base_log_entry(request, result.latency_ms)
        entry.update({
            "status": "success",
            "output": {
                "text": result.text,
                "usage": result.usage,
                "finish_reason": self._extract_finish_reason(result.raw),
            },
            "error": None,
        })
        return entry

    def _build_error_log(self, request: LLMRequest, latency_ms: int, exc: Exception) -> dict[str, Any]:
        """构造一次失败模型调用的结构化日志。"""
        entry = self._base_log_entry(request, latency_ms)
        entry.update({
            "status": "error",
            "output": None,
            "error": {
                "type": exc.__class__.__name__,
                "message": str(exc),
            },
        })
        return entry

    @staticmethod
    def _extract_finish_reason(raw: dict[str, Any]) -> str | None:
        """从 OpenAI-compatible 原始响应里提取结束原因。mock 响应可能没有该字段。"""
        choices = raw.get("choices")
        if not choices:
            return None
        first_choice = choices[0]
        if isinstance(first_choice, dict):
            return first_choice.get("finish_reason")
        return None

    def _mock_generate(self, request: LLMRequest, started: float) -> LLMResult:
        """本地 mock provider。

        mock 不调用外部 API，不消耗 token 和费用，适合学习、测试、CI。
        """
        user_messages = [msg.content for msg in request.messages if msg.role == "user"]
        last_user = user_messages[-1] if user_messages else ""
        text = (
            "[mock response] 我已经收到你的请求。"
            f" 本次模型={request.model}, temperature={request.temperature}."
            f" 用户最后输入：{last_user[:80]}"
        )
        latency_ms = int((time.perf_counter() - started) * 1000)
        return LLMResult(
            request_id=request.request_id,
            provider="mock",
            model=request.model,
            text=text,
            latency_ms=latency_ms,
            usage={"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            raw={"mock": True},
        )

    def _openai_compatible_generate(self, request: LLMRequest, started: float) -> LLMResult:
        """调用 OpenAI-compatible /chat/completions 接口。

        OpenAI、GLM、腾讯混元都可以走这条路径。差异通过环境变量配置：
        LLM_PROVIDER、LLM_MODEL、LLM_BASE_URL、LLM_API_KEY。
        """
        if not self.api_key:
            raise RuntimeError(
                "LLM_API_KEY is required when LLM_PROVIDER is openai/openai_compatible/glm/hunyuan"
            )

        payload = {
            "model": request.model,
            "messages": [message.model_dump() for message in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # httpx.Client 用 with 管理连接生命周期，退出 with 时会自动释放连接资源。
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(f"{self.base_url.rstrip('/')}/chat/completions", json=payload, headers=headers)
            # 非 2xx 状态会抛出 HTTPStatusError。后续 Lesson 5 会在这里加 retry/fallback。
            response.raise_for_status()
            data = response.json()

        latency_ms = int((time.perf_counter() - started) * 1000)
        text = data["choices"][0]["message"]["reasoning_content"]
        usage = data.get("usage", {})

        return LLMResult(
            request_id=request.request_id,
            provider=self.provider,
            model=request.model,
            text=text,
            latency_ms=latency_ms,
            usage=usage,
            raw=data,
        )


def load_default_request(user_input: str) -> LLMRequest:
    """从 .env 读取默认模型参数，并构造一个最小请求。"""
    load_dotenv()
    model = env_first("LLM_MODEL", "OPENAI_MODEL", "ZAI_MODEL", "HUNYUAN_MODEL", default="mock-model")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "512"))

    return LLMRequest(
        model=model or "mock-model",
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            Message(role="system", content="你是一个严谨的 AI 工程课程助教，回答要简洁、结构化、可执行。"),
            Message(role="user", content=user_input),
        ],
    )
