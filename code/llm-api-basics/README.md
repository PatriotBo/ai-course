# code/llm-api-basics

本目录对应 Week 1 Lesson 3：LLM API 第一课。

目标不是炫技，而是建立一个最小但有工程意识的 LLM Client：

- 统一读取模型配置；
- 支持 mock provider，没 API key 也能跑通链路；
- 支持 OpenAI-compatible 接口，配置 `provider / model / base_url / api_key` 即可切换 OpenAI、智谱 GLM、腾讯混元等模型；
- 记录 request_id、latency、usage；
- 将每次模型调用以 JSON Lines 结构化日志追加写入文件，方便观察输入、输出、参数、成功/失败状态；
- 为后续 timeout、retry、cost log、structured output 做铺垫。

如果你阅读 Python 语法时有卡点，先看：[`PYTHON_NOTES.md`](PYTHON_NOTES.md)。

## 运行 mock 模式

```bash
cd ai-course/code/llm-api-basics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo_generate.py
```

默认 `LLM_PROVIDER=mock`，不会产生 API 费用。

运行后会在 metadata 中看到日志文件路径，例如：

```json
{
  "request_id": "...",
  "provider": "mock",
  "model": "mock-model",
  "latency_ms": 0,
  "usage": {
    "input_tokens": 0,
    "output_tokens": 0,
    "total_tokens": 0
  },
  "log_path": "/.../code/llm-api-basics/logs/llm_calls.jsonl"
}
```

## 结构化调用日志

每次调用 `client.generate(request)` 都会追加一行 JSON 到日志文件，默认路径：

```text
code/llm-api-basics/logs/llm_calls.jsonl
```

你也可以通过环境变量修改：

```text
LLM_LOG_PATH=logs/llm_calls.jsonl
```

查看最新日志：

```bash
tail -n 1 logs/llm_calls.jsonl | python -m json.tool
```

日志是 JSON Lines 格式，一行代表一次模型调用，核心字段包括：

| 字段 | 说明 |
|---|---|
| `timestamp` | UTC 时间，方便按时间排查 |
| `request_id` | 本次模型调用 ID |
| `status` | `success` 或 `error`，用于判断调用是否成功 |
| `provider` / `model` / `base_url` | 本次调用的供应商、模型和 OpenAI-compatible 地址 |
| `parameters` | `temperature`、`max_tokens`、`timeout_seconds` 等调用参数 |
| `input.messages` | 本次传给模型的 messages，包含 system/user/assistant/tool |
| `output.text` | 模型输出文本，失败时为 `null` |
| `output.usage` | token usage，真实 provider 返回时用于成本分析 |
| `output.finish_reason` | 模型结束原因，mock 响应可能为空 |
| `latency_ms` | 本次调用耗时 |
| `error.type` / `error.message` | 失败时的异常类型和错误信息 |

> 注意：本课程为了学习排查，会默认记录明文 `messages` 和 `output.text`。生产环境不能无脑记录用户隐私和模型输出，应该做脱敏、hash、采样或受控开关。

## 接真实 OpenAI-compatible API

```bash
cp .env.example .env
```

编辑 `.env`。课程示例统一使用这四个配置项：

```text
LLM_PROVIDER=openai_compatible
LLM_API_KEY=你的 key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=你的模型名
```

再运行：

```bash
python demo_generate.py
```

不要提交 `.env`。

### 切换到智谱 GLM

智谱 GLM 支持 OpenAI-compatible 调用。只需要改配置，不需要改代码：

```text
LLM_PROVIDER=glm
LLM_API_KEY=你的智谱 API Key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
LLM_MODEL=glm-5.2
```

如果你已经在系统环境变量里设置了 `ZAI_API_KEY`，代码也会自动读取。

### 切换到腾讯混元 Hunyuan

腾讯混元也支持 OpenAI-compatible 调用：

```text
LLM_PROVIDER=hunyuan
LLM_API_KEY=你的混元 API Key
LLM_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
LLM_MODEL=hunyuan-turbos-latest
```

如果你已经在系统环境变量里设置了 `HUNYUAN_API_KEY`，代码也会自动读取。

## 后续扩展

下一步会逐渐加入：

- timeout；
- retry with backoff；
- rate limit；
- token cost estimate；
- structured output；
- streaming；
- prompt version；
- eval harness。

## 配置原则

本目录后续统一遵守一个原则：

```text
换模型 = 改配置，不改业务代码
```

也就是只改：

```text
LLM_PROVIDER
LLM_MODEL
LLM_BASE_URL
LLM_API_KEY
```

业务层仍然只调用：

```python
client = LLMClient()
result = client.generate(request)
```
