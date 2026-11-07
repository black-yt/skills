---
name: rebuttal-writing
description: "当需要撰写、重构或压缩 AI/ML conference rebuttal、reviewer response、AC response 或给 AC 的私密审稿问题说明时使用；覆盖匿名性、开头感谢、陈述式 Q 标题、问题弱化改写、Markdown Q&A 格式、强证据回答、小表格、引用、限字符分块及独立子 agent 对抗评审。"
---

# Rebuttal Writing

## 使用场景

- 为 AI/ML conference 写 reviewer rebuttal、author response、discussion reply 或 AC summary。
- 当某个低分 reviewer 存在明显事实错误、可能偏见或严重误读时，起草给 AC 的私密说明。
- 把零散实验、case、修订承诺和 reviewer comment 整理成紧凑 Markdown。
- 在字数限制下，把尖锐问题转写成可回答、对作者有利但不歪曲原意的 `Q1/Q2/...`。
- 回答必须完全匿名，不能出现作者身份、外部链接、GitHub、主页、机构、项目私有路径或任何可反查身份的信息。

## 总体原则

- 先感谢，再回答；先承认 reviewer 的有效关注点，再给证据。
- 每个 reviewer-specific response 都必须以 `Dear Reviewer [ID],` 或 `Dear Reviewer,` 开始；不要省略称呼。
- 所有 `Q1/Q2/...` 标题都要写成中性陈述式主题，而不是复述 reviewer 的质问。
- 问题摘要要弱化尖锐措辞，但不能偷换问题或删掉核心 concern。
- reviewer 提到的弱点、concern 和 question 都要一对一回应；即使原文不是问句，也要转成正式的 `Q1/Q2/...` 来回答。
- 回答要具体，优先使用数据、补充实验、ablation、case study、统计检验、表格和真实引用。
- 新增实验不能只报数值；必须用一句话简介实验 setting，例如数据集/子集、模型或方法、指标、对照项和改变的变量。
- rebuttal 中的结论、数值、指标方向和术语必须与原论文一致；不要为了回应 reviewer 临时写出和正文相反的结论。
- 少写空泛套话，例如 “we will improve” 或 “this is interesting”；必须说清楚改什么、结果是什么、支持什么结论。
- rebuttal 通常有严格字数限制；每个回答先给核心结论，再给最强证据。
- 整体回复应该是高信息密度的纯文本 Q&A，不要把 reviewer response 整体改成表格。
- 给 AC 的私密说明要低姿态、证据化、克制；不要直接指责 reviewer，只说明可能存在的 factual misunderstanding、evaluation inconsistency 或 unsupported claim。
- 每个段落第一句话必须简短清楚地给出该段核心点，后文再展开证据或解释。
- 只有当内容天然适合结构化表达时才用分点或表格；不要为了显得充足而加入低信息量表格或空泛 bullet。
- 只承诺实际可以放进 revised version / appendix 的内容；不要编造实验、数据、引用或未来开源链接。

## 推荐结构

### Reviewer-specific response

```md
Dear Reviewer,

Thank you for your careful review and constructive comments. We are pleased that you recognized [认可点1] and [认可点2]. Regarding your remaining concerns about [主题A], [主题B], and [主题C], we respond below.

> **Q1: [中性陈述式主题].**

**Response.** [一句话直接回答核心疑问。]

[用一段高密度文本解释核心证据。段首第一句先给结论，随后展开实验、case 或修订位置。]

[只有在多个证据点天然并列时才用分点。]

- **Ablation.** [具体设置和数值变化。]
- **Case study.** [具体 failure mode 和改进。]

| Setting | Metric | Result |
| --- | --- | --- |
| [baseline] | [metric] | [value] |
| [ours] | [metric] | **[value]** |

> **Q2: [另一个中性陈述式主题].**

**Response.** [直接回答。] [如需引用，用 `[1]`。]

We hope these responses clarify your concerns. If they address your questions, we would be grateful if you could consider [updating / raising] your score. If any concern remains, we would be happy to continue the discussion.

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

### Private note to AC

```md
Dear Area Chair,

