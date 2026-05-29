# Markdown 与 LaTeX 模板

这个文件只放 AI conference paper 写作中可直接复制和改写的 Markdown / LaTeX 代码模板。规则性判断放在 `../SKILL.md`。

说明性文字默认用中文，便于快速沟通论文结构；只有图内英文文本、英文 caption、LaTeX/Markdown 模板等会直接进入英文论文或图表的内容保留英文。

## 目录

- [Markdown 中会用到的](#markdown-中会用到的)
- [LaTeX 中会用到的](#latex-中会用到的)

## Markdown 中会用到的

这部分用于讨论论文 story、章节顺序、图表位置、绘图需求和 GitHub Markdown 公式展示。典型做法是：用中文写段落目的；用 `>` 引用块写图表说明和 caption；用普通 Markdown 表格承载数据；用 fenced math block 写公式；用占位符标记未知数值；为每张图写清楚 panel、箭头、图内英文文本和 caption。这一阶段的目标是让人可以准确画图、补表和预览公式，不是生成最终 LaTeX。

未知数字、模型名、指标或失败类型使用 `[N]`、`[MODEL]`、`[SCORE]`、`[FAILURE_MODE]` 等占位符，不要编造。

### Research Story 矩阵

```markdown
| 核心问题 | 方法设计 | 指标 | 实验发现 | Case / Analysis |
| --- | --- | --- | --- | --- |
| [Challenge 1] | [Module] | [Metric] | [Result] | [Failure mode] |
| [Challenge 2] | [Module] | [Metric] | [Result] | [Failure mode] |
| [Challenge 3] | [Module] | [Metric] | [Result] | [Failure mode] |
```

如果某个 challenge 只在 Introduction 出现，后文没有证据，删掉它或补实验证据。

### 中心命题模板

```text
This paper argues that, to achieve [long-term goal], models must possess [core capability]. Existing work lacks a systematic characterization of this capability, so we introduce [method/data/system] to evaluate, diagnose, and improve it.
```

```text
本文认为：为了实现 [长期目标]，模型必须具备 [核心能力]；现有工作缺少对该能力的系统刻画，因此我们提出 [方法/数据/系统]。
```

### 中文论文大纲骨架

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

### 通用图占位模板

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

### 通用表占位模板

```markdown
> **Table x.** [English caption. State the comparison target, whether higher/lower is better, and why the table supports the claim.]

| Method / Dataset | [Challenge 1] | [Challenge 2] | [Challenge 3] | Metric |
| --- | --- | --- | --- | ---: |
| Prior A | partial | no | yes | [value] |
| Prior B | yes | partial | no | [value] |
| Ours | yes | yes | yes | [value] |
```

### 主文压缩 case 图模板

主文 case study 应压缩。优先使用 2 个对照 case：correct vs. wrong、valid format vs. invalid format、parameter preserved vs. parameter drift、dependency maintained vs. dependency break。

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

### Teaser caption 模板

Teaser 不能只是 workflow diagram。它至少要包含问题场景、输入/输出例子、关键 challenges、本文方法/benchmark/system 结构和一个主要 empirical finding。

```text
Figure 1. [Paper Name] studies [core capability] by connecting [challenge 1], [challenge 2], and [challenge 3]. The benchmark/method exposes [main failure mode] and enables [evaluation/training loop].
```

### Related Work 数据集对比表

```markdown
| Dataset | [Challenge 1 Attribute] | [Challenge 2 Attribute] | [Challenge 3 Attribute] | Programmatic Eval | Train Split |
| --- | --- | --- | --- | --- | --- |
| Prior A | partial | no | yes | no | no |
| Prior B | yes | partial | no | yes | no |
| Ours | yes | yes | yes | yes | yes |
```

### Method 数据分布表

Method pipeline 图要标清：

- 输入数据或任务来源。
- instance/data generation。
- validation/filtering。
- model inference/training。
- programmatic evaluation 或 reward。
- analysis/error feedback。
- final output 或 learning loop。

Method 组件图应解释一个技术核心，不要重复 pipeline。适合单独画的对象包括 generator、state tracker、parser/evaluator、reward function、agent loop、training loop 或 dependency graph。

```markdown
| Split / Category | Count | Avg. Length | Difficulty | Key Attribute |
| --- | ---: | ---: | --- | --- |
| Train | [N] | [L] | [level] | [attribute] |
| Test | [N] | [L] | [level] | [attribute] |
```

表后要解释分布如何支撑 challenge，例如 long-range dependency、category coverage、parameter perturbation、negative examples 或 compositional generalization。

### 训练超参数表

```markdown
| Hyperparameter | Value |
| --- | --- |
| learning rate | [value] |
| batch size | [value] |
| training steps / epochs | [value] |
| optimizer | [value] |
| temperature / decoding | [value] |
```

主结果表应包含主指标、关键子指标和 invalid/error rate。消融表要与 Method 对齐：移除 component A 应影响 challenge A；移除 validation/feedback 应影响 correctness 或 robustness。

Analysis 图表可以包括 error breakdown、performance by difficulty、scaling trend、metric correlation、invalid distribution、category distribution 或 human/model agreement。

### 术语表

```markdown
| 正式术语 | 中文含义 | 禁用别名 | 对应证据 |
| --- | --- | --- | --- |
| [Term] | [Meaning] | [Aliases] | [Metric/Section] |
```

### GitHub Markdown 公式

GitHub 可以渲染数学公式，但它不是完整 LaTeX 环境，而是 GitHub Markdown 加 KaTeX/MathJax 子集。块级公式优先使用 fenced math block，比 `$$ ... $$` 更稳，尤其是复杂多行公式、`<details>` 折叠块、表格附近的公式。

最稳块级公式：

````markdown
```math
\mathcal{L}(\theta)
=
\mathbb{E}_{x\sim p_\theta}
\left[
\mathrm{KL}\left(
p_\theta(\cdot \mid x)
\,\|\,
p_T(\cdot \mid x)
\right)
\right].
```
````

复杂公式拆块：

````markdown
```math
\sigma_t
=
a\sqrt{\frac{t}{1-t}}.
```

```math
\bar{\sigma}_j^2
=
\sigma_{t_j}^2(-\Delta t_j).
```
````

KL 示例：

````markdown
```math
\mathrm{KL}\left(
p_S(\cdot \mid x)
\,\|\,
p_T(\cdot \mid x)
\right)
```
````

Norm 示例：

````markdown
```math
\left\lVert
\mu_S-\mu_T
\right\rVert_2^2
```
````

行内变量优先用普通 Markdown code：

```markdown
`x_t`、`mu_S`、`bar_sigma_j`
```

常见坑和替代写法：

| 高风险写法 | 问题 | 推荐写法 |
| --- | --- | --- |
| `\operatorname{KL}` | GitHub 可能报 `The following macros are not allowed: operatorname` | `\mathrm{KL}` |
| `x_{<t}` | `<t` 在 Markdown/HTML 语境里可能被预处理干扰 | `x_{1:t-1}`；正文中可写成 `` `x_<t` `` |
| `\Vert` | GitHub 数学渲染中更容易不稳定 | KL 分隔符写 `\,\|\,` |
| `\| ... \|` | norm 语义不如成对符号清楚 | `\left\lVert ... \right\rVert_2^2` |
| `\newcommand` | GitHub 不支持完整宏定义环境 | 直接写展开后的公式 |
| `\DeclareMathOperator` | GitHub 不支持完整宏定义环境 | 直接用 `\mathrm{...}` |
| `\overset{^}{y}` | 渲染风险高且可读性差 | `\hat{y}` 或 `\hat{y}_{j,k}` |

通常可用的宏：

```latex
\mathcal
\mathrm
\mathbb
\theta
\pi
\mu
\sigma
\epsilon
\Delta
\sum
\frac
\sqrt
\left
\right
\mid
\cdot
\sim
\nabla
\top
```

更推荐的稳定写法：

```latex
\mathrm{KL}
\mathcal{L}
\mathbb{E}
\mathcal{N}
\left[
\right]
\left(
\right)
\,\|\,
\lVert
\rVert
```

不推荐或高风险写法：

```latex
\operatorname{KL}
x_{<t}
\Vert
\newcommand
\DeclareMathOperator
\overset{^}{y}
```

修改公式后搜索高风险字符串：

```bash
grep -nE '\\operatorname|x_\\{<|\\Vert|\\newcommand|\\DeclareMathOperator|\\overset\\{\\^\\}' papers_*.md
```

公式不显示时按顺序修：

1. 把 `$$ ... $$` 改成 fenced math block。
2. 把 `\operatorname{...}` 改成 `\mathrm{...}`。
3. 把 `x_{<t}` 改成 `x_{1:t-1}`。
4. 把 KL 分隔符改成 `\,\|\,`。
5. 把 norm 改成 `\left\lVert ... \right\rVert`。
6. 删除自定义宏，写成完整展开公式。
7. 将超长公式拆成多个短块。

### Method 形式化定义

GitHub Markdown 版本：

````markdown
```math
\begin{aligned}
R, A &= \mathrm{Model}(Q),\\
R &= \text{reasoning process},\quad A=\text{final answer}.
\end{aligned}
```
````

LaTeX 正文版本：

```latex
\[
\begin{aligned}
R, A &= \mathrm{Model}(Q),\\
R &= \text{reasoning process},\quad A=\text{final answer}.
\end{aligned}
\]
```

### Introduction 写作片段

第一段：大背景。

```text
Recent progress in X has enabled models to do A and B. However, achieving Y requires more than A and B: systems must also handle C, D, and E. This gap becomes especially critical in [scenario], where errors in [factor] can lead to [consequence]. Therefore, understanding and improving [core capability] is necessary for [long-term goal].
```

第二段：已有工作分类。

```text
Existing studies have made progress along three directions. First, ... Second, ... Third, ... However, these lines primarily focus on [existing focus], while leaving [our problem] underexplored.
```

第三段：研究挑战。

```text
This gap raises three challenges. First, **[Term 1]**: models must [capability], because [specific difficulty source such as long context, parameter perturbation, state transition, visual grounding, or dependency propagation]. Second, **[Term 2]**: models must [capability], while avoiding [specific failure mode]. Third, **[Term 3]**: models must [capability], so that [evaluation/training/deployment consequence]. Together, these challenges require [integrated pipeline], rather than treating [subtasks] as isolated steps.
```

Challenge 总括句：

```text
In short, [core packaging term] requires a pipeline that connects [challenge 1], [challenge 2], [challenge 3], and [challenge 4], rather than treating them as isolated subtasks.
```

第四段：本文方法。

```text
For [challenge 1], we...
For [challenge 2], we...
For [challenge 3], we...
For [challenge 4], we...
```

第五段：实验发现。

```text
Results show that models can often solve local steps but fail to maintain global consistency, suggesting that current models still lack robust [core capability].
```

第六段：贡献列表。

```text
- **Task formulation.** We formalize...
- **Dataset.** We construct...
- **Evaluation.** We introduce...
- **Empirical findings.** We show...
- **Training and agent framework.** We provide...
```

### Related Work 写作片段

小节第一段：分类后的领域进展。

```text
Prior work on [area] can be grouped into [line 1], [line 2], and [line 3]. The first line focuses on..., the second line studies..., and the third line explores... Together, these works establish [shared progress].
```

小节第二段：本文区别。

```text
However, these works primarily assume [setting/format/scope], whereas our work focuses on [specific capability]. This distinction matters because [failure mode or missing evidence], which we evaluate through [metric/task/analysis].
```

避免冒犯的差异写法：

```text
Existing benchmarks primarily evaluate static visual reasoning or short-form question answering, while our focus is on long-horizon decision making under structured constraints.
```

### Method 写作片段

方法段落微结构：

```text
To address [problem], we construct [component]. Specifically, we [method]. To prevent [failure], we enforce [constraint]. This design ensures that [role in the overall task].
```

工程口吻改论文口吻：

```text
We implement an automated construction pipeline that samples source records, generates candidate instances, validates format constraints, and applies quality filters.
```

### Data / Benchmark 写作片段

LLM-generated data 验证流程：

```text
We constrain generation with [prompt/schema], reject candidates that fail [automatic checks], verify semantic consistency through [model/human review], and repair or discard instances according to [criteria].
```

### Evaluation 写作片段

指标解释：

```text
Parameter accuracy evaluates whether the model preserves values that affect execution, rather than superficial text overlap.
```

### Experiments 写作片段

结果段：

```text
As shown in Table X, model performance ranges from A to B. The strongest model achieves C, while smaller models remain below D. Notably, invalid outputs account for E, suggesting that...
```

Insight 段：

```text
This suggests that the bottleneck is not [easy factor], but [core capability]. Models can often do [local behavior], yet fail to [global behavior].
```

### Abstract 与 Conclusion 片段

Abstract 一段式模板：

```text
[Background and gap]. To address this, we introduce [method/data/system], which [core design]. [Scope/scale if available]. Experiments on [setting] show that [main finding], revealing [capability gap or benefit]. These results suggest that [broader implication].
```

Conclusion 一段式模板：

```text
We studied [problem] by introducing [method/data/system] for [core capability]. Experiments show [main finding], indicating [insight]. We hope this work supports future progress toward [long-term goal].
```

## LaTeX 中会用到的

这部分用于最终 `.tex` 论文排版和视觉强化，不是中文版 Markdown 大纲的必需格式。典型做法是：用 `xcolor` 给数值表上色；用 `\ScoreCell`、`\BestScore`、`\SecondScore` 标记结果；用 `\paragraph{Insight ...}` 写分析段首；用 `tcolorbox` 在 Appendix 展示完整 case。这些命令不应强加到中文 Markdown 大纲里，只在写 LaTeX 正文或附录时使用。

### 紧凑贡献列表

当会议页数非常紧，Introduction 最后一段贡献列表需要压缩时，可以使用 `paralist` 的 `compactitem`。贡献仍然保持 3-5 点、名词开头、语法并列；不要因为压缩版式而把多个贡献塞进一个过长 bullet。

Preamble:

```latex
\usepackage{paralist}       % compactitem
```

正文模板：

```latex
\begin{compactitem}
\item \textbf{[Contribution 1 Name]}: [one-sentence contribution, focusing on task/data/method/evaluation rather than implementation details].
\item \textbf{[Contribution 2 Name]}: [one-sentence contribution with parallel grammar].
\item \textbf{[Contribution 3 Name]}: [one-sentence contribution that states the empirical finding or released resource].
\end{compactitem}
```

示例：

```latex
\begin{compactitem}
\item \textbf{ResearchClawBench}: 40 real scientific discovery tasks with expert-annotated rubrics across 10 domains and diverse scenarios.
\item \textbf{ResearchHarness}: a unified lightweight tool-use evaluation harness for LLM baselines.
\item \textbf{Unified evaluation}: a systematic assessment of seven autonomous research agents and eleven native LLM baselines, quantifying the gap between current AI research systems and target-paper-level re-discovery.
\end{compactitem}
```

### 常用 packages 与颜色

```latex
\usepackage[table]{xcolor}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{amssymb}
\usepackage{tcolorbox}
\tcbuselibrary{breakable, skins}

\definecolor{DeepPurple}{HTML}{5C3A96}
\definecolor{LighterGray}{HTML}{F7F7FA}
\definecolor{White}{HTML}{FFFFFF}
\definecolor{RcbRowShade}{HTML}{F7F7FA}
\definecolor{RcbAppendixRowShade}{HTML}{EFEFEF}
\definecolor{RcbHighlightPurple}{RGB}{236,229,250}
\definecolor{rcbScorePurple}{HTML}{5C3A96}
\definecolor{rcbCheckGreen}{HTML}{2E7D32}
\definecolor{rcbCrossRed}{HTML}{C62828}
\definecolor{rcbPartialYellow}{HTML}{B8860B}
```

### Score heatmap 宏

```latex
\newcommand{\ScoreCell}[2]{\cellcolor{rcbScorePurple!#1!white}#2}
\newcommand{\BestScore}[2]{\ScoreCell{#1}{\textbf{#2}}}
\newcommand{\SecondScore}[2]{\ScoreCell{#1}{\underline{#2}}}
\newcommand{\DimCell}[2]{\cellcolor{rcbScorePurple!#1!white}#2}
```

第一个参数是颜色强度，通常是 0-100 的归一化整数；第二个参数是展示值。同一个表内保持颜色强度尺度一致。如果表格太花，只给关键指标列上色或降低强度。

### Related Work 属性对比符号

适用于 dataset、benchmark、method、system 的 yes/no/partial 属性列；不适合替代主结果表中的数值指标。三种符号形状不同，即使灰度打印也能区分；颜色只是辅助。

```latex
\newcommand{\cmark}{\textcolor{rcbCheckGreen}{\(\checkmark\)}}
\newcommand{\xmark}{\textcolor{rcbCrossRed}{\(\times\)}}
\newcommand{\pmark}{\textcolor{rcbPartialYellow}{\(\triangle\)}}
```

对比表模板：

```latex
\begin{table}[t]
\centering
\caption{\textbf{Comparison with related datasets.} \cmark indicates full support, \pmark indicates partial support, and \xmark indicates no support.}
\label{tab:related-datasets}
\begingroup
\small
\setlength{\tabcolsep}{4pt}
\renewcommand{\arraystretch}{1.08}
\begin{tabular}{@{}lcccc@{}}
\toprule
Dataset & [Challenge 1] & [Challenge 2] & [Challenge 3] & Programmatic Eval \\
\midrule
Prior A & \pmark & \xmark & \cmark & \xmark \\
Prior B & \cmark & \pmark & \xmark & \cmark \\
\textbf{Ours} & \cmark & \cmark & \cmark & \cmark \\
\bottomrule
\end{tabular}
\endgroup
\end{table}
```

使用规则：

- 每一列必须对应 Introduction 中的 challenge、能力边界或关键设计，不要列无关特性。
- `\pmark` 必须有明确含义，例如 only synthetic data、limited modalities、no train split、partial programmatic validation。
- Caption 或表下注明三种符号含义。
- `Ours` 放最后一行，并只在真实满足的列上用 `\cmark`。
- 符号表和数值主表分开。Related Work 对比表用 `\cmark/\pmark/\xmark`，Main Results 表用数值、bold/underline 和必要的 heatmap。

### 模型或系统图标

只有 logo 文件确实存在且图标能提升可读性时才用；否则保持纯文本模型名。如果论文不是 RCB 风格资源，重命名项目 prefix。

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

### 紧凑彩色主结果表

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

### Appendix 组织顺序

Appendix 可以比主文长，目标是可复现和可审计。不要把 appendix 当成继续压缩主文的地方。常见顺序：

1. **Training and experimental settings.** 训练设置、数据 split、模型版本、prompt、decoding、invalid handling、解析规则、硬件、超参数等表格。
2. **Supplementary results.** 补充实验结果、额外 ablation、error breakdown、更多 category/difficulty 分析。
3. **Full cases and logs.** 完整 case、完整 agent report、完整 judge reasoning、完整 run log 或完整 scoring log。

完整 case 不要只放截取版。主文可以放压缩 case，Appendix 应展示 full input、full output、full rubrics、full score items 和 full log。附录长一点是可以接受的；如果一个 case 或 log 太长，拆成多个 `tcolorbox`、多个 subsection 或 continuation pages，而不是删掉中间内容。

### Appendix tcolorbox 完整 case

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

### Appendix tcolorbox 多块文本与图片

当 appendix case 很复杂时，可以把一个完整案例拆成多个有明确边界的文本块：`Meta Info`、`Task`、`Data`、`Rubrics`、`Generated Report`、`Figures`、`Score Items`。这种结构适合展示 benchmark run、agent report、自动评分过程、失败案例或长 case study。不要把所有内容混成一段；读者应该能快速定位输入、证据、输出和评分。

建议先定义两个局部 helper，减少重复的标题和分隔线写法：

```latex
\newcommand{\CaseSection}[1]{%
  \par\smallskip\noindent{\color{DeepPurple}\rule{\linewidth}{0.35pt}}\par\smallskip
  \noindent{\color{DeepPurple}\textit{\textbf{#1}}}\par\smallskip
}
\newcommand{\CaseFirstSection}[1]{%
  \noindent{\color{DeepPurple}\textit{\textbf{#1}}}\par\smallskip
}
```

完整结构模板：

```latex
\begin{tcolorbox}[
    breakable,
    enhanced,
    fontupper=\small,
    title={(c) Math\_003},
    colback=LighterGray,
    colframe=DeepPurple,
    colbacktitle=DeepPurple,
    coltitle=White
]
\CaseFirstSection{Meta Info}
\begin{itemize}
\item \textbf{System / Model:} [Agent] / [Model]
\item \textbf{Total Score:} [score]
\item \textbf{Duration:} [seconds] seconds
\item \textbf{Cost:} \$[cost]
\end{itemize}

\CaseSection{Task}
\noindent Input: [one-sentence input description].\par
\noindent Output: [one-sentence expected output].\par
\noindent Scientific Goal: [one-sentence scientific goal].\par

\CaseSection{Data}
\begin{itemize}
\item \texttt{[file\_name]} ([data type]). [Brief description]. Path: \texttt{[relative/path/to/file]}.
\end{itemize}

\CaseSection{Rubrics}
\begin{enumerate}
\item \textbf{Text | Weight([w]):} [criterion].
\emph{Expected evidence:} [evidence 1]; [evidence 2]; [evidence 3].
\item \textbf{Image | Weight([w]):} [criterion].
\emph{Expected evidence:} [evidence 1]; [evidence 2].
\end{enumerate}

\CaseSection{Generated Report}
\medskip\noindent\textbf{\normalsize [Report Title]}\par
\medskip\noindent\textbf{\small Full Report / Log}\par
\noindent [Paste the full generated report or full log here. If it is too long for one box, continue in the next box or subsection; do not silently truncate.]\par

\CaseSection{Figures}
\begin{center}
\includegraphics[width=0.92\linewidth]{\detokenize{imgs/appendix/[CaseID]/fig1_overview.png}}
\par\footnotesize [Short Figure Title]
\end{center}
\noindent \textbf{Figure A}: [Caption explaining what the image shows and why it supports the case.]\par

\begin{center}
\includegraphics[width=0.92\linewidth]{\detokenize{imgs/appendix/[CaseID]/fig2_analysis.png}}
\par\footnotesize [Short Figure Title]
\end{center}
\noindent \textbf{Figure B}: [Caption explaining the second figure.]\par

\CaseSection{Score Items}
\begin{enumerate}
\item \textbf{Text | Weight([w]) | Score([score]):} [criterion summary].
\emph{Reasoning.} [Judge reasoning, grounded in the report and rubric.]
\item \textbf{Image | Weight([w]) | Score([score]):} [criterion summary].
\emph{Reasoning.} [Judge reasoning for visual evidence.]
\end{enumerate}
\end{tcolorbox}
```

使用规则：

- `Meta Info` 用 `itemize`，适合展示 system/model、score、duration、cost、run ID、seed 等短字段。
- `Task` 用短段落，按 `Input / Output / Scientific Goal` 或 `Question / Gold / Prediction` 组织。
- `Data` 用 `itemize`，每个文件一项；长文件名可以在下划线或路径分隔处手动加入 `\allowbreak{}`。
- `Rubrics` 和 `Score Items` 用 `enumerate`，保持 criterion、weight、score、reasoning 对齐。
- `Generated Report` / `Full Report / Log` 应保留完整内容。不要只放 representative excerpt；如果很长，拆成多个 box、多个 subsection 或 continuation pages。
- 图片放在 `center` 环境中，使用 `\includegraphics[width=0.92\linewidth]{...}`。路径中有下划线、空格或特殊字符时，用 `\detokenize{...}` 包住路径。
- 图片下面先放短标题，例如 `\par\footnotesize Dataset Overview`，再用正文 caption 解释图像证据。
- 每个 section 之间用 `\CaseSection{...}` 的 DeepPurple 分隔线，避免长 box 中块边界不清。
- `breakable` 必须保留，长 case 才能跨页。
- 不要把过多图片塞进一个 box；超过 2-3 张图时，拆成多个 box 或只保留最能支撑 insight 的图。
- LaTeX preamble 中要提前准备颜色和 packages。不要让样式损害可读性。Appendix 的完整 case 必须支撑主文中的 failure mode、metric 或 insight。
