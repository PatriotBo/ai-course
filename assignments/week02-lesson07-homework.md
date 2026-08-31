# Week 2 Lesson 7：课后练习及答案

> 主题：结构化输出——JSON Schema / Pydantic / Validation / Repair
>
> 建议用法：每题先独立思考，再阅读紧随其后的参考答案。
>
> 代码目录：`code/structured-output/`

---

## 1. 基础概念题

### 1.1 为什么“输出合法 JSON”仍不足以直接进入业务系统？

> **参考答案**

合法 JSON 只证明语法能被解析，不证明字段、类型、枚举、范围和业务关系正确。生产链路至少还需要：

```text
JSON parsing
→ Schema validation
→ Business validation
→ Permission / safety check
```

例如 `{"status":"maybe"}` 是合法 JSON，但枚举非法；`status=complete` 且 `root_cause=unknown` 可能通过类型校验，但业务上矛盾。

### 1.2 JSON Schema、Pydantic 和业务规则分别负责什么？

> **参考答案**

- JSON Schema：描述 JSON 数据形状，可传给支持原生结构化输出的 Provider；
- Pydantic：在 Python 运行时执行字段、类型、枚举、范围、长度和额外字段校验，并生成类型化对象；
- 业务规则：校验跨字段关系、业务状态、权限和风险边界。

Pydantic 可以生成 JSON Schema，但 Schema 不能覆盖全部业务语义。

### 1.3 JSON mode 与 constrained decoding 有什么区别？

> **参考答案**

JSON mode 通常只保证或提高输出为合法 JSON 的概率，不一定严格符合业务 Schema。Constrained decoding 在生成每个 token 时按语法或 Schema 限制允许的输出，格式约束更强。

二者都不能验证事实真实性、权限和跨字段业务逻辑，所以后端仍要校验。

### 1.4 为什么应该设置 `extra="forbid"`？

> **参考答案**

它让未声明字段直接失败，避免模型偷偷增加下游未约定字段，降低数据污染、Schema 漂移和敏感信息意外输出风险。若业务确实需要扩展字段，应显式升级模型与 Schema，而不是静默忽略。

---

## 2. 三层错误分类题

判断下列输出最先在哪一层失败。

### 2.1 输出 A

```text
{"status": "complete",}
```

> **参考答案**

JSON Parse Error：尾随逗号不符合标准 JSON。

### 2.2 输出 B

```json
{
  "status": "maybe",
  "confidence": 0.8
}
```

> **参考答案**

首先是 Schema Error：`status` 不在枚举内，而且缺少多个必填字段。

### 2.3 输出 C

```json
{
  "status": "complete",
  "impact": "影响未知",
  "timeline": [],
  "confirmed_root_cause": "unknown",
  "unknowns": [],
  "actions": [],
  "confidence": 0.8
}
```

> **参考答案**

JSON 和字段类型可能通过，但 Business Rule Error：根因未知时不能把状态标为 `complete`。

---

## 3. Schema 设计题

为“客服工单分类”设计 Pydantic 模型，要求：

- `category` 只能是 `payment`、`delivery`、`refund`、`other`；
- `priority` 只能是 1 到 5；
- `summary` 1 到 200 字；
- `needs_human` 是布尔值；
- 禁止额外字段；
- 当 category=other 时，needs_human 必须为 true。

> **参考答案**

```python
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class TicketClassification(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    category: Literal["payment", "delivery", "refund", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=200)
    needs_human: bool

    @model_validator(mode="after")
    def validate_other_category(self):
        if self.category == "other" and not self.needs_human:
            raise ValueError("other category must be routed to a human")
        return self
```

字段约束由 Pydantic 执行；跨字段关系使用 model validator 或独立业务校验层。

---

## 4. Repair 设计题

第一次模型输出缺少 `actions`，并把 confidence 写成 82。请写 repair 请求必须包含的四类信息。

> **参考答案**

```text
1. 明确前一次输出校验失败；
2. 给出字段级错误：actions missing，confidence must be <= 1；
3. 附上当前 JSON Schema；
4. 要求只返回一个修正后的 JSON object，不加 Markdown、不加解释、不新增事实。
```

不能让 repair “补一个合理负责人”，因为这会创造事实。负责人未知时应按 Schema 使用 `unknown` 或 null。

### 4.1 为什么不建议无限 repair？

