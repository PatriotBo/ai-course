# Week 0 Lesson 2：真实项目选择方法

> 状态：正式授课中  
> 预计时长：60-75 分钟  
> 本节类型：项目选型课 + GitHub 项目阅读方法 + 作品集规划课  
> 今日新增术语：Agentic Workflow

---

## 0. 本节课为什么重要

前两节课解决的是“能力地图”和“基础术语”。从这一节开始，我们要解决一个更现实的问题：

> 你到底应该复刻、拆解、改造什么真实项目，才能真正转向 AI 应用 / Agent 工程师？

很多人学 AI 应用会犯一个严重错误：

```text
课程看了很多
Demo 跑了很多
Prompt 写了很多
但最后没有一个像样的项目能展示
```

这会导致三个后果：

1. 面试时只能讲概念，讲不出系统；
2. 简历上只能写“熟悉 RAG / Agent”，没有证据；
3. 真做产品时不知道一个 AI 项目从数据、工具、状态、评估到部署到底怎么闭环。

所以本节课不是让你随便挑一个 GitHub repo，而是建立一套**真实项目选择方法**：

```text
目标定位 → 项目分类 → 筛选指标 → 阅读方法 → 复刻边界 → 改造路径 → 简历表达
```

这节课的产出不是代码，而是：

```text
项目候选清单 + 选型评分表 + 第一阶段复刻项目方向
```

---

## 1. 先定义：什么叫“适合学习的真实 AI 项目”

不是所有 star 多的项目都适合现在学。

一个适合你当前阶段的真实项目，应该满足 5 个条件：

| 条件 | 含义 | 为什么重要 |
|---|---|---|
| 能看懂主链路 | 你能在 1-2 天内画出输入、处理、输出 | 否则只会复制，不会理解 |
| 能本地跑最小路径 | 有清晰 README / example / demo | 否则大量时间耗在环境问题 |
| 涉及核心 AI 能力 | LLM API、RAG、Tool、Agent、Memory、Eval 至少命中 1-2 个 | 才能迁移到课程能力 |
| 可裁剪 | 可以只复刻一小块，而不是吃完整个平台 | 对个人学习更现实 |
| 可改造成你的项目 | 能和 AI 投研、吵架帮手、知识库、Coding Agent 等方向结合 | 才能形成作品集 |

反过来，不适合当前阶段的项目通常有这些特征：

- 依赖特别重，启动需要十几个服务；
- 主要价值在前端 UI，不在 AI 工程链路；
- 代码量巨大，但核心链路藏得很深；
- 文档差，跑不起来；
- 只是玩具 prompt demo，没有工程价值；
- 需要昂贵外部 API 或复杂账号权限；
- 你无法解释它和自己转型目标有什么关系。

---

## 2. 真实项目的 6 种类型

AI 项目不能只按“RAG / Agent / MCP”粗暴分类。更实用的是按**学习价值**分类。

### 2.1 Cookbook 型项目

代表：

- OpenAI Cookbook
- Anthropic Cookbook
- LangChain templates
- LlamaIndex examples

特点：

```text
小而清晰，覆盖单点能力，适合快速学习 API / RAG / Tool / Eval 的标准写法。
```

优势：

- 容易跑通；
- 代码短；
- 适合建立第一手感；
- 适合课程早期。

缺点：

- 通常不是完整产品；
- 工程化不一定完整；
- 简历价值有限，必须二次改造。

适合阶段：

```text
Week 1-5
```

---

### 2.2 Framework Example 型项目

代表：

- LangGraph examples
- LlamaIndex workflows
- CrewAI examples
- AutoGen examples

特点：

```text
展示某个框架如何表达 workflow、agent、tool、memory、checkpoint。
```

优势：

- 能学到框架思想；
- 适合理解状态、节点、边、checkpoint；
- 后面做 Agent / Multi-Agent 必须看。

缺点：

- 容易被框架概念牵着走；
- 如果基础 API / Tool / RAG 没学好，看起来会很抽象；
- 不能一开始就依赖框架，容易“会调框架但不会设计系统”。

适合阶段：

```text
Week 6-9
```

