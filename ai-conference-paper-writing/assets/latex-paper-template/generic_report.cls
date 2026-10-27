\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{generic_report}[2026/10/27 Generic research report layout]
\LoadClassWithOptions{article}
\pdfoutput=1
\pdfminorversion=7

\RequirePackage[top=2.75cm,bottom=2.5cm,left=2.5cm,right=2.5cm,columnsep=0.65cm]{geometry}
\RequirePackage[protrusion=true,expansion=false]{microtype}
\RequirePackage[T1]{fontenc}
\RequirePackage[english]{babel}
\RequirePackage{graphicx}
\RequirePackage{xcolor}
\RequirePackage[most]{tcolorbox}
\RequirePackage{etoolbox}
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\RequirePackage{caption}
\RequirePackage{tocloft}
\RequirePackage{placeins}
\RequirePackage{flafter}
\RequirePackage{needspace}
\RequirePackage[colorlinks]{hyperref}
\RequirePackage[noabbrev,nameinlink]{cleveref}
\RequirePackage[numbers,sort&compress]{natbib}

\input{seed/theme.tex}
\hypersetup{linkcolor=ReportTheme,citecolor=ReportTheme,urlcolor=ReportTheme}
\def\bibfont{\small\raggedright}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\renewcommand{\cftsecfont}{\sffamily}
\renewcommand{\cftsecpagefont}{\sffamily\color{ReportTheme}}
\renewcommand{\cfttoctitlefont}{\large\sffamily\bfseries\color{ReportTheme}}

\titleformat*{\section}{\large\sffamily\bfseries\color{ReportTheme}}
\titleformat*{\subsection}{\normalsize\sffamily\bfseries\color{ReportTheme}}
\titleformat*{\subsubsection}{\normalsize\sffamily\bfseries\color{ReportTheme}}
\titleformat*{\paragraph}{\itshape}
\pretocmd{\section}{\Needspace{12\baselineskip}}{}{}
\pretocmd{\subsection}{\Needspace{6\baselineskip}}{}{}
\clubpenalty=10000
\widowpenalty=10000
\setlength{\@fptop}{0pt}
\setlength{\@dblfptop}{0pt}
\setlength{\@fpsep}{14pt}
\setlength{\@dblfpsep}{14pt}
\DeclareCaptionFormat{report}{{\sffamily\bfseries #1#2}#3}
\captionsetup{format=report,font=small,singlelinecheck=true}

\setlength{\headheight}{27pt}
\fancypagestyle{firststyle}{\fancyhf{}\fancyhead[L]{\rule{0pt}{8mm}}}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\newcommand{\PaperTitle}{}
\renewcommand{\title}[1]{\gdef\PaperTitle{#1}}
\newcommand{\PaperAuthors}{}
\newcommand{\PaperAffiliations}{}
\newcommand{\PaperContributions}{}
\newcommand{\PaperMetadata}{}
\newcommand{\AuthorFormat}[2]{\textsf{#2$^{#1}$}}
\newcommand{\AffiliationFormat}[2]{{\small\textsf{$^{#1}$#2}}}
\renewcommand{\author}[2][]{\g@addto@macro\PaperAuthors{\AuthorFormat{#1}{#2}\quad}}
\newcommand{\affiliation}[2][]{\g@addto@macro\PaperAffiliations{\AffiliationFormat{#1}{#2}\quad}}
\newcommand{\contribution}[2][]{\g@addto@macro\PaperContributions{{\small $^{#1}$#2}\quad}}
\newcommand{\checkdata}[2][]{\g@addto@macro\PaperMetadata{{\small\textsf{\textbf{#1:}} #2}\par}}
\renewcommand{\date}[1]{\checkdata[Date]{#1}}
\newcommand{\correspondence}[1]{\checkdata[Correspondence]{#1}}
\newcommand{\PaperAbstract}{}
\renewcommand{\abstract}[1]{\gdef\PaperAbstract{#1}}
\newcommand{\PaperTeaser}{}
\newcommand{\teaser}[1]{\gdef\PaperTeaser{#1}}
\newcommand{\PaperTeaserCaption}{}
\newcommand{\teasercaption}[1]{\gdef\PaperTeaserCaption{#1}}
\newcommand{\PaperResources}{}
\newcommand{\resourcelinks}[1]{\gdef\PaperResources{#1}}
\newcommand{\email}[1]{\href{mailto:#1}{\texttt{#1}}}

\newcommand{\ReportMakeTitle}{%
  \thispagestyle{firststyle}%
  \vspace*{-6mm}%
  {\centering
    {\color{ReportTheme}\hrule height 0.5pt}\vskip 6mm
    {\Large\sffamily\bfseries\PaperTitle\par}\vskip 6mm
    {\color{ReportTheme}\hrule height 0.5pt}\vskip 6mm
    \PaperAuthors\par\smallskip
    \PaperAffiliations\par\smallskip
    \PaperContributions\par
  }
  \vskip 6mm
  \begin{tcolorbox}[enhanced,breakable,colback=white,colframe=ReportThemeLight,boxrule=0.5pt,arc=2.5mm,left=8mm,right=8mm,top=6mm,bottom=6mm]
    \ifdefempty{\PaperTeaser}{}{\begin{center}\PaperTeaser\end{center}\vskip 2mm}
    \ifdefempty{\PaperTeaserCaption}{}{{\small\PaperTeaserCaption\par}\vskip 3mm}
  \end{tcolorbox}
  \clearpage
  \begin{tcolorbox}[enhanced,breakable,colback=white,colframe=ReportThemeLight,boxrule=0.5pt,arc=2.5mm,left=8mm,right=8mm,top=6mm,bottom=6mm]
    \begin{center}{\large\sffamily\bfseries\color{ReportTheme}Abstract}\end{center}
    \PaperAbstract\par
    \ifdefempty{\PaperResources}{}{\vskip 4mm{\small\PaperResources\par}}
  \end{tcolorbox}
  \PaperMetadata
  \FloatBarrier
}
\renewcommand{\maketitle}{\ReportMakeTitle}
\newcommand{\beginappendix}{\appendix\section*{Appendix}}

% Front matter stays full width; the optional twocolumn class setting applies
% only after the main file calls \ReportBeginMain.
\newif\ifReportTwoColumn
\AtBeginDocument{\if@twocolumn\global\ReportTwoColumntrue\onecolumn\fi}
\newcommand{\ReportBeginMain}{\clearpage\ifReportTwoColumn\twocolumn\fi}
\newenvironment{widefigure}[1][htbp]{%
  \ifReportTwoColumn\begin{figure*}[#1]\else\begin{figure}[#1]\fi
}{\ifReportTwoColumn\end{figure*}\else\end{figure}\fi}
\newenvironment{widetable}[1][htbp]{%
  \ifReportTwoColumn\begin{table*}[#1]\else\begin{table}[#1]\fi
}{\ifReportTwoColumn\end{table*}\else\end{table}\fi}
