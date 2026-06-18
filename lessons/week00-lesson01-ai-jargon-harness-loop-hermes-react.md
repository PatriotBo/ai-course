# Week 0 Lesson 1：AI 圈黑话课 1：harness / loop / hermes / ReAct

> 状态：讲义已生成，准备正式授课  
> 预计时长：60-75 分钟  
> 本节类型：概念索引 + 后端类比 + 面试表达

---

## 1. 本节课目标

学完本节课，你应该能回答：

1. AI 圈常说的 harness 到底是什么；
2. Agent Loop 和普通一次性 LLM 调用有什么区别；
3. Hermes 为什么不能脱离上下文解释；
4. ReAct 的 Thought / Action / Observation 循环解决什么问题；
5. 这些概念在真实 Agent 项目里分别落在哪里；
6. 面试时如何用后端工程师听得懂的话解释这些黑话。

---

## 2. 为什么要单独学 AI 黑话

AI 应用开发里有一个很烦人的点：很多词不是传统软件工程里的标准术语，而是从论文、开源项目、模型社区、框架文档里混出来的。

比如：

```text
harness
loop
ReAct
Hermes
agentic
context engineering
guardrails
checkpoint
```

如果不先建立概念索引，后面看 LangGraph、OpenAI Cookbook、Claude Code、MCP、TradingAgents、OpenHands 时，很容易出现：

```text
每个单词都认识，但不知道它在系统里到底是哪个模块。
```

所以本节课的目标不是背术语，而是建立一套翻译方法：

```text
AI 黑话
  ↓
对应的系统职责
  ↓
后端类比
  ↓
真实项目位置
  ↓
面试表达
```

---

## 3. 今日新增热词：Agent Harness

> 选择理由：近期 AI Agent 工程讨论里，Agent Harness 经常被用来描述“模型之外真正决定 Agent 能不能落地的那层执行框架”。相比单纯说 harness，Agent Harness 更强调围绕 Agent 的工具、状态、权限、日志、评估和恢复能力。

### 一句话解释

**Agent Harness 是包在 LLM 外面的 Agent 运行框架，负责把模型能力接入工具、状态、记忆、权限、日志、评估和失败恢复。**

### 后端类比

如果 LLM 是一个“推理函数”，Agent Harness 就像：

```text
服务框架 + 任务调度器 + RPC 客户端 + 状态存储 + 日志系统 + 测试框架 + 安全沙箱
```

没有 harness 的 Agent 大概是：

```text
模型说下一步要干什么
  ↓
人肉执行 / 简单脚本执行
```

有 harness 的 Agent 是：

```text
模型提出行动意图
  ↓
Harness 校验工具 schema / 权限 / 参数
  ↓
执行工具
  ↓
记录 trace / token cost / tool log
  ↓
把 observation 写回状态
  ↓
决定继续、终止、重试或转人工
```

### 面试表达

```text
我理解 Agent Harness 是模型之外的工程执行层。LLM 负责推理和决策，但工具注册、参数校验、权限控制、状态持久化、执行日志、失败重试和 Eval 都应该由 Harness 承担。生产级 Agent 的稳定性更多取决于 Harness，而不是只看模型本身。
```

---

## 4. Harness：模型外面的工程外壳

### 4.1 一句话

Harness 是用来**运行、测试、评估模型或 Agent 的外层框架**。

它不是模型，也不是 prompt 本身，而是把模型放进一个可运行、可测试、可观测的工程环境里。

### 4.2 后端类比

传统后端里，你不会只写一个函数就上线。你会有：

```text
HTTP 框架
配置加载
日志
监控
测试
鉴权
超时
重试
灰度
CI
```

AI 里的 harness 也类似：

```text
Prompt Harness：批量运行 prompt 测试集
Eval Harness：自动评估回答质量
Agent Harness：管理工具、状态、权限、日志和执行循环
Benchmark Harness：跑模型或 Agent 性能测试
```

### 4.3 常见错误理解

错误：

```text
Harness 是某个具体框架。
```

更准确：

```text
Harness 是一种工程角色。不同项目里的 harness 实现可以不同。
```

比如 Claude Code、Cursor、Cline、OpenHands、SWE-agent 都可以看作有自己的 Agent Harness：它们都要负责工具调用、文件操作、安全边界、状态追踪和结果展示。

---

## 5. Loop：Agent 为什么不是一次调用

### 5.1 普通 LLM 调用

```text
用户输入
  ↓
LLM 生成回答
  ↓
结束
```

这是一次性调用。

### 5.2 Agent Loop

```text
Observe：读取任务和当前状态
  ↓
Think / Plan：判断下一步
  ↓
Act：调用工具或生成操作
  ↓
Observe：接收工具结果
  ↓
Repeat：继续判断是否完成
```

### 5.3 后端类比

Agent Loop 很像一个带状态的任务 worker：

```text
while not done:
    task_state = load_state(task_id)
    next_step = decide(task_state)
    result = execute(next_step)
    save_state(task_id, result)
```

区别是：传统 worker 的 next_step 通常是代码写死的；Agent 的 next_step 可能由 LLM 根据上下文动态决定。

