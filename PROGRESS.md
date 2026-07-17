# AI Course Progress

> 课程进度 Ledger。每节课开始前读取，每节课结束后更新。

---

## 1. 当前状态

| 项目 | 状态 |
|---|---|
| 当前阶段 | Phase 1：Prompt Engineering 与结构化输出 |
| 当前周 | Week 2 |
| 当前课 | Lesson 6（进行中） |
| 课程节奏 | 每周 3 天，每天 ≥ 60 分钟 |
| 主语言 | Python 优先；工程化可用 Go |
| 当前总进度 | 6 / 39 lessons |
| 当前项目 | Project 1：LLM API Backend Service（Prompt 模板化阶段） |
| 下节课 | Week 2 Lesson 7：结构化输出：JSON Schema / Pydantic |

---

## 2. 已完成课程

- [x] L00 后端工程师的 AI 能力地图
- [x] L01 AI 圈黑话课 1：harness / loop / hermes / ReAct
- [x] L02 真实项目选择方法
- [x] L03 LLM API 第一课
- [x] L04 Streaming 与后端接口封装
- [x] L05 错误处理：超时、重试、限流、成本估算
- [ ] L06 Prompt 设计原则
- [ ] L07 结构化输出
- [ ] L08 Prompt 版本管理与测试集
- [ ] L09 Embedding 直觉与向量检索
- [ ] L10 Chunking / Metadata / Index
- [ ] L11 RAG 问答链路
- [ ] L12 Hybrid Search / Rerank
- [ ] L13 引用来源与幻觉控制
- [ ] L14 RAG Eval
- [ ] L15 Function Calling 基础
- [ ] L16 Tool Router 与多工具编排
- [ ] L17 工具安全与审计
- [ ] L18 Workflow vs Agent / Agent Loop
- [ ] L19 ReAct
- [ ] L20 Planning / Reflection
- [ ] L21 Short-term / Long-term Memory
- [ ] L22 Context Engineering
- [ ] L23 Agent 可靠性
- [ ] L24 LangGraph State / Node / Edge
- [ ] L25 Checkpoint / Persistence
- [ ] L26 Human-in-the-loop / Streaming / Trace
- [ ] L27 Supervisor + Worker
- [ ] L28 Debate / Review / Judge
- [ ] L29 真实项目拆解
- [ ] L30 MCP 核心概念
- [ ] L31 写一个本地 MCP Server
- [ ] L32 MCP 安全与权限
- [ ] L33 AI 服务架构
- [ ] L34 成本、模型路由、缓存、降级
- [ ] L35 Eval 自动化与部署
- [ ] L36 最终项目选型与架构
- [ ] L37 README / 架构图 / 技术方案
- [ ] L38 面试答辩与简历打磨

---

## 3. 作业状态

| 课程 | 作业 | 状态 | 备注 |
|---|---|---|---|
| L00 | `assignments/week00-lesson00-homework.md` | 已提交，已批改 | 课堂练习：`reviews/week00-lesson00-class-exercise.md`；作业批改：`reviews/week00-lesson00-homework-review.md` |
| L01 | `assignments/week00-lesson01-homework.md` | 已提交，已批改 | 课堂练习：`reviews/week00-lesson01-class-exercise.md`；作业批改：`reviews/week00-lesson01-homework-review.md` |
| L02 | `assignments/week00-lesson02-homework.md` | 已豁免 | 用户确认本节为项目选择方法课，不做课后习题；豁免记录：`reviews/week00-lesson02-homework-review.md` |
| L03 | `assignments/week01-lesson03-homework.md` | 已提交，已批改 | 课堂练习记录为历史留存；后续同类题合并到课后练习，完整批改：`reviews/week01-lesson03-homework-review.md` |
| L04 | [课后练习](assignments/week01-lesson04-homework.md) | 已提供参考答案，本节完成 | 用户选择不提交个人答案，直接查看参考答案；[参考答案](reviews/week01-lesson04-homework-reference.md) |
| L05 | [课后练习 HTML](assignments/week01-lesson05-homework.html) | 已提供参考答案，本节完成 | 讲义：[Lesson 5 HTML](lessons/week01-lesson05-error-retry-rate-limit-cost.html)；代码：[llm-api-reliability](code/llm-api-reliability/README.md)；[参考答案 HTML](reviews/week01-lesson05-homework-reference.html) |
| L06 | [课后练习 HTML](assignments/week02-lesson06-homework.html) | 已生成，未提交 | 讲义：[Lesson 6 HTML](lessons/week02-lesson06-prompt-design-principles.html)；代码：[prompt-design](code/prompt-design/README.md) |

