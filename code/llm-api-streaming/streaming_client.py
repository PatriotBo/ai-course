from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator, Literal

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant", "tool"]
OPENAI_COMPATIBLE_PROVIDERS = {"openai", "openai_compatible", "glm", "hunyuan"}

DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "openai_compatible": "https://api.openai.com/v1",
    "glm": "https://open.bigmodel.cn/api/paas/v4/",
    "hunyuan": "https://api.hunyuan.cloud.tencent.com/v1",
}

DEFAULT_LOG_PATH = Path(__file__).with_name("logs") / "llm_streams.jsonl"


def env_first(*names: str, default: str | None = None) -> str | None:
    """按顺序读取环境变量，返回第一个非空值。

    课程示例统一优先使用 LLM_* 配置，同时兼容 OPENAI_*、ZAI_*、HUNYUAN_*。
    这样切 GLM / 腾讯混元 / OpenAI-compatible 服务时，只需要换配置，不改代码。
    """
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


class Message(BaseModel):
    """传给 Chat Completions 接口的一条消息。"""

    role: Role
    content: str


class StreamRequest(BaseModel):
    """业务层提交给 Streaming Client 的标准请求。

    stream=True 是供应商协议细节，不暴露给业务层；业务层只关心模型、messages 和参数。
    """

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str
    messages: list[Message]
    temperature: float = 0.2
    max_tokens: int = 512


class StreamChunk(BaseModel):
    """一次流式响应中的增量片段。

    delta 是本次新增文本；done 表示流结束。真实前端通常会不断把 delta 追加到页面上。
    """

    request_id: str
    delta: str = ""
    done: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


@dataclass
class LLMStreamingClient:
    """最小 LLM Streaming Client。

    这个类承担 provider adapter 的职责：
    - mock provider：本地演示，不调用外部模型；
    - OpenAI-compatible provider：OpenAI / GLM / 腾讯混元等走 /chat/completions + stream=True。
    """

    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "mock"))
    api_key: str | None = field(
        default_factory=lambda: env_first("LLM_API_KEY", "OPENAI_API_KEY", "ZAI_API_KEY", "HUNYUAN_API_KEY")
    )
    base_url: str | None = field(default_factory=lambda: env_first("LLM_BASE_URL", "OPENAI_BASE_URL"))
    timeout_seconds: float = field(default_factory=lambda: float(os.getenv("LLM_TIMEOUT_SECONDS", "60")))
    log_path: str = field(default_factory=lambda: os.getenv("LLM_STREAM_LOG_PATH", str(DEFAULT_LOG_PATH)))

    def __post_init__(self) -> None:
        self.provider = self.provider.lower().strip()
        if not self.base_url:
            self.base_url = DEFAULT_BASE_URLS.get(self.provider, DEFAULT_BASE_URLS["openai_compatible"])

    def stream(self, request: StreamRequest) -> Iterator[StreamChunk]:
        """生成一次流式响应，并在结束或失败时追加结构化日志。

        这里用 generator/yield 暴露流式片段。调用方可以一边接收一边返回给浏览器，
        不需要等完整回答生成完。
        """
        started = time.perf_counter()
        output_parts: list[str] = []

        try:
            source = self._mock_stream(request) if self.provider == "mock" else self._openai_compatible_stream(request)
            for chunk in source:
                output_parts.append(chunk.delta)
                yield chunk
        except Exception as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            self._write_stream_log(self._build_error_log(request, latency_ms, "".join(output_parts), exc))
            raise

        latency_ms = int((time.perf_counter() - started) * 1000)
        self._write_stream_log(self._build_success_log(request, latency_ms, "".join(output_parts)))
        yield StreamChunk(request_id=request.request_id, done=True)

    def _mock_stream(self, request: StreamRequest) -> Iterator[StreamChunk]:
        """本地 mock 流。

        真实模型会逐 token / chunk 返回；mock 用固定短句拆分，方便学习 SSE 链路。
        """
        user_messages = [msg.content for msg in request.messages if msg.role == "user"]
        last_user = user_messages[-1] if user_messages else ""
        text = (
            "[mock stream] 已收到请求。"
            f"模型={request.model}，temperature={request.temperature}。"
            f"用户最后输入：{last_user[:80]}"
        )
        for part in self._split_text(text, size=12):
            yield StreamChunk(request_id=request.request_id, delta=part, raw={"mock": True})

    def _openai_compatible_stream(self, request: StreamRequest) -> Iterator[StreamChunk]:
        """调用 OpenAI-compatible streaming 接口。

        OpenAI / GLM / 腾讯混元都可以走这条路径，前提是供应商兼容 /chat/completions stream=True。
        """
        if not self.api_key:
            raise RuntimeError("LLM_API_KEY is required when LLM_PROVIDER is openai/openai_compatible/glm/hunyuan")

        payload = {
            "model": request.model,
            "messages": [message.model_dump() for message in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self.base_url.rstrip('/')}/chat/completions"

        # httpx.Client.stream 会边接收响应边迭代，不会等完整 body 下载完。
        with httpx.Client(timeout=self.timeout_seconds) as client:
            with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line or not line.startswith("data:"):
                        continue

                    data = line.removeprefix("data:").strip()
                    if data == "[DONE]":
                        break

                    event = json.loads(data)
                    choices = event.get("choices") or []
                    if not choices:
                        continue

                    delta = choices[0].get("delta", {}).get("content") or ""
                    if delta:
                        yield StreamChunk(request_id=request.request_id, delta=delta, raw=event)

    def _write_stream_log(self, entry: dict[str, Any]) -> None:
        """以 JSON Lines 格式追加写入流式调用日志。"""
        log_file = Path(self.log_path).expanduser()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

    def _base_log_entry(self, request: StreamRequest, latency_ms: int, output_text: str) -> dict[str, Any]:
        """构造流式调用日志公共字段。不要记录 api_key。"""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": request.request_id,
            "provider": self.provider,
            "model": request.model,
            "base_url": self.base_url,
            "stream": True,
            "parameters": {
                "temperature": request.temperature,
                "max_tokens": request.max_tokens,
                "timeout_seconds": self.timeout_seconds,
            },
            "input": {"messages": [message.model_dump() for message in request.messages]},
            "output": {"text": output_text, "length": len(output_text)},
            "latency_ms": latency_ms,
        }

    def _build_success_log(self, request: StreamRequest, latency_ms: int, output_text: str) -> dict[str, Any]:
        entry = self._base_log_entry(request, latency_ms, output_text)
        entry.update({"status": "success", "error": None})
        return entry

    def _build_error_log(self, request: StreamRequest, latency_ms: int, output_text: str, exc: Exception) -> dict[str, Any]:
        entry = self._base_log_entry(request, latency_ms, output_text)
        entry.update({
            "status": "error",
            "error": {"type": exc.__class__.__name__, "message": str(exc)},
        })
        return entry

    @staticmethod
    def _split_text(text: str, size: int) -> list[str]:
        """把 mock 文本切成固定长度片段，模拟模型流式输出。"""
        return [text[index:index + size] for index in range(0, len(text), size)]


def load_default_stream_request(user_input: str) -> StreamRequest:
    """从 .env 读取默认模型参数，并构造一个流式请求。"""
    load_dotenv()
    model = env_first("LLM_MODEL", "OPENAI_MODEL", "ZAI_MODEL", "HUNYUAN_MODEL", default="mock-stream-model")
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "512"))

    return StreamRequest(
        model=model or "mock-stream-model",
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            Message(role="system", content="你是一个严谨的 AI 工程课程助教，回答要分步、准确、可执行。"),
            Message(role="user", content=user_input),
        ],
    )
