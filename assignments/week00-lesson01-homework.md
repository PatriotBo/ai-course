# Homework：Week 0 Lesson 1

> 主题：AI 圈黑话课 1：harness / loop / hermes / ReAct  
> 预计耗时：30-45 分钟

---

## 1. 基础题

请用自己的话回答：

1. Harness 和 LLM 本身有什么区别？
2. Agent Harness 通常要负责哪些工程职责？至少列 5 个。
3. Agent Loop 和普通 Chatbot 的一次性回答有什么区别？
4. ReAct 中的 Thought、Action、Observation 分别是什么意思？
5. 为什么 Hermes 不能脱离具体项目上下文解释？

---

## 2. 后端类比题

请把下面 AI 概念映射到你熟悉的后端系统组件，并说明原因。

| AI 概念 | 后端类比 | 为什么这么类比 |
|---|---|---|
| Harness |  |  |
| Agent Harness |  |  |
| Agent Loop |  |  |
| ReAct |  |  |
| Observation |  |  |
| Checkpoint |  |  |

---

## 3. 系统设计题

假设你要设计一个“吵架帮手 Agent”，它不是一次性聊天，而是要根据用户表现进行多轮训练。

请画出它的 Agent Harness 至少包含哪些模块：

```text
用户输入
  ↓
模块 1：？
  ↓
模块 2：？
  ↓
模块 3：？
  ↓
模块 4：？
  ↓
最终输出：？
```

要求至少包含以下关键词中的 4 个：

```text
Prompt
Tool
Memory / State
Score
Trace
Guardrails
Retry
Eval
```

---

## 4. 风险题

Agent Loop 如果没有工程约束，可能出现哪些问题？请至少列 5 个，并写出对应的工程手段。

示例：

| 风险 | 工程手段 |
|---|---|
| 死循环 | max steps / timeout |

---

## 5. 面试题

请准备 1 分钟回答：

> 你如何理解 Agent Harness？为什么说生产级 Agent 的关键不只是模型本身？

要求：

- 必须包含 Tool、State、Trace、Eval 至少两个关键词；
- 要能用后端工程师听得懂的方式解释；
- 不要只说“它是一个框架”，要讲清楚它负责什么。

---

## 6. 提交方式

把答案直接发给我即可。我会按以下维度批改：

1. 是否区分清楚 Harness / Agent Harness / Agent Loop / ReAct；
2. 是否能用后端类比解释概念；
3. 是否有工程边界意识；
4. 系统设计是否包含状态、工具、安全、评估；
5. 面试表达是否清楚、有层次。

---

## 7. 本次提交与批改记录

> 状态：已提交，已批改  
> 提交日期：2026-06-18  
> 完整批改记录：`../reviews/week00-lesson01-homework-review.md`

### 7.1 用户提交摘要

#### 基础题

1. **Harness 和 LLM 的区别**
   LLM 是大模型本身，不保存状态和记忆，只负责接受输入、推理和输出；Harness 是模型运行的真实工程环境，负责工具注册、执行、参数校验、权限控制、状态记录、记忆存储、失败恢复、日志和评估。

2. **Agent Harness 职责**
   用户列出权限控制、工具调用、状态记录、结果评估、失败恢复、日志存储等职责。

3. **Agent Loop 和 Chatbot 的区别**
   Chatbot 更像一次性问答；Agent Loop 能把复杂任务拆成子任务，多轮执行、调用工具、处理中间结果和 Observation。

4. **ReAct 理解**
   Thought 是推理和判断下一步；Action 是执行具体操作，通常是工具调用；Observation 是观测工具/环境返回结果，并判断是否进入 Final Answer 或继续循环。

5. **Hermes**
   Hermes 在不同语境下有不同含义，不能脱离上下文解释。

#### 后端类比题

| AI 概念 | 用户类比 | 批改要点 |
|---|---|---|
| Harness | 服务框架 + 测试框架 + 运行时 | 准确 |
| Agent Harness | Agent 执行框架 | 准确，但可继续展开 Tool / State / Trace / Eval |
| Agent Loop | 状态机 | 对，建议补 worker loop / workflow engine |
| ReAct | 决策逻辑 + 接口调用 + 回填 | 准确 |
| Observation | 结果断言 | 需修正：Observation 是下游返回值/工具结果，断言更接近 Eval |
| Checkpoint | 未回答 | 需补：类似 Kafka offset / 任务状态快照 / workflow checkpoint |

### 7.2 批改结论

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

### 7.3 本次重点修正

1. **Observation 不是结果断言**  
   Observation 是工具或环境返回的事实结果；断言和质量判断属于 Eval / Test / 下一轮 Thought。

2. **Checkpoint 要补进后端类比词库**  
   Checkpoint 类似 Kafka offset、任务状态快照、workflow checkpoint，用于恢复、重放和排查。

3. **风险题必须配工程手段**  
   风险不能只说现象，需要配套 max steps、timeout、budget、tool whitelist、checkpoint、fallback 等治理方案。

4. **Agent Harness 设计要形成闭环**  
   不只是列 Prompt / Tool / State / Guardrails，还要说明 Loop 如何运行、如何评分、如何记录、如何退出和如何复盘。

### 7.4 下一节课衔接

下一课：**Week 0 Lesson 2：真实项目选择方法**。

进入 Lesson 2 前，需要带着这三个问题：

1. 什么样的 GitHub AI 项目适合作为学习项目？
2. 如何区分 toy demo、框架样例和可简历化项目？
3. 如何从项目中拆出可复刻、可改造、可展示的工程资产？
