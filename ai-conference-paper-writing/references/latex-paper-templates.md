# LaTeX 论文模板

这个文件只放 AI conference paper 写作中可直接复制和改写的 LaTeX 模板。规则性判断放在 `../SKILL.md`；中文 Markdown 大纲、GitHub Markdown 公式和图表说明模板放在 `markdown-writing-templates.md`。

说明性文字默认用中文；LaTeX 命令、英文 caption、表格/图表内英文文本保留英文，便于直接复制到论文工程中。

## LaTeX 中会用到的

这部分用于最终 `.tex` 论文排版和视觉强化，不是中文版 Markdown 大纲的必需格式。典型做法是：用 `xcolor` 给数值表上色；用 `\ScoreCell`、`\BestScore`、`\SecondScore` 标记结果；用 `\paragraph{Insight ...}` 写分析段首；用 `tcolorbox` 在 Appendix 展示完整 case。这些命令不应强加到中文 Markdown 大纲里，只在写 LaTeX 正文或附录时使用。

### BibTeX 与 Citation 写法

LaTeX 论文中使用 `.bib` / BibTeX 管理引用，不要在 `References` 里手写裸文本条目。所有论文条目都必须先通过搜索或原始页面确认真实存在；如果同一工作有 arXiv 和已接收/正式发表版本，优先使用已接收/正式发表版本对应的 BibTeX。

引用位置要贴近被支持的对象：

```latex
Vision-language models have been widely used for scientific figure understanding~\citep{li2024scifig,wang2025chartvlm}.

Programmatic evaluation~\citep{chen2021codex,hendrycks2021apps} reduces ambiguity by checking executable outputs rather than relying only on text overlap.

\citet{vaswani2017attention} introduced the Transformer architecture, which later became the backbone of many language-model-based agents.
```

避免把一整段写完后堆引用：

```latex
% Avoid.
Recent work studies multimodal reasoning, tool use, long-horizon planning, and programmatic evaluation. Several benchmarks and agents have been proposed for these problems~\citep{paperA,paperB,paperC,paperD,paperE,paperF}.
```

更稳的写法是把引用分配到对应术语后：

```latex
Recent multimodal benchmarks evaluate chart and figure understanding~\citep{paperA,paperB}, while tool-use agents study external API or code execution~\citep{paperC,paperD}. Long-horizon planning benchmarks focus on multi-step state tracking~\citep{paperE}, and programmatic evaluation checks executable outputs directly~\citep{paperF}.
```

BibTeX 条目示例：

```bibtex
@inproceedings{vaswani2017attention,
  title = {Attention Is All You Need},
  author = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, Lukasz and Polosukhin, Illia},
  booktitle = {Advances in Neural Information Processing Systems},
  year = {2017}
}

@article{trinh2024alphageometry,
  title = {Solving Olympiad Geometry without Human Demonstrations},
  author = {Trinh, Trieu H. and Wu, Yuhuai and Le, Quoc V. and He, He and Luong, Thang},
  journal = {Nature},
  year = {2024}
}
```

主文件参考文献写法：

```latex
\bibliographystyle{plainnat}
\bibliography{main}
```

检查项：

- 引用数量：AI conference paper 通常不少于 40 篇，正常约 50 篇；benchmark/survey 可以更多。
- 引用真实性：每个 BibTeX entry 都要能在论文官网、ACL Anthology、OpenReview、IEEE/ACM、PMLR、NeurIPS proceedings、CVF、Springer、Nature、arXiv 等来源中找到。
- 版本选择：有正式中稿/发表版时优先引用正式版；不要在正式版已存在时继续引用旧 arXiv，除非正文明确讨论 arXiv 版本特有内容。
- 位置贴近：citation 放在对应方法、数据集、模型、任务或 claim 后面，不要段末堆引用。
- Key 稳定：BibTeX key 使用 `surnameYearShortTitle` 风格，避免 `paper1`、`refA`、`unknown2024`。

### 摘要资源链接图标

如果论文有公开 homepage、code 或 dataset，可以在 abstract 正文之后加入一小段资源入口。正文 abstract 仍保持一段式；资源入口是附加块，不要把它写成新的摘要段落或贡献列表。Page、GitHub 与 Hugging Face 的 PDF logo 已随 skill 保存：

