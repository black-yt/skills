---
name: ai-conference-paper-writing
description: "当需要撰写、重构或审阅 AI conference paper 时使用，包括 NeurIPS/ICLR/ICML/ACL/CVPR 等会议论文的 research story、中心命题、teaser 图、Introduction、Related Work、Method pipeline、Experiments 图表布局、Analysis、Case Study、Abstract、Conclusion、贡献列表、术语体系、claim-evidence 对齐和可复现评测写法；重点是把工作从数据集/系统/方法对象包装成清晰的问题、能力缺口和论证闭环。"
---

# AI Conference Paper Writing

## 使用原则

- 把论文写成论证，不写成 README、实验报告或工程流水账。
- 先确定中心命题、核心包装关键词和 challenge 词，再写章节和句子；不要先润色语言。
- 所有章节服务同一条主线：问题为什么重要、已有工作为什么没覆盖、本文如何系统补上、证据说明什么。
- 不编造实验结果、数据规模、引用或模型表现；缺数据时写成待填占位或建议补实验。
- 若用户要求最新相关工作、精确引用或 SOTA 对比，必须查原论文、官方页面或可信来源后再写。
- 默认帮助用户提高 AI 会议论文的可读性、可信度和可复述性，而不是单纯让句子更华丽。

具体可复制的 Markdown 与 LaTeX 图表/公式/表格/case 模板放在 `references/markdown-latex-templates.md`。当任务涉及中文 Markdown 大纲、GitHub Markdown 公式、teaser/pipeline/case 图说明、Related Work 对比表、LaTeX 表格配色、`\cmark/\pmark/\xmark`、`\paragraph{Insight ...}`、摘要资源链接图标、紧凑贡献列表或 Appendix `tcolorbox` 时，必须读取该 reference。

## 工作顺序

优先按这个顺序推进：

1. **中心命题。** 一句话说明领域缺少什么关键能力/视角/资源，以及本文如何补上。
2. **核心包装关键词。** 为题目确定 2-3 词的高层新组合词，例如 `Protocol-Conditioned Action Prediction`。
3. **核心挑战。** 提炼 3-4 个学术化、带限定词、能映射到方法和实验的 challenge 词。
4. **贡献列表。** 3-5 点，名词开头，语法并列，避免实现细节。
5. **图表计划。** Teaser、Method pipeline、组件/算法图、主表、消融表、分析图表、case 展示。
6. **方法结构。** 形式化输入输出、模块、约束、质量控制和评测协议。
7. **实验结构。** 指标、模型、设置、主结果、消融、分析、case 和可复现细节。
8. **Introduction。** 按六段结构写。
9. **Abstract。** 最后写，必须是一段。
10. **Conclusion。** 回扣问题、方法、结果和未来方向，一段或两段。

如果用户直接要求改某一节，仍先快速判断该节是否服务中心命题；必要时先指出主线问题再改文。

## 论文类型路由

- **Benchmark/Data paper.** 主线是能力缺口和资源缺口；重点写任务定义、覆盖范围、数据质量控制、Related Work 数据集对比表、主表和模型失败分析。
- **Method paper.** 主线是假设和机制设计；重点写方法为何解决 challenge、强 baseline、公平设置、1-2 个必要消融和泛化分析。
- **System/Agent paper.** 主线是闭环能力；重点写模块协作、端到端 workflow、失败恢复、组件贡献和真实 case。
- **Training/Data-loop paper.** 主线是监督或反馈如何形成优化闭环；重点写数据/奖励来源、训练设置、超参数表、稳定性、泛化和 ablation。

不要把所有论文都写成 benchmark。论文类型决定 Related Work、Method、Experiment 和图表布局的重心。

## 中心命题与包装词

论文不能只是“我们做了一个东西”，必须把对象提升成问题。

- 弱命题：`We introduce a new benchmark.`
- 强命题：`Current models perform well on X, but still lack Y, a capability required for Z. We propose a framework that covers A, B, and C to systematically evaluate and improve Y.`

中心命题检查句：

```text
本文认为：为了实现 [长期目标]，模型必须具备 [核心能力]；现有工作缺少对该能力的系统刻画，因此我们提出 [方法/数据/系统]。
```

如果这句话说不清，先不要细写 Abstract、Method 或 Experiments；先把论文对象重新提升成问题。

核心包装关键词应满足：

- 由 2-3 个词组成，理解顺畅但有新鲜感；例如 `Protocol-Conditioned Action Prediction`，既有 next-token prediction 的影子，又定义了新的任务视角。
- 出现在 title，并在 Abstract、Introduction、Method 形式化定义、Experiments/Analysis、Conclusion 中适度点名。
- 如果是新造术语，至少在论文中两处出现并前后呼应；只出现一次的包装词要删掉、改名或补足后文设计。
- 每次出现应承担不同功能：Intro 提出能力缺口，Method 对应设计，Experiment 对应指标，Analysis 对应失败模式，Conclusion 回扣主线。

