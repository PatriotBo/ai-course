from __future__ import annotations

import os
import time
import uuid
from dataclasses import dataclass, field
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

    def __post_init__(self) -> None:
        self.provider = self.provider.lower().strip()
        if not self.base_url:
            self.base_url = DEFAULT_BASE_URLS.get(self.provider, DEFAULT_BASE_URLS["openai_compatible"])

    def generate(self, request: LLMRequest) -> LLMResult:
        """生成一次模型回复。

        started 用单调时钟记录耗时，避免系统时间调整影响 latency 计算。
        """
        started = time.perf_counter()

        if self.provider == "mock":
            return self._mock_generate(request, started)

        if self.provider in OPENAI_COMPATIBLE_PROVIDERS:
            return self._openai_compatible_generate(request, started)

        raise ValueError(f"Unsupported LLM_PROVIDER: {self.provider}")

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
        text = data["choices"][0]["message"]["content"]
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
