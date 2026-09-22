# 投稿模板转换项目说明

这是一个用于**论文投稿模板转换与版本维护**的项目仓库。

## 项目目标

`arxiv` 文件夹中存放论文的原始版本（LaTeX 格式）。严禁修改。

核心任务是：

> 基于 arXiv 版本论文内容，将文本、图片、表格等内容按照**最小且必要的修改原则**迁移到不同会议的投稿版本中。

例如：

- `submissions/ICLR_27`
- `submissions/ICML_27`

等目录中的对应投稿版本均需要保持 LaTeX 格式，并符合目标会议的官方投稿要求。

---

## 核心原则

### 1. 最小改动原则

模板迁移过程中：

- 尽可能保留原始论文（arxiv）的：
  - 文本内容
  - 图片
  - 表格
  - 公式
  - 实验结果
  - 章节结构
- 仅进行必要修改，包括但不限于：
  - 满足会议格式要求
  - 删除不允许出现的内容
  - 调整篇幅限制
  - 匿名化处理
  - 修改模板相关引用方式
  - 用户要求的表述修改
- 不同会议的投稿版本均应直接基于 arXiv 版本进行迁移和对齐，不应基于已有的其他投稿版本继续修改，以避免多次迭代导致内容偏移和版本漂移
- 避免进行非必要的内容重写
- 内容以 `arxiv` 版本为准，格式以目标会议官方模板为准：
  - 严禁因适配格式要求而修改 `arxiv` 版本中的内容表达
  - 严禁因内容调整或篇幅限制而修改投稿模板中的硬性格式规范

详细流程和具体要求请参考 `latex-template-migration` SKILL，后文将对此进行进一步说明。

---

## 文件夹结构

每个 `submissions` 子目录中通常包含：

```
submissions/
├── ICLR_27/
│ ├── latex/
│ ├── latex_build/
│ ├── latex_preview/
│ └── template/
├── ICML_27/
│ ├── latex/
│ ├── latex_build/
│ ├── latex_preview/
│ └── template/
└── ...
```

其中 `template` 文件夹存放对应会议官方 LaTeX 模板。

迁移时必须：

- 使用官方模板作为基础。
- 严禁修改模板中的硬性格式要求，包括但不限于：
  - 行间距
  - 页边距
  - 字体大小
  - 字体类型
  - 版式结构
- 检查官方模板的 Git commits，确保模板文件始终未被修改

`latex` 中存放你需要编辑的投稿版本的latex，可以使用必要的空间优化方案提高信息密度，例如：

- 减少不必要空白
- 优化图片尺寸
- 调整浮动体位置
- 合理压缩表格空间
- 删除冗余内容

但不得破坏会议规定的格式约束。

**Note**: 虽然部分会议投稿规范明确不建议或禁止使用 `\vspace` 等手动调整空间的方式，但在实际投稿过程中，可以在合理范围内使用其进行版面优化、减少不必要空白以及提升信息密度。需要注意：

- 不得出现文字、图片、表格之间的重叠；
- 不得造成过小的间距影响可读性；
- 最终版本应保持美观、清晰，并符合会议审稿阅读体验。

- `latex_build`：用于存放 LaTeX 编译生成的 PDF 文件以及编译过程中产生的中间产物。

- `latex_preview`：用于存放由编译完成的 PDF 转换得到的图片文件，用于进行可视化预览检查，并支持后续的循环迭代优化。

- `latex_build` 和 `latex_preview` 均属于临时生成目录，不纳入 Git 版本管理。

---

## 投稿规则调研要求

在进行任何模板转换前，需要先进行充分调研，确认目标会议最新一届投稿要求。

注意：

- 必须使用**当前届（current submission cycle）**的规则。
- 不允许直接使用往年的投稿要求，因为会议规则可能每年变化。

重点关注以下信息：

- 截稿时间
- 是否要求匿名（默认）或者半匿名（部分数据集类型工作可以不匿名）
- 投稿页数限制（page limit）
- reference 是否计入页面限制
- reference 格式要求
- 是否允许附录
- 是否允许 supplementary material
- supplementary material 数量和要求
- appendix 是否需要单独的pdf
- appendix 与 reference 的前后顺序
- appendix 是否有单独的模板
- appendix 单栏还是双栏
- 是否必须要有 limitations 等章节
- limitations 章节是否计入页面限制
- 是否必须要有 ethics impact 等说明章节
- 是否允许添加外部匿名链接（默认不允许添加外部匿名链接）
- desk reject 红线
- 是否需要 checklist
- 其他特殊投稿规则

将调研得到的投稿要求统一保存至 `submissions/*/rules.md`，并进行长期维护，确保后续模板迁移流程始终基于最新规则。

---

## 工具与规范

| 工具/规范 | 链接 | 用途 |
|---|---|---|
| agents-md-maintenance（必要） | https://github.com/black-yt/skills/blob/main/agents-md-maintenance/SKILL.md | 用于维护项目相关信息和维护文档 |
| latex-template-migration（必要） | https://github.com/black-yt/skills/blob/main/latex-template-migration/SKILL.md | 用于指导投稿模板转换的完整流程，是模板迁移的核心规范 |
| latex-compiling（必要） | https://github.com/black-yt/skills/blob/main/latex-compiling/SKILL.md | 用于编译 LaTeX 文件 |
| pdf-to-images（必要） | https://github.com/black-yt/skills/blob/main/pdf-to-images/SKILL.md | 用于将编译后的 PDF 转换为图片，并进行可视化检查 |

以上外部链接需要同步记录到项目维护文档中，避免后续流程中遗漏或遗忘。相关 SKILL 仅作为当前项目流程规范使用，无需安装到全局配置中。

> 本文件为固定要求，禁止修改。请你先阅读所有工具并初始化 `AGENTS.md` 和其他维护文档，随后开始正式工作。所有维护文档都是用中文。若仓库中已存在维护文档或部分产物，应在其基础上继续工作，复用必要的信息和成果，避免重复劳动。但无论现有维护文档和产物是否完全符合要求，后续所有新增、修改和维护工作均必须严格遵循上述规范。