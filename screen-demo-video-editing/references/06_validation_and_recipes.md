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
| 末尾卡顿与错误诊断 | 最后几帧时间连续、全片无解码错误，换播放器核对后再判断是否改剪辑 |

失败时先定位最小出错层，不对未完成片宣称成功；修改后重跑受影响检查。正确文件在单台播放器卡顿时，不无证据地继续裁掉尾部或降低所有画质。
