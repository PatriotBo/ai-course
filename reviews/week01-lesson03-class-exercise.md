# Review：Week 1 Lesson 3 课堂练习

> 主题：LLM API 第一课——messages / token / model / temperature  
> 类型：课堂练习批改  
> 日期：2026-06-22  
> 状态：课堂练习已完成，课后作业未提交

---

## 1. 用户提交内容摘要

### 练习 1：模型策略与 temperature

1. **投诉 / 咨询 / 闲聊分类**
   - 模型策略：小模型
   - temperature：低
   - 理由：分类不需要强推理，为节约成本使用小模型；不希望输出太发散，否则体验差且影响可信度。

2. **给“吵架帮手”生成 5 个不同风格的反驳句**
   - 模型策略：小模型
   - temperature：中
   - 理由：场景不复杂，小模型够用；用户期待不同答案，因此适当提高 temperature。

3. **固定 JSON 输出，供后端解析**
   - 模型策略：未明确填写
   - temperature：低
   - 理由：结构化输出不应太发散，否则后端难以解析。

### 练习 2：LLM Client 排查字段

用户列出的字段：

- request_id
- model
- messages
- 用户问题
- 模型输出
- temperature
- latency_ms
- error

---

## 2. 总体评价

这次练习整体 **基本通过，但不算优秀**。

你已经理解了两个关键点：

1. 不同场景应该选择不同模型和 temperature；
2. LLM 调用必须记录 trace 信息，否则线上问题很难排查。

但也暴露出两个明显问题：

1. **参数选择还停留在“大概对”的层面**：能判断低温/中温，但没有把结构化输出、schema、JSON mode、模型能力边界说完整。
2. **日志字段不够生产级**：缺少 token usage、cost、provider、prompt_version、max_tokens、finish_reason、retry 等关键字段；并且 raw messages / 用户问题直接入日志存在隐私风险，需要考虑脱敏。

综合评分：**72 / 100**。

---

## 3. 分题批改

## 3.1 场景 1：投诉 / 咨询 / 闲聊分类

你的答案：

```text
模型策略：小模型
温度：低
```

判断：**正确**。

这个场景本质是分类任务，不需要复杂推理，目标是：

- 稳定；
- 便宜；
- 快；
- 可复现；
- 输出范围受控。

更完整的答案应该是：

```text
模型策略：小模型优先，必要时可用规则 + 小模型混合。
temperature：0-0.2。
输出约束：固定枚举值，如 consult / complaint / chat。
治理手段：结构化输出 schema + 置信度 + 低置信度人工兜底或二次判断。
```

你答对了主方向，但少了 **输出约束** 和 **低置信度处理**。

---

## 3.2 场景 2：生成 5 个不同风格的吵架训练回应

你的答案：

```text
模型策略：小模型
temperature：中
```

判断：**基本正确，但要分层**。

如果只是生成普通候选句，小模型 + 中等 temperature 可以。

但“吵架帮手”这个场景有两个额外要求：

1. 不能输出人身攻击、威胁、歧视、侮辱内容；
2. 不同风格不等于无边界发散。

所以更好的答案是：

```text
模型策略：默认小模型生成候选；如果需要复杂策略、强情绪博弈或高质量复盘，可以路由到更强模型。
temperature：0.6-0.8。
输出约束：明确 5 种风格标签，例如理性反驳、幽默化解、边界声明、追问澄清、温和反击。
安全边界：Guardrails 过滤人身攻击、威胁、歧视和隐私攻击。
```

你答对了“需要多样性”，但没有提安全边界。这在吵架帮手项目里是硬伤，后面必须补。

---

## 3.3 场景 3：固定 JSON 输出供后端解析

你的答案：

```text
temperature：低
```

判断：**不完整**。

你只答了 temperature，没有答模型策略。

固定 JSON 输出不是只靠低 temperature。真正的工程手段应该是：

```text
模型策略：选择支持 structured output / JSON schema / function calling 的模型，通常小模型或中等模型即可，关键看结构化输出能力。
temperature：0-0.2。
输出约束：JSON schema / Pydantic schema / enum / required fields。
后端校验：schema validation，不通过则 retry 或 fallback。
```

这里要记住：

```text
低 temperature 只能降低随机性，不能保证 JSON 一定合法。
```

生产系统里必须有 schema 约束和后端校验。

---

## 4. 练习 2：排查字段批改

你列出的字段：

```text
request_id, model, messages, 用户问题, 模型输出, temperature, latency_ms, error
```

判断：**方向对，但字段不够生产级**。

这些字段可以帮助定位一部分问题，但如果线上用户反馈“这次回答很奇怪”，仅靠这些还不够。

主要缺口如下：

