# 架构图与界面绘制 API

## 模块入口

| 模块 | 能力 |
| --- | --- |
| [style2.py](../scripts/style2.py) | `theme`、`Diagram`、`save_pdf`、配色常量及物理宽度控制 |
| [icons.py](../scripts/icons.py) | `ICON_PALETTES` 与独立配色的矢量小图标，不依赖 emoji 字体 |
| [diagrams.py](../scripts/diagrams.py) | `component_overview`、`lifecycle`、`interface_walkthrough` 完整布局；`miniature_table` 和 `ui_panel` 可单独复用 |

## 坐标与字体

- **原点**：`Diagram` 使用左上角 `(0, 0)`，y 向下；默认逻辑宽度 1100。
- **文字**：`text` 的 y 默认是垂直中心，和基线坐标不同；`va="top"` 可改为顶部对齐。多行字符串用 `\n`。
- **字号**：`Diagram` 字号为逻辑单位，导出时自动换算为 PDF point；原生 Matplotlib 图表 API 的 `fontsize` 则是 point。
- **测宽**：`text_width(value, size, bold)` 测量当前主题字体；`text(..., max_width=...)` 会缩小超宽文字。先缩短内容，避免为了塞入卡片把文字缩得过小。
- **默认字体**：DejaVu Sans 随 Matplotlib 提供。中文或其他缺失字符需要合法可用的字体，可用 `matplotlib.font_manager.fontManager.addfont(...)` 注册，再传 `theme(font="[FONT_FAMILY]")`；注册文件需在每个新进程中执行。
- **缺字检查**：PDF 导出前核对字体字符表，遇到缺失字符报错。不要忽略缺字警告，也不要用方框作为替代。

## 常用绘图方法

| 调用 | 参数与行为 |
| --- | --- |
| `Diagram(height, width=1100, width_in=11)` | 创建单页画布；高度、宽度、物理宽度必须为正数 |
| `rect(x, y, w, h, fill, edge, radius, lw)` | 纯色矩形或圆角卡片；`fill=None`/`edge=None` 关闭填充/描边 |
| `group(x, y, w, h, title, zone, icon, icon_color, icon_accent)` | 标题条与大分区；`zone` 为 green/blue/purple/gold/rose；图标默认使用自身调色板 |
| `card(x, y, w, h, title, body, color, icon, icon_color, icon_accent)` | 白底小卡片；`color` 控制标题和边框，两个 `icon_*` 参数独立控制图标 |
| `text(x, y, value, size, color, bold, ha, va)` | 可提取文字；`ha` 为 left/center/right；`max_width` 控制可用宽度 |
| `line(points, color, lw, dash)` | 折线或虚线；points 为 `(x,y)` 列表 |
| `arrow(points, color, lw, dash, head)` | 最后一段带箭头；通过多个点组成正交连接 |
| `circle(...)` / `polygon(...)` | 阶段序号、数据缩略图与自定义矢量图元 |
| `icon(name, x, y, size, color, accent)` | 左上角定位的矢量图标；主色、点缀色默认取 `ICON_PALETTES[name]` |
| `save(output, title)` | 保存文字和图形均可编辑的 PDF |

**内置图标名**：`terminal`、`code`、`screen`、`cube`、`sandbox`、`network`、`loop`、`tools`、`search`、`robot`、`model`、`document`、`report`、`science`、`records`、`sliders`、`schedule`、`adapter`、`chart`、`analysis`、`clock`、`play`、`trash`、`folder`。部分名称共用图形；未知名称明确报错。

- **默认配色**：不传图标颜色时使用鲜明的语义配色；例如 `cube` 为蓝青，`sandbox` 为青绿，`adapter` 为洋红。分区标题和节点边框仍使用各自的分区或阶段色。
- **颜色覆盖**：`icon(..., color=..., accent=...)` 显式指定两色；仅传 `color` 时，点缀色自动取主色的浅色版本。`card` / `group` 对应参数是 `icon_color` / `icon_accent`。
- **保持层次**：大面积背景采用浅色，鲜明色用于图标和少量强调标签。不要把 `color` 同时机械地传给整区每个图标。

## 可运行的自定义示例

在 skill 根目录保存为临时脚本，使用同一个 Python 环境执行。实际项目可将 `scripts` 路径改为完整 skill 目录；不要依赖本仓库中其他 skill。

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path("scripts").resolve()))
from style2 import Diagram, theme, BLUE, TEAL

with theme():
    d = Diagram(290)
    d.group(12, 12, 1076, 244, "Reproducible analysis", zone="blue", icon="science")
    d.card(44, 86, 280, 86, "Collect", "Versioned input records", color=BLUE, icon="folder")
    d.card(409, 86, 280, 86, "Validate", "Executable checks", color=BLUE, icon="science")
    d.card(774, 86, 280, 86, "Report", "Traceable conclusions", color=TEAL, icon="report")
    d.arrow([(325, 129), (408, 129)], color=BLUE)
    d.arrow([(690, 129), (773, 129)], color=TEAL)
    d.text(550, 220, "Inputs, checks and evidence share the same run identifier.", ha="center")
    d.note()
    d.save("outputs/custom_pipeline.pdf", "Reproducible analysis pipeline")
```

## 使用完整布局

- **组件总览**：`component_overview(output, width_in=11, title=...)`；标签和连接关系定义在 [diagrams.py](../scripts/diagrams.py)。新用户的不同拓扑应复用 `Diagram` 图元重新布局，不强行塞入固定拓扑。
- **生命周期**：`lifecycle(output, width_in=11, stages=[...])` 支持四个阶段名；更换节点、正常路径或异常路径时一并修改对应连线。
- **界面说明**：`interface_walkthrough(...)` 组合五个 `ui_panel(...)`；它是可编辑的产品示意图，不能当作已实现功能的截图证据。
- **自定义组件**：复用 `miniature_table` 展示短记录，避免在全局架构图里嵌入需要放大很多倍才能阅读的完整日志。

## 导出与排版检查

- **图表宽度**：Matplotlib 图表使用 `save_pdf(fig, output, title=..., width_in=...)` 等比缩放几何、字体、线宽与标记；`Diagram` 已在构造时设好尺寸，直接 `save`。
- **拥挤**：先缩短标题或显式换行，再移动卡片或增加画布高度；箭头不能穿过文字。
- **密集面板**：检查缩略表格、页脚和五屏界面的最小字号；PDF 可复制不等于印刷时足够可读。
- **验证**：导出后运行 `verify_pdf.py`，并查看从 PDF 渲染的 PNG，不能只检查 Matplotlib 源对象。
