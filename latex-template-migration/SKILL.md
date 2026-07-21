---
name: latex-template-migration
description: "将 arXiv、旧会议、旧期刊或自定义 LaTeX 论文工程迁移到目标会议/期刊投稿模板；用于模板 A 到模板 B 的 LaTeX class/style/bibliography/单双栏转换、页数约束、图表公式排版、PDF 可视化检查、文本 diff 守恒、模板标准文件守恒和最终压页。"
---

# LaTeX Template Migration

## 核心目标

- 先把论文工程从源模板迁移到目标投稿模板，并确保能稳定编译、PDF 美观、图表公式不重叠。
- 第一阶段只做模板迁移和排版适配，不改正文语义文本；允许超页数，但不允许隐藏内容丢失。
- 后续阶段按页数缺口分层处理：先排版压缩，再轻微文字压缩，最后才询问是否移动内容到补充材料。
- 全程用 diff、LaTeX 编译日志、PDF 转图片可视化检查来证明迁移没有偷偷改内容或破坏模板。

## 硬性边界

- 不修改目标会议/期刊提供的标准 class/style/template 文件；如必须加宏或长度调整，放在主 `.tex` 或项目自有 preamble 文件中，并能和官方模板包 diff 区分。
- 第一阶段不改论文正文、claim、实验数字、表格数据、公式含义、引用意图或 conclusion。
- 第一阶段可调整 float、equation、table 的位置、大小、跨栏形式和 LaTeX 包装方式；这些调整必须服务排版，不改变内容。
- 不为了压页删除数据、实验、图表证据、重要 citation 或方法定义。
- 不在用户未授权时 commit 或 push；可以用 git diff 做检查，但不要把阶段性调整提交成历史。
- 如果目标模板规则不明确，先查看官方 author kit、sample paper、submission checklist 和页数/匿名/补充材料要求，不凭印象猜。

## 启动前清点

- 确认源工程入口：主 `.tex`、`bib`、figures、tables、appendix/supplement、custom `.sty`、Makefile 或 latexmk 配置。
- 确认目标模板：官方 author kit、`.cls`、`.sty`、sample `.tex`、bibliography style、compiler 要求、单双栏、匿名设置和页数限制。
- 先编译源版本，保存源 PDF 页数、日志和可视化截图；源版本不能编译时，先记录原因，再决定是否先修源工程。
- 保留一份目标模板官方原件目录，用于后续 `diff -ru` 检查模板文件是否被改。
- 尽量把输出放入项目内可清理的 build 目录，例如 `build/template-migration/`，不要把中间文件散在源码目录。

常用基线命令：

```bash
git status --short
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/source paper.tex
pdfinfo build/source/paper.pdf | sed -n '1,80p'
pdftoppm -png -r 180 build/source/paper.pdf build/source/page
```

如果项目使用 `xelatex`、`lualatex`、`bibtex`、`biber` 或官方脚本，以目标模板要求为准。

## 阶段一：只换模板

阶段一的验收目标是“模板 B 下排版正常”，不是“页数已经合格”。

执行顺序：

1. 用目标模板 sample 作为骨架，迁移 title、author block、abstract、sections、bibliography、appendix 和必要宏定义。
2. 替换 `\documentclass`、conference/journal option、bibliography style、`\maketitle`、appendix/supplement 入口等模板相关结构。
3. 优先复用源工程的正文文件，例如 `\input{sections/introduction}`，减少手工复制正文导致的误改。
4. 对单双栏转换做排版适配：`figure`/`table` 与 `figure*`/`table*` 按目标模板切换，宽图和宽表优先用跨栏环境。
5. 对公式做宽度适配：长公式可用 `aligned`、`split`、`multline` 或局部缩放，但不能改变数学含义。
6. 对表格做宽度适配：优先调整 `tabcolsep`、字号、列宽、`resizebox`/`adjustbox`，不要删列、删数据或改数字。
7. 对图片做宽度适配：单栏通常用 `0.95\linewidth` 到 `\linewidth`，跨栏通常用 `0.85\textwidth` 到 `\textwidth`，以不越界和清晰为准。
8. 编译到无错误，排查 undefined refs/citations、missing figures、overfull boxes、float too large 和 bibliography 错误。
9. PDF 转图片逐页检查：无文字重叠、无图表越界、无公式截断、无异常大空白、无标题/作者/页眉错误。

