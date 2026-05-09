# PDF 转图片技能

本技能记录使用系统级 Ghostscript (`gs`) 将 PDF 页面导出为 PNG 图片的稳定方案。

## 核心原则

- 使用系统级 Ghostscript，不依赖 conda 环境。
- 输出图片放到明确的预览目录，不要和 LaTeX 源码目录混在一起。
- 不要长期把输出放在 `/tmp`，避免环境清理后结果丢失。
- 导出预览图时按需设置页码范围，避免不必要地生成整篇 PDF 的大量图片。

## 安装

Debian/Ubuntu 系统可使用：

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y ghostscript
apt-get clean
```

如果同时需要 LaTeX 编译环境，也可以一次安装：

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y texlive-latex-extra latexmk ghostscript
apt-get clean
```

检查 Ghostscript 是否可用：

```bash
gs --version
```

## 推荐目录结构

建议将 PDF 和预览图分开保存：

```text
project/
  latex_build/
    main.pdf
  pdf_pages_png/
    page_001.png
    page_002.png
```

说明：

- `latex_build/`：存放编译生成的 PDF。
- `pdf_pages_png/`：存放从 PDF 导出的 PNG 预览图。
- 如果某个目录会和 Overleaf 或其他编辑器同步，不建议把 PNG 预览图放进去。

## 导出单页或页码范围

先创建输出目录：

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
  /path/to/project/latex_build/main.pdf
```

导出第 3 到第 5 页：

```bash
gs -q -dSAFER -dBATCH -dNOPAUSE \
  -sDEVICE=pngalpha \
  -r180 \
  -dFirstPage=3 \
  -dLastPage=5 \
  -sOutputFile=/path/to/project/pdf_pages_png/page_%03d.png \
  /path/to/project/latex_build/main.pdf
```

## 导出整篇 PDF

去掉 `-dFirstPage` 和 `-dLastPage`：

```bash
gs -q -dSAFER -dBATCH -dNOPAUSE \
  -sDEVICE=pngalpha \
  -r180 \
  -sOutputFile=/path/to/project/pdf_pages_png/page_%03d.png \
  /path/to/project/latex_build/main.pdf
```

## 参数说明

- `gs`：Ghostscript 命令。
- `-q`：减少输出日志。
- `-dSAFER`：启用更安全的文件访问限制。
- `-dBATCH`：处理完成后退出。
- `-dNOPAUSE`：页面之间不暂停。
- `-sDEVICE=pngalpha`：输出带 alpha 通道的 PNG。
- `-r180`：分辨率为 180 DPI。数值越高图片越清晰，文件也越大。
- `-dFirstPage=1`：从第 1 页开始导出。
- `-dLastPage=1`：导出到第 1 页结束。
- `-sOutputFile=.../page_%03d.png`：输出文件模板，`%03d` 会生成三位页码。
- 最后一个参数是输入 PDF 路径。

## 分辨率选择

常用设置：

- `-r120`：快速预览，文件较小。
- `-r180`：推荐默认值，清晰度和文件大小较平衡。
- `-r300`：高质量截图或打印级预览，文件较大。

如果只是检查 PDF 排版，通常 `-r180` 足够。

## 输出目录规范

建议：

- 输出到项目中的明确预览目录，例如 `pdf_pages_png/`、`latex_imgs_png/` 或 `preview_png/`。
- 不要输出到 LaTeX 源码目录，避免污染源码和同步目录。
- 不要长期输出到 `/tmp`，避免结果丢失。
- 如果重复导出同一 PDF，先确认是否需要清理旧图片，避免新旧页数混杂。

## 常见问题

### 找不到 gs

表现：

```text
gs: command not found
```

处理：

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y ghostscript
```

### 图片太模糊

提高 DPI：

```bash
-r300
```

### 图片太大

降低 DPI：

```bash
-r120
```

或者只导出需要检查的页码范围。

### 输出文件页码不符合预期

`page_%03d.png` 中的编号通常从导出的第一页开始编号，而不是总 PDF 页码。若导出第 3 到第 5 页，输出文件仍可能是 `page_001.png`、`page_002.png`、`page_003.png`。需要保留原 PDF 页码时，可在输出目录名或文件名前缀中注明页码范围。

## 验证建议

导出后检查：

```bash
ls -lh /path/to/project/pdf_pages_png
```

需要确认：

- 图片数量是否符合页码范围。
- 图片能正常打开。
- 文本、公式、表格和图片是否清晰。
- 没有把预览图误输出到源码目录或临时目录。
