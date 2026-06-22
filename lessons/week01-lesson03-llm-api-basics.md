# Week 1 Lesson 3：LLM API 第一课——messages / token / model / temperature

> 状态：今日正式开课  
> 预计时长：60-75 分钟  
> 本节类型：核心基础 + API 链路 + 代码实战  
> 代码目录：`code/llm-api-basics/`

---

## 0. 本节课为什么重要

从今天开始，课程从“路线认知”进入真正的工程能力训练。

很多人学 LLM API 的方式是：

```text
复制一段 SDK 示例
填一个 API key
print(model output)
```

这只能证明“接口通了”，不能证明你会做 AI 应用。

对后端工程师来说，LLM API 第一课要解决的是：

```text
如何把一个不稳定、昂贵、延迟高、输出不完全可控的模型调用，封装成可治理的后端依赖。
```

这节课不只讲参数名字，而是讲 LLM API 在系统里的位置：

```text
用户请求
  ↓
业务 API / Agent API
  ↓
Prompt / Messages 构造
  ↓
LLM Client / Gateway
  ↓
模型供应商 API
  ↓
响应解析 / 错误处理 / 成本记录
  ↓
业务结果
```

本节目标不是立刻做复杂 Agent，而是把后面所有 RAG、Tool Calling、Agent、Eval 都会依赖的底座打稳。

---

## 1. 本节课目标

学完本节，你应该能回答：

1. LLM API 调用在 AI 应用架构里到底处在哪一层；
2. `messages` / `input` / `instructions` 这些字段分别承担什么职责；
3. token 为什么是成本、延迟和上下文能力的共同计量单位；
4. model 选择不是“越强越好”，而是质量、成本、延迟和能力边界的权衡；
5. temperature 不是“创意按钮”，而是控制输出随机性的采样参数；
6. 为什么生产系统里不应该在业务代码里到处散落模型调用；
7. 一个最小 LLM Client 应该记录哪些信息。

---

## 2. 先建立系统框架：LLM API 不是业务逻辑，而是外部推理依赖

传统后端里，我们不会把所有数据库访问直接散落在 controller 里。通常会有：

```text
Controller → Service → Repository / RPC Client / MQ Client
```

LLM API 也一样。你不应该在每个业务函数里直接写：

```python
client.chat.completions.create(...)
```

更合理的结构是：

```text
业务层
  ↓
Prompt Builder / Context Builder
  ↓
LLM Client / LLM Gateway
  ↓
Provider Adapter
  ↓
OpenAI / Azure OpenAI / Anthropic / Gemini / 本地模型
```

### 2.1 为什么要有 LLM Client / Gateway

因为模型调用不是普通函数调用，它至少有这些治理问题：

| 问题 | 如果不封装会怎样 | Gateway / Client 应该做什么 |
|---|---|---|
| API key 管理 | 密钥散落，难以轮换 | 统一读取环境变量或密钥服务 |
| 模型选择 | 业务代码到处写死模型名 | 统一模型路由和默认模型 |
| 参数管理 | temperature、max_tokens 混乱 | 统一默认值和场景配置 |
| 超时 | 请求卡住拖垮接口 | 统一 timeout |
| 重试 | 429/5xx 失败直接暴露给用户 | 指数退避、有限重试 |
| 成本 | 不知道一次调用花多少钱 | 记录 token usage 和估算成本 |
| Trace | 出问题不知道 prompt 是什么 | 记录 request_id、prompt version、latency |
| 输出解析 | 自由文本导致业务不可控 | 后续接 structured output / schema validation |

所以 LLM Client 是 AI 应用的基础设施，不是语法糖。

---

## 3. Messages：模型看到的“请求上下文包”

在 Chat Completions 形态里，常见字段是 `messages`：

```json
[
  {"role": "system", "content": "你是一个严谨的 AI 课程老师。"},
  {"role": "user", "content": "解释什么是 RAG。"}
]
```

你可以把它理解为一次模型调用的上下文包，但不要强行等同 HTTP 请求体。它更像：

```text
角色约束 + 用户问题 + 历史上下文 + 检索资料 + 工具结果
```

### 3.1 role 的职责

