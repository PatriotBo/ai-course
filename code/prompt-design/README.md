# Lesson 6 代码：Prompt 设计与模板化

本目录对应 Week 2 Lesson 6：Prompt 设计原则。

本节不追求“写一段更长的 Prompt”，而是把 Prompt 变成可维护的工程对象：

```text
业务变量
  ↓
PromptTemplate.render()
  ├── 检查 required_variables
  ├── 渲染 system instruction
  ├── 渲染 user context
  └── 返回 prompt_key / prompt_version / messages
  ↓
OpenAI-compatible Client
  ↓
GLM / 腾讯混元 / 其他兼容 Provider
```

---

## 1. 文件说明

| 文件 | 作用 |
|---|---|
| `prompt_template.py` | PromptTemplate、变量校验、Prompt Contract 示例 |
| `demo_generate.py` | 使用真实 provider 渲染 Prompt 并调用模型 |
| `test_prompt_template.py` | 校验正常渲染、缺失变量、复合占位符和重复变量 |
| `.env.example` | GLM / 腾讯混元 / OpenAI-compatible 配置 |
| `PYTHON_NOTES.md` | 只解释本节新增的模板解析语法 |
| `requirements.txt` | Python 依赖 |

---

## 2. 安装与配置

```bash
cd ai-course/code/prompt-design
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

然后把 `.env` 中的 `LLM_API_KEY` 替换成真实 key。

GLM：

```text
LLM_PROVIDER=glm
LLM_API_KEY=replace_with_your_real_api_key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
LLM_MODEL=glm-5.2
```

腾讯混元：

```text
LLM_PROVIDER=hunyuan
LLM_API_KEY=replace_with_your_real_api_key
LLM_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
LLM_MODEL=hunyuan-turbos-latest
```

---

## 3. 运行

```bash
python demo_generate.py
```

输出包含：

```text
provider
model
prompt_key
prompt_version
usage
model output
```

程序默认调用你配置的真实 provider。

---

## 4. 重点阅读顺序

1. 先看 `INCIDENT_SUMMARY_PROMPT` 的六个区块；
2. 再看 `PromptTemplate.__post_init__()` 如何检查模板定义；
3. 看 `render()` 如何检查业务变量并生成 messages；
4. 最后看 `demo_generate.py` 如何把 Prompt Builder 接到真实 provider。

---

## 5. 工程边界

本节负责：

- Prompt 模板化；
- 变量校验；
- instruction/context 分层；
- prompt_key / prompt_version；
- 真实 provider 调用。

本节暂不负责：

- JSON Schema 强校验（Lesson 7）；
- Prompt 测试集与回归 Eval（Lesson 8）；
- Prompt Registry / 灰度发布；
- Prompt Injection 的完整防御体系。
