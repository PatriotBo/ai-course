# Week 1 Lesson 4：Streaming 与后端接口封装

> 状态：讲义已生成，等待正式授课  
> 预计时长：60-75 分钟  
> 本节类型：工程实战 + API 设计 + 流式协议

---

## 0. 本节课目标

学完本节课，你应该能回答：

1. LLM streaming 解决的到底是“模型更快”还是“用户感知更快”；
2. SSE、WebSocket、HTTP chunked streaming 的边界是什么；
3. 后端为什么不能把模型供应商的 stream 原样透传给前端；
4. 一个生产可用 streaming endpoint 至少要处理哪些状态、错误、日志和取消场景；
5. 如何用 FastAPI 封装一个最小 SSE 流式接口；
6. 如何让 GLM、腾讯混元等 OpenAI-compatible provider 通过配置切换。

---

## 1. 先澄清：Streaming 不等于模型真的更快

很多人第一次看到流式输出，会以为：

```text
streaming = 模型响应速度更快
```

这个理解不准确。

更准确地说：

```text
streaming 主要改善的是首字可见时间和用户等待体验，而不是一定减少模型完整生成时间。
```

普通非流式调用：

```text
用户请求
  ↓
模型完整生成 800 字
  ↓
后端一次性返回
  ↓
前端一次性展示
```

用户在模型生成完整答案之前，只能一直等。

流式调用：

```text
用户请求
  ↓
模型生成第一段
  ↓
后端立即返回第一段
  ↓
前端边收边展示
  ↓
模型继续生成后续内容
```

用户更早看到反馈，所以体验明显变好。

但总耗时可能仍然接近：

```text
完整生成时间 ≈ 非流式完整耗时
```

核心指标要区分：

| 指标 | 含义 | Streaming 的影响 |
|---|---|---|
| Time To First Token / 首 token 时间 | 用户多久看到第一段内容 | 通常明显改善感知体验 |
| Total Completion Time / 完整生成时间 | 全部内容生成完成耗时 | 不一定减少 |
| Perceived Latency / 用户感知延迟 | 用户主观觉得等了多久 | 明显降低 |
| Backend Occupancy / 后端连接占用 | 请求连接持续多久 | 通常更长 |

所以 streaming 是产品体验和接口形态问题，也是后端资源管理问题。

---

## 2. Streaming 在系统架构里的位置

上一节我们建立了 LLM Client / Gateway：

```text
业务层
  ↓
Prompt Builder / Context Builder
  ↓
LLM Client / Gateway
  ↓
Provider Adapter
  ↓
OpenAI / GLM / Hunyuan / 本地模型
```

今天加入 streaming 后，链路变成：

```text
Browser / App
  ↓ SSE / fetch stream
Backend Streaming Endpoint
  ↓
LLM Gateway / Streaming Client
  ↓
Provider Adapter
  ↓ streaming=true
Model Provider
```

注意：后端不是简单中转。

后端至少要负责：

- 输入校验；
- 鉴权；
- 参数白名单；
- provider 切换；
- request_id / trace_id；
- 错误事件；
- 取消连接；
- 日志记录；
- 成本统计；
- 输出安全边界；
- 客户端协议统一。

如果你直接把供应商 stream 原样透给前端，会导致：

```text
前端强依赖供应商协议
多 provider 切换困难
日志和 trace 缺失
错误事件不可控
安全边界难加
后续改 API 影响面巨大
```

所以正确做法是：

```text
供应商 stream → 后端统一 StreamChunk → SSE event → 前端
```

---

## 3. SSE、WebSocket、HTTP Chunked 怎么选

近两年 LLM 应用里，常见 streaming 传输主要是三类：

| 方案 | 特点 | 适合场景 |
|---|---|---|
| SSE | 服务端单向推送，基于 HTTP，浏览器支持好 | LLM 文本流式输出 |
| WebSocket | 双向长连接，客户端和服务端都能主动发消息 | 协同编辑、实时游戏、双向 Agent 控制 |
| HTTP Chunked / fetch stream | 更底层的分块传输 | 自定义客户端、Node/移动端流式消费 |

这节课我们选 SSE，因为：

