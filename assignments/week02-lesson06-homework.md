# Week 2 Lesson 6：课后练习

> 主题：Prompt 设计原则——Instruction / Context / Examples / Output Contract
> 预计耗时：45-60 分钟
> 代码目录：`code/prompt-design/`

---

## 1. 基础概念题

请用自己的话回答：

1. 为什么说 Prompt Engineering 更接近“编写规格”，而不是寻找神奇咒语？
2. Instruction 和 Context 的区别是什么？为什么要分开？
3. Output Contract 应该解决什么问题？
4. Failure Behavior 为什么是生产 Prompt 的关键组成？
5. 什么情况下适合加入 Few-shot examples？examples 有哪些风险？
6. 为什么 system prompt 不能被当作真正的安全边界？

---

## 2. Prompt 拆解题

阅读下面 Prompt：

```text
你是一个客服助手。根据用户反馈判断问题并给出处理建议。回答要专业，不要胡说，尽量简洁。

用户反馈：付款后订单仍显示未支付，已经等了两个小时。
```

请指出它缺少哪些部分：

```text
Role / Scope：
Task / Instruction：
Context：
Constraints：
Output Contract：
Failure Behavior：
Examples：是否需要？为什么？
```

---

## 3. Prompt 改写题

把上面的客服 Prompt 改写为一个可执行的 Prompt Contract。

要求：

- 只能使用用户提供的信息；
- 不能猜测订单真实状态；
- 输出必须包括 `issue_type`、`known_facts`、`unknowns`、`next_actions`；
- 缺失信息要明确标记；
- 指出是否需要人工客服或订单查询工具；
- instruction 与用户输入必须使用分隔符隔开。

---

## 4. Failure Behavior 设计题

为下面三个场景分别设计 failure behavior：

1. 事故复盘材料缺少明确根因；
2. 用户要求模型根据不存在的数据预测销售额；
3. 两份输入文档对同一事实描述冲突。

每个场景回答：

```text
模型不应该做什么：
模型应该输出什么：
后端是否需要额外处理：
```

---

## 5. 代码阅读题

阅读：

```text
code/prompt-design/prompt_template.py
code/prompt-design/demo_generate.py
```

回答：

1. `required_variables` 的作用是什么？为什么要在调用模型前校验？
2. `PromptTemplate.render()` 返回了哪些信息？
3. 为什么需要同时记录 `prompt_key` 和 `prompt_version`？
4. `_extract_placeholders()` 为什么要解析模板变量？
5. 如果要加入 Few-shot examples，你会放在哪一层？

---

## 6. Prompt Review 题

请按照以下 10 个维度评审你在第 3 题写出的 Prompt，每项回答“通过 / 不通过 + 原因”：

```text
Goal
Inputs
Boundary
Constraints
Output
Failure
Examples
Cost
Safety
Observability
```

---

## 7. 面试题

准备 1 分钟回答：

> 你会如何设计、管理和迭代一个生产级 Prompt？

必须包含：

- Prompt Builder；
- instruction / context 分离；
- output contract；
- failure behavior；
- prompt_key / prompt_version；
- 测试集和回归评估；
- Prompt 不是安全边界。

---

## 8. 提交方式

把答案直接发给我。我会按以下维度批改：

1. 是否真正理解 Prompt 是规格而不是文案；
2. 是否能区分规则、数据和输出契约；
3. 是否能设计缺失信息和冲突信息的处理；
4. 是否能把 Prompt 放进工程链路；
5. 面试表达是否系统、准确、可落地。