- `assets/logos/page-logo.pdf`
- `assets/logos/github-logo.pdf`
- `assets/logos/hf-logo.pdf`

在论文项目中使用时，把这些 PDF 放到论文的图片目录，例如 `imgs/page-logo.pdf`、`imgs/github-logo.pdf` 和 `imgs/hf-logo.pdf`，或把下面命令里的路径改成实际路径。

Preamble / command definitions:

```latex
\newcommand{\homepage}{\raisebox{-1.5pt}{\includegraphics[height=1em]{imgs/page-logo.pdf}}}
\newcommand{\github}{\raisebox{-1.5pt}{\includegraphics[height=1em]{imgs/github-logo.pdf}}}
\newcommand{\huggingface}{\raisebox{-1.5pt}{\includegraphics[height=1em]{imgs/hf-logo.pdf}}}
```

Abstract 末尾资源链接块：

```latex
\vspace{\baselineskip}

\homepage\ \textbf{Page} \texttt{\url{https://[PROJECT_PAGE]}}

\github\  \textbf{Code} \texttt{\url{https://github.com/[ORG]/[REPO]}}

\huggingface\ \textbf{Data} \texttt{\url{https://huggingface.co/datasets/[ORG]/[DATASET]}}
```

如果没有 homepage，可以只保留 Code/Data 两行；如果模板不适合放图标，也可以退回纯文本：

```latex
\textbf{Page} \texttt{\url{https://[PROJECT_PAGE]}}

\github\  \textbf{Code} \texttt{\url{https://github.com/[ORG]/[REPO]}}

\huggingface\ \textbf{Data} \texttt{\url{https://huggingface.co/datasets/[ORG]/[DATASET]}}
```

使用规则：

- 需要 `graphicx` 和支持 `\url` 的包或模板；如果模板没有加载，补充 `\usepackage{graphicx}` 和 `\usepackage{hyperref}`。
- 图标高度通常用 `height=1em`，并用 `\raisebox{-1.5pt}{...}` 做基线对齐。
- 链接标签保持短：`Code`、`Data`、`Page`。不要在 abstract 资源块里解释项目细节。
- 如果会议模板禁止 abstract 内放链接，把同样的资源块移到 abstract 后、first-page footnote 或 camera-ready artifact section。

### 技术报告风格首页

适用于 arXiv technical report、project manuscript、internal report 或不受严格会议 class 限制的论文。核心思路是统一一个主题色，把标题横线、页眉 logo、章节标题、链接颜色、teaser/abstract box、case box 都放在同一套视觉语言里。不要在 NeurIPS/ICLR/ICML/ACL/CVPR 官方提交模板中强行覆盖 `\maketitle`、页眉或章节标题，除非已经确认 camera-ready 允许自定义。

这一类样式可以参考 LabHorizon 的组织方式：

- 首页左上角放机构/项目 logo，去掉页眉横线。
- Title 上方和下方各放一条主题色细横线，形成技术报告感。
- Teaser 和 resource links 放在一个 `tcolorbox` 中，摘要单独放在另一个 `tcolorbox` 中。
- Abstract 标题用主题色 sans-serif bold，正文保持一段式。
- Section、subsection、subsubsection 全部使用主题色 sans-serif bold。
- Caption 的 label 用 sans-serif bold，正文保持正常小字号。
- Hyperlink、citation、url 颜色与主题色一致。

Preamble / class-level skeleton:

```latex
\usepackage[top=2.75cm, bottom=2.5cm, left=2.5cm, right=2.5cm, columnsep=0.65cm]{geometry}
\usepackage[protrusion=true,expansion=false]{microtype}
\usepackage{graphicx}
\usepackage[most]{tcolorbox}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{caption}
\usepackage{etoolbox}
\usepackage{placeins}
\usepackage{hyphenat}
\usepackage[colorlinks]{hyperref}

\definecolor{ReportTheme}{HTML}{8C1515}
\definecolor{ReportLightGray}{HTML}{F4F4F4}
\newcommand{\reporttheme}[1]{{\bfseries\color{ReportTheme}#1}}

\hypersetup{
  linkcolor=ReportTheme,
  citecolor=ReportTheme,
  urlcolor=ReportTheme
}
```

