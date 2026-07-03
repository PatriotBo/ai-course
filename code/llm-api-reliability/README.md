# Lesson 5 代码：LLM API 可靠性封装

本目录对应 Week 1 Lesson 5：错误处理、超时、重试、限流与成本估算。

目标不是“加一个 retry 装饰器”，而是建立一个更接近生产的 LLM Client：

```text
业务请求
  ↓
ReliableLLMClient
  ├── timeout
  ├── error classification
  ├── retry policy
  ├── exponential backoff with jitter
  ├── usage normalization
  ├── cost estimate
  └── structured log
  ↓
OpenAI-compatible provider / GLM / Hunyuan
```

---

## 1. 文件说明

| 文件 | 作用 |
|---|---|
| `reliable_client.py` | 带 timeout、错误分类、有限重试、成本估算和结构化日志的 LLM Client |
| `demo_generate.py` | 使用真实 provider 运行一次模型调用 |
| `.env.example` | provider / model / base_url / api_key / retry / cost 配置模板 |
| `PYTHON_NOTES.md` | 本节新增 Python 语法和可靠性代码说明 |
| `requirements.txt` | Python 依赖 |

---

## 2. 安装依赖

```bash
cd ai-course/code/llm-api-reliability
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`，填入真实 provider 信息。

---

## 3. GLM 配置

```text
LLM_PROVIDER=glm
LLM_API_KEY=你的智谱_API_Key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
LLM_MODEL=glm-5.2
```

---

## 4. 腾讯混元配置

```text
LLM_PROVIDER=hunyuan
LLM_API_KEY=你的混元_API_Key
LLM_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
LLM_MODEL=hunyuan-turbos-latest
```

---

## 5. 可靠性配置

```text
LLM_TIMEOUT_SECONDS=30
LLM_MAX_RETRIES=3
LLM_BASE_DELAY_SECONDS=1
LLM_MAX_DELAY_SECONDS=20
LLM_TEMPERATURE=0.2
LLM_MAX_TOKENS=512
```

含义：

| 配置 | 含义 |
|---|---|
| `LLM_TIMEOUT_SECONDS` | 单次 provider 请求超时时间 |
| `LLM_MAX_RETRIES` | 失败后最多再重试几次 |
| `LLM_BASE_DELAY_SECONDS` | 第一次重试的基础等待时间 |
| `LLM_MAX_DELAY_SECONDS` | 指数退避等待上限 |
| `LLM_TEMPERATURE` | 模型采样温度 |
| `LLM_MAX_TOKENS` | 最大输出 token |

---

## 6. 成本估算配置

```text
LLM_INPUT_PRICE_PER_1M=0
LLM_OUTPUT_PRICE_PER_1M=0
```

单位是：

```text
元 / 1M tokens
```

例如某模型 input 价格为 2 元 / 1M tokens，output 价格为 8 元 / 1M tokens：

```text
LLM_INPUT_PRICE_PER_1M=2
LLM_OUTPUT_PRICE_PER_1M=8
```

---

## 7. 运行

```bash
python demo_generate.py
```

运行后会输出：

```text
模型回答
request_id
provider
model
attempt_count
latency_ms
usage
cost
log_path
```

如果没有配置 `LLM_API_KEY`，程序会直接报错，提醒你配置真实 provider。

---

## 8. 结构化日志

每次成功或最终失败，都会追加一行结构化日志：

```text
logs/llm_reliability.jsonl
```

本节新增的关键字段：

| 字段 | 作用 |
|---|---|
| `attempt_count` | 判断是否发生重试 |
| `retry_errors` | 记录每次失败的类型和 HTTP 状态码 |
| `error.retryable` | 判断错误是否可重试 |
| `usage` | 记录 input/output/total tokens |
| `cost` | 估算本次调用成本 |
| `latency_ms` | 记录端到端耗时 |
| `parameters.max_retries` | 记录当时使用的 retry policy |

---

## 9. 本节边界

本节实现：

- timeout；
- 错误分类；
- 有限重试；
- exponential backoff with jitter；
- token usage 归一化；
- 成本估算；
- 结构化日志。

暂不实现：

- 多 provider fallback；
- 分布式 rate limiter；
- 队列削峰；
- Prometheus 指标；
- 用户级 budget；
- 自动模型路由。

这些会在后续工程化课程继续补。
