from __future__ import annotations

import json
import os
import random
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Literal

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field


Role = Literal["system", "user", "assistant", "tool"]
RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
NON_RETRYABLE_STATUS_CODES = {400, 401, 403, 404, 422}
DEFAULT_LOG_PATH = Path(__file__).with_name("logs") / "llm_reliability.jsonl"

DEFAULT_BASE_URLS = {
    "openai": "https://api.openai.com/v1",
    "openai_compatible": "https://api.openai.com/v1",
    "glm": "https://open.bigmodel.cn/api/paas/v4/",
    "hunyuan": "https://api.hunyuan.cloud.tencent.com/v1",
}

DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "openai_compatible": "gpt-4o-mini",
    "glm": "glm-5.2",
    "hunyuan": "hunyuan-turbos-latest",
}


def env_first(*names: str, default: str | None = None) -> str | None:
    """按顺序读取环境变量，返回第一个非空值。"""
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return default


class Message(BaseModel):
    """Chat Completions 标准消息。"""

    role: Role
    content: str


class LLMRequest(BaseModel):
    """业务层提交给可靠 LLM Client 的标准请求。"""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model: str
    messages: list[Message]
    temperature: float = 0.2
    max_tokens: int = 512


class Usage(BaseModel):
    """统一后的 token usage 字段，避免业务层依赖 provider 原始字段名。"""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0


class CostEstimate(BaseModel):
    """一次调用的粗略成本估算。"""

    input_cost: float = 0
    output_cost: float = 0
    total_cost: float = 0
    currency: str = "CNY"


class LLMResult(BaseModel):
    request_id: str
    provider: str
    model: str
    text: str
    usage: Usage
    cost: CostEstimate
    attempt_count: int
    latency_ms: int
    raw: dict[str, Any] = Field(default_factory=dict)


class ProviderError(RuntimeError):
    """封装 provider 调用错误，保留是否可重试的信息。"""

    def __init__(self, message: str, *, retryable: bool, error_type: str, http_status: int | None = None) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.error_type = error_type
        self.http_status = http_status


@dataclass(frozen=True)
class RetryPolicy:
    """重试策略。

    max_retries 表示失败后最多再尝试几次，不包含第一次调用。
    base_delay_seconds 和 max_delay_seconds 控制指数退避等待区间。
    jitter_ratio 用于打散并发重试，避免大量请求同一时间再次打到 provider。
    """

    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 20.0
    jitter_ratio: float = 0.25


