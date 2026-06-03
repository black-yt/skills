---
name: pdf-to-images
description: "当需要用系统级 Ghostscript 或 Poppler pdftoppm 将 PDF 页面导出为 PNG/JPEG 图片，支持单页、页码范围、整篇导出和论文排版可视化检查时使用。"
---

# PDF 转图片

## 核心原则

- 首选系统级工具：Ghostscript (`gs`) 或 Poppler `pdftoppm`。
- `pdftoppm` 适合把 PDF 稳定渲染成页面图片，用于论文写作、LaTeX 编译检查和排版验收。
- `gs` 适合已有 Ghostscript 环境、需要 `pngalpha` 或更细控制输出设备的场景。
- 输出图片放到明确的预览目录，不要和源文件目录混在一起。
- 不要长期把输出放在 `/tmp`，避免环境清理后结果丢失。
- 按需设置页码范围，避免不必要地导出整篇 PDF。
- 如果缺依赖需要安装，先确认当前环境是否允许安装；共享环境或集群环境中不要擅自安装系统包。

## 工具选择

- **快速论文预览。** 优先用 `pdftoppm -png -r 180`。
- **检查字体、图标、表格细节。** 使用 `pdftoppm -png -r 200` 或 `-r 300`。
- **检查图表是否溢出或页面是否截断。** `150-180` DPI 通常足够。
- **需要 alpha PNG 或 Ghostscript 已是默认工具。** 使用 `gs -sDEVICE=pngalpha`。

## 安装与检查

Poppler / `pdftoppm`：

```bash
# Ubuntu / Debian / WSL
sudo apt update
sudo apt install -y poppler-utils

# macOS
brew install poppler

# conda
conda install -c conda-forge poppler

# Windows 推荐 conda
conda install -c conda-forge poppler
```

检查：

```bash
pdftoppm -v
pdfinfo -v
```

Ghostscript：

Debian/Ubuntu：

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y ghostscript
apt-get clean
```

检查：

```bash
gs --version
```

## 导出单页或页码范围

创建输出目录：

```bash
mkdir -p /path/to/project/pdf_pages_png
```

### 使用 pdftoppm

导出整篇 PDF：

```bash
pdftoppm -png -r 180 /path/to/project/main.pdf /path/to/project/pdf_pages_png/page
```

输出示例：

```text
page-1.png
page-2.png
page-3.png
```

只导出第 1 页：

```bash
pdftoppm -png -r 180 -f 1 -l 1 /path/to/project/main.pdf /path/to/project/pdf_pages_png/page
```

只导出第 8 页：

```bash
pdftoppm -png -r 180 -f 8 -l 8 /path/to/project/main.pdf /path/to/project/pdf_pages_png/page
```

输出单个文件，不带页码后缀：

```bash
pdftoppm -png -r 200 -f 1 -l 1 -singlefile /path/to/project/main.pdf /path/to/project/pdf_pages_png/first_page
```

输出：

```text
first_page.png
```

导出 JPEG：

```bash
pdftoppm -jpeg -r 200 /path/to/project/main.pdf /path/to/project/pdf_pages_png/page
```

### 使用 Ghostscript

导出第 1 页：

```bash
gs -q -dSAFER -dBATCH -dNOPAUSE \
  -sDEVICE=pngalpha \
  -r180 \
  -dFirstPage=1 \
  -dLastPage=1 \
  -sOutputFile=/path/to/project/pdf_pages_png/page_%03d.png \
  /path/to/project/main.pdf
```

导出第 3 到第 5 页：

```bash
gs -q -dSAFER -dBATCH -dNOPAUSE \
  -sDEVICE=pngalpha \
  -r180 \
  -dFirstPage=3 \
  -dLastPage=5 \
  -sOutputFile=/path/to/project/pdf_pages_png/page_%03d.png \
  /path/to/project/main.pdf
```

导出整篇 PDF 时去掉 `-dFirstPage` 和 `-dLastPage`。

## 参数要点

- `pdftoppm -png`：输出 PNG。
- `pdftoppm -jpeg`：输出 JPEG。
- `pdftoppm -r 180`：180 DPI，论文预览常用。
- `pdftoppm -f 1 -l 1`：指定起止页。
- `pdftoppm -singlefile`：单页输出时不追加页码后缀。
- `-sDEVICE=pngalpha`：输出带 alpha 通道的 PNG。
- `-r180`：180 DPI，清晰度和文件大小较平衡。
- `-r120`：快速预览。
- `-r300`：高质量截图或打印级预览。
- `-sOutputFile=.../page_%03d.png`：输出文件模板。

## 论文排版检查流程

编译 PDF 后转成页面图片：

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error paper.tex
mkdir -p preview_pages
pdftoppm -png -r 180 paper.pdf preview_pages/page
```

检查重点：

- 页面是否被截断。
- 图、表、algorithm、case box 是否超出正文边框。
- 字体、公式、图标、表格线是否清晰。
- 图片数量是否符合 PDF 页数。
- 输出目录是否在项目内明确位置，而不是散落到源码目录或临时目录。

如果只是检查溢出，`150-180` DPI 足够；如果要检查细节，用 `200` 或 `300` DPI。

## 常见问题

- `pdftoppm: command not found`：安装 `poppler-utils` 或 `poppler`。
- `gs: command not found`：安装 `ghostscript`。
- 图片太模糊：提高 DPI，例如 `-r300`。
- 图片太大：降低 DPI，例如 `-r120`，或只导出需要的页码范围。
- 输出文件页码不符合预期：`page_%03d.png` 通常从导出的第一页开始编号，不一定等于原 PDF 页码。
- `pdftoppm` 输出 `page-1.png` 这类后缀；如果只想要单个固定文件名，使用 `-singlefile`。

## 验证

导出后检查：

```bash
ls -lh /path/to/project/pdf_pages_png
```

确认图片数量符合页码范围、能正常打开，文本/公式/表格/图片清晰，且没有误输出到源码目录或临时目录。
