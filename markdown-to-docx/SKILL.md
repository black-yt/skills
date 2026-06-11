---
name: markdown-to-docx
description: Use when converting Markdown documents into Microsoft Word .docx deliverables, including articles, reports, announcements, release notes, project documentation, image-rich explainers, meeting materials, and public-facing drafts that need embedded local images, captions, readable headings, Chinese/English typography, visible word counts, and a deterministic Python conversion workflow.
---

# Markdown to DOCX

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 1 | 说明 Markdown 转 DOCX 的使用边界和执行入口，覆盖依赖、`build_docx.py`/`count_visible_words.py` 参数、本地图片、caption、表格展开、公式降级、字体、输出检查和 `/tmp` 清理。 | Markdown to DOCX、Word、`.docx`、`python-docx`、`build_docx.py`、`count_visible_words.py`、images、caption、HTML img、tables、formula、font、word count、quality check | 触发本 skill 后默认读取；需要把 Markdown 交付为 Word 前；选择脚本参数前；处理图片/表格/公式前；检查 docx 字数、图片、caption 或格式问题前读取 | `SKILL.md` |
| 2 | 展开从零组织一份 Word 文档的内容工作流，说明 Markdown 材料如何拆成一级章节、图文块、居中图片、caption、目录结构、正文段落和可维护的分文件草稿。 | document workflow、section plan、Heading 1、image-text block、caption、table-to-text、directory structure、split draft、article、report、public draft、PR document | 从零规划 DOCX 文档结构前；把杂乱 Markdown/图片整理成正式 Word 前；需要拆分长文、组织图文块、重写一级章节或统一 caption 时必须读取 | [references/docx-workflow-and-structure.md](references/docx-workflow-and-structure.md) |

## 使用边界

- 核心技能是把 Markdown 文档转换成可交付的 Word `.docx`，不绑定某一种业务场景。
- 适合文章、报告、公告、release note、项目文档、说明书、会议材料、图文解读稿、官网/公众号草稿和对外沟通材料。
- 优先使用本 skill 的 `scripts/build_docx.py`，不要临时手写一次性转换脚本。
- 图片应是本地相对路径，推荐放在 Markdown 同级的 `images/` 目录。
- 不要依赖远程图片 URL；先下载到项目内再引用。
- 不要把生成文件长期放进 `/tmp`；临时测试可以放 `/tmp`，测试后必须清理。
- 如果用户要求严格保留复杂 Markdown 表格为 Word 网格表，本脚本不是最佳选择；它更适合把 Markdown 排成可读的 Word 文档和图文块。
- 如果用户要求企业模板、页眉页脚、封面、目录、编号样式、参考文献格式，应在脚本基础上扩展或使用 Word 模板驱动流程。

## 能力范围

输入能力：

- Markdown 标题、段落、粗体、斜体、inline code、链接。
- 无序列表、有序列表、嵌套列表。
- blockquote。
- fenced code block，按普通文本块进入 Word，不做语法高亮。
- Markdown 图片和 HTML `<img>` 图片。
- Markdown table，按“图文块”展开为 Word 正文结构。

输出能力：

- 生成独立 `.docx` 文件。
- 嵌入本地图片，而不是保留外链。
- 使用 Word 内置 `Title`、`Heading 1/2/3`、`Normal`、`List Bullet`、`List Number`、`Quote` 样式。
- 设置中英文都可读的标题/正文字体。
- 图片居中，caption 居中、小号、斜体。
- 链接按蓝色下划线显示。
- 可用脚本估算 Word 可见字数。

## 核心流程

1. 明确交付目标：
   - 普通图文文档：直接使用默认参数。
   - 中文正式文档：通常保留 `--body-font 等线 --heading-font 黑体`。
   - 英文文档：可改为 `--body-font Calibri --heading-font Arial`。
   - 图片密集文档：优先在 Markdown 中给 `<img>` 写 `width`。
2. 整理 Markdown 和图片：
   - `![Caption](images/a.png)` 可以直接生成图片和 caption。
   - `<p align="center"><img src="images/a.png" alt="Caption" width="360" /></p>` 可以控制图片宽度。
   - `alt` 文本会作为图片 caption。
   - 重复图片默认只保留第一次，避免正文和表格重复插图。
3. 转换为 DOCX：

```bash
python3 markdown-to-docx/scripts/build_docx.py /path/to/article.md -o /path/to/article.docx
```

4. 如需保留重复图片：

```bash
python3 markdown-to-docx/scripts/build_docx.py /path/to/article.md -o /path/to/article.docx --keep-duplicate-images
```

5. 检查可见字数：

```bash
python3 markdown-to-docx/scripts/count_visible_words.py /path/to/article.docx
```

6. 人工打开 `.docx` 检查：
   - 标题层级是否正确。
   - 图片是否全部出现。
   - caption 是否符合预期。
   - 链接是否以蓝色下划线显示。
   - 列表、引用、粗体、斜体是否可读。

完整示例：

```bash
python3 markdown-to-docx/scripts/build_docx.py ./draft.md \
  -o ./draft.docx \
  --base-dir . \
  --body-font "等线" \
  --heading-font "黑体" \
  --body-size 11 \
  --default-image-width 5.8

python3 markdown-to-docx/scripts/count_visible_words.py ./draft.docx
```

## 依赖

安装：

```bash
pip install python-docx markdown beautifulsoup4 lxml
```

检查：

