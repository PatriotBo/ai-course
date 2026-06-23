# Python 语法补充：LLM Client 示例代码

这份补充文档只解释本目录代码里用到的 Python 语法，方便边读代码边补基础。

## 1. `from __future__ import annotations`

作用：让类型注解延迟解析。

```python
from __future__ import annotations
```

在本项目里的好处：

- 可以更稳定地使用 `str | None`、`list[Message]` 这类现代类型写法；
- 减少某些循环引用或类未定义时的类型解析问题。

你可以先把它理解为：让类型注解更好用，不影响运行逻辑。

---

## 2. `Literal`：限制字符串只能取固定值

```python
Role = Literal["system", "user", "assistant", "tool"]
```

意思是：`role` 最好只写这四种字符串。

这样写的价值：

- 编辑器能更早发现拼写错误；
- 数据模型更清楚；
- 后续做 schema / validation 更自然。

---

## 3. Pydantic `BaseModel`

```python
class Message(BaseModel):
    role: Role
    content: str
```

`BaseModel` 会帮你做数据结构定义和基础校验。

比如后续你构造：

```python
Message(role="user", content="你好")
```

它会得到一个结构化对象，而不是随手拼 dict。

为什么 AI 工程里常用它：

- LLM 输入输出经常需要 schema；
- Tool Calling 参数需要校验；
- Structured Output 需要强约束；
- 后端接口也需要清晰的数据模型。

---

## 4. `Field(default_factory=...)`

```python
request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
```

意思是：如果调用方不传 `request_id`，就自动生成一个 UUID。

为什么不用：

```python
request_id: str = str(uuid.uuid4())
```

因为那样可能在类定义时只生成一次。`default_factory` 会在每次创建对象时生成新值。

---

## 5. `@dataclass`

```python
@dataclass
class LLMClient:
    provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "mock"))
```

`dataclass` 用来快速定义主要存数据的类。它会自动生成初始化方法。

这里用它是因为 `LLMClient` 需要保存：

- provider；
- api_key；
- base_url；
- timeout_seconds。

---

## 6. `field(default_factory=...)`

`dataclass` 里的 `field(default_factory=...)` 和 Pydantic 的 `Field(default_factory=...)` 思路类似：

```python
provider: str = field(default_factory=lambda: os.getenv("LLM_PROVIDER", "mock"))
```

每次创建 `LLMClient()` 时，从当前环境变量读取配置。

---

## 7. `__post_init__`

```python
def __post_init__(self) -> None:
    self.provider = self.provider.lower().strip()
```

`dataclass` 创建对象后，会自动调用 `__post_init__`。

这里做两件事：

1. 统一 provider 小写，避免 `GLM` / `glm` 混用；
2. 如果没配置 `LLM_BASE_URL`，根据 provider 填默认 base_url。

---

## 8. `with httpx.Client(...) as client`

```python
with httpx.Client(timeout=self.timeout_seconds) as client:
    response = client.post(...)
```

`with` 是上下文管理器，会自动管理资源。

这里的作用：

- 创建 HTTP client；
- 发请求；
- 退出代码块时自动释放连接资源。

---

## 9. `response.raise_for_status()`

```python
response.raise_for_status()
```

如果 HTTP 状态码不是 2xx，它会抛异常。

例如：

- 401：API Key 错；
- 403：权限不够；
- 429：限流；
- 500：供应商服务异常。

后续 Lesson 5 会在这附近加入 retry、fallback 和错误分类。

---

## 10. `model_dump()`

```python
[message.model_dump() for message in request.messages]
```

Pydantic 对象不能直接作为 JSON 发给模型接口，需要转成 dict。

`model_dump()` 会把：

```python
Message(role="user", content="你好")
```

转成：

```python
{"role": "user", "content": "你好"}
```

---

## 11. `rstrip('/')`

```python
f"{self.base_url.rstrip('/')}/chat/completions"
```

作用：去掉 base_url 末尾多余的 `/`。

这样下面两种配置都能得到正确地址：

```text
https://api.example.com/v1
https://api.example.com/v1/
```

最终都会拼成：

```text
https://api.example.com/v1/chat/completions
```

---

## 12. JSON Lines 日志：一行一个 JSON 对象

本节新增的调用日志使用 JSON Lines 格式：

```text
{"request_id": "...", "status": "success", ...}
{"request_id": "...", "status": "error", ...}
```

和普通 JSON 数组不同，JSON Lines 的好处是：

- 追加写入简单，不需要读取整个文件；
- `tail -f` 可以实时观察；
- 后续导入日志系统或数据分析工具也方便。

代码里对应的是：

```python
file.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
```

---

## 13. `Path(...).mkdir()` 和追加写入

```python
log_file = Path(self.log_path).expanduser()
log_file.parent.mkdir(parents=True, exist_ok=True)
with log_file.open("a", encoding="utf-8") as file:
    file.write(...)
```

这里有几个点：

- `Path` 是 Python 标准库 `pathlib` 里的路径对象，比手写字符串拼路径更稳；
- `expanduser()` 会把 `~/xxx` 展开成用户目录；
- `mkdir(parents=True, exist_ok=True)` 表示父目录不存在就创建，已经存在也不报错；
- `open("a")` 是 append 追加模式，不会覆盖旧日志；
- `encoding="utf-8"` 保证中文输入输出不会乱码。

---

## 14. 本节你最该掌握的 Python 点

优先级从高到低：

1. 看懂 `BaseModel` 如何定义请求和响应；
2. 看懂 `dataclass` 如何保存 client 配置；
3. 看懂环境变量如何控制 provider/model/base_url/api_key；
4. 看懂 `httpx.Client.post()` 如何调用 OpenAI-compatible 接口；
5. 看懂 `usage` / `latency_ms` 为什么要进入标准返回结果；
6. 看懂 JSON Lines 日志为什么适合模型调用记录；
7. 看懂 `open("a")` 为什么是追加写入，不会覆盖已有日志。
