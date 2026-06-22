# Review：Week 1 Lesson 3 课后作业完整批改

> 课程：Week 1 Lesson 3：LLM API 第一课——messages / token / model / temperature  
> 提交时间：2026-06-22  
> 批改结论：通过，但不是满分；需要补齐生产级 LLM Gateway 的日志字段、结构化输出治理和参数选择完整性。

---

## 1. 总体评分

| 维度 | 分数 | 评价 |
|---|---:|---|
| 基础概念理解 | 82 / 100 | 能理解 LLM API 不是简单 HTTP 调用，但个别表述还不够精准。 |
| message / token / model / temperature | 80 / 100 | 大方向正确，model 选择维度偏窄，temperature 表达基本准确。 |
| 参数选择 | 65 / 100 | 只回答了 3 个场景，漏掉 2 个；JSON 场景仍然只强调低温度，缺 schema 治理。 |
| 代码阅读 | 78 / 100 | 能理解 request_id、latency、usage、mock provider，但 retry 放置层级解释不够完整。 |
| LLM Gateway 日志表 | 72 / 100 | 有基础字段，但缺少 token 拆分、trace_id、prompt_version、finish_reason、retry_count、status/error_type 等生产关键字段。 |
| 面试表达 | 80 / 100 | 你没有自己作答，而是要求满分答案；说明你知道这里重要，但还需要自己训练表达。 |

综合评分：**76 / 100**

结论：**通过，可以进入 Lesson 4；但 LLM Gateway 的生产化字段设计需要继续练。**

---

## 2. 基础概念题批改

### 2.1 为什么 LLM API 是需要治理的外部推理依赖？

你的回答方向正确，尤其这几点是好的：

- 不能把模型调用散落在业务代码里；
- 需要统一输入校验、权限控制、成本控制、风险控制、失败处理、超时重试、模型路由、异常兜底、监控采样；
- 需要统一管理 API key、模型选择和参数设置；
- 架构链路写得基本正确：

```text
业务层
  ↓
Prompt Builder / Context Builder
  ↓
LLM Client / LLM Gateway
  ↓
Provider Adapter
  ↓
OpenAI / Anthropic / GLM / 本地模型
```

需要修正的地方：你开头说“LLM API 在实际应用场景中是为了保证模型稳定输出的工程方法”，这个表述不够准。

更准确：

```text
LLM API 本身只是模型供应商暴露的推理接口；
为了让它在业务系统中稳定、可控、可观测、可降级地运行，才需要 LLM Client / Gateway 这一层工程封装。
```

也就是说：

```text
LLM API ≠ 稳定输出工程方法
LLM Gateway / Client 封装 = 稳定输出工程方法的一部分
```

### 2.2 四类 message 的职责

你的回答基本正确：

| role | 你的理解 | 批改 |
|---|---|---|
| system | 行为边界、角色、约束 | 正确 |
| user | 用户输入、目标、问题、任务 | 正确 |
| assistant | 模型上下文、历史回答 | 基本正确，最好说“历史 assistant 消息” |
| tool | 工具调用结果 | 正确 |

需要补一点：`system` 是软约束，不是安全边界。生产安全不能只靠 system prompt，必须配合输入校验、工具权限、输出校验和审计。

### 2.3 token 为什么影响成本、延迟和上下文窗口？

你的回答正确，但还可以更工程化：

- 成本：输入 token 和输出 token 都可能计费；
- 延迟：输入越长、输出越长，模型处理和生成越慢；
- 上下文窗口：超过模型窗口会报错、截断或丢失上下文；
- Agent 场景：多轮 loop 会持续堆积 token，导致成本和延迟放大；
- RAG 场景：检索内容塞太多会挤占模型回答空间。

你答到了主干，给分较高。

### 2.4 为什么不能只选最强模型？

你的回答只从成本角度展开，这是不完整的。

最强模型不一定最适合，至少还要看：

| 维度 | 说明 |
|---|---|
| 任务复杂度 | 简单分类、改写、摘要不一定需要强模型 |
| 成本 | 强模型单次调用贵，高频场景成本会爆 |
| 延迟 | 强模型通常更慢，实时交互体验可能差 |
| 上下文窗口 | 长文档任务需要看上下文能力，不只是推理能力 |
| 工具能力 | 有些任务需要 tool calling / structured output / vision |
| 稳定性 | 有些模型输出更稳定，有些模型更发散 |
| 合规和部署 | 企业场景可能优先私有化、本地模型或指定供应商 |

