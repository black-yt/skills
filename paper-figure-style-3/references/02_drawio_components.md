# 原生组件与复用代码

## 生成器

`scripts/drawio.py` 仅使用 Python 标准库。坐标原点在左上，x 向右、y 向下；文字字号是 draw.io 的像素字号。形状、文字和连线分别生成 `mxCell`；主文件为未压缩 XML。自定义图标和轮廓使用 draw.io 的原生 stencil XML，文件中没有 SVG 图片单元。

| 接口 | 关键行为 |
| --- | --- |
| `Diagram(name,width,height)` | 创建一页画布和必须的 root/layer cells。 |
| `d.shape(id,x,y,w,h,kind=...,fill=...,stroke=...)` | 原生矩形、椭圆、note、cloud、triangle 等形状。`sketch`、`jiggle` 和 `rounded` 由原生样式控制。 |
| `d.text(id,x,y,w,h,value,size=...,align=...)` | 独立真实文字，`\n` 显式换行；默认使用 DejaVu Serif 和 `html=0`。 |
| `d.group(id,x,y,w,h,parent=...)` | 分组。子单元以父组左上为原点；同一个 cell id 在整页中必须唯一。 |
| `d.edge(id,source,target,exit=...,entry=...,points=...)` | 真实连接线；`exit/entry` 是 0–1 相对锚点，`points` 为 waypoint。支持曲线、虚线和箭头。 |
| `d.line(id,points,...)` | 不带箭头的原生 edge，适合网格、纹理、线图、图标内部笔画。 |
| `d.contour(...)` / `d.polygon(...)` | 原生 stencil 轮廓或多边形；控制点可通过 Edit Shape 的 XML 修改。 |
| `save([diagram,...],path)` | 保存单页或多页 `.drawio`，保留可读 XML。 |

不要对文字坐标施加随机抖动。`sketch=True` 默认使用小幅 `jiggle=.45` 与单笔轮廓；科学坐标轴、数据 marker 和下载图标采用规整形状。图标本身保持集合的准确轮廓。

## 完整的新图骨架

把 `[SKILL_DIR]` 替换成实际 skill 路径，在自己的任务目录运行：

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path('[SKILL_DIR]/scripts').resolve()))
from drawio import Diagram, save
from components import card, cube, native_icon

d = Diagram('My method', 900, 330)
card(d, 'task', 40, 95, 200, 100, 'New task', fill='#D4E7CE', size=24)
card(d, 'adapt', 350, 95, 200, 100, 'Adapt latent', fill='#96C7C4', size=24)
card(d, 'prior', 660, 95, 200, 100, 'Update prior', fill='#E8D8E9', size=24)
d.edge('task-to-adapt', 'task', 'adapt')
d.edge('adapt-to-prior', 'adapt', 'prior')
cube(d, 'latent-state', 418, 236, 58, 47)
native_icon(d, 'task-code-icon', 'tabler-file-code', 109, 37, 44, color='#2E657D')
save([d], 'my-method.drawio')
```

用导出器打开 `my-method.drawio` 后检查。短标签更长时，先换行或增大卡片；不要连续缩小字号来遮盖布局问题。

## 复合图元

`components.py` 提供以下可复用分组；各部分都在组内单独保留：

- `card` / `document`：模块卡片、折角任务文档和独立文字。
- `cube`：front/top/side 三个可编辑面，适合区分 base/refined latent。
- `brain`：头部轮廓、gear、脑形底色和实际获取的 Tabler brain stencil。
- `native_icon`：加载 `assets/icons/*.shape.xml`，作为原生 draw.io 自定义形状；`color` 控制线色，`fill` 控制填色。
- `yarn` / `snowflake`：经 Yesicon 获取的 Tabler 图标，图 1/2 已实际使用。
- `phase`：两半底色、太阳、月亮和星点组成的昼夜分组。
- `buffer`：矩形筒身、顶/底椭圆和标题；可换底色、边线与顶面色。显式绘制这三个原生形状，避免内置 cylinder 的尺寸参数误解导致圆弧越界。
- `network`：由原生节点和连线构成的 SLM 示意。

主要流程的 edge 应连接语义模块组，而非组内一条装饰线。图标内部笔画可以是无端点引用的 line，科学关系使用有 `source`/`target` 的 edge。

## 替换数据图

`assets/data/latent-evolve.json` 保留示例的数值与“按图面转录”的来源声明。复制该文件后替换自己的数据：

```bash
python3 scripts/build_examples.py --figures 3 4 --data [DATA.json] --output-dir outputs/my-data
```

- **图 3**：`trajectories` 包含 `MATH-500`、`MMLU`、`GPQA`、`JAMA` 四个键，每个 8 个有限百分数。改变数据集名称、批次数、轴范围时编辑 `figure3`；左右轴分别由 `yleft` 和 `yright` 映射。
- **图 4**：`ablation` 有 3 个面板，各含 `MATH-500` 和 `SciBench` 的五个值；`latent_lengths` 有五个互异长度。当前示例轴范围为 20–85，函数会拒绝范围外数据；用于新数据时同步修改 `figure4` 的轴范围、刻度和输入校验。
- **数值编辑**：draw.io 内直接拖柱不会自动重算数字。以 JSON 和生成代码作为数值真源，再重新生成并核对标签。
- **标记和纹理**：线图的曲线是原生 edges，marker 是原生顶点；柱和纹理属于同一组，可整体移动，也可逐项改色。
- **标签避让**：跨轴曲线可能在同一物理位置相交。`figure3` 按点配置数值标签偏移，换数据后重新检查所有交会区域；五根相邻柱的数字必须分别可读。
