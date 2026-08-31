# Week 2 Lesson 7：结构化输出——JSON Schema / Pydantic / Validation / Repair

> 状态：今日正式开课
> 预计时长：60-75 分钟
> 本节类型：结构化输出 + 后端校验 + 真实 Provider 实战
> 代码目录：`code/structured-output/`

---

## 0. 本节课为什么重要

Lesson 6 把 Prompt 当成可执行规格，定义了 Output Contract。但“Prompt 中要求输出 JSON”不代表后端真的拿到了可用对象。

模型可能返回：

```text
1. 合法 JSON，但字段名错误；
2. 合法 JSON，但枚举值不在允许范围；
3. 字段类型正确，但业务语义互相矛盾；
4. JSON 外多一段解释或 Markdown 代码块；
5. 缺少字段，或者偷偷增加未约定字段；
6. 第一次格式错误，第二次可以修好；
7. 连续失败，必须停止而不是把脏数据送进业务。
```

所以本节的核心不是“让模型输出大括号”，而是建立一条后端可以信任的链路：

```text
Prompt Contract
  ↓
Model Output
  ↓
JSON Parse
  ↓
Schema Validation
  ↓
Business Validation
  ↓
Typed Object / Explicit Failure
```

> 结构化输出不是一种 Prompt 风格，而是模型不确定性与确定性后端之间的协议适配层。

---

## 1. 结构化输出在系统里的位置

完整调用链路：

```text
业务请求
  ↓
Prompt Builder
  ├── instruction
  ├── context
  └── JSON Schema
  ↓
LLM Gateway / Provider Adapter
  ↓
模型原始输出（不可信字符串）
  ↓
Output Parser
  ├── 提取唯一 JSON object
  └── json.loads
  ↓
Schema Validator（Pydantic）
  ├── required fields
  ├── types
  ├── enum / range / length
  └── extra fields
  ↓
Business Validator
  ├── 跨字段一致性
  ├── 权限 / 风险规则
  └── 事实与状态边界
  ↓
业务对象 / Repair / Fallback
```

职责边界：

| 组件 | 负责什么 | 不能假设什么 |
|---|---|---|
| Prompt | 告诉模型目标、字段和失败行为 | 不能保证模型一定遵守 |
| Provider JSON Mode | 尽量限制输出为 JSON | 不保证业务字段与事实正确 |
| JSON Parser | 确认语法可解析 | 不理解字段语义 |
| Pydantic | 校验结构、类型、枚举、范围 | 不自动理解全部业务关系 |
| Business Validator | 校验跨字段规则和系统约束 | 不负责修复模型事实错误 |
| Repair | 让模型按错误信息重新表达 | 不能把错误事实变成正确事实 |

---

## 2. 三层契约：JSON 合法、Schema 合法、业务可用

### 2.1 第一层：JSON 语法合法

下面是合法 JSON：

```json
{
  "status": "maybe",
  "confidence": 99
}
```

它能被 `json.loads()` 解析，但并不代表字段符合要求。

常见 JSON 语法问题：

- 单引号代替双引号；
- 尾随逗号；
- Markdown fence；
- JSON 前后夹着解释；
- 生成中途截断；
- 同时返回两个对象。

本课的 `extract_json_object()` 只负责提取一个括号平衡的 JSON object，不使用粗暴的 `{.*}` 正则，也不偷偷修改内容。

### 2.2 第二层：Schema 合法

Schema 定义数据形状：

```python
class IncidentSummary(BaseModel):
    status: Literal["complete", "insufficient_context"]
    impact: str = Field(min_length=1, max_length=300)
    timeline: list[TimelineEvent] = Field(max_length=5)
    confirmed_root_cause: str
    unknowns: list[str] = Field(max_length=10)
    actions: list[ActionItem] = Field(max_length=10)
    confidence: float = Field(ge=0.0, le=1.0)
```

它能验证：