所以这题你的方向对，但维度偏窄。

### 2.5 temperature 是否代表聪明程度？

你的回答正确。

需要修正一个措辞：“更高的温度代表模型的创新能力会越强”容易被误解。

更准确：

```text
temperature 越高，采样随机性越强，输出更多样、更发散；
但它不代表模型推理能力更强，也不等于更聪明。
```

---

## 3. 参数选择题批改

作业原题有 5 个场景，你只回答了 3 个：

1. 投诉/咨询/闲聊分类；
2. 生成 5 个不同风格的吵架训练回应；
3. 输出固定 JSON；
4. 分析复杂技术文章并总结架构；
5. 高频用户输入改写。

你漏了第 4、5 个，所以这部分不能给高分。

### 3.1 投诉/咨询类分类

你的答案：`0-0.2`，理由是稳定、可复现、快速、低成本。

判断：正确。

更完整答案：

```text
模型策略：小模型优先；必要时加规则或分类器兜底。
temperature：0-0.2。
原因：分类任务输出空间固定，不需要发散；重点是稳定、便宜、低延迟、可复现。生产中还应配合枚举约束和置信度阈值。
```

### 3.2 生成不同风格的吵架训练回应

你的答案：`0.6-0.8`，理由是需要不同回答和发散能力。

判断：基本正确，但不完整。

漏了安全边界。吵架帮手不能为了多样化而输出攻击、辱骂、威胁、歧视内容。

更完整答案：

```text
模型策略：中小模型生成候选；高风险场景可用更强模型做安全改写或评审。
temperature：0.6-0.8。
原因：用户需要多种表达风格，需要一定随机性；但必须用 Guardrails 限制人身攻击、威胁、歧视和冲突升级，并对候选结果做安全过滤。
```

### 3.3 固定 JSON 输出

你的答案：`0-0.2`，理由是稳定输出。

判断：不完整。

低 temperature 不能保证 JSON 合法。生产里固定 JSON 需要：

```text
structured output / JSON schema / function calling
后端 schema validation
失败 retry / repair
兜底错误返回
```

更完整答案：

```text
模型策略：支持 structured output / JSON schema 的模型优先；简单场景可用小模型，但必须有 schema validation。
temperature：0-0.2。
原因：结构化输出要求稳定和可解析。低 temperature 只能降低随机性，不能替代 schema、解析校验、重试修复和 fallback。
```

### 3.4 漏答：分析复杂技术文章并总结架构

参考答案：

```text
模型策略：强模型或长上下文模型；如果文章很长，先切分摘要再汇总。
temperature：0.2-0.4。
原因：这类任务需要理解架构、抽象层次、识别关键模块和风险，不是简单改写。temperature 不宜太高，否则容易脑补；也不必为 0，因为总结表达需要一定自然度。
```

### 3.5 漏答：高频用户输入改写

参考答案：

```text
模型策略：小模型优先；高频请求应考虑缓存、批处理或规则模板。
temperature：0.2-0.5，取决于是否需要多样化。
原因：输入改写通常不需要强推理，重点是低成本、低延迟和稳定风格。如果是客服/搜索 query 改写，应偏低温；如果是文案润色，可稍微提高。
```

---

## 4. 代码阅读题批改

### 4.1 request_id 的作用

你的回答正确。

更完整：

```text
request_id 用于唯一标识一次 LLM 调用，串联业务日志、模型调用日志、错误日志、监控上报和用户反馈。没有 request_id，线上出现异常时很难定位是哪次模型调用出了问题。
```

### 4.2 latency_ms 和 usage

你的回答基本正确。

需要更细：

- `latency_ms`：用于分析模型延迟、provider 抖动、网络问题、超时阈值和用户体验；
- `usage`：不仅是“成本”，还包括 input/output token，能判断 prompt 是否过长、输出是否异常、RAG 是否塞太多上下文。

### 4.3 mock provider

你的回答正确。

补充：mock provider 还可以用于：

- 单元测试；
- CI 环境；
- 教学演示；
- 离线开发；
- 固定响应回归测试；
- 避免 API key 泄露和真实成本。

### 4.4 retry 放在哪一层？

你说“加在 `_openai_compatible_generate` 上，对其封装”。这个答案只对了一半。

更合理的设计：

