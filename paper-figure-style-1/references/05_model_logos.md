# 模型 logo 与柱状图

## 内置资产

模型 logo 原样复制自本仓库 `ai-conference-paper-writing/assets/logos/models/`，存放在本 skill 的 [assets/logos/models/](../assets/logos/models/) 中。使用时只需当前 skill，无需访问论文写作 skill 或联网下载。

| `provider` 标识 | 默认文字 | PNG 资产 |
| --- | --- | --- |
| `anthropic` | Claude | [anthropic.png](../assets/logos/models/anthropic.png) |
| `openai` | GPT | [openai.png](../assets/logos/models/openai.png) |
| `gemini` | Gemini | [gemini.png](../assets/logos/models/gemini.png) |
| `deepseek` | DeepSeek | [deepseek.png](../assets/logos/models/deepseek.png) |
| `qwen` | Qwen | [qwen.png](../assets/logos/models/qwen.png) |
| `glm` | GLM | [glm.png](../assets/logos/models/glm.png) |
| `kimi` | Kimi | [kimi.png](../assets/logos/models/kimi.png) |
| `grok` | Grok | [grok.png](../assets/logos/models/grok.png) |
| `mimo` | MiMo | [mimo.png](../assets/logos/models/mimo.png) |
| `minimax` | MiniMax | [minimax.png](../assets/logos/models/minimax.png) |

- **素材保真**：保留原图比例、透明度和颜色；不重绘、不拉伸，也不将 logo 改色成柱体颜色。
- **标识含义**：logo 对应模型家族/provider，不能挂到无关模型或虚构方法名上。系统有多个模型时，明确标识的是哪个模型。
- **标签保留**：模型名称、版本、分数和坐标仍用文本绘制，不能只靠 logo 让读者猜名称。
- **PDF 类型**：仅 logo 是嵌入的小尺寸 PNG；柱体、误差线、背景和文字仍保持原生 PDF 对象。含 logo 的成品不能称为“零位图”或“全矢量”。

## 运行示例

在 skill 根目录执行：

```bash
.venv/bin/python scripts/render_examples.py --examples model-logos
.venv/bin/python scripts/verify_pdf.py outputs/model_leaderboard.pdf \
  --expect "DeepSeek" --expect "Task success (%)" --previews
```

也可独立运行 [model_leaderboard.py](../scripts/examples/model_leaderboard.py)：

```bash
.venv/bin/python scripts/examples/model_leaderboard.py \
  --output outputs/models.pdf --width-in 7.2
```

- **示例内容**：十个真实模型家族名称，配虚构数值和区间；标题下方与页脚都明确说明是演示数据。排列顺序不代表真实模型能力。
- **数据替换**：修改示例的 `ROWS`，或调用 `draw(output, rows=...)`。每行包含 `provider / value / low / high`，可选 `label` 指定具体版本，换行用 `\n`。
- **坐标范围**：示例纵轴为 `0–80%`。真实数值或区间超过该范围时，修改 `Axes` 的上限和刻度，不能裁掉超出的部分。
- **标签过长**：用两行版本名、加宽画布或减少一页内的模型数；`max_width` 会报出拥挤标签。

## 复用绘制接口

[model_logos.py](../scripts/model_logos.py) 提供 `MODEL_LOGOS`、`logo_path()` 与 `draw_model_logo()`。在已有统计图的柱循环中调用：

```python
from model_logos import draw_model_logo

# axis / f 是已有的 Axes 与 Figure；i 是当前柱的类别中心。
draw_model_logo(f, "openai", axis.sx(i), 264, size=18)
f.text(axis.sx(i), 291, "GPT", size=10.5, align="center")
```

- **定位**：`cx / cy` 表示图标中心，沿用 `Figure` 的左上原点坐标。`size` 是正方形容器边长，默认 17，单位为逻辑坐标。
- **大小**：常用 16–20；接口上限为 32。宽高保持比例，透明背景直接露出图表底色。
- **路径**：从模块自身位置定位 `assets/`，与运行命令的当前目录无关。复制代码到独立工程时，同时保留 `scripts/model_logos.py` 和旁边的 `assets/logos/models/` 目录层级。
- **失败**：未知标识、缺少文件、超大图标或越出页面时明确报错，不静默用其他品牌替换。

## PDF 校验

- **默认检查**：继续验证可提取文字、字体嵌入、ToUnicode、原生 shading 与文字边界。
- **logo 例外**：解码 PDF 图像及 alpha 蒙版，与内置原始 logo 的 RGB/alpha 像素逐一匹配；同时要求每次放置不超过页面宽度的 6%，且完全位于页面内。
- **报告**：`validation.json` 分别记录实际位图数和通过校验的 `model_logos`，不把 PNG logo 宣称为矢量。
- **拒绝范围**：未知位图、替换过的透明度、放大为背景的 logo、未匹配到 logo 的图像绘制操作仍会失败。
- **严格模式**：需要确认零位图时加 `--strict-vector`。它会拒绝含 PNG logo 的示例；其他纯矢量示例仍应通过。