```bash
python3 - <<'PY'
import bs4
import docx
import markdown
import lxml
print("ok")
PY
```

不要在共享环境中擅自安装或升级依赖；需要安装时先征得用户同意。若只是临时测试，优先使用当前项目已有环境或单独临时环境。

## 输入组织

推荐目录：

```text
document-project/
├── draft.md
├── draft.docx
└── images/
    ├── overview.png
    ├── pipeline.png
    └── result.png
```

路径规则：

- 默认情况下，图片相对路径以 Markdown 文件所在目录为基准。
- 如果 Markdown 和图片不在同一项目目录下，用 `--base-dir` 显式指定图片基准目录。
- 路径中尽量不要使用空格、中文标点和过长文件名。
- 不要引用上级目录里的大范围路径，例如 `../../...`；交付文档应能在单个项目目录中复现。
- 远程图片、base64 图片和本地绝对路径都不推荐作为 Markdown 输入。

## Markdown 写法

标题：

```markdown
# 文档标题
## 脚本参数

`scripts/build_docx.py`：

| 参数 | 必需 | 说明 |
| --- | --- | --- |
| `input` | 是 | Markdown 源文件。 |
| `-o, --output` | 否 | 输出 `.docx` 路径；默认与输入同名。 |
| `--base-dir` | 否 | 解析图片相对路径的目录；默认输入 Markdown 所在目录。 |
| `--keep-duplicate-images` | 否 | 保留重复图片，不跳过后续重复引用。 |
| `--body-font` | 否 | 正文字体，默认 `等线`。 |
| `--heading-font` | 否 | 标题字体，默认 `黑体`。 |
| `--body-size` | 否 | 正文字号，默认 `11`。 |
| `--default-image-width` | 否 | 未显式设置宽度时的图片宽度，单位英寸。 |

`scripts/count_visible_words.py`：

| 参数 | 必需 | 说明 |
| --- | --- | --- |
| `paths` | 是 | 一个或多个 `.docx` 文件。 |

统计说明：

- 英文按 token-like words 统计。
- 中文/中英混排按 CJK 字符数 + 英文 token 数，再乘以经验系数。
- 统计用于估算 Word 可见内容量，不等同于严格出版字数。

## 转换策略

标题策略：

- 文档只应有一个 `#` 主标题。
- 后续章节从 `##` 开始。
- 标题不要只靠加粗段落表达；使用真正 Markdown 标题，Word 里才有清晰层级。

图片策略：

- 每张重要图片都写清楚 `alt`，因为它会变成 caption。
- 宽图使用 `width="520"` 到 `width="580"`。
- 小图、流程图和示意图使用 `width="320"` 到 `width="460"`。
- 如果图片已经含有英文/中文标注，caption 不要重复图片里的完整句子，只写图的名称或作用。

表格策略：

- 如果表格是“解释型内容”，允许展开成图文块。
- 如果表格是“数据型内容”，不要默认用本脚本的展开策略；先确认用户是否接受。
- 数据表若必须保留网格，应该专门修改脚本，不要假装默认转换能保留复杂表格。

字数策略：

- `.docx` 生成后再估算字数，因为图片 caption、表格展开和 HTML 换行会影响可见内容。
- 中文稿用 `calibrated` 看大致篇幅。
- 英文稿用 `word_tokens` 看大致篇幅。
- 字数统计只是排版和投稿前的快速估算，最终以 Word / 目标平台统计为准。

## 质量检查

转换前：

```bash
python3 - <<'PY'
from pathlib import Path
import re

md = Path("/path/to/article.md")
base = md.parent
text = md.read_text(encoding="utf-8")
paths = re.findall(r'!\[[^\]]*\]\(([^)]+)\)|<img[^>]+src=["\']([^"\']+)["\']', text)
missing = []
for a, b in paths:
    src = a or b
    if src.startswith(("http://", "https://", "data:")):
        continue
    if not (base / src).exists():
        missing.append(src)
print("missing:", missing)
raise SystemExit(1 if missing else 0)
PY
```

转换后：

```bash
python3 markdown-to-docx/scripts/count_visible_words.py /path/to/article.docx
```

必须人工查看：

- Word 是否能正常打开。
- 图片是否被嵌入，不是外链。
- caption 是否重复或缺失。
- 表格展开是否符合文档阅读顺序。
- 中英文混排字体是否可读。
- 标题是否过密，是否需要拆段。
- 代码块是否因为长行影响可读性。
- 生成文件是否放在用户指定目录，而不是遗留在临时目录。

## 常见问题

- 图片缺失：确认 `--base-dir` 和 Markdown 图片路径是否一致。
- 图片重复：默认会跳过重复 `src`；需要全部保留时加 `--keep-duplicate-images`。
- 表格不像 Word 表格：这是预期行为，本脚本按图文块展开表格。
- 远程图片没有出现：先下载图片到本地项目目录，再使用相对路径。
- 字体不符合要求：用 `--body-font` 和 `--heading-font` 显式指定。
- 需要严格模板/页眉/页脚/参考文献样式：应在脚本基础上扩展，或改用 Word 模板驱动流程。
- Word 里图片太大：在 Markdown HTML 图片里写 `width`，或调低 `--default-image-width`。
- Word 里内容太挤：可以增大 `paragraph_format.space_after`，或拆分 Markdown 长段落。
- Word 里代码块不好看：这不是代码文档专用渲染器；需要代码高亮时应扩展脚本或使用 Pandoc/template 流程。
