# Week 1 Lesson 4：课后习题参考答案

> 主题：Streaming 与后端接口封装
> 类型：参考答案，不是用户提交批改
> 日期：2026-07-02
> 说明：用户本次选择不提交个人答案，直接查看参考答案；后续如要训练表达，建议至少复述第 6 题面试答案。

---

## 1. 基础概念题

### 1.1 LLM streaming 主要改善的是哪类体验？它是否一定让模型完整生成更快？

LLM streaming 主要改善的是：

```text
首 token 可见时间
用户感知延迟
交互反馈体验
```

它不一定让模型完整生成更快。

非流式调用时，模型必须完整生成后，后端才一次性返回，用户在这段时间里只能等待。流式调用时，模型生成第一段内容后，后端就可以立刻推给前端，用户可以边看边等后续内容，所以主观体验会更快。

但完整生成 1000 字的总耗时可能并没有减少，甚至因为流式传输、事件包装、前端渲染等开销略有增加。

正确表达：

```text
Streaming 改善的是用户感知延迟，不一定降低完整生成耗时。
```

---

### 1.2 SSE、WebSocket、HTTP chunked streaming 有什么区别？本课为什么优先使用 SSE？

| 方案 | 特点 | 适合场景 |
|---|---|---|
| SSE | 基于 HTTP，服务端向客户端单向推送事件 | LLM 文本流式输出 |
| WebSocket | 双向长连接，客户端和服务端都可以主动发送消息 | 实时协作、游戏、复杂双向 Agent 控制 |
| HTTP chunked / fetch stream | 更底层的分块传输方式 | 自定义客户端、移动端、Node 服务间流式传输 |

本课优先使用 SSE，因为 LLM 文本生成通常是：

```text
客户端发起请求
服务端持续返回文本片段
客户端展示
```

这是典型的服务端单向推送，SSE 刚好适合。

SSE 的优势：

- 协议简单；
- 基于 HTTP，容易调试；
- 浏览器支持较好；
- FastAPI 实现成本低；
- 适合教学和后端封装演示。

但 SSE 不适合复杂双向通信。如果前端需要持续向后端发送控制指令，例如暂停、改写、多人协作，就更适合 WebSocket。

---

### 1.3 为什么后端不应该把模型供应商的 streaming 原样透传给前端？

因为这样会让前端强依赖供应商协议。

如果直接透传 OpenAI / GLM / 混元的原始 streaming 格式，会带来几个问题：

1. **前端绑定供应商协议**：换模型供应商时，前端也要改。
2. **多模型切换困难**：不同供应商即使兼容 OpenAI API，细节也可能不同。
3. **错误处理不可控**：中途失败时，供应商返回什么，前端就被迫处理什么。
4. **日志和 trace 缺失**：后端很难统一记录 request_id、latency、usage、finish_reason、error。
5. **安全边界难加**：鉴权、限流、Guardrails、敏感内容过滤应该在后端做。
6. **协议演进困难**：后续增加 `meta`、`delta`、`done`、`error`、`tool_call` 等事件会很痛苦。

正确做法：

```text
供应商 stream
  ↓
后端 Provider Adapter
  ↓
统一 StreamChunk
  ↓
统一 SSE event
  ↓
前端消费
```

---

### 1.4 streaming 已经开始后，中途失败为什么不能再改 HTTP status？应该怎么通知前端？

因为 streaming 响应一旦开始，HTTP header 和 status code 通常已经发送给客户端了。

例如一开始返回：

```text
HTTP/1.1 200 OK
Content-Type: text/event-stream
```

后面如果模型调用中途失败，后端不能再把状态码改成：

```text
500 Internal Server Error
```

因为 HTTP 响应已经开始了。

所以 streaming 中途失败应该通过事件通知前端：

```text
event: error
data: {"request_id":"abc","error_type":"ProviderTimeout","message":"模型响应超时"}

```

前端收到 `error` event 后：

- 停止打字机展示；
- 显示错误提示；
- 可以提示用户重试；
- 可以记录 request_id 方便排查。

---

### 1.5 哪些场景不适合使用 streaming？至少列 3 个。

不适合 streaming 的场景：

1. **短分类任务**

例如：

```text
咨询 / 投诉 / 闲聊
```

这种任务输出很短，直接返回完整结果即可。streaming 反而增加接口复杂度。

2. **固定 JSON 输出给后端解析**

例如：

```json
{"intent":"complaint","confidence":0.91}
```

