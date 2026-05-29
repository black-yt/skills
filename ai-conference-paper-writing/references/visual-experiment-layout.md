# 图表与实验布局

当需要梳理完整 AI conference paper 大纲、决定主文图表位置、设计 Method/Experiment/Case Study 结构，或先用中文大纲规划论文时，使用这个 reference。

说明性文字默认用中文，便于快速沟通论文结构；只有图内英文文本、英文 caption、LaTeX/Markdown 模板等会直接进入英文论文或图表的内容保留英文。

## 技巧边界：中文版 Markdown 大纲 vs LaTeX 成稿

这个 reference 里有两类技巧，使用时不要混在一起。

- **中文版 Markdown 大纲技巧。** 用于讨论论文 story、章节顺序、图表位置和绘图需求。典型做法是：用中文写段落目的；用 `>` 引用块写图表说明和 caption；用普通 Markdown 表格承载数据；用占位符标记未知数值；为每张图写清楚 panel、箭头、图内英文文本和 caption。这一阶段的目标是让人可以准确画图和补表，不是生成最终 LaTeX。
- **LaTeX 成稿技巧。** 用于最终 `.tex` 论文排版和视觉强化。典型做法是：用 `xcolor` 给数值表上色；用 `\ScoreCell`、`\BestScore`、`\SecondScore` 标记结果；用 `\paragraph{Insight ...}` 写分析段首；用 `tcolorbox` 在 Appendix 展示完整 case。这些命令不应强加到中文 Markdown 大纲里，只在写 LaTeX 正文或附录时使用。

## 主文图表顺序

推荐主文顺序：

1. **Abstract 前的 teaser 图。** 通常放在 title/authors 之后、abstract 之前。一张图同时讲清任务场景、能力缺口、方法想法和关键发现。
2. **Method pipeline 图。** 放在 Method 开头。展示输入、模块、输出、验证/训练/评测闭环，以及每个模块对应哪个 challenge。
3. **Method 组件图或算法图。** 放在 Method 后半部分，解释一个具体技术核心，例如 data generator、parser/evaluator、reward function、state tracker、agent loop、dependency graph 或 training loop。
4. **主结果表。** 放在 Experiments 前部，直接回答论文最核心的 empirical question。
5. **消融表。** 使用 1-2 个表，每个表对应一个核心设计选择。
6. **分析图表。** 使用 2-3 个图表，对应 2-3 个 insight。不必为每个 insight 单独拆 subsection；中文大纲中写成 insight 小段，LaTeX 成稿时可用 `\paragraph{Insight ...}`。
7. **压缩 case study。** 主文放 2 个压缩 case；完整 case 放 Appendix。

## 写中文版 Markdown 大纲的技巧

规划完整论文时，可以先写中文 Markdown 大纲，并把每个图和表放在它最终应该出现的位置。这个大纲要让读者不需要猜 panel 结构、箭头、图内文字或 caption，就能准确画出图。

格式规则：

- 章节规划和段落意图用中文写。
- 图的说明和 caption 使用 Markdown 引用块 `>`，让它和正文明显区分。
- 每张图都要包含：详细自然语言绘图说明、图内英文文本、英文 caption，caption 使用 `Figure x. ...`。
- 每个表都在表格上方放一个引用块 caption，格式为 `Table x. ...`；表格数据本身使用普通 Markdown 表格，不放进引用块。
- Case 图不要尝试展示完整长 case。图中只放压缩文本：sample ID、input summary、gold answer、model output excerpt、score、failure mode、takeaway。完整 case 放 Appendix。
- 数字未知时使用 `[N]`、`[MODEL]`、`[SCORE]`、`[FAILURE_MODE]` 等占位符，不要编造。

推荐大纲骨架：

