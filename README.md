# Skills

本目录存放可复用、可转发的技能。每个 skill 使用独立子文件夹，并按 Anthropic/Claude Skills 风格提供 `SKILL.md`。

每个 skill 的基本结构：

```text
skill-name/
  SKILL.md
  scripts/      # 可选，放可执行脚本
  references/   # 可选，放按需读取的参考资料
  assets/       # 可选，放模板、图片、示例文件等素材
```

## Skill 列表

| Skill | 入口文档 | 用途 |
| --- | --- | --- |
| `docx-splitting` | [`docx-splitting/SKILL.md`](docx-splitting/SKILL.md) | 在 Windows + Microsoft Word 环境中，通过 [`scripts/split_docx.py`](docx-splitting/scripts/split_docx.py) 按页无损拆分 `.docx` 文档。 |
| `latex-compiling` | [`latex-compiling/SKILL.md`](latex-compiling/SKILL.md) | 使用系统级 `latexmk` + `pdflatex` 编译 LaTeX，并隔离 build 目录与 TeX 缓存。 |
| `markdown-to-pdf` | [`markdown-to-pdf/SKILL.md`](markdown-to-pdf/SKILL.md) | 使用 [`scripts/md_to_pdf.py`](markdown-to-pdf/scripts/md_to_pdf.py) 将 Markdown 转为 PDF，支持表格、代码块、图片路径和基础 CSS。 |
| `pdf-to-images` | [`pdf-to-images/SKILL.md`](pdf-to-images/SKILL.md) | 使用系统级 Ghostscript (`gs`) 将 PDF 页面导出为 PNG 图片，支持单页、页码范围和整篇导出。 |
| `pdf-parsing` | [`pdf-parsing/SKILL.md`](pdf-parsing/SKILL.md) | 使用 `structai.read_pdf` 将 PDF 解析为本地 Markdown，并处理图片抽取、代理重试和解析质量检查。 |

## 下载 Skill 文件夹

GitHub 网页不支持直接下载指定文件夹。可以先下载本目录下的 `download_skill.py`，之后用它下载本仓库中的一个或多个 skill 文件夹。

### 下载脚本

```bash
curl -L -o download_skill.py https://raw.githubusercontent.com/black-yt/skills/main/download_skill.py
```

### 下载单个 Skill

```bash
python download_skill.py docx-splitting
```

下载后会生成同名目录：

```text
docx-splitting/
  SKILL.md
  scripts/
    split_docx.py
```

指定输出目录：

```bash
python download_skill.py docx-splitting -o my_skills/docx-splitting
```

### 一次下载多个 Skill

```bash
python download_skill.py docx-splitting pdf-parsing markdown-to-pdf -o skills
```

多个 skill 同时下载时，`-o` 表示父目录。上面的命令会生成：

```text
skills/
  docx-splitting/
  pdf-parsing/
  markdown-to-pdf/
```

默认不会覆盖已存在文件；需要覆盖时加 `--overwrite`。

如果 GitHub API 触发限流，可以设置 `GITHUB_TOKEN` 后重试：

```bash
export GITHUB_TOKEN=<your_github_token>
python download_skill.py docx-splitting
```
