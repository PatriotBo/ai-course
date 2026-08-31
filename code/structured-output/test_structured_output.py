import json
import unittest

from models import IncidentSummary
from structured_output import (
    StructuredOutputError,
    extract_json_object,
    generate_structured,
    validate_output,
)


VALID_PAYLOAD = {
    "status": "insufficient_context",
    "impact": "支付接口 P99 延迟升至 8 秒，影响范围未知。",
    "timeline": [
        {"timestamp": "10:02", "event": "支付 API P99 延迟升至 8 秒"},
        {"timestamp": "10:18", "event": "延迟恢复"},
    ],
    "confirmed_root_cause": "unknown",
    "unknowns": ["受影响用户数", "连接池参数是否为唯一根因"],
    "actions": [
        {"action": "补充受影响用户数", "owner": "unknown", "deadline": "unknown"}
    ],
    "confidence": 0.82,
}


class JsonExtractionTest(unittest.TestCase):
    def test_extracts_plain_json_object(self) -> None:
        raw = json.dumps(VALID_PAYLOAD, ensure_ascii=False)
        self.assertEqual(extract_json_object(raw), raw)

    def test_extracts_json_from_markdown_fence(self) -> None:
        raw = "```json\n" + json.dumps(VALID_PAYLOAD, ensure_ascii=False) + "\n```"
        extracted = extract_json_object(raw)
        self.assertEqual(json.loads(extracted), VALID_PAYLOAD)

    def test_extracts_balanced_json_from_surrounding_text(self) -> None:
        raw = "下面是结果：\n" + json.dumps(VALID_PAYLOAD, ensure_ascii=False) + "\n以上。"
        extracted = extract_json_object(raw)
        self.assertEqual(json.loads(extracted), VALID_PAYLOAD)

    def test_rejects_multiple_json_objects(self) -> None:
        with self.assertRaisesRegex(StructuredOutputError, "exactly one JSON object"):
            extract_json_object('{"a": 1} {"b": 2}')


class ValidationTest(unittest.TestCase):
    def test_validates_expected_schema(self) -> None:
        result = validate_output(json.dumps(VALID_PAYLOAD, ensure_ascii=False))
        self.assertIsInstance(result, IncidentSummary)
        self.assertEqual(result.status, "insufficient_context")

    def test_rejects_unknown_enum_value(self) -> None:
        payload = {**VALID_PAYLOAD, "status": "maybe"}
        with self.assertRaisesRegex(StructuredOutputError, "schema validation failed"):
            validate_output(json.dumps(payload, ensure_ascii=False))

    def test_rejects_extra_fields(self) -> None:
        payload = {**VALID_PAYLOAD, "debug_reasoning": "hidden chain"}
        with self.assertRaisesRegex(StructuredOutputError, "schema validation failed"):
            validate_output(json.dumps(payload, ensure_ascii=False))

    def test_rejects_complete_status_with_unknown_root_cause(self) -> None:
        payload = {**VALID_PAYLOAD, "status": "complete", "unknowns": []}
        with self.assertRaisesRegex(StructuredOutputError, "business validation failed"):
            validate_output(json.dumps(payload, ensure_ascii=False))


class GenerationTest(unittest.TestCase):
    def test_repairs_once_after_invalid_output(self) -> None:
        responses = iter([
            '{"status": "maybe"}',
            json.dumps(VALID_PAYLOAD, ensure_ascii=False),
        ])
        captured_messages: list[list[dict[str, str]]] = []

        def provider(messages: list[dict[str, str]]) -> str:
            captured_messages.append(messages)
            return next(responses)

        result = generate_structured(
            messages=[{"role": "user", "content": "生成事故摘要"}],
            provider=provider,
            max_repairs=1,
        )

        self.assertEqual(result.attempts, 2)
        self.assertTrue(result.repaired)
        self.assertEqual(result.value.status, "insufficient_context")
        self.assertIn("validation error", captured_messages[1][-1]["content"].lower())

    def test_raises_after_repair_budget_is_exhausted(self) -> None:
        def provider(messages: list[dict[str, str]]) -> str:
            return "not json"

        with self.assertRaisesRegex(StructuredOutputError, "after 2 attempts"):
            generate_structured(
                messages=[{"role": "user", "content": "生成事故摘要"}],
                provider=provider,
                max_repairs=1,
            )


if __name__ == "__main__":
    unittest.main()
