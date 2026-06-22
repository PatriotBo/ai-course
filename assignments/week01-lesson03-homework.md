# Homework：Week 1 Lesson 3

> 主题：LLM API 第一课——messages / token / model / temperature  
> 预计耗时：45-60 分钟  
> 代码目录：`code/llm-api-basics/`

> 课程规则更新：从后续课程开始，课堂练习和课后习题默认合并为一套课后练习，避免阅读讲义后重复做两套题。只有真实课堂互动、设计评审或代码调试诊断明显不同于作业时，才单独生成课堂记录。

---

## 1. 基础概念题

请用自己的话回答：

1. 为什么说 LLM API 调用不是普通函数调用，而是一个需要治理的外部推理依赖？
2. `system` / `user` / `assistant` / `tool` 四类 message 分别承担什么职责？
3. token 为什么同时影响成本、延迟和上下文窗口？
4. model 选择为什么不能只选“最强模型”？
5. temperature 越高是否代表模型越聪明？为什么？

---

## 2. 参数选择题

为下面场景选择模型策略和 temperature，并说明理由。

| 场景 | 模型策略 | temperature | 理由 |
|---|---|---:|---|
| 投诉/咨询/闲聊分类 |  |  |  |
| 生成 5 个不同风格的吵架训练回应 |  |  |  |
| 输出固定 JSON 供后端解析 |  |  |  |
| 分析一篇复杂技术文章并总结架构 |  |  |  |
| 高频用户输入改写 |  |  |  |

---

## 3. 代码阅读题

阅读：

```text
code/llm-api-basics/llm_client.py
code/llm-api-basics/demo_generate.py
```

回答：

1. `LLMRequest` 里为什么要包含 `request_id`？
2. `LLMResult` 里为什么要记录 `latency_ms` 和 `usage`？
3. 为什么代码里保留 `mock` provider？
4. 如果你要加 retry，应该放在哪一层？为什么？

---

## 4. LLM Gateway 设计题

设计一个最小 LLM Gateway 的调用日志表，至少包含 8 个字段。

格式：

| 字段名 | 类型 | 说明 | 为什么需要 |
|---|---|---|---|
| request_id | string | 请求 ID | 用于 trace 和排查 |
| ... | ... | ... | ... |

要求：

- 必须包含 model、latency、usage/token、error 相关字段；
- 不能只列字段，要说明排查价值；
- 如果你觉得某些字段涉及隐私，需要说明是否脱敏。

---

## 5. 面试题

准备 1 分钟回答：

> 你会如何把 LLM API 调用封装成生产可用的后端能力？

要求包含：

- LLM Client / Gateway；
- messages / prompt 构造；
- 模型选择；
- 超时重试；
- token usage / cost；
- trace / logging；
- 输出解析或结构化输出。

---

## 6. 提交方式

把答案直接发给我即可。我会按以下维度批改：

1. 是否真正理解 LLM API 的工程边界；
2. 是否能把参数选择和业务场景对应起来；
3. 是否能设计可排查、可治理的调用日志；
4. 是否能用后端工程语言表达；
5. 是否避免“只会调 API”的 demo 思维。

---

## 7. 本次提交与批改记录

> 提交时间：2026-06-22  
> 批改结论：通过，但不是满分；需要补齐生产级 LLM Gateway 的日志字段、结构化输出治理和参数选择完整性。  
> 完整批改：`reviews/week01-lesson03-homework-review.md`

### 7.1 综合评分

| 维度 | 分数 | 评价 |
|---|---:|---|
| 基础概念理解 | 82 / 100 | 能理解 LLM API 不是简单 HTTP 调用，但个别表述还不够精准。 |
| message / token / model / temperature | 80 / 100 | 大方向正确，model 选择维度偏窄，temperature 表达基本准确。 |
| 参数选择 | 65 / 100 | 只回答了 3 个场景，漏掉 2 个；JSON 场景仍然只强调低温度，缺 schema 治理。 |
| 代码阅读 | 78 / 100 | 能理解 request_id、latency、usage、mock provider，但 retry 放置层级解释不够完整。 |
| LLM Gateway 日志表 | 72 / 100 | 有基础字段，但缺少 token 拆分、trace_id、prompt_version、finish_reason、retry_count、status/error_type 等生产关键字段。 |
| 面试表达 | 80 / 100 | 用户要求提供满分答案，后续仍需自己训练 1 分钟表达。 |

综合评分：**76 / 100**

### 7.2 关键修正

1. `LLM API` 本身不是稳定输出工程方法；`LLM Client / Gateway` 封装才是稳定输出工程方法的一部分。
2. 固定 JSON 输出不能只靠低 temperature，必须使用 structured output / JSON schema / function calling + 后端 validation + retry/fallback。
3. `max_tokens` 通常表示最大输出 token，不等于模型上下文窗口。
4. LLM Gateway 调用日志必须补齐 `trace_id`、`prompt_version`、`input_tokens`、`output_tokens`、`total_tokens`、`retry_count`、`status`、`error_type`、`finish_reason` 等字段。
5. `messages` 和模型输出不能默认明文全量入库，生产环境应脱敏、hash 或采样。
