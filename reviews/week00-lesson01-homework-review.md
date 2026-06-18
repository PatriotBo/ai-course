# Review：Week 0 Lesson 1 Homework

> 主题：AI 圈黑话课 1：harness / loop / hermes / ReAct  
> 提交日期：2026-06-18  
> 批改状态：已批改，通过  
> 下一课：Week 0 Lesson 2：真实项目选择方法

---

## 1. 总体评价

大哥，这次作业比课堂练习明显进步，尤其是第 4 题“吵架帮手 Agent Harness”已经从“不会做”推进到能拆出 Prompt、Tool、State、Guardrails 四个核心模块，这说明你开始从概念理解进入系统设计视角了。

综合评价：**通过，可以进入 Lesson 2。**

| 维度 | 评分 | 评价 |
|---|---:|---|
| Harness / LLM 边界 | 90 / 100 | 能清楚区分模型本体和工程运行环境 |
| Agent Harness 职责 | 85 / 100 | 已覆盖权限、工具、状态、失败、日志、评估等关键职责 |
| Agent Loop / ReAct 理解 | 82 / 100 | 整体正确，Thought / Action / Observation 边界比课堂练习更清楚 |
| 后端类比能力 | 78 / 100 | 类比方向对，但 Observation / Checkpoint 还需要补齐 |
| 系统设计能力 | 72 / 100 | 已能拆出主干模块，但缺 Memory、Trace、Eval、Budget、Retry 和最终输出 |
| 风险意识 | 75 / 100 | 风险列得对，但需要补对应工程手段 |
| 面试表达 | 85 / 100 | 表达已经比较完整，有工程化层次 |

---

## 2. 基础题批改

### 2.1 Harness 和 LLM 本身有什么区别？

你的回答核心正确：

> LLM 即大模型本身，自身不保存状态，没有记忆，只负责接受输入、推理和输出；Harness 是大模型运行的真实环境，包括工具注册、执行、参数校验、权限控制、状态记录、记忆存储、失败恢复、日志存储和结果评估等。

这是本课最重要的概念，你抓住了。

可以进一步压缩成面试表达：

```text
LLM 是推理和生成组件，Harness 是模型外层的工程运行环境。
LLM 本身不负责工具执行、权限、状态、日志、失败恢复和评估；这些生产级职责应该由 Harness 承担。
```

### 2.2 Agent Harness 通常负责哪些工程职责？

你列到：

- 权限控制；
- 工具调用；
- 状态记录；
- 结果评估；
- 失败恢复；
- 日志存储。

这是合格答案。建议以后再补 4 个词：

```text
参数校验 / Trace / 成本预算 / Checkpoint
```

完整一点可以是：

```text
Agent Harness 负责 Tool Registry、Tool Schema 校验、权限控制、状态管理、Memory、Trace、Eval、Retry、Checkpoint、Budget 和 Guardrails。
```

### 2.3 Agent Loop 和普通 Chatbot 的区别

你说普通 Chatbot 只能一问一答，没有记忆、状态和工具调用；Agent Loop 能拆解复杂任务，循环执行子任务，过程中产生中间结果、调用工具和观测结果。

这个理解是对的。

建议你以后加一句：

```text
Agent Loop 的关键不是“循环次数多”，而是每一轮都会基于状态和 Observation 决定下一步。
```

### 2.4 ReAct 中 Thought / Action / Observation 是什么？

你这次比课堂练习修正得很好：

| 阶段 | 你的理解 | 批改 |
|---|---|---|
| Thought | 推理思考，判断下一步、拆解目标、是否调工具 | 正确 |
| Action | 执行具体操作，通常是调用工具 | 正确 |
| Observation | 观测结果是否正常，判断是否拿到 Final Answer | 基本正确，但要区分 Observation 与 Eval |

小修正：

```text
Observation 更准确是“工具或外部环境返回给 Agent 的事实结果”。
判断是否符合预期、是否能 Final Answer，是下一轮 Thought 或 Eval Harness 的职责。
```

也就是说：

```text
Observation = 下游返回值 / 工具结果 / 错误信息
Eval / Thought = 判断结果质量和下一步
```

### 2.5 Hermes 为什么不能脱离上下文解释？

你的回答是对的：

> Hermes 在不同语境下有不同含义。

可以更完整一点：

```text
Hermes 不是像 MCP、RAG、ReAct 那样相对明确的标准概念，它可能是模型系列、通信层、工具桥接模块或项目代号。看到 Hermes 时要先看项目上下文，而不是直接套固定定义。
```

---

## 3. 后端类比题批改

你的类比：

| AI 概念 | 你的后端类比 | 批改 |
|---|---|---|
| Harness | 服务框架 + 测试框架 + 运行时 | 准确 |
| Agent Harness | Agent 执行框架 | 准确，但可以更具体 |
| Agent Loop | 状态机 | 对，但建议补 worker loop / workflow engine |
| ReAct | 决策逻辑 + 接口调用 + 回填 | 准确 |
| Observation | 结果断言 | 需要修正 |
| Checkpoint | 未回答 | 需要补齐 |

### 3.1 Observation 不等于结果断言

更准确：

```text
Observation = 下游返回值 / RPC response / 工具执行结果 / 错误信息
```

“结果断言”更像：

```text
Eval / Test Assertion / Quality Check
```

### 3.2 Checkpoint 要补上

