---
name: pdf-parsing
description: "当需要用 structai.read_pdf 将 PDF 文档解析成本地 Markdown、抽取图片资源，并处理 MinerU 解析缓存或代理重试问题时使用。"
---

# PDF 解析

## 目标

把 PDF 文档解析成本地可读取、可搜索、可复制的 Markdown，并抽取 PDF 中的图片资源。解析完成后，后续阅读应优先使用本地 Markdown 文件，不要反复重新解析同一个 PDF。

## 依赖安装

```bash
pip install structai
```

如果需要使用 GitHub 仓库中的最新代码：

```bash
pip install "git+https://github.com/black-yt/structai.git"
```

校验：

```bash
python3 -c "from structai import read_pdf; import inspect; print(inspect.signature(read_pdf))"
```

为了避免解析时生成 `__pycache__`，建议运行命令时加上：

```bash
PYTHONDONTWRITEBYTECODE=1
```

## 基本解析

Python 调用：

```python
from structai import read_pdf

result = read_pdf("paper.pdf")
```

命令行解析：

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -c "from structai import read_pdf; read_pdf('paper.pdf')"
```

带摘要输出：

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

对 `paper.pdf` 调用 `read_pdf` 后，通常会在 PDF 同级位置生成同名目录：

```text
paper/
  full.md
  layout.json
  *_content_list.json
  图片资源子目录
```

常用文件：

- `full.md`：解析后的全文 Markdown。
- `layout.json`：版面结构信息，可用于排查版面解析问题。
- `*_content_list.json`：内容块列表，可辅助定位段落、标题、表格和图片。
- 图片资源子目录：保存从 PDF 中抽取出来的图片或版面切片。

如果同名目录下已经存在 `full.md`，`read_pdf` 通常会优先复用本地结果。因此解析成功后，后续应直接打开 `full.md`。

## 返回值结构

成功时通常返回：

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

## 网络问题与代理处理

MinerU 处理和结果下载需要网络。如果遇到 `SSLError`、`UNEXPECTED_EOF_WHILE_READING`、`Max retries exceeded`、`Connection reset`、上传成功但结果压缩包下载失败等问题，优先关闭代理后重试：

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u http_proxy -u https_proxy -u all_proxy -u NO_PROXY -u no_proxy PYTHONDONTWRITEBYTECODE=1 python3 -c "from structai import read_pdf; read_pdf('paper.pdf')"
```

处理顺序：

1. 保留当前目录，不要删除已经生成的解析缓存。
2. 用关闭代理的命令重试同一个 PDF。
3. 如果重试成功，后续直接读取本地 `full.md`。
4. 如果重试失败但已有可读 `full.md`，直接使用本地 Markdown。
5. 如果没有 `full.md`，记录完整错误信息，稍后重试或更换网络环境。

## 读取与检查

读取开头：

```bash
sed -n '1,120p' paper/full.md
```

查看标题结构：

```bash
rg -n "^#|^##|^###" paper/full.md
```

查看图片引用：

```bash
rg -n "!\\[" paper/full.md
```

至少确认：

- `full.md` 存在且非空。
- 标题、摘要、章节标题基本可读。
- 图表引用能对应到本地图片资源。
- 关键表格没有严重错行。
- 公式和特殊符号没有影响理解。

## 常见问题

- 解析返回 `None`：关闭代理重试；检查是否已有可读 `full.md`；如果仍失败，记录错误信息。
- Markdown 局部乱码或断词：用 `full.md` 快速定位章节，对关键段落、公式和表格回到 PDF 原文或抽取图片核对。
- 图片目录文件很多：优先看 Markdown 中实际引用的图片，再按后续任务需要浏览其他图片。
