# Latex Appendix Cases

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
3. **Full case studies.** 完整 case、完整 agent report、完整 judge reasoning、完整 score items 和完整评审记录。

完整 case 不要只放截取版。主文可以放压缩 case，Appendix 应展示 full input、full output、full rubrics、full score items 和完整 case study 记录。这里的 log 指完整 case study 展示，不是训练日志。附录长一点是可以接受的；如果一个 case study 太长，拆成多个 `tcolorbox`、多个 subsection 或 continuation pages，而不是删掉中间内容。

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
\medskip\noindent\textbf{\small Full Report / Case Study Record}\par
\noindent [Paste the full generated report and full case-study record here. If it is too long for one box, continue in the next box or subsection; do not silently truncate.]\par

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
- `Generated Report` / `Full Report / Case Study Record` 应保留完整内容。不要只放 representative excerpt；如果很长，拆成多个 box、多个 subsection 或 continuation pages。
- 图片放在 `center` 环境中，使用 `\includegraphics[width=0.92\linewidth]{...}`。路径中有下划线、空格或特殊字符时，用 `\detokenize{...}` 包住路径。
- 图片下面先放短标题，例如 `\par\footnotesize Dataset Overview`，再用正文 caption 解释图像证据。
- 每个 section 之间用 `\CaseSection{...}` 的 DeepPurple 分隔线，避免长 box 中块边界不清。
- `breakable` 必须保留，长 case 才能跨页。
- 不要把过多图片塞进一个 box；超过 2-3 张图时，拆成多个 box 或只保留最能支撑 insight 的图。
- LaTeX preamble 中要提前准备颜色和 packages。不要让样式损害可读性。Appendix 的完整 case 必须支撑主文中的 failure mode、metric 或 insight。
