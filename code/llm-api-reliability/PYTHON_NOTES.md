# Python 语法补充：Lesson 5 Reliability

本文件只解释 Lesson 5 新增的 Python 语法和可靠性代码结构，不重复解释前面已经讲过的 Pydantic、dataclass、JSONL 基础概念。

---

## 1. 自定义异常 `ProviderError`

```python
class ProviderError(RuntimeError):
    def __init__(self, message: str, *, retryable: bool, error_type: str, http_status: int | None = None) -> None:
```

这里自定义异常是为了把 provider 错误变成可操作的数据：

- `retryable`：是否值得重试；
- `error_type`：错误类型，如 `rate_limit`、`timeout`；
- `http_status`：HTTP 状态码。

`*` 的意思是后面的参数必须用关键字传入，例如：

```python
ProviderError("timeout", retryable=True, error_type="timeout")
```

这样可以避免调用时把参数位置写错。

---

## 2. `@dataclass(frozen=True)`

```python
@dataclass(frozen=True)
class RetryPolicy:
```

`frozen=True` 表示对象创建后字段不能再被修改。

适合 retry policy 这种配置对象，因为运行中不应该随便改：

```python
policy.max_retries = 100  # 会报错
```

这能减少“运行中被意外修改配置”的风险。

---

## 3. `Decimal` 为什么用于价格计算

```python
from decimal import Decimal
```

浮点数适合工程计算，但金额计算更适合 `Decimal`，因为它能减少二进制浮点误差。

本节成本估算只是粗略估算，但仍然用 `Decimal` 表示更严谨的习惯。

---

## 4. `raise ... from exc`

```python
raise ProviderError(...) from exc
```

这表示把底层异常包装成新的业务异常，同时保留原始异常链。

好处是：

- 业务层只处理统一的 `ProviderError`；
- debug 时仍然能看到底层是 `TimeoutException`、`HTTPStatusError` 还是网络错误。

---

## 5. `set` 用于状态码分类

```python
RETRYABLE_STATUS_CODES = {408, 409, 425, 429, 500, 502, 503, 504}
```

`set` 适合做“是否包含”的判断：

```python
status in RETRYABLE_STATUS_CODES
```

比 list 更表达语义：这里不是有序列表，而是一组可重试状态码。

---

## 6. retry loop 的结构

```python
for attempt in range(1, max_attempts + 1):
    try:
        return self._call_provider_once(...)
    except ProviderError as exc:
        ...
```

这个结构表达了：

```text
每次只调用一次 provider
失败后由外层循环决定是否继续
```

这样比把 retry 混在 HTTP 请求函数里更清晰。

---

## 7. 指数退避计算

```python
base_delay = min(base * (2 ** (attempt - 1)), max_delay)
jitter = random.uniform(0, base_delay * jitter_ratio)
time.sleep(base_delay + jitter)
```

核心点：

- `2 ** n` 表示 2 的 n 次方；
- `min(..., max_delay)` 限制最大等待时间；
- `random.uniform()` 生成随机扰动；
- `time.sleep()` 暂停当前线程。

生产异步服务里更常用 `asyncio.sleep()`，本节先用同步版本讲清楚逻辑。

---

## 8. 本节你最该看懂的链路

```text
generate()
  ↓
for attempt in retry loop
  ↓
_call_provider_once()
  ↓
_classify_http_error() / timeout / transport error
  ↓
_sleep_before_retry()
  ↓
_normalize_usage()
  ↓
_estimate_cost()
  ↓
_write_log()
```

不要只看语法，要看职责边界：

- `generate()` 管重试；
- `_call_provider_once()` 管单次 HTTP 调用；
- `_classify_http_error()` 管错误分类；
- `_estimate_cost()` 管成本估算；
- `_write_log()` 管结构化记录。
