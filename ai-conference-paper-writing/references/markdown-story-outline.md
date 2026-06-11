# Markdown Story Outline

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
