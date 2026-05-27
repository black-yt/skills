---
name: ai-conference-paper-writing
description: "当需要撰写、重构或审阅 AI conference paper 时使用，包括 NeurIPS/ICLR/ICML/ACL/CVPR 等会议论文的 research story、中心命题、teaser 图、Introduction、Related Work、Method pipeline、Experiments 图表布局、Analysis、Case Study、Abstract、Conclusion、贡献列表、术语体系、claim-evidence 对齐和可复现评测写法；重点是把工作从数据集/系统/方法对象包装成清晰的问题、能力缺口和论证闭环。"
---

# AI Conference Paper Writing

## 使用原则

- 把论文写成论证，不写成 README、实验报告或工程流水账。
- 先确定中心命题，再写章节和句子；不要先润色语言。
- 所有章节服务同一条主线：问题为什么重要、已有工作为什么没覆盖、本文如何系统补上、证据说明什么。
- 不编造实验结果、数据规模、引用或模型表现；缺数据时写成待填占位或建议补实验。
- 若用户要求最新相关工作、精确引用或 SOTA 对比，必须查原论文、官方页面或可信来源后再写。
- 默认帮助用户提高 AI 会议论文的可读性、可信度和可复述性，而不是单纯让句子更华丽。

## 写作顺序

优先按这个顺序推进：

1. 中心命题：一句话说明本文认为领域缺少什么关键能力/视角/资源，以及本文如何补上。
2. 核心挑战：提炼 3-4 个带限定词的能力关键词。
3. 贡献列表：3-5 点，使用并列结构。
4. 图表计划：teaser、method pipeline、组件/算法图、主表、消融表、分析图表、case 展示。
5. 方法结构：形式化输入输出、模块、约束、质量控制。
6. 实验表格：指标、模型、设置、主要发现。
7. Introduction：按六段结构写。
8. Abstract：最后压缩全文，且必须是一段。
9. Conclusion：回扣问题、方法、结果和未来方向，通常一段或两段。

如果用户直接要求改某一节，仍先快速判断该节是否服务中心命题；必要时先指出主线问题再改文。

## 论文类型路由

先判断论文类型，再选择叙事重心：

- **Benchmark/Data paper.** 主线是能力缺口和资源缺口；重点写任务定义、覆盖范围、数据质量控制、Related Work 数据集对比表、主表和模型失败分析。
- **Method paper.** 主线是假设和机制设计；重点写方法为何解决 challenge、强 baseline、公平设置、1-2 个必要消融和泛化分析。
- **System/Agent paper.** 主线是闭环能力；重点写模块协作、端到端 workflow、失败恢复、组件贡献和真实 case。
- **Training/Data-loop paper.** 主线是监督或反馈如何形成优化闭环；重点写数据/奖励来源、训练设置、超参数表、稳定性、泛化和 ablation。

不要把所有论文都写成 benchmark。论文类型决定 Related Work、Method、Experiment 和图表布局的重心。

## 中心命题

论文不能只是“我们做了一个东西”。先把对象提升成问题。

弱命题：

```text
We introduce a new benchmark.
```

强命题：

```text
Current models perform well on X, but still lack Y, a capability required for Z. We propose a framework that covers A, B, and C to systematically evaluate and improve Y.
```

通用模板：

```text
This paper argues that, to achieve [long-term goal], models must possess [core capability]. Existing work lacks a systematic characterization of this capability, so we introduce [method/data/system] to evaluate, diagnose, and improve it.
```

中文检查：

```text
本文认为：为了实现 [长期目标]，模型必须具备 [核心能力]；现有工作缺少对该能力的系统刻画，因此我们提出 [方法/数据/系统]。
```

如果这句话说不清，先不要细写 Abstract、Method 或 Experiments。

## Research Story 矩阵

写作前建立对应矩阵。每个核心问题至少要有方法、指标/实验和分析/case 支撑。

| 核心问题 | 方法设计 | 指标 | 实验发现 | Case / Analysis |
| --- | --- | --- | --- | --- |
| [Challenge 1] | [Module] | [Metric] | [Result] | [Failure mode] |
| [Challenge 2] | [Module] | [Metric] | [Result] | [Failure mode] |
| [Challenge 3] | [Module] | [Metric] | [Result] | [Failure mode] |

如果某个 challenge 只在 Introduction 出现，后文没有证据，删掉它或补实验证据。