首页页眉 logo 和隐藏页眉/页脚横线：

```latex
\setlength{\headheight}{27pt}
\fancypagestyle{firststyle}{
  \fancyhead[R]{}
  \fancyhead[L]{\includegraphics[height=8mm,keepaspectratio]{figures/[LOGO].png}}
}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}
```

章节标题和 caption 风格：

```latex
\newcommand{\sectionfont}{\fontsize{12}{10}\selectfont}
\newcommand{\subsectionfont}{\fontsize{11}{10}\selectfont}

\titleformat*{\paragraph}{\itshape}
\titleformat*{\section}{\sectionfont\sffamily\bfseries\color{ReportTheme}}
\titleformat*{\subsection}{\subsectionfont\sffamily\bfseries\color{ReportTheme}}
\titleformat*{\subsubsection}{\normalsize\sffamily\bfseries\color{ReportTheme}}

\DeclareCaptionLabelSeparator{custom}{}
\DeclareCaptionFormat{custom}{{\sffamily\textbf{#1 #2}} #3}
\captionsetup{singlelinecheck=true,format=custom,labelsep=custom,font=small}
\captionsetup[sub]{singlelinecheck=true,format=custom,labelsep=custom,font=small}
```

Title 上下横线、teaser/resource box、abstract box：

```latex
\makeatletter
\newcommand{\ReportTopTitleBar}{
  {\color{ReportTheme}\hrule height 0.5pt}
  \vskip 6mm
}
\newcommand{\ReportBottomTitleBar}{
  \vskip 6mm
  {\color{ReportTheme}\hrule height 0.5pt}
}

\newcommand{\titlefont}{\fontsize{17}{20}\selectfont}
\renewcommand{\title}[1]{\newcommand{\titlelist}{\titlefont{\sffamily #1}}}
\newcommand{\abstractinfont}{\fontsize{10}{12}\selectfont}
\renewcommand{\abstract}[1]{\def\abstractlist{{\abstractinfont #1}}}
\newcommand{\abstractlabel}{\fontsize{12}{12}\selectfont\sffamily\bfseries\textcolor{ReportTheme}{Abstract}}

\newcommand{\teaserlist}{}
\newcommand{\teaser}[1]{\def\teaserlist{#1}}
\newcommand{\teasercaptionlist}{}
\newcommand{\teasercaption}[1]{\def\teasercaptionlist{#1}}
\newcommand{\resourcelinkslist}{}
\newcommand{\resourcelinks}[1]{\def\resourcelinkslist{#1}}

\newcommand{\ReportMakeTitle}{%
  \thispagestyle{firststyle}
  \vspace*{-6mm}
  \tcbset{
    enhanced,
    left=8mm,
    right=8mm,
    top=6mm,
    bottom=6mm,
    colback=white,
    colframe=ReportTheme,
    boxrule=0.5pt,
    before skip=0pt,
    grow to left by=1.5pt,
    grow to right by=1.5pt,
    arc=2.5mm
  }
  {\setlength{\parskip}{0mm}\centering\nohyphens
    \ReportTopTitleBar
    \titlelist\par
    \ReportBottomTitleBar
    \vskip 6mm
    [AUTHOR_LIST]\par
    \vskip 3mm
    [AFFILIATION_LIST]\par
  }
  \vskip 6mm
  \begin{tcolorbox}[breakable]
    \setlength{\parindent}{0cm}
    \setlength{\parskip}{0cm}
    \ifdefempty{\teaserlist}{}{
      \begin{center}
        \includegraphics[width=0.97\textwidth,height=0.48\textheight,keepaspectratio]{\teaserlist}
      \end{center}
      \vskip 2mm
    }
    \ifdefempty{\teasercaptionlist}{}{{\small \teasercaptionlist\par}\vskip 3mm}
    \ifdefempty{\resourcelinkslist}{}{{\small \resourcelinkslist\par}}
  \end{tcolorbox}
  \clearpage
  \begin{tcolorbox}[breakable]
    \setlength{\parindent}{0cm}
    \setlength{\parskip}{0cm}
    \begin{center}
      \abstractlabel
      \vskip 3mm
    \end{center}
    \abstractlist\par
  \end{tcolorbox}
  \tcbset{reset}
  \FloatBarrier
}
\makeatother
```

