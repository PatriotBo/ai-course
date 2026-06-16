# AI Course Projects

> 课程项目档案。目标是形成可运行、可展示、可写进简历的项目资产。

---

## Project 1：LLM API Backend Service

| 项 | 内容 |
|---|---|
| 时间 | Week 1-2 |
| 目标 | 封装一个生产友好的 LLM 调用后端服务 |
| 技术栈 | Python, FastAPI, Pydantic, SSE, dotenv |
| 核心能力 | 普通生成、流式输出、结构化输出、重试、超时、成本日志 |
| 可写简历 | 设计并实现支持流式输出、结构化响应和异常重试的 LLM API 网关服务 |

交付物：
- `code/llm-api-service/`
- README
- API 文档
- Prompt 测试集

---

## Project 2：RAG Knowledge Assistant

| 项 | 内容 |
|---|---|
| 时间 | Week 3-4 |
| 目标 | 构建一个可查询本地文档的 RAG 知识库助手 |
| 技术栈 | Python, LlamaIndex/LangChain, Vector DB, Rerank |
| 核心能力 | 文档加载、切分、Embedding、检索、引用来源、RAG Eval |
| 可写简历 | 构建企业知识库 RAG 系统，支持文档检索、引用溯源和评估闭环 |

真实项目参考：
- LlamaIndex examples
- OpenAI Cookbook RAG examples
- AnythingLLM / RAGFlow

---

## Project 3：Tool-Using Agent

| 项 | 内容 |
|---|---|
| 时间 | Week 5-7 |
| 目标 | 构建能选择工具、执行工具、处理失败的 Agent |
| 技术栈 | Python, Tool Calling, Pydantic, SQLite/Redis optional |
| 核心能力 | Tool Schema、Tool Router、执行日志、权限边界、Memory |
| 可写简历 | 实现支持多工具编排、权限校验和失败恢复的 AI Agent 系统 |

---

## Project 4：Multi-Agent Research Assistant

| 项 | 内容 |
|---|---|
| 时间 | Week 8-9 |
| 目标 | 用 LangGraph 构建多 Agent 调研助手 |
| 技术栈 | LangGraph, Checkpoint, Supervisor/Worker, Debate |
| 核心能力 | 状态机、checkpoint、人工审批、多 Agent 协作 |
| 可写简历 | 基于 LangGraph 构建可恢复的多智能体研究工作流，支持调研、辩论、审查与报告生成 |

真实项目参考：
- TradingAgents
- LangGraph examples
- OpenHands / SWE-agent 架构

---

## Project 5：MCP Tool Server

| 项 | 内容 |
|---|---|
| 时间 | Week 10 |
| 目标 | 写一个本地 MCP Server，让 AI 能调用你的工具 |
| 技术栈 | MCP SDK, Python, Go optional |
| 核心能力 | Tools、Resources、Prompts、权限控制、路径白名单 |
| 可写简历 | 设计并实现 MCP Server，将本地工具和业务数据标准化暴露给 AI Agent |

---

## Final Project：真实项目复刻 + 改造

候选方向：

| 方向 | 参考项目 | 适合原因 |
|---|---|---|
| AI 投研助手 | TradingAgents | 已学习过，贴合投资兴趣，多 Agent 架构完整 |
| RAG 知识库 | RAGFlow / AnythingLLM | 易展示，企业常见需求 |
| Coding Agent | OpenHands / SWE-agent | 招聘市场关注度高 |
| 个人任务 Agent | goal-driven-agent / LangGraph examples | 可结合个人长期目标系统 |
| 吵架帮手 Agent 版 | 自有项目 + Agent Memory | 和独立开发目标强绑定 |

最终项目要求：
- 能本地运行；
- 有 README；
- 有架构图；
- 有部署说明；
- 有 Eval 或测试集；
- 能讲 5 分钟架构；
- 能回答 10 个面试追问。