1. LLM 文本生成通常是服务端向客户端单向推送；
2. SSE 协议简单；
3. 浏览器支持 `EventSource`，也可以用 fetch 读流；
4. FastAPI 实现成本低；
5. 便于教学和调试。

不要把 SSE 神化。它也有局限：

- 主要是单向推送；
- 长连接会占用后端资源；
- 代理层可能缓冲响应；
- 中途错误不能改 HTTP status；
- 断线重连和幂等要自己设计。

所以今天我们只用 SSE 做 LLM 文本流式输出，不把它强行类比成传统消息队列。

---

## 4. SSE 协议最小格式

SSE 是文本协议，最小格式：

```text
event: delta
data: {"text":"你好"}

```

每个事件以空行结束。

常见事件设计：

```text
event: meta
data: {"request_id":"...","model":"..."}

event: delta
data: {"text":"第一段"}

event: delta
data: {"text":"第二段"}

event: done
data: {"request_id":"..."}
```

为什么不要只返回纯文本？

因为生产里你不只需要文本，还需要：

- request_id；
- model；
- status；
- error；
- usage；
- trace；
- done 标记；
- 前端渲染类型。

所以建议统一成事件流。

---

## 5. 后端 Streaming Endpoint 的设计边界

一个最小但像样的接口：

```text
POST /api/chat/stream
```

请求：

```json
{
  "message": "解释 LLM streaming 的价值",
  "model": "glm-5.2",
  "temperature": 0.2,
  "max_tokens": 512
}
```

响应：

```text
event: meta
...
event: delta
...
event: done
...
```

你要重点看后端职责。

### 5.1 请求校验

不能让前端随便传：

```text
任意 model
任意 temperature
任意 max_tokens
任意 system prompt
```

否则会有：

- 成本失控；
- prompt injection；
- 越权调用强模型；
- 输出不可控；
- provider 错误。

课程代码里用 Pydantic 做最小校验：

```python
class ChatStreamRequest(BaseModel):
    message: str = Field(..., min_length=1)
    model: str | None = None
    temperature: float = Field(default=0.2, ge=0, le=2)
    max_tokens: int = Field(default=512, ge=1, le=4096)
```

### 5.2 统一响应协议

供应商可能返回：

```text
data: {"choices":[{"delta":{"content":"你"}}]}
```

但你自己的前端不应该依赖这个结构。

后端应该统一成：

```text
event: delta
data: {"request_id":"...","text":"你"}
```

这就是 Gateway 的价值。

### 5.3 错误处理

非流式接口可以：

```text
HTTP 500 + JSON error
```

但 streaming 一旦开始输出，HTTP header 已经发出，状态码改不了了。

所以中途错误要发：

```text
event: error
data: {"type":"...","message":"..."}
```

前端收到 error event 后停止渲染，提示用户重试。

### 5.4 日志记录

Streaming 更需要日志，因为排查更难。

至少要记录：

```text
request_id
provider
model
base_url
stream=true
parameters
input.messages
output.text
latency_ms
status
error
```

课程代码写到：

```text
logs/llm_streams.jsonl
```

依然是追加模式。

---

## 6. OpenAI-compatible streaming 的事件解析

OpenAI-compatible 的 `/chat/completions` 流通常长这样：

```text
data: {"choices":[{"delta":{"content":"你"}}]}

data: {"choices":[{"delta":{"content":"好"}}]}

data: [DONE]
```

代码核心逻辑：

```python
for line in response.iter_lines():
    if not line or not line.startswith("data:"):
        continue

    data = line.removeprefix("data:").strip()
    if data == "[DONE]":
        break

    event = json.loads(data)
    delta = event["choices"][0]["delta"].get("content", "")
```

这段代码的工程含义是：

```text
供应商原始事件
  ↓
解析 delta
  ↓
转换成自己的 StreamChunk
  ↓
再转换成 SSE event
```

不要在业务代码里到处写这种解析逻辑。它应该集中在 provider adapter。

---

## 7. 什么时候不该用 Streaming

Streaming 不是所有场景都适合。

不适合：

