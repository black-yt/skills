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
- reviewer 提到的弱点、concern 和 question 都要一对一回应；即使原文不是问句，也要转成正式的 `Q1/Q2/...` 来回答。
- 回答要具体，优先使用数据、补充实验、ablation、case study、统计检验、表格和真实引用。
- 新增实验不能只报数值；必须用一句话简介实验 setting，例如数据集/子集、模型或方法、指标、对照项和改变的变量。
- 少写空泛套话，例如 “we will improve” 或 “this is interesting”；必须说清楚改什么、结果是什么、支持什么结论。
- rebuttal 通常有严格字数限制；每个回答先给核心结论，再给最强证据。
- 整体回复应该是高信息密度的纯文本 Q&A，不要把 reviewer response 整体改成表格。
- 每个段落第一句话必须简短清楚地给出该段核心点，后文再展开证据或解释。
- 只有当内容天然适合结构化表达时才用分点或表格；不要为了显得充足而加入低信息量表格或空泛 bullet。
- 只承诺实际可以放进 revised version / appendix 的内容；不要编造实验、数据、引用或未来开源链接。

## 推荐结构

### Reviewer-specific response

```md
Dear Reviewer,

Thank you for your careful review and constructive comments. We are pleased that you recognized [认可点1] and [认可点2]. Regarding your remaining concerns about [主题A], [主题B], and [主题C], we respond below.

> **Q1: Clarification on [弱化后的问题简述].**

**Response.** [一句话直接回答核心疑问。]

[用一段高密度文本解释核心证据。段首第一句先给结论，随后展开实验、case 或修订位置。]

[只有在多个证据点天然并列时才用分点。]

- **Ablation.** [具体设置和数值变化。]
- **Case study.** [具体 failure mode 和改进。]

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

The main concerns are [A], [B], and [C]. We address them with [new experiment/statistical test/case analysis], and provide reviewer-specific details below.

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

## 问题覆盖与引用策略

覆盖规则：

- **弱点也算问题**：reviewer 写成 `Weaknesses`、`Concerns`、`Limitations` 或普通陈述时，也要逐条抽取成 `Q1/Q2/...`。
- **默认一对一**：每个 reviewer 的每个实质性弱点或疑问默认单独回答，不要只挑显式 question 回答。
- **谨慎合并**：只有两个点内容高度相似、证据完全相同或一个点明显是另一个点的子问题时，才合并成一个 Q。
- **合并要透明**：合并后在 Q 摘要或首句说明覆盖两个 concerns，避免 reviewer 觉得某个点被跳过。
- **不要过度合并**：同一 reviewer 的 novelty、metric、experiment、writing、scope 等不同维度问题通常应分开回答。

同一 reviewer 内可以做问题间引用：

- 后面的回答可以引用前面已经解释过的证据，例如 “As discussed in Q2, ...”。
- 引用应尽量从后文指向前文，不要让读者先看到一个尚未解释的 future reference。
- 引用只能减少重复背景，不能替代当前 Q 的直接回答；每个 Q 仍要有自己的第一句核心结论。
- 如果 Q4 依赖 Q2 的 ablation，Q4 中只复述与当前问题直接相关的结论和数值。

跨 reviewer 引用是高风险技巧，只在特定情况下使用：

- 适用场景：有明确积极或高分 reviewer，且低分 reviewer 批评的点正好被积极 reviewer 明确认可。
- 写法要克制：只写 reviewer ID 和被认可的具体点，例如 “Reviewer 2 also recognized the robustness of our metric, which supports that the evaluation design is practically meaningful.”
- 作用边界：跨 reviewer 引用只能辅助说明某个设计有外部认可，不能替代数据、实验或 case 证据。
- 风险控制：不要把一个 reviewer 的其他负面意见引入另一个 reviewer 的视野；不要制造 reviewer 之间对立；不要暗示某个 reviewer “错了”。
- 默认不用：如果没有明确积极 reviewer，或引用会让读者注意到更多问题，就不要跨 reviewer 引用。

## 回答写法

每个回答按证据强度组织：

1. **直接结论**：第一句回答问题，不绕。
2. **强证据**：数据、表格、补充实验、统计检验、case。
3. **机制解释**：为什么这个结果能回应 concern。
4. **修订承诺**：会在 revised paper 的哪个部分补充。
5. **引用**：必要时用 `[1]`，最后集中列 reference。

段落规则：

- 每段第一句先给结论，例如 “The gain mainly comes from the framework rather than the base LLM.”
- 后续句子再写数据、实验设置、case 或修订承诺。
- 如果补充新实验，先用一句短句交代 setting，再给结果；不要让 reviewer 猜实验条件。
- 一段只服务一个论点；如果有多个并列证据，再考虑分点。
- 一段中如果出现多个设置、多个指标或多个数值对比，优先改成小表格，而不是塞进长句。
- 不要用很多短 bullet 替代论证；bullet 只适合并列证据、步骤、维度或明确 checklist。
- 字数紧张时优先删铺垫、感谢重复句和低信息量形容词，保留数值、对比和结论。

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

小表格只能用于数据或天然结构化内容。不要直接用表格作为回复 reviewer 的主体结构；主体仍应是 `> **Qx: ...**` 后接文本回答。

表格规则：

- 控制在 2-5 列、2-6 行。
- 只展示能直接回答问题的指标。
- 如果一个段落里需要同时报告多个数据点、多个模型、多个 setting 或多个 metric，优先用小表格。
- 新增实验表格至少要包含 setting 或 notes，让读者知道比较条件；不要只放裸数值。
- 用 `**bold**` 标最好结果，不要塞大 leaderboard。
- 表格前后各用一句话解释，不要让表格自己说话。
- 表格适合展示新实验、ablation、metric 对比、评分维度、错误类型分布。
- 表格不适合展示空泛承诺、普通文字解释、reviewer 问题清单或为了“看起来充足”而造的信息量低的内容。

分点规则：

- 分点适合多个并列证据、多个质量控制步骤、多个实验设置或多个修订位置。
- 分点不适合把连续论证切碎；如果 2-3 句话能讲清楚，就用普通段落。
- 每个 bullet 必须有具体信息，最好包含设置、数值、机制或修订位置。

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
- reviewer 的弱点、concern 和非问句批评是否也被逐条转成 Q 并回答？
- 同一 reviewer 的不同维度问题是否避免了不必要合并？
- 问题间引用是否只用于减少重复，且没有替代当前 Q 的直接回答？
- 跨 reviewer 引用是否只在明确积极 reviewer 存在时使用，且没有引入额外负面信息？
- Q 摘要是否中性、可回答、不过度暴露缺点？
- 每个 response 第一段是否直接回答？
- 每段第一句话是否给出核心点？
- 新增实验是否简介了 setting，而不是只报数值？
- 是否至少用一个强证据回答核心 concern？
- 是否保持整体纯文本 Q&A，而不是把回复主体表格化？
- 一段中多个数据点是否已考虑改成小表格？
- 表格是否只用于数据或更适合结构化表达的内容？
- 分点是否只用于并列证据、步骤或维度，且每个 bullet 都有具体信息？
- 是否删除了冗余、空话和刻意堆信息量的内容？
- 引用是否真实、紧跟 claim、最后有 `References`？
- 最后一段是否礼貌请求更新评分并表示愿意继续沟通？
- 全文是否匿名、无外部链接、无身份线索？
