# Lesson 7 代码：结构化输出、Pydantic 校验与有限修复

本目录对应 Week 2 Lesson 7：结构化输出——JSON Schema / Pydantic。

本节把上一课的 Output Contract 变成后端可执行链路：

```text
业务输入
  ↓
Prompt + JSON Schema
  ↓
真实 OpenAI-compatible Provider
  ↓
模型原始文本
  ↓
JSON 提取与语法解析
  ↓
Pydantic Schema 校验
  ↓
业务规则校验
  ├── 通过 → IncidentSummary
  └── 失败 → 最多一次 repair → 再失败则显式报错
```

---

## 1. 文件说明

| 文件 | 作用 |
|---|---|
| `models.py` | 严格 Pydantic 模型、枚举、字段范围、额外字段拒绝 |
| `structured_output.py` | JSON 提取、Schema 校验、业务校验、一次 repair 与统一异常 |
| `provider.py` | 真实 OpenAI-compatible provider，支持 GLM / 腾讯混元等配置切换 |
| `demo_generate.py` | 事故摘要端到端演示，输出校验结果与 repair 次数 |
| `test_structured_output.py` | 覆盖 JSON 提取、字段错误、业务规则和 repair 预算 |
| `.env.example` | Provider / model / base_url / api_key 配置 |
| `PYTHON_NOTES.md` | 解释本节新增的 Pydantic v2 和类型语法 |

---

## 2. 安装与配置

请使用隔离环境，不要把依赖装到系统 Python：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

然后在 `.env` 中设置真实 Provider。

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

`LLM_RESPONSE_MODE=text` 兼容性最好。如果你确认当前 Provider 支持 OpenAI-compatible JSON mode，可以改为：

```text
LLM_RESPONSE_MODE=json_object
```

注意：JSON mode 只提高“输出是 JSON”的概率，不能替代 Pydantic 和业务规则校验。

---

## 3. 运行测试

```bash
python -m unittest -v test_structured_output.py
```

测试不调用真实模型，原因不是提供 mock provider，而是 `generate_structured()` 通过 callable 注入边界测试纯业务逻辑。生产演示仍默认真实 Provider。

覆盖边界：

- 纯 JSON、Markdown fenced JSON、前后解释文本；
- 多个 JSON object、括号不完整；
- 枚举错误、额外字段、字段范围；
- Schema 合法但业务状态矛盾；
- 首次失败后修复成功；
- 修复预算耗尽后明确失败。

---

## 4. 运行真实 Provider 演示

```bash
python demo_generate.py
```

成功输出：

```json
{
  "status": "ok",
  "provider": "glm",
  "model": "glm-5.2",
  "attempts": 1,
  "repaired": false,
  "data": {}
}
```

失败时不会返回半合法对象，而是输出：

```text
status=failed
error=structured output failed after 2 attempts
issues=[具体字段错误]
```

---

## 5. 三层契约必须分开

### 5.1 JSON 语法合法

只能证明字符串能被 `json.loads()` 解析，不能证明字段正确。

### 5.2 Schema 合法

Pydantic 验证字段名、类型、枚举、长度、范围和额外字段。

### 5.3 业务可用

例如以下对象 JSON 与 Schema 都可能合法，但业务上矛盾：

```json
{
  "status": "complete",
  "confirmed_root_cause": "unknown"
}
```

所以 `_check_business_rules()` 仍然必要。

---

## 6. Repair 的正确边界

本示例只允许一次 repair：

1. 把字段级错误摘要返回给模型；
2. 附上完整 JSON Schema；
3. 要求只修格式与字段，不新增事实；
4. 第二次失败立即结束。

不要做：

- 无限重试；
- 用正则偷偷补引号、删逗号；
- 校验失败后仍把原始对象送入数据库；
- 把 repair 当成事实纠错工具。

Repair 解决的是“表达不符合契约”，不是“内容不真实”。

---

## 7. 建议阅读顺序

1. `models.py`：先看 Schema；
2. `test_structured_output.py`：从失败边界理解需求；
3. `structured_output.py`：看提取、校验与 repair；
4. `provider.py`：看供应商边界；
5. `demo_generate.py`：看端到端组合。
