---
name: latex-template-migration
description: "将 arXiv、旧会议、旧期刊或自定义 LaTeX 论文工程迁移到目标会议/期刊投稿模板；用于模板 A 到模板 B 的 LaTeX class/style/bibliography/单双栏转换、投稿要求 web search 备忘、全匿名投稿检查、页数约束、图表公式排版、PDF 可视化检查、逐页 desk-reject 风险审计、文本/图片/表格/公式守恒、模板标准文件守恒和最终压页。"
---

# LaTeX Template Migration

## 核心目标

- 先把论文工程从源模板迁移到目标投稿模板，并确保能稳定编译、PDF 美观、图表公式不重叠。
- 投稿版本必须完全匿名：不能出现作者信息、affiliation、acknowledgement、个人主页、项目链接、代码/数据链接或暗示“这是我们之前工作”的表述；即使源版本来自 arXiv、camera-ready 或技术报告，submission 版本也默认按匿名稿处理。
- 阶段1只做模板迁移和排版适配，不改正文语义文本；允许超页数，但不允许文本、图片、表格、公式、算法、case、proof 或关键脚注丢失。
- 后续阶段按页数缺口分层处理：先排版压缩，再轻微文字压缩，最后才询问是否移动内容到补充材料。
- 写满、空隙、短尾和最终压行要求默认只针对 references 之前的正文部分；参考文献不按正文审美处理，不要求最后一行写满，也不因 references 区域空隙判断论文是否认真。
- 全程用投稿要求检索备忘、diff、内容清点、LaTeX 编译日志、PDF 转图片可视化检查和逐页风险审计表来证明迁移没有偷偷改内容、删掉多模态证据或破坏模板。

## 硬性边界

- 不修改目标会议/期刊提供的标准 class/style/template 文件；如必须加宏或长度调整，放在主 `.tex` 或项目自有 preamble 文件中，并能和官方模板包 diff 区分。
- 不改全文行间距、正文字体、页边距、正文区域大小或模板全局版式；不要通过 `\linespread`、`\baselinestretch`、`\setstretch`、全局 `\small`/`\footnotesize`、`geometry`、`\textwidth`、`\textheight`、`\oddsidemargin`、`\evensidemargin`、`\topmargin`、`\footskip` 等方式压缩全文。这类改动属于投稿模板敏感项，可能触发 desk reject；除非是官方模板选项或 venue 明确要求，否则不要使用。
- 投稿版本必须全匿名，除非目标明确是 camera-ready 或用户明确要求非匿名版本；submission 阶段默认删除或模板化作者、单位、邮箱、ORCID、主页、funding、acknowledgement 和 PDF metadata 中的身份信息。不要因为源稿是 arXiv、旧 camera-ready、技术报告或内部版本，就保留任何身份痕迹。
- 投稿版本不能包含外部链接，包括 project page、GitHub、Hugging Face、OpenReview 外链、demo/video、个人主页、机构页面、匿名性不足的数据下载链接和脚注 URL；如目标 venue 允许匿名补充链接，也必须先得到用户确认。
- 自引必须使用第三人称正常引用，不写“our previous work”“we previously proposed”“we build on our ...”这类暗示身份的句子。
- 所有阶段默认保留正文中的文本、图片、表格、公式、算法、case、proof、重要脚注和关键引用；这些内容是论文信息密度和说服力的一部分，不应为了压页直接删除。
- 实验部分的主结果表、消融表、实验设置表、分析图、case/qualitative example 图表是核心证据，优先保留在正文中；不要为了压缩页数删除、弱化成一句话、改成普通列表，或未经用户同意移入 appendix/supplement。
- 表格必须保持表格形态；不能为了省空间把 main result、ablation、setting、comparison、analysis 等表格改写成 prose、bullet list 或纯文本 summary。可以压缩字号、列宽、`tabcolsep`、`arraystretch`、caption 和布局，但不能让结构化证据消失。
- 如果某段文字被删除、压缩或匿名化后又需要加回，优先从源论文、源 LaTeX、原始 arXiv/技术报告或用户提供的原稿中恢复第一手文本；不要凭记忆重写，也不要让模型重新生成近似文本，避免删除后再添加导致 claim、术语、数值或语气漂移。
- 只有在用户明确同意时，才能把正文中的图表、公式、算法、case、proof 或大段内容移动到 appendix/supplement；移动前必须说明会移动什么、为什么、对主文证据链有什么影响。
- 首页 title、`\maketitle`、匿名 author block、title 下方、author block 上下方、abstract 前的模板预留区域不能用负 `\vspace` 压缩。很多匿名投稿模板会给非匿名版本作者列表预留空间；submission 里即使显示 Anonymous，也必须保留官方模板的作者区域版式。压掉这块空白属于破坏模板规范，可能触发 desk reject。
- 阶段1不改论文正文、claim、实验数字、表格数据、公式含义、引用意图或 conclusion。
- 阶段1可调整 float、equation、table 的位置、大小、跨栏形式和 LaTeX 包装方式；这些调整必须服务排版，不改变内容。
- 不为了压页删除数据、实验、图片、表格、公式、算法、图表证据、重要 citation 或方法定义。
- 所有“写满页面”“减少大空隙”“最后一行超过半行”“短尾修正”的要求都只看 references 之前的正文；references、appendix 和 supplement 不适用正文压行标准。若目标 venue 将 references 计入总页数，仍需遵守总页数，但不要为了 references 的视觉短尾改全局版式或非合规 bibliography style。
- 不在用户未授权时 commit 或 push；可以用 git diff 做检查，但不要把阶段性调整提交成历史。
- 如果目标模板规则不明确，先查看官方 author kit、sample paper、submission checklist 和页数/匿名/补充材料要求，不凭印象猜。

