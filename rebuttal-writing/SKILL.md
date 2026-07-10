---
name: rebuttal-writing
description: "当需要撰写、重构或压缩 AI/ML conference rebuttal、reviewer response 或 AC response 时使用；覆盖匿名性、开头感谢、问题弱化改写、Markdown Q&A 格式、强证据回答、小表格、引用和礼貌结尾。"
---

# Rebuttal Writing

## 使用场景

- 为 AI/ML conference 写 reviewer rebuttal、author response、discussion reply 或 AC summary。
- 把零散实验、case、修订承诺和 reviewer comment 整理成紧凑 Markdown。
- 在字数限制下，把尖锐问题转写成可回答、对作者有利但不歪曲原意的 `Q1/Q2/...`。
- 回答必须完全匿名，不能出现作者身份、外部链接、GitHub、主页、机构、项目私有路径或任何可反查身份的信息。

## 总体原则

- 先感谢，再回答；先承认 reviewer 的有效关注点，再给证据。
- 问题摘要要弱化尖锐措辞，但不能偷换问题。
- 回答要具体，优先使用数据、补充实验、ablation、case study、统计检验、表格和真实引用。
- 少写空泛套话，例如 “we will improve” 或 “this is interesting”；必须说清楚改什么、结果是什么、支持什么结论。
- rebuttal 通常有严格字数限制；每个回答先给核心结论，再给最强证据。
- 只承诺实际可以放进 revised version / appendix 的内容；不要编造实验、数据、引用或未来开源链接。

## 推荐结构

### Reviewer-specific response

```md
Dear Reviewer,

Thank you for your careful review and constructive comments. We are pleased that you recognized [认可点1] and [认可点2]. Regarding your remaining concerns about [主题A], [主题B], and [主题C], we respond below.

> **Q1: Clarification on [弱化后的问题简述].**

**Response.** [一句话直接回答核心疑问。]

- **Evidence 1.** [数据/实验/case/修订位置。]
- **Evidence 2.** [机制解释或对比。]

| Setting | Metric | Result |
| --- | --- | --- |
| [baseline] | [metric] | [value] |
| [ours] | [metric] | **[value]** |

> **Q2: Concern regarding [弱化后的问题简述].**

**Response.** [直接回答。] [如需引用，用 `[1]`。]

We hope these responses clarify your concerns. If they address your questions, we would be grateful if you could consider updating your score. If any concern remains, we would be happy to continue the discussion.

### References

- `[1]` *[Paper Title]*
```

### Global / AC response

```md
Dear Area Chair and Reviewers,

We sincerely thank all reviewers for their time, careful evaluation, and constructive feedback. We are grateful that the reviews recognized [共同认可点]. Below, we summarize the major concerns and the evidence we added to address them.

| Concern | Response | Evidence |
| --- | --- | --- |
| [concern A] | [one-line answer] | [metric/table/appendix] |
| [concern B] | [one-line answer] | [case/statistical test] |

- **Concern A.** [2-3 sentences with concrete evidence.]
- **Concern B.** [2-3 sentences with concrete evidence.]

We hope this summary helps clarify the main issues raised during review. We are grateful for the reviewers' feedback and would be happy to provide further clarification if needed.
```

## 开头段写法

开头段一般包含四件事：

- **称呼**：`Dear Reviewer,`、`Dear Reviewers,` 或 `Dear Area Chair and Reviewers,`。
- **感谢**：感谢认真审阅和建设性意见。
- **正向锚点**：点名 reviewer 认可的地方，例如 writing quality、novel task、strong experiments、broad benchmark。
- **过渡**：说明剩余疑问会在下面逐条回答。

推荐句式：

```md
Dear Reviewer,

Thank you for your careful review and constructive comments. We are pleased that you recognized [positive aspect]. Regarding your remaining concerns about [A], [B], and [C], we respond below.
```

避免：

- 开头就反驳 reviewer。
- “We disagree with you” 这类强对抗表达。
- 过度道歉，把问题说得比 reviewer 更严重。
- 引入外部链接或身份线索。

## 问题摘要写法

每个问题用 Markdown blockquote：

```md
> **Q1: Clarification on [topic].**
```

改写规则：

- 把 “fatal flaw / not novel / invalid / missing” 改成 “clarification / concern / request for details / relation to prior work”。
- 把宽泛批评收窄成可回答的问题。
- 把攻击性表述转成中性学术表述。
- 保留 reviewer 的核心疑问，不要篡改为完全不同的问题。

