# 通用 LaTeX 论文模板

这是一套可独立编译的技术报告与论文初稿工程，覆盖本 skill 中适用于 LaTeX 成稿的写作、排版、图表、引用和附录技巧。默认单栏，保留 `paper.tex`、`sections/`、`figures/`、`figures/cases/`、`figures/logos/`、`seed/` 的相对目录结构；文件名、作者、机构、任务内容与图表均已通用化。

正文中的 `[占位内容]`、`TBD`、表格色阶、排名标记和示意图几何仅展示写法，不是实验结果。四条已核实的论文引用用于测试 BibTeX、引用位置和模型 logo 宏，不代表完整 Related Work 或模型评测。

## 文件与使用入口

```text
latex-paper-template/
  paper.tex                       # 主入口、作者、摘要、资源链接和可选开关
  generic_report.cls              # 首页、标题、页眉、目录、浮动和单双栏衔接
  main.bib                        # 四条真实引用示例，按论文实际来源替换
  sections/
    1-introduction.tex            # 六段式 Introduction 与 compactitem 贡献
    2-related-work.tex            # 分类与差异、能力对比、引用
    3-method.tex                  # 形式化定义、数据构造、质量控制与评测
    4-experiments.tex             # 主表、消融、分析、双案例
    5-conclusion.tex              # 问题、贡献、证据和未来方向
    appendix.tex                  # 设置、prompt、补充结果、完整案例、宏预览
  figures/
    teaser.tex                    # 场景、输入输出、challenge、方法和 finding
    pipeline.tex                  # 构造、验证、推理、评测与反馈流程
    component.tex                 # 独立技术核心与约束分支
    analysis.tex                  # 三联分析布局，无观测数据
    cases/
      comparison.tex              # 主文两个压缩案例
      example.tex                 # 通用证据图的独立 LaTeX 源文件
      example.pdf                 # 附录可直接 includegraphics 的矢量图
    logos/
      page-logo.pdf
      github-logo.pdf
      hf-logo.pdf
      models/                     # 10 款模型 provider PNG
  seed/
    theme.tex                     # 主题色、染色/方向/属性宏、可换页 case box
    model-logos.tex               # 与 reference 一致的 provider 宏和 ModelRef
```

- **复制**：复制整个模板目录到论文项目，再修改其中的主文件、章节和图像。不要只拷贝 `paper.tex`。
- **定位技巧**：先按下表找到实际示例，再阅读对应 reference；模板已定义的宏不要重复 `newcommand`。
- **投稿**：这是自定义 report 样式。正式会议或期刊投稿应切换为目标 venue 的官方 class，并核对当届页数、匿名、图表和补充材料要求。

## 编译与可选配置

需要 TeX Live 的 `latexmk`、`pdflatex`、BibTeX 及源文件加载的常用宏包。Debian/Ubuntu 可使用 `texlive-latex-extra`、`texlive-fonts-recommended`、`cm-super`；已有环境满足依赖时直接编译。

从模板目录执行，输出与 TeX 缓存隔离到 `build/`：

```bash
mkdir -p build
TEXMFVAR=build/texmf-var TEXMFCONFIG=build/texmf-config latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build paper.tex
```

结果为 `build/paper.pdf`。默认配置已实际编译并逐页检查；双栏、可选字体、关闭目录和关闭宏预览的组合也经过独立编译。检查日志中的 `Overfull`、未定义引用、字体替换和错误；最终交付前将 PDF 渲染为图片复核。

| 配置 | 修改位置 | 行为 |
| --- | --- | --- |
| 单栏 / 双栏 | `paper.tex` 的 `documentclass` | `generic_report` 为单栏；增加 `twocolumn` 后，封面、Abstract、目录和附录仍为整页，主文使用双栏。 |
| 可选目录 | `showcontentstrue` / `showcontentsfalse` | 长报告可保留，短稿可关闭。 |
| 宏预览附录 | `showgallerytrue` / `showgalleryfalse` | 展示全部 10 款 logo、染色包装宏和方向/属性符号；真实投稿稿关闭。 |
| 可选字体 | `usealternatefontsfalse` / `usealternatefontstrue` | 默认 TeX 字体；启用后使用 TeX 提供的 Helvetica 标题字体。未捆绑许可不明的字体文件。 |
| 主题 | `seed/theme.tex` | 调整主题、表格色阶与 case box；同一张结果表保持统一归一化尺度。 |
| 图表浮动 | `widefigure` / `widetable` 与 `[htbp]` | 单栏时使用普通浮动，双栏时使用跨栏浮动；正文通过标签引用，避免图表先于其来源位置。 |

