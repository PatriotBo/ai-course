# AI Engineering Glossary

> AI 圈术语表。每周持续更新。
> 解释格式：一句话解释 → 后端类比 → 真实项目位置 → 面试表达。

---

## 1. Agent Loop

**一句话**：Agent 不是只调用一次模型，而是循环执行“观察 → 思考 → 行动 → 反馈 → 再思考”。

```text
Observe → Think → Act → Observe → ...
```

**后端类比**：类似一个消费任务的 worker，不断从任务状态中读取上下文，执行下一步，并把结果写回状态。

**真实项目位置**：LangGraph、OpenHands、SWE-agent、AutoGPT 类项目。

**面试表达**：Agent Loop 是让 LLM 从单轮回答升级为多步骤任务执行器的核心机制。

---

## 2. Harness

**一句话**：Harness 是用来运行、测试、评估模型或 Agent 的“外层框架”。

**后端类比**：类似测试框架 + 任务运行器 + 监控脚手架。

例子：
- Prompt harness：批量跑 prompt 测试集；
- Eval harness：自动评估回答质量；
- Agent harness：管理 Agent 的工具、状态、日志和结果。

**面试表达**：Harness 不是模型能力本身，而是让模型能力可测试、可复现、可迭代的工程外壳。

---

## 3. Hermes

**一句话**：Hermes 不是一个固定概念，常见上下文包括 Nous Hermes 模型系列、Agent 消息通信或工具调用相关命名。

**后端类比**：Hermes 在希腊神话里是信使，所以很多项目用它命名“通信层 / 消息层 / 指令模型”。

**学习注意**：遇到 Hermes 必须看具体上下文，不要以为它一定指同一个技术。

---

## 4. ReAct

**一句话**：Reasoning + Acting，让模型一边推理，一边调用工具行动。

```text
Thought → Action → Observation → Thought → Action → ...
```

**后端类比**：类似“决策逻辑 + 外部服务调用 + 结果回填”的循环。

---

## 5. Tool Use / Tool Calling

**一句话**：让模型调用外部函数、API、数据库、搜索、文件系统等工具。

**后端类比**：LLM 是调度器，工具是后端 service / RPC。

关键点：
- Tool Schema；
- 参数校验；
- 权限控制；
- 超时重试；
- 执行日志。

---

## 6. Function Calling

**一句话**：模型按结构化 schema 输出函数名和参数，由程序执行函数。

**后端类比**：类似让模型生成一段 RPC 调用请求，而不是自由文本。

---

## 7. RAG

**一句话**：Retrieval-Augmented Generation，先检索相关资料，再让模型基于资料回答。

**后端类比**：类似搜索系统 + 召回 + 排序 + 模板渲染，只是最后一步由 LLM 生成自然语言。

---

## 8. Embedding

**一句话**：把文本转成向量，让语义相近的内容在向量空间里距离更近。

**后端类比**：类似给文本生成一个“语义索引 key”。

---

## 9. Context Engineering

**一句话**：设计、筛选、压缩和组织传给模型的上下文。

**后端类比**：类似接口入参设计 + 缓存选择 + 查询聚合 + payload 控制。

---

## 10. Memory

**一句话**：让 Agent 能记住任务内或跨任务的信息。

分类：
- Short-term memory：当前任务/会话上下文；
- Long-term memory：跨会话长期信息；
- Episodic memory：过去经历；
- Semantic memory：事实知识。

---

## 11. Eval

**一句话**：评估 LLM / RAG / Agent 输出质量的方法和系统。

**后端类比**：单元测试 + 集成测试 + 回归测试 + 线上监控。

---

## 12. MCP

**一句话**：Model Context Protocol，AI 应用连接外部工具、数据和工作流的标准协议。

核心对象：
- Server；
- Client；
- Tools；
- Resources；
- Prompts。

**后端类比**：类似 AI 时代的标准 RPC / 插件协议。

---