Thank you for coordinating the review process. We appreciate Reviewer [ID]'s time and feedback. However, we would like to respectfully note several points that may affect how this review should be weighed.

- **Factual mismatch.** Reviewer [ID] states that [claim], but the submitted paper explicitly includes [evidence] in [Section/Table/Figure/Appendix].
- **Evaluation inconsistency.** Reviewer [ID]'s concern about [topic] appears inconsistent with [paper evidence / other reviewer's explicit recognition / benchmark result].

We do not intend to dismiss the reviewer's feedback. We only hope these factual issues can be considered when assessing the review, because they may have contributed to an unusually low score or an inaccurate interpretation of the paper.
```

## 开头段写法

每个审稿人的回复都必须单独有开头段，不要多个 reviewer 合并后只写一次总称呼。开头段一般包含四件事：

- **称呼**：单个 reviewer 用 `Dear Reviewer [ID],` 或 `Dear Reviewer,`；全局/AC 汇总才用 `Dear Reviewers,` 或 `Dear Area Chair and Reviewers,`。
- **感谢**：感谢认真审阅和建设性意见。
- **正向锚点**：只点名该 reviewer 原文确实认可的地方，例如 writing quality、novel task、strong experiments、broad benchmark；不要把其他 reviewer 的肯定移植过来。
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

每个回复项用 Markdown blockquote；下面的 `Qx` 表示任意编号，实际写作时替换成 `Q1/Q2/...`：

```md
> **Qx: Ablation of the [module] module.**
```

改写规则：

- 每一个 Q 标题都遵守陈述式主题规则，不只是 `Q1`。
- 把 reviewer 的问题改写成陈述式主题、名词短语或短句，例如 “Ablation of the routing module”。
- 避免在 Q 标题里使用 `why`、`whether`、`missing`、`insufficient`、`questionable`、`fatal flaw`、`concern about`、`request for` 等会强化攻击感或缺陷感的词。
- 把 “fatal flaw / not novel / invalid / missing” 改成中性主题，例如 “Novelty relative to prior work” 或 “Ablation of [module]”。
- 把宽泛批评收窄成可回答的问题。
- 把攻击性表述转成中性学术表述。
- 保留 reviewer 的核心疑问，不要篡改为完全不同的问题。
- 如果 reviewer 问 “the paper does not compare the impact of [module]”，Q 标题写成 `> **Qx: Ablation of the [module] module.**`，不要写成 `> **Qx: Missing comparison of [module].**`。

示例：

| 原始尖锐问题 | 推荐 Q 标题 |
| --- | --- |
| The method is not novel. | `> **Qx: Novelty relative to prior work.**` |
| The benchmark may be biased because GPT-4o was used. | `> **Qx: Construction bias analysis for LLM-assisted data generation.**` |
| The experiments are insufficient. | `> **Qx: Additional evidence on experimental coverage.**` |
| The metric is questionable. | `> **Qx: Metric rationale and robustness.**` |
| The paper does not compare the impact of the XXX module. | `> **Qx: Ablation of the XXX module.**` |

## 问题覆盖与引用策略

覆盖规则：

- **弱点也算问题**：reviewer 写成 `Weaknesses`、`Concerns`、`Limitations` 或普通陈述时，也要逐条抽取成 `Q1/Q2/...`。
- **默认一对一**：每个 reviewer 的每个实质性弱点或疑问默认单独回答，不要只挑显式 question 回答。
- **谨慎合并**：只有两个点内容高度相似、证据完全相同或一个点明显是另一个点的子问题时，才合并成一个 Q。
- **合并要透明**：合并后在 Q 标题或首句说明覆盖两个 closely related points，避免 reviewer 觉得某个点被跳过。
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

## AC 私密信与审稿问题申诉

适用场景：

- reviewer 给分明显偏低，且意见中存在可证实的事实错误。
- reviewer 声称论文没有某个实验、模块、数据或讨论，但原文中明确写在某个 section、table、figure 或 appendix。
- reviewer 的主要批评和原文证据明显不一致，或和其他 reviewer 的明确正面认可形成强烈冲突。
- reviewer 的措辞显示可能没有认真阅读关键部分，但不要直接写 “the reviewer did not read the paper”。

写作姿态：

- 使用私密 AC 通道，不要把这类投诉写进公开 rebuttal。
- 开头仍然感谢 AC 和该 reviewer 的审稿投入。
- 用 “we respectfully note” / “may affect how this review should be weighed” / “possible factual misunderstanding” 这类低姿态表达。
- 目标是让 AC 在参考该 reviewer 意见时降低权重，而不是要求 AC 惩罚 reviewer 或直接删除该 review。
- 只陈述可验证事实：原文位置、表格编号、figure 编号、appendix 位置、明确数值和 reviewer 原话。
- 如果说 reviewer 可能有偏见，也要写成 “possible bias / unsupported assumption / evaluation inconsistency”，不要直接指责人格、动机或能力。

证据组织：

- 每个问题用一个短 bullet，先写 reviewer 的具体说法，再写原文证据。
- 原文证据必须具体到 `Section X`、`Table Y`、`Figure Z`、`Appendix A` 或 rebuttal 中已有补充实验。
- 如果 reviewer 说 “no XXX comparison”，证据应写 “Table X reports XXX ablation under [setting]”，不要只说 “we already included it”。
- 如果引用其他 reviewer 的正面意见，只写 reviewer ID 和对应认可点；不要把其他 reviewer 的负面意见带进来。
- 只列最强的 2-4 个问题；不要把所有不满都写成投诉。

推荐模板：

```md
Dear Area Chair,