JSON 没生成完整前通常不可解析，半截 JSON 对后端没有意义。

3. **后台批处理任务**

例如批量生成 1000 条摘要。用户不需要实时看每个 token，更适合异步任务 + 状态查询。

4. **高并发低价值请求**

streaming 会占用长连接，高并发下资源压力更大。

5. **强结构化、强一致性任务**

比如财务字段抽取、订单状态判断、风控标签输出，这类任务更需要完整校验结果，而不是边生成边展示。

---

## 2. SSE 协议题

给定片段：

```text
event: delta
data: {"request_id":"abc","text":"你好"}

```

### 2.1 `event` 是什么？

`event` 是 SSE 事件类型。

这里：

```text
event: delta
```

表示这是一个增量输出事件，也就是模型正在流式返回一小段文本。

前端可以根据 event 类型决定怎么处理：

| event | 作用 |
|---|---|
| meta | 返回请求元信息 |
| delta | 返回增量文本 |
| done | 表示流结束 |
| error | 表示中途失败 |

---

### 2.2 `data` 是什么？

`data` 是事件携带的数据内容。

这里：

```json
{"request_id":"abc","text":"你好"}
```

表示这次增量属于请求 `abc`，新增文本是：

```text
你好
```

生产中 `data` 通常设计成 JSON 字符串，方便前端解析。

---

### 2.3 为什么末尾需要空行？

SSE 协议用空行表示一个事件结束。

也就是说：

```text
event: delta
data: {"text":"你好"}

```

最后这个空行告诉客户端：

```text
这个 delta 事件完整结束了，可以触发处理逻辑。
```

如果没有空行，客户端可能会继续等待后续内容，不触发事件回调。

---

### 2.4 如果是流结束，应该设计什么 event？

应该设计：

```text
event: done
```

例如：

```text
event: done
data: {"request_id":"abc","finish_reason":"stop"}

```

表示模型已经正常结束输出。

---

### 2.5 如果中途失败，应该设计什么 event？

应该设计：

```text
event: error
```

例如：

```text
event: error
data: {"request_id":"abc","error_type":"ProviderError","message":"模型服务暂时不可用"}

```

注意：不要只断开连接。如果直接断开，前端不知道是正常结束、网络中断，还是模型失败。

---

## 3. 代码阅读题

### 3.1 `ChatStreamRequest` 做了哪些输入校验？这些校验为什么必要？

`ChatStreamRequest` 一般会校验：

1. `message` 不能为空；
2. `temperature` 在合理范围内，例如 `0-2`；
3. `max_tokens` 在合理范围内；
4. 可选 `model` 不能乱传；
5. 输入长度不能无限大。

这些校验必要，因为 streaming 是长连接接口，如果不限制输入和参数，可能导致：

- 超长输入撑爆上下文；
- `max_tokens` 太大导致连接占用过久；
- temperature 过高导致输出不可控；
- 恶意请求拖垮后端；
- 成本失控；
- 日志和 trace 难以排查。

后端接口不能相信前端传参，必须做参数白名单和边界校验。

---

### 3.2 `event_generator()` 的作用是什么？为什么它里面用 `yield`？

`event_generator()` 的作用是：**把模型流式输出转换成 SSE 事件流。**

它大概做这几件事：

```text
生成 request_id
先 yield meta 事件
循环读取 LLMStreamingClient.stream()
每收到一个 chunk，就 yield delta 事件
正常结束时 yield done 事件
异常时 yield error 事件
```

之所以用 `yield`，是因为 streaming 不能一次性返回完整结果。

`yield` 可以让函数变成 generator：

```text
生成一段
返回一段
继续执行
再返回下一段
```

这正好适合流式输出。如果不用 `yield`，而是先把所有内容拼好再 return，那就退化成非流式接口了。

---

### 3.3 `LLMStreamingClient.stream()` 为什么返回 `Iterator[StreamChunk]`？

因为 streaming 的结果不是一次性返回的完整字符串，而是一连串增量片段。

所以它返回：

```python
Iterator[StreamChunk]
```

意思是：

```text
你可以不断遍历它，每次拿到一个 StreamChunk。
```

每个 `StreamChunk` 可能包含：

```text
request_id
text
finish_reason
raw
```

这样上层代码不需要关心 provider 的原始协议，只需要处理统一的 `StreamChunk`。

这就是 Provider Adapter 的价值：

```text
OpenAI / GLM / Hunyuan stream
  ↓
StreamChunk
  ↓
SSE event
```

