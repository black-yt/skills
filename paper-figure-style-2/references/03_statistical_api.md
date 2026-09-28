# 统计图组件与数据语义

## 入口与数组约定

- **基础组件**：[charts.py](../scripts/charts.py) 定义图形、校验和计算函数，接收调用者提供的数据。
- **完整布局**：[plots.py](../scripts/plots.py) 组合组件形成可直接导出的成品图。
- **演示输入**：[demo_data.py](../scripts/demo_data.py) 固定随机种子，包含六组任务需求、二项计数与三次运行记录。它只用于示例。
- **维度名**：`INST` 指指令遵循，`TOOLS` 指工具使用，`SEARCH` 指证据搜索，`PLAN` 指研究规划，`REASON` 指科学推理，`CODE` 指代码执行。真实项目可替换，但标签与数组列必须同步。

| 组件 | 输入形状与含义 | 行为 |
| --- | --- | --- |
| `grouped_bars` | `values[series, group]`，单位为百分比；可附同形状的 `counts` 与 `(lower, upper)` | 零基线；缺失为 NaN；默认 n < 20 透明度 0.32；细误差线 |
| `radial_profile` | 每维一个 0–5 的有限值，通常是任务需求均值 | 等角扇区、同心圆标尺、分层浅色填充；值表达径向长度 |
| `response_curve` | 一维 `levels`、`successes`、`totals` | 实心观测点、二项 logistic 拟合，超出观测最大等级后为虚线 |
| `recovery_bars` | 每行恰好 1 次高分任务数、恰好 2 次高分任务数、任务总数 | 两色横条与合计比例的 Wilson 区间 |
| `rate_heatmap` | `successes[row, column]`、`totals[row, column]` | 矢量网格、百分比标签、稀疏 `†`、零分母缺失短横线 |
| `failure_pie` | 非负整数计数、同长度分类名与颜色 | 每面板内部归一化，标签和引导线随扇区放置 |

## 计数、区间与缺失

- **Wilson**：`wilson(k, n, confidence=.95)` 返回 `(rate, lower, upper)`，均为 0–1 比例；传给百分比柱图前乘 100。
- **输入边界**：k、n 必须为相同形状的有限非负整数，且 k ≤ n；不把小数分数当作成功次数。
- **零分母**：n = 0 返回 NaN，图中显示缺失；k = 0 且 n > 0 是有效零结果，仍有非零区间上界。
- **区间来源**：柱图接收的 lower/upper 必须包围对应值，并位于 0–100；不得为了画面随机生成误差条。
- **连续分数**：平均任务分数、奖励、耗时等不适用二项 Wilson 区间。使用原始样本估计合适区间，再传入图形组件，同时更改轴标题和说明。
- **小样本**：柱图默认 n < 20 半透明；热力图默认 n < 5 加 `†`。这些阈值是示例约定，项目可修改，必须在图注说明。
- **百分比标尺**：热力图固定 0–100%；当前布局省略色条，格内数值给出准确结果。不同图若使用不同色标，必须明确标注。

## 曲线拟合

- **估计目标**：`logistic_fit(levels, successes, totals, ridge=.02)` 使用分组二项对数似然，任务数作为权重，返回原始 x 单位下的 `[intercept, slope]`。
- **正则化**：默认对两个标准化坐标系系数添加显式 L2 惩罚，降低完全分离时的发散风险；不是无正则 MLE，也不是论文实验拟合的数值复刻。
- **缺失组**：n = 0 的等级不参与拟合；至少需要两个不同的有效等级。输入错误和不收敛会报错。
- **外推**：`response_curve(..., end=10)` 将观测最大等级之后的曲线画为虚线；这一区域不是观测证据。
- **解释**：曲线表示按需求分组后的任务成功率，不表示某个能力的因果效应，也不能把六条需求维度当作互不相关的独立试验。
- **锚点**：示例不添加人为“零成功”锚点。若真实研究方法需要锚点或特殊加权，调用者应显式实现并说明，不能把额外假设隐藏在绘图代码里。

## 可运行的两方法柱状图

在 skill 根目录执行，使用当前 Python 环境：

```python
from pathlib import Path
import sys
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, str(Path("scripts").resolve()))
from style2 import theme, save_pdf, footer, BLUE, TEAL
from charts import wilson, grouped_bars

# 行是方法，列是 Low / Medium / High 任务组。
successes = np.array([[42, 31, 8], [45, 38, 11]])
totals = np.array([[50, 50, 16], [50, 50, 16]])
rate, low, high = wilson(successes, totals)

with theme():
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    fig.subplots_adjust(left=.1, right=.98, bottom=.2, top=.79)
    grouped_bars(
        ax, rate * 100, ["Low", "Medium", "High"],
        ["Method A", "Method B"], [BLUE, TEAL],
        intervals=(low * 100, high * 100), counts=totals, legend=True,
    )
    ax.set_ylabel("Task accuracy (%)")
    footer(fig, "Illustrative counts · 95% Wilson intervals · translucent: n < 20")
    save_pdf(fig, "outputs/custom_comparison.pdf", title="Harness comparison")
```

## 完整布局的可替换数据

| 布局函数 | 可传参数 |
| --- | --- |
| `capability_profiles` | `demands` 为六个 `[tasks, 6]` 整数矩阵；`names` 与 `dimensions` 为六个标签。覆盖率是非零比例，均值包含零需求任务 |
| `demand_response` | `observations=(levels, successes, totals)`，形状分别为 `[levels]`、`[2,6,levels]`、`[6,levels]`；两模型默认共享每组任务数 |
| `harness_grid` | `successes` 与 `totals` 形状为 `[benchmark=3, model=3, capability=6, harness=3, group=3]`；维度或数量变化时改用基础组件重新布局 |
| `recovery_analysis` | `counts=(one, two, total, hits, ns)`；前三个数组每能力一个值，后两个为 `[6,5]` 的等级计数 |
| `failure_distributions` | `counts` 为两个长度 9 的失败计数数组；分类对应 `FAILURE_LABELS`，修改分类时同步标签与颜色 |
| `evidence_table` | `tasks=(ids, scores, demands)`；scores 为 `[tasks,3]` 的 0–1 分数，demands 为 `[tasks,6]` 的整数等级；支持 `threshold` 与 `max_rows` |

- **重复运行的一致性**：示例的横条汇总、等级热力图与任务表共享 `repeated_tasks()`。`check_charts.py` 会验证热力图分组计数与横条总计一致。
- **表格筛选**：只展示恰好一次或两次达到阈值的任务；默认 17 行，约四分之三来自两次高分组，其余来自一次高分组。图注明确是分层子集，不能用展示子集估算总体比例。
- **阈值**：判断使用未四舍五入的分数，表格仅显示三位小数。边界附近的数据可增加显示精度，避免肉眼看到相同数字却有不同底色。
- **失败分母**：饼图百分比仅基于每个面板传入的失败记录，不是全部评测任务；若要展示整体失败率，另提供总任务数。
- **复用限制**：内置布局对面板数量有明确约定；改变任务结构时优先复用基础图形，不要悄悄裁切多出的数据。
