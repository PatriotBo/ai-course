# Week 1 Lesson 5：课后习题参考答案

> 主题：错误处理、超时、重试、限流与成本估算
> 类型：参考答案，不是用户提交批改
> 日期：2026-07-03
> 说明：本答案用于辅助理解 LLM API 可靠性治理，重点不是背答案，而是形成“错误分类 → 有限重试 → 成本日志 → 可观测”的工程表达。

---

## 1. 基础概念题

### 1.1 为什么说 LLM API 失败是常态，而不是偶发异常？

因为 LLM API 本质上是一个外部推理依赖，不是本地函数调用。

它依赖：

- 网络连接；
- provider 服务稳定性；
- API key 权限；
- 模型可用性；
- 账户额度；
- 请求上下文长度；
- provider 限流策略；
- 内容安全策略。

所以在真实生产环境中，LLM API 经常会遇到：

```text
Timeout
HTTP 429
HTTP 5xx
上下文超限
额度不足
API key 错误
模型不存在
内容过滤
```

这些都不是异常中的异常，而是外部服务调用的正常风险。

更工程化的表达：

```text
LLM API 应该被当作不稳定外部依赖治理，而不是当成本地确定性函数调用。
```

---

### 1.2 为什么错误处理的第一步是“分类”，而不是直接重试？

因为不是所有错误都能通过重试解决。

如果不分类，直接重试，会出现两个问题：

1. **浪费资源**

例如 API key 错误、余额不足、模型不存在，原样重试多少次都不会成功。

2. **放大故障**

例如已经触发 429 限流，如果系统继续疯狂重试，失败请求也可能计入限流额度，导致限流更严重。

所以错误处理的第一步应该是判断：

```text
这个错误是否是短暂性错误？
同一个请求再次尝试是否有合理概率成功？
```

可以重试的通常是：

```text
Timeout
网络抖动
HTTP 429
HTTP 500 / 502 / 503 / 504
```

不应原样重试的通常是：

```text
API key 错误
权限不足
余额不足
参数错误
上下文超限
模型不存在
内容安全拦截
```

---

### 1.3 `timeout` 对后端服务有什么意义？如果没有 timeout 会发生什么？

`timeout` 的意义是限制单次外部调用最多等待多久，避免请求无限挂住。

如果没有 timeout，LLM provider 一旦响应变慢或网络卡住，后端会出现：

```text
HTTP worker 被占用
连接资源被占用
用户请求一直等待
上游请求堆积
线程池/连接池耗尽
服务整体响应变慢
最终可能拖垮系统
```

所以 timeout 是保护后端服务的基础手段。

常见策略：

| 场景 | timeout 建议 |
|---|---|
| 分类 / 打标签 | 3-10 秒 |
| 普通问答 | 15-30 秒 |
| 长文生成 | 60 秒左右 |
| 后台批处理 | 可以更长，但最好异步化 |
| streaming | 需要区分连接超时和读超时 |

面试表达：

```text
LLM API 调用必须设置 timeout，否则下游抖动会直接占住后端资源，造成请求堆积和级联故障。
```

---

### 1.4 什么是 exponential backoff with jitter？为什么要加 jitter？

Exponential backoff 是指数退避。

意思是每次失败后等待一段时间再重试，而且等待时间按指数增长：

```text
第 1 次失败：等 1 秒
第 2 次失败：等 2 秒
第 3 次失败：等 4 秒
第 4 次失败：等 8 秒
```

Jitter 是随机扰动。

加入 jitter 后，实际等待时间不是固定的 1、2、4、8 秒，而是在基础时间上加一点随机偏移：

```text
实际等待 = base_delay + random_jitter
```

为什么要加 jitter？

因为大量请求可能同时失败。如果它们都按固定间隔重试，会在 1 秒、2 秒、4 秒后再次同时打到 provider，形成重试洪峰。

Jitter 可以把这些重试请求打散，降低雪崩风险。

一句话：

```text
backoff 是为了越失败越慢，jitter 是为了不要大家一起重试。
```

---

### 1.5 RPM、TPM、RPD 分别是什么意思？为什么只看请求数不够？

| 缩写 | 含义 |
|---|---|
| RPM | Requests Per Minute，每分钟请求数 |
| TPM | Tokens Per Minute，每分钟 token 数 |
| RPD | Requests Per Day，每天请求数 |

只看请求数不够，因为 LLM API 的成本和限流不仅取决于请求次数，还取决于 token 数。

例如：

```text
请求 A：每分钟 100 次，每次 100 tokens
请求 B：每分钟 10 次，每次 10000 tokens
```

请求 B 次数更少，但 token 压力更大，可能更容易触发 TPM 限制。

所以治理 rate limit 要同时看：

```text
request_count
input_tokens
output_tokens
total_tokens
max_tokens
attempt_count
retry_count
```