阶段一允许做的排版调整：

- 移动图、表、公式或算法块在源码中的相对位置，使其靠近首次正文引用并减少空隙。
- 调整 `figure`、`table`、公式、算法、caption 和子图的尺寸。
- 切换单栏/双栏 float 环境。
- 调整局部 float placement，例如 `[t]`、`[tb]`、`[!t]`。
- 增加必要的 template-compatible 包装命令，例如 `\centering`、`minipage`、`subfigure`、`resizebox`。

阶段一禁止做的内容调整：

- 改写段落、句子、摘要、conclusion 或 related work。
- 改实验结果、数据、指标、模型名、表格数值或 caption 含义。
- 删除图表、公式、引用、脚注、算法、appendix 内容。
- 改目标模板官方 `.cls`、`.sty` 或官方 sample 的模板文件。

阶段一 diff 检查：

```bash
git diff --check
git diff --stat
git diff --word-diff -- '*.tex'
diff -ru target-template-pristine/ target-template-current/ || true
```

如果源版本和目标版本入口文件不同，额外做展开文本对比。优先用 `latexpand` 展开 `\input`，再用 `detex` 或同等工具抽取正文文本；工具不可用时，至少对所有正文 section 文件做 `diff -u`：

```bash
mkdir -p build/template-migration-diff
latexpand source-main.tex > build/template-migration-diff/source-expanded.tex
latexpand target-main.tex > build/template-migration-diff/target-expanded.tex
detex build/template-migration-diff/source-expanded.tex > build/template-migration-diff/source-text.txt
detex build/template-migration-diff/target-expanded.tex > build/template-migration-diff/target-text.txt
diff -u build/template-migration-diff/source-text.txt build/template-migration-diff/target-text.txt
```

检查时按语义分类：

- 允许：preamble、模板命令、float placement、figure/table/equation wrapper、尺寸参数、文件组织变化。
- 不允许：正文 prose 改写、数字变化、claim 变化、citation 意图变化、公式等价性无法确认的改写。
- 如果必须改文字才能适配模板要求，例如匿名作者信息或 mandatory statement，单独记录，不和正文改写混在一起。

## 页数判断

阶段一完成后再判断页数。先确认目标要求：

- 主文页数限制：例如 8 页、9 页、12 页。
- References 是否计入页数。
- Appendix/supplement 是否单独提交。
- Camera-ready 与 submission 页数是否不同。
- 匿名信息、ethics、limitations、checklist、acknowledgement 是否计入主文。

页数目标：

- 在目标页数内尽量写满，不留明显空白。
- 最后一页最后一行应尽量接近页面底部；大面积空白会显得不认真。
- 如果少很多页，不要靠废话填充；需要询问用户是否补实验、补分析、把 supplement 内容移入正文或调整论文结构。