```text
retry 策略应该放在 LLM Client / Provider Adapter 边界处，而不是散落到业务层。
```

原因：

- 业务层不应该关心 provider 的瞬时错误；
- retry 需要区分错误类型：429、5xx、timeout 可重试；400、schema 错误、权限错误不应盲目重试；
- retry 应记录 retry_count 和最终失败原因；
- 不同 provider 的错误格式不同，Provider Adapter 可以做归一化。

所以满分表达：

```text
我会在 LLM Client 调用 Provider Adapter 的边界加 retry policy，对 timeout、429、5xx 等临时错误做指数退避重试；对参数错误、鉴权错误、schema 校验失败不盲目重试。retry_count、error_type 和最终状态要写入调用日志。
```

---

## 5. LLM Gateway 日志表批改

你列了 10 个字段，满足“至少 8 个字段”的数量要求，但生产完整性不足。

### 5.1 做得对的字段

| 字段 | 评价 |
|---|---|
| request_id | 必须有 |
| model | 必须有 |
| provider | 必须有 |
| latency | 必须有 |
| message | 可以有，但必须脱敏或采样 |
| error | 必须有，但应拆成 error_type / error_message |
| cost | 重要 |
| stop_reason | 方向对，但推荐叫 finish_reason |
| temperature | 重要参数字段 |

### 5.2 明确有问题的字段

#### max_token

你写：

```text
max_token | 上下文窗口 | 用于判断是否有超过限制，发生截断
```

这个不准确。

`max_tokens` 通常表示“本次最大输出 token 限制”，不是模型上下文窗口。上下文窗口一般是模型能力属性，例如 128k context window。

建议拆成：

```text
max_output_tokens：本次最大输出 token 限制
context_window：模型上下文窗口大小，可作为模型元数据，不一定每次记录
```

#### message

生产中不能直接明文记录完整 messages。

更安全：

```text
messages_hash
messages_preview_masked
input_redaction_status
sampled_payload_uri
```

只有在受控调试、脱敏和权限审批下，才记录完整 payload。

### 5.3 缺失的生产关键字段

你漏了这些：

| 字段 | 为什么需要 |
|---|---|
| trace_id | 串起业务请求、RAG、Tool、LLM 调用全链路 |
| user_id_hash / session_id | 定位用户维度问题，但避免明文隐私 |
| prompt_version | 判断异常是否由 prompt 改版造成 |
| input_tokens | 判断输入上下文是否过长 |
| output_tokens | 判断输出长度和成本 |
| total_tokens | 成本统计和用量趋势 |
| retry_count | 判断 provider 抖动或重试策略是否有效 |
| status | success / failed / timeout / fallback |
| error_type | timeout / rate_limit / auth / bad_request / provider_5xx |
| finish_reason | stop / length / tool_call / content_filter / error |
| environment | dev / staging / prod，排查环境差异 |
| prompt_hash | 不存明文 prompt 时仍能定位版本和内容变化 |

### 5.4 推荐的最小生产表

| 字段名 | 类型 | 说明 | 为什么需要 |
|---|---|---|---|
| id | string | 日志主键 | 唯一标识一条调用日志 |
| request_id | string | LLM 调用 ID | 定位单次模型调用 |
| trace_id | string | 业务链路 ID | 串联 API、RAG、Tool、LLM 全链路 |
| user_id_hash | string | 脱敏用户标识 | 支持用户维度排查，不暴露隐私 |
| session_id | string | 会话 ID | 分析多轮上下文问题 |
| provider | string | 模型供应商 | 区分 OpenAI、Anthropic、Azure、本地模型等 |
| model | string | 模型名称 | 判断质量、成本、延迟与模型选择关系 |
| prompt_version | string | prompt 版本 | 定位 prompt 改版导致的输出变化 |
| messages_hash | string | messages 脱敏 hash | 避免明文存储敏感上下文，同时支持定位 |
| temperature | float | 采样温度 | 排查输出发散或不稳定问题 |
| max_output_tokens | int | 最大输出 token | 判断输出是否被限制或截断 |
| input_tokens | int | 输入 token | 成本、延迟、上下文窗口分析 |
| output_tokens | int | 输出 token | 成本和输出异常分析 |
| total_tokens | int | 总 token | 成本统计和预算控制 |
| estimated_cost | decimal | 预估成本 | 用户/功能/模型维度成本治理 |
| latency_ms | int | 调用耗时 | 监控延迟、P95/P99 和 provider 抖动 |
| retry_count | int | 重试次数 | 判断稳定性和重试策略效果 |
| status | string | 调用状态 | success / failed / timeout / fallback |
| error_type | string | 错误类型 | 聚合错误、告警和降级策略 |
| error_message_masked | string | 脱敏错误信息 | 辅助排查，避免泄露敏感信息 |
| finish_reason | string | 结束原因 | 判断正常结束、长度截断、内容过滤、工具调用 |
| created_at | datetime | 创建时间 | 时间维度统计和问题回溯 |
| environment | string | 环境 | 区分 dev / staging / prod |

