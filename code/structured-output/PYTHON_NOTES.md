# Lesson 7 Python 语法补充

本页只解释 Lesson 7 新增语法，不重复前几课的环境变量、dataclass 和 OpenAI-compatible 基础。

---

## 1. `Literal`：把字符串限制为枚举

```python
from typing import Literal

status: Literal["complete", "insufficient_context"]
```

它表示 `status` 只能是两个固定字符串之一。Pydantic 会在运行时校验，编辑器也能做静态提示。

不要用普通 `str` 再靠注释写“只能填 complete”。注释不会执行。

---

## 2. `Field`：声明字段约束

```python
confidence: float = Field(ge=0.0, le=1.0)
impact: str = Field(min_length=1, max_length=300)
timeline: list[TimelineEvent] = Field(max_length=5)
```

- `ge`：greater than or equal，大于等于；
- `le`：less than or equal，小于等于；
- `min_length` / `max_length`：限制字符串或列表长度。

这些约束会进入 JSON Schema，也会被 Pydantic 执行。

---

## 3. `ConfigDict(extra="forbid")`

```python
class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
```

默认情况下，模型可能忽略未知字段。结构化输出链路更适合拒绝额外字段，避免模型偷偷返回：

```json
{
  "debug_reasoning": "...",
  "unexpected_field": "..."
}
```

`str_strip_whitespace=True` 会自动清理字符串两侧空白，但不会修复事实内容。

---

## 4. `model_validate()` 与 `model_validate_json()`

两种常见入口：

```python
IncidentSummary.model_validate(payload_dict)
IncidentSummary.model_validate_json(raw_json_text)
```

本课先用 `json.loads()`，再用 `model_validate()`，是为了把错误分类得更清楚：

```text
JSON parsing failed
Schema validation failed
Business validation failed
```

如果不需要区分 JSON 解析错误，也可以直接使用 `model_validate_json()`。

---

## 5. `ValidationError.errors()`

```python
except ValidationError as error:
    for item in error.errors(include_url=False, include_input=False):
        print(item["loc"], item["msg"], item["type"])
```

典型结果：

```text
status Input should be 'complete' or 'insufficient_context' literal_error
confidence Input should be less than or equal to 1 less_than_equal
```

生产日志里不要记录完整 `input`，因为模型输出可能含用户隐私或业务敏感数据。

---

## 6. `Callable` 与 Provider 注入

```python
Provider = Callable[[list[dict[str, str]]], str]
```

意思是 Provider 是一个函数：输入 messages，返回模型文本。

```python
def generate_structured(*, messages, provider, max_repairs=1):
    raw = provider(messages)
```

这样结构化校验逻辑不依赖具体 SDK：

- 生产传入 `OpenAICompatibleProvider.generate`；
- 单元测试传入一个小函数，返回指定文本；
- 将来换 Provider 时不改校验核心。

这不是为课程写一个 mock provider；它是依赖反转，让纯逻辑可测试。

---

## 7. `raise ... from error`

```python
raise StructuredOutputError("schema validation failed") from error
```

`from error` 保留原异常链。上层看到统一业务异常，调试时仍能追到 Pydantic 的根因。

---

## 8. `model_json_schema()`

```python
schema = IncidentSummary.model_json_schema()
```

Pydantic 可以从 Python 模型生成 JSON Schema。它可用于：

- 放进 Prompt 告诉模型输出结构；
- 传给支持原生 schema 的模型 API；
- 生成接口文档；
- repair 时提醒模型修复字段。

但要记住：同一份 Schema 应由代码生成并复用，不要在 Prompt 和后端手写两份不同版本。