## 图表叙事布局

AI 会议论文的图表要承担导航功能，不只是装饰。只要任务涉及完整论文结构、teaser、pipeline、Related Work 数据集表、实验图表、case study 或 appendix 展示，必须读取 `references/visual-experiment-layout.md`。

主文默认顺序：Abstract 前放 teaser 图；Method 开头放 pipeline 图，后半部分再放一个组件/算法图；Experiments 放主表、1-2 个消融表、2-3 个分析图表；Case Study 主文放 2 个压缩 case，完整 case 放 Appendix。Teaser 图必须同时呈现问题场景、输入输出、关键 challenge、本文方案和一句主要发现。

## Challenge 命名

Challenge 要写成研究问题，不写成工程需求。

例如不要只写 `The output must be JSON`；要上升为 `How can model outputs be represented so that long-horizon decisions, parameters, and dependencies can be systematically evaluated?`

关键词建议使用“限定词 + 能力名”：

- `Long-Horizon Planning under Constraints`
- `Structured State Tracking`
- `Grounded Decision Making`
- `Constraint-Aware Generation`
- `Programmatic Verification`
- `Scalable Supervision`
- `Real-World Protocol Alignment`
- `Compositional Generalization`
- `Optimizable Learning Loop`

每个关键词第一次出现时必须解释一句：

```text
First, **Structured State Tracking** asks whether models can preserve intermediate variables and dependency states across multi-step tasks, rather than solving each step in isolation.
```

Challenge 段最后加总括句：

```text
In short, achieving [goal] requires a pipeline that connects [challenge 1], [challenge 2], [challenge 3], and [challenge 4], rather than treating them as isolated subtasks.
```

## Introduction

默认使用六段结构。

第一段：大背景。先讲领域目标和现实意义，不要急着讲本文。

```text
Recent progress in X has enabled models to do A and B. However, achieving Y requires more than A and B: systems must also handle C, D, and E. This gap becomes especially critical in [scenario], where errors in [factor] can lead to [consequence]. Therefore, understanding and improving [core capability] is necessary for [long-term goal].
```

第二段：已有工作分类。不要罗列论文笔记，要按方向组织。

```text
Existing studies have made progress along three directions. First, ... Second, ... Third, ... However, these lines primarily focus on [existing focus], while leaving [our problem] underexplored.
```

第三段：研究挑战。必须具体到“能力 + 难点来源 + 任务关系”，不要只列抽象名词或应用需求。推荐写成一个总句、3-4 个并列 challenge、一个总括句：

```text
This gap raises three challenges. First, **[Term 1]**: models must [capability], because [specific difficulty source such as long context, parameter perturbation, state transition, visual grounding, or dependency propagation]. Second, **[Term 2]**: models must [capability], while avoiding [specific failure mode]. Third, **[Term 3]**: models must [capability], so that [evaluation/training/deployment consequence]. Together, these challenges require [integrated pipeline], rather than treating [subtasks] as isolated steps.
```

每个 challenge 都要满足四点：

- 术语有边界：用 `Long-Horizon Planning under Constraints` 这类限定词，不用泛泛的 `Reasoning`。
- 难点可定位：说明难在长上下文、状态依赖、参数扰动、模态对齐、输出结构化、错误传播或监督稀缺。
- 后文可映射：Method 中有对应模块，Experiments 中有对应指标，Analysis/Case 中有对应失败模式。
- 句法并列：`First/Second/Third` 的语法结构一致，顺序必须和下一段 `In this paper` 的方案顺序一致。

第四段：本文方法。用 `In this paper, we...` 开头，并逐点回应上一段 challenge。顺序必须对齐：

```text
For [challenge 1], we...
For [challenge 2], we...
For [challenge 3], we...
For [challenge 4], we...
```

第五段：实验发现。不要只报分数，要提炼现象和能力缺口。

```text
Results show that models can often solve local steps but fail to maintain global consistency, suggesting that current models still lack robust [core capability].
```

第六段：贡献列表。保持 3-5 点，每点以名词开头，避免实现细节。

```text
- **Task formulation.** We formalize...
- **Dataset.** We construct...
- **Evaluation.** We introduce...
- **Empirical findings.** We show...
- **Training and agent framework.** We provide...
```

## Related Work

Related Work 要和贡献对应，不要写与主线无关的名论文。

