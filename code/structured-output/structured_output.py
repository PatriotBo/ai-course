from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, TypeAlias

from pydantic import ValidationError

from models import IncidentSummary

Message: TypeAlias = dict[str, str]
Provider: TypeAlias = Callable[[list[Message]], str]


class StructuredOutputError(ValueError):
    """模型输出无法解析、无法通过 Schema 或违反业务规则。"""

    def __init__(self, message: str, *, issues: list[str] | None = None) -> None:
        super().__init__(message)
        self.issues = issues or []


@dataclass(frozen=True)
class StructuredResult:
    value: IncidentSummary
    attempts: int
    repaired: bool


def extract_json_object(raw: str) -> str:
    """从模型文本中提取唯一、括号平衡的 JSON object。

    这里不用正则直接匹配 `{.*}`，因为字符串内部也可能包含花括号。
    """

    text = raw.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    spans: list[tuple[int, int]] = []
    depth = 0
    start: int | None = None
    in_string = False
    escaped = False

    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}":
            if depth == 0:
                raise StructuredOutputError("JSON object has an unmatched closing brace")
            depth -= 1
            if depth == 0 and start is not None:
                spans.append((start, index + 1))
                start = None

    if depth != 0 or in_string:
        raise StructuredOutputError("JSON object is incomplete")
    if len(spans) != 1:
        raise StructuredOutputError("expected exactly one JSON object")

    begin, end = spans[0]
    return text[begin:end]


def _format_validation_issues(error: ValidationError) -> list[str]:
    issues: list[str] = []
    for item in error.errors(include_url=False, include_input=False):
        location = ".".join(str(part) for part in item["loc"]) or "$"
        issues.append(f"{location}: {item['msg']} ({item['type']})")
    return issues


def _check_business_rules(value: IncidentSummary) -> list[str]:
    issues: list[str] = []
    root_cause_unknown = value.confirmed_root_cause.casefold() == "unknown"

    if value.status == "complete" and root_cause_unknown:
        issues.append("status cannot be complete when confirmed_root_cause is unknown")
    if value.status == "insufficient_context" and not value.unknowns:
        issues.append("unknowns must not be empty when status is insufficient_context")

    return issues


def validate_output(raw: str) -> IncidentSummary:
    """依次执行 JSON 语法、Pydantic Schema 和业务规则校验。"""

    try:
        json_text = extract_json_object(raw)
        payload = json.loads(json_text)
    except json.JSONDecodeError as error:
        issue = f"line {error.lineno}, column {error.colno}: {error.msg}"
        raise StructuredOutputError("JSON parsing failed", issues=[issue]) from error

    try:
        value = IncidentSummary.model_validate(payload)
    except ValidationError as error:
        raise StructuredOutputError(
            "schema validation failed",
            issues=_format_validation_issues(error),
        ) from error

    business_issues = _check_business_rules(value)
    if business_issues:
        raise StructuredOutputError("business validation failed", issues=business_issues)

    return value


def _repair_message(error: StructuredOutputError) -> str:
    schema = json.dumps(IncidentSummary.model_json_schema(), ensure_ascii=False)
    issues = "\n".join(f"- {issue}" for issue in error.issues) or f"- {error}"
    return (
        "Your previous response failed validation. Return one corrected JSON object only.\n"
        "Do not add Markdown fences, explanations, or new facts.\n\n"
        f"Validation error:\n{issues}\n\n"
        f"Required JSON Schema:\n{schema}"
    )


def generate_structured(
    *,
    messages: list[Message],
    provider: Provider,
    max_repairs: int = 1,
) -> StructuredResult:
    """调用模型并校验；失败时在预算内请求一次定向修复。"""

    if max_repairs < 0:
        raise ValueError("max_repairs must be >= 0")

    conversation = [message.copy() for message in messages]
    last_error: StructuredOutputError | None = None

    for attempt in range(1, max_repairs + 2):
        raw = provider(conversation)
        try:
            value = validate_output(raw)
            return StructuredResult(value=value, attempts=attempt, repaired=attempt > 1)
        except StructuredOutputError as error:
            last_error = error
            if attempt > max_repairs:
                break

            # 只保留有限长度的失败输出，避免 repair 请求无限膨胀。
            conversation = conversation + [
                {"role": "assistant", "content": raw[:4000]},
                {"role": "user", "content": _repair_message(error)},
            ]

    assert last_error is not None
    raise StructuredOutputError(
        f"structured output failed after {max_repairs + 1} attempts",
        issues=last_error.issues,
    ) from last_error
