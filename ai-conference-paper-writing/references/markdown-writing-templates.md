# Markdown 写作模板

这个文件只放 AI conference paper 写作中可直接复制和改写的 Markdown 模板。规则性判断放在 `../SKILL.md`；LaTeX 成稿技巧放在 `latex-paper-templates.md`。

说明性文字默认用中文，便于快速沟通论文结构；只有图内英文文本、英文 caption、Markdown 模板等会直接进入英文论文或图表的内容保留英文。

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

一段式英文摘要。一般不要在 Abstract 中放 citation；背景引用放到 Introduction。

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

核心目标是让 Markdown 在 GitHub 上稳定渲染，不被 Markdown、HTML、KaTeX/MathJax 三层解析互相干扰。GitHub 可以渲染数学公式，但它不是完整 LaTeX 环境；写法上优先追求稳定，而不是追求 LaTeX 排版精致。

最重要规则：

- 独立公式优先用 GitHub 支持的 `math` 围栏。
- 不要默认用 `$$ ... $$`。
- `$$` 理论上能渲染，但在 `<details>`、HTML 标签、表格、空行、OCR 乱码、特殊字符附近更容易失败。
- 表格里尽量不要渲染公式；复杂公式移出表格，表格只写变量名、shape 和含义。

推荐块级公式：

````markdown
```math
\widehat{P}(y_i \succ \pi_t \mid x)
=
\frac{1}{K}\sum_{k=1}^{K}
\Pr(y_i \succ y_k \mid x)
```
````

场景选择：

| 场景 | 推荐写法 |
| --- | --- |
| 很短的行内变量 | `$K=5$`、`$\pi_t$`，或普通 code：`` `x_t` `` |
| 长公式 | ` ```math ` |
| 多行公式 | ` ```math ` |
| 有 `\frac` / `\sum` / `\mathbb` / `\mathrm` | ` ```math ` |
| 表格里出现公式 | 尽量不要渲染，写成反引号文本 |
| 表格里必须表达条件概率 | 用 `given` 或 `\mid`，不要写裸 `|` |

行内变量也可以优先用普通 Markdown code，例如 `` `x_t` ``、`` `mu_S` ``、`` `bar_sigma_j` ``。

`math` 围栏规范：

- 必须独占行。
- 前后留空行。
- 不要粘在一句话后面。
- 不要放进 Markdown 表格单元格。
- 放在 `<details>` 里时，也要让围栏前后都有空行。

稳定示例：

````markdown
这里是解释文字：

```math
\pi_\theta(y \mid x)
=
\prod_i \pi_\theta(y_i \mid x,y_{1:i-1})
```

这里继续解释变量。
````

不要这样写：

````markdown
公式是：```math
...
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

Loss/KL 块级示例：

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

Norm 示例：

````markdown
```math
\left\lVert
\mu_S-\mu_T
\right\rVert_2^2
```
````

下标里的 `<` 和 `>` 是最常见高风险写法。危险：

````markdown
```math
\pi_\theta(y \mid x)=\prod_i \pi_\theta(y_i \mid x,y_{<i})
```
````

GitHub 可能把 `y_{<i}` 里的 `<i` 当成 HTML/tag 相关内容，导致 `Extra open brace or missing close brace`。稳定写法是改成区间记号：

````markdown
```math
\pi_\theta(y \mid x)
=
\prod_i \pi_\theta(y_i \mid x,y_{1:i-1})
```
````

类似替换：

| 高风险 | 稳定写法 |
| --- | --- |
| `s_h=(x,y_{<h})` | `s_h=(x,y_{1:h-1})` |
| `y_{\le h}` | `y_{1:h}`，正文解释“前 h 个 token” |
| `x_{<t}` | `x_{1:t-1}` |

正文里可以用普通 code 解释原始概念，例如 `` `x_<t` ``，但公式块里不要写 `x_{<t}`。

高风险宏和替代：