## 阶段0：投稿要求检索备忘

开始改模板前，必须先通过 web search 详细核对目标会议/期刊的最新投稿要求，并写成 Markdown 备忘。不要只看旧论文、旧模板或本地印象；规则可能每年变化。

优先检索和记录官方来源：

- Venue 官网 author instructions、call for papers、submission guidelines、camera-ready/submission checklist。
- 官方 author kit、LaTeX template、README、sample paper、`.cls`/`.sty` 说明。
- OpenReview、CMT、Microsoft CMT、HotCRP、PCS 或期刊系统里的正式 submission instructions。
- 官方 FAQ、ethics/checklist/data availability/code availability/reproducibility policy。
- 官方关于 supplement、appendix、anonymous code/data、external link、AI disclosure、dual-use、conflict of interest 的说明。

必须确认的要求：

- 模板版本、官方下载链接、compiler 要求、单栏/双栏、字号、页边距、行号、页眉页脚、匿名开关。
- 主文页数限制，references 是否计入页数，appendix/supplement 是否单独提交，ethics/limitations/checklist 是否计入页数。
- 是否需要额外 PDF，例如 checklist PDF、ethics checklist、reproducibility checklist、supplement PDF、source zip、author response 文件。
- 匿名规则：single/double blind、作者信息、acknowledgement、funding、self-citation、external links、code/data links、PDF metadata、source zip 注释和文件名。
- 文件格式：PDF 版本、字体嵌入、最大文件大小、source 是否必须上传、supplement 文件数量和命名要求。
- Bibliography/style：`.bst`/BibLaTeX 要求、citation style、references 是否可超页、是否允许压缩 bibliography。
- Desk-reject 风险：非匿名、模板不合规、页数超限、缺 checklist、缺 ethics statement、缺 line numbers、外链泄漏身份、字体/页边距/行距改动。

将结果写入项目内可追溯的备忘文件，例如 `build/template-migration/notes/submission-requirements.md`。不要放在系统 `/tmp`；如果只是临时存放，任务结束前要清理或移动到项目内。

备忘模板：

```markdown
# Submission Requirements Memo

## Target Venue

- Venue:
- Track:
- Submission stage:
- Deadline/version date:
- Access date:

## Official Sources

| Source | URL | What It Confirms | Notes |
| --- | --- | --- | --- |
| Author instructions | [URL] | page limit, anonymity, checklist | |
| Author kit | [URL] | LaTeX class/style/template version | |
| Submission system | [URL] | required files, PDF/source upload | |

## Requirements Checklist

| Requirement | Confirmed Rule | Source | Action Needed | Status |
| --- | --- | --- | --- | --- |
| Template version |  |  |  | TODO |
| Main text page limit |  |  |  | TODO |
| References count toward limit |  |  |  | TODO |
| Appendix/supplement policy |  |  |  | TODO |
| Checklist PDF required |  |  |  | TODO |
| Ethics/limitations required |  |  |  | TODO |
| Anonymous author block |  |  |  | TODO |
| External links policy |  |  |  | TODO |
| Code/data link policy |  |  |  | TODO |
| PDF metadata/source zip anonymity |  |  |  | TODO |
| Line numbers/header/footer |  |  |  | TODO |
| File size/source upload |  |  |  | TODO |

## Open Questions

- [ ] Requirement:
  - Why unclear:
  - Proposed handling:
  - Need user confirmation:
```

