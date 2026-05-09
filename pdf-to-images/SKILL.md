---
name: pdf-to-images
description: "当需要用系统级 Ghostscript 将 PDF 页面导出为 PNG 图片，支持单页、页码范围或整篇导出时使用。"
---

# PDF 转图片

## 核心原则

- 使用系统级 Ghostscript (`gs`)。
- 输出图片放到明确的预览目录，不要和源文件目录混在一起。
- 不要长期把输出放在 `/tmp`，避免环境清理后结果丢失。
- 按需设置页码范围，避免不必要地导出整篇 PDF。

## 安装

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

- `-sDEVICE=pngalpha`：输出带 alpha 通道的 PNG。
- `-r180`：180 DPI，清晰度和文件大小较平衡。
- `-r120`：快速预览。
- `-r300`：高质量截图或打印级预览。
- `-sOutputFile=.../page_%03d.png`：输出文件模板。

## 常见问题

- `gs: command not found`：安装 `ghostscript`。
- 图片太模糊：提高 DPI，例如 `-r300`。
- 图片太大：降低 DPI，例如 `-r120`，或只导出需要的页码范围。
- 输出文件页码不符合预期：`page_%03d.png` 通常从导出的第一页开始编号，不一定等于原 PDF 页码。

## 验证

导出后检查：

```bash
ls -lh /path/to/project/pdf_pages_png
```

确认图片数量符合页码范围、能正常打开，文本/公式/表格/图片清晰，且没有误输出到源码目录或临时目录。
