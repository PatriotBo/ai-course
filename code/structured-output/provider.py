from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class ProviderConfig:
    provider: str
    model: str
    base_url: str
    api_key: str
    temperature: float = 0.1
    max_tokens: int = 1000
    response_mode: str = "text"

    @classmethod
    def from_env(cls) -> "ProviderConfig":
        return cls(
            provider=os.getenv("LLM_PROVIDER", "openai_compatible").strip(),
            model=require_env("LLM_MODEL"),
            base_url=require_env("LLM_BASE_URL"),
            api_key=require_env("LLM_API_KEY"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
            response_mode=os.getenv("LLM_RESPONSE_MODE", "text").strip(),
        )


class OpenAICompatibleProvider:
    """真实 OpenAI-compatible Provider；不内置 mock/dry-run 路径。"""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def generate(self, messages: list[dict[str, str]]) -> str:
        request: dict[str, object] = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }

        # json_object 只作为兼容 Provider 的可选提示；最终仍必须经过 Pydantic 校验。
        if self.config.response_mode == "json_object":
            request["response_format"] = {"type": "json_object"}
        elif self.config.response_mode != "text":
            raise ValueError("LLM_RESPONSE_MODE must be text or json_object")

        response = self.client.chat.completions.create(**request)
        return response.choices[0].message.content or ""
