# 独立示例与验收

## 先看什么

先查看 [skill 入口的 8 张效果预览](../SKILL.md#效果预览)，无需安装依赖即可了解输出质量。运行示例后可打开 `outputs/examples.pdf` 查看全部 17 页成品。每页对应一个完整的新用户需求，无需阅读参考论文，也不需要原图作输入。统计示例在页脚明确标注虚构演示数据，区间不是计算得到的置信区间。

| 场景 | 模拟用户需求 | 代码 | 输出 |
| --- | --- | --- | --- |
| `pipeline` | 为论文画五阶段研究流程，从研究问题到可信证据，说明每阶段的输入与产物。 | [research_pipeline.py](../scripts/examples/research_pipeline.py) | `outputs/research_pipeline.pdf` |
| `architecture` | 为检索增强系统画架构图，展示知识源、可选模块和四个可验证的系统能力。 | [system_architecture.py](../scripts/examples/system_architecture.py) | `outputs/system_architecture.pdf` |
| `factory` | 为评测任务生成方法画流程图，展示模板适配、候选任务和七类任务覆盖范围。 | [task_factory.py](../scripts/examples/task_factory.py) | `outputs/task_factory.pdf` |
| `validation` | 展示任务质量控制，明确参考解、扰动解与运行故障得到怎样的不同判定。 | [validation_matrix.py](../scripts/examples/validation_matrix.py) | `outputs/validation_matrix.pdf` |
| `learning` | 展示统一实验接口如何产生可验证记录，供模型比较、监督学习和策略优化复用。 | [learning_loop.py](../scripts/examples/learning_loop.py) | `outputs/learning_loop.pdf` |
| `leaderboard` | 比较十五种研究助手的完成率，用实心柱、误差线、两行标签和家族图例展示排名。 | [evaluation_leaderboard.py](../scripts/examples/evaluation_leaderboard.py) | `outputs/evaluation_leaderboard.pdf` |
| `model-logos` | 给十个模型家族的柱状图加入对应 logo，保留原图透明度、独立文字与演示数据说明。 | [model_leaderboard.py](../scripts/examples/model_leaderboard.py) | `outputs/model_leaderboard.pdf` |
| `budget` | 按四个方法家族画完成率随时间预算增长的阶梯曲线，配区间带和不同线型。 | [budget_profiles.py](../scripts/examples/budget_profiles.py) | `outputs/budget_profiles.pdf` |
| `efficiency` | 同时查看成功率与成本、耗时、token 的关系；成本使用对数轴，每个面板独立计算 Pareto 前沿。 | [efficiency_frontier.py](../scripts/examples/efficiency_frontier.py) | `outputs/efficiency_frontier.pdf` |
| `gains` | 展示多基准训练前后结果、样本数和表内增益条，用带零参考线的森林图展示正负变化。 | [benchmark_gains.py](../scripts/examples/benchmark_gains.py) | `outputs/benchmark_gains.pdf` |
| `training` | 用两行五列小图呈现两个实验的奖励、截断率、token、熵和留出集前后变化，保留逐步波动。 | [training_dashboard.py](../scripts/examples/training_dashboard.py) | `outputs/training_dashboard.pdf` |
| `outcomes` | 按同一方法顺序对齐六列横条，比较失败类别、耗时与重复不稳定性，保留各列单位。 | [failure_outcomes.py](../scripts/examples/failure_outcomes.py) | `outputs/failure_outcomes.pdf` |
| `domains` | 用四列横条展示不同任务领域的能力与区间，第五列显示相对参考方法额外完成的任务数。 | [domain_specialization.py](../scripts/examples/domain_specialization.py) | `outputs/domain_specialization.pdf` |
| `mechanisms` | 用成组横条比较失败归因，再用任务卡汇合与两条修复轨迹解释共同错误。 | [failure_mechanisms.py](../scripts/examples/failure_mechanisms.py) | `outputs/failure_mechanisms.pdf` |
| `coverage` | 用粉彩双环图展示七类任务与十四个子领域，旁边以横条展示能力概览。 | [coverage_overview.py](../scripts/examples/coverage_overview.py) | `outputs/coverage_overview.pdf` |
| `runtime` | 展示异步学习阶段、工作进程、GPU/CPU 资源池和物理节点的分层架构。 | [resource_runtime.py](../scripts/examples/resource_runtime.py) | `outputs/resource_runtime.pdf` |
| `cycle` | 用双向循环连接能力构建与科学实践，展示八个阶段如何经过统一研究平台形成反馈。 | [research_cycle.py](../scripts/examples/research_cycle.py) | `outputs/research_cycle.pdf` |

## 运行命令

在本 skill 根目录使用已满足 [requirements.txt](../scripts/requirements.txt) 的 Python 环境。以下示例沿用 `.venv/bin/python`；不依赖任何原始 PDF 或图片。

```bash
# 列出示例需求，不写入文件
.venv/bin/python scripts/render_examples.py --list

# 全部 17 个单页 PDF，以及 17 页 PDF 合集
.venv/bin/python scripts/render_examples.py --book

# 只生成十个含统计结果的示例及合集
.venv/bin/python scripts/render_examples.py --group statistics \
  --book --book-name statistics.pdf

# 浏览统计扩展示例，包括 logo 柱状图、资源架构和循环概念图
.venv/bin/python scripts/render_examples.py --group extension \
  --book --book-name statistics_gallery.pdf

# 只选择两个场景
.venv/bin/python scripts/render_examples.py --examples pipeline learning

# 单独运行一份示例，覆盖输出路径和物理宽度
.venv/bin/python scripts/examples/system_architecture.py \
  --output outputs/custom_architecture.pdf --width-in 7.2

# 柱状图同样支持独立运行
.venv/bin/python scripts/examples/evaluation_leaderboard.py \
  --output outputs/custom_leaderboard.pdf

# 检查 PDF 并生成目视检查用预览
.venv/bin/python scripts/verify_pdf.py --previews
```

- **工作目录**：脚本通过自身位置寻找绘图库和默认输出目录，可从其他工作目录运行；显式传入的相对输出路径按当前工作目录解析。
- **重新运行**：同名生成物会重新生成；用户手工修改过的 PDF 应另存文件名，或使用 `--output` / `--output-dir`。
- **保留可编辑性**：`--book` 用 PDF 页合并生成合集，不是将页面截图后拼接。
- **分组**：`diagrams` 含七个方法/系统示例，`statistics` 含十个统计示例，`extension` 含十二个扩展示例，`all` 含全部十七例。`--examples` 和 `--group` 二选一；不指定时生成全部。
- **合集命名**：`--book-name` 只接受 `.pdf` 文件名，不能包含目录或与本批单页文件重名；输出位置使用 `--output-dir` 控制。
- **生成物目录**：示例 PDF、逐页检查图与验证报告都在 `outputs/` 下，由 `.gitignore` 排除；分发时保留代码、`assets/` 内的 logo 和两张精选预览、依赖及参考文档。

## 重新生成预览图集

[build_previews.py](../scripts/build_previews.py) 将八个示例的单页 PDF 转成两张 2×2 PNG。图集只展示这些代码的成品，没有原论文图片或对照图。

| 图集 | 第一行（左 → 右） | 第二行（左 → 右） | 文件 |
| --- | --- | --- | --- |
| 方法结构与任务总览 | `pipeline`、`architecture` | `runtime`、`coverage` | [01_methods_and_coverage.png](../assets/previews/01_methods_and_coverage.png) |
| 模型评估与训练统计 | `model-logos`、`budget` | `efficiency`、`training` | [02_evaluation_and_training.png](../assets/previews/02_evaluation_and_training.png) |

在 skill 根目录运行：

```bash
# 从可复用示例代码生成八个源 PDF
.venv/bin/python scripts/render_examples.py --examples \
  pipeline architecture runtime coverage model-logos budget efficiency training

# 从现有 PDF 重建两张随 skill 分发的预览
.venv/bin/python scripts/build_previews.py

# 可选：把临时图集写入本地输出目录
.venv/bin/python scripts/build_previews.py \
  --output-dir outputs/contact-sheets --tile-width 1440 --renderer pymupdf
```

- **渲染方式**：默认优先调用系统 `pdftoppm`，未安装时使用已有 PyMuPDF 依赖；无需为预览单独安装系统工具。`--renderer` 可显式选择。
- **画幅与清晰度**：每个示例默认渲染为 1440 像素宽，等比居中排列，完整保留标题、坐标、图例和页脚。图集编号为 01–08，对应上表阅读顺序。
- **位置**：`--pdf-dir` 指定源 PDF 目录，默认为本 skill 的 `outputs/`；`--output-dir` 默认为本 skill 的 `assets/previews/`，可以从其他工作目录运行。
- **重建行为**：默认只更新两张固定命名的 PNG；源 PDF 缺失或不是单页时明确报错，不改动原 PDF。
- **分发边界**：两张 `assets/previews/` PNG 是可公开浏览的固定展示资产，保存在 Git 中；逐页检查图和 PDF 继续留在 ignored 的 `outputs/`。
- **验收**：重新生成后打开两张图集，检查八个面板完整、文字可辨、比例正常。预览是栅格图，不能替代可复制文字的 PDF 交付文件。

## 替换为自己的数据

- **共享数据**：[demo_data.py](../scripts/demo_data.py) 提供排行榜、预算曲线、成本散点和能力概览共用的方法名称、家族颜色和终点数值。修改其中一项时，检查所有使用它的示例。
- **场景数据**：增益表的 `CORE / TRANSFER / EFFECTS`、领域矩阵的 `DOMAINS`、归因图的 `CATEGORIES / PLANNING / SEARCH`、双环图的 `GROUPS` 均在对应示例文件开头。
- **模型标识**：`model-logos` 的 `ROWS` 独立于虚构研究助手数据，使用模型家族名称与对应 logo；调用方式和资产清单见 [模型 logo](05_model_logos.md)。
- **训练轨迹**：`training_trace()` 使用固定随机种子生成演示轨迹；真实任务应读入逐步日志，不要继续调用该生成器。
- **真实结果**：提供实际数值及区间上下界，按 [统计 API 与数据语义](04_statistical_charts.md) 处理分母、单位、共享任务 ID 与缺失值。将演示页脚换成真实的数据来源和区间定义。
- **可复用层次**：绘图通用组件在 `charts.py`；示例中的 `draw(output, **options)` 负责布局与场景文字。换图时优先改数据和标签，新增版式再调整 `draw()`。

## 自动检查

[verify_pdf.py](../scripts/verify_pdf.py) 验证实际输出文件：

- **文本**：每页能提取到足够正文；没有空字符或 Unicode 替换字符；指定 `--expect` 时能完整恢复关键短语。
- **字体**：实际使用的字体有嵌入数据和 `ToUnicode` 映射。
- **位图**：默认仅允许与内置 logo 像素及 alpha 完全一致的小图标；仍报告实际位图数并拒绝未知图片。`--strict-vector` 要求没有任何 `fill-image` 或 Image XObject，含 PNG logo 的示例会被该严格模式拒绝。
- **渐变**：页面有 `fill-shade`，背景来自 PDF 原生 shading。
- **边界**：文字包围盒位于页面边界内。
- **失败**：任一项不通过时退出码为 1，并将具体问题写入 `outputs/validation.json`；修复对应问题后重跑。

```bash
.venv/bin/python scripts/verify_pdf.py outputs/learning_loop.pdf \
  --expect "Independent evaluation" \
  --expect "Verified experiment record"
```

**PyMuPDF 检查细节**：部分版本会在 `get_image_info()` 中将原生 shading 临时表示为 `xref=0` 的图像，用于文本/图像提取。这不等同于 PDF 内嵌了 PNG。应结合实际 `fill-image` 绘制操作、Image XObject 与 shading 资源判定，不能只看该方法返回的数量。

修改统计组件后，可运行数值与 PDF 行为检查。它会检查线性/对数距离、Pareto 支配与并列点、零基线、区间、数据长度、演示曲线终点和实际半透明渲染。

```bash
.venv/bin/python scripts/check_charts.py
```

## 目视验收

- **整体**：渐变连续、色彩浅而可辨，卡片和图标保持一致的视觉语言。
- **文字**：标题、节点、说明和短注释有清晰层级；字符不贴边、不遮挡、不错行。
- **连线**：流向符合方法语义；分支与汇合位置清楚，箭头不穿过标签。
- **统计图**：查看刻度、误差线端帽、区间带透明度、图例顺序和标注位置。多列横条必须按同一行顺序对齐；不同单位不能共用一个数值范围。
- **印刷尺寸**：按论文最终放置宽度查看，不能只在大屏放大状态下检查小字。
- **复制验证**：在 PDF 阅读器中选取一个完整节点标签，确认可搜索、可复制；同时运行提取检查。
- **预览用途**：PNG 只用于检查和快速展示；用户最终插入论文的文件使用 PDF。

自动检查不能证明节点之间没有遮挡或图中科学关系正确，交付前仍要检查成品和用户原始材料。
