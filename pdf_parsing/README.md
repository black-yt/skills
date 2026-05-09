# PDF 解析技能：使用 StructAI ReadPDF 生成本地 Markdown

本文件是一份通用说明，可独立转发给需要解析 PDF 文档的人使用。它只描述通用 PDF 解析方法，不绑定任何特定项目或目录结构。

## 目标

把 PDF 文档解析成本地可读取、可搜索、可复制的 Markdown，并抽取 PDF 中的图片资源，方便后续阅读、整理资料或交给大语言模型分析。

解析完成后，后续阅读应优先使用本地 Markdown 文件，而不是反复读取或重新解析 PDF。

## 安装与环境检查

Python 依赖：

```bash
pip install structai
```

如果需要使用 GitHub 仓库中的最新代码，可以从源码安装：

```bash
pip install "git+https://github.com/black-yt/structai.git"
```

安装后确认 Python 环境里能导入 `structai`：

```bash
python3 -c "import structai; print(structai.__file__)"
```

如果能输出安装路径，说明环境可用。

进一步确认 `read_pdf` 可用：

```bash
python3 -c "from structai import read_pdf; import inspect; print(inspect.signature(read_pdf))"
```

如果输出类似 `(path: str | list[str])`，说明 PDF 解析入口可用。

为了避免解析时生成 `__pycache__`，建议运行命令时加上：

```bash
PYTHONDONTWRITEBYTECODE=1
```

## 基本解析命令

本技能使用 `structai.read_pdf`。它会调用 MinerU 对 PDF 做版面解析，并在本地保存解析结果。

Python 调用：

```python
from structai import read_pdf

result = read_pdf("paper.pdf")
```

解析单个 PDF：

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -c "from structai import read_pdf; read_pdf('paper.pdf')"
```

带结果摘要的解析命令：

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -c "from structai import read_pdf
p='paper.pdf'
r=read_pdf(p)
print('success', bool(r))
if r:
    print('path', r['path'])
    print('text_length', len(r['text']))
    print('image_count', len(r['img_paths']))
    print(r['text'][:1200])"
```

## 本地解析结果

对 `paper.pdf` 调用 `read_pdf` 后，通常会在 PDF 同级位置生成一个同名目录，例如：

```text
paper/
  full.md
  layout.json
  *_content_list.json
  图片资源子目录
```

常用文件说明：

- `full.md`：最重要的输出文件，包含解析后的全文 Markdown。
- `layout.json`：版面结构信息，可用于排查版面解析问题。
- `*_content_list.json`：内容块列表，可辅助定位段落、标题、表格和图片。
- 图片资源子目录：保存从 PDF 中抽取出来的图片或版面切片。

如果同名目录下已经存在 `full.md`，`read_pdf` 通常会优先复用本地结果，不会重复上传解析。因此解析成功后，后续阅读应直接打开 `full.md`。

## 返回值结构

`read_pdf("paper.pdf")` 成功时通常返回字典：

```python
{
    "path": "paper.pdf",
    "text": "...",
    "img_paths": [...],
    "imgs": [...]
}
```

字段含义：

- `path`：原始 PDF 路径。
- `text`：`full.md` 的全文内容。
- `img_paths`：Markdown 正文实际引用到的图片路径。
- `imgs`：对应的 PIL 图片对象。

注意：本地图片资源子目录中可能包含更多中间切片；`img_paths` 只表示 Markdown 正文实际引用到的图片。

## 网络问题与代理处理

MinerU 处理和结果下载需要网络。如果遇到以下问题，优先尝试关闭代理后重试：

- `SSLError`
- `UNEXPECTED_EOF_WHILE_READING`
- `Max retries exceeded`
- `Connection reset`
- 上传成功但下载结果压缩包失败
- 命令长时间没有输出，最后返回下载失败

关闭常见代理环境变量后重试：

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy -u NO_PROXY -u no_proxy PYTHONDONTWRITEBYTECODE=1 python3 -c "from structai import read_pdf; read_pdf('paper.pdf')"
```

判断是否可能是代理问题：

- 错误发生在下载解析结果阶段，而不是 Python 导入阶段。
- 报错域名来自 MinerU、OpenXLab 或结果压缩包 CDN。
- 报错包含 SSL EOF、连接被重置、远端提前断开等信息。
- 同一个 PDF 关闭代理后可以继续下载或成功解析。

处理顺序：

1. 先保留当前目录，不要删除已经生成的解析缓存。
2. 用关闭代理的命令重试同一个 PDF。
3. 如果重试成功，后续直接读取本地 `full.md`。
4. 如果重试失败但本地已有 `full.md` 且内容可读，可以直接使用本地 Markdown。
5. 如果没有 `full.md`，记录完整错误信息，稍后重试或更换网络环境。

如果第一次失败但已经生成了同名目录，可以直接重试。除非确认缓存损坏，一般不要急着删除本地解析结果。

## 直接读取本地 Markdown

解析成功后，优先读取 `full.md`：

```bash
sed -n '1,120p' paper/full.md
```

查看文档结构：

```bash
rg -n "^#|^##|^###" paper/full.md
```

查看图片引用：

```bash
rg -n "!\\[" paper/full.md
```

推荐检查顺序：

1. 先看标题、目录、摘要或章节开头，确认整体结构是否可读。
2. 用标题列表定位需要阅读或处理的章节。
3. 用图片引用列表定位图表、插图或版面截图。
4. 对关键公式、表格、数值和结论回到 PDF 原文或抽取图片核对。

## 质量检查

解析完成后至少检查：

```bash
test -s paper/full.md
rg -n "^#|^##|^###" paper/full.md
rg -n "!\\[" paper/full.md
```

需要确认：

- `full.md` 存在且非空。
- 标题、摘要、章节标题基本可读。
- 图表引用能对应到本地图片资源。
- 关键表格没有严重错行。
- 公式和特殊符号没有影响理解。

## 常见问题

### 解析返回 None

可能原因：

- 网络连接失败。
- 代理导致 SSL 或下载异常。
- PDF 文件损坏。
- MinerU 服务暂时不可用。

处理方法：

1. 关闭代理重试。
2. 检查本地是否已经生成 `full.md`。
3. 如果 `full.md` 可读，就直接使用本地 Markdown。
4. 如果仍无可用结果，记录错误信息，不要凭空补写原文没有的信息。

### Markdown 局部乱码或断词

PDF 版面复杂时，OCR 或版面解析可能产生乱码、断词、公式错位和表格错行。

处理方法：

- 用 `full.md` 快速定位章节。
- 对关键段落回到 PDF 原文核对。
- 对表格和公式优先查看 PDF 原图或抽取图片。
- 后续输出中只使用核对过的内容。

### 图片目录里文件很多

解析器可能保存正文图片，也可能保存中间版面切片。优先看 Markdown 中实际引用的图片，再按后续任务需要浏览其他图片。

## 推荐工作流

1. 确认 `structai` 可导入。
2. 对目标 PDF 运行 `read_pdf`。
3. 如果失败，关闭代理后重试。
4. 确认 `full.md` 存在且非空。
5. 直接阅读 `full.md`，用标题和图片引用快速定位结构。
6. 对关键数值、图表、公式回到 PDF 或图片核对。
7. 后续再次阅读时直接打开本地 `full.md`，不要重复解析。
