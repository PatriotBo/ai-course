# Week 1 Lesson 5：错误处理、超时、重试、限流与成本估算

> 状态：今日正式开课
> 预计时长：60-75 分钟
> 本节类型：工程可靠性 + 生产治理 + LLM Gateway 基础设施
> 代码目录：`code/llm-api-reliability/`

---

## 0. 本节课为什么重要

前两节我们已经建立了 LLM API 的两个基础能力：

```text
Lesson 3：普通模型调用 + messages / token / model / temperature
Lesson 4：streaming + SSE 后端接口封装
```

但这些还只是“能调用”。生产系统真正难的是：

```text
模型调用失败怎么办？
接口超时怎么办？
429 限流怎么办？
调用成本怎么记录？
哪些错误可以重试，哪些错误绝对不能重试？
如何避免重试把系统打爆？
```

这节课的目标是把 LLM API 从“能跑”提升为“能治理”。

一句话：

```text
LLM API 是外部不稳定依赖，必须像治理数据库、RPC、消息队列一样治理它。
```

---

## 1. LLM API 的失败不是异常情况，而是常态

传统后端调用数据库、Redis、RPC 时，我们默认会遇到：

- 网络抖动；
- 超时；
- 连接池耗尽；
- 下游 5xx；
- 限流；
- 参数错误；
- 权限错误。

LLM API 也一样，而且更复杂。

常见失败包括：

| 类型 | 表现 | 是否适合重试 |
|---|---|---|
| Timeout | 请求超时、连接断开 | 可以有限重试 |
| Rate Limit | HTTP 429 | 可以退避重试，但不能无脑重试 |
| 5xx | provider 服务异常 | 可以有限重试 |
| Auth Error | API key 错误、权限不足 | 不应重试 |
| Invalid Request | 参数错误、上下文超限 | 不应原样重试 |
| Quota Exhausted | 余额不足、额度用完 | 不应重试，应告警或降级 |
| Content Filter | 内容被安全策略拦截 | 不应直接重试，应改变输入或兜底 |

你要建立一个基本判断：

```text
不是所有错误都该 retry。
```

错误处理的第一步不是重试，而是分类。

---

## 2. 生产级 LLM Client 的最小可靠性职责

一个生产级 LLM Client / Gateway 至少要做这些事：

```text
业务层
  ↓
Prompt Builder / Context Builder
  ↓
Reliable LLM Client
  ├── timeout
  ├── retry policy
  ├── rate limit awareness
  ├── error classification
  ├── fallback hook
  ├── usage / cost estimate
  └── structured log
  ↓
Provider Adapter
  ↓
GLM / Hunyuan / OpenAI-compatible provider
```

注意这里的顺序。

不要把 retry 写成一个孤立装饰器就结束了。生产里你要知道：

- 为什么失败；
- 第几次失败；
- 本次是否还值得重试；
- 重试等待多久；
- 最终成功还是失败；
- 花了多少 token；
- 估算成本多少；
- 是否需要降级模型；
- 是否需要告警。

---

## 3. Timeout：不要让模型调用无限挂住

LLM 调用可能因为 provider 抖动、网络问题、响应过长而卡住。

如果没有 timeout，后端请求会一直占着资源：

```text
HTTP worker 被占用
连接被占用
用户一直等待
上游请求堆积
最终拖垮服务
```

所以所有 LLM 调用都必须设置 timeout。

常见策略：

| 场景 | timeout 建议 |
|---|---|
| 短分类 / 标签 | 3-10 秒 |
| 普通问答 | 15-30 秒 |
| 长文生成 | 60 秒左右 |
| 后台批处理 | 可以更长，但应异步化 |
| streaming | 需要区分连接 timeout 和读超时 |

本节代码用：

```text
LLM_TIMEOUT_SECONDS
```

统一控制超时时间。

---

## 4. Retry：重试是药，不是饭

重试能提升成功率，但也可能放大故障。

错误做法：

```text
失败就立刻重试
重试次数很大
所有错误都重试
所有用户同时重试
没有日志
没有退避
```

这会导致典型问题：

```text
provider 已经限流
  ↓
你的系统疯狂重试
  ↓
失败请求也计入限流
  ↓
限流更严重
  ↓
系统雪崩
```

正确做法：

```text
只对可恢复错误重试
有限次数
指数退避
加入 jitter
记录 attempt
最终失败要可观测
```

---

## 5. Exponential Backoff：指数退避

今日新增术语是：**Exponential Backoff with Jitter**。

指数退避的意思是：

```text
第 1 次失败：等 1 秒
第 2 次失败：等 2 秒
第 3 次失败：等 4 秒
第 4 次失败：等 8 秒
```

jitter 是随机扰动：

```text
实际等待 = 基础等待时间 + 一点随机偏移
```

为什么要 jitter？

因为如果很多请求同时失败，又同时按固定 1、2、4 秒重试，会形成“重试洪峰”。jitter 可以把这些请求打散。

官方文档也强调：处理 429 / rate limit 时应使用指数退避；失败请求本身也会消耗限流额度，所以不能持续重复发送同一请求。

本节代码不用第三方 retry 库，而是手写一个小的 retry loop，方便你看清楚底层逻辑。

---

## 6. 哪些错误可以重试？

可以重试的通常是短暂性错误：

```text
Timeout
网络连接失败
HTTP 429 rate limit
HTTP 500 / 502 / 503 / 504
```

