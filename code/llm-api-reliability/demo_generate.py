from __future__ import annotations

import json

from dotenv import load_dotenv

from reliable_client import ReliableLLMClient, load_default_request


def main() -> None:
    """使用真实 provider 运行一次可靠性封装后的 LLM 调用。

    运行前请先复制 `.env.example` 为 `.env`，并填入真实 provider / model / base_url / api_key。
    """
    load_dotenv()
    client = ReliableLLMClient()
    request = load_default_request("用三句话解释 LLM API 为什么需要 timeout、retry 和 cost log。")
    result = client.generate(request)

    print("=== LLM Result ===")
    print(result.text)
    print("\n=== Metadata ===")
    print(json.dumps({
        "request_id": result.request_id,
        "provider": result.provider,
        "model": result.model,
        "attempt_count": result.attempt_count,
        "latency_ms": result.latency_ms,
        "usage": result.usage.model_dump(),
        "cost": result.cost.model_dump(),
        "log_path": client.log_path,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
