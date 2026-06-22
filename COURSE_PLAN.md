# AI 应用 / Agent 开发课程总纲

> 学员：后端开发工程师 → AI 应用 / Agent 工程师  
> 节奏：12 周，每周 3 节，每节 ≥ 60 分钟  
> 主语言：Python 优先；工程化扩展使用 Go  
> 课程风格：DeepLearning.AI 的概念密度 + Udacity/Coursera 的项目制 + YouTube 实战课的边写边跑 + 后端工程化标准  
> 更新日期：2026-06-16

---

## 0. 总目标

把传统后端能力升级为 AI 应用工程能力，最终具备：

1. 能独立构建 LLM API 服务、RAG、Tool Calling、Agent、MCP Server；
2. 能用工程化方式处理日志、重试、降级、成本、评估、部署；
3. 能拆解真实 GitHub AI 项目并改造成自己的项目；
4. 能准备 2-3 个可写进简历的 AI 项目；
5. 能在面试中讲清楚 AI Agent / RAG / MCP / Eval / Memory 的原理、架构和生产坑。

---

## 1. 课程参考体系

### DeepLearning.AI / 吴恩达路线
- Agentic AI：Reflection、Tool Use、Planning、Multi-Agent、Evals、成本和延迟优化。
- Prompt Engineering for Developers：Prompt 原则、迭代优化、结构化任务。
- LangChain / LlamaIndex / MCP / Agent Memory 短课程：框架和专项能力。

### OpenAI Cookbook 路线
- LLM API / Responses API / Prompt Caching / Cost API / Rate Limit。
- RAG：Embeddings、File Search、PDF RAG、多模态 RAG。
- Tool Calling：Structured Outputs、MCP Tool、多工具编排。
- Evals：结构化输出评估、Agent Eval、Prompt Evaluation Flywheel。

### LangGraph 官方路线
- State、Node、Edge、Graph。
- Checkpoint / Persistence。
- Human-in-the-loop。
- Multi-agent orchestration。
- Streaming、Tracing、Debugging。

### LlamaIndex 官方路线
- Data Connectors、Indexes、Query Engines、Chat Engines。
- Agents、Workflows。
- Evaluation / Observability。
- LlamaParse / LlamaExtract / LlamaCloud。

### MCP 官方路线
- Server、Client、Tools、Resources、Prompts。
- AI 应用连接外部系统的标准协议。

---

## 2. 12 周课程地图

| 周 | 阶段 | 主题 | 阶段产物 |
|---|---|---|---|
| Week 0 | Phase 0 | AI 能力地图 + AI 圈术语 | 学习路线图 + 术语表 v1 |
| Week 1 | Phase 1 | LLM API 基础 | 可运行 LLM 调用脚本 |
| Week 2 | Phase 1 | Prompt Engineering + 结构化输出 | Prompt 测试集 + JSON 输出服务 |
| Week 3 | Phase 2 | RAG 基础：Embedding / Chunking / Vector DB | 本地文档问答 Demo |
| Week 4 | Phase 2 | RAG 进阶：Hybrid Search / Rerank / Eval | RAG 知识库助手 v1 |
| Week 5 | Phase 3 | Tool Calling / Function Calling | Tool-Using Assistant v1 |
| Week 6 | Phase 4 | Agent Loop / ReAct / Planning / Reflection | 单 Agent 任务执行器 |
| Week 7 | Phase 4 | Memory / Context Engineering / Agent 可靠性 | 带记忆的 Agent |
| Week 8 | Phase 5 | LangGraph：State / Node / Edge / Checkpoint | 可恢复 Agent Workflow |
| Week 9 | Phase 5 | Multi-Agent / Supervisor / Debate | 多 Agent Research Assistant |
| Week 10 | Phase 6 | MCP：Server / Client / Tools / Resources | 本地 MCP Server |
| Week 11 | Phase 7 | AI 应用工程化：服务化、成本、评估、部署 | Production AI Service Template |
| Week 12 | Phase 8 | 真实项目拆解 + 简历化 | 最终项目 + 面试材料 |

---

## 3. 36 节课详细列表

### Week 0：AI 能力地图与术语入门
| 课次 | 主题 | 目标 | 产出 |
|---|---|---|---|
| L00 | 后端工程师的 AI 能力地图 | 搞清楚岗位能力、学习路径和最终项目 | 学习路线图 |
| L01 | AI 圈黑话课 1：harness / loop / hermes / ReAct | 建立概念索引，避免后续听不懂 | GLOSSARY v1 |
| L02 | 真实项目选择方法 | 从 GitHub/课程项目里筛选适合复刻的项目 | 项目候选清单 |

### Week 1：LLM API 基础
| L03 | LLM API 第一课：messages / token / model / temperature | 会调用模型并理解参数 | `code/llm-api-basics` |
| L04 | Streaming 与后端接口封装 | 用 FastAPI 输出 SSE 流 | streaming endpoint |
| L05 | 错误处理：超时、重试、限流、成本估算 | 写出生产可用调用 wrapper | LLM client wrapper |

### Week 2：Prompt Engineering 与结构化输出
| L06 | Prompt 设计原则：instruction / context / examples | 写稳定 prompt | prompt templates |
| L07 | 结构化输出：JSON Schema / Pydantic | 输出可解析 JSON | schema output demo |
| L08 | Prompt 版本管理与测试集 | 像测接口一样测 prompt | prompt eval mini harness |

### Week 3：RAG 基础
| L09 | Embedding 直觉与向量检索 | 理解语义搜索 | embedding demo |
| L10 | Chunking / Metadata / Index | 会切文档并建立索引 | local vector index |
| L11 | RAG 问答链路 | 完成基础文档问答 | RAG v0 |