作者、机构、贡献说明和元信息列表：

```latex
\makeatletter
\newcommand\addtolist[5][]{
  \begingroup
    \if\relax#3\relax\def\sep{}\else\def\sep{#5}\fi
    \let\protect\@unexpandable@protect
    \xdef#3{\expandafter{#3}\sep #4[#1]{#2}}%
  \endgroup
}
\makeatother

\newcommand{\authorfont}{\fontsize{12}{14}\selectfont}
\newcommand\authorlist{}
\newcommand\authorformat[2][]{\authorfont{\sffamily #2$^{#1}$}}
\renewcommand\author[2][]{\addtolist[#1]{#2}{\authorlist}{\authorformat}{, }}

\newcommand{\affiliationfont}{\fontsize{10}{12}\selectfont}
\newcommand\affiliationlist{}
\newcommand\affiliationformat[2][]{{\affiliationfont\sffamily $^{#1}$#2}}
\newcommand\affiliation[2][]{\addtolist[#1]{#2}{\affiliationlist}{\affiliationformat}{, }}

\newcommand{\contributionfont}{\fontsize{10}{12}\selectfont}
\newcommand\contributionlist{}
\newcommand\contributionformat[2][]{{\contributionfont $^{#1}$#2}}
\newcommand\contribution[2][]{\addtolist[#1]{#2}{\contributionlist}{\contributionformat}{, }}

\newcommand{\checkdatafont}{\fontsize{8}{10}\selectfont}
\newcommand\checkdatalist{}
\newcommand\checkdataformat[2][]{{\small{\checkdatafont\sffamily\bfseries #1:} #2}}
\newcommand\checkdata[2][]{\addtolist[#1]{#2}{\checkdatalist}{\checkdataformat}{\par}}
\renewcommand\date[1]{\checkdata[Date]{#1}}
\newcommand\correspondence[1]{\checkdata[Correspondence]{#1}}
\newcommand{\email}[1]{\href{mailto:#1}{\texttt{#1}}}
```

把上面的列表接入首页时，将 `ReportMakeTitle` 中的占位替换为：

```latex
\authorlist
\vskip 3mm
\affiliationlist\par
\vskip 3mm
\contributionlist\par
```

如果还要在首页展示日期、项目页、数据集、arXiv 或 correspondence，可以把 `\checkdatalist` 放在 title box 末尾或 abstract box 之后。元信息较多时，不要塞进摘要正文；用 `\checkdata[Project Page]{...}` 这种短行更清楚。

目录、附录入口和参考文献风格：

```latex
\usepackage[english]{babel}
\usepackage[subfigure]{tocloft}
\usepackage[numbers,sort&compress]{natbib}

\def\bibfont{\small}
\addto{\captionsenglish}{\renewcommand{\refname}{References}}

\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftsecfont}{\sffamily}
\renewcommand{\cftsecpagefont}{\sffamily\color{ReportTheme}}
\renewcommand{\cfttoctitlefont}{\sffamily\sectionfont\color{ReportTheme}}

\newcommand{\beginappendix}{%
  \appendix{\titlefont\sffamily\textcolor{ReportTheme}{Appendix}\par}%
}
```

如果主文需要目录，放在 `\maketitle` 之后、Introduction 之前；会议论文通常不放目录，technical report 或 long-form manuscript 可以放。附录入口常见写法：

```latex
\clearpage
\bibliographystyle{plainnat}
\bibliography{main}

\clearpage
\beginappendix
\input{sections/appendix}
```

单栏/双栏 `\maketitle` 适配：

```latex
\makeatletter
\if@twocolumn
\renewcommand{\maketitle}{%
  \twocolumn[%
    \vskip 3mm
    \ReportMakeTitle
    \vskip 8mm
  ]%
}
\else
\renewcommand{\maketitle}{%
  \ReportMakeTitle
  \vskip 8mm
}
\fi
\makeatother
```