如果 web search 找不到官方答案，必须在 memo 的 Open Questions 里记录，不要猜。对会导致 desk reject 的未知项，先问用户或保守处理。

## 启动前清点

- 确认源工程入口：主 `.tex`、`bib`、figures、tables、appendix/supplement、custom `.sty`、Makefile 或 latexmk 配置。
- 确认目标模板：官方 author kit、`.cls`、`.sty`、sample `.tex`、bibliography style、compiler 要求、单双栏、匿名设置和页数限制。
- 确认投稿阶段：submission、camera-ready、journal revision 或 arXiv。若是 submission，默认执行全匿名检查；若用户没有明确说明，按匿名投稿处理。
- 清点源版本正文内容：section 输入文件、`\includegraphics`、`figure`/`table`/`equation`/`align`/`algorithm` 环境、关键 footnote、appendix/supplement 引用和 bibliography。后续每个阶段都用这份清单检查有没有丢失。
- 先编译源版本，保存源 PDF 页数、日志和可视化截图；源版本不能编译时，先记录原因，再决定是否先修源工程。
- 保留一份目标模板官方原件目录，用于后续 `diff -ru` 检查模板文件是否被改。
- 尽量把输出放入项目内可清理的 build 目录，例如 `build/template-migration/`，不要把中间文件散在源码目录。

常用基线命令：

```bash
git status --short
rg -n "\\\\input|\\\\include|\\\\includegraphics|\\\\begin\\{figure\\*?\\}|\\\\begin\\{table\\*?\\}|\\\\begin\\{equation\\*?\\}|\\\\begin\\{align\\*?\\}|\\\\begin\\{algorithm\\*?\\}|\\\\footnote|\\\\bibliography|\\\\printbibliography" .
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/source paper.tex
pdfinfo build/source/paper.pdf | sed -n '1,80p'
pdftoppm -png -r 180 build/source/paper.pdf build/source/page
```

如果项目使用 `xelatex`、`lualatex`、`bibtex`、`biber` 或官方脚本，以目标模板要求为准。

## 匿名投稿安全检查

匿名检查优先级高于排版美观。只要是投稿版本，先保证不会泄漏身份，再处理页数和视觉细节。
投稿版默认全匿名：源版本是否公开、是否有作者、是否含项目链接，都不能作为 submission 保留身份信息的理由。

必须移除或匿名化：

- `\author{...}`、`\affiliation{...}`、`\institute{...}`、`\email{...}`、`\orcid{...}`、`\thanks{...}` 中的真实身份。
- Acknowledgement、funding、grant number、project name、lab name、institution name 和 internal system name。
- 个人主页、项目主页、GitHub、Hugging Face、demo、video、leaderboard、dataset page、supplement download、Google Drive、Dropbox、OSF、Zenodo 等外部链接。
- PDF metadata 中的 author、creator、subject、keywords、producer 之外的身份信息。
- 文件名、图片名、注释、supplement 路径、附录标题中能暴露团队或项目身份的内容。
- “our previous work”“we previously released”“we build on our benchmark”“as proposed by us”“in our earlier paper” 这类一眼能暴露自引身份的表达。

允许保留：

- 目标模板要求的匿名占位，例如 `Anonymous Author(s)`、`Anonymous Institution` 或官方 `anonymous` option。
- 正常的第三人称引用，例如 `Smith et al. introduced ...`，即使该论文实际来自作者团队，也不要暗示这是自己的工作。
- 参考文献条目本身，除非目标 venue 明确要求匿名化尚未公开的 submission、code、data 或 supplemental material。

匿名检查命令：