---

## 4. 当前薄弱点

- MCP 概念边界需要持续保持准确：MCP 的核心是标准化连接工具、数据源和上下文资源，不是多 Agent 互相通信协议；
- Agent 概念需要从“记忆/上下文管理”升级到“目标驱动的任务执行循环”：LLM + Tools + Memory/State + Planning + Execution Loop；
- RAG 需要理解为“基于外部可追溯资料回答，降低幻觉并支持私有/实时知识”，不只是补充私有知识；
- 项目模块拆解还偏粗，需要训练输入、输出、状态、工具、失败处理、质量评估六个维度；
- Python、LangGraph、Eval、AI 项目工程化和面试表达需要系统补齐；
- Observation 与 Eval/Test Assertion 的边界要继续巩固：Observation 是工具或环境返回的事实结果，不等于结果断言；
- 风险题需要形成“风险 + 工程手段”的表达习惯，如 max steps、timeout、budget、tool whitelist、checkpoint、fallback；
- Lesson 2 已建立真实项目选择框架，后续选项目不能只看 star，需要使用 10 维评分；
- Lesson 3 开始后，需要重点建立 LLM API 工程边界：messages、token、model、temperature、LLM Gateway、usage、trace、timeout 和成本意识；
- Lesson 3 课堂练习暴露的问题：结构化输出不能只靠低 temperature，必须补 schema、validation、retry/fallback；LLM 调用日志必须补 token usage、cost、provider、prompt_version、finish_reason、retry_count，并考虑 messages/output 的隐私脱敏。
- Lesson 3 课后作业暴露的问题：参数选择题漏答复杂技术文章和高频改写场景；模型选择不能只从成本看，还要看质量、延迟、上下文、工具能力、合规和部署；`max_tokens` 与上下文窗口概念要区分；面试表达需要从“要求满分答案”升级到自己能组织 1 分钟回答。
- 后续课程形态修正：课堂练习和课后习题默认合并成一套课后练习，避免重复出题；代码示例必须补充必要注释和 Python 语法说明；模型调用示例必须支持通过配置切换 GLM、腾讯混元等 OpenAI-compatible provider。
- Lesson 4 需要重点掌握 Streaming 的工程边界：SSE 事件协议、首 token 感知延迟、后端统一封装、provider adapter、错误事件、代理缓冲、取消连接和结构化流式日志。
- Lesson 5 需要重点掌握 LLM API 可靠性治理：timeout、错误分类、可重试/不可重试错误、exponential backoff with jitter、rate limit、usage/cost、attempt 日志和 fallback 边界；
- Lesson 6 需要建立 Prompt 工程边界：Prompt 不是神奇咒语，而是包含 instruction、context、constraints、output contract、failure behavior 和版本信息的可测试规格；必须区分 Prompt 软约束与代码安全边界。

---

## 5. 项目进度

| 项目 | 状态 | 下一个动作 |
|---|---|---|
| Project 1：LLM API Backend Service | Prompt 模板化阶段 | Week 2 使用 `code/prompt-design/` 建立 Prompt Contract、变量校验和版本信息 |
| Project 2：RAG Knowledge Assistant | 未开始 | Week 3 创建 |
| Project 3：Tool-Using Agent | 未开始 | Week 5 创建 |
| Project 4：Multi-Agent Research Assistant | 未开始 | Week 8 创建 |
| Project 5：MCP Tool Server | 未开始 | Week 10 创建 |
| Final Project：真实项目复刻 + 改造 | 未开始 | Week 12 确定 |

---

## 6. 课后记录

### 2026-06-17 Lesson 0 课后记录

- 今日主题：后端工程师的 AI 能力地图。
- 关键概念：AI 应用不是简单调 API，而是围绕 LLM 构建可控、可观测、可评估、可降级的工程系统；后端能力可迁移到 LLM Gateway、RAG、Tool Server、Agent Task、Trace、Eval 等模块。
- 完成代码：无，本课为路线认知和诊断课。
- 作业：已提交并批改，记录见 `reviews/week00-lesson00-homework-review.md`。
- 掌握情况：能正确识别 LLM API 只是 AI 应用链路一环，具备较好的后端工程迁移意识。
- 薄弱点：MCP、Agent、RAG 的边界需要修正；项目模块拆解和面试表达需要继续训练。
- 下节课：Week 0 Lesson 1：AI 圈黑话课 1：harness / loop / hermes / ReAct。

