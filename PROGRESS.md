# AI Course Progress

> 课程进度 Ledger。每节课开始前读取，每节课结束后更新。

---

## 1. 当前状态

| 项目 | 状态 |
|---|---|
| 当前阶段 | Phase 0：AI 能力地图与术语入门 |
| 当前周 | Week 0 |
| 当前课 | Lesson 1（待开始） |
| 课程节奏 | 每周 3 天，每天 ≥ 60 分钟 |
| 主语言 | Python 优先；工程化可用 Go |
| 当前总进度 | 1 / 39 lessons |
| 当前项目 | 尚未开始 |
| 下节课 | Week 0 Lesson 1：AI 圈黑话课 1：harness / loop / hermes / ReAct |

---

## 2. 已完成课程

- [x] L00 后端工程师的 AI 能力地图
- [ ] L01 AI 圈黑话课 1：harness / loop / hermes / ReAct
- [ ] L02 真实项目选择方法
- [ ] L03 LLM API 第一课
- [ ] L04 Streaming 与后端接口封装
- [ ] L05 错误处理：超时、重试、限流、成本估算
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

---

## 4. 当前薄弱点

> Lesson 0 作业批改后诊断。

- MCP 概念边界需要修正：MCP 的核心是标准化连接工具、数据源和上下文资源，不是多 Agent 互相通信协议；
- Agent 概念需要从“记忆/上下文管理”升级到“目标驱动的任务执行循环”：LLM + Tools + Memory/State + Planning + Execution Loop；
- RAG 需要理解为“基于外部可追溯资料回答，降低幻觉并支持私有/实时知识”，不只是补充私有知识；
- 项目模块拆解还偏粗，需要训练输入、输出、状态、工具、失败处理、质量评估六个维度；
- Python、LangGraph、Eval、AI 项目工程化和面试表达需要系统补齐。

---

## 5. 项目进度

| 项目 | 状态 | 下一个动作 |
|---|---|---|
| Project 1：LLM API Backend Service | 未开始 | Week 1 创建 |
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

---

## 7. 已生成资料索引

| 类型 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 课程首页 | `course-showcase.html` | 已生成 | 已显示当前进度：L00 完成，L01 待开始 |
| Markdown 阅读器 | `reader.html` | 已生成 | 用于 UTF-8 预览所有课程 Markdown |
| Lesson 0 讲义 | `lessons/week00-lesson00-ai-career-map.md` | 已完成 | 历史课程可回看 |
| Lesson 0 课堂练习 | `reviews/week00-lesson00-class-exercise.md` | 已完成 | 课中能力迁移诊断，不与课后作业混用 |
| Lesson 0 课后作业 | `assignments/week00-lesson00-homework.md` | 已提交，已批改 | 题目与提交记录保留在仓库中；不作为课后回看中心主入口 |
| Lesson 0 完整批改 | `reviews/week00-lesson00-homework-review.md` | 已完成 | 课后作业回看中心唯一保留的作业批改入口 |
| 术语表 | `GLOSSARY.md` | 持续更新 | 今日新增：Agentic AI |
| Lesson 1 讲义 | 待生成 | 未开始 | 开始 Lesson 1 后再生成真实文件并开放入口 |

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