---

### 3.4 `_openai_compatible_stream()` 如何解析 provider 返回的 `data:` 行？

OpenAI-compatible streaming 通常返回类似：

```text
data: {"choices":[{"delta":{"content":"你好"}}]}

data: {"choices":[{"delta":{"content":"，大哥"}}]}

data: [DONE]
```

解析逻辑通常是：

1. 逐行读取 HTTP stream；
2. 跳过空行；
3. 只处理以 `data:` 开头的行；
4. 去掉 `data:` 前缀；
5. 如果内容是 `[DONE]`，说明结束；
6. 否则把 JSON 字符串解析成 dict；
7. 从里面取：

```text
choices[0].delta.content
```

8. 如果 content 不为空，就 yield 一个 `StreamChunk(text=content)`。

这样就把供应商原始协议转换成统一的内部 chunk。

---

### 3.5 结构化日志是在什么时候写入的？成功和失败分别记录什么？

结构化日志通常在 stream 结束时写入。

因为 streaming 是多段输出，不能每个 token 都写一次完整日志，否则日志量太大。更合理做法是：

- 开始时记录 request_id / provider / model；
- 过程中累积输出片段；
- 正常结束时写 success 日志；
- 异常时写 error 日志。

成功日志应该记录：

```text
timestamp
request_id
status=success
provider
model
base_url
parameters
input messages
output text
chunk_count
latency_ms
finish_reason
```

失败日志应该记录：

```text
timestamp
request_id
status=error
provider
model
parameters
input messages
partial_output
latency_ms
error_type
error_message
```

注意：课程 demo 为了学习会记录明文输入输出。生产环境应该做脱敏、hash、采样或权限隔离。

---

## 4. 接口设计题：吵架帮手流式训练接口

接口：

```text
POST /api/training/stream
```

### 4.1 请求 JSON 字段

可以设计为：

```json
{
  "scenario_id": "couple_conflict_001",
  "user_input": "你每次都不听我说话",
  "target_style": "calm_but_firm",
  "difficulty": "medium",
  "persona": "coach",
  "temperature": 0.7,
  "max_tokens": 512
}
```

字段说明：

| 字段 | 说明 |
|---|---|
| `scenario_id` | 冲突场景 ID |
| `user_input` | 用户输入的回应 |
| `target_style` | 想训练的回应风格 |
| `difficulty` | 难度 |
| `persona` | AI 扮演的人格或教练模式 |
| `temperature` | 控制生成多样性 |
| `max_tokens` | 限制输出长度 |

---

### 4.2 SSE 事件类型

建议设计：

| event | 作用 |
|---|---|
| `meta` | 返回 request_id、scenario_id、model 等元信息 |
| `delta` | 返回模型生成的增量文本 |
| `score_delta` | 可选，返回阶段性评分或提示 |
| `guardrail_warning` | 可选，提醒输出有风险 |
| `done` | 正常结束 |
| `error` | 中途失败 |

最小版本可以只保留：

```text
meta
delta
done
error
```

---

### 4.3 每个事件的 data 字段

#### meta

```json
{
  "request_id": "req_123",
  "scenario_id": "couple_conflict_001",
  "model": "glm-5.2",
  "style": "calm_but_firm"
}
```

#### delta

```json
{
  "request_id": "req_123",
  "text": "我理解你现在很生气，"
}
```

#### guardrail_warning

```json
{
  "request_id": "req_123",
  "risk_type": "insult",
  "message": "检测到可能升级冲突的表达，已进行弱化处理。"
}
```

#### done

```json
{
  "request_id": "req_123",
  "finish_reason": "stop",
  "latency_ms": 2300
}
```

#### error

```json
{
  "request_id": "req_123",
  "error_type": "ProviderTimeout",
  "message": "模型响应超时，请稍后重试。"
}
```

---

### 4.4 哪些字段要写入日志？

至少记录：

```text
timestamp
request_id
user_id_hash
scenario_id
target_style
difficulty
provider
model
temperature
max_tokens
input_text_hash 或脱敏后的 input
output_text 或脱敏后的 output
chunk_count
latency_ms
status
finish_reason
error_type
error_message
guardrail_result
```

如果是生产环境，用户原始输入和模型输出不能无脑明文入库，最好：

```text
开发环境：可以明文
生产环境：脱敏 / hash / 采样 / 权限隔离
```

---

### 4.5 如何处理中途失败？

