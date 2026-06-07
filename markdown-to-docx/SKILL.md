---
name: markdown-to-docx
description: Use when converting Markdown documents into Microsoft Word .docx deliverables, including articles, reports, announcements, release notes, project documentation, image-rich explainers, meeting materials, and public-facing drafts that need embedded local images, captions, readable headings, Chinese/English typography, visible word counts, and a deterministic Python conversion workflow.
---

# Markdown to DOCX

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

## 端到端工作流

### 1. 建立文档目录

把 Markdown、图片和输出文件放在同一个可追溯目录内：

```text
[PROJECT]/
├── draft.md
├── draft.docx
└── images/
    ├── overview.png
    ├── pipeline.png
    └── result.png
```

要求：

- 不要把正文、图片或输出散落到多个无关目录。
- 不要把长期交付文件放进 `/tmp`。
- 如果只是测试，可以在临时目录中生成，但测试后必须清理。
- 输出 `.docx` 应与源 Markdown 同目录或放入明确的 `outputs/`、`dist/` 目录。

### 2. 整理 Markdown 源文件

先让 Markdown 本身成为清晰文档，而不是把转换脚本当成修稿工具：

- 只保留一个 `#` 主标题。
- 正文章节使用 `##`、`###`、`####`。
- 长段落先在 Markdown 中拆开，避免 Word 中出现过长段落。
- 图片都写 `alt`，让生成的 caption 可读。
- 外部链接保持 Markdown 链接写法。
- 表格如果是解释型图文内容，可以保留为 Markdown table。
- 表格如果是数据型内容，先确认是否需要保留 Word 网格表。

推荐先做一次 Markdown 自查：

```bash
python3 - <<'PY'
from pathlib import Path

md = Path("/path/to/draft.md")
text = md.read_text(encoding="utf-8")
print("headings:")
for line in text.splitlines():
    if line.startswith("#"):
        print(line)
print("image refs:", text.count("![") + text.count("<img"))
PY
```

### 3. 检查本地图片

转换前必须确认本地图片存在：

```bash
python3 - <<'PY'
from pathlib import Path
import re

md = Path("/path/to/draft.md")
base = md.parent
text = md.read_text(encoding="utf-8")
paths = re.findall(r'!\[[^\]]*\]\(([^)]+)\)|<img[^>]+src=["\']([^"\']+)["\']', text)
missing = []
remote = []
for a, b in paths:
    src = a or b
    if src.startswith(("http://", "https://", "data:")):
        remote.append(src)
        continue
    if not (base / src).exists():
        missing.append(src)
print("remote:", remote)
print("missing:", missing)
raise SystemExit(1 if missing else 0)
PY
```

处理规则：

- `missing` 非空时先修路径或补图片。
- `remote` 非空时，优先下载图片到本地 `images/` 再引用。
- 不要让缺失图片静默进入最终交付稿。

### 4. 生成 DOCX

普通转换：

```bash
python3 markdown-to-docx/scripts/build_docx.py /path/to/draft.md -o /path/to/draft.docx
```

显式指定图片基准目录：

```bash
python3 markdown-to-docx/scripts/build_docx.py /path/to/draft.md \
  -o /path/to/draft.docx \
  --base-dir /path/to/project
```

英文文档：

```bash
python3 markdown-to-docx/scripts/build_docx.py /path/to/draft.md \
  -o /path/to/draft.docx \
  --body-font "Calibri" \
  --heading-font "Arial"
```

图片很多且不希望去重：

```bash
python3 markdown-to-docx/scripts/build_docx.py /path/to/draft.md \
  -o /path/to/draft.docx \
  --keep-duplicate-images
```

### 5. 统计可见字数

```bash
python3 markdown-to-docx/scripts/count_visible_words.py /path/to/draft.docx
```

判断方式：

- 英文稿主要看 `word_tokens`。
- 中文和中英混排稿主要看 `calibrated`。
- 统计结果用于估算篇幅，不替代 Word 自带字数统计。

### 6. 程序化验收

至少确认 `.docx` 可被 `python-docx` 打开，并包含段落文本：

