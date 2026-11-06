# 从任务背景到可观察结果的动画

## 先写镜头合同

- **分层叙事：** 非专业观众先理解“输入是什么、为什么难、要得到什么”，再看软件操作。可用“标题 → 分层数据 → 少量切片 → 拉远看到大量数据 → 任务桥接 → GUI 操作 → 结果 → 品牌”作起点，不把这套顺序强加给所有录屏。
- **每镜头一个信息：** 第一镜头若要求纯标题，就不提前露出切片、角标或后续说明。标题淡出后才让图片和第二组文字进入；不要因共用背景而把所有图层提前显示。
- **制造对比：** 先展示少量、可辨认的完整图片，再拉远展示完整集合。第一次先铺满全部图片，会提前消耗“原始数据很多”的信息。
- **统一画布：** 有指定背景时，介绍、操作和片尾沿用同一背景；不要另加未要求的深色蒙层。设计透明素材后，需合成到实际背景检查颜色和对比度。
- **结果可见：** 最后一条交付消息应包含实际结果截图和短解释。停留从图片与文字全部出现、滚动稳定之后算起，不能从消息开始生成算起。精确时长见 [08](08_exact_timing_and_source_quality.md)。
- **样式可配置：** 深灰虚线、细长侧栏、某个特写比例或特定秒数只是可选方案。新任务先继承用户确认的样式，再调整局部，不每次另起设计。

## 科研图片与来源

- **数量说清：** 原始采集层数、重采样后数量、多个方向的派生切片和总缩略图数不是同一概念。不要把重复取样或三方向合计称作原始采集了同样多层。
- **图片不造假：** 使用合法提供的原始数据或真实截图；不通过生成图片补齐科研结果。几何示意需明确为示意，不伪装成真实采样。
- **一致显示：** 同一组切片保持一致的窗宽窗位、方向、灰度映射和物理长宽比；二维图像的像素尺寸未必等于物理比例。堆叠深度用于说明时可夸张，但不能当作精确空间尺度。
- **描述有边界：** 阈值筛选高密度区域可展示初步骨骼重建，不等同于精确组织分割或完成疾病诊断。字幕写实际观察到的结果。
- **源文件留在项目：** 数据、实际日志、原始截图、字体、音乐、logo 不随公共 skill 提交；示例只给配置与合成测试素材。

已有研究结果需要制作纹理染色、三维点云聚合/转向、局部求解与失败撤回动画时，按 [09](09_research_animation_and_evidence.md) 使用稳定图片 ID、实际坐标和候选评分；本章的堆叠展开工具不负责聚类或恢复层序。

## 同一张图片从堆叠飞到网格

`animate_cards.py` 接受 `assets/cards.example.json` 的配置。`images` 显式列表或 `images_glob` 二选一；图片数必须等于 `rows × columns`，每张有稳定身份。需要严格层序时用显式列表，避免文件名字典序把第 10 层放在第 2 层前面。

```bash
python3 "$SKILL_DIR/scripts/animate_cards.py" --config ./cards.json --preview-at 3
python3 "$SKILL_DIR/scripts/animate_cards.py" --config ./cards.json
```

- **身份连续：** 每张图片先有起始堆叠四边形、目标网格四边形，再插值移动。静止堆叠可只画代表层，遮挡剔除也可省掉不可见层，但不能用目标网格淡入冒充逐张展开。
- **两种展开合同：** `flight_scope: "all"` 为每张图片安排从堆叠到目标的移动；`"first"` 只展开首次近景子集，其余网格已在画外等待拉远。后者适合保留最后揭示的冲击力，不能用来满足“所有图片都要飞出”的要求。
- **坐标一致：** `stack.quad` 与 `depth_offset` 用画布坐标；目标网格由 `grid.rect/rows/columns/gap` 决定。`first_view` 的行列索引从 0 开始，指定矩形子集和边距。
- **镜头移动而非换图：** 近景到远景保持同一个网格与图片身份，插值相机中心和倍率；不是切换两张内容不同的蒙太奇图。
- **首屏完整：** 默认 `edge_policy: "whole"` 只显示边界完整进入视口的卡片，边缘半张直接不画。首次近景同时限制到明确子集，避免空余边距多露出几张。
- **构图计算：** 先用网格宽/列数划分等宽单元，再在每格四边各留 `gap/2`，取整后得到卡片边界；高度同理。对子集边界盒，倍率取可用画布宽/边界宽与高/边界高的较小值；同时校准中心和顶部文字安全区。只改倍率不改中心容易偏出屏幕。
- **拉远揭示：** 新进入视口的卡片完整进入后才显示；检查实际视频是否有明显跳现，必要时减小卡片尺寸或增大镜头时长。不要为藏边缘问题改成半张切片。
- **性能：** 缩略图预合成 atlas；移动卡片只变换当前包围盒，不为每张分配整幅画布。可用粗遮挡剔除减少堆叠冗余绘制，精细边缘需要更准确绘制时设 `occlusion_grid: 0` 关闭。缓存纹理和静态背景，避免逐帧解码大 PNG。
- **审计：** `.animation.json` 记录阶段帧数、参与飞行的身份、起止四边形、完整网格可见性和输入哈希；仍要抽查中间帧，清单不能替代肉眼检查运动。