| 高风险 | 稳定写法 |
| --- | --- |
| `\operatorname{KL}` | `\mathrm{KL}` |
| `\operatorname*{argmax}` | `\arg\max` |
| `\overset{^}{y}` | `\hat{y}` 或 `\widehat{y}` |
| `\mathcal { M }` | `\mathcal{M}` |
| `\begin{array}` | 拆成多个 `math` 块或普通 Markdown 列表 |
| `\begin{align}` | 拆成多个 `math` 块；必要时只用很简单的 `aligned` |
| `\substack` | 拆成多行文字说明或多个公式块 |
| `\newcommand` | 直接写展开后的公式 |
| `\DeclareMathOperator` | 直接用 `\mathrm{...}` |
| `\Vert` | KL 分隔符写 `\,\|\,` |
| `\| ... \|` | norm 写 `\left\lVert ... \right\rVert_2^2` |

其中 `\operatorname{KL}` 在 GitHub 可能报 `The following macros are not allowed: operatorname`，直接写 `\mathrm{KL}` 更稳。

少用纯排版宏。以下宏不是数学含义必须，GitHub 上没必要冒险：

```latex
\bigl
\bigr
\Bigl
\Bigr
\!
```

改成普通括号或：

```latex
\left( ... \right)
\left[ ... \right]
```

稳定示例：

````markdown
```math
\Pr(y \succ y' \mid x)
=
\sigma\left(r(y;x)-r(y';x)\right)
```
````

比下面更稳：

````markdown
```math
\Pr(y \succ y' \mid x)=\sigma\bigl(r(y;x)-r(y';x)\bigr)
```
````

表格里的公式经验：

- Markdown 表格用 `|` 分列，所以公式里不要出现裸竖线。
- 表格里只写变量名、shape 和含义。
- 条件概率、KL、norm 等公式移出表格。

危险：

```markdown
| `P(y|x)` | 条件概率 |
```

推荐：

```markdown
| `P(y given x)` | 条件概率 |
```

或者把公式移出表格：

````markdown
条件概率写作：

```math
P(y \mid x)
```
````

OCR/PDF 解析公式必须手工清理。PDF 解析出来的公式经常会有异常空格、错括号、断裂命令。

危险：

```latex
\hat { \mathcal { M } } ( x , t , m )
```

稳定：

````markdown
```math
\widehat{\mathcal{M}}(x,t,m)
```
````

危险：

```latex
${\overset{^}{y}_{j,k}}$
```

稳定：

````markdown
```math
\hat{y}_{j,k}
```
````

推荐稳定符号：

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
\mathbb{E}
\mathbb{R}
\mathcal{N}
\mathcal{L}
\mathrm{KL}
\mathrm{ref}
\mathrm{PairRM}
\frac{...}{...}
\sum_{k=1}^{K}
\left\lVert x \right\rVert_2^2
\Pr(y \succ y' \mid x)
\pi_\theta(y\mid x)
```

公式旁边必须解释变量，尤其是 RLHF、diffusion、world model、agent training 和 benchmark metric 公式。公式后说明：

- 每个变量是什么。
- 是标量、token 序列、分布还是张量。
- 形状是什么，例如 `[B,T,D]`、`[B,N_v,D]`。
- 这个公式实际在做什么。

示例：

```text
这里的 `y_{1:i-1}` 表示 response 中第 1 到第 i-1 个 token，也就是生成第 i 个 token 时已经看到的前缀。
```

修完公式后的检查清单：

```bash
grep -nE '\\$\\$|\\operatorname|\\operatorname\\*|\\bigl|\\bigr|\\Bigl|\\Bigr|\\!|y_\\{<|<think>|<answer>' papers_*.md
git diff --check
```

还要确认：

- ` ```math ` 数量和关闭围栏配对。
- 没有公式围栏嵌在表格里。
- 没有 `<think>`、`<answer>` 这类未转义标签。
- GitHub 页面上没有 `Unable to render rich display`。

公式不显示时按顺序修：

1. 把 `$$ ... $$` 改成 fenced math block。
2. 把 `\operatorname{...}` 改成 `\mathrm{...}`。
3. 把 `x_{<t}` 改成 `x_{1:t-1}`。
4. 把 KL 分隔符改成 `\,\|\,`。
5. 把 norm 改成 `\left\lVert ... \right\rVert`。
6. 删除自定义宏，写成完整展开公式。
7. 将超长公式拆成多个短块。

一句话总结：GitHub 上写公式，不追求 LaTeX 排版精致，追求 KaTeX + Markdown + HTML 三层都稳定。长公式用 `math` 围栏，复杂符号简化，prefix 下标别写 `<`，表格里别塞公式。

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