不该重试的通常是确定性错误：

```text
API key 错误
权限不足
余额不足
参数非法
上下文超限
模型不存在
内容安全拦截
```

判断标准：

```text
重试同一个请求，有没有合理概率变成功？
```

如果答案是没有，就不要重试。

例如：

```text
API key 错了，重试 100 次也还是错。
上下文超限，原样重试 100 次也还是超限。
余额不足，重试只会浪费时间。
```

---

## 7. Rate Limit：RPM / TPM / RPD

LLM provider 常见限流维度：

| 缩写 | 含义 |
|---|---|
| RPM | Requests Per Minute，每分钟请求数 |
| TPM | Tokens Per Minute，每分钟 token 数 |
| RPD | Requests Per Day，每天请求数 |

429 不一定只是请求太多，也可能是 token 太多。

例如：

```text
每分钟最多 60 次请求
每分钟最多 100000 tokens
```

你请求次数不多，但每次都塞很长上下文，也可能触发 TPM 限制。

所以治理 rate limit 不能只看请求数，还要看：

```text
input_tokens
output_tokens
total_tokens
max_tokens
并发数
重试次数
```

---

## 8. 成本估算：先粗略，再精确

生产系统不能等账单来了才知道花了多少钱。

每次模型调用应该记录：

```text
provider
model
input_tokens
output_tokens
total_tokens
estimated_cost
```

成本估算公式通常是：

```text
input_cost = input_tokens / 1_000_000 * input_price_per_1m
output_cost = output_tokens / 1_000_000 * output_price_per_1m
total_cost = input_cost + output_cost
```

注意：不同 provider 的 usage 字段名可能不同。

OpenAI-compatible 常见：

```json
{
  "usage": {
    "prompt_tokens": 100,
    "completion_tokens": 50,
    "total_tokens": 150
  }
}
```

课程代码会统一转换成：

```text
input_tokens
output_tokens
total_tokens
estimated_cost
```

---

## 9. 结构化日志字段

本节继续使用结构化日志，但不重复讲 JSONL 的基础好处。你只需要关注这次新增的可靠性字段：

```text
request_id
provider
model
base_url
status
attempt_count
retryable
error_type
error_message
http_status
latency_ms
timeout_seconds
input_tokens
output_tokens
total_tokens
estimated_cost
```

关键是：日志要能回答这些问题：

```text
这次调用成功了吗？
失败原因是什么？
重试了几次？
每次等待多久？
是否命中了限流？
最终花了多少 token？
成本大概多少？
```

---

## 10. Fallback：什么时候降级？

Fallback 不是本节代码的重点，但你要先建立意识。

当主模型失败时，可以有几种降级：

| 降级方式 | 适合场景 |
|---|---|
| 切备用模型 | 主模型 5xx / 429 |
| 切小模型 | 成本压力大或任务简单 |
| 返回安全兜底回答 | 高风险或内容过滤 |
| 转异步任务 | 长任务超时 |
| 人工处理 | 高价值失败请求 |

但 fallback 也有风险：

```text
备用模型质量可能更差
输出风格可能不同
工具能力可能不一致
模型可能共享同一限流池
```

所以 fallback 不能偷偷发生，必须记录到日志里。

---

## 11. 本节代码目录

```text
code/llm-api-reliability/
  README.md
  PYTHON_NOTES.md
  requirements.txt
  .env.example
  reliable_client.py
  demo_generate.py
```

这次遵守最新课程规则：

```text
不默认生成 mock provider
不把 mock 作为默认路径
默认使用真实 OpenAI-compatible provider 配置
```

代码支持：

```text
LLM_PROVIDER
LLM_MODEL
LLM_BASE_URL
LLM_API_KEY
```

可切换：

```text
glm
hunyuan
openai_compatible
openai
```

---

## 12. 本节课后练习

本节只保留一套课后练习，不再单独出课堂练习。

文件：

```text
assignments/week01-lesson05-homework.md
```

重点训练：

1. 错误分类；
2. 哪些错误可以重试；
3. 指数退避和 jitter；
4. rate limit 的 RPM / TPM；
5. 成本估算字段；
6. 生产级 LLM Client 的面试表达。

---

## 13. 面试表达

如果面试官问：

> 你如何把 LLM API 调用做成生产可用？

不要只说：

```text
加个 retry。
```

更好的表达：

```text
我会把 LLM API 当作不稳定的外部推理依赖来治理。首先在 LLM Gateway 层统一封装 provider adapter、timeout、错误分类、retry policy、rate limit 处理、usage/cost 记录和结构化日志。

重试方面，我不会对所有错误无脑重试，而是只对 timeout、429、5xx 这类短暂性错误做有限重试，并使用 exponential backoff with jitter，避免重试风暴。对 API key 错误、参数错误、quota exhausted、上下文超限等确定性错误不做原样重试。

同时每次调用要记录 request_id、provider、model、attempt_count、latency、usage、estimated_cost、error_type、http_status 和 fallback 信息。这样后续才能排查质量、成本、限流和稳定性问题。
```

---

## 14. 本节你必须记住的 5 句话

1. LLM API 失败是常态，不是异常情况。
2. 错误处理的第一步是分类，不是重试。
3. 只对可恢复错误做有限重试，并使用指数退避和 jitter。
4. rate limit 不只看请求数，也要看 token 数。
5. 没有 usage / cost / attempt 日志，就谈不上生产级 LLM Gateway。