```markdown
# 中文论文大纲

## Title

英文题目：[Core Packaging Term]: [Subtitle]

## Teaser Figure

> **Figure 1 绘图说明。** 画一个三栏式 teaser。左栏是 Problem Setting，展示输入数据、任务目标和模型输出；中栏是 Challenge，使用三个并列小卡片展示核心挑战；右栏是 Our Framework 和 Key Finding，展示本文方法如何把任务构造、模型推理、程序化评测和错误反馈连接起来。用箭头从左到右连接，底部放一条 finding ribbon。
>
> **Figure 1 内部英文文本。**
> - Left title: "Problem: [Task Setting]"
> - Input box: "Input: [data / prompt / multimodal context]"
> - Output box: "Output: [answer / plan / report / action sequence]"
> - Challenge cards: "[Challenge 1]", "[Challenge 2]", "[Challenge 3]"
> - Framework title: "[Method/Benchmark Name]"
> - Module labels: "Instance Construction", "Model Inference", "Programmatic Evaluation", "Error Feedback"
> - Finding ribbon: "Current models solve local steps but fail at [core capability]."
>
> **Figure 1.** [Method/Benchmark Name] studies [core packaging term] by connecting [challenge 1], [challenge 2], and [challenge 3]. The framework exposes [main failure mode] and enables [evaluation/training loop].

## Abstract

一段式英文摘要。

## 1 Introduction

### 第一段：大背景

中文说明这一段要写什么。
```

通用图占位模板：

```markdown
> **Figure x 绘图说明。** [用中文详细描述布局、panel、视觉层级、箭头、必要颜色、每个区域放什么。描述必须具体到设计师可以直接复现这张图。]
>
> **Figure x 内部英文文本。**
> - Main title: "[Text]"
> - Panel (a): "[Panel title]" with labels "[label 1]", "[label 2]"
> - Panel (b): "[Panel title]" with arrows "[arrow text]"
> - Legend: "[legend item 1]", "[legend item 2]"
>
> **Figure x.** [English caption that states what the figure shows and how it supports the paper's main claim.]
```

通用表占位模板：

```markdown
> **Table x.** [English caption. State the comparison target, whether higher/lower is better, and why the table supports the claim.]

| Method / Dataset | [Challenge 1] | [Challenge 2] | [Challenge 3] | Metric |
| --- | --- | --- | --- | ---: |
| Prior A | partial | no | yes | [value] |
| Prior B | yes | partial | no | [value] |
| Ours | yes | yes | yes | [value] |
```

主文压缩 case 图模板：

```markdown
> **Figure x 绘图说明。** 画一个左右对照的压缩 case 图。左侧为成功 case，右侧为失败 case。每个 case 用 5 个短字段展示：Input Summary、Gold、Model Output Excerpt、Score、Diagnosis。底部用一条横向 takeaway 总结该 case 支持的 insight。完整输入、完整输出和评分细节不放在图里，留到 Appendix。
>
> **Figure x 内部英文文本。**
> - Left case title: "Case A: Correct Dependency Tracking"
> - Left fields: "ID: [sample_id]", "Input: [one-line input summary]", "Gold: [short gold answer]", "Output: [short correct excerpt]", "Score: [score]", "Diagnosis: preserves [key dependency]"
> - Right case title: "Case B: Parameter Drift"
> - Right fields: "ID: [sample_id]", "Input: [one-line input summary]", "Gold: [short gold answer]", "Output: [short wrong excerpt]", "Score: [score]", "Diagnosis: changes [parameter] and breaks [dependency]"
> - Bottom takeaway: "Failures arise from [failure mode], not from [less central factor]."
>
> **Figure x.** Two compressed cases illustrate how [method/benchmark] diagnoses [success behavior] and [failure mode]. Full cases are provided in Appendix [section].
```

## Teaser 图

Teaser 不能只是 workflow diagram。它至少要包含：

- 问题场景。
- 输入/输出例子。
- 关键 challenges。
- 本文方法、benchmark 或系统结构。
- 一个主要 empirical finding。

Caption 模板：

```text
Figure 1. [Paper Name] studies [core capability] by connecting [challenge 1], [challenge 2], and [challenge 3]. The benchmark/method exposes [main failure mode] and enables [evaluation/training loop].
```

## Related Work 数据集对比表

如果是 benchmark 或 data paper，Related Work 中最好加入数据集对比表。`Ours` 放最后一行。列名要对应 Introduction 中的 challenge，而不是随意列一些规模属性。

示例：

| Dataset | [Challenge 1 Attribute] | [Challenge 2 Attribute] | [Challenge 3 Attribute] | Programmatic Eval | Train Split |
| --- | --- | --- | --- | --- | --- |
| Prior A | partial | no | yes | no | no |
| Prior B | yes | partial | no | yes | no |
| Ours | yes | yes | yes | yes | yes |