---

## 2. 错误分类题

| 错误 | 是否重试 | 原因 |
|---|---|---|
| HTTP 429 Rate Limit | 可以有限重试 | 这是限流错误，通常可以等待窗口恢复后重试，但必须使用指数退避和 jitter，不能立即疯狂重试。 |
| HTTP 500 Provider Error | 可以有限重试 | 5xx 通常代表 provider 短暂异常，同一个请求稍后可能成功。 |
| API key 无效 | 不应重试 | 这是确定性配置错误，原样重试不会成功，应告警或提示修复配置。 |
| 请求上下文超限 | 不应原样重试 | 输入太长导致失败，必须裁剪、压缩或改写上下文，原样重试仍然失败。 |
| 网络连接超时 | 可以有限重试 | 网络抖动可能是短暂性的，适合有限重试，但要有 timeout 和最大次数。 |
| 余额不足 / quota exhausted | 不应重试 | 账户额度不足，重试不能解决，应告警、充值、切换账号或降级。 |
| 模型不存在 | 不应重试 | 模型名配置错误或无权限，原样重试不会成功，应检查 model 配置。 |
| HTTP 503 Service Unavailable | 可以有限重试 | provider 暂时不可用，稍后可能恢复，适合退避重试或 fallback。 |

核心判断：

```text
短暂性错误可以有限重试；确定性错误不能原样重试。
```

---

## 3. Retry Policy 设计题

一个最小可用的 LLM API retry policy 可以这样设计。

### 3.1 最大重试次数

```text
max_retries = 3
```

即：

```text
第一次正常调用
失败后最多再重试 3 次
总共最多 4 次 attempt
```

不建议设置太大，否则会放大故障、增加延迟和成本。

---

### 3.2 哪些错误可以重试？

可以重试：

```text
Timeout
TransportError / 网络连接失败
HTTP 408
HTTP 409
HTTP 425
HTTP 429
HTTP 500
HTTP 502
HTTP 503
HTTP 504
```

这些通常是短暂性错误。

---

### 3.3 哪些错误不能重试？

不应原样重试：

```text
HTTP 400 参数错误
HTTP 401 API key 错误
HTTP 403 权限不足
HTTP 404 模型或接口不存在
HTTP 422 请求格式错误
quota exhausted
context length exceeded
content filter
```

这些问题不改变请求内容或配置，重试也不会成功。

---

### 3.4 每次重试等待时间如何计算？

可以使用指数退避：

```text
base_delay = 1s
max_delay = 20s
wait = min(base_delay * 2 ** (attempt - 1), max_delay)
```

例如：

```text
第 1 次失败后：1s
第 2 次失败后：2s
第 3 次失败后：4s
第 4 次失败后：8s
```

---

### 3.5 如何避免大量请求同时重试？

加入 jitter：

```text
jitter = random(0, wait * 0.25)
actual_wait = wait + jitter
```

这样不同请求的重试时间会被打散，避免同一时间再次打到 provider。

---

### 3.6 最终失败后如何返回给业务层？

最终失败后不应该吞掉错误，而应该：

1. 抛出统一异常，例如 `ProviderError`；
2. 记录结构化日志；
3. 日志里包含 attempt_count、error_type、http_status、retryable；
4. 业务层根据错误类型决定是提示用户、降级、转异步任务还是告警。

业务层可以拿到类似：

```json
{
  "status": "error",
  "request_id": "req_xxx",
  "attempt_count": 4,
  "error": {
    "type": "rate_limit",
    "http_status": 429,
    "retryable": true
  }
}
```

---

## 4. 代码阅读题

### 4.1 `ProviderError` 为什么要区分 `retryable`？

因为 retry loop 需要知道这个错误是否值得重试。

如果不区分 `retryable`，代码只能做两种错误选择：

```text
所有错误都重试
所有错误都不重试
```

这都不对。

例如：

```text
Timeout：retryable=True
HTTP 429：retryable=True
API key 错误：retryable=False
参数错误：retryable=False
```

`retryable` 把错误分类结果变成代码可以执行的决策。

---

### 4.2 `RetryPolicy` 里每个字段分别控制什么？

| 字段 | 作用 |
|---|---|
| `max_retries` | 失败后最多再重试几次，不包含第一次调用 |
| `base_delay_seconds` | 第一次重试的基础等待时间 |
| `max_delay_seconds` | 指数退避等待时间上限 |
| `jitter_ratio` | 随机扰动比例，用于打散重试时间 |

例如：

```text
max_retries=3
base_delay_seconds=1
max_delay_seconds=20
jitter_ratio=0.25
```

表示：最多重试 3 次，等待时间从 1 秒开始指数增长，最长不超过 20 秒，并加 25% 范围内的随机扰动。

---

### 4.3 `_classify_http_error()` 如何判断哪些 HTTP 状态码可以重试？

