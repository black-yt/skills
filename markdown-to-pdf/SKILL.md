---
name: markdown-to-pdf
description: "当需要用 Python 将 Markdown 转为 PDF，并保留表格、代码块、图片路径和基础 CSS 样式时使用。"
---

# Markdown 转 PDF

## 使用场景

将 Markdown 文件转为 PDF。脚本会先用 `markdown2` 转 HTML，再用 `WeasyPrint` 输出 PDF。

## 依赖安装

```bash
pip install markdown2 weasyprint
```

`WeasyPrint` 可能还需要系统图形/字体相关依赖。如果运行时报 Cairo、Pango、fontconfig 等错误，按 WeasyPrint 官方文档补齐系统依赖。

检查：

```bash
python -c "import markdown2; from weasyprint import HTML; print('md2pdf deps ok')"
```

## 脚本

优先使用 bundled script：

```text
scripts/md_to_pdf.py
```

## 命令行用法

基本用法：

```bash
python scripts/md_to_pdf.py input.md output.pdf
```

指定输出目录：

```bash
python scripts/md_to_pdf.py input.md output_dir
```

指定图片和相对资源的起始路径。第三个参数会作为 WeasyPrint 的 `base_url`，用于解析 Markdown 中的相对图片路径、CSS 和本地资源：

```bash
python scripts/md_to_pdf.py input.md output.pdf /path/to/base_dir
```

如果 Markdown 中有相对图片路径，例如 `![figure](images/fig1.png)`，把第三个参数设为 Markdown 资源所在目录。不要把第三个参数设成某个图片文件本身。

## Python 调用

```python
from scripts.md_to_pdf import md_to_pdf

md_to_pdf("input.md", "output.pdf", base_path=".")
```

## 功能特性

- 支持普通 Markdown 文本。
- 支持 Markdown 表格：`markdown2` 的 `tables` extra。
- 支持 fenced code block：`markdown2` 的 `fenced-code-blocks` extra。
- 自动注入基础 CSS，使图片最大宽度不超过页面宽度，并给表格加边框和 padding。
- 如果输出路径是目录，会自动使用 Markdown 文件名生成同名 `.pdf`。

## 注意事项

- 输入 Markdown 建议使用 UTF-8 编码。
- 图片路径最好使用相对路径，并通过第三个参数传入资源根目录。
- 外部网络图片是否能加载取决于当前网络环境和 WeasyPrint。
- 复杂 HTML、MathJax、LaTeX 公式不一定能被 WeasyPrint 直接渲染。
- 中文字体异常时，需要安装中文字体，并在 CSS 中指定字体。
- 如果需要更复杂的页面尺寸、页边距或字体样式，优先在脚本中的 CSS 块里显式添加规则。

## 验证

转换后人工打开 PDF，检查中文、图片、表格、代码块换行缩进，以及页面是否有明显溢出、截断或空白。