写作前建立 story 矩阵。每个核心问题至少要有方法、指标/实验和 analysis/case 支撑。模板见 `references/markdown-latex-templates.md`。
如果某个 challenge 只在 Introduction 出现，后文没有证据，删掉它或补实验证据。

## Challenge 命名

Challenge 要写成研究问题，不写成工程需求。不要只写 `The output must be JSON`；要上升为 `How can model outputs be represented so that long-horizon decisions, parameters, and dependencies can be systematically evaluated?`

Challenge 词建议使用“限定词 + 能力名”，并服务题目中的核心包装关键词，例如：

- `Long-Horizon Planning under Constraints`
- `Structured State Tracking`
- `Grounded Decision Making`
- `Constraint-Aware Generation`
- `Programmatic Verification`
- `Scalable Supervision`
- `Real-World Protocol Alignment`
- `Compositional Generalization`
- `Optimizable Learning Loop`
- `Protocol-Grounded State Tracking`
- `Constraint-Aware Action Selection`
- `Evidence-Calibrated Verification`

每个 challenge 第一次出现时解释一句：能力是什么、为什么难、和任务有什么关系。Challenge 段最后要有总括句：`[core packaging term] requires a pipeline that connects [challenge 1], [challenge 2], ... rather than treating them as isolated subtasks.`

Challenge 词也可以包装，但必须学术化、high-level，并能映射到后文证据。避免 low-level 词，如 `JSON Output`、`Image Upload`、`Prompt Format`。

每个 challenge 都要满足：

- 术语有边界：用限定词，不用泛泛的 `Reasoning`。
- 难点可定位：长上下文、状态依赖、参数扰动、模态对齐、输出结构化、错误传播或监督稀缺。
- 后文可映射：Method 中有对应模块，Experiments 中有对应指标，Analysis/Case 中有对应失败模式。
- 句法并列：`First/Second/Third` 的结构一致，顺序和下一段方案顺序一致。

## 图表与模板

AI 会议论文的图表承担导航功能，不只是装饰。主文默认顺序：

1. Abstract 前放 teaser 图。
2. Method 开头放 pipeline 图。
3. Method 后半部分放组件/算法图。
4. Experiments 前部放主结果表。
5. 放 1-2 个消融表。
6. 放 2-3 个分析图表，对应 2-3 个 insight。
7. Case Study 主文放 2 个压缩 case，完整 case 放 Appendix。

Teaser 图必须同时呈现问题场景、输入输出、关键 challenge、本文方案和一句主要发现。

当用户需要先梳理论文结构时，可以先写中文 Markdown 大纲，并把所有图和表放在它们最终应出现的位置。这里要区分两类技巧：

- **Markdown 大纲技巧。** 用于规划结构、给出可画图说明、普通 Markdown 表格、GitHub fenced math block。图表说明用 `>` 引用块；图必须包含详细绘图说明、图内英文文本和 `Figure x. caption`；表格 caption 用 `>`，数据表用普通 Markdown 表格。
- **LaTeX 成稿技巧。** 用于最终 `.tex` 排版，例如表格配色、`\cmark/\pmark/\xmark`、`\paragraph{Insight ...}` 和 Appendix `tcolorbox`。

具体代码模板见 `references/markdown-latex-templates.md`。

## Introduction

默认使用六段结构：

1. **大背景。** 先讲领域目标、现实意义、当前能力不足和你要研究的核心能力，不要急着讲本文。
2. **已有工作分类。** 按方向组织已有进展，先肯定，再指出没有覆盖本文目标。
3. **研究挑战。** 写成总句、3-4 个并列 challenge、总括句。每个 challenge 具体到“能力 + 难点来源 + 任务关系”。
4. **本文方法。** 用 `In this paper, we...` 开头，并按 challenge 顺序逐点回应。
5. **实验发现。** 不只报分数，要提炼现象和能力缺口。
6. **贡献列表。** 3-5 点，每点以名词开头，避免实现细节。

Introduction 第二段不要罗列论文笔记，要写成分类；第三段不要只列抽象名词或应用需求；第四段顺序必须和 challenge 段一致；第五段要说明结果揭示了什么能力瓶颈。

Introduction 最后一段的贡献列表仍保持 3-5 点、名词开头、语法并列。篇幅很紧时，LaTeX 成稿可以用 `paralist` 的 `compactitem` 写紧凑贡献列表；模板见 `references/markdown-latex-templates.md`。

## Related Work

Related Work 要和贡献对应，不要写与主线无关的名论文。整体先按贡献和 challenge 分 3-4 个小节，而不是按时间或名气堆文献。

常见布局：