它会根据 HTTP status code 判断。

可重试状态码通常放在集合中：

```python
RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
```

如果返回状态码在这个集合中：

```python
retryable = status in RETRYABLE_STATUS_CODES
```

就标记为可重试。

典型分类：

```text
429 → rate_limit
500 / 502 / 503 / 504 → provider_5xx
400 / 401 / 403 / 404 / 422 → non_retryable_http_error
```

这样 retry loop 就可以根据 `retryable` 决定是否继续。

---

### 4.4 `_sleep_before_retry()` 为什么要加入 jitter？

因为没有 jitter 时，大量请求可能同时失败，又同时在固定时间点重试。

例如：

```text
1000 个请求同时遇到 429
全部等待 1 秒
1 秒后又同时重试
再次打爆 provider
```

加入 jitter 后：

```text
有的请求 1.05 秒后重试
有的请求 1.18 秒后重试
有的请求 1.23 秒后重试
```

这样能打散重试洪峰，降低雪崩风险。

---

### 4.5 成本估算是如何从 usage 字段计算出来的？

代码先把 provider 返回的 usage 统一成：

```text
input_tokens
output_tokens
total_tokens
```

OpenAI-compatible 常见字段：

```json
{
  "prompt_tokens": 3000,
  "completion_tokens": 800,
  "total_tokens": 3800
}
```

然后使用价格配置：

```text
LLM_INPUT_PRICE_PER_1M
LLM_OUTPUT_PRICE_PER_1M
```

计算：

```text
input_cost = input_tokens / 1_000_000 * input_price_per_1m
output_cost = output_tokens / 1_000_000 * output_price_per_1m
total_cost = input_cost + output_cost
```

---

### 4.6 结构化日志里哪些字段最适合用于排查 429 和成本异常？

排查 429：

```text
status
error.type
error.http_status
attempt_count
retry_errors
provider
model
latency_ms
parameters.max_retries
```

排查成本异常：

```text
usage.input_tokens
usage.output_tokens
usage.total_tokens
cost.input_cost
cost.output_cost
cost.total_cost
parameters.max_tokens
model
provider
```

如果 `output_tokens` 经常很高，说明模型输出太长；如果 `input_tokens` 很高，说明 prompt、上下文或 RAG 检索内容太长。

---

## 5. 成本估算题

已知：

```text
input_price_per_1m = 2.00 元
output_price_per_1m = 8.00 元
input_tokens = 3000
output_tokens = 800
total_tokens = 3800
```

### 5.1 input 成本

```text
input_cost = 3000 / 1_000_000 * 2.00
           = 0.006 元
```

### 5.2 output 成本

```text
output_cost = 800 / 1_000_000 * 8.00
            = 0.0064 元
```

### 5.3 总成本

```text
total_cost = 0.006 + 0.0064
           = 0.0124 元
```

单次调用约：

```text
0.0124 元
```

### 5.4 一天调用 10000 次，成本约多少？

```text
daily_cost = 0.0124 * 10000
           = 124 元
```

### 5.5 如果输出 token 减少 30%，一天能节省多少？

原 output tokens：

```text
800
```

减少 30%：

```text
800 * 30% = 240 tokens
```

单次节省 output 成本：

```text
saved_per_call = 240 / 1_000_000 * 8.00
               = 0.00192 元
```

一天 10000 次节省：

```text
saved_per_day = 0.00192 * 10000
              = 19.2 元
```

所以一天大约节省：

```text
19.2 元
```

---

## 6. 接口设计题：吵架帮手生产级 LLM Gateway 日志字段

### 6.1 推荐字段表

| 字段 | 说明 | 排查价值 |
|---|---|---|
| `request_id` | 单次模型调用 ID | 定位一次具体调用 |
| `trace_id` | 整条业务链路 ID | 串起前端、后端、模型、评分链路 |
| `user_id_hash` | 用户 ID 的 hash | 支持用户维度排查，同时避免明文用户 ID |
| `session_id` | 训练会话 ID | 分析一轮训练过程中的多次调用 |
| `scenario_id` | 冲突场景 ID | 判断哪个场景成本高或失败率高 |
| `provider` | 模型供应商 | 区分 GLM、混元、OpenAI-compatible 服务 |
| `model` | 模型名 | 分析不同模型质量、成本、延迟 |
| `prompt_version` | prompt 版本 | 判断回答变化是否由 prompt 改版导致 |
| `temperature` | 采样温度 | 排查输出过于发散或过于保守 |
| `max_tokens` | 最大输出 token | 排查输出截断或成本异常 |
| `attempt_count` | 尝试次数 | 判断是否发生重试 |
| `retry_errors` | 每次重试的错误 | 分析 provider 是否频繁 429 / 5xx |
| `latency_ms` | 总耗时 | 排查慢请求 |
| `input_tokens` | 输入 token | 排查 prompt / 上下文过长 |
| `output_tokens` | 输出 token | 排查输出过长和成本增加 |
| `total_tokens` | 总 token | 成本和限流分析 |
| `estimated_cost` | 估算成本 | 成本治理和异常告警 |
| `status` | success / error | 聚合成功率 |
| `error_type` | 错误类型 | 分析失败原因 |
| `http_status` | HTTP 状态码 | 识别 429、5xx、401 等问题 |
| `fallback_used` | 是否降级 | 判断主模型是否不稳定 |
| `fallback_model` | 降级模型 | 分析降级后的效果和成本 |
| `guardrail_result` | 安全检查结果 | 判断是否触发攻击、侮辱、威胁等风险 |