### 5.4 Loop 的工程风险

Agent Loop 不是越长越好，它会带来问题：

| 风险 | 工程处理方式 |
|---|---|
| 死循环 | max steps / timeout |
| 工具乱调 | tool permission / whitelist |
| 成本失控 | token budget / cost limit |
| 状态污染 | state schema / context pruning |
| 错误累积 | checkpoint / rollback / human review |

---

## 6. Hermes：不要脱离上下文解释

### 6.1 一句话

Hermes 不是一个统一标准术语。它在不同上下文里可能表示：

1. Nous Hermes 模型系列；
2. 某个项目里的消息通信层；
3. 某个 Agent 框架里的工具调用模块；
4. 某个产品或内部模块代号。

### 6.2 为什么常见

Hermes 在希腊神话里是“信使”，所以很多工程项目喜欢用它命名：

```text
消息传递
任务分发
模型通信
工具桥接
指令跟随模型
```

### 6.3 学习方法

遇到 Hermes，第一步不是背定义，而是问：

```text
这个 Hermes 出现在什么项目？
它是模型？协议？模块？服务？工具？
输入是什么？输出是什么？
它连接了哪些组件？
```

### 6.4 面试表达

```text
Hermes 不是一个固定标准，我会先看它所在项目的上下文。很多项目用 Hermes 命名通信层、模型系列或工具桥接模块，所以不能把它和 MCP、ReAct 这种明确概念混为一谈。
```

---

## 7. ReAct：Reasoning + Acting

### 7.1 一句话

ReAct = **Reasoning + Acting**，让模型一边推理，一边行动。

典型循环：

```text
Thought：我需要先查什么
Action：调用搜索工具
Observation：工具返回结果
Thought：基于结果继续判断
Action：再调用计算或数据库工具
Observation：返回结果
Final Answer：给出最终答案
```

### 7.2 它解决的问题

普通 LLM 的问题：

```text
只能凭已有上下文回答，容易瞎猜。
```

ReAct 的思路：

```text
别一次性回答。
先思考下一步该查什么，调用工具拿到观察结果，再继续推理。
```

### 7.3 后端类比

传统后端：

```text
业务代码决定调用哪个 service
RPC 返回结果
业务代码继续处理
```

ReAct：

```text
LLM 决定需要哪个工具
Harness 执行工具
Observation 写回上下文
LLM 继续决策
```

### 7.4 ReAct 和 Agent Loop 的关系

可以这么记：

```text
Agent Loop 是大框架：循环执行任务。
ReAct 是一种常见的 Loop 模式：推理和行动交替发生。
```

---

## 8. 四个词放在一张图里

```text
用户目标
  ↓
Agent Harness
  ├─ 管理 Prompt / Tools / State / Memory / Logs / Eval
  ↓
Agent Loop
  ├─ Observe → Think → Act → Observe
  ↓
ReAct Pattern
  ├─ Thought → Action → Observation → Thought
  ↓
Tools / APIs / DB / Files / Search
  ↓
Observation 写回状态
  ↓
继续 or 结束
```

Hermes 不放在固定位置，因为它取决于项目上下文。

---

## 9. 和你后端经验的对应关系

| AI 术语 | 后端对应物 | 你应关注的工程问题 |
|---|---|---|
| Harness | 服务框架 + 测试框架 + 运行器 | 怎么让模型能力可运行、可测试、可观测 |
| Agent Harness | Agent 执行框架 | 工具注册、状态、权限、日志、失败恢复 |
| Loop | worker 循环 / 状态机 | 死循环、超时、重试、状态持久化 |
| ReAct | 决策逻辑 + RPC 调用 + 回填 | 工具选择是否正确，Observation 如何进入上下文 |
| Hermes | 项目代号/通信层/模型名 | 先看上下文，不强行套定义 |

---

## 10. 本节课堂练习

请用自己的话回答：

1. Harness 和 LLM 本身有什么区别？
2. Agent Loop 为什么需要状态管理？
3. ReAct 的 Thought / Action / Observation 分别对应后端系统里的什么？
4. 如果你设计一个“吵架帮手 Agent”，它的 Agent Harness 至少要管理哪些东西？

---

## 11. 本节作业

详见：`assignments/week00-lesson01-homework.md`

---

## 12. 面试表达模板

当面试官问：

> 你怎么理解 Agent Harness、Agent Loop 和 ReAct？

可以这样答：

```text
我会把它们分成三层理解。

第一层是 Agent Harness，它是模型之外的工程执行层，负责工具注册、参数校验、权限控制、状态管理、日志、失败恢复和 Eval。

第二层是 Agent Loop，它让 Agent 不是一次模型调用，而是围绕任务状态循环执行 Observe、Think、Act、Observe，直到完成或触发终止条件。

第三层是 ReAct，它是一种常见的 Agent Loop 模式，把推理和行动交替组织成 Thought、Action、Observation。LLM 决定下一步要调用什么工具，Harness 执行工具并把 Observation 写回上下文。

所以生产级 Agent 的关键不只是模型聪明，而是 Harness、状态、工具、安全边界和评估闭环做得是否扎实。
```