判断命令：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/target paper.tex
pdfinfo build/target/paper.pdf | rg '^Pages:'
pdftoppm -png -r 180 build/target/paper.pdf build/target/page
```

## 阶段二：不改文字压缩

如果超页，第二阶段只做排版压缩，不改正文文字。

优先顺序：

1. 调整 float 位置，减少单独占页和大块空白。
2. 合并或压缩图表布局，例如多子图横排、宽图跨栏、表格跨栏或单栏重排。
3. 微调图表尺寸，但保证坐标轴、legend、数字和文本可读。
4. 局部使用 `\vspace` 压缩图表上下空白，但幅度要小，不能造成重叠或模板违规。
5. 调整 caption spacing、`tabcolsep`、`arraystretch`、列表间距和算法块间距。
6. 检查 bibliography 样式是否按目标模板要求，不能私自改成更短但不合规的格式。

`vspace` 使用规则：

- 只在明确的大空隙处局部使用，例如 figure 前后、caption 后、section 前后。
- 每处改动尽量小，例如 `-0.2em`、`-0.4em`、`-0.6em`；避免连续堆叠大负值。
- 每次加完都重新编译并可视化检查上下文，不允许文字、caption、图表互相压住。
- 不修改目标模板 `.cls` / `.sty` 中的全局 spacing。

阶段二验收：

- 页数减少或空隙减少。
- 没有文字重叠、图表越界、caption 撞图、页脚撞内容。
- `git diff --word-diff -- '*.tex'` 中没有正文文本改写。

## 阶段三：轻微文字压缩

如果排版压缩后仍超页，才进入文字压缩。

允许优先压缩：

- caption 中重复正文的长解释。
- 表格列名、legend 名称、method 名称的冗长表达。
- 过渡句、重复定义、弱总结句。
- 已经在图表或公式中表达清楚的重复说明。
- Appendix 指针、实现细节、低价值限定语。

禁止压缩：

- 核心方法定义。
- 实验设置中影响复现的细节。
- 关键数据、指标、误差、显著性、模型名称和 dataset 名称。
- 主要 claim、contribution、limitation 和 conclusion 的实质内容。
- 会改变审稿人理解的定语、边界条件或风险控制表述。

文字压缩流程：

1. 每次只压一个局部区域，例如一个 caption、一张表、一个段落。
2. 用 `git diff --word-diff` 复核没有改变 claim 或数据。
3. 编译并检查页数和视觉效果。
4. 记录压缩来源，例如 caption、table header、method detail。

## 阶段四：仍超页时询问

如果仍然超出太多，不要继续硬压。

需要向用户说明：

- 当前目标页数、当前页数、超出多少。
- 阶段二已经做过哪些不改文字压缩。
- 阶段三已经压缩了哪些低风险文字。
- 继续压缩会伤害哪些内容或证据。

可询问用户选择：

- 将部分图表、算法、case、proof、implementation detail 移到 supplement。
- 删除或合并低优先级实验。
- 把 supplement 中更重要的内容移入正文，同时删除正文低价值内容。
- 调整论文结构或重新确定投稿目标。

## 阶段五：压行和最终美观

内容和页数合格后，再做最终压行。

检查目标：

- 每个段落最后一行尽量超过半行。
- 避免一行只有几个单词或一个短短 citation。
- 避免图表页前后出现大块空白。
- 避免 section 标题孤立在页底。
- 避免公式单独撑出大片空白。

处理方式：

- 对短尾段落，优先删掉或压缩上一行中的低价值词，让尾行并入上一行。
- 如果尾行无法并入上一行，适当补充有信息量的限定或总结，使尾行超过半行。
- 对 caption 和 table note，优先压缩重复词，避免短尾。
- 对图表造成的短尾，优先移动 float 位置，而不是硬改正文。
- 编译后转图片逐页看最终效果；LaTeX 源码换行本身不代表 PDF 行宽结果。

## 编译与可视化检查

推荐每轮都执行：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/target paper.tex
rg -n "(^!|LaTeX Warning|Package .* Warning|Overfull|Underfull|Float too large|undefined|Citation.*undefined)" build/target/*.log || true
pdfinfo build/target/paper.pdf | rg '^Pages:'
pdftoppm -png -r 180 build/target/paper.pdf build/target/page
```

可视化重点：

- 首页 title、author、affiliation、abstract、keywords 是否符合模板。
- 双栏正文是否有跨栏图表压住文字。
- 单栏转双栏后公式是否越界。
- 宽表是否可读，表格线和数字是否清楚。
- 图片是否清晰，子图标签是否可见。
- 页眉、页脚、页码、line number、匿名标记是否符合投稿阶段。
- references、appendix、supplement 起止位置是否符合要求。

## 最终交付检查

- `latexmk` 无 fatal error。
- 关键 warning 已排查，剩余 warning 不影响投稿 PDF。
- 目标模板官方文件与 pristine copy 对比无非预期改动。
- 第一阶段文字 diff 已确认没有正文语义改动。
- 最终 PDF 页数满足目标要求，并尽量写满最后一页。
- PDF 转图片逐页检查通过，没有重叠、越界、异常空白和短尾明显问题。
- 生成物、中间文件和 build 缓存没有污染源码目录。
- 最终说明中列出：使用的目标模板、编译命令、页数、主要排版调整、是否发生文字压缩、仍需用户确认的问题。
