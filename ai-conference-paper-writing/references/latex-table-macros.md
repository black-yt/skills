# Latex Table Macros

### 常用 packages 与颜色

```latex
\usepackage[table]{xcolor}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{amssymb}
\usepackage{textcomp}
\usepackage{tcolorbox}
\tcbuselibrary{breakable, skins}

\definecolor{DeepPurple}{HTML}{5C3A96}
\definecolor{LighterGray}{HTML}{F7F7FA}
\definecolor{White}{HTML}{FFFFFF}
\definecolor{CustomRowShade}{HTML}{F7F7FA}
\definecolor{CustomAppendixRowShade}{HTML}{EFEFEF}
\definecolor{CustomHighlightPurple}{RGB}{236,229,250}
\definecolor{CustomScorePurple}{HTML}{5C3A96}
\definecolor{CustomCheckGreen}{HTML}{2E7D32}
\definecolor{CustomCrossRed}{HTML}{C62828}
\definecolor{CustomPartialYellow}{HTML}{B8860B}
```

### Score heatmap 宏

```latex
\newcommand{\ScoreCell}[2]{\cellcolor{CustomScorePurple!#1!white}#2}
\newcommand{\BestScore}[2]{\ScoreCell{#1}{\textbf{#2}}}
\newcommand{\SecondScore}[2]{\ScoreCell{#1}{\underline{#2}}}
\newcommand{\DimCell}[2]{\cellcolor{CustomScorePurple!#1!white}#2}
```

第一个参数是颜色强度，通常是 0-100 的归一化整数；第二个参数是展示值。同一个表内保持颜色强度尺度一致。如果表格太花，只给关键指标列上色或降低强度。

### Metric 方向箭头

实验表格的指标表头经常需要标注 higher/lower is better。缩放过的表格中不要直接写数学模式箭头，例如 `\textbf{L2 Final Score $\uparrow$}` 或 `\textbf{Error Rate $\downarrow$}`。在 `adjustbox` / `resizebox` 缩放后，数学箭头可能被压到很小的字号，触发类似 `Font shape ... size <4.4> not available` 和 `Size substitutions` 的 pdfTeX warning。

更稳的写法是使用文本箭头宏：

```latex
\newcommand{\MetricUp}{\textnormal{\textuparrow}}
\newcommand{\MetricDown}{\textnormal{\textdownarrow}}
```

表头写法：

```latex
\textbf{L2 Final Score \MetricUp}
\textbf{Error Rate \MetricDown}
```

使用规则：

- 缩放表格里的表头符号尽量用文本符号宏，不要用数学模式符号。
- `\MetricUp` 表示 higher is better，`\MetricDown` 表示 lower is better。
- Caption 或表下注明箭头含义，避免读者误解。
- 如果模板不想引入 `textcomp`，也可以用普通文本 Unicode 箭头，但要确认当前 LaTeX engine 和字体能稳定编译。

### Related Work 属性对比符号

适用于 dataset、benchmark、method、system 的 yes/no/partial 属性列；不适合替代主结果表中的数值指标。三种符号形状不同，即使灰度打印也能区分；颜色只是辅助。

```latex
\newcommand{\cmark}{\textcolor{CustomCheckGreen}{\(\checkmark\)}}
\newcommand{\xmark}{\textcolor{CustomCrossRed}{\(\times\)}}
\newcommand{\pmark}{\textcolor{CustomPartialYellow}{\(\triangle\)}}
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
- `\rowcolor{CustomRowShade}` 只少量用于分组行或隔行，不要和 score heatmap 冲突。
- Caption 中说明 higher/lower is better，以及分数范围含义。
- 如果使用 icon，确保路径有效，PDF build 能找到 `imgs/logos/*.png`。