```bash
rg -n "\\\\author|\\\\affiliation|\\\\institute|\\\\email|\\\\orcid|\\\\thanks|acknowledg|funding|grant|homepage|project page|github|huggingface|demo|video|leaderboard|our previous|we previously|our earlier|as proposed by us|we released|we build on our|http://|https://|\\\\url\\{|\\\\href\\{" .
pdfinfo build/target/paper.pdf | sed -n '1,80p'
```

处理原则：

- 对身份字段，使用目标模板的匿名开关或匿名占位，不要手写真实信息。
- 对外部链接，submission 版本默认删除链接和 URL；如必须说明资源，将其改成匿名提交系统允许的描述，并让用户确认。
- 对自引表述，改为第三人称普通相关工作描述，不改变技术 claim。
- 对尚未公开或会暴露身份的 code/data，写成“will be released upon acceptance”这类 venue 允许的中性表达；如果 venue 禁止该表述，按 venue 规则删除。
- 对注释和源码内部路径也要检查，因为部分投稿系统可能要求上传 source zip。

## 阶段1：只换模板

阶段1的验收目标是“模板 B 下排版正常”，不是“页数已经合格”。
阶段1还必须做到内容完整：文本、图片、表格、公式、算法、case、proof、关键脚注和引用都不能少。

执行顺序：

1. 用目标模板 sample 作为骨架，迁移 title、author block、abstract、sections、bibliography、appendix 和必要宏定义。
2. 替换 `\documentclass`、conference/journal option、bibliography style、`\maketitle`、appendix/supplement 入口等模板相关结构。
3. 优先复用源工程的正文文件，例如 `\input{sections/introduction}`，减少手工复制正文导致的误改。
4. 对单双栏转换做排版适配：`figure`/`table` 与 `figure*`/`table*` 按目标模板切换，宽图和宽表优先用跨栏环境。
5. 对公式做宽度适配：长公式可用 `aligned`、`split`、`multline` 或局部缩放，但不能改变数学含义。
6. 对表格做宽度适配：优先调整 `tabcolsep`、字号、列宽、`resizebox`/`adjustbox`，不要删列、删数据或改数字。
7. 对图片做宽度适配：单栏通常用 `0.95\linewidth` 到 `\linewidth`，跨栏通常用 `0.85\textwidth` 到 `\textwidth`，以不越界和清晰为准。
8. 对照启动前内容清单，确认目标模板下仍包含全部正文 section、图片、表格、公式、算法、case/proof、关键脚注和引用。
9. 编译到无错误，排查 undefined refs/citations、missing figures、overfull boxes、float too large 和 bibliography 错误。
10. PDF 转图片逐页检查：无文字重叠、无图表越界、无公式截断、无图表缺失、无异常大空白、无作者信息、无外部链接、无标题/页眉错误。

阶段1允许做的排版调整：

- 移动图、表、公式或算法块在源码中的相对位置，使其靠近首次正文引用并减少空隙。
- 调整 `figure`、`table`、公式、算法、caption 和子图的尺寸。
- 切换单栏/双栏 float 环境。
- 调整局部 float placement，例如 `[t]`、`[tb]`、`[!t]`。
- 增加必要的 template-compatible 包装命令，例如 `\centering`、`minipage`、`subfigure`、`resizebox`。

阶段1禁止做的内容调整：

- 改写段落、句子、摘要、conclusion 或 related work。
- 改实验结果、数据、指标、模型名、表格数值或 caption 含义。
- 删除图片、表格、公式、引用、脚注、算法、case、proof、appendix/supplement 指针或正文 section。
- 改目标模板官方 `.cls`、`.sty` 或官方 sample 的模板文件。

阶段1 diff 检查：