1. 最接近的任务、benchmark 或数据集：说明已有评测覆盖什么能力。
2. 相关模型、agent、reasoning 或 planning 方法：说明已有方法优化什么能力。
3. 评测、训练闭环、数据构造或 programmatic verification：说明已有技术如何提供监督和诊断。
4. 可选领域小节：只有当具体领域知识会影响本文任务定义时才保留。

每个小节两段最稳：

1. 领域进展：代表工作解决了什么。
2. 本文区别：这些工作服务于不同目标，因此没有覆盖本文目标。

写法要求：

- 避免直接说已有工作“不好”；写成“已有工作服务于不同目标，因此没有覆盖我们的目标”。
- 小节标题和贡献对齐，例如 `Multimodal Benchmarks`、`Long-Horizon Planning Agents`、`Programmatic Evaluation`。
- 每个小节只说一个差异维度，不要反复说“没有研究我们的问题”。
- Introduction 第二段可以压缩 Related Work 的分类；Related Work 正文则展开证据和区别。
- 差异应是任务目标、评测对象、能力边界、数据分布或监督形式，不是实现细节。

Benchmark/data paper 应加入数据集对比表。`Ours` 放最后一行；列名要和 Introduction 的 challenge 对齐，而不是只列规模。这个表要证明论文的 gap claim：不要只因为 `Ours` 更大就显得更好，最好让 `Ours` 在 challenge 对应列上最完整。对于 yes/no/partial 属性列，LaTeX 成稿可用 `\cmark/\pmark/\xmark`，并在 caption 或表下注明符号含义。表后解释哪些能力过去被分散覆盖，本文如何把它们放到同一个评测、训练或诊断框架里。模板见 `references/markdown-latex-templates.md`。

## Method

Method 第一节先给总框架，不要直接进入实现细节。总览要说明：

- 系统有几个模块。
- 每个模块解决哪个 challenge。
- 输入、输出和模块连接关系是什么。
- 是否需要用轻量公式形式化模型、benchmark、数据集、任务或指标的输入输出。
- 哪些约束防止错误或退化。
- 这些设计如何支撑中心命题。

方法小节按设计逻辑组织，不按开发顺序组织。推荐顺序：Task Formulation -> Data Source Construction -> Instance Generation -> Difficulty Control -> Quality Validation -> Evaluation Protocol。

Method 开头应有 pipeline 图，标清输入数据或任务来源、instance/data generation、validation/filtering、model inference/training、programmatic evaluation 或 reward、analysis/error feedback、final output 或 learning loop。Method 后半部分最好再加一张核心组件或算法图，例如 generator、state tracker、parser/evaluator、reward function、agent loop、training loop 或 dependency graph；组件图应解释一个技术核心，不要重复 pipeline。

形式化定义有助于读者理解，尤其适用于 benchmark/data、agent/system、programmatic evaluation 和 training loop。公式应覆盖输入、输出、约束、标签或评测函数；符号必须后文使用，不能为形式化而形式化。Markdown 和 LaTeX 公式模板见 reference。

每个方法段落使用“目的 -> 做法 -> 约束 -> 作用”的微结构。不要写开发流水账，要抽象成方法设计。

## Data And Benchmark

数据或 benchmark 论文必须主动写质量控制。常见质量控制包括：

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

如果使用 LLM 生成数据，必须写验证流程：prompt/schema 约束、automatic checks、model/human review、repair/discard criteria。

难度不能只说 `challenging`，要说明难度来源：

- similar options
- long context
- multi-step dependencies
- parameter perturbation
- state transition
- locally correct but globally wrong solutions
- negative examples
- compositional generalization
- out-of-distribution settings

数据统计表后必须解释数据规模、分布平衡、类别覆盖、train/test 关系、去重和 leakage，以及这些统计如何支撑任务难度。
Benchmark/data 工作可以在 Method 或 Data section 中加入数据分布表，表后明确分布如何支撑 challenge，例如 long-range dependency、category coverage、parameter perturbation、negative examples 或 compositional generalization。

## Evaluation

指标要解释合理性，不只给公式或名称。每个指标回答：

- 衡量什么能力。
- 为什么适合任务。
- 惩罚什么错误。
- 不惩罚什么无关差异。
- 和已有指标有什么关系。

模型评测设置要可复现，至少写：test set size、model list、prompt format、output format requirement、decoding settings、token limits、parsing rules、invalid handling、number of runs、averaging/statistics、whether retries or caches are used。

如果模型可能输出无效答案，必须写 invalid：定义、是否算错、数量、是否重试、格式限制、是否只解析最终答案或代码块。

## Experiments

实验小节不要只有表格。默认布局：

1. Experimental Setup：模型、数据、prompt、decoding、invalid handling、统计方式；训练论文加超参数表。
2. Main Results：一个主表，服务中心命题，不只是排行榜。
3. Ablation Studies：1-2 个表，和 Method 设计一一对应。
4. Analysis：2-3 个图表，对应 2-3 个 insight。
5. Case Study：主文 2 个压缩 case，完整 case 放 Appendix。

