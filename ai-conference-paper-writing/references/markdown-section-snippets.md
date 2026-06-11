# Markdown Section Snippets

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
