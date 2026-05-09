# Skills

本目录存放可复用、可转发的技能文档。每个 skill 使用独立子文件夹，便于后续为同一技能添加示例、脚本、模板或辅助资料。

## Skill 列表

| Skill | 入口文档 | 用途 |
| --- | --- | --- |
| `docx_splitting` | [`docx_splitting/README.md`](docx_splitting/README.md) | 在 Windows + Microsoft Word 环境中，通过 [`split_docx.py`](docx_splitting/split_docx.py) 按页无损拆分 `.docx` 文档。 |
| `latex_compile` | [`latex_compile/README.md`](latex_compile/README.md) | 使用系统级 `latexmk` + `pdflatex` 编译 LaTeX，并隔离 build 目录与 TeX 缓存。 |
| `md2pdf` | [`md2pdf/README.md`](md2pdf/README.md) | 使用 [`md_to_pdf.py`](md2pdf/md_to_pdf.py) 将 Markdown 转为 PDF，支持表格、代码块、图片路径和基础 CSS。 |
| `pdf2img` | [`pdf2img/README.md`](pdf2img/README.md) | 使用系统级 Ghostscript (`gs`) 将 PDF 页面导出为 PNG 图片，支持单页、页码范围和整篇导出。 |
| `pdf_parsing` | [`pdf_parsing/README.md`](pdf_parsing/README.md) | 使用 `structai.read_pdf` 将 PDF 解析为本地 Markdown，并处理图片抽取、代理重试和解析质量检查。 |

## 下载 Skill 文件夹

GitHub 网页不支持直接下载指定文件夹。可以先下载本目录下的 `download_skill.py`，之后用它下载本仓库中的某个 skill 文件夹。

### 下载脚本

```bash
curl -L -o download_skill.py https://raw.githubusercontent.com/black-yt/skills/main/download_skill.py
```

### 下载 Skill

```bash
python download_skill.py docx_splitting
```

下载后会生成同名目录：

```text
docx_splitting/
  README.md
  split_docx.py
```

指定输出目录：

```bash
python download_skill.py docx_splitting -o my_skills/docx_splitting
```

默认不会覆盖已存在文件；需要覆盖时加 `--overwrite`。

如果 GitHub API 触发限流，可以设置 `GITHUB_TOKEN` 后重试：

```bash
export GITHUB_TOKEN=<your_github_token>
python download_skill.py docx_splitting
```
