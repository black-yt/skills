# 可运行配方与验收

## 从配置建立项目

把所需 `assets/*.example.json` 复制到自己的工作目录并去掉 `.example`；不要直接改 skill 安装目录中的模板。媒体路径和字体路径必须替换为实际存在的文件。

| 配置 | 输入/输出与用途 |
| --- | --- |
| `edit-plan.example.json` | 原片、源时间 cuts、输出 fps 与编码；从原片重建剪辑版 |
| `cycles.example.json` | 只供已确认周期区间的分析尺寸、信号 ROI、静态区与光标遮罩 |
| `trace.example.json` | JSONL、时间锚点、可选 EDL 和明确校准的鼠标网格 |
| `events.example.json` | 可直接编辑的合成消息与源像素鼠标轨迹，不需要某个专有 harness |
| `chat.example.json` | 对话尺寸、字体、身份、任务摘要；输出独立连续消息视频 |
| `captions.example.json` | 阶段、正文、起止时间、字重、字号和透明 strip；默认没有外部字幕 |
| `presentation.example.json` | 背景、主窗/辅窗裁切、外框、退场、特写、文字图层位置 |
| `cards.example.json` | 图片清单、堆叠四边形、网格、近景子集、全部/部分展开与拉远阶段 |
| `flow.example.json` | 透明圆角虚线信息流、方向、标签与循环节距 |
| `master.example.json` | 原片裁切和 EDL → FFV1 母版，原生像素逐帧验证 |
| `retiming.example.json` | 固定总帧数、弹性片段、明确交付停留与品牌时长 |
| `rich-events.example.json` | 合成的用户任务、观察截图、公开工具调用与结果图片事件 |
| `rich-chat.example.json` | 富卡片类别、公开参数白名单、截图高度与窄侧栏字体 |
| `audio.example.json` | 原声、音乐、现成旁白、偏移与 ducking；只重新编码音频 |

典型顺序：

```bash
SKILL_DIR="/path/to/screen-demo-video-editing"
python3 "$SKILL_DIR/scripts/edit_timeline.py" render --plan ./edit-plan.json
python3 "$SKILL_DIR/scripts/prepare_trace.py" --config ./trace.json --output ./events.json
python3 "$SKILL_DIR/scripts/render_overlays.py" chat --config ./chat.json
python3 "$SKILL_DIR/scripts/render_overlays.py" captions --config ./captions.json
python3 "$SKILL_DIR/scripts/render_presentation.py" --config ./presentation.json --preview-at 3.5
python3 "$SKILL_DIR/scripts/render_presentation.py" --config ./presentation.json --duration 5
# 短测会写入配置的 output；之后完整导出需显式覆盖这个派生文件。
python3 "$SKILL_DIR/scripts/render_presentation.py" --config ./presentation.json --overwrite
python3 "$SKILL_DIR/scripts/mix_audio.py" --config ./audio.json
python3 "$SKILL_DIR/scripts/validate_export.py" ./final.mp4 --burned-only \
  --compare-video ./presentation.mp4 --report ./delivery.json
```

普通无日志录屏可省略 trace/chat：去掉 `secondary`，直接在 `camera.moves` 写已校准的鼠标点；不需要字幕时省略 `overlays`。不需要剪时间时直接把原视频作为 presentation 的 source。

## 合成素材回归

```bash
python3 "$SKILL_DIR/scripts/smoke_test.py" --work-dir ./video-smoke --ffmpeg /path/to/ffmpeg
```

该脚本生成自己的彩色界面、指针、周期信号、消息和测试音频，不需要本次科研数据、录屏、歌曲、字体文件副本、logo 或账号。它验证的是处理链及实际像素/音频行为，不伪装成临床、科研或 TTS 能力评估。结果留在指定测试目录，便于实际查看。

## 动画、母版和精确时长回归

```bash
python3 "$SKILL_DIR/scripts/smoke_animation.py" --work-dir ./animation-smoke \
  --ffmpeg /path/to/ffmpeg --font /path/to/ChineseFont.ttf
```

目录必须是新建或空目录；测试只生成合成图片、录屏、日志和结果，不依赖真实数据。第二组测试检查实际解码像素：每张卡片身份、近景/全景完整边界、全部与子集展开、虚线方向与循环透明度、原生像素无损母版、复制前缀、精确帧预算、交付末帧停留、富卡片白名单和常驻侧栏。报告保存在 `animation_smoke_report.json`，不是只看 FFmpeg 退出码。

按需建立完整链路，避免为简单剪辑引入全部步骤：

```bash
python3 "$SKILL_DIR/scripts/animate_cards.py" --config ./cards.json
python3 "$SKILL_DIR/scripts/render_flow.py" --config ./flow.json
python3 "$SKILL_DIR/scripts/lossless_master.py" --config ./master.json
# presentation 使用已对齐的主画面/聊天；需要后续调速时输出 FFV1 MKV。
python3 "$SKILL_DIR/scripts/render_presentation.py" --config ./presentation.json
python3 "$SKILL_DIR/scripts/retime_video.py" --config ./retiming.json
# audio 的 video 指向调好时长的 MP4，复制视频流加入声音。
python3 "$SKILL_DIR/scripts/mix_audio.py" --config ./audio.json
```

