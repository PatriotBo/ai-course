# code/llm-api-basics

本目录对应 Week 1 Lesson 3：LLM API 第一课。

目标不是炫技，而是建立一个最小但有工程意识的 LLM Client：

- 统一读取模型配置；
- 支持 mock provider，没 API key 也能跑通链路；
- 支持 OpenAI-compatible 接口，配置 `provider / model / base_url / api_key` 即可切换 OpenAI、智谱 GLM、腾讯混元等模型；
- 记录 request_id、latency、usage；
- 为后续 timeout、retry、cost log、structured output 做铺垫。

如果你阅读 Python 语法时有卡点，先看：[`PYTHON_NOTES.md`](PYTHON_NOTES.md)。

## 运行 mock 模式

```bash
cd ai-course/code/llm-api-basics
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo_generate.py
```

默认 `LLM_PROVIDER=mock`，不会产生 API 费用。

## 接真实 OpenAI-compatible API

```bash
cp .env.example .env
```

编辑 `.env`。课程示例统一使用这四个配置项：

```text
LLM_PROVIDER=openai_compatible
LLM_API_KEY=你的 key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=你的模型名
```

再运行：

```bash
python demo_generate.py
```

不要提交 `.env`。

### 切换到智谱 GLM

智谱 GLM 支持 OpenAI-compatible 调用。只需要改配置，不需要改代码：

```text
LLM_PROVIDER=glm
LLM_API_KEY=你的智谱 API Key
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/
LLM_MODEL=glm-5.2
```

如果你已经在系统环境变量里设置了 `ZAI_API_KEY`，代码也会自动读取。

### 切换到腾讯混元 Hunyuan

腾讯混元也支持 OpenAI-compatible 调用：

```text
LLM_PROVIDER=hunyuan
LLM_API_KEY=你的混元 API Key
LLM_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
LLM_MODEL=hunyuan-turbos-latest
```

如果你已经在系统环境变量里设置了 `HUNYUAN_API_KEY`，代码也会自动读取。

## 后续扩展

下一步会逐渐加入：

- timeout；
- retry with backoff；
- rate limit；
- token cost estimate；
- structured output；
- streaming；
- prompt version；
- eval harness。

## 配置原则

本目录后续统一遵守一个原则：

```text
换模型 = 改配置，不改业务代码
```

也就是只改：

```text
LLM_PROVIDER
LLM_MODEL
LLM_BASE_URL
LLM_API_KEY
```

业务层仍然只调用：

```python
client = LLMClient()
result = client.generate(request)
```