- `status` 只能取两个值；
- `confidence` 必须在 0 到 1；
- timeline 最多 5 项；
- 必填字段不能缺失；
- `extra="forbid"` 时未知字段直接失败。

### 2.3 第三层：业务可用

下面对象可能通过 Schema：

```json
{
  "status": "complete",
  "confirmed_root_cause": "unknown"
}
```

但业务上矛盾：根因未知时不能说任务完整完成。

所以还需要代码规则：

```python
if value.status == "complete" and value.confirmed_root_cause == "unknown":
    issues.append("status cannot be complete when root cause is unknown")
```

> 类型正确不等于业务正确。Schema 是第一道硬边界，不是全部业务规则。

---

## 3. JSON Schema 与 Pydantic 的关系

JSON Schema 是描述 JSON 结构的标准；Pydantic 是 Python 中定义、校验并转换数据模型的工具。

二者关系：

```text
Python Pydantic Model
  ├── 运行时校验模型输出
  ├── 生成 Python 类型对象
  └── model_json_schema()
             ↓
        JSON Schema
  ├── 放入 Prompt
  ├── 传给支持原生 schema 的 Provider
  └── 用于文档和测试
```

单一事实源应是代码中的 Pydantic Model。不要在 Prompt、文档、前端和后端分别手写四套字段定义，否则它们迟早漂移。

### 3.1 严格模型

```python
class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
```

为什么拒绝额外字段：

- 防止下游误以为额外字段可信；
- 避免模型输出未授权信息；
- 让 Schema 变更必须显式升级；
- 便于评估格式合规率。

### 3.2 Optional 不等于可以乱缺失

```python
owner: str | None
```

表示值可以是字符串或 null，但字段是否必填取决于有没有默认值。

```python
owner: str | None = None
```

才表示字段缺失时默认 null。

设计结构化输出时要先决定：

- 缺失字段应该失败；
- 使用 `null`；
- 使用字符串 `unknown`；
- 还是进入 `unknowns` 列表。

不要混用，否则下游会出现三种“未知”。

---

## 4. Provider 原生结构化能力：有用，但不要误解

常见能力分三档：

| 能力 | 作用 | 仍需后端做什么 |
|---|---|---|
| Prompt 要求 JSON | 软提示 | 全部解析和校验 |
| JSON mode / `json_object` | 提高语法合法率 | Schema 与业务校验 |
| JSON Schema / constrained decoding | 按 Schema 限制 token 生成 | 业务规则、事实性、权限、版本兼容 |

不同 OpenAI-compatible Provider 对 `response_format` 的支持并不完全一致。本课默认 `LLM_RESPONSE_MODE=text`，是为了兼容 GLM、腾讯混元和其他服务；只有确认 Provider 支持时才打开 `json_object`。

即便 Provider 支持严格 Schema，也不能证明：

- 模型使用的事实正确；
- 跨字段业务关系合理；
- 用户有权限执行相应动作；
- 输出适合直接写数据库。

---

## 5. Constrained Decoding：今日新增术语

**Constrained Decoding（约束解码）**是在模型生成每个 token 时，根据语法或 Schema 限制“下一步允许生成什么”，从生成阶段减少非法格式。

例如当前 Schema 要求：

```json
{"status": "complete" | "insufficient_context"}
```

约束解码可以阻止模型生成 `"status": "maybe"` 这样的枚举外值。

但它不能保证：

- `complete` 在业务上真的成立；
- 事故根因是真实的；
- 输出没有越权内容；
- Schema 本身设计正确。

因此工程链路仍然是：

```text
Constrained Decoding（生成约束）
  + Pydantic（接收校验）
  + Business Rules（业务校验）
  + Eval（质量验证）
```

---

## 6. 错误分类：先知道哪里坏了

不要把所有失败都叫“模型输出错误”。至少分为：