### 2026-06-18 Lesson 1 课后记录

- 今日主题：AI 圈黑话课 1：harness / loop / hermes / ReAct。
- 关键概念：LLM 是推理生成组件，Harness 是工程运行环境；Agent Harness 管理 Tool、State、Trace、Eval、Guardrails、Budget 等生产级职责；Agent Loop 通过 Thought / Action / Observation 多步推进任务；Hermes 不能脱离项目上下文解释。
- 完成代码：无，本课为概念边界和系统设计训练课。
- 作业：已提交并批改，记录见 `reviews/week00-lesson01-homework-review.md`。
- 掌握情况：能较清楚地区分 Harness、Agent Harness、Agent Loop 和 ReAct，并能初步设计“吵架帮手 Agent Harness”的 Prompt、Tool、State、Guardrails 模块。
- 薄弱点：Observation 与 Eval/Test Assertion 的边界、Checkpoint 类比、风险与工程治理手段、Agent Harness 完整运行闭环仍需加强。
- 下节课：Week 0 Lesson 2：真实项目选择方法。

### 2026-06-22 Lesson 2 课后记录

- 今日主题：真实项目选择方法。
- 关键概念：选择 AI 项目不能只看 star，要看目标匹配、主链路清晰度、可运行性、可裁剪性、工程化含量、学习曲线、作品集价值、改造空间、资料质量和风险成本。
- 完成代码：无，本课为项目选择方法课。
- 作业：用户确认本节不做课后习题，已记录为作业豁免，见 `reviews/week00-lesson02-homework-review.md`。
- 掌握情况：本节作为后续项目选择框架，后续选 OpenAI Cookbook、LlamaIndex、LangGraph、TradingAgents 等项目时必须复用评分框架。
- 薄弱点：后续还需要通过真实项目练习，把评分框架转化为实际 repo 阅读和复刻能力。
- 下节课：Week 1 Lesson 3：LLM API 第一课。

### 2026-06-22 Lesson 3 课后记录

- 今日主题：LLM API 第一课：messages / token / model / temperature。
- 关键概念：LLM API 是外部推理依赖，生产中应通过 LLM Client / Gateway 统一封装 messages 构造、模型选择、参数治理、usage/cost、timeout/retry、trace/logging 和结构化输出校验。
- 完成代码：已生成 `code/llm-api-basics/`，包含最小 LLM Client、mock provider、OpenAI-compatible provider、GLM/腾讯混元配置示例、`.env.example`、Python 语法补充文档和 demo 脚本。
- 作业：已提交并批改，记录见 `reviews/week01-lesson03-homework-review.md`。
- 掌握情况：能理解 LLM API 不应散落在业务代码里，具备 Gateway、成本、参数和日志意识。
- 薄弱点：结构化输出治理、生产级日志字段、隐私脱敏、prompt_version、finish_reason、retry_count、参数选择完整性和面试表达仍需加强。
- 下节课：Week 1 Lesson 4：Streaming 与后端接口封装。

### 2026-07-02 Lesson 4 课后记录

- 今日主题：Streaming 与后端接口封装。
- 关键概念：Streaming 主要改善首 token 可见时间和用户感知延迟，不一定缩短完整生成耗时；后端应将 provider 原始 stream 转换为统一 SSE 事件协议，而不是直接透传供应商协议。
- 完成代码：已生成 `code/llm-api-streaming/`，包含 FastAPI SSE endpoint、OpenAI-compatible streaming client、结构化流式日志、GLM/腾讯混元配置示例和 Python 语法补充文档。
- 作业：用户选择不提交个人答案，直接查看参考答案，记录见 `reviews/week01-lesson04-homework-reference.md`。
- 掌握情况：已完成讲义、代码、作业、参考答案和课程中心入口；已修正 Python Notes 重复说明、mock 默认生成和课程中心链接问题。
- 薄弱点：后续仍需在真实 provider 调用中巩固 SSE error event、取消连接、代理缓冲、日志脱敏和 provider adapter 边界。
- 下节课：Week 1 Lesson 5：错误处理、超时、重试、限流、成本估算。