```bash
python3 - <<'PY'
from pathlib import Path
from docx import Document

docx_path = Path("/path/to/draft.docx")
doc = Document(docx_path)
paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
print("paragraphs:", len(paragraphs))
print("inline_shapes:", len(doc.inline_shapes))
print("first:", paragraphs[0] if paragraphs else "")
raise SystemExit(0 if paragraphs else 1)
PY
```

### 7. 人工验收

最终必须打开 Word 或兼容编辑器检查：

- 首页标题是否居中且字号合适。
- 章节层级是否符合预期。
- 图片是否显示清晰，没有被拉伸或过大。
- caption 是否存在、居中、不过度重复。
- 链接是否清楚可见。
- 列表和引用是否可读。
- 表格展开后的阅读顺序是否自然。
- 字体在中文、英文、数字、代码片段中是否协调。
- 文档是否有孤立小段、空白过多或图片位置突兀。

### 8. 迭代修正

常见迭代顺序：

1. 先改 Markdown 内容和图片引用。
2. 再改 `<img width="...">` 或 `--default-image-width`。
3. 再改字体和字号参数。
4. 最后才修改脚本逻辑。

不要直接在生成的 `.docx` 中做大量手工改动后丢失源 Markdown；如果必须手工改 Word，记录哪些地方不能由脚本复现。

### 9. 交付

交付前确认：

- 源 Markdown 保留。
- 图片目录保留。
- `.docx` 是最新生成或最新人工修订版本。
- 若文档有长度要求，附上 `count_visible_words.py` 的统计结果。
- 若文档用于公开发布，确认没有本地绝对路径、临时目录路径、内部账号、未公开链接或占位符。

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
## 一级章节
### 二级章节
#### 三级章节
```

转换规则：

- `#` 变成 Word `Title`，居中。
- `##` 变成 Word `Heading 1`。
- `###` 变成 Word `Heading 2`。
- `####` 变成 Word `Heading 3`。

普通段落：

```markdown
这是一段正文。可以使用 **粗体**、*斜体*、`inline code` 和 [链接](https://example.com)。
```

支持：

- `**bold**` / `__bold__`
- `*italic*` / `_italic_`
- inline code，按普通正文字体渲染
- links，按蓝色下划线渲染
- `<br>` 换行

图片：

```markdown
![系统架构图](images/architecture.png)
```

带宽度的 HTML 图片：

```markdown
<p align="center"><img src="images/architecture.png" alt="系统架构图" width="420" /></p>
```

图片规则：

- `src` 相对 `--base-dir` 解析；默认 `--base-dir` 是 Markdown 所在目录。
- `width` 按 px 粗略换算到英寸，限制在合理宽度内。
- 没有 `width` 时默认图片宽度约 `5.8` 英寸。
- 缺失图片会在文档中写入 `[Missing image: ...]`，不会静默跳过。
- `alt` 或表格 caption 会生成居中小号斜体 caption。

列表：

```markdown
- 要点一
- 要点二

1. 步骤一
2. 步骤二
```

引用：

```markdown
> 这是一段重点引用。
```

图文块表格：

```markdown
| Layer | Highlight | Visual |
| --- | --- | --- |
| **Big idea**<br>Human-centered research loop. | Why it matters. | ![Loop](images/loop.png) |
| **Artifact**<br>Every run leaves files behind. | Why it matters. | ![Artifacts](images/artifacts.png) |
```

处理方式：

- 每个表格行会被展开为正文块，而不是保留为 Word 网格表。
- 第一列里的 `**...**` 会作为小标题。
- 第一列剩余文字会作为描述段落。
- 后续列中的图片会被插入正文。
- 后续列中的文字会被插入为普通段落。

适用场景：

- highlights 表格。
- feature / why-it-matters 对照。
- 图文卡片。
- 多张图按说明逐段展示。

不适用场景：

- 财务表、实验结果表、参数表等需要严格网格结构的表格。
- 需要合并单元格、精确列宽、复杂表头的 Word 表格。
- 这种情况应改写脚本的 `handle_table`，或使用 `python-docx` 原生 `doc.add_table(...)` 保留网格。

代码块：

````markdown
```python
print("hello")
```
````

处理方式：

- fenced code 会进入 Word 正文。
- 不做语法高亮。
- 如果代码块是核心内容，转换后需要人工检查换行和缩进。

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
