---
name: bilibili-video-download
description: "当用户要下载哔哩哔哩普通 BV 投稿视频为 MP4、选择画质或分 P，或将其音频导出为 MP3 时使用；提供完整的标准库 Python 下载脚本、ffmpeg 安装与调用步骤、登录态处理和结果验证。"
---

# B站视频下载与 MP3 导出

## 交付范围

- 本 skill 自带完整可运行的 [下载脚本](scripts/bilibili_download.py)，使用 Python 3.10+ 标准库请求视频信息、WBI 签名与 DASH 音视频流，再用 ffmpeg 合并 MP4 或转码 MP3；不需要 pip 包。
- 支持普通投稿视频的 BV 号或含 BV 号的 URL、指定画质、交互选画质、指定/全部分 P、MP4+MP3、仅 MP3、固定码率/VBR。输出保存在用户指定目录。
- 不支持番剧 `ep/ss`、AV 号、互动视频、断点续传和批量播放列表。接口或风控变化时先诊断，不凭空声称可下载或绕过权限。

## 执行步骤

1. 确认用户给出 BV 号/普通视频 URL、要 MP4 还是 MP3、分 P 范围和输出目录；未指定时默认最高实际可用画质、首个分 P、仅 MP4。不同视频尽量使用独立输出目录，避免同名标题冲突。
2. 按 [安装与使用](references/01_install_and_usage.md) 检查 `python3 --version`、ffmpeg 和 `libmp3lame`。只在缺依赖时安装；优先使用已存在的 ffmpeg 或 `--ffmpeg` / `FFMPEG_BIN`。
3. 先用 `--list` 查看实际可用画质；执行下载时按用户需求选择 `--qn`、`--page`、`--all`、`--mp3` 或 `--mp3-only`。高画质若需要登录态，只使用用户提供的 Cookie；优先从仓库外的私有文件通过 `--cookie-file` 读取，不把真实值写入命令行、日志或仓库。
4. 检查进程退出码、输出文件存在且非空；用 ffprobe 检查容器、时长与视频/音频流。失败时按 [工作原理与排错](references/02_behavior_and_troubleshooting.md) 找首个错误。不要把下载中断留下的 `.tmp_parts` 当成成品。

## 最常用调用

```bash
SKILL_DIR="/path/to/bilibili-video-download"
VIDEO_URL="https://www.bilibili.com/video/BVxxxxxxxxxx/"

# MP4；默认首 P、当前可下载的最高画质
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --dir "./downloads/BVxxxxxxxxxx"

# 仅导出 MP3，不下载视频流
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --mp3-only --dir "./downloads_mp3/BVxxxxxxxxxx"

# 同时保留 MP4 与 MP3
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --mp3 --dir "./downloads/BVxxxxxxxxxx"
```

示例中的 BV 号和路径是占位符，执行前替换。下载用户有权保存的内容；需要账号权益时按平台访问控制获取，不尝试绕过。

## 文件导航

| 序号 | 文件内容概览 | 关键词 | 触发时机 | 文件路径 |
| --- | --- | --- | --- | --- |
| 01 | 给出 Python/ffmpeg 的 WSL、Linux、macOS、Windows 安装入口和无 root 的静态版命令；列出脚本的 MP4、MP3、画质、分 P、Cookie 文件、输出目录、ffprobe 验证等完整调用示例，说明不需 pip 安装。 | Python 3.10, ffmpeg, libmp3lame, apt, dnf, Homebrew, WSL, --ffmpeg, FFMPEG_BIN, --mp3-only, --cookie-file, ffprobe | 首次安装或迁移环境前必须读取；选择下载参数或分 P 前必须读取；提供登录态、导出 MP3 或验证输出前必须读取 | [references/01_install_and_usage.md](references/01_install_and_usage.md) |
| 02 | 解释 BV 提取、view/nav/playurl、WBI 签名、DASH 分离流、画质降级、文件跳过和本地 MP4 转码；对接口错误、风控、缺流、ffmpeg 失败、未完成临时文件及不支持的链接给出排查顺序。 | BVID, cid, WBI, w_rid, DASH, qn, accept_quality, baseUrl, 403, -400, -101, .tmp_parts, 重试, 断点续传 | 排查 API 或 CDN 失败时必须读取；画质与预期不符或音频缺失时必须读取；检查已有文件跳过、失败恢复或接口变化时必须读取 | [references/02_behavior_and_troubleshooting.md](references/02_behavior_and_troubleshooting.md) |
