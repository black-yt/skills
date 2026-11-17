# PowerPoint 自动化与 PDF 验收

## 使用 PowerPoint 测量和编辑

以下片段适用于 Windows 上的桌面 Microsoft PowerPoint。可用 PowerShell 的 `New-Object -ComObject PowerPoint.Application` 建立连接。对已经复制的工作文件，`Presentations.Open($copyPath, -1, 0, 0)` 是后台只读探测。需要保存修改时，在可写工作副本上打开。操作结束后关闭本次打开的文稿。

### 读取首行并校准年份

先根据当前幻灯片找到对应正文框、段落序号和年份框，段落与行号从 1 开始。`BoundTop` 返回渲染后的文本行位置，形状 `Top` 返回外框位置。二者的差值包含文本框内边距，不能用外框上沿直接代替文字上沿。

```powershell
$paragraph = $bodyShape.TextFrame.TextRange.Paragraphs($paragraphIndex, 1)
$firstLine = $paragraph.Lines(1, 1)
$lastLine = $paragraph.Lines($paragraph.Lines().Count, 1)
$yearText = $yearShape.TextFrame.TextRange
$deltaPt = $firstLine.BoundTop - $yearText.BoundTop
$yearShape.Top = $yearShape.Top + $deltaPt
```

计算区块底边时，使用最后一行的顶部加实际行高。若文本范围的高度已经含段后距，核对相邻段落实测位置，再决定哪些间距需要计入跨页预算。重开候选文件后重新测量，避免把修改前的行坐标当成最终结果。

### 修改已有文字链接

查找当前段落中的准确锚文本，再只取对应字符范围。下面的 `$linkStart` 是从 1 开始的字符位置，`$linkLength` 是锚文本长度。

```powershell
$anchor = $paragraph.Characters($linkStart, $linkLength)
$link = $anchor.ActionSettings.Item(1).Hyperlink
$link.Address = $newUrl
if ($link.Address -ne $newUrl) { throw 'The hyperlink address did not update.' }
```

保存后验证对应锚文字和实际目标。若新增条目时沿用原段落，先确认复制的旧链接已改成新条目的地址。

## 通过 Open XML 编辑

- 单纯移动文本框时，可在 `ppt/slides/slideN.xml` 中定位当前 `p:cNvPr/@id`，核对形状文字及旧坐标，再修改 `p:spPr/a:xfrm/a:off/@y`。PowerPoint 的坐标使用 pt，Open XML 使用 EMU。把 `round(deltaPt * 12700)` 加到原 `y`。该变换针对未分组文本框，分组时先考虑父组坐标变换。
- 跨页迁移段落时保留原段落属性和文本 run。在 `ppt/slides/_rels/slideN.xml.rels` 中解析源页 `a:hlinkClick/@r:id`，按实际目标在目的页重用或新建 relationship，重写该 run 的 `r:id`。外部链接关系需要对应的 URI 和 `TargetMode="External"`。文稿内跳转按实际目标幻灯片核对。
- 对定点坐标改动，可反向还原目标坐标并与源 XML 比较，确认变更范围。对包含跨页移动的内容改动，核对输出包可以重开、条目没有遗漏或重复、各页链接归属正确，再用目标渲染器查看实际排版。

## 导出与验证 PDF

先保存可编辑的 PPTX，再从已经验收的工作副本导出。可以用 PowerPoint 界面的 PDF 导出，也可在 COM 中用 `SaveAs`。格式值 `32` 表示 PDF，适合在临时工作副本上执行。

```powershell
$deck.Save()
$deck.SaveAs($pdfPath, 32, 0)
```

1. 重开 PDF，对比页面尺寸与页数，检查页首、页底、续页、字形和链接位置。可用 `pdftoppm -r 144 -png "$pdfPath" "$previewPrefix"` 渲染预览。
2. 核对实际链接。外部链接可读取每页 `/Annots` 中 `/Subtype /Link` 的 `/A`，检查 `/S /URI` 和 `/URI`，有几条同地址时按页核对条数。对于内部跳转，确认它跳到预期页。蓝色下划线只说明样式存在。
3. 对于增删或迁移的条目，检查它们在 PPTX 和 PDF 的预期页出现或消失，链接目标也随条目移动。单独修改链接时核对该锚文字对应的注释，避免同页其他链接刚好使用同一 URL 掩盖问题。

下面的检查可用 `pypdf` 列出外部链接和用来定位锚文字的注释矩形。将输出与预期页、链接文本及 URL 核对。

```python
from pypdf import PdfReader

pdf_path = "output.pdf"
for page_number, page in enumerate(PdfReader(pdf_path).pages, 1):
    annotations = page.get("/Annots")
    for entry in annotations.get_object() if annotations else []:
        annotation = entry.get_object()
        action = annotation.get("/A")
        if annotation.get("/Subtype") == "/Link" and action:
            action = action.get_object()
            if action.get("/S") == "/URI":
                print(page_number, annotation.get("/Rect"), action.get("/URI"))
```
