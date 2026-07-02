# Homework：Week 1 Lesson 4

> 主题：Streaming 与后端接口封装  
> 预计耗时：45-60 分钟

> 参考答案：`reviews/week01-lesson04-homework-reference.md`

---

## 1. 基础概念题

请用自己的话回答：

1. LLM streaming 主要改善的是哪类体验？它是否一定让模型完整生成更快？
2. SSE、WebSocket、HTTP chunked streaming 有什么区别？本课为什么优先使用 SSE？
3. 为什么后端不应该把模型供应商的 streaming 原样透传给前端？
4. streaming 已经开始后，中途失败为什么不能再改 HTTP status？应该怎么通知前端？
5. 哪些场景不适合使用 streaming？至少列 3 个。

---

## 2. SSE 协议题

请解释下面 SSE 片段：

```text
event: delta
data: {"request_id":"abc","text":"你好"}

```

要求说明：

1. `event` 是什么；
2. `data` 是什么；
3. 为什么末尾需要空行；
4. 如果是流结束，应该设计什么 event；
5. 如果中途失败，应该设计什么 event。

---

## 3. 代码阅读题

阅读：

```text
code/llm-api-streaming/app.py
code/llm-api-streaming/streaming_client.py
```

回答：

1. `ChatStreamRequest` 做了哪些输入校验？这些校验为什么必要？
2. `event_generator()` 的作用是什么？为什么它里面用 `yield`？
3. `LLMStreamingClient.stream()` 为什么返回 `Iterator[StreamChunk]`？
4. `_openai_compatible_stream()` 如何解析 provider 返回的 `data:` 行？
5. 结构化日志是在什么时候写入的？成功和失败分别记录什么？

---

## 4. 接口设计题

假设你要为“吵架帮手”设计一个流式训练接口：

```text
POST /api/training/stream
```

请设计：

1. 请求 JSON 字段；
2. SSE 事件类型；
3. 每个事件的 data 字段；
4. 哪些字段要写入日志；
5. 如何处理中途失败；
6. 哪些输出需要 Guardrails 检查。

---

## 5. 场景判断题

判断下列场景是否适合 streaming，并说明原因：

| 场景 | 是否适合 | 原因 |
|---|---|---|
| 用户输入分类为“咨询/投诉/闲聊” |  |  |
| 生成 1000 字产品分析报告 |  |  |
| 固定 JSON 输出给后端解析 |  |  |
| Coding Agent 展示文件修改过程 |  |  |
| 后台批量生成 1000 条摘要 |  |  |

---

## 6. 面试题

准备 1 分钟回答：

> 你会如何设计一个生产可用的 LLM streaming endpoint？

要求必须包含：

- SSE / event 类型；
- 后端 Gateway 封装；
- provider adapter；
- 日志字段；
- 错误处理；
- 为什么不能直接透传供应商协议。

---

## 7. 提交方式

把答案直接发给我即可。我会按以下维度批改：

1. 是否理解 streaming 的真实价值；
2. 是否能区分 SSE / WebSocket / chunked streaming；
3. 是否能讲清后端封装边界；
4. 是否能读懂代码链路；
5. 是否具备生产风险意识；
6. 面试表达是否有系统性。
