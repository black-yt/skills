---
name: screen-demo-video-editing
description: "将 GUI、科研软件或 agent 屏幕录制剪成清楚连贯的演示视频；处理静止与周期等待、分屏悬浮、缩放跟随、日志对话、中文字幕、背景音乐与现成旁白，附可配置 FFmpeg/Python 工具及合成素材验收。"
---

# 屏幕演示视频剪辑与包装

## 交付边界

- **面向录屏后期。** 用已有视频、截图和日志完成剪辑、镜头编排与视听包装；不把任务扩大成重新操作软件、生成科研结果或自动下载素材。
- **先识别时间轴。** 区分原始录屏、已确认的剪辑版、包装版、最终带声音版。剪辑以原片和源时间 EDL 为准；只加音频时复制已确认视频流。
- **参数可迁移。** 分辨率、分割线、ROI、网格映射、字体、品牌、阶段文案和模型显示名都由项目配置提供。示例数值是起点，不是另一份录屏的正确答案。
- **已有授权继续执行。** 保留原素材，导出新文件；不自动覆盖输入。不要为普通可逆的剪辑反复请求确认。发布、外传日志或调用付费语音服务须在用户授权范围内。

## 工作流

1. **探测与约束：** 检查流、时长、帧率、实际画面尺寸、音轨、DPI/鼠标坐标来源及播放器字幕。明确用户要缩短等待、视觉展示、实质操作还是配音；默认不改变已确认的操作顺序。
2. **剪辑：** 低分辨率分析静止/周期，只生成候选 EDL；保留必要的思考停顿、输入变化与真实第一段鼠标运动。按 [02](references/02_idle_and_periodic_cleanup.md) 复查周期相位与光标遮罩。
3. **构图与镜头：** 分开定义外层面板位置和内部取景。主画面宽度、下方字幕空间、独立日志播放器和退场时点由配置控制。选择少量相邻操作合成特写，画面大变时回到全景。
4. **对话与字幕：** 日志先映射到成片时间；消息按时间追加，退场只移动面板，不截断播放器。字幕面向观众解释行为。不要把隐藏推理、API 原始响应或工具参数直接展示为对话。
5. **音频：** 按要求加入背景音乐或现成旁白，测响度、做淡入淡出，必要时用旁白侧链压低音乐。只要求配乐时不擅自生成配音；本工具不包含 TTS/声音克隆接口。
6. **验收：** 先出关键静帧，再出包含转场的短视频，最后完整导出。静帧正常不证明动态合成正常；必须检查实际成片尺寸、切口、文字、消息时序、音画时长和全片解码。

## 核心经验

- **真实开场：** “移动前静止几秒”要保留移动前的原始画面与完整运动，不能冻结已经移动后的首帧代替。
- **周期去重：** 比较相位相邻的完整周期，遮住已确认的光标/插入符区域，同时保留输入框数值、选择状态和科研内容；不要把自动旋转等展示目标删掉。
- **取景强度：** `visible_fraction=0.4` 是保留宽、高各 40% 的区域，即 2.5 倍放大。外框不变，内部取景移动；不是把视频缩成 40%。
- **稳定透明合成：** 动态缩放的 RGB 和遮罩先填充到固定最大画布，再 `alphamerge`。否则投影会变大，主体可能仍停留在首帧尺寸。
- **聊天独立播放：** “第二轮结束后退场”依据执行反馈时间，而非只保留两条输出。播放器继续追加，合成器只改变其坐标；辅流 EOF 不能截断主视频。
- **字幕交付：** 文字已写入画面时，默认不再同目录同名导出 SRT/ASS；播放器自动加载会叠出额外大字。明确需要软字幕时才单独交付，并验证播放器实际行为。
- **画质用证据描述：** H.264 display crop 与音频后期的 stream copy 可做哈希核对；CRF 18 是高质量有损，不称逐像素无损。剪掉时间区间时同步音频，并扣除同一份源时间切段。

## 常用工具

