from __future__ import annotations

import json

from dotenv import load_dotenv

from models import IncidentSummary
from provider import OpenAICompatibleProvider, ProviderConfig
from structured_output import StructuredOutputError, generate_structured


def build_messages(incident_context: str) -> list[dict[str, str]]:
    schema = json.dumps(IncidentSummary.model_json_schema(), ensure_ascii=False)
    return [
        {
            "role": "system",
            "content": (
                "你是 SRE 事故摘要助手。只能使用输入材料中的事实，不得猜测。"
                "返回一个 JSON object，不要输出 Markdown 或解释。"
                "材料不足时 status 必须为 insufficient_context，未知值写 unknown。\n"
                f"JSON Schema:\n{schema}"
            ),
        },
        {
            "role": "user",
            "content": f"请结构化下面的事故材料：\n<context>\n{incident_context}\n</context>",
        },
    ]


def main() -> None:
    load_dotenv()
    config = ProviderConfig.from_env()
    provider = OpenAICompatibleProvider(config)
    messages = build_messages(
        "10:02 支付 API P99 延迟升至 8 秒；10:05 告警触发；"
        "10:12 回滚连接池参数；10:18 延迟恢复。"
        "材料未说明受影响用户数，也不能确认连接池参数是唯一根因。"
    )

    try:
        result = generate_structured(
            messages=messages,
            provider=provider.generate,
            max_repairs=1,
        )
    except StructuredOutputError as error:
        print(json.dumps({
            "status": "failed",
            "provider": config.provider,
            "model": config.model,
            "error": str(error),
            "issues": error.issues,
        }, ensure_ascii=False, indent=2))
        raise SystemExit(1) from error

    print(json.dumps({
        "status": "ok",
        "provider": config.provider,
        "model": config.model,
        "attempts": result.attempts,
        "repaired": result.repaired,
        "data": result.value.model_dump(),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
