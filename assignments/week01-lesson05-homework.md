# Homework：Week 1 Lesson 5

> 主题：错误处理、超时、重试、限流与成本估算
> 预计耗时：45-60 分钟
> 代码目录：`code/llm-api-reliability/`

> 参考答案：[reviews/week01-lesson05-homework-reference.md](../reviews/week01-lesson05-homework-reference.md)

---

## 1. 基础概念题

请用自己的话回答：

1. 为什么说 LLM API 失败是常态，而不是偶发异常？
2. 为什么错误处理的第一步是“分类”，而不是直接重试？
3. `timeout` 对后端服务有什么意义？如果没有 timeout 会发生什么？
4. 什么是 exponential backoff with jitter？为什么要加 jitter？
5. RPM、TPM、RPD 分别是什么意思？为什么只看请求数不够？

---

## 2. 错误分类题

判断下面错误是否应该原样重试，并说明原因：

| 错误 | 是否重试 | 原因 |
|---|---|---|
| HTTP 429 Rate Limit |  |  |
| HTTP 500 Provider Error |  |  |
| API key 无效 |  |  |
| 请求上下文超限 |  |  |
| 网络连接超时 |  |  |
| 余额不足 / quota exhausted |  |  |
| 模型不存在 |  |  |
| HTTP 503 Service Unavailable |  |  |

---

## 3. Retry Policy 设计题

请设计一个 LLM API 的最小 retry policy，要求包含：

1. 最大重试次数；
2. 哪些错误可以重试；
3. 哪些错误不能重试；
4. 每次重试等待时间如何计算；
5. 如何避免大量请求同时重试；
6. 最终失败后如何返回给业务层。

---

## 4. 代码阅读题

阅读：

```text
code/llm-api-reliability/reliable_client.py
code/llm-api-reliability/demo_generate.py
```

回答：

1. `ProviderError` 为什么要区分 `retryable`？
2. `RetryPolicy` 里每个字段分别控制什么？
3. `_classify_http_error()` 如何判断哪些 HTTP 状态码可以重试？
4. `_sleep_before_retry()` 为什么要加入 jitter？
5. 成本估算是如何从 usage 字段计算出来的？
6. 结构化日志里哪些字段最适合用于排查 429 和成本异常？

---

## 5. 成本估算题

假设某模型价格如下：

```text
input_price_per_1m = 2.00 元
output_price_per_1m = 8.00 元
```

一次调用 usage：

```text
input_tokens = 3000
output_tokens = 800
total_tokens = 3800
```

请计算：

1. input 成本；
2. output 成本；
3. 总成本；
4. 如果一天调用 10000 次，成本约多少；
5. 如果输出 token 减少 30%，一天能节省多少。

---

## 6. 接口设计题

假设你要给“吵架帮手”接入生产级 LLM Gateway，请设计调用日志字段。

至少包含：

- request_id；
- user_id_hash；
- scenario_id；
- provider / model；
- prompt_version；
- retry / attempt；
- latency；
- usage / cost；
- error；
- fallback；
- guardrails。

要求：

1. 字段不能只罗列，要说明排查价值；
2. 说明哪些字段需要脱敏；
3. 说明如何通过日志判断成本异常；
4. 说明如何通过日志判断 provider 不稳定。

---

## 7. 面试题

准备 1 分钟回答：

> 你会如何把 LLM API 调用做成生产可用？

要求必须包含：

- LLM Gateway；
- timeout；
- 错误分类；
- retry policy；
- exponential backoff with jitter；
- rate limit；
- usage / cost；
- structured log；
- fallback。

---

## 8. 提交方式

把答案直接发给我即可。我会按以下维度批改：

1. 是否理解错误分类；
2. 是否知道哪些错误不能重试；
3. 是否能解释指数退避和 jitter；
4. 是否能设计生产级日志字段；
5. 是否能计算 token 成本；
6. 面试表达是否像后端工程师。
