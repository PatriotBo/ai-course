# Lesson 4 代码：LLM Streaming 与 FastAPI SSE

本目录对应 Week 1 Lesson 4：Streaming 与后端接口封装。

目标不是简单“把字一个个吐出来”，而是建立一个后端工程师能维护的 streaming endpoint：

```text
Browser / Client
  ↓ POST /api/chat/stream
FastAPI StreamingResponse
  ↓
LLMStreamingClient
  ↓
OpenAI-compatible provider / mock provider
```

---

## 1. 文件说明

| 文件 | 作用 |
|---|---|
| `streaming_client.py` | 最小流式 LLM Client，支持 mock、OpenAI-compatible、GLM、腾讯混元 |
| `app.py` | FastAPI SSE 接口：`POST /api/chat/stream` |
| `demo_stream.py` | 命令行流式输出 demo，不启动 Web 服务也能跑 |
| `.env.example` | provider / model / base_url / api_key 配置模板 |
| `PYTHON_NOTES.md` | 本节涉及的 Python / FastAPI / SSE 语法说明 |
| `requirements.txt` | Python 依赖 |

---

## 2. 安装依赖

```bash
cd /Users/joshuozhang/WorkBuddy/20260513163028/ai-course/code/llm-api-streaming
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

默认 `.env` 使用 mock provider，不会调用真实模型，不产生费用。

---

## 3. 命令行运行 mock stream

```bash
LLM_PROVIDER=mock python demo_stream.py
```

预期输出类似：

```text
request_id=...
stream output:[mock stream] 已收到请求。模型=mock-stream-model...
log_path=logs/llm_streams.jsonl
```

---

## 4. 启动 FastAPI SSE 服务

```bash
uvicorn app:app --reload --port 8001
```

健康检查：

```bash
curl http://127.0.0.1:8001/healthz
```

调用流式接口：

```bash
curl -N -X POST http://127.0.0.1:8001/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message":"用三句话解释 LLM streaming 的价值","temperature":0.2}'
```

`-N` 的作用是关闭 curl 的输出缓冲，否则你可能看不到实时输出。

---

## 5. SSE 返回格式

服务会返回类似：

```text
event: meta
data: {"request_id":"...","model":"mock-stream-model"}

event: delta
data: {"request_id":"...","text":"[mock stream]"}

event: done
data: {"request_id":"..."}
```

几个事件的含义：

| event | 含义 |
|---|---|
| `meta` | 本次请求元信息，如 request_id / model |
| `delta` | 模型新增输出片段 |
| `done` | 流结束 |
| `error` | 流开始后发生错误，无法再改 HTTP status，只能发 error event |

---

## 6. GLM / 腾讯混元配置

### GLM / 智谱

```text
LLM_PROVIDER=glm
LLM_API_KEY=你的智谱_API_Key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
LLM_MODEL=glm-5.2
```

### 腾讯混元

```text
LLM_PROVIDER=hunyuan
LLM_API_KEY=你的混元_API_Key
LLM_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
LLM_MODEL=hunyuan-turbos-latest
```

### 通用 OpenAI-compatible

```text
LLM_PROVIDER=openai_compatible
LLM_API_KEY=你的_API_Key
LLM_BASE_URL=https://your-provider.example.com/v1
LLM_MODEL=your-model-name
```

只要 provider 支持 `/chat/completions` 且兼容 `stream=true`，就可以走这套代码。

---

## 7. 结构化日志

每次 stream 结束或失败，会追加一行 JSON 到：

```text
logs/llm_streams.jsonl
```

字段包括：

```text
timestamp
request_id
status
provider
model
base_url
stream
parameters
input.messages
output.text
output.length
latency_ms
error
```

查看最后一条日志：

```bash
tail -n 1 logs/llm_streams.jsonl | python -m json.tool
```

注意：本课程为了学习方便记录明文 input / output。生产环境应该脱敏、采样或只记录 hash / 摘要。

---

## 8. 这节课的工程边界

本节只做 streaming 基础封装：

- SSE endpoint；
- mock streaming；
- OpenAI-compatible streaming；
- 结构化日志；
- 最小错误事件。

暂不做：

- 复杂重试；
- 限流；
- token 成本估算；
- 用户鉴权；
- 前端 UI；
- 断点续传。

这些会在后续 Lesson 5 和项目课继续补。