---

### 6.2 哪些字段需要脱敏？

需要脱敏或 hash：

```text
user_id
用户输入原文
模型输出原文
session_id
IP 地址
设备信息
任何包含隐私或账号的信息
```

建议策略：

```text
user_id → user_id_hash
input_text → 脱敏摘要 / hash / 采样记录
output_text → 脱敏摘要 / 采样记录
```

开发环境可以记录完整输入输出，但生产环境不能默认明文全量入库。

---

### 6.3 如何通过日志判断成本异常？

可以看：

```text
estimated_cost 是否突然升高
input_tokens 是否持续升高
output_tokens 是否持续升高
某个 scenario_id 成本是否异常
某个 prompt_version 是否导致 token 增加
某个 model 是否成本过高
```

典型判断：

```text
如果 input_tokens 突然上涨，可能是上下文拼装过长、历史消息没裁剪、RAG 召回过多。
如果 output_tokens 突然上涨，可能是 max_tokens 太大、prompt 没限制回答长度、模型输出啰嗦。
如果某个 prompt_version 成本变高，可能是 prompt 改版引入了过长 system prompt 或 examples。
```

---

### 6.4 如何通过日志判断 provider 不稳定？

可以聚合：

```text
error_type 分布
http_status 分布
429 比例
5xx 比例
timeout 比例
attempt_count 平均值
retry 成功率
latency_ms P95 / P99
fallback_used 比例
```

如果出现：

```text
429 上升
5xx 上升
timeout 上升
attempt_count 变高
fallback_used 变高
P95 latency 变高
```

说明 provider 可能不稳定，或者调用量已经接近限流，需要：

- 降低并发；
- 增加队列削峰；
- 减少 token；
- 切备用模型；
- 调整 rate limit；
- 做供应商级告警。

---

## 7. 面试题

题目：

> 你会如何把 LLM API 调用做成生产可用？

### 7.1 1 分钟参考答案

```text
我会把 LLM API 当作不稳定的外部推理依赖来治理，而不是在业务代码里直接散落 SDK 调用。首先会在 LLM Gateway 层统一封装 provider adapter、timeout、错误分类、retry policy、rate limit 处理、usage/cost 记录和结构化日志。

重试方面，我不会对所有错误无脑重试，而是先分类错误。对于 timeout、网络抖动、HTTP 429、HTTP 5xx 这类短暂性错误，我会做有限次数重试，并使用 exponential backoff with jitter，避免大量请求同时重试造成重试风暴。对于 API key 错误、参数错误、上下文超限、余额不足、模型不存在这类确定性错误，不做原样重试，而是直接返回错误、告警或降级处理。

日志方面，每次调用要记录 request_id、trace_id、provider、model、prompt_version、attempt_count、latency_ms、input_tokens、output_tokens、total_tokens、estimated_cost、error_type、http_status、fallback 信息和 guardrails 结果。这样才能排查质量、成本、限流和稳定性问题。

本质上，生产可用的 LLM API 调用不是简单调模型，而是把模型调用治理成可观测、可控、可降级、可评估的后端能力。
```

---

### 7.2 更短版本

```text
我会用 LLM Gateway 统一封装模型调用，在这一层处理 provider adapter、timeout、错误分类、有限重试、rate limit、usage/cost 和结构化日志。

重试不会无脑做，只对 timeout、429、5xx 等可恢复错误使用 exponential backoff with jitter；对 API key 错误、参数错误、上下文超限和余额不足不做原样重试。

同时每次调用记录 attempt、latency、token usage、estimated cost、error_type 和 fallback 信息，保证后续能排查稳定性、成本和质量问题。
```

---

## 8. 本节答案重点

你真正要掌握的是这 6 个判断：

1. LLM API 是外部不稳定依赖；
2. 错误处理先分类，再决定是否重试；
3. 只对短暂性错误做有限重试；
4. 指数退避控制频率，jitter 打散重试洪峰；
5. rate limit 同时看 RPM 和 TPM；
6. 没有 attempt / usage / cost / error 日志，就谈不上生产级 LLM Gateway。