## 信息流箭头

```bash
python3 "$SKILL_DIR/scripts/render_flow.py" --config ./flow.json
```

- **几何：** `assets/flow.example.json` 用水平/垂直直线加圆角，不支持任意角度折线。圆角半径不超过相邻边长的一半。粗线、圆端虚线和清楚的箭头比复杂贝塞尔装饰更易读。
- **方向：** `points` 的第一个点为来源，最后一个点为目的地；虚线相位沿弧长递增。上下两条流方向相反时反转各自路径，不能只翻转箭头图标。
- **无缝循环：** 一个周期只移动一个虚线节距，不在结尾重复首帧；线头、转角都按同一弧长计算。透明视频导出 FFV1 MKV，在 presentation 对应 overlay 设 `"loop": true`，否则 EOF 会停住。
- **时序：** 观察箭头表示屏幕输入模型，动作箭头表示模型调用工具。不要把高频装饰流动误称为精确逐工具同步；若要求逐轮高亮，用真实时间戳控制。
- **配色与文字：** 线条颜色和标签字体由配置提供；深灰适合某些浅色背景，需实际合成检查。标签尽量简短，避免与阶段标题争夺视觉中心。

## 字体、图片与片尾

- **标题层级：** 用字体文件、字重和实际 bbox 控制，标题与副标题分开。先在目标分辨率出静帧，再按真实播放尺寸检查。不要只改字号数字而忽略字体默认 Thin、行距或安全区。
- **Emoji：** 相机/工具可用独立彩色 emoji 字体；没有可用字体时用清楚的文字类别，不接受方框缺字。结构化工具卡片不能只靠 emoji 区分，见 [04](04_trace_chat_and_typography.md)。
- **透明 logo：** 保留原始 alpha，等比缩放；若 logo 与背景混杂且用户同意，加局部半透明白底和柔和投影，不把整个片尾画布刷白。
- **放大限制：** Pillow `thumbnail()` 只缩不放；需要大图标时用显式 `resize()`，但这不增加原始细节。避免不必要的锐化与拉伸。
- **可复用底板代码：** 以下只绘制用户提供的 logo 与底板，不生成或替换商标；底板位置/大小应计入安全边距。

```python
from PIL import Image, ImageDraw, ImageFilter

def logo_plate(source, size, padding=24, alpha=205, radius=24):
    logo = Image.open(source).convert("RGBA")
    scale = min(size[0] / logo.width, size[1] / logo.height)
    logo = logo.resize((round(logo.width * scale), round(logo.height * scale)),
                       Image.Resampling.LANCZOS)
    w, h = logo.width + 2 * padding, logo.height + 2 * padding
    # Shadow has its own padding, so blur is not clipped at the plate boundary.
    pad = 48
    shadow = Image.new("RGBA", (w + 2 * pad, h + 2 * pad))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (pad, pad + 6, pad + w - 1, pad + h + 5), radius, fill=(0, 0, 0, 45))
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    plate = Image.new("RGBA", (w, h))
    ImageDraw.Draw(plate).rounded_rectangle(
        (0, 0, w - 1, h - 1), radius, fill=(255, 255, 255, alpha))
    plate.alpha_composite(logo, (padding, padding))
    shadow.alpha_composite(plate, (pad, pad))
    return shadow
```