| 错误类型 | 例子 | 处理 |
|---|---|---|
| Extraction Error | 找不到唯一 JSON object | 可 repair 一次 |
| JSON Parse Error | 截断、引号、逗号错误 | 可 repair 一次 |
| Schema Error | 缺字段、类型错、枚举错 | 带字段错误 repair |
| Business Rule Error | complete + unknown root cause | 谨慎 repair 或直接失败 |
| Safety / Permission Error | 输出请求执行未授权动作 | 不 repair，直接拒绝/审批 |
| Provider Error | timeout、429、5xx | 交给 Gateway retry policy |

`Provider Error` 与 `Validation Error` 不能混在同一层。前者是调用可靠性，后者是输出契约。

### 6.1 结构化日志至少记录

```text
request_id
provider
model
prompt_key
prompt_version
schema_name
schema_version
attempt
repair_count
validation_stage
validation_issue_types
latency_ms
input_tokens
output_tokens
finish_reason
```

不要默认把完整输入和完整模型输出写日志。生产中应考虑脱敏、采样和保留期限。

---

## 7. Repair：什么时候修，怎么修

### 7.1 推荐链路

```text
第一次输出
  ↓
Validation Failed
  ↓
生成字段级错误摘要
  ↓
附原输出（截断）+ JSON Schema
  ↓
要求只修结构，不新增事实
  ↓
第二次校验
  ├── 通过
  └── 失败 → Explicit Failure / Fallback
```

Repair Prompt 应包含：

```text
Your previous response failed validation.
Return one corrected JSON object only.
Do not add explanations or new facts.

Validation errors:
- status: expected complete or insufficient_context
- confidence: must be <= 1
```

### 7.2 为什么最多一次

- 每次 repair 都增加延迟和成本；
- 同一模型持续失败可能说明 Prompt/Schema 不兼容；
- 无限修复会掩盖线上质量问题；
- repair 可能引入新的事实变化。

一次 repair 是教学示例中的默认值。生产值应通过测试集和指标决定，而不是拍脑袋。

### 7.3 不要用字符串魔法“修 JSON”

危险做法：

```text
把单引号全换成双引号
删除所有尾随逗号
用正则抓取第一个大括号到最后一个大括号
缺字段时填一个看起来合理的值
```

这会把非法输出伪装成合法输出，并可能改变文本事实。正确策略是：解析失败 → 明确错误 → 有限 repair → 再失败则结束。

---

## 8. Fallback：修不好怎么办

Fallback 不是一句“请稍后再试”，要按业务风险设计。

### 低风险展示型场景

- 返回普通文本；
- 标记 `structured=false`；
- 前端不展示依赖结构化字段的按钮。

### 中风险自动化场景

- 切换已验证的备用模型；
- 进入异步重试队列；
- 保存 trace，等待人工处理。

### 高风险执行场景

- 立即停止；
- 不执行工具、不写数据库、不发起交易；
- 转人工审批；
- 记录审计事件。

> Fail closed：结构化输出失败时，高风险系统应默认不执行。

---

## 9. 本节代码实现

代码目录：

```text
code/structured-output/
├── models.py
├── structured_output.py
├── provider.py
├── demo_generate.py
├── test_structured_output.py
├── README.md
├── PYTHON_NOTES.md
├── requirements.txt
└── .env.example
```

### 9.1 `models.py`

负责：

- Pydantic 严格模型；
- `Literal` 枚举；
- 长度与数值范围；
- 禁止额外字段。

### 9.2 `structured_output.py`

负责：

```text
extract_json_object()
  ↓
validate_output()
  ├── json.loads
  ├── IncidentSummary.model_validate
  └── _check_business_rules
  ↓
generate_structured()
  ├── provider(messages)
  ├── validate
  ├── repair once
  └── StructuredOutputError
```

### 9.3 `provider.py`

只处理真实 Provider：

```text
LLM_PROVIDER
LLM_MODEL
LLM_BASE_URL
LLM_API_KEY
LLM_RESPONSE_MODE
```

它不负责理解事故摘要的业务 Schema，也不负责 repair 策略。

### 9.4 为什么测试不调用真实 Provider