### 2026-07-16 Lesson 5 课后记录

- 今日主题：错误处理、超时、重试、限流与成本估算。
- 关键概念：LLM API 是不稳定外部依赖；错误处理先分类，再决定是否重试；只对 timeout、429、5xx 等短暂性错误做有限次数 exponential backoff with jitter；同时记录 usage、cost、attempt 和 error_type。
- 完成代码：`code/llm-api-reliability/`，包含真实 OpenAI-compatible provider 调用、timeout、错误分类、重试策略、成本估算和结构化日志。
- 作业：用户选择直接查看参考答案，见 `reviews/week01-lesson05-homework-reference.html`。
- 掌握情况：已实际运行真实 provider 示例，并定位过 API key 配置导致的 HTTP header 编码错误。
- 薄弱点：后续仍需通过真实 429/5xx 场景巩固 retry policy、Retry-After、fallback 和成本阈值设计。
- 下节课：Week 2 Lesson 6：Prompt 设计原则。

---

## 7. 已生成资料索引

| 类型 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 课程首页 | `course-showcase.html` | 已生成 | 已显示当前进度：L00-L05 完成，L06 进行中 |
| Markdown 阅读器 | `reader.html` | 已生成 | 用于 UTF-8 预览所有课程 Markdown |
| 术语表 | [GLOSSARY.html](GLOSSARY.html) / [GLOSSARY.md](GLOSSARY.md) | 持续更新 | 今日新增：Prompt Contract；已包含 Exponential Backoff、SSE、Responses API 等术语；课程入口优先使用 HTML 页面 |
| Lesson 0 讲义 | `lessons/week00-lesson00-ai-career-map.md` | 已完成 | 历史课程可回看 |
| Lesson 0 课堂练习 | `reviews/week00-lesson00-class-exercise.md` | 已完成 | 课中能力迁移诊断，不与课后作业混用 |
| Lesson 0 完整批改 | `reviews/week00-lesson00-homework-review.md` | 已完成 | 课后作业回看中心唯一保留的作业批改入口 |
| Lesson 1 讲义 | `lessons/week00-lesson01-ai-jargon-harness-loop-hermes-react.md` | 已完成 | AI 圈黑话课 1：harness / loop / hermes / ReAct |
| Lesson 1 课堂练习 | `reviews/week00-lesson01-class-exercise.md` | 已完成 | 课中 Harness / Loop / ReAct 诊断，不与课后作业混用 |
| Lesson 1 完整批改 | `reviews/week00-lesson01-homework-review.md` | 已完成 | 课后作业回看中心唯一保留的作业批改入口 |
| Lesson 2 讲义 | `lessons/week00-lesson02-real-project-selection.md` | 已完成 | 真实项目选择方法：项目分类、评分框架、GitHub 阅读 SOP、复刻层级 |
| Lesson 2 课程记录 | `reviews/week00-lesson02-class-note.md` | 已完成 | 本节无课堂练习，记录核心结论与后续安排 |
| Lesson 2 作业豁免记录 | `reviews/week00-lesson02-homework-review.md` | 已完成 | 用户确认本节不做课后习题，已记录豁免 |
| Lesson 3 讲义 | `lessons/week01-lesson03-llm-api-basics.md` | 已完成 | LLM API 第一课：messages / token / model / temperature |
| Lesson 3 代码 | `code/llm-api-basics/` | 已生成 | 最小 LLM Client，支持 mock、OpenAI-compatible、GLM、腾讯混元配置切换 |
| Lesson 3 Python 语法补充 | `code/llm-api-basics/PYTHON_NOTES.md` | 已生成 | 解释 dataclass、Pydantic、环境变量、httpx、model_dump 等语法点 |
| Lesson 3 课堂练习 | `reviews/week01-lesson03-class-exercise.md` | 历史留存 | 本次已发生，后续同类题不再与课后作业重复设置 |
| Lesson 3 完整批改 | `reviews/week01-lesson03-homework-review.md` | 已完成 | 课后作业回看中心唯一保留的作业批改入口 |
| Lesson 4 讲义 | [lessons/week01-lesson04-streaming-backend-sse.md](lessons/week01-lesson04-streaming-backend-sse.md) | 已完成 | Streaming 与后端接口封装：SSE、provider stream、FastAPI endpoint、错误事件和日志 |
| Lesson 4 代码 | [code/llm-api-streaming/README.md](code/llm-api-streaming/README.md) | 已生成 | FastAPI SSE endpoint、OpenAI-compatible stream，支持 GLM/腾讯混元配置切换 |
| Lesson 4 Python 语法补充 | [code/llm-api-streaming/PYTHON_NOTES.md](code/llm-api-streaming/PYTHON_NOTES.md) | 已生成 | 解释 generator/yield、Iterator、StreamingResponse、SSE event、httpx stream 等语法点 |
| Lesson 4 作业 | [assignments/week01-lesson04-homework.md](assignments/week01-lesson04-homework.md) | 已生成 | 按合并规则只设置一套课后练习/作业 |
| Lesson 4 参考答案 | [reviews/week01-lesson04-homework-reference.md](reviews/week01-lesson04-homework-reference.md) | 已生成 | 用户选择不提交个人答案，本文件作为标准参考答案在线回看 |
| Lesson 5 HTML 课件 | [lessons/week01-lesson05-error-retry-rate-limit-cost.html](lessons/week01-lesson05-error-retry-rate-limit-cost.html) | 已完成 | 可直接本地打开学习和检查的 HTML 课件 |
| Lesson 5 讲义 Markdown | [lessons/week01-lesson05-error-retry-rate-limit-cost.md](lessons/week01-lesson05-error-retry-rate-limit-cost.md) | 已生成 | 错误处理、超时、重试、限流与成本估算 |
| Lesson 5 代码 | [code/llm-api-reliability/README.md](code/llm-api-reliability/README.md) | 已生成 | 真实 provider 可靠性 LLM Client：timeout、retry、cost、日志 |
| Lesson 5 Python 语法补充 | [code/llm-api-reliability/PYTHON_NOTES.md](code/llm-api-reliability/PYTHON_NOTES.md) | 已生成 | 解释 ProviderError、RetryPolicy、Decimal、raise from、指数退避等新增语法点 |
| Lesson 5 作业 HTML | [assignments/week01-lesson05-homework.html](assignments/week01-lesson05-homework.html) | 已生成 | 课件页面“课后练习”入口指向此 HTML 页面 |
| Lesson 5 作业 Markdown | [assignments/week01-lesson05-homework.md](assignments/week01-lesson05-homework.md) | 已生成 | 按合并规则只设置一套课后练习/作业 |
| Lesson 5 参考答案 HTML | [reviews/week01-lesson05-homework-reference.html](reviews/week01-lesson05-homework-reference.html) | 已生成 | 课件页面“参考答案”入口指向此 HTML 页面 |
| Lesson 5 参考答案 Markdown | [reviews/week01-lesson05-homework-reference.md](reviews/week01-lesson05-homework-reference.md) | 已生成 | 覆盖错误分类、retry policy、成本估算、Gateway 日志和面试表达 |
| Lesson 6 HTML 课件 | [lessons/week02-lesson06-prompt-design-principles.html](lessons/week02-lesson06-prompt-design-principles.html) | 已生成，进行中 | Prompt 设计原则：instruction、context、examples、output contract、failure behavior |
| Lesson 6 讲义 Markdown | [lessons/week02-lesson06-prompt-design-principles.md](lessons/week02-lesson06-prompt-design-principles.md) | 已生成 | 深度讲义原始文件 |
| Lesson 6 代码 | [code/prompt-design/README.md](code/prompt-design/README.md) | 已生成 | PromptTemplate、变量校验、prompt key/version 与真实 provider 调用 |
| Lesson 6 Python 语法补充 | [code/prompt-design/PYTHON_NOTES.md](code/prompt-design/PYTHON_NOTES.md) | 已生成 | 解释 Mapping、Formatter.parse、集合差集、format_map 和变量白名单 |
| Lesson 6 作业 HTML | [assignments/week02-lesson06-homework.html](assignments/week02-lesson06-homework.html) | 已生成，未提交 | 本节唯一一套课后练习，HTML 页面可直接打开 |
| Lesson 6 作业 Markdown | [assignments/week02-lesson06-homework.md](assignments/week02-lesson06-homework.md) | 已生成 | 课后练习原始文件 |

---

## 8. 每节课后更新模板

```markdown
## YYYY-MM-DD Lesson X 课后记录
- 今日主题：
- 关键概念：
- 完成代码：
- 作业：
- 掌握情况：
- 薄弱点：
- 下节课：
```