---

### 2.3 Product 型项目

代表：

- Dify
- RAGFlow
- AnythingLLM
- Open WebUI

特点：

```text
接近真实产品，有 UI、数据、权限、配置、部署、插件、工作流等完整模块。
```

优势：

- 能看到 AI 应用产品化长什么样；
- 架构完整；
- 很适合最终项目拆解；
- 简历表达价值高。

缺点：

- 代码量大；
- 学习成本高；
- 不适合一上来完整复刻；
- 容易陷入部署和依赖泥潭。

适合阶段：

```text
Week 10-12 或阶段性架构拆解
```

---

### 2.4 Agent System 型项目

代表：

- OpenHands
- SWE-agent
- Cline / Roo Code 类项目
- TradingAgents

特点：

```text
重点在 Agent Harness、Tool、State、Loop、Trace、任务执行和多 Agent 协作。
```

优势：

- 和 Agent 工程师目标高度相关；
- 能学到真实任务执行系统；
- 适合形成差异化项目。

缺点：

- 抽象多；
- debug 难；
- 很依赖前面基础能力；
- 不能只看 README，必须看运行链路。

适合阶段：

```text
Week 7-12
```

---

### 2.5 Memory / Context 型项目

代表：

- mem0
- Supermemory
- Letta / MemGPT 类项目

特点：

```text
重点在长期记忆、用户画像、上下文检索、记忆写入和遗忘策略。
```

优势：

- 对个人助理、吵架帮手、学习助手非常有价值；
- 能补足 Agent 长期使用能力；
- 和你自己的 WorkBuddy 方向也有关。

缺点：

- 概念容易虚；
- 很难只靠 demo 判断质量；
- 必须结合具体场景评估。

适合阶段：

```text
Week 7 以后
```

---

### 2.6 Domain Agent 型项目

代表：

- AI 投研助手
- 法律文档助手
- 医疗问答助手
- 编程 Agent
- 你的“吵架帮手 Agent 版”

特点：

```text
重点不只是 AI 技术，而是 AI 技术和某个业务场景结合。
```

优势：

- 最适合做作品集；
- 容易讲清用户价值；
- 能体现产品思考。

缺点：

- 需要业务数据和评估标准；
- 不能只做“套壳聊天”；
- 工程链路必须闭环。

适合阶段：

```text
Week 8-12，或作为最终项目方向
```

---

## 3. 项目选择评分框架：10 个维度

以后你看到任何 AI GitHub 项目，都先按这 10 个维度打分，每项 1-5 分。

| 维度 | 评分问题 | 低分表现 | 高分表现 |
|---|---|---|---|
| 1. 目标匹配度 | 是否贴合你的转型目标？ | 和 AI 工程能力无关 | 命中 RAG / Tool / Agent / MCP / Eval |
| 2. 主链路清晰度 | 能否画出输入到输出？ | 入口混乱，看不出主流程 | README / examples / src 结构清晰 |
| 3. 可运行性 | 能否本地跑最小 demo？ | 环境复杂，依赖重 | 10-30 分钟能跑通最小路径 |
| 4. 可裁剪性 | 能否只复刻一部分？ | 全平台强耦合 | 单模块可拆，如 RAG chain / tool router |
| 5. 工程化含量 | 是否包含日志、配置、错误处理、测试？ | 只有 prompt demo | 有配置、日志、重试、评估、部署 |
| 6. 学习曲线 | 当前阶段能不能吃下？ | 框架/领域/部署都很重 | 稍有挑战但可控 |
| 7. 作品集价值 | 能否写进简历？ | 只能说“跑过 demo” | 能讲架构、指标、改造和上线 |
| 8. 改造空间 | 能否变成你的项目？ | 只能照抄 | 能结合投研/吵架帮手/学习助手 |
| 9. 资料质量 | 文档、issue、example 是否好？ | 文档差，没人维护 | 文档清楚，社区活跃 |
| 10. 风险成本 | API、部署、数据、合规风险高不高？ | 需要复杂账号/贵 API/敏感数据 | 可本地、小成本、低风险运行 |

建议阈值：