| 场景 | 原因 |
|---|---|
| 短分类任务 | 完整响应很短，streaming 反而增加复杂度 |
| 固定 JSON 输出 | 分片 JSON 在未完成前不可解析，前端处理麻烦 |
| 后台批处理 | 用户不看实时过程，没必要占长连接 |
| 高并发低价值请求 | 长连接会占资源 |

适合：

| 场景 | 原因 |
|---|---|
| 长文本生成 | 用户需要尽早看到内容 |
| 代码生成 | 可以边生成边读 |
| 解释型回答 | 改善等待体验 |
| Agent 执行过程 | 可以展示 thought/action 之外的安全进度事件 |
| 多步骤报告生成 | 可以展示阶段性结果 |

这里不要强行类比传统后端。Streaming 是产品体验、协议设计和资源管理共同作用的结果。

---

## 8. 生产风险清单

### 风险 1：连接长时间占用

Streaming 请求可能持续几十秒。

处理方式：

- timeout；
- max_tokens；
- 并发限制；
- 连接池限制；
- 用户级 rate limit。

### 风险 2：代理层缓冲

Nginx 或平台网关可能缓存响应，导致前端看不到实时流。

处理方式：

```text
Cache-Control: no-cache
X-Accel-Buffering: no
```

但不同部署环境还要单独验证。

### 风险 3：中途失败体验差

模型 provider 中断后，前端可能只看到半句话。

处理方式：

- error event；
- retry 按钮；
- request_id 展示；
- 保存 partial output；
- 后端日志完整记录。

### 风险 4：前端渲染过频

每个 token 都触发 DOM 更新，前端可能卡。

处理方式：

- 前端 buffer；
- 每 30-50ms 批量渲染；
- markdown 渲染延迟到完成后；
- 大文本虚拟滚动。

### 风险 5：隐私日志

Streaming 日志如果记录完整 input/output，可能包含敏感信息。

处理方式：

- 开发环境记录明文；
- 生产环境脱敏、采样或 hash；
- 高敏业务不记录完整原文；
- 日志权限隔离。

---

## 9. 本节代码说明

代码目录：

```text
code/llm-api-streaming/
  streaming_client.py
  app.py
  demo_stream.py
  README.md
  PYTHON_NOTES.md
  requirements.txt
  .env.example
```

运行 mock demo：

```bash
cd code/llm-api-streaming
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
LLM_PROVIDER=mock python demo_stream.py
```

启动 API：

```bash
uvicorn app:app --reload --port 8001
```

调用 SSE 接口：

```bash
curl -N -X POST http://127.0.0.1:8001/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"解释 LLM streaming 的价值","temperature":0.2}'
```

国内模型配置依然走：

```text
LLM_PROVIDER
LLM_MODEL
LLM_BASE_URL
LLM_API_KEY
```

---

## 10. 面试表达模板

当面试官问：

> 你如何设计一个 LLM streaming 接口？

可以这样答：

```text
我不会直接把模型供应商的 stream 原样透传给前端，而会在后端封装一个统一的 streaming endpoint。

前端请求进入 FastAPI / Gateway 后，后端负责输入校验、鉴权、模型和参数选择，然后调用 provider adapter 的 OpenAI-compatible streaming 接口。供应商返回的 delta 会被转换成我们自己的 StreamChunk，再编码成 SSE 事件，例如 meta、delta、done、error。

这样做的好处是前端不依赖具体供应商协议，同时后端可以统一记录 request_id、provider、model、parameters、input、output、latency、status 和 error。生产环境还要处理 timeout、取消连接、代理缓冲、前端渲染节流、成本控制和日志脱敏。

所以 streaming 不只是体验优化，它也是 LLM Gateway 的协议设计和资源治理问题。
```

---

## 11. 课后练习

> 按新规则，本节不再单独设置重复课堂练习；所有练习统一放到课后作业。

作业文件：

```text
assignments/week01-lesson04-homework.md
```

重点题：

1. 解释 SSE 的事件格式；
2. 设计 streaming endpoint 的日志字段；
3. 判断哪些场景适合 streaming，哪些不适合；
4. 阅读 `app.py` 和 `streaming_client.py`，说明数据从用户输入到前端 delta 的完整链路；
5. 写一段 1 分钟面试表达。
