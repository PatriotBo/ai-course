from __future__ import annotations

import json

from dotenv import load_dotenv

from llm_client import LLMClient, load_default_request


def main() -> None:
    # 读取 .env 文件。没有 .env 时也能运行，默认走 mock provider。
    load_dotenv()

    # 构造一次标准 LLMRequest。真实业务里这里通常来自 Prompt Builder / Context Builder。
    request = load_default_request("用三句话解释 LLM API 为什么需要封装成 LLM Client。")

    # LLMClient 会根据环境变量选择 mock / OpenAI / GLM / 混元等 provider。
    client = LLMClient()
    result = client.generate(request)

    print("=== LLM Result ===")
    print(result.text)
    print("\n=== Metadata ===")
    print(json.dumps({
        "request_id": result.request_id,
        "provider": result.provider,
        "model": result.model,
        "latency_ms": result.latency_ms,
        "usage": result.usage,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
