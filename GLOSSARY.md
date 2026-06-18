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
