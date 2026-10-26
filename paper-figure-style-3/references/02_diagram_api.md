# 方法图组件与自定义

## 坐标和调用

`scripts/style3.py` 的 `diagram(width, height)` 使用左上为 `(0,0)`，x 向右、y 向下，宽高为逻辑单位。默认每 100 单位对应 1.2 英寸。`label(..., size=...)` 的字号为 PDF points；改变整体画布尺寸后需检查最终论文版心内的可读性。图 1/2 使用 `diagram_theme()` 的 DejaVu Serif；如需更明显的手写字形，可传 `font_family="Kalam"`，该字体随包分发。`style3.py` 的卡片、箭头、文档和立方体调用 `handdrawn.py` 中的路径图元；图 3/4 使用规整的 `theme()`。

`handdrawn.py` 对边线施加固定、低幅度的法线偏移；同样的坐标反复生成相同路径。文字与底色不随机抖动，渐变由窄矢量色带构成，PDF 中仍是可编辑路径。不要把 `amplitude` 调大来伪造手绘感：先画准确的轮廓，再按最终版心尺寸观察笔触。

| 组件 | 用途与关键参数 |
| --- | --- |
| `diagram(w,h)` | 新建白底等比矢量画布，返回 `fig, ax`。 |
| `box(ax,x,y,w,h,fill,edge,text,size)` | 圆角模块卡片；文本居中，可在卡片外另用 `label` 写多行说明。 |
| `arrow(ax,x1,y1,x2,y2,color,curved)` | 末端箭头，可设置曲率；箭头方向由起止点决定。 |
| `diamond(ax,x,y,w,h,fill)` | 三面体 latent 块，全部由路径组成。 |
| `brain(ax,x,y,scale)`、`head_brain(...)`、`phase_emblem(...)`、`sun(...)`、`moon(...)` | 大脑、头部轮廓、昼夜分半徽章和天体矢量图标；在图标外自行放标签。 |
| `document(ax,x,y,w,h,text)`、`notebook(...)` | 折角任务单与巩固后的技能笔记；文字仍可提取。 |
| `snowflake(ax,x,y,radius)`、`weaver(...)` | 冻结 LLM 标记与纱线形 latent weaver；由线和路径绘制。 |
| `memory_cylinder(ax,x,y,w,h)` | 有上下椭圆面的 episodic buffer 容器；内部记录、latent 块和标签另画。 |
| `label(ax,x,y,text,size,weight,style)` | 可提取的真实文本；需要换行时用 `\n`。 |
| `diagram_theme(font_family=...)` | 统一方法图字体；文字锚点不随手绘路径波动。 |
| `handdrawn.polygon/rect/ellipse/line/arrow` | 确定性笔触的基础形状与连接线；改 `amplitude` 前检查是否出现过度波浪。 |
| `handdrawn.bezier_shape/prism/wash/circle_wash` | 曲线轮廓、三面 latent 块、区域与圆形徽章的矢量渐变；适合云朵、分区背景和中间状态。 |
| `save_pdf(fig,path,title)` | 检查字体字形后保存 PDF，不接受其他后缀。 |

## 自定义图的完整骨架

先在自己的项目中创建新脚本，并把安装后的 skill `scripts/` 加入 `sys.path`；也可复制所需组件到自己项目。以下示例不依赖源论文 PDF：

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path('[SKILL_DIR]/scripts').resolve()))
from style3 import diagram_theme, diagram, box, arrow, diamond, label, save_pdf
from handdrawn import wash

with diagram_theme():
    fig, ax = diagram(720, 270)
    wash(ax, [(0, 0), (720, 0), (720, 270), (0, 270)],
         '#FFF7EC', '#E6F1FA')
    box(ax, 30, 60, 170, 100, fill='#C8E5D1', text='New task', size=14)
    box(ax, 275, 60, 170, 100, fill='#97CFCC', text='Adapt latent', size=14)
    box(ax, 520, 60, 170, 100, fill='#DDEBF7', text='Update prior', size=14)
    arrow(ax, 203, 110, 272, 110)
    arrow(ax, 448, 110, 517, 110)
    diamond(ax, 343, 205, 44, 31)
    label(ax, 365, 248, 'learned latent block', size=10)
    save_pdf(fig, 'my_method.pdf', title='My dual-phase method')
```

把 `[SKILL_DIR]` 替换成实际 skill 目录。正式图应根据任务真实流程增删节点，不能把示例术语直接当作自己的算法。

## 两张方法图如何改

- `diagrams.figure_1(path, labels=...)`：四象限类比，包含记忆云、任务文档、召回片段、三份技能文件、技能笔记、episodic buffer 和夜间 prior 生成。布局在 `figure1_layout.py` 的 `_cue_and_skills`、`_daytime`、`_nighttime` 等区域函数中；若无“大脑/昼夜”机制，不应沿用这个隐喻。
- `diagrams.figure_2(path, labels=...)`：上方输入与 latent 序列、中部截断和 base/refined latent、左下三路 rollout 与冻结 LLM、中央动量迁移、右侧 buffer/weaver/模型选择/高置信子集。布局在 `figure2_layout.py` 的 `_title_and_task`、`_decode_and_latents`、`_rollouts` 等区域函数中。先画出自己的有向流程，再调整卡片尺寸；反馈闭环要说清楚消息、经验或参数的流向。
- 两个 `DEFAULT_LABELS` 字典列出可替换的文字键。只替换文字时直接调用，例如：

```python
from pathlib import Path
import sys

sys.path.insert(0, str(Path('[SKILL_DIR]/scripts').resolve()))
from diagrams import figure_1, figure_2

figure_1('new_analogy.pdf', labels={
    'day_task': 'Analyze a\nnew dataset',
    'learned_skill': 'analysis +\nvisualization',
})
figure_2('new_pipeline.pdf', labels={
    'task_line_1': ': Analyze a new dataset',
    'task_line_2': 'Summarize the pattern and uncertainty',
})
```

- 标签更长或结构变更时，应改区域函数中的卡片宽度、字号、坐标和箭头端点，再用原图对照检查。两张例图的坐标系分别为 `948×326` 和 `1098×617`；不能假设换词后自然不重叠。
- 图 1 的贝塞尔记忆云、气泡框、圆筒技能记录和带渐变的四象限；图 2 的宽箭头、三路 rollout 反馈、双色缓冲筒与选择器，是修改复杂图时可直接复用的分区实现。源图只用于测量和对照，不参与绘制。
- `scripts/render_examples.py --figures 1 2` 可只渲染方法图。脚本默认产物在 `outputs/`，也接受 `--output-dir`。
- 同一行的任务卡文字固定 `ha='left'` 和共同左边距；多行模块文字使用 `ha='center'`，同级标题共用 y 坐标。笔迹波动只用于矢量线条，不应用到文字坐标上。
- 长文本先缩短或换行，再增大卡片/画布；不要连续缩小字号。批量改图后运行 `verify_pdf.py --previews` 并查看预览，留意连线覆盖文字与截出画布的标签。
