# Lesson 6 Python 语法补充

> 只解释本节新增语法，不重复前面已经讲过的 dataclass、Pydantic、环境变量和 JSONL。

---

## 1. `Mapping[str, str]`

```python
from typing import Mapping

def render(self, variables: Mapping[str, str]) -> RenderedPrompt:
    ...
```

`Mapping` 表示“可以按 key 读取值的映射对象”。它比直接写 `dict[str, str]` 更宽松：普通 `dict` 可以传入，只读映射也可以传入。

这里的含义是：

```text
render 接收一组字符串变量，但不要求调用方必须使用某一种具体字典实现。
```

---

## 2. `string.Formatter().parse()`

```python
from string import Formatter

formatter = Formatter()
parts = formatter.parse("你好，{name}")
```

`Formatter.parse()` 会把格式字符串拆成多个部分，其中包含变量名。

本节代码用它提取：

```text
{name}
{audience}
{incident_context}
```

这样在程序启动时就能发现：

- 模板用了变量，但 `required_variables` 没声明；
- `required_variables` 声明了变量，但模板根本没用。

这比等到线上调用 `.format_map()` 才发现错误更早。

---

## 3. 集合差集

```python
undeclared = placeholders - declared
unused = declared - placeholders
```

Python 的 `set` 支持差集运算：

```text
A - B = 在 A 里但不在 B 里的元素
```

在本节里：

```text
placeholders - declared
```

表示模板实际使用了、但没有声明的变量。

```text
declared - placeholders
```

表示声明了、但模板没有使用的变量。

---

## 4. `format_map()`

```python
content = template.format_map(safe_variables)
```

它会用映射中的值替换模板占位符：

```python
"面向{audience}".format_map({"audience": "后端工程师"})
```

结果：

```text
面向后端工程师
```

为什么本节先校验变量，再调用 `format_map()`？

因为缺少变量时，直接调用会抛 `KeyError`。提前检查后，可以给业务层更清晰的错误：

```text
Missing required prompt variables: ['incident_context']
```

---

## 5. 字典推导式做白名单

```python
safe_variables = {
    name: variables[name]
    for name in self.required_variables
}
```

这叫字典推导式。

这里不是为了少写几行，而是做变量白名单：只允许模板声明过的变量进入渲染过程。调用方即使额外传入其他字段，也不会被拼进 Prompt。

---

## 6. 本节阅读重点

按顺序看：

1. `_extract_placeholders()` 如何找模板变量；
2. `__post_init__()` 如何检查模板定义；
3. `render()` 如何检查运行时变量；
4. `safe_variables` 如何限制变量范围；
5. `RenderedPrompt` 如何携带 key/version/messages。