```bash
git diff --check
git diff --stat
git diff --word-diff -- '*.tex'
diff -ru target-template-pristine/ target-template-current/ || true
rg -n "\\\\includegraphics|\\\\begin\\{figure\\*?\\}|\\\\begin\\{table\\*?\\}|\\\\begin\\{equation\\*?\\}|\\\\begin\\{align\\*?\\}|\\\\begin\\{algorithm\\*?\\}|\\\\footnote|\\\\cite" .
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
- 不允许：正文 prose 改写、数字变化、claim 变化、citation 意图变化、图片/表格/公式/算法丢失、公式等价性无法确认的改写。
- 如果必须改文字才能适配模板要求，例如匿名作者信息或 mandatory statement，单独记录，不和正文改写混在一起。
- 如果修改文字是为了匿名化，例如删除作者、外链、acknowledgement 或自引暗示，这属于投稿安全改动；必须单独列出，不计入正文内容优化。

## 页数判断

阶段1完成后再判断页数。先确认目标要求：

- 主文页数限制：例如 8 页、9 页、12 页。
- References 是否计入页数。
- Appendix/supplement 是否单独提交。
- Camera-ready 与 submission 页数是否不同。
- 匿名信息、ethics、limitations、checklist、acknowledgement 是否计入主文。

页数目标：

- 正文在目标页数内尽量写满，不留明显空白；这里的正文指 references 之前的内容。
- 正文最后一页最后一行应尽量接近页面底部；references 页不需要按这个标准处理，可以自然结束。
- References 的长短由真实引用数量和目标模板 bibliography style 自然决定，不作为正文填充或正文压缩对象。
- 如果少很多页，不要靠废话填充；需要询问用户是否补实验、补分析、把 supplement 内容移入正文或调整论文结构。

判断命令：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/target paper.tex
pdfinfo build/target/paper.pdf | rg '^Pages:'
pdftoppm -png -r 180 build/target/paper.pdf build/target/page
```

## 阶段2：不改文字压缩

如果超页，阶段2只做排版压缩，不改正文文字。
阶段2仍必须保留正文中的图片、表格、公式、算法和关键证据；压缩只能改变排版位置、尺寸和间距，不能删除内容。
实验图表和表格仍按正文证据处理：main result、ablation、setting、comparison、analysis table 应保持 table 环境和可读结构，不能改成正文句子、普通列表或压缩到无法核对数字的形式。

优先顺序：

1. 调整 float 位置，减少单独占页和大块空白。
2. 合并或压缩图表布局，例如多子图横排、宽图跨栏、表格跨栏或单栏重排。
3. 微调图表尺寸，但保证坐标轴、legend、数字和文本可读。
4. 局部使用 `\vspace` 压缩图表上下空白；适当的小幅 `vspace` 是允许且有益的，可以减少模板迁移后的松散空白、提高正文信息密度，但不能造成肉眼可见的过度压缩、重叠、可读性下降或模板违规。
5. 调整 caption spacing、`tabcolsep`、`arraystretch`、列表间距和算法块间距。
6. 检查 bibliography 样式是否按目标模板要求，不能私自改成更短但不合规的格式。

`vspace` 使用规则：

- 把适度局部 `vspace` 视为正常排版工具，不要把所有负 `\vspace` 都当作风险；风险来自肉眼可见的过紧压缩、内容相撞、读者难读或破坏模板结构。
- 只在明确的大空隙处局部使用，例如 figure 前后、caption 后、section 前后。
- 每处改动尽量小，例如 `-0.2em`、`-0.4em`、`-0.6em`；避免连续堆叠大负值。
- 每次加完都重新编译并可视化检查上下文，不允许文字、caption、图表互相压住。
- 不修改目标模板 `.cls` / `.sty` 中的全局 spacing。
- 不修改全文行距、正文字体、页边距、正文 text block 或全局字号；压缩只能做局部 float、caption、table、list、algorithm 间距调整，不能动模板敏感项。
- 不在首页 title、`\maketitle`、匿名 author block、title 下方、author block 上下方或 abstract 前使用负 `\vspace`。这块空白通常是投稿模板为非匿名作者列表预留的结构空间，不是普通可压缩空白；submission 版本也应保留官方模板版式。

阶段2验收：

- 页数减少或空隙减少。
- 没有文字重叠、图表越界、caption 撞图、页脚撞内容。
- `git diff --word-diff -- '*.tex'` 中没有正文文本改写。
- 内容清单数量和位置合理：图片、表格、公式、算法、case/proof 没有缺失，除非用户明确同意移动到 appendix/supplement。

## 阶段3：轻微文字压缩

如果排版压缩后仍超页，才进入文字压缩。
阶段3也不能删除正文图表、公式、算法和关键证据；只能压缩对正文信息量影响极小的文字表达。

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
- 把实验表格、主结果表、消融表、超参表、对比表或分析表改写成 prose、bullet list 或纯文本摘要。
- 图片、表格、公式、算法、case、proof 和支撑核心 claim 的多模态证据。
- 主要 claim、contribution、limitation 和 conclusion 的实质内容。
- 会改变审稿人理解的定语、边界条件或风险控制表述。