```text
总分 ≥ 38：适合作为阶段项目或最终项目候选
30-37：适合局部拆解，不建议完整复刻
< 30：暂时不碰
```

注意：不是 star 越多越适合。

```text
适合学习 = 能跑 + 能懂 + 能改 + 能讲
```

---

## 4. 针对你的候选项目池分析

结合你的背景：后端工程师、AI 应用转型、投资兴趣、吵架帮手独立产品、WorkBuddy 长期系统。当前候选池可以这样分层。

### 第一优先级：OpenAI Cookbook / LlamaIndex examples

为什么先看它们？

- 更适合 Week 1-4；
- 能快速补 LLM API、RAG、Tool、Eval 基础；
- 不会被大工程拖住；
- 适合作为课堂代码的参考来源。

学习方式不是“通读全部”，而是：

```text
按课程主题挑样例
  ↓
跑通最小例子
  ↓
改成自己的代码结构
  ↓
加日志、错误处理、测试和 README
```

比如 Week 1 的 LLM API 项目，可以参考 cookbook 的结构化输出、prompt caching、rate limit 相关样例，但最终要封装成自己的 FastAPI 后端服务。

---

### 第二优先级：LangGraph examples

为什么不是第一节就上 LangGraph？

因为 LangGraph 是在你理解 Agent Loop、State、Tool、Checkpoint 后才真正有意义。

如果现在就学，很容易变成：

```text
会写 StateGraph 代码
但不知道为什么要有 state、node、edge、checkpoint
```

所以它适合 Week 8 左右深入。

真正要学的是：

- State 如何设计；
- Node 边界怎么拆；
- Edge 条件怎么定义；
- Checkpoint 解决什么失败场景；
- Human-in-the-loop 放在哪里；
- Trace 怎么看一次运行。

---

### 第三优先级：TradingAgents

这个项目贴合你的投资兴趣，也适合后面做多 Agent 投研助手。

但现在不适合一上来完整复刻。原因：

- 多 Agent 抽象多；
- 它涉及分析师、研究员、风险经理、交易员等多角色；
- 如果你还没掌握 Tool、Agent Loop、Eval，很容易只看懂“角色扮演”，看不懂系统工程。

更合理的学习路径：

```text
Week 5-7：先做单 Agent + Tool Calling
Week 8-9：学 LangGraph / Multi-Agent
Week 9-12：拆 TradingAgents
最终项目：改造成 A/H 股投研助手或个人投资研究系统
```

---

### 第四优先级：Dify / RAGFlow / AnythingLLM

这些是产品级项目，适合作为架构拆解对象。

不要一开始完整复刻 Dify。它太大。

更好的方式是：

```text
只拆一个模块：
- 工作流编排
- 知识库导入
- RAG 检索链路
- Tool / Plugin 系统
- Prompt 模板管理
- 应用发布机制
```

最终你可以借鉴它们，做一个更轻量的：

```text
个人 AI 学习助手 / 吵架帮手 Agent 控制台 / 投研 RAG 助手
```

---

### 第五优先级：OpenHands / SWE-agent

这类 Coding Agent 很有价值，但不要太早深入。

它们涉及：

- 文件系统工具；
- shell 执行；
- patch 生成；
- sandbox；
- task loop；
- observation；
- error recovery；
- benchmark。

这些都是高级 Agent Harness 内容。

适合后面做专项拆解：

```text
一个 Coding Agent 是如何从 issue 到 patch 的？
```

---

### 第六优先级：mem0 / Supermemory

这类项目适合 Week 7 之后研究 Memory。

对你的 WorkBuddy、学习助手、吵架帮手都有价值。但现在先不要深挖，因为 Memory 没有脱离场景的标准答案。

重点问题是：

```text
什么该记？
什么时候记？
怎么召回？
怎么更新？
怎么遗忘？
记错了怎么办？
用户怎么控制？
```

---

## 5. GitHub 项目阅读 SOP

以后看到一个 repo，不要从头读代码。按这个顺序：

### Step 1：先读 README，但只提取 5 件事

```text
项目解决什么问题？
输入是什么？
输出是什么？
最小运行路径是什么？
核心模块有哪些？
```

