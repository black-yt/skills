# 绘图库与适配方法

## 核心文件

- [style1.py](../scripts/style1.py)：`Figure`、`Palette` 和几何/PDF 输出；所有文字通过字体绘制，所有渐变通过原生 shading 绘制。
- [icons.py](../scripts/icons.py)：可复用线性图标，以及流程图中的文件夹、模块包、规则卡、验证卡和交互窗口插画。
- [charts.py](../scripts/charts.py)：统计坐标、柱/横条、区间、曲线、前沿、矩阵和环形图；数据结构见 [统计图 API](04_statistical_charts.md)。
- [model_logos.py](../scripts/model_logos.py)：按模型标识绘制内置透明 PNG，支持统一尺寸与独立文字；资产及用法见 [模型 logo](05_model_logos.md)。
- [requirements.txt](../scripts/requirements.txt)：绘图与验证依赖；不需要在线模型、API key 或原论文文件。

## 坐标与文字

- **坐标**：`Figure` 的 `(0, 0)` 在画布左上角。`charts.Axes` 则接受向右、向上递增的数据坐标，并转换到画布。
- **基线**：`text(x, y, ...)` 中 `y` 是文字基线；不是文本框顶边，也不是文本中心。
- **尺寸**：`Figure(output, height=..., width=720, width_in=7.2)` 将逻辑坐标统一缩放到真实 PDF 尺寸。
- **换行**：用 `lines()` 给出每一行文本和 `leading`；不要将包含换行的字符串交给 `text()`。
- **宽度**：重要卡片标签传入 `max_width`，超宽时明确报错；正文没有自动缩放或静默裁切。
- **外部使用**：把绘图库目录加入 Python 模块搜索路径，或把 `style1.py` 与 `icons.py` 复制到用户的绘图工程；两个模块要一起保留。

## API 摘要

| API | 作用 | 关键参数 |
| --- | --- | --- |
| `Figure(output, height, ...)` | 建立单页 PDF 画布并嵌入字体 | `width`, `width_in`, `title`, `font_regular`, `font_bold` |
| `background()` | 整张画布的浅桃紫渐变 | 使用实例 palette 的背景色 |
| `header(title, brand=None)` | 主标题与下方细分隔线 | `brand` 用于流程图左上角短标识 |
| `gradient(x, y, w, h, ...)` | 裁切到圆角形状的矢量渐变 | `colors`, `positions`, `radius` |
| `box(x, y, w, h, ...)` | 卡片、标签底色或区域边框 | `fill`, `stroke`, `radius`, `line_width`, `alpha` |
| `zone(x, y, w, h, color)` | 半透明分组底色 | 浅色、透明度 0.5 |
| `text(x, y, value, ...)` | 可提取的 Unicode 文本，包括旋转轴标题 | `size`, `color`, `bold`, `align`, `max_width`, `angle`（逆时针度数） |
| `lines(x, y, values, ...)` | 多行标签 | `leading`；其余参数同 `text()` |
| `arrow(points, ...)` | 直线或折线箭头 | `color`, `width`, `head`；点列表至少两点 |
| `line(a, b, ...)` / `polyline(points, ...)` | 分隔线、网格、边框、自定义路径 | `color`, `width`, `alpha`, `dash` |
| `curve(points, ...)` | 三次贝塞尔曲线，可沿曲线切向放置箭头 | 起点、两个控制点、终点；`arrow_at` 为 `(0,1]` 内的位置比例 |
| `circle(cx, cy, radius, ...)` | 编号、状态和图标细节 | `fill`, `stroke`, `width` |
| `icon(name, x, y, ...)` | 以中心点定位的线稿图标 | `size`, `color` |
| `save()` | 完成并保存 PDF | 返回输出路径；同一画布只调用一次 |

注意：API 的常用默认颜色来自 `P`。需要改整套语义色时，在自己的脚本中定义 palette，并将相应颜色显式传给卡片、连线与图标；不要假设只换背景就能自动改变全部语义元素。

## 最小自定义示例

把以下代码保存为本 skill 下的 `scripts/my_method.py`，运行后得到一张可复制文字的双阶段方法图。实际项目中将文案替换为用户内容。

```python
from pathlib import Path
from style1 import Figure, P

root = Path(__file__).resolve().parents[1]
figure = Figure(root / "outputs" / "my_method.pdf", height=220,
                title="A verifiable research workflow")
figure.background()
figure.header("A verifiable research workflow")

figure.box(20, 64, 295, 122, fill=P.lavender, stroke=P.purple)
figure.icon("workspace", 43, 89, size=18)
figure.text(65, 93, "Candidate method", size=12)
figure.lines(38, 127, ["Inputs · parameters · outputs",
                       "Versioned, reproducible execution"],
             color=P.muted, leading=19, max_width=258)

figure.box(405, 64, 295, 122, fill=P.peach, stroke=P.rust)
figure.icon("shield", 428, 89, size=18, color=P.rust)
figure.text(450, 93, "Independent checks", size=12)
figure.lines(423, 127, ["Held-out data · acceptance criteria",
                        "Evidence recorded before release"],
             color=P.muted, leading=19, max_width=258)

figure.arrow([(321, 125), (399, 125)], color=P.rust)
figure.save()
```

```bash
.venv/bin/python scripts/my_method.py
.venv/bin/python scripts/verify_pdf.py outputs/my_method.pdf \
  --expect "Independent checks" --previews
```

## 图标选择

可用名称：`code`, `workspace`, `folder`, `document`, `cube`, `flask`, `shield`, `expert`, `robot`, `search`, `layers`, `pencil`, `bolt`, `target`, `network`, `refresh`, `bars`, `check`, `cross`, `minus`。

- **中心定位**：`icon("shield", 100, 80, size=18)` 将图标中心放到 `(100, 80)`。
- **新增图标**：在 `icons.py` 中沿用 24 × 24 逻辑网格，以几何路径定义，保持同类线宽；不使用 emoji 或整张位图代替。
- **大插画**：`pipeline_illustration(figure, name, cx, cy)` 支持 `repository / package / recipe / validation / interaction`，由多个可复用图形组成。

## 字体和失败处理

- **缺字符**：绘图库会明确报出缺失字符，避免生成看似成功但出现方框的 PDF。
- **指定字体**：CLI 可传 `--font-regular [FONT_REGULAR_TTF] --font-bold [FONT_BOLD_TTF]`。选择可嵌入且覆盖所需字符的 TrueType 字体。
- **多语言排版**：默认示例为英文；不保证复杂脚本的双向排版或字形连接，使用这些语言时需要额外的 shaping 验证。
- **长标签**：改用两行、缩短表达或扩展卡片；`max_width` 报错时不要移除检查来掩盖问题。
- **文本轮廓**：图标可以是路径，标题和正文仍应保持文本；字体难题不能通过整图栅格化绕过。