## 13. Workflow vs Agent

**Workflow**：流程固定，路径可预测。
**Agent**：由模型动态决定下一步，路径不完全固定。

**后端类比**：
- Workflow = 编排好的状态机；
- Agent = 带推理能力的任务 worker。

---

## 14. Checkpoint

**一句话**：保存 Agent 执行状态，失败后可以恢复。

**后端类比**：任务执行状态表 / Kafka offset / workflow checkpoint。

---

## 15. Human-in-the-loop

**一句话**：让人在关键节点审批、修改、拒绝或继续 Agent 的执行。

**后端类比**：审批流 / 高危操作二次确认。

---

## 16. Guardrails

**一句话**：AI 系统的安全边界和规则约束。

包括：
- 输入过滤；
- 输出校验；
- 工具权限；
- 敏感操作审批；
- 合规策略。

---

## 17. Agentic AI

> 今日新增术语：2026-06-17
> 选择理由：近期 AI Agent、MCP、上下文工程相关讨论中，“Agentic AI”经常被用来描述从被动问答走向主动任务执行的 AI 系统。

**一句话**：Agentic AI 指具备目标理解、规划、工具调用、状态管理和多步骤执行能力的 AI 系统，而不是只回答问题的普通聊天模型。

**后端类比**：普通 Chatbot 像一次 RPC 调用；Agentic AI 更像一个带状态的任务编排系统，能拆任务、调服务、处理失败、记录过程并持续推进目标。

**关键组成**：
- Goal：明确任务目标；
- Planning：拆分步骤和选择路径；
- Tools：调用外部工具、API、数据库或文件系统；
- Memory / State：保存任务上下文、用户偏好和执行状态；
- Feedback Loop：根据执行结果继续调整；
- Guardrails：限制高风险动作，保证安全边界。

**容易混淆**：
- Agentic AI 不是单个模型名称；
- Agentic AI 不等于“多 Agent”；
- 只有一次模型调用的 Chatbot 通常不能算完整 Agentic AI。

**面试表达**：Agentic AI 的重点是把 LLM 从“回答器”升级为“任务执行系统”，工程上需要工具协议、状态存储、执行日志、失败恢复和评估闭环支撑。

---

## 18. Agent Harness

> 今日新增术语：2026-06-18  
> 选择理由：近期 AI Agent 工程讨论里，“Agent Harness”经常被用来描述模型之外真正决定 Agent 能否落地的执行框架，尤其适合和本节课的 harness / loop / ReAct 一起学习。

**一句话**：Agent Harness 是包在 LLM 外面的 Agent 运行框架，负责把模型能力接入工具、状态、记忆、权限、日志、评估和失败恢复。

**后端类比**：如果 LLM 是一个推理函数，Agent Harness 就像服务框架 + 任务调度器 + RPC 客户端 + 状态存储 + 日志系统 + 测试框架 + 安全沙箱。

**关键组成**：
- Tool Registry：注册工具及其 schema；
- Executor：执行工具调用，并处理超时、重试、错误；
- State / Memory：保存任务状态、上下文和长期记忆；
- Permission / Guardrails：限制高风险动作；
- Trace / Logs：记录模型调用、工具调用和 token 成本；
- Eval：评估 Agent 是否真的完成目标；
- Checkpoint：支持中断恢复和问题复盘。

**容易混淆**：
- Agent Harness 不是 LLM 本身；
- Agent Harness 不等于单个 prompt；
- Agent Harness 也不只是工具调用，它还包括状态、权限、日志、评估和恢复。

**面试表达**：生产级 Agent 的稳定性不只取决于模型本身，还取决于 Agent Harness 是否能把工具、状态、权限、Trace、Eval 和失败恢复管理好。

---

## 19. Agentic Workflow