单元测试目标是验证确定性逻辑：提取、校验、业务规则、repair 次数。网络和真实模型会让测试慢、不稳定、收费且不可重复。

测试通过 callable 注入指定输出，不等于在产品代码中增加 mock provider；真实 `demo_generate.py` 仍然只连接实际 Provider。

---

## 10. 常见误区

### 误区 1：temperature=0 就一定输出稳定 JSON

错误。低温度降低随机性，不提供语法或 Schema 保证。

### 误区 2：能 `json.loads()` 就能入库

错误。必须继续做 Schema、业务、权限和安全校验。

### 误区 3：Pydantic 会自动判断事实真假

错误。Pydantic 验证“形状”，不会验证事故根因是否真实。

### 误区 4：所有字段都 Optional，成功率更高

这只是把错误推迟到下游。业务必需字段应该必填；真正允许缺失的字段才 Optional。

### 误区 5：Repair 越多成功率越高

可能提高表面通过率，却增加成本、延迟和事实漂移。必须有预算和指标。

### 误区 6：原生 Structured Outputs 可以删除后端校验

错误。生成约束与接收校验是两道独立边界，业务规则永远要由系统负责。

---

## 11. 如何设计一个好 Schema

使用以下清单：

| 维度 | 检查问题 |
|---|---|
| Purpose | 下游为什么需要这个字段？ |
| Required | 缺失时应失败、null 还是 unknown？ |
| Type | 能否用明确类型代替自由字符串？ |
| Enum | 状态集合是否有限？ |
| Range | 数值是否有上下界？ |
| Length | 列表和文本是否需要上限？ |
| Extra | 是否拒绝未声明字段？ |
| Consistency | 哪些字段之间存在关系？ |
| Version | Schema 如何升级与兼容？ |
| Privacy | 字段是否可能含敏感数据？ |
| Actionability | 校验失败后系统下一步是什么？ |

好的 Schema 不是越复杂越好，而是只表达业务真正需要的最小稳定结构。

---

## 12. 面试表达

题目：

> 如何设计生产级 LLM 结构化输出链路？

参考回答：

```text
我不会只在 Prompt 里要求模型输出 JSON，而会把结构化输出分成生成约束、接收校验和业务校验三层。

首先用 Pydantic 定义单一事实源，包含必填字段、类型、枚举、范围、长度和 extra=forbid，并从模型生成 JSON Schema。调用模型时，如果 Provider 支持 JSON mode 或 constrained decoding，可以用来提高格式合规率，但不会把它当成最终保证。

模型返回后，我会先提取并解析唯一 JSON object，再做 Pydantic Schema 校验，最后做跨字段业务规则和权限校验。失败要分类记录字段路径、错误类型、prompt/schema/model 版本和 repair 次数。

对于纯格式或字段错误，可以带着精简错误摘要做一次有限 repair；再次失败就显式失败或走降级。高风险场景必须 fail closed，绝不能把未通过校验的数据直接写数据库或触发工具。
```

---

## 13. 本节必须记住的 7 句话

```text
1. 要求输出 JSON，不等于获得可靠结构化对象。
2. JSON 合法、Schema 合法、业务可用是三件不同的事。
3. Pydantic 是后端接收边界，不是事实验证器。
4. Provider JSON mode 能提高合规率，不能替代校验。
5. Repair 只修契约表达，不负责创造或纠正事实。
6. 修复必须有次数、成本和延迟预算。
7. 高风险链路校验失败必须 fail closed。
```

---

## 14. 课后练习

本节只保留一套题答合一课后练习：

```text
assignments/week02-lesson07-homework.html
```

完成后应能：

- 区分 JSON / Schema / Business Validation；
- 独立设计 Pydantic Schema；
- 阅读字段级 ValidationError；
- 设计一次 repair 与显式失败；
- 用 1 分钟说明生产级结构化输出链路。

下一节 Lesson 8 将把 Prompt、Schema 和测试用例纳入版本管理与回归 Eval。
