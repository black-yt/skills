# LaTeX 编译技能

本技能记录稳定的 LaTeX 编译方案：使用系统级 `latexmk` + `pdflatex`，并将编译产物、TeX 缓存和源码目录隔离。

## 核心原则

- 使用系统包安装 TeX 工具链，不建议在 conda 环境中安装 TeX。
- 用 `latexmk -pdf` 编译，让它自动处理多轮编译、引用和目录。
- 使用独立 build 目录保存 PDF 和中间文件，避免污染 LaTeX 源码目录。
- 设置 `TEXMFVAR` 和 `TEXMFCONFIG` 到可写目录，避免 TeX 首次生成字体缓存时写入 `/tmp`、只读目录或不可控位置。

不建议使用 conda 安装 TeX 的原因：

- conda TeX 依赖较重。
- 容易和已有环境中的 `icu`、`nodejs` 等包产生冲突。
- 在 agent 或容器环境中更容易出现路径和动态库问题。

## 安装

Debian/Ubuntu 系统可使用：

```bash
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y texlive-latex-extra latexmk ghostscript
apt-get clean
```

说明：

- `texlive-latex-extra`：常见 LaTeX 宏包集合。
- `latexmk`：自动化 LaTeX 编译工具。
- `ghostscript`：常用于 PDF 后处理，也可配合 PDF 转图预览。

如果没有 root 权限，需要让系统管理员安装，或使用已有系统级 TeX 环境。

## 推荐目录结构

建议把源码、编译产物和 TeX 缓存分开：

```text
project/
  latex/
    main.tex
    sections/
    figures/
  latex_build/
    texmf-var/
    texmf-config/
    main.pdf
    ...
```

其中：

- `latex/`：只放需要同步、维护和提交的 LaTeX 源文件。
- `latex_build/`：放 PDF、中间文件、日志和 TeX 缓存。
- 如果项目会和 Overleaf 同步，不要把编译中间文件写进同步目录。

## 标准编译命令

进入 LaTeX 源码目录：

```bash
cd /path/to/project/latex
```

执行编译：

```bash
TEXMFVAR=/path/to/project/latex_build/texmf-var \
TEXMFCONFIG=/path/to/project/latex_build/texmf-config \
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=../latex_build main.tex
```

参数说明：

- `TEXMFVAR=...`：TeX 运行时生成的变量缓存目录。
- `TEXMFCONFIG=...`：TeX 配置缓存目录。
- `latexmk -pdf`：使用 PDFLaTeX 工作流生成 PDF。
- `-interaction=nonstopmode`：遇到错误时尽量输出完整日志，不进入交互模式。
- `-halt-on-error`：遇到致命错误时停止，适合自动化环境。
- `-outdir=../latex_build`：把 PDF 和中间文件输出到 build 目录。
- `main.tex`：主 tex 文件，请替换为实际入口文件名。

## 清理编译产物

清理中间文件但保留 PDF：

```bash
latexmk -c -outdir=../latex_build main.tex
```

清理中间文件和 PDF：

```bash
latexmk -C -outdir=../latex_build main.tex
```

如果需要完全重建，也可以删除 build 目录中的中间文件和缓存目录，但不要误删源码目录。

## 常见问题

### 找不到宏包

表现：

```text
LaTeX Error: File `xxx.sty' not found.
```

处理：

- 优先安装系统 TeX 包，例如 `texlive-latex-extra`。
- 如果是会议模板自带 `.sty`，确认它和主 `.tex` 在可被 TeX 搜索到的位置。
- 不要优先用 conda 安装 TeX 宏包。

### TeX 尝试写入只读目录

表现：

- 字体缓存生成失败。
- 报 `/tmp`、home、只读目录不可写。

处理：

- 显式设置 `TEXMFVAR` 和 `TEXMFCONFIG` 到项目 build 目录中的可写子目录。

### 源码目录被中间文件污染

处理：

- 使用 `-outdir=../latex_build`。
- 不要在源码目录中直接裸跑 `pdflatex main.tex`。
- 如果已经产生 `.aux`、`.log`、`.fls`、`.fdb_latexmk` 等文件，确认无用后再清理。

## 验证建议

编译后检查：

- `latex_build/main.pdf` 是否生成。
- 日志中是否有 `Fatal error`、`Emergency stop`、`Undefined control sequence`。
- 参考文献、目录、交叉引用是否正常。
- PDF 中图片、表格、公式和中文字体是否正常。

可以快速查看 build 目录：

```bash
ls -lh /path/to/project/latex_build
```