如果模型中途失败，不能再改 HTTP status，应该发送：

```text
event: error
```

例如：

```text
event: error
data: {"request_id":"req_123","error_type":"ProviderError","message":"模型服务暂时不可用"}

```

同时后端要：

1. 记录 error 日志；
2. 记录 partial_output；
3. 告诉前端停止展示；
4. 前端提示用户重试；
5. 如果有 fallback 模型，可以降级重试；
6. 如果输出已经部分展示，要标注“生成中断”。

---

### 4.6 哪些输出需要 Guardrails 检查？

“吵架帮手”尤其需要检查：

1. 人身攻击；
2. 侮辱性语言；
3. 威胁恐吓；
4. 歧视性表达；
5. 诱导暴力；
6. 引导升级冲突；
7. 涉及自伤或伤害他人；
8. 过度操控、PUA 式表达；
9. 隐私泄露；
10. 违法建议。

特别注意：这个产品不是帮用户“骂赢”，而是训练用户在冲突中更有表达能力。所以 Guardrails 要保证输出：

```text
有力量，但不失控；
有边界，但不攻击；
能表达情绪，但不升级冲突。
```

---

## 5. 场景判断题

| 场景 | 是否适合 | 原因 |
|---|---|---|
| 用户输入分类为“咨询/投诉/闲聊” | 不适合 | 输出很短，直接返回分类结果即可。streaming 增加复杂度，没有明显体验收益。 |
| 生成 1000 字产品分析报告 | 适合 | 输出长，用户可以先看到开头和结构，降低感知等待时间。 |
| 固定 JSON 输出给后端解析 | 不适合 | JSON 没完整生成前不可解析，半截 JSON 对后端没有意义，应该完整生成后校验。 |
| Coding Agent 展示文件修改过程 | 适合 | Agent 执行过程较长，适合流式展示计划、步骤、文件修改、命令结果等进度。 |
| 后台批量生成 1000 条摘要 | 不适合 | 这是后台批处理任务，用户不需要实时看 token，更适合异步任务队列 + 进度查询。 |

---

## 6. 面试题

题目：

> 你会如何设计一个生产可用的 LLM streaming endpoint？

### 6.1 1 分钟参考答案

```text
我会用后端 Gateway 封装 LLM streaming，而不是把模型供应商的 stream 原样透传给前端。接口层可以提供一个 POST /api/chat/stream，前端通过 SSE 消费统一事件，例如 meta、delta、done 和 error。

业务层先做鉴权、输入校验、参数白名单和 request_id / trace_id 生成，然后由 Streaming Gateway 调用 provider adapter。adapter 负责把 OpenAI、GLM、腾讯混元等 OpenAI-compatible 的 data stream 解析成统一的 StreamChunk，再由后端转换成统一 SSE event。

日志方面，我会记录 request_id、trace_id、provider、model、temperature、max_tokens、input、output 或脱敏版本、chunk_count、latency_ms、finish_reason、status、error_type 和 partial_output。中途失败时，因为 HTTP status 已经发出，不能再改状态码，所以要发送 error event 通知前端，并记录失败日志。

不直接透传供应商协议的原因是：前端不应该绑定某个 provider 的 stream 格式。后端统一协议后，才能支持多模型切换、日志观测、错误处理、限流、Guardrails 和后续协议演进。
```

### 6.2 更短版本

```text
生产可用的 LLM streaming endpoint 不能只是透传模型输出，而应该由后端 Gateway 统一封装。前端通过 SSE 消费 meta、delta、done、error 事件；后端负责鉴权、参数校验、provider adapter、错误事件、结构化日志和 Guardrails。

Streaming 主要改善首 token 时间和用户感知延迟，不一定缩短完整生成时间。后端要把 OpenAI、GLM、混元等 provider 的原始 stream 转成统一 StreamChunk，再转成统一 SSE 协议。这样前端不用关心供应商差异，系统也更容易做观测、降级、限流和安全治理。
```

---

## 7. 本节答案重点

你真正要记住的不是某个代码细节，而是这 5 句话：

1. Streaming 改善用户感知延迟，不一定减少完整生成耗时。
2. SSE 适合 LLM 单向文本流，但不适合所有实时场景。
3. 后端不能直接透传 provider stream，要统一成自己的事件协议。
4. 中途失败不能再改 HTTP status，要通过 `error` event 告知前端。
5. 生产级 streaming endpoint 必须有输入校验、日志、错误处理、取消连接、Guardrails 和隐私治理。
