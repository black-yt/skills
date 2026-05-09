---
name: docx-splitting
description: "当需要在 Windows + Microsoft Word 环境中按页拆分 .docx 文件并尽量保留原始格式、图片、表格和分页效果时使用。"
---

# DOCX 按页拆分

## 使用场景

用于把一个 `.docx` 文档按页数拆分成多个较小的 `.docx` 文件，并尽量保留 Word 原始排版。

仅适用于 Windows + Microsoft Word 环境，因为脚本通过 `win32com.client` 调用 Word COM 自动化接口，分页结果依赖本机 Word 排版引擎。

## 依赖安装

前置条件：

- Windows。
- 已安装 Microsoft Word 桌面版。
- Python 与 Word 位数兼容，通常使用当前 Windows Python 即可。

```bash
pip install pywin32
```

安装后可做最小检查：

```bash
python -c "import win32com.client; print('pywin32 ok')"
```

## 脚本

优先使用 bundled script：

```text
scripts/split_docx.py
```

## 命令行用法

拆成 4 份：

```bash
python scripts/split_docx.py input.docx
```

拆成 8 份并指定输出目录：

```bash
python scripts/split_docx.py input.docx --output-dir split_output --parts 8
```

## Python 调用

```python
from scripts.split_docx import split_docx_lossless_by_pages

split_docx_lossless_by_pages(
    "input.docx",
    output_dir="split_output",
    parts=8,
)
```

## 注意事项

- 运行前关闭正在编辑的同一个 Word 文件。
- 建议先复制原始 `.docx`，在副本上运行。
- 字体缺失、页面设置差异或 Word 版本差异可能导致分页略有不同。
- `--parts` 必须是正整数；如果总页数少于 `parts`，脚本只会生成实际需要的 part。
- 如果拆分边界落在复杂表格、图片或分页符附近，需要人工检查边界页是否缺失或重复。

## 验证

拆分后人工打开输出文件，检查：

- 每个 part 是否能正常打开。
- 页码范围是否大致符合预期。
- 表格、图片、公式和标题格式是否保留。
- 相邻 part 之间是否有明显内容缺失或重复。