不要一开始陷入安装细节。

---

### Step 2：找 examples / demo / quickstart

真实学习入口通常不在源码根目录，而在：

```text
examples/
demo/
cookbook/
notebooks/
quickstart.py
app.py
main.py
```

目标是先找到最短执行链路。

---

### Step 3：画主链路图

不看懂主链路，不要急着改代码。

模板：

```text
用户输入
  ↓
入口函数 / API
  ↓
Prompt / Context 构造
  ↓
LLM / Retriever / Tool / Agent
  ↓
状态记录 / 日志 / 回调
  ↓
输出结果
```

如果 30 分钟内画不出这个图，说明项目当前阶段不适合完整复刻。

---

### Step 4：找工程边界

重点看这些：

```text
配置在哪里？
模型调用封装在哪里？
错误处理在哪里？
日志在哪里？
状态在哪里？
工具注册在哪里？
评估在哪里？
测试在哪里？
```

这些比“Prompt 写得多漂亮”更重要。

---

### Step 5：决定复刻范围

复刻不是照抄完整项目，而是选一个能力闭环。

比如 RAGFlow 太大，可以只复刻：

```text
文档上传 → chunk → embedding → retrieval → answer with citations
```

OpenHands 太大，可以只复刻：

```text
任务输入 → 读取文件 → 修改文件 → 生成 patch → 记录 trace
```

TradingAgents 太大，可以只复刻：

```text
基本面分析师 → 新闻分析师 → 风险评审 → 结论汇总
```

---

## 6. 项目复刻的 4 个层级

你以后不要说“我复刻了某某项目”，要说清楚复刻到哪一层。

### Level 1：跑通 Demo

```text
能启动，能看到输出。
```

价值最低，但必要。

---

### Level 2：理解主链路

```text
能画出架构图，讲清楚输入、处理、输出。
```

这才算真正开始学。

---

### Level 3：局部重写

```text
不用原项目代码，自己实现一个最小闭环。
```

这对学习最关键。

---

### Level 4：场景改造

```text
把能力迁移到自己的业务场景。
```

比如：

- 把 RAGFlow 的知识库链路改造成你的 AI 学习知识库；
- 把 TradingAgents 的多角色分析改造成 A/H 股投研助手；
- 把 Coding Agent 的任务 loop 改造成 WorkBuddy 本地代码助手；
- 把 Agent Harness 思路改造成吵架帮手训练系统。

最终能写进简历的是 Level 3-4，不是 Level 1。

---

## 7. 当前阶段的项目选择建议

你现在不应该马上做最终大项目。应该选一个“低依赖、高闭环”的早期项目。

### Week 1-2 推荐项目：LLM API Backend Service

目标：

```text
做一个可运行的 LLM API 后端服务。
```

核心能力：

- 普通生成；
- 流式输出；
- 结构化输出；
- timeout；
- retry；
- rate limit；
- token cost log；
- prompt version；
- API 文档。

为什么适合你：

- 你是后端，能快速理解服务封装；
- 它是后续 RAG / Tool / Agent 的底座；
- 可以作为所有后续项目的基础组件；
- 不依赖复杂前端。

简历表达可以是：

```text
设计并实现一个面向 AI 应用的 LLM API Gateway，支持流式输出、结构化响应、超时重试、成本日志和模型配置管理，为后续 RAG 与 Agent 系统提供统一模型调用底座。
```

---

## 8. 项目候选初筛表

| 项目 | 当前阶段建议 | 原因 |
|---|---|---|
| OpenAI Cookbook | 立即使用 | 用于 LLM API、结构化输出、RAG、Eval 的样例参考 |
| LlamaIndex examples | Week 3 开始 | 适合 RAG 与 Query Engine |
| LangGraph examples | Week 8 开始 | 等 Agent Loop / State / Checkpoint 有基础后再学 |
| TradingAgents | Week 9 后拆解 | 适合多 Agent 投研方向，但现在过早 |
| Dify | Week 12 架构拆解 | 产品级项目，适合最终拆解，不适合早期完整复刻 |
| RAGFlow / AnythingLLM | Week 4 或 Week 12 | 适合 RAG 产品化拆解 |
| OpenHands / SWE-agent | Week 9 后专项拆解 | 适合 Coding Agent Harness 学习 |
| mem0 / Supermemory | Week 7 后学习 | 适合 Memory / Context 方向 |
| 吵架帮手 Agent 版 | 最终项目候选 | 和你的独立开发目标强绑定 |
| AI 投研助手 | 最终项目候选 | 和你的投资兴趣强绑定，适合多 Agent |

