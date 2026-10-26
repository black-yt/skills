# 来源、解析与视觉语言

## 来源与图片提取

参考论文：[LatentEvolve: Self-Evolving Test-Time Scaling in Latent Space，arXiv:2509.24771v1](https://arxiv.org/abs/2509.24771v1)。本 skill 对照的是 v1，不把之后可能更新的版本视为同一视觉证据。

本轮先对用户提供的 20 页 PDF 运行 `structai.read_pdf([PAPER.pdf])`，解析正文 Markdown 和 `img_paths`；然后根据 `full.md` 紧邻的 Figure 标题定位四张原图。若要在另一份 PDF 中重做这个步骤，安装与认证流程见独立的 `pdf-parsing` skill；此 skill 的绘图运行不需要 MinerU。原图保留在用户自己的解析目录，**不随本 skill 发布**。

| 原论文 | PDF 页码 | 图片中的主结构 | 本 skill 的重绘 |
| --- | ---: | --- | --- |
| Figure 1 | 2 | 左右对应“人脑”与 LatentEvolve，上下对应快召回与慢巩固，四象限和昼夜色块 | `01_brain_analogy.pdf` |
| Figure 2 | 4 | 任务→冻结 LLM→latent 序列→迭代 rollout；buffer→weaver→新 latent；昼夜大分区 | `02_dual_phase_architecture.pdf` |
| Figure 3 | 8 | 8 个 Day/Night 交替阶段，MATH/MMLU 左轴与 GPQA/JAMA 右轴 | `03_day_night_trajectories.pdf` |
| Figure 4 | 9 | Full、w/o Daytime、w/o Nighttime 三栏；每栏 2 个数据集 × 5 个长度 | `04_latent_ablation.pdf` |

可复查图片与标题的对应关系：

```bash
python3 - <<'PY'
from pathlib import Path
import re
md = Path('[PARSED_DIR]/full.md').read_text(encoding='utf-8')
for path, n in re.findall(r'!\[\]\((images/[^)]+)\)\s*\nFigure ([1-4]):', md):
    print('Figure', n, Path('[PARSED_DIR]') / path)
PY
```

`[PARSED_DIR]` 是 PDF 旁的解析结果目录占位符。解析输出是参照材料，不是独立复现证明；复杂图还需回到 PDF 页渲染确认边界和图注。

## 色彩与结构

| 语义 | 代表色 | 用法 |
| --- | --- | --- |
| 昼间/快适配 | 浅珊瑚 `#F8DCDD`、深珊瑚 `#B85C61` | 上方记忆类比、交替曲线底色、流程强调 |
| 夜间/慢巩固 | 淡蓝 `#DDEBF7`、深蓝 `#3A6791` | 下方记忆类比、夜间半区、缓冲与回流 |
| LLM/任务 | 浅绿 `#C8E5D1`、深绿 `#5C8763` | 冻结模型、源任务与已学习技能 |
| latent/中间结果 | 青绿 `#97CFCC`、淡黄 `#F4E6AD` | latent 序列、几何 latent 块、合并结果 |
| buffer/weaver | 淡紫 `#D8CBE8`、紫 `#8063A4` | episodic buffer 与跨任务整合 |

- **方法图**：分区底色低饱和；卡片、图标和箭头只对矢量路径施加轻微笔迹波动，文字保持规则基线。左上坐标系便于按论文结构改节点位置；不要对底色或文字施加随机抖动。
- **统计图**：白色数据画布、轻网格、点型与色彩共同区分系列。Figure 3 用交替底色和左右双轴；Figure 4 用五种低饱和填充及纹理。
- **字体**：Figure 1/2 默认使用 DejaVu Serif，Figure 3/4 使用 DejaVu Sans。方法图同级标题、卡片标题和正文分别保持一致字号；居中的多行文字显式统一对齐，左对齐任务卡使用同一左边距。PDF 嵌入 TrueType 字体与 Unicode 映射；最终版心下仍须检查微小标签可读性。
- **可选手写字体**：`assets/fonts/Kalam-Regular.ttf`、`Kalam-Bold.ttf` 来自 [Google Fonts Kalam](https://github.com/google/fonts/tree/main/ofl/kalam)，按随附的 [`OFL.txt`](../assets/fonts/OFL.txt) 分发。`diagram_theme(font_family="Kalam")` 可选用；局部图元代码会注册字体，无需从系统另行安装。
- **图标**：大脑、日月和 latent 立方体是 Matplotlib 绘制的新矢量形状；没有复用论文中的像素图标或嵌入源图。

## 适配与差异

- Figure 1/2 保留过程拓扑、主色分区与主要细节：记忆云中的文档、三份技能文件、episodic buffer 中的 latent 块、冻结标记、序列截断、三路 rollout、动量迁移、weaver 和高置信子集。图标和轮廓改为轻微手绘感的矢量路径，部分长句改成较短标签；这是结构重绘而非逐像素临摹。
- Figure 3/4 的数值来自图面文字；读不清或无法判定的数值不能据此当成原始研究数据。最终写作应优先采用作者公开的表格或用户自己的数据文件。
- Figure 4 原图的视觉 y 轴从约 20% 开始。这里从 0% 画柱，避免截断柱长造成夸大；因此柱高比例不会与原截图完全一致。
