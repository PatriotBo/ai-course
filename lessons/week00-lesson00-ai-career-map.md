# Week 0 Lesson 0：后端工程师的 AI 能力地图

> 状态：备课单已生成，等待正式授课  
> 预计时长：60-75 分钟  
> 本节类型：路线认知 + 能力地图 + 诊断课

---

## 1. 本节课目标

学完本节课，你应该能回答：

1. AI 应用工程师到底和传统后端有什么不同；
2. Agent 工程师到底要会什么；
3. 当前招聘市场里的 AI 能力要求可以拆成哪些模块；
4. 你已有的后端能力如何迁移到 AI 方向；
5. 接下来 12 周每个阶段学什么，为什么这么安排。

---

## 2. 为什么先上这节课

很多后端转 AI 的人会陷入两个误区：

### 误区 A：以为会调 API 就是 AI 工程师

```text
用户问题 → 调模型 → 返回答案
```

这只是 demo，不是工程能力。

真实 AI 系统要处理：
- Prompt 稳定性；
- 结构化输出；
- 工具调用；
- 检索；
- 记忆；
- 权限；
- 成本；
- 延迟；
- 评估；
- 可观测；
- 失败恢复。

### 误区 B：以为要先学深度学习数学

对 AI 应用 / Agent 工程师来说，优先级不是从反向传播开始，而是：

```text
模型 API 使用
  ↓
应用架构
  ↓
RAG / Tool / Agent
  ↓
工程化和评估
  ↓
再按需补模型原理
```

---

## 3. 后端工程师能力迁移图

```text
传统后端能力                         AI 应用工程能力
────────────────────────────────────────────────────────
API 设计          ─────────────→   LLM API Gateway / Agent API
数据库建模        ─────────────→   Vector DB / Memory Store / Trace Store
缓存 Redis        ─────────────→   Prompt Cache / Embedding Cache / Context Cache
消息队列 Kafka    ─────────────→   Async Agent Task / Retry / DLQ
RPC/微服务        ─────────────→   Tool Server / MCP Server / Model Router
配置中心          ─────────────→   Prompt Version / Model Config / Eval Config
日志监控          ─────────────→   Agent Trace / Tool Call Log / Token Cost
权限系统          ─────────────→   Tool Permission / Human Approval / Guardrails
任务调度          ─────────────→   Agent Workflow / Planner / Executor
容灾降级          ─────────────→   Model Fallback / Tool Fallback / Safe Reply
```

核心结论：

> 你不是从零转行，而是把后端工程能力迁移到 AI 系统里。

---

## 4. AI 应用工程师能力分层

```text
Level 0：会用 ChatGPT
  ↓
Level 1：会调用 LLM API
  ↓
Level 2：会做稳定 Prompt 和结构化输出
  ↓
Level 3：会做 RAG 和知识库
  ↓
Level 4：会做 Tool Calling
  ↓
Level 5：会做 Agent Loop / Memory / Planning
  ↓
Level 6：会做 LangGraph / Multi-Agent / MCP
  ↓
Level 7：会做 Eval / Trace / Cost / Production
  ↓
Level 8：能做完整 AI 产品并讲清楚架构
```

你当前目标：从传统后端直接切到 Level 3-6，并逐步补 Level 7。

---

## 5. 当前招聘岗位常见要求拆解

| 招聘描述 | 背后能力 |
|---|---|
| 熟悉 LLM API | 模型调用、参数、流式输出、错误处理 |
| 熟悉 Prompt Engineering | Prompt 模板、few-shot、结构化输出、评估 |
| 熟悉 RAG | Embedding、向量数据库、chunking、rerank、引用 |
| 熟悉 Agent 开发 | Agent Loop、工具调用、规划、记忆、状态管理 |
| 熟悉 LangChain / LangGraph | 工作流编排、checkpoint、多 Agent |
| 熟悉 MCP | 外部工具协议、server/client、权限边界 |
| 有 AI 应用落地经验 | 服务化、部署、成本控制、日志监控 |
| 有 Eval 经验 | 测试集、指标、回归测试、质量闭环 |

---

## 6. 本课程的训练目标

到课程结束，你应该能做 3 件事：

### 1. 面试能讲

你能清楚解释：
- RAG 怎么做；
- Agent 和 Workflow 区别；
- Tool Calling 怎么设计；
- Memory 怎么设计；
- MCP 是什么；
- AI 应用怎么评估；
- 生产环境有哪些坑。

### 2. 代码能写

你能写出：
- LLM API 服务；
- RAG 知识库；
- Tool-Using Agent；
- LangGraph Workflow；
- MCP Server；
- Eval 脚本。

### 3. 项目能展示

你有至少 2 个能写进简历的项目：
- 一个 RAG / 知识库项目；
- 一个 Agent / 多 Agent 项目；
- 最好再有一个结合你兴趣的 AI 投研或吵架帮手 Agent 项目。

---

## 7. 本节课堂练习

### 练习：把你的后端经验映射成 AI 能力

请回答：

1. 你最熟悉的后端能力是什么？例如 Redis、Kafka、MySQL、Go 服务、RPC、定时任务等。
2. 它在 AI 应用系统里可以迁移成什么能力？
3. 你最想优先补齐哪 3 个 AI 能力？

示例：

```text
我熟悉 Kafka 消费失败重试
  ↓
迁移到 Agent 任务队列：工具调用失败重试、死信任务、人工补偿
```

---

## 8. 本节作业

详见：`assignments/week00-lesson00-homework.md`

---

## 9. 参考资料

必读：
- DeepLearning.AI Agentic AI 课程大纲
- OpenAI Cookbook：Structured Outputs / RAG / Evals 相关示例
- LangGraph 官方文档：State / Node / Edge / Checkpoint

选读：
- LlamaIndex 官方文档：Data Connectors / Query Engines / Workflows
- MCP 官方文档：Server / Client / Tools / Resources / Prompts

---

## 10. 面试表达模板

当面试官问：

> 你作为后端开发，为什么能做 AI 应用开发？

可以这样答：

```text
我理解 AI 应用本质上不是简单调模型，而是一个以 LLM 为核心的新型后端系统。
传统后端里的 API 设计、任务调度、缓存、队列、权限、日志、监控、降级，在 AI 系统里分别对应 LLM Gateway、Agent Workflow、Prompt/Embedding Cache、Tool Queue、Tool Permission、Agent Trace、Cost Monitoring 和 Model Fallback。
我现在的学习路径也是围绕这些能力展开：先掌握 LLM API 和 Prompt，再做 RAG、Tool Calling、Agent、MCP，最后补齐 Eval 和生产工程化。
```