文字压缩流程：

1. 每次只压一个局部区域，例如一个 caption、一张表、一个段落。
2. 用 `git diff --word-diff` 复核没有改变 claim 或数据。
3. 编译并检查页数和视觉效果。
4. 记录压缩来源，例如 caption、table header、method detail。
5. 如果后续需要补回被删或被压缩的文字，先从源论文、源 LaTeX、原始 arXiv/技术报告或用户提供原稿中复制第一手文本，再做最小必要适配；不要直接新写一段替代文本。

## 阶段4：仍超页时询问

如果仍然超出太多，不要继续硬压。

需要向用户说明：

- 当前目标页数、当前页数、超出多少。
- 阶段2已经做过哪些不改文字压缩。
- 阶段3已经压缩了哪些低风险文字。
- 继续压缩会伤害哪些内容或证据。

可询问用户选择：

- 将部分图表、算法、case、proof、implementation detail 移到 supplement。
- 删除或合并低优先级实验。
- 把 supplement 中更重要的内容移入正文，同时删除正文低价值内容。
- 调整论文结构或重新确定投稿目标。

## 阶段5：压行和最终美观

内容和页数合格后，再做最终压行。

检查目标：

- references 之前的正文段落最后一行尽量超过半行。
- 避免一行只有几个单词或一个短短 citation。
- 避免图表页前后出现大块空白。
- 避免 section 标题孤立在页底。
- 避免公式单独撑出大片空白。
- 不检查 references 的最后一行、参考文献条目短尾或 bibliography 区域空隙；这些自然由模板和 `.bst`/BibTeX/BibLaTeX 控制。

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
- submission 版本首页、页眉、脚注、PDF metadata 和 source zip 是否完全匿名。
- 首页 title/author/abstract 前后的空白是否来自官方模板；不要把匿名 author block 的预留空间当作普通空白压掉。
- 全文没有改全局行间距、正文字体、页边距、正文 text block、模板字号或 bibliography style 来压缩空间。
- 双栏正文是否有跨栏图表压住文字。
- 单栏转双栏后公式是否越界。
- 宽表是否可读，表格线和数字是否清楚。
- 图片是否清晰，子图标签是否可见。
- 源版本中的图片、表格、公式、算法、case/proof 是否都仍在正文或经用户同意后移动到 appendix/supplement。
- 页眉、页脚、页码、line number、匿名标记是否符合投稿阶段。
- references、appendix、supplement 起止位置是否符合要求。

## 阶段6：逐页 Desk-Reject 风险审计

最终交付前，必须逐页查看渲染后的 PDF 图片，并写 `page-risk-audit.md`。这不是泛泛浏览，而是按页填满风险表：每一页是一行，每个风险维度都要写 `OK`、`N/A` 或具体风险描述。

建议先渲染每一页：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/target paper.tex
mkdir -p build/template-migration/pages build/template-migration/notes
pdftoppm -png -r 180 build/target/paper.pdf build/template-migration/pages/page
pdfinfo build/target/paper.pdf | rg '^Pages:'
```

逐页审计文件建议写入 `build/template-migration/notes/page-risk-audit.md`。如果项目已有专门的 migration notes 目录，可放入该目录，但路径必须在最终说明里写清楚。

审计模板：

```markdown
# Page Risk Audit

## Build Info

- PDF:
- Render command:
- Page count:
- Target venue:
- Submission stage:
- Requirements memo:
- Audit date:

## Global Risks

| Risk | Check Method | Result | Action |
| --- | --- | --- | --- |
| PDF metadata contains author or private info | `pdfinfo` and source inspection | TODO | TODO |
| Source zip contains private comments, paths, or filenames | `rg` / archive inspection | TODO | TODO |
| Global line spacing, body font, margin, or text block changed | diff preamble and template files | TODO | TODO |
| Official class/style/template files modified | `diff -ru pristine current` | TODO | TODO |
| Required checklist/supplement/source files missing | compare with requirements memo | TODO | TODO |

## Per-Page Risk Table