---

## 6. 面试题满分答案

题目：

> 你会如何把 LLM API 调用封装成生产可用的后端能力？

满分回答：

```text
我不会在业务代码里直接散落调用模型 SDK，而是会把 LLM API 封装成统一的 LLM Client 或 LLM Gateway。

在入口层，业务只提交标准化的 LLMRequest，例如 request_id、trace_id、model 或 model_policy、messages、temperature、max_output_tokens、prompt_version 等。messages 会由 Prompt Builder 或 Context Builder 统一构造，区分 system、user、assistant、tool 等角色，并避免把 prompt 拼接逻辑散落在各个业务模块里。

在 Gateway 内部，我会做几件事：第一，统一模型选择和 provider adapter，把 OpenAI、Anthropic、Azure、本地模型或 OpenAI-compatible 服务封装成一致接口，方便后续做模型路由和降级。第二，统一参数治理，比如 temperature、max tokens、timeout、streaming、structured output schema，避免业务随意配置导致输出不稳定。第三，统一可靠性处理，包括 timeout、可重试错误的指数退避、rate limit、fallback 和错误归一化。第四，统一输出解析，对于 JSON 或结构化场景使用 schema / function calling / structured output，并在后端做 validation、repair 或 fallback，而不是只依赖低 temperature。

同时，生产环境必须把可观测性做好。每次调用都要记录 request_id、trace_id、provider、model、prompt_version、temperature、max_output_tokens、input_tokens、output_tokens、total_tokens、latency_ms、estimated_cost、retry_count、status、error_type、finish_reason 等字段。messages 和模型输出不能默认明文全量入库，要做脱敏、hash 或采样，避免泄露用户隐私和业务敏感信息。

最后，我会把 LLM Gateway 当成一个外部推理依赖来治理，而不是普通函数调用。它需要配置管理、密钥管理、权限控制、成本预算、监控告警、日志审计、灰度发布和回归评估。这样业务层看到的是稳定、可观测、可降级的 AI 后端能力，而不是直接面对不稳定、昂贵且不可控的模型接口。
```

可以压缩成 1 分钟版本：

```text
我会把 LLM API 封装成统一的 LLM Client / Gateway，而不是在业务代码里直接调用模型 SDK。业务层只提交标准化请求，由 Prompt Builder 负责构造 messages，由 Gateway 统一管理模型选择、provider adapter、temperature、max tokens、timeout、重试、降级和结构化输出解析。

生产环境还必须记录 request_id、trace_id、provider、model、prompt_version、token usage、latency、cost、retry_count、status、error_type 和 finish_reason，用于排查质量、延迟和成本问题。messages 和模型输出要做脱敏或采样，不能无脑明文入库。

本质上，我会把 LLM API 当成一个不稳定但强大的外部推理依赖来治理，通过 Gateway 把它封装成可观测、可控、可降级、可评估的后端能力。
```

---

## 7. 本次作业最终结论

你这次作业说明你已经摆脱“只会调 API”的 demo 思维，能从 Gateway、参数、日志、成本和排查角度看 LLM API。

但还不能算扎实，主要因为：

1. 参数选择题漏答 2 个场景；
2. JSON 结构化输出仍然容易误以为低 temperature 就够；
3. Gateway 日志字段缺少生产排查的关键维度；
4. 对隐私脱敏、prompt_version、finish_reason、retry_count 的敏感度还不够；
5. 面试题你没有先自己答，后面必须训练自己组织 1 分钟表达。

下一节 Lesson 4 讲 Streaming 与后端接口封装时，要重点把今天的 Gateway 思维带进去：

```text
同步生成只是第一步；
真正生产可用的 AI 后端，还要处理 streaming、SSE、断连、首 token 延迟、取消、错误事件和 trace。
```
