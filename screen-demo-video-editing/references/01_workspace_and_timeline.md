# 工作目录与时间轴

## 素材边界

- **原始输入：** 录屏、用户提供的背景、logo、音乐与原始日志保持不变。脚本拒绝把输出写回输入路径。
- **派生层：** 原片 EDL → 确认的剪辑视频 → 包装视频 → 配乐/旁白版。调整剪辑从原片与 EDL 重建；仅修改声音时复制确认版的视频流。
- **配置路径：** `media_root` 相对配置所在目录；其他路径相对这个根目录。脚本可从任意 cwd 调用，不依赖 skill 所在目录、临时下载目录或本机盘符。
- **本地资产：** 数据、字体、logo、音乐与完整轨迹属于项目。公开复用工具时只提交代码、通用参数与合成例子，不把它们顺手放进公共仓库。
- **原始日志与展示：** 项目可归档原图、全局/局部网格图、模型输出及工具调用，以文件哈希核对；聊天展示只选用户允许显示的消息正文，保留原始来源，不改原记录冒充另一条运行。

## 环境

```bash
python3 --version
ffmpeg -version
ffmpeg -hide_banner -h filter=zoompan
ffmpeg -hide_banner -h filter=alphamerge
ffmpeg -hide_banner -h filter=sidechaincompress
```

- Python 3.10+；剪辑/分割/轨迹/音频工具仅用标准库，周期分析需 NumPy，视觉素材需 Pillow。
- 先使用已有 FFmpeg；缺少时可在项目虚拟环境安装 `scripts/requirements.txt`。不要为了单个视频改全局 shell、系统默认编码或共享 Python 环境。
- 提供 `--ffmpeg /path/to/ffmpeg` 或 `FFMPEG_BIN`。有 ffprobe 时优先读取 JSON 元数据；便携 FFmpeg-only 环境有 stderr 回退解析，解析尺寸要避开流 ID 和 `0x...` codec tag。
- Windows 路径在 WSL 中转换为对应挂载路径，继续使用 bash；路径含空格、中文时通过 Python 参数列表传给 subprocess，不拼 shell 字符串。
- 依赖行为以当前 CLI help 为准；官方入口为 [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html)、[bitstream filters](https://ffmpeg.org/ffmpeg-bitstream-filters.html)、[formats](https://ffmpeg.org/ffmpeg-formats.html) 与 [Pillow ImageFont](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html)。这些是滚动文档，遇到选项差异先核对本地版本与 `-h`，不要把文档最新版当成本机实现。

## 源时间与成片时间

- **切段格式：** `cuts=[[a,b], ...]` 表示原片半开区间 `[a,b)`。先排序、合并重叠、裁到源片尾；避免重复扣除时长。
- **时间映射：** 成片时间 = 源时间 − 该时刻之前已经删除的时间。落在删除区间内的日志映射到同一剪口，不凭空加停顿。
- **日志锚点：** 找一个在录屏和日志都可确认的动作，给出它的源片秒数和日志 ISO 时间。不能把日志创建时刻直接当录屏起点。
- **音画一致：** 视频和音频使用同一份源时间切段与时间戳扣除。不要分别按输出视频帧数与音频包数重排时间，否则大量剪口会积累漂移。
- **帧边界：** 先确定输出 CFR 帧率，再把候选切点量化到该帧网格。音频采样边界与视频帧边界不同，验收允许合理的单帧/采样误差，但不能放任累积漂移。
- **VFR：** 对可变帧率素材先检查实际时间戳，必要时生成一次带明确 CFR 的中间基准并记录映射；不能只看 metadata 里一个四舍五入 fps 就认定每帧间隔恒定。

## 调整与长任务

- 先验证源裁切范围，再做静帧，随后导出跨越退场或缩放的短片。源像素、屏幕 DPI、逻辑桌面坐标与输出画布像素是四个不同概念。
- 参数确定后完整导出，记录配置、源哈希、时长与结果；中间画面不覆盖确认的成品。
- 工具用 `.partial` 容器完成后再发布最终文件，避免把中断视频当成成功输出。中断后核对进程与文件，再重跑派生结果，不盲目删除原片。
- 执行环境有运行时限时，将素材预渲染、视频导出和验收分成可观察的阶段；必要时使用带 PID、日志、退出结果的受控长任务，持续跟踪到结束。不要把“已启动”当成“已交付”。