整体布局先按贡献和 challenge 分 3-4 个小节，不按“谁有名”或时间顺序堆文献。常见布局：

1. 最接近的任务、benchmark 或数据集：说明已有评测覆盖什么能力。
2. 相关模型、agent、reasoning 或 planning 方法：说明已有方法优化什么能力。
3. 评测、训练闭环、数据构造或 programmatic verification：说明已有技术如何提供监督和诊断。
4. 可选领域小节：只有当具体领域知识会影响本文任务定义时才保留。

每个小节两段最稳：

1. 领域进展：代表工作解决了什么。
2. 本文区别：这些工作服务于不同目标，因此没有覆盖本文目标。

小节第一段写“分类后的进展”，不要逐篇复述：

```text
Prior work on [area] can be grouped into [line 1], [line 2], and [line 3]. The first line focuses on..., the second line studies..., and the third line explores... Together, these works establish [shared progress].
```

小节第二段写“本文区别”，必须落到本文的一个 challenge 或 contribution：

```text
However, these works primarily assume [setting/format/scope], whereas our work focuses on [specific capability]. This distinction matters because [failure mode or missing evidence], which we evaluate through [metric/task/analysis].
```

避免直接说已有工作“不好”。更稳的写法：

```text
Existing benchmarks primarily evaluate static visual reasoning or short-form question answering, while our focus is on long-horizon decision making under structured constraints.
```

Related Work 的组织检查：

- 小节标题要和贡献对齐，例如 `Multimodal Benchmarks`、`Long-Horizon Planning Agents`、`Programmatic Evaluation`。
- 每个小节只说一个差异维度，不要所有小节都重复“没有研究我们的问题”。
- Introduction 第二段可以压缩 Related Work 的分类；Related Work 正文则展开证据和区别。
- 不要把实现细节写成相关工作差异；差异应是任务目标、评测对象、能力边界、数据分布或监督形式。

如果是 benchmark 或 data paper，Related Work 中最好加入数据集对比表。我们的数据集放最后一行；列名要和 Introduction 的 challenge 对齐，而不是只列规模。`Ours` 最好在 challenge 对应列上最完整。表后解释：哪些能力过去被分散覆盖，本文如何把它们放到同一个评测/训练框架里。完整模板见 `references/visual-experiment-layout.md`。

## Method

Method 第一节先给总框架，不要直接进入实现细节。总览要说明：

- 系统有几个模块。
- 每个模块解决哪个 challenge。
- 输入、输出和模块连接关系是什么。
- 是否需要用轻量公式形式化模型、benchmark、数据集、任务或指标的输入输出。
- 哪些约束防止错误或退化。
- 这些设计如何支撑中心命题。

方法小节按设计逻辑组织，不按开发顺序组织。

推荐顺序示例：Task Formulation -> Data Source Construction -> Instance Generation -> Difficulty Control -> Quality Validation -> Evaluation Protocol。

Method 开头应有 pipeline 图，标清输入、生成/推理/训练、验证、评测、反馈和输出闭环。Method 后半部分最好再加一张核心组件或算法图，例如 generator、state tracker、parser/evaluator、reward function、agent loop、training loop 或 dependency graph。Benchmark/data 工作还可以在 Method 中加入数据分布表，并解释分布如何支撑 challenge。完整图表模板见 `references/visual-experiment-layout.md`。

在合适位置加入形式化定义有助于读者理解。常见写法是先用一句话给直觉，再给 Markdown 可渲染的分行公式：

$$
\begin{aligned}
R, A &= \mathrm{Model}(Q),\\
R &= \text{reasoning process},\quad A=\text{final answer}.
\end{aligned}
$$

形式化定义应覆盖输入、输出、约束、标签或评测函数，尤其适用于 benchmark/data、agent/system、programmatic evaluation 和 training loop。公式要服务导航，不要引入后文不用的符号。

每个方法段落使用微结构：

```text
To address [problem], we construct [component]. Specifically, we [method]. To prevent [failure], we enforce [constraint]. This design ensures that [role in the overall task].
```

不要写成：

```text
We wrote a script. Then we tuned prompts. Then we fixed bugs.
```

要抽象成：

```text
We implement an automated construction pipeline that samples source records, generates candidate instances, validates format constraints, and applies quality filters.
```

## Data And Benchmark

数据或 benchmark 论文必须主动写质量控制。常见质量控制：