自定义字体是可选项。只有当论文工程里真的包含对应字体文件时才使用；否则保持默认 Computer Modern 或模板默认字体，避免无法编译。若要复现更强的 report branding，可以把 sans-serif family 换成项目字体：

```latex
\usepackage[T1]{fontenc}

% Optional. Requires actual font files in the project.
\DeclareFontFamily{T1}{reportsans}{}
\DeclareFontShape{T1}{reportsans}{m}{n}{<-> s * [1] path/to/ReportSans-Regular}{}
\DeclareFontShape{T1}{reportsans}{b}{n}{<-> s * [1] path/to/ReportSans-Bold}{}
\DeclareFontShape{T1}{reportsans}{bx}{n}{<-> s * [1] path/to/ReportSans-Bold}{}
\renewcommand{\sfdefault}{reportsans}
\renewcommand{\rmdefault}{cmr}
```

完整主文件结构：

```latex
\documentclass[]{[report_class_or_article]}

\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{tabularx}
\usepackage{array}
\usepackage{colortbl}
\usepackage{adjustbox}
\usepackage{enumitem}
\usepackage{listings}
\usepackage{tikz}
\usetikzlibrary{positioning}

% Report theme, title-box, resource-link, table, case-box commands go here.

\title{[Title with Core Packaging Term]}
\teaser{figures/teaser.png}
\teasercaption{\textbf{Figure 1. [Project] overview.} [Caption.]}
\resourcelinks{[Page / Code / Data links]}
\author[1]{[Author]}
\affiliation[1]{[Affiliation]}
\abstract{[One-paragraph abstract.]}
\date{\today}
\correspondence{[Contact or project page]}
\checkdata[Project Page]{\url{https://[PROJECT_PAGE]}}
\checkdata[Datasets]{\url{https://[DATASET_PAGE]}}
\checkdata[arXiv]{Coming soon}

\begin{document}
\maketitle
\setcounter{figure}{1}

\input{sections/1-introduction}
\input{sections/2-related-work}
\input{sections/3-method}
\input{sections/4-experiments}
\input{sections/5-conclusion}

\clearpage
\bibliographystyle{plainnat}
\bibliography{main}

\clearpage
\beginappendix
\input{sections/appendix}

\end{document}
```

复现 report style 时的检查项：

- 首页是否只在第一页使用 logo 页眉，正文页不要被 logo 干扰。
- Title 上下横线、box frame、section title、link color 是否使用同一个主题色。
- Teaser box 是否先出现，abstract box 是否单独成块，abstract 本文是否仍是一段。
- 作者、机构、贡献和元信息是否是短行结构，不要混进摘要主体。
- 若使用目录，目录标题、section 文字和页码颜色是否与主题色一致。
- 若使用自定义字体，字体文件是否随论文工程提交并能被 CI 或 arXiv 编译环境找到。

正文使用示例：

```latex
\title{[Title with Core Packaging Term]}
\teaser{figures/teaser.png}
\teasercaption{\textbf{Figure 1. [Method] overview.} [One-sentence description of the full pipeline and main capability.]}
\resourcelinks{\begin{center}
\homepage\ \textbf{Page} \texttt{\url{https://[PROJECT_PAGE]}}\quad
\github\ \textbf{Code} \texttt{\url{https://github.com/[ORG]/[REPO]}}\quad
\huggingface\ \textbf{Data} \texttt{\url{https://huggingface.co/[ORG]/[DATASET]}}
\end{center}}
\abstract{[One-paragraph abstract. Keep the abstract itself one paragraph even if resource links are shown separately.]}

\begin{document}
\ReportMakeTitle
\setcounter{figure}{1} % The title-page teaser is treated as Figure 1 in the paper narrative.
\section{Introduction}
```

维护建议：

