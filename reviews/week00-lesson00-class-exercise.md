# Week 0 Lesson 0 课堂练习记录

> 课程：后端工程师的 AI 能力地图  
> 日期：2026-06-17  
> 类型：课堂练习 / 能力迁移诊断  
> 状态：已完成课堂练习，待完成课后作业

---

## 1. 用户回答原文整理

### 问题 1：最熟悉的后端能力

- Redis
- Kafka
- Go 服务
- MySQL
- 性能优化
- 接口设计

### 问题 2：后端能力到 AI 能力的迁移理解

| 后端能力 | 用户给出的 AI 迁移方向 |
|---|---|
| Redis | Prompt Cache / Embedding Cache / Context Cache |
| Kafka | Agent 工具调用失败重试、异步任务队列等 |
| Go 服务 | MCP、网关等 |
| MySQL | 向量数据库、记忆存储等 |
| 性能优化 | Agent 稳定快速输出结果 |
| 接口设计 | LLM API 设计、MCP、Skill 设计等 |

### 问题 3：优先补齐的 AI 能力

用户倾向：按照由浅入深的逻辑，系统学习 AI 知识能力。

---

## 2. 课堂诊断

### 2.1 优势

1. **工程迁移意识已经建立**  
   用户没有把 AI 学习理解成单纯 Prompt 或调 API，而是已经能把 Redis、Kafka、Go 服务、MySQL、接口设计映射到 AI 系统组件。

2. **后端工程底座强**  
   熟悉缓存、队列、服务、数据库、性能优化和接口设计，这些能力正好对应 AI 应用工程化里的缓存、异步任务、Tool Server、Memory Store、Trace、Gateway 和降级体系。

3. **学习顺序判断正确**  
   用户选择“由浅入深”而不是直接跳到复杂 Agent / LangGraph / MCP，说明当前更适合按 LLM API → Prompt → RAG → Tool → Agent → MCP → Eval 的路线推进。

### 2.2 需要补齐的点

1. **概念边界需要继续清晰化**  
   例如 MySQL 并不直接等于向量数据库，而是迁移到结构化业务数据、Memory 元数据、Trace Store；向量数据库更对应检索索引层。

2. **性能优化需要从“快”扩展到“稳、准、省、可观测”**  
   AI 系统里的性能不只是延迟，还包括 token 成本、首 token 时间、工具调用耗时、检索耗时、输出质量稳定性和失败恢复。

3. **MCP / Skill / Tool 的边界后续要重点讲**  
   用户已经提到了 MCP 和 Skill 设计，后续需要区分 Tool Calling、MCP Server、Agent Skill、工作流节点之间的关系。

---

## 3. 初步学习优先级建议

| 优先级 | 能力 | 原因 |
|---:|---|---|
| P0 | LLM API 基础 | 先理解 messages、model、token、temperature、streaming，是所有 AI 应用的入口 |
| P0 | Prompt / Structured Output | 解决模型输出不稳定、格式不可靠的问题 |
| P1 | RAG | 将 MySQL/文档/知识库经验迁移到检索增强生成 |
| P1 | Tool Calling | 将后端接口和工具封装能力迁移到模型可调用工具 |
| P2 | Agent Loop / Memory | 在 Tool 之上加入状态、规划和多轮任务执行 |
| P2 | MCP | 将工具能力标准化，连接本地系统和外部工具 |
| P3 | Eval / Trace / Cost | 补齐生产级 AI 应用的质量闭环和工程化能力 |

---

## 4. 老师点评

当前回答是合格的，而且方向很对。最大的亮点是：你已经不是从“AI 黑话”角度理解这些概念，而是在用后端系统组件去理解 AI 应用。

下一步不要急着学 LangGraph 或 MCP。先把最底层的 LLM API、Prompt 稳定性和结构化输出打牢。否则后面 Agent 写得越复杂，问题越难排查。

---

## 5. 下一步

1. 继续完成 Lesson 0 下半部分：把个人能力映射成 12 周学习优先级。
2. 完成课后作业：`assignments/week00-lesson00-homework.md`。
3. 作业提交后再更新 `PROGRESS.md`，并生成正式作业批改记录。