---

## 9. 常见错误

### 错误 1：按 star 选项目

star 高不等于适合你现在学。

```text
适合当前阶段 > 技术名气 > star 数
```

---

### 错误 2：一开始就完整复刻大项目

Dify、OpenHands、RAGFlow 这种项目不能一口吃。

正确方式：

```text
先拆一条链路，再复刻一个最小闭环。
```

---

### 错误 3：只看功能，不看工程边界

一个 AI 项目真正值得学的，往往不是“能聊天”，而是：

- 怎么组织 context；
- 怎么注册 tool；
- 怎么记录 trace；
- 怎么做 eval；
- 怎么处理失败；
- 怎么控制成本；
- 怎么部署。

---

### 错误 4：项目和个人目标脱节

你最终应该围绕自己的目标形成作品集：

```text
AI 学习助手
吵架帮手 Agent
AI 投研助手
WorkBuddy 本地工具 Agent
RAG 知识库助手
```

不要为了追热点做一个自己讲不清价值的项目。

---

## 10. 课堂练习

请你回答下面 4 个问题。不要泛泛而谈，要结合自己的目标。

### 问题 1

从下面候选中选出你当前最想优先拆解的 3 个项目，并说明原因：

```text
OpenAI Cookbook
LlamaIndex examples
LangGraph examples
Dify
RAGFlow / AnythingLLM
OpenHands / SWE-agent
TradingAgents
mem0 / Supermemory
吵架帮手 Agent 版
AI 投研助手
```

### 问题 2

对你选择的第 1 个项目，用 10 个维度做快速评分：

```text
目标匹配度：
主链路清晰度：
可运行性：
可裁剪性：
工程化含量：
学习曲线：
作品集价值：
改造空间：
资料质量：
风险成本：
```

每项 1-5 分，并写一句理由。

### 问题 3

如果你选择“吵架帮手 Agent 版”作为最终项目，它最小可复刻闭环是什么？

按这个格式回答：

```text
用户输入：
核心能力 1：
核心能力 2：
核心能力 3：
输出结果：
如何评估效果：
```

### 问题 4

如果你选择“AI 投研助手”作为最终项目，它应该先做 RAG、Tool Calling 还是 Multi-Agent？为什么？

---

## 11. 本节作业

详见：`assignments/week00-lesson02-homework.md`

本节作业重点不是写代码，而是完成一个**项目选择决策文档**。

---

## 12. 面试表达模板

当面试官问：

> 你如何选择一个 AI 项目来学习和复刻？

可以这样答：

```text
我不会只按 star 数选项目，而是会从目标匹配度、主链路清晰度、可运行性、可裁剪性、工程化含量、学习曲线、作品集价值、改造空间、资料质量和风险成本十个维度评估。

对学习项目，我会先跑通最小 demo，再画出输入到输出的主链路，然后选择一个可裁剪的能力闭环进行局部重写，最后结合自己的业务方向做场景改造。

比如早期我会优先参考 OpenAI Cookbook 和 LlamaIndex examples 来建立 LLM API 与 RAG 基础；等 Agent Loop、State、Checkpoint 基础建立后，再拆 LangGraph、TradingAgents 或 OpenHands 这类更复杂的 Agent 系统。
```

---

## 13. 本节课结论

今天你要记住：

```text
真实项目选择不是追热点，而是做学习投资决策。
```

一个好项目应该满足：

```text
能跑、能懂、能裁剪、能改造、能展示、能讲清楚。
```

下一阶段我们会进入 Week 1：LLM API 基础。也就是说，从下一节课开始，会真正写代码。
