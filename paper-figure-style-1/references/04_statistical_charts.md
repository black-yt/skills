# 统计图组件与数据语义

## 选择图形

| 用户想表达的关系 | 推荐结构 | 关键规则 |
| --- | --- | --- |
| 方法排名、单指标大小 | 竖柱 + 误差线 | 从零开始，排序与标签/区间一起变换 |
| 时间预算逐步增加时的累计完成率 | 家族小多图 + 阶梯线 + 区间带 | 中心线和区间使用相同的阶梯约定 |
| 成功率与多种资源消耗的权衡 | 大小面板散点 + Pareto 前沿 | 每种资源独立算前沿；对数轴只能放正值 |
| 多基准训练前后表现 | 表格 + 内嵌增益条 + 森林图 | 绝对百分点变化与相对百分比增长分开 |
| 训练过程 | 两行五列小图 + 前后连接点 | 保留每步数据；同种指标尽量共享刻度 |
| 方法 × 多个指标或领域 | 横条矩阵 | 每列独立标单位，行顺序一致；不是堆积柱或热力图 |
| 失败归因与原因解释 | 成组横条 + 案例汇合 + 轨迹流程 | 先定义归因分母与是否互斥，再画比例 |
| 类别及其子领域的构成 | 层级双环 + 编号图例 | 父项总数由子项求和，内外环边界对应 |

## 共用代码

- [charts.py](../scripts/charts.py)：坐标、刻度、线、区间、柱、点、前沿和组合布局。
- [demo_data.py](../scripts/demo_data.py)：虚构方法与共享演示数值；`budget_curve()` 生成的终点与排行榜一致。
- [check_charts.py](../scripts/check_charts.py)：检查数值不变量和输出 PDF 的透明度、文字、矢量属性。
- **依赖**：沿用 `scripts/requirements.txt`，无额外统计包、在线服务或参考图片依赖。绘图组件只呈现调用者提供的区间，不代算统计置信度。
- **复用方式**：将 `scripts/` 加入 Python 搜索路径；统计绘图至少保留 `style1.py` 与 `charts.py`，使用图标时还要保留 `icons.py`。只有运行演示场景才需要 `demo_data.py`。

## 坐标和基本 API

`Axes(f, x, y, w, h, xlim, ylim, logx=False)` 中 `(x,y,w,h)` 是画布布局位置；后续统计方法接受原始数据坐标，数值向右、向上增加。轴范围必须递增且覆盖全部数据和区间；超界、非有限值和无效对数会报错，不会静默裁切。

| API | 数据与参数 | 行为 |
| --- | --- | --- |
| `Scale(low, high, start, end, log=False)` | 数据范围、画布两端坐标 | 连续线性/对数映射；支持倒置画布端点 |
| `axis.point(x, y)` | 原始数据坐标 | 返回画布坐标，供标签或自定义连接线使用 |
| `axis.frame(...)` | `xticks`, `yticks`, `xformat`, `yformat`, `xlabel`, `ylabel`, `ylabels`, `grid`, `size` | 薄轴线、水平网格、可复制刻度；y 轴标题使用旋转文本 |
| `axis.bar(x, value, width=.7, color=..., interval=None)` | 分类中心为数值 x；`interval=(low,high)` 是上下界 | 实心竖柱，从 y=0 开始；区间不是误差长度 |
| `axis.hbar(y, value, height=.35, ...)` | 类别中心 y；可传 `interval`、`endpoint` | 水平柱，从线性 x=0 开始；适合矩阵与成组条 |
| `axis.error(x, y, low, high, horizontal=False)` | 估计值必须落在上下界之间 | 原生路径误差线与端帽；可以跨越零 |
| `axis.series(x, y, step=False, dash=None, ...)` | 等长数组，至少两点；x 严格递增 | 普通折线或右连续阶梯线（post） |
| `axis.band(x, low, high, center=None, step=False, alpha=.13, ...)` | 等长数组，逐点 low ≤ high；传 center 时检查区间包含中心线 | 透明矢量多边形，不使用栅格填充 |
| `axis.dot(x, y, filled=True, shape="circle", ...)` | `circle / square / diamond / triangle` | 空心/实心矢量标记 |
| `legend_item(f, x, y, label, color, dash=None, shape=None)` | y 为文字基线 | 线型或形状图例；可读文字保持文本 |
| `pareto_frontier(cost, score)` | 等长非空数组：成本越低越好，分数越高越好 | 返回非支配点索引，按成本排序；并列最优重复点保留 |

- **柱宽**：`width`、`height` 使用数据单位；例如 x 取 `0,1,2`，柱宽 `.7` 保留类别间距。
- **累计曲线**：先按时间排序，合并重复时间戳，校验完成率不下降。`series()` 不会擅自把下降值改成单调。
- **线与区间**：预算图两者均设置 `step=True`；不要用阶梯中心线配线性插值区间。
- **散点标注**：用 `axis.point()` 得到位置后添加合理偏移；密集场景用编号与页脚索引，避免挤在点旁边。
- **超界处理**：扩大有意义的范围、检查单位或拆面板；不能随意截断区间以改善外观。

## 组合布局数据结构

### 对齐横条矩阵

`bar_matrix(f, x, y, width, labels, columns, colors, row_height=19, label_width=147)` 每一列独立映射数值，标签与色序共用。