| 缺失字段 | 为什么重要 |
|---|---|
| provider | 同一个 model 名可能来自不同供应商或兼容层，问题归因需要知道 provider |
| prompt_version | 回答异常可能是 prompt 改版导致，不记录版本无法回溯 |
| input_tokens / output_tokens / total_tokens | 没有 token 就无法判断是否上下文过长、输出被截断或成本异常 |
| cost | 生产系统必须能按请求、用户、功能统计成本 |
| max_tokens | 输出异常短可能是 max_tokens 太小导致 |
| finish_reason | 判断是正常停止、长度截断、内容过滤还是工具调用结束 |
| status_code / error_type | error 不能只有字符串，要能分类统计和告警 |
| retry_count | 排查是否 provider 抖动、重试后成功或失败 |
| user_id / session_id | 排查用户维度、会话维度问题；注意脱敏或使用内部 ID |
| prompt_hash / messages_hash | 不一定存完整敏感内容，但要能关联输入版本 |
| response_id / trace_id | 对接模型供应商和内部 trace |
| environment | dev / staging / prod，不同环境问题不能混在一起 |

更合格的最小日志表应该至少包含：

| 字段名 | 类型 | 说明 | 排查价值 |
|---|---|---|---|
| request_id | string | 内部请求 ID | 串起业务请求、模型调用、错误日志 |
| trace_id | string | 链路追踪 ID | 和后端 trace / gateway log 对齐 |
| user_id_hash | string | 脱敏用户标识 | 排查用户维度问题，避免明文隐私 |
| provider | string | 模型供应商 | 区分 OpenAI-compatible、Azure、本地模型等 |
| model | string | 实际模型 | 判断模型选择是否正确 |
| prompt_version | string | Prompt 版本 | 回溯 prompt 变更导致的异常 |
| messages_hash | string | 输入消息 hash | 保护隐私，同时支持定位同类输入 |
| temperature | float | 采样温度 | 判断输出异常是否与随机性有关 |
| max_tokens | int | 最大输出 token | 判断是否因限制导致输出不完整 |
| input_tokens | int | 输入 token | 判断上下文长度和成本 |
| output_tokens | int | 输出 token | 判断输出长度和成本 |
| total_tokens | int | 总 token | 成本统计和异常检测 |
| latency_ms | int | 调用耗时 | 定位慢请求和 provider 抖动 |
| finish_reason | string | 结束原因 | 判断正常结束、截断、内容过滤等 |
| retry_count | int | 重试次数 | 判断稳定性和 provider 抖动 |
| status | string | success / failed | 统计成功率 |
| error_type | string | 错误类型 | 做告警、聚合和降级策略 |
| created_at | datetime | 调用时间 | 时间维度排查和报表 |

这才是接近生产可用的 LLM Gateway 调用日志。

---

## 5. 必须修正的几个点

### 5.1 “用户问题”和“messages”不能随便原样入日志

你说要记录 messages 和用户问题，这对排查有帮助，但直接存明文有风险。

原因：

- 用户输入可能包含隐私；
- 对话可能包含业务敏感信息；
- 后续如果做线上服务，日志权限、留存周期、合规边界都要考虑。

更合理的做法：

```text
开发期：可以记录完整 messages，方便调试。
生产期：默认记录摘要 / hash / 脱敏版本；必要时通过受控开关采样记录。
```

### 5.2 模型输出也不能无脑全量记录

模型输出也可能包含敏感内容或被 prompt injection 污染。

生产建议：

```text
记录 output_summary / output_hash / finish_reason / token usage。
需要保留完整输出时，必须有权限控制和留存周期。
```

### 5.3 结构化输出不能只依赖 temperature

固定 JSON 输出必须有：

```text
schema 约束 + 后端校验 + retry / repair / fallback
```

低温度只是辅助，不是保证。

---

## 6. 本节课堂练习结论

你已经理解：

- 分类任务适合小模型低温度；
- 创意生成需要适当提高 temperature；
- 结构化输出需要降低随机性；
- LLM Client 必须记录请求、模型、上下文、输出、温度、耗时和错误。

但还需要补：

- 结构化输出的 schema 和后端校验；
- token usage / cost 作为一等日志字段；
- prompt_version / provider / finish_reason / retry_count；
- messages / output 的隐私脱敏策略；
- 参数选择和业务风险之间的对应关系。

---

## 7. 下一步训练重点

下一段课程要继续强化三件事：

1. **LLM Gateway 思维**：不要把 API 调用散落在业务代码里。
2. **调用日志表设计**：每次模型调用都要可追踪、可统计、可复盘。
3. **结构化输出治理**：低 temperature 不等于稳定输出，必须靠 schema、validation、retry、fallback。

课后作业里，重点做：

```text
第 3 题：代码阅读题
第 4 题：LLM Gateway 调用日志表设计
第 5 题：面试表达
```

尤其第 4 题，要用今天批改里的字段表作为起点，但必须用自己的话重新组织。
