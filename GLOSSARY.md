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