```python
labels = ["Method A", "Method B"]
colors = ["#A36840", "#3E846B"]
columns = [
    {
        "title": ["Task", "success"],
        "maximum": 100,
        "format": lambda v: f"{v:g}%",
        "values": [
            {"value": 52, "low": 48, "high": 56},
            {"value": 61, "low": 58, "high": 64},
        ],
    },
    {
        "title": ["Additional", "solved tasks"],
        "maximum": 10,
        "show_values": True,
        "values": [0, 4],
    },
]
```

- **缺失值**：`values` 中 `None` 显示破折号；`0` 表示确实测得零。数值可以是标量或 `{value,low,high}`，列长度必须与 `labels` 相等。
- **单位**：标题和格式说明百分比、分钟或任务数；不能把不同量纲堆在同一条柱里。
- **额外覆盖**：先用同一批任务 ID 求当前方法已解决集合减去参考方法集合的大小；不能把两个总体成功率相减当作额外覆盖数。
- **计数标签**：`show_values=True` 在列右侧显示 `+数值`，专用于额外覆盖等非负增量计数；普通指标不启用。

### 增益表与森林图

- **增益表**：`gain_table(f,x,y,width,rows,title=...,max_gain=20)` 的行字段为 `model / benchmark / n / before / after`。前后值是百分数，`n` 为正整数；增益由 `after-before` 计算，条长度使用相同的 `max_gain`。
- **适用边界**：表内增益条只接受非负变化；若有退化，使用森林图或明确实现发散条，不把负值裁成零。
- **森林图**：`forest(f,x,y,width,rows,limits=(-10,20),ticks=(-10,0,10,20))` 的行字段为 `label / value / low / high`。数值按百分点解释，保留可见零线与正负两侧范围。
- **区间解释**：是否跨零可从图上读取；显著性仍取决于区间方法、样本设计和多重比较处理，不能仅凭演示线判断。

### 层级双环

`nested_donut(f,cx,cy,groups,inner=45,split=75,outer=101)` 返回总数和子项的编号位置。每组结构为：

```python
groups = [
    {
        "label": "Repair",
        "color": "#D6C8E7",
        "children": [
            {"label": "Tables", "value": 280, "color": "#BAB0D6"},
            {"label": "Documents", "value": 200, "color": "#D3B8CE"},
        ],
    },
]
```

- **数量**：值为正数；零项从扇区中省略，可在图例另外说明。总数由所有子项相加，示例的中心数不会手工另填。
- **关系**：此 API 的内外环表示父子层级。若数据只有两个独立边际分布，应分别绘制独立环并说明关系，不能伪造成层级。
- **绘制**：`ring_segment()` 使用原生三次弧路径，编号和中心总数是可提取文本。

## 完整柱状图骨架

将下面代码保存为本 skill 的 `scripts/my_results.py` 后执行。示例数值仅用于演示；应用到真实研究时应替换数据、标题和页脚来源说明。

```python
from pathlib import Path
from style1 import Figure, P
from charts import Axes, COLORS, footer

rows = [
    {"name": "Baseline", "value": 36, "low": 32, "high": 40},
    {"name": "Retrieval", "value": 51, "low": 47, "high": 55},
    {"name": "Full system", "value": 67, "low": 64, "high": 70},
]
root = Path(__file__).resolve().parents[1]
f = Figure(root / "outputs" / "my_results.pdf", height=300,
           title="Task success under three configurations")
f.background()
f.header("Task success under three configurations")
axis = Axes(f, 65, 63, 615, 158, (-.6, 2.6), (0, 80))
axis.frame(yticks=(0, 20, 40, 60, 80), ylabel="Success (%)")
for i, row in enumerate(rows):
    axis.bar(i, row["value"], color=COLORS[i],
             interval=(row["low"], row["high"]))
    f.text(axis.sx(i), axis.sy(row["high"])-6, row["value"],
           size=11, align="center")
    f.text(axis.sx(i), 243, row["name"], size=11, align="center")
footer(f, detail="Error bars: illustrative bounds")
f.save()
```

```bash
.venv/bin/python scripts/my_results.py
.venv/bin/python scripts/verify_pdf.py outputs/my_results.pdf \
  --expect "Full system" --expect "Success (%)" --previews
```

## 数据与验收

- **来源**：演示数据留在演示图；用户未提供实验值时应请求数值，或明确约定制作占位示意，不能发明“实测结果”。
- **区间**：传上下界；如果原始数据只有标准差、标准误或重复运行结果，先确认要呈现的量与统计方法，不能统一称作 95% CI。
- **增益**：30% 到 45% 是增加 15 个百分点，相对增加 50%；示例的 `Gain` / `Δ (pp)` 使用前者。
- **分母**：总体任务、失败任务、完成轨迹、单次运行和跨次均值必须标清；归因类别互斥时检查各组总和。
- **训练**：演示函数用固定种子保证输出可复现。真实曲线保持输入日志的步数和波动；若要平滑，应同时交代方法并保留原始观测。
- **最终输出**：按 [示例与验收](03_examples_and_validation.md) 生成预览并检查 PDF。自动校验不代替对标签重叠、单位正确性和最终印刷字号的目视检查。