推荐类比：

```text
Checkpoint → Kafka offset / workflow checkpoint / 任务状态快照 / 断点续跑记录
```

它解决的是：

```text
长任务执行到一半失败后，能从最近状态恢复，而不是从头再来。
```

---

## 4. 系统设计题批改：吵架帮手 Agent Harness

你的设计：

```text
用户输入
  ↓
Prompt 管理模块：负责设计场景，模式，难度，角色等
  ↓
Tool 管理模块：负责工具调用，如评分工具等
  ↓
状态管理模块：负责本次训练的中间状态管理，如轮次记录、对话记录、token 使用量等
  ↓
Guardrails 模块：限制模型输出，不要有人身攻击、威胁、歧视、侮辱等话语
```

这已经过了及格线。相比课堂练习时“不会做”，这次已经能拆出 4 个核心模块：

- Prompt；
- Tool；
- State；
- Guardrails。

### 4.1 还缺哪些模块？

建议补齐成生产级版本：

```text
用户输入
  ↓
Input Guardrails：检查是否存在极端攻击、隐私、违法风险
  ↓
Prompt 管理：加载场景、角色、难度、训练目标
  ↓
State / Memory：记录轮次、对话、用户薄弱点、历史表现
  ↓
Tool Router：调用评分、情绪检测、话术建议等工具
  ↓
Agent Loop：根据评分和用户表现决定继续追问、升级难度或结束
  ↓
Eval / Score：输出逻辑、情绪控制、说服力、攻击性等评分
  ↓
Trace / Log：记录 Prompt 版本、工具调用、模型输出和评分依据
  ↓
Budget / Limit：限制轮数、token、耗时、工具调用次数
  ↓
最终输出：训练复盘报告 + 下一次训练建议
```

### 4.2 你这题下一步要重点练什么？

你现在会拆“功能模块”，下一步要练“运行闭环”：

```text
输入 → 状态 → 工具 → 观测 → 评分 → 决策 → 继续 / 结束 → 复盘
```

Agent 不是把模块列出来就完了，关键是这些模块如何在 Loop 中协作。

---

## 5. 风险题批改

你列的风险都对：

1. 死循环；
2. token 使用太多，成本不可控；
3. 超时，无法得到结果；
4. 工具乱调；
5. 错误无法处理，任务中间崩掉。

不过题目要求是“风险 + 对应工程手段”，你这次只列了风险，缺少治理方案。

补齐如下：

| 风险 | 工程手段 |
|---|---|
| 死循环 | max steps、timeout、人工中断、Loop 状态检测 |
| token 成本不可控 | token budget、模型路由、上下文压缩、缓存、成本告警 |
| 超时无结果 | request timeout、异步任务、fallback answer、任务恢复 |
| 工具乱调 | tool whitelist、权限控制、schema 校验、human approval |
| 错误无法处理 | retry、circuit breaker、checkpoint、DLQ、人工补偿 |

这类题以后一定要形成条件反射：

```text
风险不能只说现象，必须配工程手段。
```

---

## 6. 面试题批改

你的回答质量不错：

> Agent Harness 是保证 Agent 能够可靠、可控、低成本运行的真实环境，包括工具调用、失败处理、日志记录、权限控制、参数校验、成本控制、结果评估、状态管理等。

这个已经具备面试表达雏形。

我帮你整理成 1 分钟版本：

```text
我理解 Agent Harness 是 Agent 外层的工程运行环境。LLM 本身主要负责推理和生成，但生产级 Agent 还需要工具注册和调用、参数校验、权限控制、状态管理、Trace 日志、失败恢复、成本控制和 Eval 评估。

如果没有 Harness，模型只能像普通 Chatbot 一样做单轮回答，无法可靠地执行多步骤任务。真正上线时，Agent 的稳定性不只取决于模型能力，还取决于 Harness 能否把 Tool、State、Trace、Eval、Guardrails 和 Budget 这些工程边界管理好。
```

建议你后面就按这个版本背。

---

## 7. 本次关键修正

1. **Observation 不是结果断言**  
   Observation 是工具或环境返回的事实结果；断言和质量判断属于 Eval / Test / 下一轮 Thought。

2. **Checkpoint 要补进你的后端类比词库**  
   Checkpoint 类似 Kafka offset、任务状态快照、workflow checkpoint，用于恢复、重放和排查。

3. **风险题必须配工程手段**  
   面试中只说“可能死循环、成本高”不够，要继续说 max steps、timeout、budget、tool whitelist、checkpoint、fallback。

4. **Agent Harness 设计要形成闭环**  
   不只是列 Prompt / Tool / State / Guardrails，还要说明 Loop 如何运行、如何评分、如何记录、如何退出和如何复盘。

---

## 8. Lesson 1 结论

本节课你已经掌握：

- Harness 和 LLM 的边界；
- Agent Harness 的主要工程职责；
- Agent Loop 和普通 Chatbot 的区别；
- ReAct 的 Thought / Action / Observation；
- Hermes 不能脱离上下文解释；
- 初步的 Agent Harness 系统设计方法。

仍需继续强化：

- Checkpoint；
- Observation 与 Eval 的边界；
- 风险 → 工程手段的对应表达；
- Agent Harness 的完整运行闭环设计。

结论：**Lesson 1 通过。下一课进入 Week 0 Lesson 2：真实项目选择方法。**