| Page | Non-anonymous info | Identity/link leak | Header/footer/line no. | Over-tight compression | Text/figure overlap | Figure/table overflow | Formula overflow | Missing/low-res evidence | Main-body blank/short-tail | Template-sensitive region | Action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
| 2 | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TODO |
```

风险列填写规则：

- `Non-anonymous info`：作者、单位、邮箱、ORCID、funding、acknowledgement、项目名、个人主页、文件名泄漏。
- `Identity/link leak`：GitHub、Hugging Face、project page、demo/video、OpenReview 外链、匿名性不足的数据下载地址、自引身份暗示。
- `Header/footer/line no.`：页眉、页脚、页码、line number、anonymous marker、submission id 是否符合 memo。
- `Over-tight compression`：局部负 `\vspace` 过度、caption 和正文贴太近、表格字号不可读、图例或轴标签过小。适度局部 `vspace` 本身不是问题；只有肉眼可见过紧或影响阅读时才标为风险。
- `Text/figure overlap`：正文、标题、caption、图表、脚注、页脚之间是否重叠或遮挡。
- `Figure/table overflow`：图表是否越过正文边界、裁切、压到边栏、跨栏位置异常。
- `Formula overflow`：公式是否越界、截断、压住编号或破坏双栏。
- `Missing/low-res evidence`：源稿中的图表、表格、case、算法、proof 是否缺失，图片是否糊到无法审稿。
- `Main-body blank/short-tail`：仅针对 references 之前正文；是否有明显大空白、孤立 section 标题、正文段落短尾。
- `Template-sensitive region`：首页 title/author/abstract 预留区、页边距、行距、正文字体、模板全局版式是否有被压缩的迹象。
- `Action`：如果无风险写 `None`；如果有风险，写最小修复动作和复查状态。

修复规则：

- 只对标记为风险的页做最小必要调整；一次只修一个页面或一个风险。
- 优先微调 float 位置、局部图表尺寸、caption/table spacing、局部 `tabcolsep`、局部 `arraystretch`、局部段落压缩。
- 每次只调一点点，立即编译、重新渲染对应页面、更新 `page-risk-audit.md`。
- 严禁大版面调整：不改全局行距、正文字体、页边距、正文 text block、模板 class/style、首页 author 预留区。
- 如果一个调整影响多页，必须回看受影响页面并更新表格；不要只看原风险页。
- 如果风险来自目标规则不明确，回到 `submission-requirements.md` 的 Open Questions，不要猜。
- 持续迭代直到 `Per-Page Risk Table` 中没有具体风险描述，只剩 `OK`、`N/A` 或 `None`。

## 最终交付检查

- `latexmk` 无 fatal error。
- 关键 warning 已排查，剩余 warning 不影响投稿 PDF。
- `submission-requirements.md` 已完成，所有关键要求有官方来源或明确 Open Question。
- `page-risk-audit.md` 已完成，每一页和每个风险维度都填过，所有 desk-reject 风险已消除或明确交给用户确认。
- 投稿版本已通过匿名检查：无作者、单位、邮箱、acknowledgement、funding、外部链接、项目链接和自引身份暗示。
- 目标模板官方文件与 pristine copy 对比无非预期改动。
- 阶段1文字 diff 和内容清单已确认没有正文语义改动，也没有丢失图片、表格、公式、算法、case/proof、关键脚注或引用。
- 实验部分的主结果、消融、设置、对比和分析表仍保留表格形态；相关图表没有被删除、散文化或未经用户同意移动到 appendix/supplement。
- 若发生过文字删除、压缩后回填或匿名化后恢复，已确认回填文本来自源论文/源 LaTeX/原始版本/用户原稿，而不是重新生成的近似文本。
- 首页 title、`\maketitle`、匿名 author block 和 abstract 前区域没有用负 `\vspace` 压缩，保留目标投稿模板的官方首页结构。
- 最终 PDF 页数满足目标要求，并尽量写满 references 之前的正文最后一页；references 不要求最后一行占满，不用按正文短尾标准修。
- PDF 转图片逐页检查通过；正文区域没有重叠、越界、异常空白和短尾明显问题。
- 生成物、中间文件和 build 缓存没有污染源码目录。
- 最终说明中列出：使用的目标模板、编译命令、页数、主要排版调整、是否发生文字压缩、仍需用户确认的问题。