这个表要证明论文的 gap claim。不要只因为 `Ours` 更大就显得更好；最好让 `Ours` 在 challenge 对应列上最完整。表后解释：哪些能力过去被分散覆盖，本文如何把它们统一到同一个评测、训练或诊断框架里。

## Method 图与数据分布

Method pipeline 图要标清：

- 输入数据或任务来源。
- instance/data generation。
- validation/filtering。
- model inference/training。
- programmatic evaluation 或 reward。
- analysis/error feedback。
- final output 或 learning loop。

Method 组件图应解释一个技术核心，不要重复 pipeline。适合单独画的对象包括 generator、state tracker、parser/evaluator、reward function、agent loop、training loop 或 dependency graph。

Benchmark/data 工作可以在 Method 中加入数据分布表：

| Split / Category | Count | Avg. Length | Difficulty | Key Attribute |
| --- | ---: | ---: | --- | --- |
| Train | [N] | [L] | [level] | [attribute] |
| Test | [N] | [L] | [level] | [attribute] |

表后要解释分布如何支撑 challenge，例如 long-range dependency、category coverage、parameter perturbation、negative examples 或 compositional generalization。

## 实验布局

推荐 Experiment 结构：

1. **Experimental Setup.** 写模型、数据、prompt、decoding、invalid handling、统计方式。训练论文加超参数表。
2. **Main Results.** 一个主表，回答中心 claim。
3. **Ablation Studies.** 1-2 个表，分别对应核心模块或设计选择。
4. **Analysis.** 2-3 个图表，每个图表产出一个 insight。
5. **Case Study.** 主文 2 个压缩 case；完整 case 放 Appendix。

训练超参数表：

| Hyperparameter | Value |
| --- | --- |
| learning rate | [value] |
| batch size | [value] |
| training steps / epochs | [value] |
| optimizer | [value] |
| temperature / decoding | [value] |

主表应包含主指标、关键子指标和 invalid/error rate。消融表要与 Method 对齐：移除 component A 应影响 challenge A；移除 validation/feedback 应影响 correctness 或 robustness。

Analysis 图表可以包括 error breakdown、performance by difficulty、scaling trend、metric correlation、invalid distribution、category distribution 或 human/model agreement。

每个实验部分采用两段式：

1. 结果段：描述数字和趋势。
2. Insight 段：解释结果为什么支持论文的核心能力 claim。

## Case Study 内容规划

主文 case study 应压缩。优先使用 2 个对照 case：

- correct vs. wrong。
- valid format vs. invalid format。
- parameter preserved vs. parameter drift。
- dependency maintained vs. dependency break。

每个 case 至少包含 sample ID、input summary、gold answer、model output excerpt、score 和 error explanation。主文只展示能支撑 insight 的关键片段；完整输入、完整输出和逐项评分放到 Appendix。

## LaTeX 成稿技巧

下面的内容用于最终 `.tex` 论文排版，不是中文版 Markdown 大纲的必需格式。

### LaTeX 表格配色

主结果表、消融表和分析表可以用颜色帮助读者扫描数值模式。颜色必须服务 claim，不应只是装饰。最好同时使用 bold 标记 best、underline 标记 second-best，保证灰度打印也能读。

常用 palette 和 packages：

```latex
\usepackage[table]{xcolor}
\usepackage{booktabs}
\usepackage{graphicx}

\definecolor{DeepPurple}{HTML}{5C3A96}
\definecolor{LighterGray}{HTML}{F7F7FA}
\definecolor{White}{HTML}{FFFFFF}
\definecolor{RcbRowShade}{HTML}{F7F7FA}
\definecolor{RcbAppendixRowShade}{HTML}{EFEFEF}
\definecolor{RcbHighlightPurple}{RGB}{236,229,250}
\definecolor{rcbScorePurple}{HTML}{5C3A96}
```

Score heatmap macros。第一个参数是颜色强度，通常是 0-100 的归一化整数；第二个参数是展示值。

```latex
\newcommand{\ScoreCell}[2]{\cellcolor{rcbScorePurple!#1!white}#2}
\newcommand{\BestScore}[2]{\ScoreCell{#1}{\textbf{#2}}}
\newcommand{\SecondScore}[2]{\ScoreCell{#1}{\underline{#2}}}
\newcommand{\DimCell}[2]{\cellcolor{rcbScorePurple!#1!white}#2}
```

