# Visual And Experiment Layout

Use this reference when creating a full AI conference paper outline, deciding figures/tables, or revising the Method/Experiment/Case Study structure.

## Main Paper Figure/Table Order

Recommended main-paper sequence:

1. **Teaser figure before Abstract.** Place it before the abstract, usually after title/authors. It should communicate the task, capability gap, method idea, and key finding in one view.
2. **Method pipeline figure.** Place it at the beginning of Method. Show inputs, modules, outputs, validation/training/evaluation loop, and which challenge each module addresses.
3. **Method component or algorithm figure.** Add one later Method figure for a concrete component: data generator, parser/evaluator, reward function, state tracker, agent loop, dependency graph, or training loop.
4. **Main results table.** Put it early in Experiments. It answers the central empirical question.
5. **Ablation tables.** Use 1-2 tables, each tied to a core design choice.
6. **Analysis figures/tables.** Use 2-3 figures/tables for 2-3 insights. These do not need separate subsections; use `\paragraph{Insight ...}`.
7. **Compressed case studies.** Put 2 cases in the main paper and complete cases in Appendix.

## Teaser Figure

The teaser should not be only a workflow diagram. It should include:

- problem scenario
- input/output example
- key challenges
- proposed method or benchmark structure
- one main empirical finding

Caption template:

```text
Figure 1: [Paper Name] studies [core capability] by connecting [challenge 1], [challenge 2], and [challenge 3]. The benchmark/method exposes [main failure mode] and enables [evaluation/training loop].
```

## Related Work Dataset Table

For benchmark or data papers, add a dataset comparison table in Related Work. Put `Ours` in the last row. Columns should match the paper challenges, not arbitrary dataset properties.

Example:

| Dataset | [Challenge 1 Attribute] | [Challenge 2 Attribute] | [Challenge 3 Attribute] | Programmatic Eval | Train Split |
| --- | --- | --- | --- | --- | --- |
| Prior A | partial | no | yes | no | no |
| Prior B | yes | partial | no | yes | no |
| Ours | yes | yes | yes | yes | yes |

The table should prove the paper's gap claim. Avoid making `Ours` look better only because it is larger. Ideally, `Ours` is most complete on columns that correspond to the named challenges. After the table, explain which abilities were previously covered separately and how the new work unifies them.

## Method Figures And Data Distribution

Method pipeline figure should mark:

- input data or task source
- instance/data generation
- validation/filtering
- model inference/training
- programmatic evaluation or reward
- analysis/error feedback
- final output or learning loop

Method component figure should explain one technical core and should not duplicate the pipeline. Good targets include a generator, state tracker, parser/evaluator, reward function, agent loop, training loop, or dependency graph.

For benchmark/data work, add a data distribution table in Method:

| Split / Category | Count | Avg. Length | Difficulty | Key Attribute |
| --- | ---: | ---: | --- | --- |
| Train | [N] | [L] | [level] | [attribute] |
| Test | [N] | [L] | [level] | [attribute] |

Explain how the distribution supports the challenges: long-range dependency, category coverage, parameter perturbation, negative examples, or compositional generalization.

## Experiment Layout

Recommended Experiment structure:

1. **Experimental Setup.** Models, data, prompt, decoding, invalid handling, statistics. For training papers, add a hyperparameter table.
2. **Main Results.** One main table for overall performance and the central claim.
3. **Ablation Studies.** 1-2 tables tied to core modules or design choices.
4. **Analysis.** 2-3 figures/tables, each producing one insight.
5. **Case Study.** 2 compressed main-paper cases; full cases in Appendix.

Training hyperparameter table:

| Hyperparameter | Value |
| --- | --- |
| learning rate | [value] |
| batch size | [value] |
| training steps / epochs | [value] |
| optimizer | [value] |
| temperature / decoding | [value] |

Main table columns should include the main metric, key sub-metrics, and invalid/error rate. Ablation tables should match Method: removing component A should affect challenge A; removing validation/feedback should affect correctness or robustness.

Analysis figures/tables can include error breakdown, performance by difficulty, scaling trend, metric correlation, invalid distribution, category distribution, or human/model agreement.

## LaTeX Table Coloring

Use table coloring for main results, ablations, and analysis tables when it helps readers scan numeric patterns. Color must support the claim, not decorate the table. Always pair color with typography such as bold for best and underline for second-best, so the table remains readable in grayscale.

Common palette and packages:

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

Score heatmap macros. The first argument is color intensity, usually a normalized integer from 0 to 100; the second argument is the displayed value.

```latex
\newcommand{\ScoreCell}[2]{\cellcolor{rcbScorePurple!#1!white}#2}
\newcommand{\BestScore}[2]{\ScoreCell{#1}{\textbf{#2}}}
\newcommand{\SecondScore}[2]{\ScoreCell{#1}{\underline{#2}}}
\newcommand{\DimCell}[2]{\cellcolor{rcbScorePurple!#1!white}#2}
```

Optional model or system icons. Use only when the logo files exist and icons improve readability; otherwise keep plain text model names. Rename the project prefix if the paper is not using RCB-style assets.

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

Compact colored result table skeleton:

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

Practical rules:

- Keep the intensity scale consistent within a table. If scores are 0-100, the score itself can often be the intensity; otherwise normalize first.
- Do not over-saturate every cell. If the table becomes visually heavy, color only key metric columns or use lower intensity.
- Use `\rowcolor{RcbRowShade}` sparingly for section separators or alternating rows; do not fight with score heatmaps.
- In captions, state whether higher or lower is better and what the score range means.
- If using icons, ensure paths are valid and the PDF build includes `imgs/logos/*.png`.

Use paragraph-level insights:

```latex
\paragraph{Insight 1: Models fail primarily through dependency breaks rather than local perception errors.}
As shown in Figure X, ...
This suggests that ...
```

Each experiment part should use two paragraphs:

1. Result paragraph: describe numbers and trends.
2. Insight paragraph: explain why the result matters for the paper's core capability.

## Case Study And Appendix

Main paper case studies should be compressed. Use two cases when possible, preferably contrastive:

- correct vs. wrong
- valid format vs. invalid format
- parameter preserved vs. parameter drift
- dependency maintained vs. dependency break

Each case should include sample ID, input summary, gold answer, model output excerpt, score, and error explanation.

Appendix can show full cases. A compact `tcolorbox` format:

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

Prepare colors and packages in the LaTeX preamble. Do not let styling reduce readability. Full cases must support the main-paper failure modes, metrics, or insights.