Thank you for coordinating the review process. We appreciate Reviewer [ID]'s time and feedback. However, we would like to respectfully note several factual issues that may affect how this review should be weighed.

- **[Neutral issue label].** Reviewer [ID] states that [reviewer claim]. In the submitted paper, [Section/Table/Figure/Appendix] explicitly reports [paper evidence], including [specific result or statement].
- **[Neutral issue label].** Reviewer [ID] suggests [reviewer claim]. This appears inconsistent with [paper evidence / another reviewer ID's positive recognition], which shows [specific supported point].

We do not intend to dismiss the reviewer's feedback. We only hope these factual issues can be considered when assessing the review, because they may have contributed to an unusually low score or an inaccurate interpretation of the paper.
```

避免：

- “Reviewer [ID] is biased / unfair / incompetent.”
- “The review should be ignored.”
- “The reviewer clearly did not read the paper.”
- 没有原文位置或具体证据的主观抱怨。
- 把普通 disagreement、审美偏好或可接受的 critical opinion 写成投诉。

## 原文一致性与短板承认

一致性规则：

- 回复前先核对原论文中的 main claim、实验表格、figure、appendix、metric 定义和数值，不要凭记忆回答。
- rebuttal 中新增的数值必须和原文已有数值、指标方向、dataset split、setting 名称一致。
- 如果使用新实验，必须说明它是 `additional experiment`，并避免让它推翻正文的主实验叙述。
- 如果原文中的某个表述确实不够严谨，要把它包装成 “we will clarify / qualify the statement”，不要写成 “our conclusion was wrong”。
- 如果 reviewer 指出的是局部短板，可以诚恳承认范围、表达或补充实验不足；不要承认成原则性错误、方法无效或与原论文主结论相反。
- 如果某个结论有潜在不妥，先在保持原结论方向一致的前提下加限定词，例如 `in this setting`、`under the evaluated benchmark`、`for the tested model family`。
- 修订承诺应是补充说明、补充实验、补充限制讨论或更谨慎措辞，而不是重写核心贡献边界。

推荐表达：

```md
**Response.** Our conclusion remains consistent with the submitted paper: [core claim]. We agree that the current wording can better specify [scope/setting], and will revise it to emphasize that the conclusion holds under [bounded condition].
```

避免：

- “This contradicts our original conclusion.”
- “The main claim does not hold.”
- “The result in the paper is wrong.”
- 为了显得诚恳而主动扩大 reviewer 的 concern。

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
We hope these responses clarify your concerns. If they address your questions, we would be grateful if you could consider [updating / raising] your score. If any concern remains, we would be happy to continue the discussion. Thank you again for your time and feedback.
```

注意：

- 可以请求调整评分，但语气要克制。
- 如果 reviewer 原始分数还可以，用 `consider updating your score`。
- 如果 reviewer 原始分数较低，用 `consider raising your score` 或 `consider improving your score`。
- 不要施压、抱怨或暗示 reviewer 不公平。
- 不要泄露身份或附外部链接。

## 证据台账与对照归因

- **先分来源**：内部台账分别标注已投稿论文、正式运行记录、作者补充确认、代码默认值和历史诊断；每个关键结论关联位置、设置和可支持范围。内部台账不复制到对外回复。
- **论文优先但不掩盖冲突**：复述投稿设置以论文为主，代码用于解释实现；发现冲突要标明并核实，不能静默用默认值改写已报实验，也不能把论文声明当作运行日志已验证。
- **区分缺失与难找**：先核对正文和附录；已有信息礼貌给出准确位置并承诺突出，确实未记录的数值不能声称“附录已有”。总样本数不能推成每阶段样本数或偏好对数量。
- **把公平性写具体**：对核心消融逐项核对初始化、训练数据、交互结构、训练预算、loss 覆盖/系数、评测接口和辅助模块；只把已确认相同的条件写成相同。作者确认可作为确认事实，不能升级成独立运行审计。
- **最强控制先回答**：优先呈现只改变目标因素的已有比较；随后再报完整系统结果和辅助实验。不要用结构、监督或推理预算同时变化的总分差归因单个模块。
- **拆开训练量**：奖励数值、轮次 token-loss 系数、归一化、mask 范围和额外监督是不同设置；说明组件加入前后各行对应什么，不把后续配置倒套到早期消融。
- **拆开模型与系统**：分别报告核心策略、辅助选择/汇总模块和完整系统。生成式选择器可能改变答案；不能仅称格式整理，不能把它带来的总分提升全归因训练算法。
- **小样本保留分母**：由原始题数计算百分数和百分点，写明样本量、宏/微平均、条件比例和无条件比例；净收益增加不代表有害修改减少。
- **描述不等于因果**：初始答案或评测样本不同的反馈对比只能作描述；随机评测重复不是重复训练，训练曲线不是 held-out 敏感性，局部扰动不是全参数鲁棒性。
- **成本分母明确**：某阶段占流水线总时间的比例，不等于相对其余阶段的新增开销；注明绝对/相对时间、统计范围及是否包含训练，不能直接当作等算力对照。
- **相关工作比机制**：读原文后比较目标、约束、奖励项、训练流程和调度机制；一个公式项不代表整套方法。承认已有原则及缺少的直接比较，不把机制差异写成实证优越性。
- **诚实优先**：如证据只支持净改进或局部有效，收窄 claim；不能为维持原文口径掩盖下降、敏感性或未完成的对照。把“将修订”与“已修改稿件”分开。

## 按字符上限拆分正式回复

- **先确认计量单位**：会议总字数、单条评论字符数和用户指定限制是不同约束；不限总字数也可能需要分条。不要把某次任务的阈值固定成通用会议规则。
- **先定论证再切分**：按完整 concern 或证据单元划分 `Response (1/N)`、`Response (2/N)`；保持 Q 编号连续，不从表格、公式、引用条目或关键限定中间截断。
- **每块可读**：每块有称呼和编号，首块感谢并点出真实认可点，末块礼貌收尾；其余块直接进入主题，避免反复感谢。依赖前块时指向具体 Q/Part，同时保留当前问题的直接回答。
- **数实际提交文本**：把称呼、part 标题、空格、换行、Markdown 标记、表格和 References 都计入。按平台实际口径验证，未知时可同时记录 Unicode 字符、UTF-16 单元和 UTF-8 字节并留余量。
- **单块文件是提交单元**：另存每位 reviewer 的合并阅读版及计数清单；明确合并版可能超过单条限制，不应一次粘贴。参考文献与其调用放在同块，或明确跨块定位。
- **最终再数**：翻译、润色、补充证据、改编号或加结尾后重新计数；归档副本必须与最终正式块逐字一致。

## 独立子 agent 对抗评审

用户要求模拟审稿或确实需要独立评估，且 delegation 已获授权时使用；普通润色不强制启动。

1. **冻结输入**：为每轮保存完整投稿论文、原始审稿意见和当前正式回复的版本/哈希；评审期间不修改该轮快照。
2. **独立初始化**：每位 reviewer、每一轮都新建无历史继承的 agent，例如可用时设置 `fork_turns="none"`。只提供完整论文、该 reviewer 的原审稿和其本轮完整回复，不提供其他 verdict、优化历史或目标分数。
3. **保留真实判断**：要求逐项判断原 concern 是否解决，核对归因和证据边界，给出原会议量表下的评分、理由、残留阻塞点；不要求 agent 扮演“已被说服”的 reviewer。
4. **按证据优化**：主 agent 汇总重复阻塞点，优先找遗漏的已有控制、核实事实、缩小 claim 和改善组织。用户禁止新增实验时坚持该边界；未解决处如实承认。
5. **有变化才重评**：只有回复或证据发生实质变化才开启新轮；不能反复抽样同一稿直到偶然得到好分，也不能改变评分标准、引导目标或隐藏负面 verdict。
6. **留全记录**：保留所有轮次、输入哈希、agent 初始化方式和完整 verdict；中断/失败及替换原因也记录，未完成的 agent 不能算作通过。
7. **评最终原文**：翻译、分块或实质修改后，必须让新 agent 阅读实际最终英文稿及全部 parts；旧草稿通过不代表正式稿通过。通过后再实质改动，要重评或明确说明尚未重评。
8. **边界与停止**：目标分数由具体会议/用户决定，模拟不能保证真人涨分。若剩余问题需要禁止的实验或不可得事实，报告当前结果与原因，不伪造证据或承诺无限优化。

## 匿名性和安全检查

提交前逐项检查：

- 没有作者姓名、机构、邮箱、GitHub、个人主页、项目主页、匿名仓库链接。
- 没有本地路径、私有数据路径、内部服务器、真实 token、私有账号。
- 没有 “our released code at ...” 或 “we have open-sourced ...” 这类可反查线索。
- 没有引用未公开补充材料中的外部链接。
- 没有过度承诺无法在 revised version 中实现的实验。
- 没有攻击 reviewer 的语气。
- 如果给 AC 写私密信，没有直接指责 reviewer，只用事实证据说明 possible factual misunderstanding 或 evaluation inconsistency。

## 快速检查清单

- 第一段是否感谢 reviewer 并点出认可点？
- 每个 reviewer-specific response 是否都以 `Dear Reviewer [ID],` 或 `Dear Reviewer,` 开始？
- 每个问题是否用 `> **Qx: ...**`？
- Q 标题是否是中性陈述式主题，而不是疑问句或缺陷复述？
- reviewer 的弱点、concern 和非问句批评是否也被逐条转成 Q 并回答？
- 同一 reviewer 的不同维度问题是否避免了不必要合并？
- 问题间引用是否只用于减少重复，且没有替代当前 Q 的直接回答？
- 跨 reviewer 引用是否只在明确积极 reviewer 存在时使用，且没有引入额外负面信息？
- 如果需要给 AC 写私密信，是否只列出有原文证据支持的 2-4 个最强问题？
- AC 私密信是否保持低姿态，只请求 AC 考虑这些事实问题对 review 权重的影响？
- Q 标题和摘要是否中性、可回答、不过度暴露或强化缺点？
- 回复中的结论、数值、metric、setting 是否和原论文一致？
- 短板承认是否控制在范围、表达、补充实验或限制讨论层面，而不是推翻主结论？
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
- 最后一段是否根据原始分数选择了 `updating your score` 或 `raising/improving your score`，并表示愿意继续沟通？
- 限字符分块是否按实际最终文本重新计数，所有归档是否一致？
- 若做独立模拟，是否无历史继承、保留负面结果，并评审了实际最终正式稿？
- 全文是否匿名、无外部链接、无身份线索？
