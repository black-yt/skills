# Docx Workflow And Structure

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
