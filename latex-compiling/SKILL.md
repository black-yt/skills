---
name: latex-compiling
description: "当需要用系统级 latexmk 和 pdflatex 编译 LaTeX，并把 PDF、中间文件、TeX 缓存与源码目录隔离时使用。"
---

# LaTeX 编译

## 核心原则

- 使用系统级 TeX 工具链，不优先使用 conda 安装 TeX。
- 用 `latexmk -pdf` 自动处理多轮编译、引用和目录。
- 使用独立 build 目录保存 PDF、中间文件、日志和 TeX 缓存。
- 设置 `TEXMFVAR` 和 `TEXMFCONFIG` 到可写目录，避免 TeX 首次生成字体缓存时写入 `/tmp`、只读目录或不可控位置。

## 安装

Debian/Ubuntu：

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y texlive-latex-extra latexmk ghostscript
apt-get clean
```

如果没有 root 权限，让系统管理员安装，或使用已有系统级 TeX 环境。

## 推荐目录结构

```text
project/
  latex/
    main.tex
    sections/
    figures/
  latex_build/
    texmf-var/
    texmf-config/
```

如果项目会和 Overleaf 同步，不要把编译中间文件写进同步目录。

## 标准编译命令

```bash
cd /path/to/project/latex
TEXMFVAR=/path/to/project/latex_build/texmf-var \
TEXMFCONFIG=/path/to/project/latex_build/texmf-config \
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=../latex_build main.tex
```

参数要点：

- `-interaction=nonstopmode`：遇到错误时尽量输出完整日志，不进入交互模式。
- `-halt-on-error`：遇到致命错误时停止。
- `-outdir=../latex_build`：把 PDF 和中间文件输出到 build 目录。
- `main.tex`：替换为实际入口文件名。

## 清理

清理中间文件但保留 PDF：

```bash
latexmk -c -outdir=../latex_build main.tex
```

清理中间文件和 PDF：

```bash
latexmk -C -outdir=../latex_build main.tex
```

## 常见问题

- 找不到 `.sty`：优先安装系统 TeX 包，或确认模板自带 `.sty` 在 TeX 可搜索位置。
- 字体缓存写入失败：显式设置 `TEXMFVAR` 和 `TEXMFCONFIG` 到 build 目录中的可写子目录。
- 源码目录被中间文件污染：使用 `-outdir`，不要在源码目录裸跑 `pdflatex main.tex`。

## 验证

检查：

- `latex_build/main.pdf` 是否生成。
- 日志中是否有 `Fatal error`、`Emergency stop`、`Undefined control sequence`。
- 参考文献、目录、交叉引用、图片、表格、公式和中文字体是否正常。
