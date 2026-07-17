from __future__ import annotations

import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from prompt_template import INCIDENT_SUMMARY_PROMPT


def require_env(name: str) -> str:
    """读取必需环境变量；缺失时在发起网络请求前失败。"""
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> None:
    load_dotenv()

    provider = os.getenv("LLM_PROVIDER", "openai_compatible").strip()
    model = require_env("LLM_MODEL")
    base_url = require_env("LLM_BASE_URL")
    api_key = require_env("LLM_API_KEY")

    rendered = INCIDENT_SUMMARY_PROMPT.render({
        "audience": "后端研发和 SRE 团队",
        "incident_context": (
            "10:02 支付 API P99 延迟升至 8 秒；10:05 告警触发；"
            "10:12 回滚刚上线的连接池参数；10:18 延迟恢复。"
            "当前材料未提供受影响用户数，也没有明确证明连接池参数就是唯一根因。"
        ),
    })

    # OpenAI Python SDK 支持自定义 base_url，可连接 GLM、腾讯混元等兼容服务。
    client = OpenAI(api_key=api_key, base_url=base_url)
    response = client.chat.completions.create(
        model=model,
        messages=rendered.messages,
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "800")),
    )

    text = response.choices[0].message.content or ""
    usage = response.usage.model_dump() if response.usage else {}

    print("=== Prompt Metadata ===")
    print(json.dumps({
        "provider": provider,
        "model": model,
        "prompt_key": rendered.prompt_key,
        "prompt_version": rendered.prompt_version,
        "usage": usage,
    }, ensure_ascii=False, indent=2))
    print("\n=== Model Output ===")
    print(text)


if __name__ == "__main__":
    main()
