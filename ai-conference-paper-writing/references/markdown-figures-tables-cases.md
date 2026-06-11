# Markdown Figures Tables Cases

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