可选模型或系统图标。只有 logo 文件确实存在且图标能提升可读性时才用；否则保持纯文本模型名。如果论文不是 RCB 风格资源，重命名项目 prefix。

```latex
\newcommand{\RcbIcon}[1]{\raisebox{-0.12em}{\includegraphics[height=0.9em]{imgs/logos/#1.png}}\hspace{0.25em}}
\newcommand{\ClaudeIcon}{\RcbIcon{anthropic}}
\newcommand{\OpenAIIcon}{\RcbIcon{openai}}
\newcommand{\ArisIcon}{\RcbIcon{asx}}
\newcommand{\OpenClawIcon}{\RcbIcon{openclaw}}
\newcommand{\NanobotIcon}{\RcbIcon{nanobot}}
\newcommand{\EvoIcon}{\RcbIcon{evo}}
\newcommand{\ResearchClawIcon}{\RcbIcon{researchclaw}}
\newcommand{\GlmIcon}{\RcbIcon{glm}}
\newcommand{\GeminiIcon}{\RcbIcon{gemini}}
\newcommand{\DeepSeekIcon}{\RcbIcon{deepseek}}
\newcommand{\GrokIcon}{\RcbIcon{grok}}
\newcommand{\KimiIcon}{\RcbIcon{kimi}}
\newcommand{\MimoIcon}{\RcbIcon{mimo}}
\newcommand{\QwenIcon}{\RcbIcon{qwen}}
```

紧凑彩色主结果表骨架：

```latex
\begin{table}[t]
\centering
\caption{\textbf{Main results on [Benchmark].} Higher is better.}
\label{tab:main-results}
\begingroup
\scriptsize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.08}
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}lcccc@{}}
\toprule
System & Overall & Dimension 1 & Dimension 2 & Dimension 3 \\
\midrule
\multicolumn{5}{l}{\textbf{Autonomous agents}} \\
\ClaudeIcon System A & \BestScore{82}{82.1} & \ScoreCell{70}{70.4} & \SecondScore{76}{75.8} & \ScoreCell{68}{67.9} \\
\OpenAIIcon System B & \SecondScore{79}{78.6} & \BestScore{83}{83.2} & \ScoreCell{60}{60.1} & \BestScore{80}{80.0} \\
\midrule
\multicolumn{5}{l}{\textbf{LLMs}} \\
\QwenIcon Model C & \ScoreCell{72}{72.3} & \SecondScore{79}{79.1} & \BestScore{84}{84.0} & \SecondScore{77}{77.2} \\
\bottomrule
\end{tabular}%
}
\endgroup
\end{table}
```

实用规则：

- 同一个表内保持颜色强度尺度一致。如果分数是 0-100，分数本身通常可以直接作为强度；否则先归一化。
- 不要把每个 cell 都染得过重。表格太花时，只给关键指标列上色，或者降低强度。
- `\rowcolor{RcbRowShade}` 只少量用于分组行或隔行，不要和 score heatmap 冲突。
- Caption 中说明 higher/lower is better，以及分数范围含义。
- 如果使用 icon，确保路径有效，PDF build 能找到 `imgs/logos/*.png`。

### LaTeX 段首 insight

```latex
\paragraph{Insight 1: Models fail primarily through dependency breaks rather than local perception errors.}
As shown in Figure X, ...
This suggests that ...
```

### LaTeX Appendix tcolorbox

Appendix 可以展示完整 case。紧凑 `tcolorbox` 模板：

```latex
\begin{tcolorbox}[
    breakable,
    enhanced,
    fontupper=\small,
    title={(a) Physics\_003},
    colback=LighterGray,
    colframe=DeepPurple,
    colbacktitle=DeepPurple,
    coltitle=White
]
\textbf{Input.} ...

\textbf{Gold.} ...

\textbf{Model Output.} ...

\textbf{Error Analysis.} ...
\end{tcolorbox}
```

LaTeX preamble 中要提前准备颜色和 packages。不要让样式损害可读性。Appendix 的完整 case 必须支撑主文中的 failure mode、metric 或 insight。