@dataclass
class ReliableLLMClient:
    """带 timeout、错误分类、有限重试和成本估算的 LLM Client。"""

    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "glm"))
    api_key: str | None = field(
        default_factory=lambda: env_first("LLM_API_KEY", "OPENAI_API_KEY", "ZAI_API_KEY", "HUNYUAN_API_KEY")
    )
    base_url: str | None = field(default_factory=lambda: env_first("LLM_BASE_URL", "OPENAI_BASE_URL"))
    timeout_seconds: float = field(default_factory=lambda: float(os.getenv("LLM_TIMEOUT_SECONDS", "30")))
    log_path: str = field(default_factory=lambda: os.getenv("LLM_LOG_PATH", str(DEFAULT_LOG_PATH)))
    input_price_per_1m: Decimal = field(default_factory=lambda: Decimal(os.getenv("LLM_INPUT_PRICE_PER_1M", "0")))
    output_price_per_1m: Decimal = field(default_factory=lambda: Decimal(os.getenv("LLM_OUTPUT_PRICE_PER_1M", "0")))
    retry_policy: RetryPolicy = field(default_factory=lambda: RetryPolicy(
        max_retries=int(os.getenv("LLM_MAX_RETRIES", "3")),
        base_delay_seconds=float(os.getenv("LLM_BASE_DELAY_SECONDS", "1")),
        max_delay_seconds=float(os.getenv("LLM_MAX_DELAY_SECONDS", "20")),
    ))

    def __post_init__(self) -> None:
        self.provider = self.provider.lower().strip()
        if not self.base_url:
            self.base_url = DEFAULT_BASE_URLS.get(self.provider, DEFAULT_BASE_URLS["openai_compatible"])

    def generate(self, request: LLMRequest) -> LLMResult:
        """执行一次模型调用。

        这层负责 retry loop；真正的 HTTP 请求放在 _call_provider_once，方便分离职责。
        """
        started = time.perf_counter()
        errors: list[dict[str, Any]] = []
        max_attempts = self.retry_policy.max_retries + 1

        for attempt in range(1, max_attempts + 1):
            try:
                result = self._call_provider_once(request, attempt, started)
                self._write_log(self._build_success_log(request, result, errors))
                return result
            except ProviderError as exc:
                errors.append(self._error_to_dict(exc, attempt))
                if not exc.retryable or attempt >= max_attempts:
                    latency_ms = int((time.perf_counter() - started) * 1000)
                    self._write_log(self._build_error_log(request, latency_ms, attempt, errors, exc))
                    raise
                self._sleep_before_retry(attempt)

        raise RuntimeError("unreachable retry loop state")

    def _call_provider_once(self, request: LLMRequest, attempt: int, started: float) -> LLMResult:
        """只调用一次 provider，不在这里做重试。"""
        if not self.api_key:
            raise ProviderError("LLM_API_KEY is required for real provider calls", retryable=False, error_type="missing_api_key")

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
        url = f"{self.base_url.rstrip('/')}/chat/completions"

        try:
            with httpx.Client(timeout=self.timeout_seconds) as client:
                response = client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderError(str(exc), retryable=True, error_type="timeout") from exc
        except httpx.TransportError as exc:
            raise ProviderError(str(exc), retryable=True, error_type="transport_error") from exc
        except httpx.HTTPStatusError as exc:
            raise self._classify_http_error(exc) from exc

        data = response.json()
        text = data["choices"][0]["message"].get("content") or ""
        usage = self._normalize_usage(data.get("usage", {}))
        cost = self._estimate_cost(usage)
        latency_ms = int((time.perf_counter() - started) * 1000)

        return LLMResult(
            request_id=request.request_id,
            provider=self.provider,
            model=request.model,
            text=text,
            usage=usage,
            cost=cost,
            attempt_count=attempt,
            latency_ms=latency_ms,
            raw=data,
        )

    def _classify_http_error(self, exc: httpx.HTTPStatusError) -> ProviderError:
        """把 HTTP 状态码转换成可操作的错误类型。"""
        status = exc.response.status_code
        retryable = status in RETRYABLE_STATUS_CODES
        if status == 429:
            error_type = "rate_limit"
        elif status in {500, 502, 503, 504}:
            error_type = "provider_5xx"
        elif status in NON_RETRYABLE_STATUS_CODES:
            error_type = "non_retryable_http_error"
        else:
            error_type = "http_error"
        return ProviderError(str(exc), retryable=retryable, error_type=error_type, http_status=status)

    def _sleep_before_retry(self, failed_attempt: int) -> None:
        """指数退避 + jitter，避免大量请求同时重试。"""
        base_delay = min(
            self.retry_policy.base_delay_seconds * (2 ** (failed_attempt - 1)),
            self.retry_policy.max_delay_seconds,
        )
        jitter = random.uniform(0, base_delay * self.retry_policy.jitter_ratio)
        time.sleep(base_delay + jitter)

    def _normalize_usage(self, usage: dict[str, Any]) -> Usage:
        """兼容 OpenAI-compatible usage 字段。"""
        input_tokens = int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("completion_tokens") or usage.get("output_tokens") or 0)
        total_tokens = int(usage.get("total_tokens") or input_tokens + output_tokens)
        return Usage(input_tokens=input_tokens, output_tokens=output_tokens, total_tokens=total_tokens)

    def _estimate_cost(self, usage: Usage) -> CostEstimate:
        """按每 1M tokens 单价估算成本。"""
        input_cost = Decimal(usage.input_tokens) / Decimal(1_000_000) * self.input_price_per_1m
        output_cost = Decimal(usage.output_tokens) / Decimal(1_000_000) * self.output_price_per_1m
        total_cost = input_cost + output_cost
        return CostEstimate(
            input_cost=float(input_cost),
            output_cost=float(output_cost),
            total_cost=float(total_cost),
        )

    def _write_log(self, entry: dict[str, Any]) -> None:
        log_file = Path(self.log_path).expanduser()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

    def _base_log_entry(self, request: LLMRequest) -> dict[str, Any]:
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
                "max_retries": self.retry_policy.max_retries,
            },
            "input": {"messages": [message.model_dump() for message in request.messages]},
        }

    def _build_success_log(self, request: LLMRequest, result: LLMResult, errors: list[dict[str, Any]]) -> dict[str, Any]:
        entry = self._base_log_entry(request)
        entry.update({
            "status": "success",
            "attempt_count": result.attempt_count,
            "retry_errors": errors,
            "latency_ms": result.latency_ms,
            "usage": result.usage.model_dump(),
            "cost": result.cost.model_dump(),
            "output": {"text": result.text, "length": len(result.text)},
            "error": None,
        })
        return entry

    def _build_error_log(
        self,
        request: LLMRequest,
        latency_ms: int,
        attempt_count: int,
        errors: list[dict[str, Any]],
        final_error: ProviderError,
    ) -> dict[str, Any]:
        entry = self._base_log_entry(request)
        entry.update({
            "status": "error",
            "attempt_count": attempt_count,
            "retry_errors": errors,
            "latency_ms": latency_ms,
            "usage": None,
            "cost": None,
            "output": None,
            "error": self._error_to_dict(final_error, attempt_count),
        })
        return entry

    @staticmethod
    def _error_to_dict(exc: ProviderError, attempt: int) -> dict[str, Any]:
        return {
            "attempt": attempt,
            "type": exc.error_type,
            "message": str(exc),
            "retryable": exc.retryable,
            "http_status": exc.http_status,
        }


def load_default_request(user_input: str) -> LLMRequest:
    """从 .env 构造一次真实 provider 调用请求。"""
    load_dotenv()
    provider = os.getenv("LLM_PROVIDER", "glm").lower().strip()
    model = env_first("LLM_MODEL", "OPENAI_MODEL", "ZAI_MODEL", "HUNYUAN_MODEL", default=DEFAULT_MODELS.get(provider, "glm-5.2"))
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))
    max_tokens = int(os.getenv("LLM_MAX_TOKENS", "512"))

    return LLMRequest(
        model=model or DEFAULT_MODELS.get(provider, "glm-5.2"),
        temperature=temperature,
        max_tokens=max_tokens,
        messages=[
            Message(role="system", content="你是一个严谨的 AI 工程课程助教，回答要简洁、准确、可执行。"),
            Message(role="user", content=user_input),
        ],
    )