### Week 4：RAG 进阶
| L12 | Hybrid Search / Rerank | 提升召回质量 | rerank demo |
| L13 | 引用来源与幻觉控制 | 回答可追溯 | citation RAG |
| L14 | RAG Eval | 建立测试集和评分方法 | RAG eval report |

### Week 5：Tool Calling
| L15 | Function Calling 基础 | 定义工具 schema | calculator/weather tools |
| L16 | Tool Router 与多工具编排 | 模型选择工具并执行 | multi-tool assistant |
| L17 | 工具安全与审计 | 权限、超时、重试、日志 | tool guardrails |

### Week 6：Agent 基础
| L18 | Workflow vs Agent / Agent Loop | 理解 Agent 不是一次调用 | agent loop demo |
| L19 | ReAct：Reasoning + Acting | 实现观察-思考-行动循环 | ReAct mini agent |
| L20 | Planning / Reflection | 任务规划和自我修复 | planner-reflector demo |

### Week 7：Memory 与上下文工程
| L21 | Short-term / Long-term Memory | 区分工作记忆与长期记忆 | memory store demo |
| L22 | Context Engineering | 上下文预算、压缩、摘要 | context packer |
| L23 | Agent 可靠性 | 防死循环、失败恢复、人工审批 | reliability checklist |

### Week 8：LangGraph 工程化
| L24 | State / Node / Edge | 用图表达 Agent Workflow | simple graph |
| L25 | Checkpoint / Persistence | 中断后恢复执行 | checkpoint demo |
| L26 | Human-in-the-loop / Streaming / Trace | 人工审批和可观测 | reviewable workflow |

### Week 9：多 Agent
| L27 | Supervisor + Worker | 多角色分工 | supervisor-worker demo |
| L28 | Debate / Review / Judge | 多 Agent 辩论和评审 | debate agent |
| L29 | TradingAgents / OpenHands / Dify 项目拆解 | 学真实项目架构 | project teardown note |

### Week 10：MCP
| L30 | MCP 核心概念 | Server / Client / Tools / Resources / Prompts | MCP concept map |
| L31 | 写一个本地 MCP Server | 暴露一个文件/搜索/数据库工具 | local MCP server |
| L32 | MCP 安全与权限 | 工具边界、路径白名单、审批 | MCP security checklist |

### Week 11：AI 应用工程化
| L33 | AI 服务架构 | FastAPI + Go Gateway + Queue | service blueprint |
| L34 | 成本、模型路由、缓存、降级 | 生产成本控制 | routing policy |
| L35 | Eval 自动化与部署 | 回归测试 + Docker + CI | production template |

### Week 12：最终项目与面试化
| L36 | 最终项目选型与架构 | 从真实项目改造成自己的项目 | final project plan |
| L37 | README / 架构图 / 技术方案 | 项目可展示 | project docs |
| L38 | 面试答辩与简历打磨 | 能讲清楚项目 | resume bullets + Q&A |

---

## 4. 每节课固定结构

```text
00-10 min  回顾上节课 + 作业状态
10-25 min  今日核心概念 + 系统框架 + 边界条件
25-45 min  代码/架构实战 + 工程风险
45-55 min  关键追问 + 误区纠正
55-60 min  总结 + 课后练习/面试题
```

每节课输出：
1. Markdown 讲义；
2. 可运行代码；
3. 一套课后练习/作业文件（避免与课堂练习重复）；
4. 参考资料；
5. 进度更新。

说明：后续默认不再同时设置“课堂练习 + 课后习题”两套重复题；只有真实课堂互动、设计评审或代码调试诊断明显不同于课后作业时，才单独生成课堂记录。

---

## 5. 阶段项目

| 项目 | 阶段 | 说明 | 技术栈 |
|---|---|---|---|
| Project 1 | Week 1-2 | LLM API 后端服务 | Python, FastAPI, Pydantic, SSE |
| Project 2 | Week 3-4 | RAG 知识库助手 | Python, Embedding, Vector DB, Rerank |
| Project 3 | Week 5-7 | Tool-Using Agent | Python, Tool Calling, Memory |
| Project 4 | Week 8-10 | Multi-Agent Research Assistant | LangGraph, Checkpoint, Debate |
| Project 5 | Week 10-11 | MCP Tool Server | MCP, Python, Go optional |
| Final Project | Week 12 | 真实 GitHub 项目复刻 + 改造 | 待选 |

---

## 6. 真实项目候选池

| 项目 | 学习价值 | 适合阶段 |
|---|---|---|
| OpenAI Cookbook | API/RAG/Tool/Eval 实战样例 | 全程参考 |
| LangGraph examples | Agent Workflow 工程化 | Week 8-9 |
| LlamaIndex examples | RAG / Workflow / Agent | Week 3-5 |
| Dify | AI 应用平台架构 | Week 12 拆解 |
| RAGFlow / AnythingLLM | RAG 产品化 | Week 4 / Week 12 |
| OpenHands / SWE-agent | Coding Agent | Week 9 / Week 12 |
| TradingAgents | 多 Agent 投研 | Week 9 |
| mem0 / Supermemory | Agent Memory | Week 7 |

---

## 7. 评估标准

每周从 7 个维度评估：

1. 概念能否讲清楚；
2. 代码能否跑通；
3. 是否理解边界和坑；
4. 是否能设计架构；
5. 是否能做工程化封装；
6. 是否能回答面试追问；
7. 是否能沉淀项目资产。

---

## 8. 下一个动作

当前状态：课程体系已搭建。  
下一节：`Week 0 Lesson 0：后端工程师的 AI 能力地图`。

正式开课触发语：

```text
开始 Lesson 0
```
