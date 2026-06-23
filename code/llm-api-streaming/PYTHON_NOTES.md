# Python / FastAPI 语法补充：Lesson 4 Streaming

本文件解释 `code/llm-api-streaming/` 中出现的关键 Python 和 FastAPI 语法。

---

## 1. `Iterator[StreamChunk]`

```python
def stream(...) -> Iterator[StreamChunk]:
```

表示这个函数不会一次性返回完整列表，而是返回一个可迭代对象，调用方可以逐个拿到 `StreamChunk`。

这正适合模型流式输出：

```text
chunk1 → chunk2 → chunk3 → done
```

---

## 2. `yield`

```python
for chunk in source:
    yield chunk
```

`yield` 会让函数变成 generator。它每次产出一个值后暂停，下一次迭代时从暂停的位置继续。

和 `return` 的区别：

| 写法 | 行为 |
|---|---|
| `return value` | 一次性结束函数 |
| `yield value` | 产出一个值，但函数还可以继续执行 |

LLM streaming 必须用这种逐步产出的思路。

---

## 3. `with client.stream(...) as response`

```python
with client.stream("POST", url, json=payload, headers=headers) as response:
```

这是 httpx 的流式 HTTP 请求写法。它不会等完整响应体下载完，而是允许你边接收边处理。

退出 `with` 时，连接会自动关闭，避免资源泄漏。

---

## 4. `response.iter_lines()`

```python
for line in response.iter_lines():
```

逐行读取 HTTP streaming 响应。OpenAI-compatible streaming 通常返回 SSE 文本：

```text
data: {"choices":[{"delta":{"content":"你"}}]}
data: {"choices":[{"delta":{"content":"好"}}]}
data: [DONE]
```

所以代码会解析每一行 `data:`。

---

## 5. `removeprefix("data:")`

```python
data = line.removeprefix("data:").strip()
```

去掉字符串开头的 `data:`，拿到真正的 JSON 内容。

比如：

```python
"data: {\"x\":1}".removeprefix("data:").strip()
# '{"x":1}'
```

---

## 6. FastAPI `StreamingResponse`

```python
return StreamingResponse(event_generator(), media_type="text/event-stream")
```

`StreamingResponse` 会把 generator 产出的字符串逐段发送给客户端。

`media_type="text/event-stream"` 表示这是 SSE 协议。

---

## 7. SSE event 格式

```python
return f"event: {event}\ndata: {payload}\n\n"
```

SSE 每个事件由多行文本组成，最后必须有一个空行：

```text
event: delta
data: {"text":"你好"}

```

如果没有最后的空行，浏览器可能不会触发事件。

---

## 8. 为什么 stream 开始后不能再改 HTTP status？

普通接口如果失败，可以返回：

```text
HTTP 500
```

但 streaming 接口一旦开始输出，HTTP header 已经发给客户端了，状态码不能再改。

所以中途失败时，只能继续发一个：

```text
event: error
data: {"message":"..."}
```

前端收到 error event 后自行处理。

---

## 9. 为什么日志用 JSONL？

streaming 调用结束后追加一行：

```text
{"request_id":"...","status":"success",...}
```

JSONL 的好处：

- 一次调用一行；
- 可以 `tail -f` 实时看；
- 追加写入简单；
- 后续容易导入日志系统。

---

## 10. 学这节代码时重点看什么？

不要只看语法，要看链路：

```text
HTTP 请求进来
  ↓
FastAPI 构造 StreamRequest
  ↓
LLMStreamingClient 调 provider
  ↓
一段段 StreamChunk 产出
  ↓
SSE event 返回浏览器
  ↓
结束后追加结构化日志
```
