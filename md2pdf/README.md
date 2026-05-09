# Markdown 转 PDF 技能

本技能用于将 Markdown 文件转换为 PDF。脚本会先用 `markdown2` 将 Markdown 转为 HTML，再用 `WeasyPrint` 输出 PDF。

## 文件结构

```text
md2pdf/
  README.md
  md_to_pdf.py
```

其中 `md_to_pdf.py` 是可直接运行的脚本，`README.md` 记录环境、用法和注意事项。

## 依赖安装

Python 依赖：

```bash
pip install markdown2 weasyprint
```

注意：`WeasyPrint` 可能还需要系统图形/字体相关依赖。不同系统安装方式不同，如果 `pip install weasyprint` 后运行报 Cairo、Pango、fontconfig 等错误，需要按 WeasyPrint 官方文档补齐系统依赖。

## 功能特性

- 支持普通 Markdown 文本。
- 支持 Markdown 表格：`markdown2` 的 `tables` extra。
- 支持 fenced code block：`markdown2` 的 `fenced-code-blocks` extra。
- 自动给 HTML 注入基础 CSS：
  - 图片最大宽度不超过页面宽度。
  - 表格使用边框。
  - 表格单元格增加基础 padding。
- 支持传入 base path，用于解析 Markdown 中的相对图片路径。
- 如果输出路径是目录，会自动使用 Markdown 文件名生成同名 `.pdf`。

## 使用方法

基本用法：

```bash
python md_to_pdf.py input.md output.pdf
```

指定输出目录：

```bash
python md_to_pdf.py input.md output_dir
```

这会生成：

```text
output_dir/input.pdf
```

指定图片和相对资源的起始路径：

```bash
python md_to_pdf.py input.md output.pdf /path/to/base_dir
```

如果 Markdown 中有相对图片路径，例如：

```markdown
![figure](images/fig1.png)
```

可以把第三个参数设为 Markdown 资源所在目录，使 WeasyPrint 能找到图片。

## Python 调用

也可以在其他 Python 脚本中导入函数：

```python
from md_to_pdf import md_to_pdf

md_to_pdf("input.md", "output.pdf", base_path=".")
```

## 参数说明

- `md_path`：输入 Markdown 文件路径。
- `pdf_path`：输出 PDF 文件路径；如果是目录，则自动生成同名 PDF。
- `base_path`：可选，资源起始路径，用于解析图片等相对路径。

命令行格式：

```text
python md_to_pdf.py <markdown路径> <输出pdf路径> [起始路径]
```

## 实现流程

1. 以 UTF-8 读取 Markdown 文件。
2. 使用 `markdown2.markdown(..., extras=["tables", "fenced-code-blocks"])` 转为 HTML。
3. 注入基础 CSS，保证图片和表格在 PDF 中可读。
4. 如果提供 `base_path`，对 HTML 中的 `src="..."` 做路径前缀处理。
5. 调用 `HTML(string=html_content, base_url=base_path or ".").write_pdf(pdf_path)` 输出 PDF。

## 注意事项

- 输入 Markdown 建议使用 UTF-8 编码。
- 图片路径最好使用相对路径，并通过第三个参数传入资源根目录。
- 如果 Markdown 中包含外部网络图片，转换结果取决于当前网络环境和 WeasyPrint 是否能访问该 URL。
- 表格过宽时可能超出页面，需要手动调整 Markdown、CSS 或页面尺寸。
- 复杂 HTML、MathJax、LaTeX 公式不一定能被 WeasyPrint 直接渲染。
- 如果 PDF 中中文字体显示异常，需要安装中文字体，并在 CSS 中指定字体。

## 验证建议

转换完成后，人工打开 PDF 检查：

- 中文是否正常显示。
- 图片是否加载成功。
- 表格边框和内容是否完整。
- 代码块是否保留换行和缩进。
- 页面是否有明显溢出、截断或空白。