| role | 作用 | 常见错误 |
|---|---|---|
| system | 定义模型行为边界、角色、约束 | 写太空泛，不能真正约束输出 |
| user | 用户目标、问题、任务输入 | 把系统规则混在用户输入里 |
| assistant | 历史模型回答 | 历史太长导致上下文膨胀 |
| tool | 工具调用结果 / 外部观察 | 把工具结果和用户话混在一起 |

### 3.2 system prompt 不是万能的

很多人会以为：

```text
只要 system prompt 写得够强，模型就一定听话。
```

这是错的。

system prompt 是软约束，不是安全边界。真正的生产边界要靠：

```text
输入校验
输出校验
工具权限
schema validation
敏感操作审批
日志审计
fallback
```

这点后面讲 Guardrails 和 Tool Safety 时会反复强调。

---

## 4. Responses API：当前 API 形态正在从“单次聊天”走向“统一响应接口”

今日新增术语是 **Responses API**。

根据 Azure OpenAI Responses API 文档，Responses API 用于生成有状态、多轮响应，并把流式输出、工具调用、Code Interpreter、远程 MCP、响应检索、删除、上下文压缩等能力整合到统一接口里。

为什么今天讲它？因为 API 形态正在变化：

```text
Chat Completions：更像一次聊天补全接口
Responses API：更像统一的模型响应与工具执行入口
```

但对你现在学习来说，不要陷进某一家 SDK 的细节。你要抓住不变的抽象：

```text
输入：任务目标 + 指令 + 上下文 + 参数
处理：模型推理 / 工具调用 / 状态续接
输出：文本 / 结构化结果 / 工具请求 / 流式事件 / usage
治理：超时 / 重试 / 成本 / trace / 安全
```

也就是说，本节课用 `messages` 入门，但你要知道生产系统最终会把它抽象为统一的 LLM Gateway。

---

## 5. Token：LLM 系统里的成本、延迟和上下文计量单位

token 不是“字数”。它是模型处理文本的基本单位。

粗略理解：

```text
英文：1 个 token 大约 0.75 个单词
中文：一个汉字可能接近 1 个 token，但不同模型 tokenizer 不完全一样
代码：符号、缩进、变量名也会消耗 token
```

### 5.1 token 为什么重要

| 维度 | token 的影响 |
|---|---|
| 成本 | 输入 token + 输出 token 通常都计费 |
| 延迟 | 输入越长、输出越长，通常越慢 |
| 上下文窗口 | 超出窗口会报错或被截断 |
| RAG | 检索内容塞太多会挤占回答空间 |
| Agent | 多轮 loop 会不断累积上下文 |
| Eval | 同一个任务不同 prompt 版本 token 成本不同 |

### 5.2 最常见的 token 错误

错误 1：把所有历史对话都塞进去。

```text
后果：成本暴涨、延迟增加、模型注意力被稀释。
```

错误 2：RAG 检索 TopK 太大。

```text
后果：上下文变长，但有效信息密度下降。
```

错误 3：不限制输出长度。

```text
后果：模型啰嗦，成本不可控，接口响应慢。
```

正确做法是从第一天就记录：

```text
input_tokens
output_tokens
total_tokens
latency_ms
model
prompt_version
```

---

## 6. Model：不是越强越好，而是任务匹配

模型选择要看 5 个维度：

| 维度 | 典型问题 |
|---|---|
| 质量 | 这个任务是否需要强推理？ |
| 成本 | 是否每次调用都值得用最贵模型？ |
| 延迟 | 用户是否需要实时响应？ |
| 上下文 | 是否需要处理长文档？ |
| 工具能力 | 是否需要 tool calling / vision / code interpreter？ |

一个常见策略：

```text
简单分类 / 改写 / 摘要 → 小模型
复杂推理 / 架构设计 / 多步分析 → 强模型
高频请求 → 优先考虑成本和缓存
关键决策 → 强模型 + Eval + 人审
```

### 6.1 模型路由的雏形

后面 Week 11 会做模型路由，今天先建立概念：

```text
if task_type == "rewrite":
    use cheap_model
elif task_type == "analysis":
    use strong_model
elif user_tier == "free":
    use cost_control_model
else:
    use default_model
```

这不是现在就要完整实现，但你要从第一节 API 课就知道：模型名不应该散落在业务代码里。

---

## 7. Temperature：控制随机性，不是质量开关