> 今日新增术语：2026-06-18  
> 选择理由：近期 Agent 工程讨论中，越来越多资料强调企业级 AI 应用不是“更强模型 + 几个函数”，而是把模型放进可恢复、可观测、可治理、可扩展的工作流系统里；Agentic Workflow 正是描述这种从对话走向任务执行的关键概念。

**一句话**：Agentic Workflow 是由 LLM 参与决策的任务工作流，它把模型推理、工具调用、状态管理、人工审批、错误恢复和评估闭环组织成一个可运行的系统。

**不要强行类比**：它和传统固定工作流不完全一样。传统工作流的路径通常由代码预先写死；Agentic Workflow 中某些节点可以由模型根据上下文动态选择下一步，因此它既有 workflow 的可控性，也有 agent 的动态性。

**关键组成**：
- Goal：任务目标和完成标准；
- State：当前任务状态、上下文和中间结果；
- Model Decision：由模型判断下一步或生成结构化决策；
- Tools：执行搜索、数据库、文件、API 等外部操作；
- Human Gate：高风险节点由人审批；
- Checkpoint：关键状态可恢复；
- Trace / Eval：记录执行过程并评估结果质量。

**容易混淆**：
- Agentic Workflow 不等于纯 Agent Loop；它通常更强调可控的流程边界；
- Agentic Workflow 不等于传统 Workflow；它允许模型参与局部决策；
- Agentic Workflow 也不是某个具体框架，LangGraph、Dify Workflow、LlamaIndex Workflow 都可以实现类似思想。

**面试表达**：Agentic Workflow 的价值是把 LLM 的动态推理能力放进可控的工程流程里，让系统既能根据上下文灵活决策，又能通过状态、权限、checkpoint、trace 和 eval 保持生产可控。

---

## 20. Responses API

> 今日新增术语：2026-06-22  
> 选择理由：当前主流模型 API 正在从单次 chat completion 走向统一响应接口，Responses API 把多轮状态、工具调用、流式输出、上下文压缩和响应管理放进统一抽象中，适合作为 LLM API 基础课的补充概念。

**一句话**：Responses API 是一种统一的模型响应接口，用于把文本生成、多轮状态续接、工具调用、流式输出和响应管理组织到同一套 API 形态里。

**不要只背 API 名字**：不同厂商的字段和 SDK 会变，但背后的工程抽象更重要：输入、指令、上下文、模型参数、工具调用、流式事件、usage、trace 和错误治理。

**关键能力**：
- Stateful response：通过 response id 或上下文续接多轮交互；
- Streaming：逐步返回增量输出；
- Tool calling：让模型请求外部函数、Code Interpreter 或 MCP 工具；
- Response management：检索、删除或压缩历史响应；
- Guardrails：在输入和输出层面应用安全过滤。

**容易混淆**：
- Responses API 不等于 Agent；它只是更统一的模型响应接口；
- Responses API 不会自动解决业务状态管理，生产系统仍需要自己的 LLM Gateway、日志、权限和 Eval；
- 学习时不必死记某个 SDK 的写法，要掌握稳定抽象。

**面试表达**：Responses API 体现了模型接口从单次补全向统一响应与工具执行入口演进。工程上我会把它封装在 LLM Gateway 后面，统一处理模型参数、上下文续接、streaming、tool calling、usage、trace 和错误治理。

---

## 21. Server-Sent Events（SSE）

> 今日新增术语：2026-06-23
> 选择理由：LLM 应用中流式输出已经成为标准交互形态，近期工程文章持续讨论 SSE、WebSocket 和 HTTP chunked streaming 的取舍；本节课正好进入 Streaming 与后端接口封装。

**一句话**：SSE 是一种基于 HTTP 的服务端单向事件推送协议，常用于把 LLM 的增量文本输出实时推给浏览器。

**不要强行类比**：SSE 不是消息队列，也不是 WebSocket 的简化版。它更像一种浏览器友好的流式响应协议：客户端发起请求，服务端持续推送事件，直到完成或出错。

