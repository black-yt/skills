# DOCX 按页无损拆分技能

本技能用于把一个 `.docx` 文档按页数拆分成多个较小的 `.docx` 文件，并尽量保留原文档格式、图片、表格和分页效果。

## 运行环境

该方法只能在 Windows 上运行，并且需要安装 Microsoft Word。

原因：

- 使用 `win32com.client` 调用 Word COM 自动化接口。
- 分页信息依赖 Word 自身的排版引擎。
- Linux、macOS 或没有安装 Word 的环境无法运行该脚本。

Python 依赖：

```bash
pip install pywin32
```

## 适用场景

- 原始 `.docx` 很大，需要拆成多个部分处理。
- 希望尽量保留 Word 原始排版和格式。
- 需要按页切分，而不是按标题、段落或字符数切分。

## 注意事项

- 拆分结果依赖当前机器上的 Word 排版效果；字体缺失、页面设置差异或 Word 版本差异可能导致页码略有不同。
- 脚本会调用本机 Word 后台打开文档，运行时不要手动编辑同一个文件。
- 建议先复制原始 `.docx`，在副本上运行脚本。
- 输出目录会自动创建。
- 如果目标文件已存在，Word 可能覆盖或弹出冲突；建议使用新的输出目录。

## 文件结构

本技能包含：

```text
docx_splitting/
  README.md
  split_docx.py
```

其中 `split_docx.py` 是可直接运行的脚本，`README.md` 只记录环境、用法和注意事项。

## 参数说明

- `input_path`：输入 `.docx` 文件路径。
- `output_dir`：输出目录，默认是 `split_output`。
- `parts`：拆分份数，默认是 `4`。

拆分逻辑：

1. 使用 Word 打开原始文档。
2. 调用 `Repaginate()` 更新分页。
3. 使用 `ComputeStatistics(2)` 获取总页数。
4. 按 `math.ceil(total_pages / parts)` 计算每份页数。
5. 通过 Word 的 `Selection.GoTo` 定位起始页和结束页后一页。
6. 用 `doc.Range(start_pos, end_pos)` 获取该部分范围。
7. 通过 `FormattedText` 复制到新文档，尽量保留格式。
8. 保存为 `part_1.docx`、`part_2.docx` 等。

## 使用示例

拆成 4 份：

```bash
python split_docx.py input.docx
```

拆成 8 份并指定输出目录：

```bash
python split_docx.py input.docx --output-dir split_output --parts 8
```

也可以在其他 Python 脚本中导入函数：

```python
from split_docx import split_docx_lossless_by_pages

split_docx_lossless_by_pages(
    "input.docx",
    output_dir="split_output",
    parts=8,
)
```

## 验证建议

拆分完成后，建议人工打开输出文件检查：

- 每个 part 是否能正常打开。
- 页码范围是否大致符合预期。
- 表格、图片、公式和标题格式是否保留。
- 相邻 part 之间是否有明显内容缺失或重复。

如果拆分边界刚好落在复杂表格、图片或分页符附近，可能需要人工检查并微调 `parts` 或手动处理边界页。
