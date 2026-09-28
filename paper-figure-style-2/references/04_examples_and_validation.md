# 示例、预览与验收

## 先看成品

直接打开 [效果预览](../SKILL.md#效果预览)，即可查看代码实际生成的九个成品示例，不需要先安装依赖或阅读参考论文。

| 场景键 | 模拟用户需求 | 独立示例代码 | 默认 PDF 文件名 |
| --- | --- | --- | --- |
| `overview` | 展示评测集、Harness、执行环境、控制层和分析层如何连接 | [component_overview.py](../scripts/examples/component_overview.py) | `component_overview.pdf` |
| `lifecycle` | 展示从排队到清理资源的四阶段流程及异常路径 | [evaluation_lifecycle.py](../scripts/examples/evaluation_lifecycle.py) | `evaluation_lifecycle.pdf` |
| `profiles` | 比较六组任务的能力覆盖率与平均需求等级 | [capability_profiles.py](../scripts/examples/capability_profiles.py) | `capability_profiles.pdf` |
| `response` | 对比两个模型随能力需求提高时的成功率变化 | [demand_response.py](../scripts/examples/demand_response.py) | `demand_response.pdf` |
| `harness` | 按评测集、模型、能力和难度分层比较三个 Harness | [harness_grid.py](../scripts/examples/harness_grid.py) | `harness_grid.pdf` |
| `recovery` | 找出三次运行中偶尔能达到高分的任务分组 | [recovery_analysis.py](../scripts/examples/recovery_analysis.py) | `recovery_analysis.pdf` |
| `failures` | 对比研究任务与代码任务中的失败类别组成 | [failure_distributions.py](../scripts/examples/failure_distributions.py) | `failure_distributions.pdf` |
| `interface` | 在论文中用五个可编辑界面面板说明产品使用流程 | [interface_walkthrough.py](../scripts/examples/interface_walkthrough.py) | `interface_walkthrough.pdf` |
| `evidence` | 列出三次运行分数、达标次数与任务需求等级 | [evidence_table.py](../scripts/examples/evidence_table.py) | `evidence_table.pdf` |

## 运行命令

在 skill 根目录执行；下例使用独立虚拟环境。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt

# 全部九个示例与保留文字的 PDF 合集
.venv/bin/python scripts/render_examples.py --book

# 只生成指定场景
.venv/bin/python scripts/render_examples.py --examples overview lifecycle profiles

# 单独执行一个示例，指定文件与物理宽度
.venv/bin/python scripts/examples/recovery_analysis.py \
  --output outputs/recovery_for_paper.pdf --width-in 7.2

# 在其他目录交付选中的示例
.venv/bin/python scripts/render_examples.py --examples response evidence \
  --output-dir outputs/selected --book
```

- **默认输出**：以 skill 文件所在位置计算 `outputs/`，不受当前工作目录影响。
- **相对参数**：显式传入的 `--output`、`--output-dir`、`--pdf-dir` 相对执行命令的工作目录解释。
- **合集**：`--book` 将本次选择的 PDF 页合并为 `examples.pdf`；如果只选两个场景，合集就只有两页。
- **宽度**：`--width-in` 必须为正的有限数，默认 11；绘图内容等比缩放。密集矩阵不适合直接压入小尺寸单栏。
- **数据替换**：示例调用可复用布局；真实数据的函数签名见 [统计 API](03_statistical_api.md)，新架构拓扑见 [绘图 API](02_diagram_api.md)。

## PDF 检查

```bash
# 检查所有本地 PDF，同时生成逐页 PNG
.venv/bin/python scripts/verify_pdf.py --previews

# 检查某个文件，并确认关键标签可提取
.venv/bin/python scripts/verify_pdf.py outputs/evaluation_lifecycle.pdf \
  --expect "Resource Reclamation" --expect "Runtime Interface"

# 检查区间、拟合、缺失值、共享任务计数及真实 PDF 对象
.venv/bin/python scripts/check_charts.py
```

- **文字**：提取结果应包含标题、标签和表格数字，不含替代字符或空字符；所有实际使用的字体必须嵌入并提供 ToUnicode。
- **矢量**：检查页面 image 资源和实际位图绘制操作。本 skill 的 PDF 不允许位图，包括热力图和界面示例。
- **页面边界**：检测文字边框是否超出 PDF 画布；检查报告为 `outputs/validation.json`。
- **图像预览**：从最终 PDF 渲染，保存在 `outputs/previews/`。可复制文字并不能证明无重叠，必须目视检查标题、图例、外标注和表格。
- **统计检查**：七项自动检查覆盖 Wilson 已知数值与边界、logistic 参数恢复、横条/热力图共享计数、缺失与零的区别、小样本透明度、扇区几何、矢量热力图和物理尺寸缩放。

## 重建随附 PNG

```bash
.venv/bin/python scripts/render_examples.py --book
.venv/bin/python scripts/build_previews.py

# 可选：不依赖系统 Poppler，使用已有 PyMuPDF
.venv/bin/python scripts/build_previews.py \
  --renderer pymupdf --output-dir outputs/contact-sheets --tile-width 1600
```

| 预览资产 | 内容 |
| --- | --- |
| [01_systems_and_profiles.png](../assets/previews/01_systems_and_profiles.png) | 2×2：组件总览、生命周期、能力画像、产品界面 |
| [02_diagnostics_and_evidence.png](../assets/previews/02_diagnostics_and_evidence.png) | 2×2：响应曲线、重复运行、失败组成、任务证据 |
| [03_harness_grid.png](../assets/previews/03_harness_grid.png) | 单张完整的 54 面板矩阵，避免拼进图集后文字过小 |

- **渲染器**：默认优先 `pdftoppm`；未安装时使用已有的 PyMuPDF，不要求额外安装系统软件。
- **像素**：每个图集单元默认 1600 像素宽；矩阵默认 2400 像素宽。保留完整画幅与长宽比，不裁切、不拉伸。
- **更新**：只有九个源 PDF 均存在并能正常渲染时，才替换三张固定命名的预览资产。脚本不更改源 PDF。
- **分发**：三个精选 PNG 放在 `assets/previews/`；PDF、验证 JSON 和逐页检查 PNG 留在本地 `outputs/`。
- **独立性**：整个 skill 拷贝到其他目录后即可运行；代码不读取原论文、不访问外部服务，也不引用 `paper-figure-style-1`。

## 失败处理

- **缺依赖**：使用运行脚本的同一个 Python 执行 `-m pip install -r scripts/requirements.txt`，优先独立虚拟环境，不修改共享环境。
- **缺源 PDF**：先运行对应示例；预览构建器列出缺失文件名，不拿旧 PNG 伪装最新结果。
- **缺字或文字过长**：换用覆盖字符的字体、缩短标签或扩大布局后重新生成；不要把文本栅格化来绕过检查。
- **非法计数或区间**：先修正分母、数组形状和单位；不能静默截断、把缺失填零或修造误差条。
- **拟合不收敛**：检查有效等级、完全分离和任务量；记录使用的正则化值，必要时只展示观测点，不画未经解释的趋势线。
- **视觉拥挤**：拆分面板、减少展示行或增大画布；修改后重新导出 PDF 并渲染检查。