配置字段/镜头设计见 [07](07_storyboard_and_animation.md)，源画质证据与时间映射见 [08](08_exact_timing_and_source_quality.md)。程序测试通过后还需检查自己的实际素材：长中文、极窄聊天面板、特定 logo 透明边缘和复杂 CT 纹理都不能由合成测试代替。

## 科研结果动画回归

```bash
python3 "$SKILL_DIR/scripts/smoke_research_animation.py" --work-dir ./research-animation-smoke \
  --ffmpeg /path/to/ffmpeg --font /path/to/ReadableFont.ttf
```

使用同一组 NumPy/Pillow 依赖，不需要 SciPy、患者数据或分析模型；目录须为新建或空目录。`research_animation.py` 作为可导入的展示模块提供染色、统一坐标缩放、刚体相机插值、像素间距/遮挡报告及稳定 ID 插值，具体接口见 [09](09_research_animation_and_evidence.md)。此测试的特征和候选均为合成数据，不评价任何真实模型。

检查源纹理未变、alpha 保留、相机正交与距离不变（含半周转向）、屏幕间距与直接计算一致、重复/丢失 ID 和非法相机被拒绝；再导出 6 秒 FFV1，比较 6 个实际解码帧与期望画面，并逐帧核对末尾 20 帧完全静止。输出 `research-smoke.json`、`research-display.mkv`、`contact.jpg` 和实际抽帧，需查看失败提示、撤回、局部重排与最终合并的连续运动。该检查不能替代项目自己的数据/对话时序及完整交付测试。

## 覆盖与交付清单

| 能力/历史问题 | 需要的可观察证据 |
| --- | --- |
| 静止压缩、真实开场、头尾裁切 | 源时间 EDL、首次运动前的原始连续画面、成片时长与音频时长 |
| 周期闪烁、插入符造成误判 | 周期信号、遮罩前后差异、参数变化被保留、相位接缝画面 |
| 双画面素材拆分 | 解码宽高、同步时间、metadata 模式开中末像素哈希，不以文件大小判断 |
| 悬浮、圆角、投影与移动 | 实际连续视频的边界、投影与主体同步、布局比例和留白 |
| 连续特写与鼠标跟随 | 全景/局部切换有目的，边缘无黑边，相邻操作不反复呼吸 |
| 动态缩放只改变投影 | 转场中/后实际帧对照对应静帧，固定画布的 RGB 与 mask 一起变化 |
| 退场截断消息或视频 | 第二轮执行反馈时触发移动，独立消息源在之后继续推进，主片时长不变 |
| 字体与字幕 | 中文字形完整、可变字重明确、正文单行不溢出、标题和正文都不遮挡 UI |
| 播放器叠出大字幕 | 从 MP4 直接解码与播放器截图对照；烧入交付无额外轨道、无同名 sidecar |
| 音乐与现成旁白 | 实际可听音轨、延迟正确、淡入淡出、说话时音乐降低、混后无削波 |
| 只改声音保护画质 | 音频后期前后压缩视频数据 SHA-256 相同，不仅是分辨率相同 |
| 逐张展开与拉远揭示 | 稳定图片 ID、首尾四边形、飞行参与集合、近景到远景实际连续帧 |
| 边缘半张卡片 | 实际解码首屏与拉远中间帧，完整进入或不显示，最终全量数量正确 |
| 信息流动方向 | 箭头和虚线沿路径同向、圆角连续、循环接缝无重复停顿 |
| 常驻富对话框 | 中后段侧栏仍可见，观察截图真实且哈希一致、工具参数白名单、结果来源明确 |
| 精确总时长与交付停留 | 整数总帧数、固定段不变、fit 吸收预算、最后冻结帧已完整交付 |
| 无损源/合成母版 | 原生格式与逐帧 framehash、实际合成母版像素，各自证明范围明确 |
| 纹理染色与分组 | 原始数据不变、alpha 保留、灰度纹理可辨；颜色随稳定组 ID，而非屏幕位置 |
| 三维点云与相机选角 | 实际投影坐标来源、共同刚体旋转、目标可见数及点半径/标签遮挡；不以屏幕间隔证明聚类准确率 |
| 排序失败、撤回与改善 | 全状态排列集合一致、位置和曲线来自同一候选、评分允许下降、失败有真实计算依据 |
| 固定介绍边界与报告清单 | 新停留不推迟约定切换帧；逐项勾选和最后文字结束后才计算完整静止停留 |
| 末尾卡顿与错误诊断 | 最后几帧时间连续、全片无解码错误，换播放器核对后再判断是否改剪辑 |

失败时先定位最小出错层，不对未完成片宣称成功；修改后重跑受影响检查。正确文件在单台播放器卡顿时，不无证据地继续裁掉尾部或降低所有画质。