```bash
SKILL_DIR="/path/to/screen-demo-video-editing"
python3 -m pip install -r "$SKILL_DIR/scripts/requirements.txt"

# 分析和编辑配置写在自己的工作目录，不写到 skill 安装目录。
python3 "$SKILL_DIR/scripts/edit_timeline.py" detect-static ./source.mp4 --output ./freezes.json
python3 "$SKILL_DIR/scripts/edit_timeline.py" build-plan --freezes ./freezes.json --output ./edit.json
python3 "$SKILL_DIR/scripts/edit_timeline.py" render --plan ./edit.json

# 复制 assets 的对应配置到工作目录，填写素材/字体/尺寸后使用。
python3 "$SKILL_DIR/scripts/prepare_trace.py" --config ./trace.json --output ./events.json
python3 "$SKILL_DIR/scripts/render_overlays.py" chat --config ./chat.json
python3 "$SKILL_DIR/scripts/render_overlays.py" captions --config ./captions.json
python3 "$SKILL_DIR/scripts/render_presentation.py" --config ./presentation.json --preview-at 3.5
python3 "$SKILL_DIR/scripts/render_presentation.py" --config ./presentation.json
python3 "$SKILL_DIR/scripts/mix_audio.py" --config ./audio.json
```

工具接受 `--ffmpeg` 或 `FFMPEG_BIN`，可选使用 `imageio-ffmpeg` 提供的可执行文件。JSON 中路径相对于配置文件的 `media_root`，默认就是配置所在目录；字体和媒体不随 skill 分发。已有导出默认拒绝覆盖，确认更新派生结果时用 `--overwrite`。`--duration` 仅用于构图短测，不替代全片验收。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 说明源素材、源时间 EDL、成片时间、配置路径和帧率边界，给出不依赖机器私有目录的安装与执行方式；区分分析图和交付视频。 | FFmpeg, ffprobe, Python, media_root, EDL, CFR, VFR, source time, 路径, 原片 | 首次处理新录屏前读取；替换输入或改变帧率前读取；日志和视频时间对不上时读取 | [references/01_workspace_and_timeline.md](references/01_workspace_and_timeline.md) |
| 02 | 给出静止候选、保留停顿、周期检测、相位比较、光标遮罩和真实开场恢复的判定流程，解释哪些变化必须保护及如何核对剪口。 | freezedetect, 静止帧, 周期, 闪烁, 插入符, ROI, 相位, 光标, cut, 开场 | 删除等待片段前读取；判断周期是否冗余前读取；片头缺动作或剪口跳变时读取 | [references/02_idle_and_periodic_cleanup.md](references/02_idle_and_periodic_cleanup.md) |
| 03 | 解释左右素材拆分、H.264 显示裁切、悬浮圆角投影、等比面板移动、少量连续特写和鼠标跟随，包含固定画布透明合成的已验证修复。 | split, h264_metadata, crop, alpha, pad, zoompan, 悬浮, 缩放, 跟随, shadow | 拆分素材或改布局前读取；安排特写或退场前读取；预览正常而成片尺寸错误时读取 | [references/03_panels_and_camera.md](references/03_panels_and_camera.md) |
| 04 | 说明日志时间锚点、坐标校准、连续对话与自动上滚，以及中文字体、可变字重、阶段标题和单行字幕；定位播放器重复字幕。 | JSONL, anchor, executed_at, 对话气泡, 退场, Noto, Pillow, 字重, SRT, 字幕 | 将日志转成对话前读取；设置模型显示名或鼠标映射前读取；加文字或排查异常大字幕时读取 | [references/04_trace_chat_and_typography.md](references/04_trace_chat_and_typography.md) |
| 05 | 给出背景音乐、预录旁白的响度测量、延迟对齐、淡入淡出和侧链压低流程，区分现成语音混音与未提供的 TTS 合成能力。 | loudnorm, LUFS, AAC, 配乐, 配音, voiceover, adelay, sidechaincompress, stream copy | 添加音乐或旁白前读取；调整人声与音乐平衡前读取；仅改声音而需要保护画质时读取 | [references/05_audio_music_and_voiceover.md](references/05_audio_music_and_voiceover.md) |
| 06 | 提供逐命令的配置示例、合成素材 smoke test 和交付覆盖表，检查动态几何、消息续播、字体、音画同步、无重复字幕及视频流哈希。 | smoke test, validate_export, SHA-256, full decode, transition, frame hash, manifest, 验收 | 首次运行脚本前读取；改工具或参数后读取；最终交付及播放器卡顿排查时读取 | [references/06_validation_and_recipes.md](references/06_validation_and_recipes.md) |