temperature 控制采样随机性。

粗略理解：

```text
temperature 低：输出更稳定、更保守、更可复现
temperature 高：输出更多样、更发散、更有创意，但更不稳定
```

### 7.1 不同场景怎么选

| 场景 | 建议 |
|---|---|
| JSON / 结构化输出 | 低温度，如 0-0.3 |
| 分类 / 打标签 | 低温度 |
| 面试表达润色 | 中等温度 |
| 创意写作 / 头脑风暴 | 中高温度 |
| 生产关键流程 | 低温度 + schema + eval |

### 7.2 常见错误

错误：觉得 temperature 越高模型越聪明。

这是错的。

高 temperature 只是让采样更发散，不代表推理更强。生产系统里，稳定性通常比“看起来有创意”更重要。

---

## 8. 最小 LLM Client 应该记录什么

今天代码目录 `code/llm-api-basics/` 里提供了一个最小 LLM Client 骨架。

它不是为了追求复杂，而是让你从第一天就养成工程习惯：

```text
request_id
model
messages
temperature
max_tokens
latency_ms
usage
provider
error
```

### 8.1 最小调用链路

```text
main.py
  ↓
构造 messages
  ↓
LLMClient.generate()
  ↓
读取 env 配置
  ↓
调用模型 API 或 mock provider
  ↓
记录 latency / usage
  ↓
返回 LLMResult
```

### 8.2 为什么保留 mock 模式

因为学习和测试时不应该每次都依赖真实 API。

mock provider 可以让你：

- 没有 API key 时也能跑通链路；
- 写测试时不产生费用；
- 先验证日志、参数、异常处理；
- 后续做 Eval harness 时可构造稳定输出。

---

## 9. 生产环境中的 LLM API 风险

| 风险 | 表现 | 工程手段 |
|---|---|---|
| 超时 | 接口卡住 | timeout、异步任务、fallback |
| 429 限流 | 请求失败 | retry with backoff、队列、限速 |
| 5xx | provider 抖动 | 有限重试、切换模型、降级回复 |
| token 超限 | 报错或截断 | context budget、摘要、裁剪 |
| 成本失控 | 调用费用暴涨 | usage log、budget、模型路由 |
| 输出不稳定 | 同问不同答 | 低 temperature、schema、eval |
| prompt 泄露 | 用户诱导输出系统提示 | prompt hygiene、输出过滤、权限边界 |
| 观测缺失 | 出问题无法复盘 | request_id、trace、prompt_version、usage |

本节课不会一次解决所有问题，但从今天起，写任何 LLM 调用都要想这些维度。

---

## 10. 面试表达

如果面试官问：

> 你如何理解 LLM API 调用？

不要只说：

```text
就是把 prompt 发给模型拿回答。
```

更好的表达：

```text
我理解 LLM API 调用不是简单的 HTTP 请求，而是 AI 应用里的外部推理依赖。工程上需要把它封装成 LLM Client 或 Gateway，统一处理模型选择、messages 构造、temperature/max_tokens 等参数、超时重试、token usage、成本日志、响应解析和错误治理。

后续无论做 RAG、Tool Calling 还是 Agent，底层都会依赖这个调用层。如果这一层没有统一封装，后面系统会很难做可观测、可评估和可降级。
```

---

## 11. 本节课堂练习

### 练习 1：判断参数

给下面 3 个场景选择合适模型策略和 temperature：

1. 将用户输入分类为“咨询 / 投诉 / 闲聊”；
2. 给“吵架帮手”生成 5 个不同风格的反驳句；
3. 让模型输出固定 JSON，供后端解析。

请回答：

```text
场景：
模型策略：小模型 / 强模型 / 多模型路由？
temperature：低 / 中 / 高？
原因：
```

### 练习 2：设计最小 LLM Client 日志字段

假设你要在生产中排查一次模型回答异常，你至少要记录哪些字段？为什么？

---

## 12. 本节作业

详见：

```text
assignments/week01-lesson03-homework.md
```

本节作业会要求你：

1. 跑通 mock 模式；
2. 阅读 `llm_client.py`；
3. 解释 messages / token / model / temperature；
4. 设计一个 LLM Gateway 的最小字段表；
5. 回答一道面试题。