主表应包含主指标、关键子指标和 invalid/error rate。消融表要与 Method 对齐：移除 component A 应影响 challenge A；移除 validation/feedback 应影响 correctness 或 robustness。

Analysis 图表可以包括 error breakdown、performance by difficulty、scaling trend、metric correlation、invalid distribution、category distribution 或 human/model agreement。

每个实验部分采用两段式：

1. 结果段：描述数字和趋势。
2. Insight 段：解释结果为什么支持核心能力 claim。

结果低也可以成为贡献，但要解释低分来自任务更长、参数更密、状态依赖更强、输出空间更结构化或错误传播更严重。

## Analysis And Case Study

Analysis 不重复结果，要解释错误类型。可按能力维度、错误类型、模型规模、任务阶段、输入模态或指标拆分。每个分析点包含现象、原因、例子和 insight。

失败模式要命名，例如：

- parameter drift
- order inversion
- missing step
- redundant action
- dependency break
- modality shortcut
- default-value bias
- stage confusion

Case Study 要真实、完整、可验证，至少包含 sample ID、input summary、task/question、gold answer、model output、score、error explanation。主文放 2 个压缩 case 最稳，优先做对照：correct vs. wrong、valid format vs. invalid format、parameter preserved vs. parameter drift、dependency maintained vs. dependency break。不要把完整长输出塞进主文；完整 case 放 Appendix。Appendix 的 `tcolorbox` 可以结构化展示 meta info、task、data、rubrics、generated report、figures 和 score items，模板见 `references/markdown-latex-templates.md`。

Appendix 可以长一些，目标是可复现和可审计，不是继续压缩主文。常见顺序是先放训练、实验 setting、超参数、prompt、解析规则等表格；随后放补充实验结果、额外 ablation 或 error breakdown；最后放完整 case study 记录。这里的 log 指完整 case study 展示，不是训练日志。Appendix 的 case 不要只放截取版，必须展示完整输入、完整输出、完整评分和完整评审记录；如果太长，拆成多个 box、多个 subsection 或 continuation pages。

## Abstract And Conclusion

Abstract 最后写，且必须是一整段，不要拆成多段或 bullet。稳妥顺序：背景/缺口 -> 本文提出什么 -> 方法或资源范围 -> 关键实验发现 -> 贡献定位。摘要里的每个术语都应该能在 Introduction、Method 和 Experiments 中找到对应内容。

如果论文有公开 homepage/code/data，可以在摘要文字后加入简短资源链接块，并用 Page / GitHub / Hugging Face 图标提高可扫读性。正文 abstract 仍保持一段式；资源链接块只作为附加入口，模板和内置 PDF logo 见 `references/markdown-latex-templates.md`。

Conclusion 可以一段，也可以两段。短会议论文通常一段；如果需要同时写 limitations/future work，可以两段。Conclusion 只回扣已有主线：重申问题、方法、结果和未来方向。不要在 Conclusion 引入新概念、新实验或新贡献。

## 段落、语言与术语

每段要有主题句和收束句。常见段落逻辑：

- 背景 -> 缺口 -> 本文
- 目标 -> 方法 -> 约束 -> 效果
- 现象 -> 原因 -> 影响 -> insight
- 已有工作 -> 局限 -> 本文区别
- 定义 -> 例子 -> 重要性

列表前要有总领句，列表后最好有总结句，bullet 语法结构保持并列。删除或改写空泛弱句，例如 `This is important`、`This is challenging`、`Existing methods are limited`、`Our method is effective`；必须说明重要在哪里、难点在哪里、已有工作缺口在哪里、效果体现在哪个指标或现象。

避免过度声称：少用 `solve`、`fully address`、`human-level`、`comprehensive in all aspects`；多用 `study`、`characterize`、`systematically evaluate`、`provide evidence`、`make a step toward`、`reveal limitations`。

术语必须统一。好术语必须能映射到数据、方法、指标、实验或 case。无法映射的 fancy 术语要删掉。可以用 `grep` 检查核心术语出现次数：只出现 1-2 次通常没有成为主线；出现很多但没有新信息则是在堆词。

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

最终四轮检查：结构检查、对应检查、术语检查、证据检查。

## 输出风格

- 用户要求“帮我写”：优先给可直接放进论文的英文正文；必要时先给中文结构说明。
- 用户要求“帮我改”：先指出结构性问题，再给改写版本；不要只做同义改写。
- 用户要求“帮我审”：先列主要风险和缺口，再给具体修改建议和示例句。
- 信息不足时，使用明确占位符，例如 `[DATASET_SIZE]`、`[MODEL_NAME]`、`[METRIC]`，不要编造。