**关键组成**：
- `event`：事件类型，例如 `meta`、`delta`、`done`、`error`；
- `data`：事件数据，通常是 JSON 字符串；
- 空行：表示一个事件结束；
- `text/event-stream`：HTTP 响应类型；
- 长连接：服务端持续写入，客户端持续消费。

**容易混淆**：
- SSE 主要是服务端到客户端的单向推送；如果需要强双向实时交互，WebSocket 更合适；
- Streaming 改善的是首 token 可见时间和用户感知延迟，不一定减少完整生成总耗时；
- 中途失败时 HTTP status 通常已经发出，只能通过 `error` event 通知前端。

**面试表达**：LLM streaming 接口可以用 SSE 封装，后端把供应商增量输出转换为统一的 `meta/delta/done/error` 事件。这样前端不依赖具体模型供应商协议，后端也能统一做鉴权、日志、错误处理、限流和可观测。

---

## 22. Exponential Backoff with Jitter

> 今日新增术语：2026-07-02
> 选择理由：LLM API 生产环境里经常遇到 429 限流、网络抖动和 provider 5xx。官方文档和生产实践都推荐用指数退避处理可恢复错误，但不能无脑重试。

**一句话**：Exponential Backoff with Jitter 是一种重试等待策略，每次失败后按指数增长等待时间，并加入随机扰动，避免大量请求同时重试造成雪崩。

**不要强行类比**：它不是简单 sleep，也不是失败就重试。它是一种保护系统和下游 provider 的恢复策略，前提是先判断错误是否可重试。

**关键组成**：
- Retryable Error：只对 timeout、429、5xx 等短暂性错误重试；
- Max Attempts：限制最大尝试次数；
- Exponential Delay：等待时间按 1、2、4、8 秒增长；
- Max Delay：设置等待上限；
- Jitter：加入随机扰动，打散重试洪峰；
- Structured Log：记录 attempt、error_type、http_status、latency。

**容易混淆**：
- API key 错误、参数错误、余额不足、上下文超限不应该原样重试；
- 重试失败请求也可能消耗 rate limit；
- 加 retry 不等于系统可靠，必须配合 timeout、限流、fallback 和日志。

**面试表达**：我会在 LLM Gateway 层对可恢复错误使用有限次数的 exponential backoff with jitter。这样能提高短暂性错误的成功率，同时避免所有请求在同一时间重试，把 provider 或自己的服务打爆。

---

## 23. Prompt Contract

> 今日新增术语：2026-07-16
> 选择理由：Prompt Engineering 正从“技巧和咒语”转向可版本化、可测试的工程规格；本节课正好进入 Prompt 设计原则。

**一句话**：Prompt Contract 是用明确、可测试的方式描述 Prompt 的输入、指令、约束、输出格式和失败行为，让模型调用像接口契约一样可管理。

**关键组成**：
- `prompt_key`：Prompt 的稳定业务标识；
- `prompt_version`：本次使用的 Prompt 版本；
- Required Variables：调用方必须提供的输入变量；
- Instruction：模型要执行的任务；
- Context Boundary：规则与外部数据的边界；
- Constraints：事实、长度、受众、安全和不确定性约束；
- Output Contract：结果必须满足的结构；
- Failure Behavior：信息不足或冲突时应该怎么处理。

**容易混淆**：
- Prompt Contract 不是某一家模型厂商的正式协议；
- 它不能替代 JSON Schema、后端校验、权限控制和 Eval；
- Prompt 写得长不代表 Contract 更完整，关键是字段清楚且可验收。

**真实项目位置**：客服分类、事故摘要、RAG 回答、Tool 选择、Agent 决策等所有需要稳定模型行为的业务链路。

**面试表达**：我会把 Prompt 当成可版本化、可测试的业务契约，明确 required variables、instruction、context、constraints、output contract 和 failure behavior，并记录 prompt_key/version，通过固定测试集做回归，而不是凭感觉调字符串。