- automatic format checks
- syntax parsing
- deduplication
- leakage detection
- annotation consistency
- difficulty filtering
- model-based pilot testing
- human audit
- error feedback and repair
- version control

如果使用 LLM 生成数据，必须写验证流程：

```text
We constrain generation with [prompt/schema], reject candidates that fail [automatic checks], verify semantic consistency through [model/human review], and repair or discard instances according to [criteria].
```

难度不能只说 challenging，要说明难度来源：

- similar options
- long context
- multi-step dependencies
- parameter perturbation
- state transition
- locally correct but globally wrong solutions
- negative examples
- compositional generalization
- out-of-distribution settings

数据统计表后必须解释：

- 数据规模说明什么。
- 分布是否平衡。
- 覆盖多少类别。
- train/test 是否同分布。
- 是否去重和避免 leakage。
- 为什么这些统计支撑任务难度。

## Evaluation

指标要解释合理性，不只给公式或名称。每个指标回答：

- 衡量什么能力。
- 为什么适合任务。
- 惩罚什么错误。
- 不惩罚什么无关差异。
- 和已有指标有什么关系。

模板：

```text
Parameter accuracy evaluates whether the model preserves values that affect execution, rather than superficial text overlap.
```

模型评测设置要可复现，至少写：

- test set size
- model list
- prompt format
- output format requirement
- decoding settings
- token limits
- parsing rules
- invalid handling
- number of runs
- averaging/statistics
- whether retries or caches are used

如果模型可能输出无效答案，必须写 invalid：

- invalid 定义。
- invalid 是否算错。
- invalid 数量。
- 是否重试。
- 是否格式限制。
- 是否只解析最终答案或代码块。

## Experiments

实验小节不要只有表格。默认布局：Experimental Setup、Main Results 主表、1-2 个 Ablation 表、2-3 个 Analysis 图表、2 个压缩 Case。训练论文在实验设置或 Appendix 中加超参数表。主表要服务中心命题，不只是排行榜；消融表要与 Method 设计一一对应；Analysis 用 `\paragraph{Insight ...}` 直接给出 2-3 个核心 insight，不必为每个 insight 拆章节。完整实验图表模板见 `references/visual-experiment-layout.md`。

每个实验部分都采用两段式写作：第一段写结果，第二段写 insight。

现象段模板：

```text
As shown in Table X, model performance ranges from A to B. The strongest model achieves C, while smaller models remain below D. Notably, invalid outputs account for E, suggesting that...
```

Insight 段模板：

```text
This suggests that the bottleneck is not [easy factor], but [core capability]. Models can often do [local behavior], yet fail to [global behavior].
```

结果低也可以成为贡献，但要解释低分来源：

- 任务更长。
- 参数更密。
- 状态依赖更强。
- 输出空间更结构化。
- 错误传播更严重。

## Analysis And Case Study

Analysis 不重复结果，要解释错误类型。可按能力维度、错误类型、模型规模、任务阶段、输入模态或指标拆分。

每个分析点包含：

1. 现象。
2. 原因。
3. 例子。
4. Insight。

失败模式要命名，例如：

- parameter drift
- order inversion
- missing step
- redundant action
- dependency break
- modality shortcut
- default-value bias
- stage confusion

Case Study 要真实、完整、可验证：

- sample ID
- input summary
- task/question
- gold answer
- model output
- score
- error explanation

主文放 2 个压缩 case 最稳。优先做对照：一个模型对、一个模型错；一个格式合法、一个 invalid；一个保留参数、一个参数漂移。不要把完整长输出塞进主文；主文只展示能解释 insight 的关键片段。Appendix 可以展示完整 case，并可用 `tcolorbox` 支持跨页和紧凑展示；模板见 `references/visual-experiment-layout.md`。

## Abstract And Conclusion

Abstract 最后写，且必须是一整段，不要拆成多段或 bullet。一个稳妥顺序是：背景/缺口 -> 本文提出什么 -> 方法或资源范围 -> 关键实验发现 -> 贡献定位。

```text
[Background and gap]. To address this, we introduce [method/data/system], which [core design]. [Scope/scale if available]. Experiments on [setting] show that [main finding], revealing [capability gap or benefit]. These results suggest that [broader implication].
```