- 主题色只定义一次，并复用到 title bar、section title、hyperref、box frame 和关键强调，不要每个模块单独发明颜色。
- Title bar 的 `0.5pt` 横线足够克制；如果论文更偏正式报告，可以保持细线和白底，而不是用大面积色块。
- Abstract box 和 teaser box 都用 `breakable`，避免内容略长时溢出。
- 如果 abstract 前有 teaser 图，正文第一张图的计数需要手动对齐，例如 `\setcounter{figure}{1}`。
- 如果模板已有作者/机构命令，替换上面 `[AUTHOR_LIST]` 和 `[AFFILIATION_LIST]`，不要重复实现一套作者系统。

### 版面微调与图表浮动

这一节用于最终 `.tex` 排版检查。此时默认正文、caption、图大小和表格内容已经确定；排版调整应尽量不改变论文 claim、文字内容、图表数值或图像尺寸。

段落末行规则：

- 每个段落最后一行尽量超过半行，避免只剩几个词或一个短短的 dangling line。
- 如果末行不足半行，优先通过轻微压缩到上一行解决，例如检查是否有冗余短语、重复限定词或可合并的表达。
- 如果不能自然压缩到上一行，可以适度补足一句必要解释，让段落超过一行，而不是留下很短的末行。
- 不要为了版面美观删除重要 claim、弱化证据或改变 technical meaning。
- 这类微调只适合最终 polish；在结构和论证未稳定前不要过早逐段抠末行。

图表溢出规则：

- 图、表、case box 或 algorithm 一旦超出正文边框、页边距或双栏范围，必须修排版，不能保留溢出版面。
- 若溢出是由浮动位置导致的，优先只调整位置，不改正文文字、不改 caption 内容、不改图大小、不改表格数值。
- 允许图表不紧贴首次提到它的文字；可以放到上一小节末尾、下一小节开头、页顶、页底或 float page，只要整体阅读顺序仍然自然。
- 只要正文中已经明确引用对应 figure/table，图表在前后相邻区域浮动是可以接受的。
- 可调整的对象是位置和浮动策略，例如 `figure`/`table` 的 `[t]`、`[b]`、`[p]`、`[!t]`，或把图表移到相邻段落之间。
- 不要用改文字、缩小图、压缩表格、删 caption 或删内容来掩盖溢出问题。
- 如果仅靠移动位置无法解决真实宽度溢出，停止并说明需要用户确认是否允许改图大小、表格排版或内容。

最终检查项：

- 图表外边界没有超出正文区域、页边距、单栏或双栏边界。
- 图表 caption 和正文引用顺序可读，没有让读者先看到很远之后才解释的图。
- 段落末行没有大量只剩 1-3 个词的短行。
- 版面调整没有改变实验数字、claim、caption 含义、图大小或表格内容。

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

### 模型或系统图标

只有 logo 文件确实存在且图标能提升可读性时才用；否则保持纯文本模型名。复制到新论文时，请把示例宏名和 logo 路径改成当前项目自己的命名。

本 skill 已保存一组常用模型 logo，可从 `assets/logos/models/` 复制到论文工程，例如放到 `figures/logos/models/`：

- `anthropic.png`
- `deepseek.png`
- `gemini.png`
- `glm.png`
- `grok.png`
- `kimi.png`
- `mimo.png`
- `minimax.png`
- `openai.png`
- `qwen.png`

模型结果表、leaderboard 表、消融对比表中，模型名前建议加对应 provider logo，提升扫读性。不要在每个 cell 里重复 logo，只在第一列模型名处加；如果同一个系统由多个模型组成，只给主模型或系统入口加一个 logo。

推荐写法：

```latex
\newcommand{\ModelLogo}[1]{\raisebox{-1.5pt}{\includegraphics[height=1.05em]{figures/logos/models/#1.png}}\hspace{0.28em}}
\newcommand{\OpenAIModel}[1]{\ModelLogo{openai}#1}
\newcommand{\AnthropicModel}[1]{\ModelLogo{anthropic}#1}
\newcommand{\GeminiModel}[1]{\ModelLogo{gemini}#1}
\newcommand{\GrokModel}[1]{\ModelLogo{grok}#1}
\newcommand{\QwenModel}[1]{\ModelLogo{qwen}#1}
\newcommand{\GLMModel}[1]{\ModelLogo{glm}#1}
\newcommand{\KimiModel}[1]{\ModelLogo{kimi}#1}
\newcommand{\MiMoModel}[1]{\ModelLogo{mimo}#1}
\newcommand{\MiniMaxModel}[1]{\ModelLogo{minimax}#1}
\newcommand{\DeepSeekModel}[1]{\ModelLogo{deepseek}#1}
```