> **参考答案**

无限 repair 会累积成本和延迟，掩盖 Prompt/Schema/Provider 的系统性不兼容，并可能导致事实在多轮修复中漂移。应设置最大次数、总耗时和 token 预算，并记录 repair rate；超过预算走明确失败、备用模型或人工处理。

---

## 5. 代码阅读题

阅读：

```text
code/structured-output/models.py
code/structured-output/structured_output.py
code/structured-output/provider.py
```

### 5.1 `extract_json_object()` 为什么不用简单的 `{.*}` 正则？

> **参考答案**

简单贪婪正则无法正确处理字符串内花括号、多个对象和嵌套对象。当前实现逐字符跟踪字符串状态、转义字符和大括号深度，确保提取唯一且括号平衡的对象。

### 5.2 为什么 `validate_output()` 要先 `json.loads()` 再 `model_validate()`？

> **参考答案**

为了把错误阶段分开：`json.loads()` 负责 JSON 语法，Pydantic 负责字段 Schema。日志和 repair 可以明确告诉模型是“第 4 行逗号错误”还是“status 枚举错误”，而不是统一报“解析失败”。

### 5.3 `generate_structured()` 为什么接收 callable provider？

> **参考答案**

这是依赖反转。结构化输出逻辑只依赖“输入 messages，返回文本”的接口，不耦合 OpenAI SDK。生产传真实 provider 方法，单元测试传确定性函数，因此测试无需网络、API key 和真实费用。

### 5.4 `raw[:4000]` 的目的是什么？

> **参考答案**

限制 repair 请求携带的失败输出长度，防止异常超长输出导致上下文膨胀、成本失控或二次超过上下文限制。真实系统还应做隐私脱敏和日志采样。

---

## 6. 工程设计题

场景：模型根据用户自然语言生成退款操作参数。你能否在 Pydantic 校验通过后直接退款？

> **参考答案**

不能。Pydantic 只验证数据结构。退款属于高风险动作，还必须：

```text
鉴权：用户是否有权操作该订单；
业务校验：订单是否可退、金额是否超限、是否重复退款；
数据查询：订单与支付状态必须来自可信系统；
Human Gate：高金额或异常场景人工审批；
幂等：避免重复执行；
审计：记录模型建议、实际参数、审批人和执行结果。
```

结构化输出让参数可解析，不代表参数已授权、真实或安全。

---

## 7. 可观测性题

设计结构化输出日志字段，至少覆盖调用、版本、校验和成本。

> **参考答案**

```text
request_id
provider / model
prompt_key / prompt_version
schema_name / schema_version
attempt / repair_count
validation_stage
validation_issue_types
latency_ms
input_tokens / output_tokens
finish_reason
fallback_used
final_status
```

避免默认记录完整用户输入、完整模型输出和密钥。必要时脱敏、采样并设置保留期限。

---

## 8. 面试题

用 1 分钟回答：如何设计生产级 LLM 结构化输出链路？

> **参考答案**

```text
我会把结构化输出分成生成约束、接收校验和业务校验三层，而不是只在 Prompt 中写“输出 JSON”。

首先用 Pydantic 定义单一事实源，包含必填字段、类型、枚举、范围和 extra=forbid，并从它生成 JSON Schema。如果 Provider 支持 JSON mode 或 constrained decoding，可以提高格式合规率，但这不是最终保证。

模型返回后，先提取并解析唯一 JSON object，再做 Pydantic 校验，最后检查跨字段业务关系、权限和风险边界。失败时记录字段路径、错误类型、Prompt/Schema/模型版本与 repair 次数。

对于纯格式或字段错误，可以附错误摘要和 Schema 做一次有限 repair；仍失败则显式报错或降级。高风险链路必须 fail closed，未通过校验的数据不能写库或触发工具。
```

---

## 9. 自测清单

- [ ] 我能区分 JSON 合法、Schema 合法与业务可用；
- [ ] 我能用 Pydantic 定义必填、枚举、范围、长度和 extra forbid；
- [ ] 我知道 JSON mode / constrained decoding 不能替代后端校验；
- [ ] 我能设计字段级错误和一次 repair；
- [ ] 我知道高风险场景必须 fail closed；
- [ ] 我能说清结构化输出日志和版本字段。

下一课：Lesson 8 Prompt 版本管理、测试集与回归 Eval。