Abstract 不要塞过多实现细节，也不要引入后文没有支撑的术语。摘要里的每个术语都应该能在 Introduction、Method 和 Experiments 中找到对应内容。

Conclusion 可以是一段，也可以是两段。短会议论文通常一段即可；如果需要同时写 limitations/future work，可以用两段。Conclusion 只回扣已有主线：

- 重申问题。
- 重申方法。
- 重申结果。
- 说明未来工作。

一段式 Conclusion：

```text
We studied [problem] by introducing [method/data/system] for [core capability]. Experiments show [main finding], indicating [insight]. We hope this work supports future progress toward [long-term goal].
```

两段式 Conclusion：第一段总结问题、方法和结果；第二段写 limitations 或 future work。不要在 Conclusion 引入新概念、新实验或新贡献。

## 段落与语言

每段要有主题句和收束句。常见段落逻辑：背景 -> 缺口 -> 本文；目标 -> 方法 -> 约束 -> 效果；现象 -> 原因 -> 影响 -> insight；已有工作 -> 局限 -> 本文区别；定义 -> 例子 -> 重要性。

列表前要有总领句，列表后最好有总结句，bullet 语法结构保持并列。删除或改写空泛弱句，例如 `This is important`、`This is challenging`、`Existing methods are limited`、`Our method is effective`；必须说明重要在哪里、难点在哪里、已有工作缺口在哪里、效果体现在哪个指标或现象。

避免过度声称：少用 `solve`、`fully address`、`human-level`、`comprehensive in all aspects`；多用 `study`、`characterize`、`systematically evaluate`、`provide evidence`、`make a step toward`、`reveal limitations`。

## 术语与呼应

术语必须统一。为核心概念维护小表：

| 正式术语 | 中文含义 | 禁用别名 | 对应证据 |
| --- | --- | --- | --- |
| [Term] | [Meaning] | [Aliases] | [Metric/Section] |

好术语必须能映射到数据、方法、指标、实验或 case。无法映射的 fancy 术语要删掉。

同一个核心术语应在不同章节承担不同功能：

- Introduction：提出能力缺口。
- Method：对应设计。
- Experiments：对应指标和结果。
- Analysis：对应失败模式。
- Conclusion：回扣主线。

可以用 `grep` 检查术语出现次数：只出现 1-2 次通常没有真正成为主线；出现很多但没有新信息则是在堆词。

## 审阅与改稿检查

审阅论文草稿时按严重程度指出问题：

1. Story：中心命题是否清楚，工作是否从对象提升到问题。
2. Alignment：challenge、method、metric、experiment、case、conclusion 是否一一对应。
3. Evidence：每个 claim 是否有数据、实验、分析或 case 支撑。
4. Reproducibility：评测设置、数据构造、invalid、split、prompt、decoding 是否可复现。
5. Terminology：关键词是否统一、具体、有边界。
6. Formalization：输入、输出、数据实例、模型函数、指标或 benchmark 任务是否有必要的形式化定义，且符号后文确实使用。
7. Section Logic：每节是否服务主线，是否像 README 或实验流水账。
8. Paragraph Logic：段首主题句、段尾收束、列表并列和图表解读是否到位。
9. Language：最后再润色句子，不要先做表层 polish。

Reviewer-risk 快速检查：

- Novelty risk：是否只是组合已有任务、数据或模块。
- Validity risk：指标是否真的衡量 claim 中的能力。
- Baseline fairness risk：baseline、prompt、decoding、token limit、重试策略是否公平。
- Reproducibility risk：数据、代码、prompt、模型版本、超参数、解析规则是否足够复现。
- Overclaim risk：结论是否超过实验、case 或人工分析支持。

最终检查四轮：

- 结构检查：每章是否服务中心命题。
- 对应检查：challenge/method/experiment/conclusion 是否对齐。
- 术语检查：关键词是否统一，是否能映射到证据。
- 证据检查：每个 claim 是否有数据、实验或 case 支撑。

## 输出风格

当用户要求“帮我写”时，优先给可直接放进论文的英文正文；必要时先给一段中文结构说明。

当用户要求“帮我改”时，先指出结构性问题，再给改写版本。不要只做同义改写。

当用户要求“帮我审”时，先列主要风险和缺口，再给具体修改建议和示例句。

当信息不足时，使用明确占位符，例如 `[DATASET_SIZE]`、`[MODEL_NAME]`、`[METRIC]`，不要编造。