如果需要把引用紧跟模型名，可以额外定义 citation helper；这要求论文模板支持 `natbib` 的 `\citealp`，否则改成当前模板使用的 citation 命令。

```latex
\newcommand{\ModelRef}[1]{\textsuperscript{\citealp{#1}}}
```

表格示例：

```latex
\begin{table}[t]
\centering
\caption{\textbf{Main results on [Benchmark].} Higher is better.}
\label{tab:main-results-with-logos}
\begingroup
\scriptsize
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.08}
\resizebox{\textwidth}{!}{%
\begin{tabular}{@{}lccc@{}}
\toprule
Model & Overall & Level 1 & Level 2 \\
\midrule
\GeminiModel{Gemini 3.1 Pro}\ModelRef{google_gemini_models} & \BestScore{82}{82.1} & \ScoreCell{78}{78.4} & \BestScore{84}{84.0} \\
\OpenAIModel{GPT-5.5}\ModelRef{openai_models} & \SecondScore{79}{78.6} & \BestScore{80}{80.2} & \ScoreCell{77}{76.9} \\
\QwenModel{Qwen3.6-35B-A3B}\ModelRef{qwen_models} & \ScoreCell{72}{72.3} & \SecondScore{79}{79.1} & \SecondScore{77}{77.2} \\
\DeepSeekModel{DeepSeek V4 Pro}\ModelRef{deepseek_models} & \ScoreCell{68}{67.8} & \ScoreCell{70}{70.0} & \ScoreCell{66}{66.4} \\
\bottomrule
\end{tabular}%
}
\endgroup
\end{table}
```

使用规则：

- 模型表第一列使用 `\OpenAIModel{...}`、`\QwenModel{...}` 这类宏，不要手动在每行写 `\includegraphics`。
- logo 高度通常用 `0.9em-1.1em`，以文字基线自然对齐为准；`raisebox` 可以按模板微调。
- 宏里的图片路径必须和论文工程实际路径一致，例如 `figures/logos/models/#1.png` 或 `imgs/logos/models/#1.png`。
- 如果 logo 在压缩后的表格中显得拥挤，优先略调 `\tabcolsep` 或 logo 高度，不要删除模型名或改实验数字。
- 这些 logo 只服务可读性，不替代 citation；模型名附近仍应有对应真实引用。

更通用的系统图标写法如下。适合 agent/system 表或自定义 logo 较多的表；只有对应 logo 文件真实存在时才定义宏。

```latex
\newcommand{\CustomIcon}[1]{\raisebox{-0.12em}{\includegraphics[height=0.9em]{imgs/logos/#1.png}}\hspace{0.25em}}
\newcommand{\ClaudeIcon}{\CustomIcon{anthropic}}
\newcommand{\OpenAIIcon}{\CustomIcon{openai}}
\newcommand{\ArisIcon}{\CustomIcon{asx}}
\newcommand{\OpenClawIcon}{\CustomIcon{openclaw}}
\newcommand{\NanobotIcon}{\CustomIcon{nanobot}}
\newcommand{\EvoIcon}{\CustomIcon{evo}}
\newcommand{\ResearchClawIcon}{\CustomIcon{researchclaw}}
\newcommand{\GlmIcon}{\CustomIcon{glm}}
\newcommand{\GeminiIcon}{\CustomIcon{gemini}}
\newcommand{\DeepSeekIcon}{\CustomIcon{deepseek}}
\newcommand{\GrokIcon}{\CustomIcon{grok}}
\newcommand{\KimiIcon}{\CustomIcon{kimi}}
\newcommand{\MimoIcon}{\CustomIcon{mimo}}
\newcommand{\QwenIcon}{\CustomIcon{qwen}}
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
- `\rowcolor{CustomRowShade}` 只少量用于分组行或隔行，不要和 score heatmap 冲突。
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