通用证据图已打包为 PDF，正常编译无需额外步骤。修改其源图后可重建：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build/case figures/cases/example.tex
cp build/case/example.pdf figures/cases/example.pdf
```

## 技巧覆盖清单

表中每项都能定位到模板文件、实际排版或源文件注释。Markdown 专属的中文大纲、blockquote 绘图说明与 GitHub fenced math 属于成稿前的规划阶段；按原 reference 使用，不把 Markdown 语法混入 `.tex`。

| 技巧与检查点 | 模板中的落点 | 对应 skill 内容 |
| --- | --- | --- |
| 中心命题、2–3 词包装词、问题到证据闭环 | `CoreTerm`、Introduction 注释与本页 story 矩阵 | `SKILL.md`；`markdown-story-outline.md` |
| 四类论文路由 | `paper.tex` 路由注释；按目标保留 Method、Data、Agent、Training 内容 | `SKILL.md` 的论文类型路由 |
| 六段式 Introduction、3–5 点平行贡献 | `sections/1-introduction.tex`，实际使用 `compactitem` | `markdown-section-snippets.md`；`latex-layout-and-contribution.md` |
| 3 个 challenge 与相同顺序的方法响应 | Introduction 第三、四段；Method 总览 | `SKILL.md` 的 Challenge 命名与 Method |
| Related Work 3 类小节、每类两段、正向限定差异 | `sections/2-related-work.tex` | `SKILL.md`；`markdown-section-snippets.md` |
| BibTeX、紧贴对象的引用、文本式引用、模型引用 | `main.bib`、`citep`、`citet`、`ModelRef` | `latex-citation-report-style.md`；`latex-model-logos.md` |
| 一段摘要、无 citation、Abstract 内平台资源 logo | `paper.tex` 与 `generic_report.cls` | `latex-citation-report-style.md` |
| 统一主题、title 横线、无机构页眉、摘要框、目录、作者机构与元信息 | `generic_report.cls`、`seed/theme.tex`、`paper.tex` | `latex-citation-report-style.md` |
| 场景 / 输入输出 / challenges / 方法 / finding teaser | `figures/teaser.tex` | `markdown-story-outline.md`；`markdown-figures-tables-cases.md` |
| 能力对比表、full/partial/no、Ours 最后一行 | Related Work 的 `tab:coverage`；符号含义写在 caption | `latex-table-macros.md` |
| 模型输入输出、目标、约束与评测函数的轻量形式化 | Method 的 `eq:formulation` 与变量解释 | `markdown-section-snippets.md`；`SKILL.md` |
| 构造到推理/训练、验证、评测、反馈、输出 pipeline | `figures/pipeline.tex` | `SKILL.md`；`markdown-figures-tables-cases.md` |
| 与 pipeline 区分的组件或算法机制图 | `figures/component.tex` | `SKILL.md` 的 Method 图表要求 |
| 数据来源、难度、生成验证、去重/泄漏/人工审计/修复 | Method 的构造与质量控制段；`tab:distribution` | `SKILL.md` 的 Data And Benchmark |
| 评测定义、invalid、预算、重试缓存、baseline 公平性 | Method 评测段；附录 `tab:settings`、prompt 和 parser listings | `SKILL.md` 的 Evaluation |
| 主指标、子指标、invalid/error rate、模型 logo 第一列 | `tab:main-results`；`seed/model-logos.tex` | `latex-table-macros.md`；`latex-model-logos.md` |
| ScoreCell / BestScore / SecondScore / DimCell / 归一化强度 | `seed/theme.tex`；主表、消融和宏预览 | `latex-table-macros.md` |
| 文本上下箭头、克制 rowcolor、可缩放表格 | 主表 `adjustbox`、`MetricUp/MetricDown`、分组行 | `latex-table-macros.md` |
| 组件消融与 validation/feedback 消融 | `tab:component-ablation`、`tab:validation-ablation` | `SKILL.md` 的 Experiments |
| 2–3 个分析图与 paragraph Insight、结果/解释两段 | `figures/analysis.tex`；Experiments 的三个 Insight | `latex-appendix-cases.md`；`SKILL.md` |
| 主文两个压缩 case、真实案例字段与附录链接 | `figures/cases/comparison.tex`；Case Study 正文 | `markdown-figures-tables-cases.md` |
| 设置 / 超参数 / prompt / parsing 优先，补充结果其次 | 附录 A、A.1 和 B | `latex-appendix-cases.md` |
| 完整 case 的 Meta / Task / Data / Rubrics / Report / Figures / Score / Diagnosis | 附录 C、D；`ReportCaseBox`、`CaseSection` | `latex-appendix-cases.md` |
| 长 case 换页与 continuation、图片短标题、detokenize 路径 | `ReportCaseBox` 的续页标题、Case A 的 `includegraphics` | `latex-appendix-cases.md` |
| 全部 10 款 provider wrapper、统一高度基线 | `seed/model-logos.tex` 与附录宏预览 | `latex-model-logos.md` |
| 一段 Conclusion、局限与未来方向、无新证据 | `sections/5-conclusion.tex` | `SKILL.md`；`markdown-section-snippets.md` |
| 标签导航、浮动边界、段末短尾、四轮终审 | 所有图表的 label/ref；下方最终检查 | `latex-layout-and-contribution.md`；`SKILL.md` |

## 写作与最终检查

先填 story 矩阵，再写正文；不能映射到设计和证据的 challenge 应删除或补证据。

| 核心问题 | 方法设计 | 指标 | 实验发现 | Case / Analysis |
| --- | --- | --- | --- | --- |
| [Challenge A] | [Component A] | [Metric] | [Verified result] | [Case / figure] |
| [Challenge B] | [Component B] | [Metric] | [Verified result] | [Case / figure] |
| [Challenge C] | [Component C] | [Metric] | [Verified result] | [Case / figure] |

- **选择路由**：Benchmark/Data 强调定义、覆盖和质量；Method 强调机制和消融；System/Agent 强调模块、恢复和端到端证据；Training/Data-loop 强调监督、奖励、超参数和稳定性。示例全集用于选取与改写，不要求真实论文保留所有模块。
- **统一术语**：首次定义类别缩写，包装词在题目、摘要、方法、实验和结论承担不同功能；维护“正式术语 / 含义 / 禁用别名 / 证据位置”表，检查只出现一次的术语。
- **核实引用**：先核验原始来源，优先正式版本；实际 AI conference paper 按研究覆盖准备约 40–50 篇相关引用，不用无关或虚构条目凑数。logo 不能代替 citation。
- **替换结果**：模型名、数值、色阶、best/second、属性符号、曲线和案例全部按真实数据更新；正文解释观察和 insight，明确单位、分母、缺失值、无效率和不确定性。
- **检查完整性**：所有 figure、table、algorithm 和 appendix 都要有正文入口；完整案例不以节选替代。超长 case 分 box 或 continuation page。
- **检查语言**：每段一个主点，段首主题、段尾收束；贡献语法平行。用适用场景和协议限制 claim，避免无证据的“全面解决”或低层工程流水账。
- **按顺序审阅**：中心命题 → 对应关系 → 证据 → 可复现性 → 术语 → 必要形式化 → 章节/段落逻辑 → 语言。再检查 novelty、validity、baseline fairness、reproducibility、overclaim 风险。
- **四轮终审**：结构、对应、术语、证据。最终编译与逐页预览时，修复正文边界溢出、孤立标题和段末 1–3 词短尾；先调整浮动和相邻内容位置，保持 claim、caption 和数据准确。