示例：

| 原始尖锐问题 | 推荐 Q 摘要 |
| --- | --- |
| The method is not novel. | `> **Q1: Clarification on novelty relative to prior work.**` |
| The benchmark may be biased because GPT-4o was used. | `> **Q1: Concern about potential construction bias from LLM-assisted data generation.**` |
| The experiments are insufficient. | `> **Q1: Request for additional evidence on experimental coverage.**` |
| The metric is questionable. | `> **Q1: Clarification on the rationale and robustness of the metric.**` |

## 回答写法

每个回答按证据强度组织：

1. **直接结论**：第一句回答问题，不绕。
2. **强证据**：数据、表格、补充实验、统计检验、case。
3. **机制解释**：为什么这个结果能回应 concern。
4. **修订承诺**：会在 revised paper 的哪个部分补充。
5. **引用**：必要时用 `[1]`，最后集中列 reference。

推荐模板：

```md
**Response.** The main improvement comes from [factor], not from [reviewer concern]. We support this with three pieces of evidence.

- **Ablation.** [具体设置] improves [metric] from [x] to [y].
- **Case study.** In [case type], [method] avoids [failure mode].
- **Revision.** We will add this analysis to [Section/Appendix].
```

不要只写：

- “We agree and will clarify.”
- “This is beyond the scope.”
- “The reviewer misunderstood.”
- “More details will be added.”

如果确实超出范围，仍要正向包装：

```md
**Response.** Our current scope focuses on [bounded setting]. Within this setting, [evidence]. We agree that extending to [broader setting] is valuable and will explicitly discuss it as future work.
```

## 表格和数据

小表格非常适合 rebuttal，因为它能在短字数内制造证据密度。

表格规则：

- 控制在 2-5 列、2-6 行。
- 只展示能直接回答问题的指标。
- 用 `**bold**` 标最好结果，不要塞大 leaderboard。
- 表格前后各用一句话解释，不要让表格自己说话。

模板：

```md
The added ablation shows that the gain remains after controlling for [factor].

| Setting | Acc.↑ | F1↑ | Notes |
| --- | ---: | ---: | --- |
| Baseline | 60.9 | 63.2 | single LLM |
| Ours | **80.8** | **76.8** | same base model |

This supports that the improvement is mainly due to [method component].
```

## 引用格式

- rebuttal 中引用用 `[1]`、`[2]`，不要使用外部链接。
- 最后加 `### References`。
- reference 只写论文题名即可；如果会场允许，也可写作者/年份，但不要写 URL。
- 只能引用真实存在且相关的论文；不确定就先查证，不要编造标题。
- citation 要紧跟被支持的 claim，而不是一段末尾堆很多引用。

格式：

```md
This setting follows common practice in agent benchmark evaluation `[1]`.

### References

- `[1]` *[Paper Title]*
```

## 结尾段写法

结尾要礼貌、简洁、可继续沟通：

```md
We hope these responses clarify your concerns. If they address your questions, we would be grateful if you could consider updating your score. If any concern remains, we would be happy to continue the discussion. Thank you again for your time and feedback.
```

注意：

- 可以请求更新评分，但语气要克制。
- 不要施压、抱怨或暗示 reviewer 不公平。
- 不要泄露身份或附外部链接。

## 匿名性和安全检查

提交前逐项检查：

- 没有作者姓名、机构、邮箱、GitHub、个人主页、项目主页、匿名仓库链接。
- 没有本地路径、私有数据路径、内部服务器、真实 token、私有账号。
- 没有 “our released code at ...” 或 “we have open-sourced ...” 这类可反查线索。
- 没有引用未公开补充材料中的外部链接。
- 没有过度承诺无法在 revised version 中实现的实验。
- 没有攻击 reviewer 的语气。

## 快速检查清单

- 第一段是否感谢 reviewer 并点出认可点？
- 每个问题是否用 `> **Qx: ...**`？
- Q 摘要是否中性、可回答、不过度暴露缺点？
- 每个 response 第一段是否直接回答？
- 是否至少用一个强证据回答核心 concern？
- 表格是否小而有用？
- 引用是否真实、紧跟 claim、最后有 `References`？
- 最后一段是否礼貌请求更新评分并表示愿意继续沟通？
- 全文是否匿名、无外部链接、无身份线索？
