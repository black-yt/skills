# 数据图接口与验收

## Figure 3：交替阶段曲线

`charts.figure_3(path, data=...)` 的 `data` 必须有 `MATH-500`、`MMLU`、`GPQA`、`JAMA` 四个键，每个键为 8 个按时间顺序排列的百分数。位置依次为 Day、Night、Day、Night、Day、Night、Day、Night；四个任务批次按 `MATH 200`、`MATH 200`、`MMLU 200`、`MMLU 200` 排列。前两个指标在左轴、后两个在右轴；在图例中用圆形、菱形、上三角、下三角区分。

内置 `TRAJECTORY` 是从 Figure 3 **图面数值标签人工转录**的示例，部分靠得很近的标签可能存在读数误差。它不是作者的原始记录，不要据此重新计算显著性或报告额外小数位。使用自己的数据：

```python
import sys
sys.path.insert(0, '[SKILL_DIR]/scripts')
from charts import figure_3

observed = {
    'MATH-500': [58, 61, 64, 68, 70, 72, 74, 76],
    'MMLU': [55, 57, 59, 61, 64, 67, 69, 71],
    'GPQA': [32, 34, 35, 37, 39, 42, 44, 46],
    'JAMA': [25, 27, 29, 31, 33, 35, 37, 40],
}
figure_3('my_trajectory.pdf', data=observed)
```

示例数值仅演示接口。调整任务名、批次标题或左右轴范围时编辑 `charts.py` 中的对应绘图函数，并重新验收；不要在双轴图中用相同的物理高度暗示左右数值可直接相减。

## Figure 4：参数敏感性与消融

`charts.figure_4(path, data=..., lengths=...)` 的 `data` 外层为 3 个面板；每个面板包含 `MATH-500` 和 `SciBench` 两个键，分别给出五个百分数。`lengths` 是五个互异长度，默认 `10,15,20,30,50`。默认 `ABLATION` 同样是按原图数字标签转录，不是原始实验表。

```python
import sys
sys.path.insert(0, '[SKILL_DIR]/scripts')
from charts import figure_4

results = {
    'Full method': {'MATH-500': [71, 73, 76, 78, 77],
                    'SciBench': [25, 27, 30, 31, 29]},
    'Without phase A': {'MATH-500': [66, 68, 71, 72, 70],
                        'SciBench': [23, 24, 26, 26, 25]},
    'Without phase B': {'MATH-500': [63, 65, 67, 67, 66],
                        'SciBench': [21, 22, 24, 23, 22]},
}
figure_4('my_ablation.pdf', data=results, lengths=[10, 15, 20, 30, 50])
```

所有输入百分数要求有限且在 0–100；无数据时保留缺失说明，不填 0 冒充观测。原论文图使用约 20% 的截断 y 轴；本实现柱状图从零开始，柱上数字保留论文式密排与五种纹理。若用户明确要求严格复刻轴范围，先说明视觉截断的影响，并标记轴断裂或改用点图。

## 生成、预览与验证

```bash
python3 scripts/render_examples.py --book
python3 scripts/verify_pdf.py --previews
python3 scripts/build_previews.py
```

- `render_examples.py` 支持 `--figures 1 3`、`--output-dir [OUTPUT_DIR]`。合并 `--book` 保留四页文字和矢量路径。
- `verify_pdf.py` 检查单页、文本提取、字体嵌入、ToUnicode、位图数量与标签页边界；生成 `outputs/validation.json` 和逐页 PNG。检查通过不替代人工查看线条和图例。
- `build_previews.py` 从四个 PDF 输出两张预览图集到 `assets/previews/`；更改绘图代码后重建图集，避免展示页与实际 PDF 不一致。
- 正式交付核对：文字可以选择/复制；预览无叠字、裁切或指向相反的箭头；百分数与自己的输入一一对应；图中方法名与论文正文一致；最终放在单栏或双栏时文字仍清晰。
- 安装依赖：Python 3.10+，`python3 -m pip install -r scripts/requirements.txt`；优先在独立 venv 安装，不改共享环境。无需 LaTeX 和网络图像 API。

## 原图 MSE 定位

持有可用的原图时，先运行 `verify_pdf.py --previews`，再将重绘 PNG 与原图逐像素比较。脚本只读取原图，输出放在已忽略的 `outputs/`，不把论文原图打包进 skill。

```bash
python3 scripts/compare_reference.py [ORIGINAL_FIGURE_1] outputs/previews/01_brain_analogy.png --output outputs/mse/figure-1 --grid 2 2
python3 scripts/compare_reference.py [ORIGINAL_FIGURE_2] outputs/previews/02_dual_phase_architecture.png --output outputs/mse/figure-2 --grid 3 3
```

- `metrics.json` 含 0–1 RGB MSE、MAE、0–255 RMSE、低频模糊 MSE 及每个网格的平均误差和总误差占比；`comparison.png` 并列原图、等尺寸重绘和差异热图。
- 脚本只把重绘缩放到原图尺寸，不自动裁切或配准。先排查留白、分区边界和模块尺寸，再排查字体、图标与线宽；不要靠任意移动图像掩盖真实的布局差。
- 原图的 JPEG 压缩、抗锯齿和字体栅格化都会影响原始 MSE；模糊 MSE 可辅助看大块色区和位置，但任何单一数字都不能证明方法图的语义箭头正确或达到逐像素复刻。
- 对真实矢量重绘，MSE 是定位差异的工具，不要求等于零。优先修正大片色区、模块位置、箭头和文本，再考虑线宽与抗锯齿差异；保留可编辑性，不以原图像素回拼换取零误差。
