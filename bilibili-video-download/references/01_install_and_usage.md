# 安装、调用与验收

## 文件与依赖

安装或复制整个 `bilibili-video-download/` 文件夹，至少保留 `SKILL.md`、`scripts/bilibili_download.py` 和本目录的 reference。脚本为单文件实现，仅依赖 Python 3.10+ 标准库；不用 `pip install`。运行时需要 ffmpeg，导出 MP3 还需要其 `libmp3lame` 编码器。脚本的 ffmpeg 查找顺序为 `--ffmpeg`、`FFMPEG_BIN`、`PATH`。

先检查现有环境：

```bash
python3 --version
ffmpeg -version
ffmpeg -hide_banner -encoders 2>/dev/null | grep libmp3lame
python3 "/path/to/bilibili-video-download/scripts/bilibili_download.py" --help
```

在 Debian/Ubuntu/WSL 中，缺少 Python 或 ffmpeg 时可使用系统包管理器；Fedora 使用对应命令。安装后再核对 Python 是否达到 3.10：

```bash
sudo apt update
sudo apt install python3 ffmpeg
python3 --version
# Fedora: sudo dnf install python3 ffmpeg
```

macOS 已安装 Homebrew 时可用 `brew install python ffmpeg`。若系统包提供的 Python 版本不足，从 [Python 官方下载页](https://www.python.org/downloads/)安装 3.10 或更高版本。Windows 原生环境也从 Python 官网安装 Python，再从 [FFmpeg 官方下载页](https://ffmpeg.org/download.html)选择页面列出的可执行文件提供方，解压后把 `ffmpeg.exe` 路径交给 `--ffmpeg`；WSL 项目应在 WSL 中运行 Linux 版 Python 与 ffmpeg。FFmpeg 官方只提供源码，并在下载页列出平台包和构建来源，不要假设一个跨平台下载命令始终有效。Windows 原生调用示例：

```powershell
py -3 --version
py -3 "C:\path\to\bilibili-video-download\scripts\bilibili_download.py" "[VIDEO_URL]" --ffmpeg "C:\path\to\ffmpeg.exe" --dir "[OUTPUT_DIR]"
```

无 root 的 x86-64 Linux/WSL 可使用 FFmpeg 官方下载页指向的静态版提供方。以下地址于 2026-10-22 验证可访问，使用前仍需检查来源和架构：

```bash
mkdir -p "$HOME/tools/ffmpeg-static"
curl -fL -o "$HOME/tools/ffmpeg-static/ffmpeg.tar.xz" \
  https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
tar -xf "$HOME/tools/ffmpeg-static/ffmpeg.tar.xz" \
  -C "$HOME/tools/ffmpeg-static" --strip-components=1
"$HOME/tools/ffmpeg-static/ffmpeg" -version
"$HOME/tools/ffmpeg-static/ffmpeg" -hide_banner -encoders 2>/dev/null | grep libmp3lame
```

调用时只给当前进程指定路径，不修改 shell 启动文件：

```bash
FFMPEG_BIN="$HOME/tools/ffmpeg-static/ffmpeg" \
  python3 "/path/to/bilibili-video-download/scripts/bilibili_download.py" \
  "[VIDEO_URL]" --mp3-only --dir "[OUTPUT_DIR]"
```

## 下载与转码

以下假设已将 `SKILL_DIR` 指到安装后的 skill 目录，并把 `VIDEO_URL` 换成真实普通投稿 BV 链接。推荐每个 BV 号使用单独输出目录，以免不同视频同名标题被当成已存在文件。

```bash
SKILL_DIR="/path/to/bilibili-video-download"
VIDEO_URL="https://www.bilibili.com/video/BVxxxxxxxxxx/"
OUTPUT_DIR="./downloads/BVxxxxxxxxxx"

# 只看实际可用画质；不下载媒体
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --list

# 首 P MP4，当前可用最高画质；指定画质会降到不超过它的最高可用档
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --qn 1080P --dir "$OUTPUT_DIR"

# 交互式选画质
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --interactive --dir "$OUTPUT_DIR"

# 下载指定分 P 或全部分 P（默认只下载首 P）
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --page 3 --dir "$OUTPUT_DIR"
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --all --dir "$OUTPUT_DIR"

# MP4 + MP3；或只导出 MP3
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --mp3 --dir "$OUTPUT_DIR"
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --mp3-only --dir "$OUTPUT_DIR"

# MP3 质量：0-9 为 VBR（0 质量最高），或固定码率
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --mp3-only --mp3-bitrate 2 --dir "$OUTPUT_DIR"
python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" --mp3-only --mp3-bitrate 320k --dir "$OUTPUT_DIR"
```

`--qn` 支持数字代号和文本别名，例如 `80`/`1080P`、`64`/`720P`、`120`/`4K`。`--list` 显示的“理论可选”与 DASH 中实际返回的流可能不同，下载以实际流为准。`--mp3` 与 `--mp3-only` 不能同时使用。已有文件默认跳过；确实需要重下或重转时使用 `--force`，先确认输出目录与原文件。

## 登录态

公开可访问的视频先不传 Cookie。高画质可能需要登录及对应账号权益，登录也不能保证所有档位可用。只使用用户自己提供的登录态，不写进 Git、命令行参数、shell 历史或日志。脚本保留 `--cookie` 兼容参数，但推荐私有文件：

```bash
umask 077
mkdir -p "$HOME/.config/bilibili-video-download"
read -r -s -p '输入自己的 Cookie: ' BILI_COOKIE
printf '\n'
printf '%s\n' "$BILI_COOKIE" > "$HOME/.config/bilibili-video-download/cookie"
unset BILI_COOKIE
chmod 600 "$HOME/.config/bilibili-video-download/cookie"

python3 "$SKILL_DIR/scripts/bilibili_download.py" "$VIDEO_URL" \
  --cookie-file "$HOME/.config/bilibili-video-download/cookie" \
  --list
```

Cookie 文件可包含 `SESSDATA=...` 或完整 Cookie 字符串。它必须位于 skill 仓库外，且只由当前用户读取。不要在聊天记录、脚本、提交或故障日志里粘贴真实值。

## 结果验证

脚本正常完成应退出 0 并列出生成的 `.mp4`/`.mp3`。检查目标文件非空，再用 ffprobe 读取流和时长：

```bash
test -s "[OUTPUT_FILE]"
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,codec_name \
  -of json "[OUTPUT_FILE]"
```

MP4 应有视频流；有声视频通常还应有音频流。MP3 应有音频流。`ffprobe` 通常与 ffmpeg 一起提供；若只配置了自定义 `ffmpeg`，可用对应目录下的 `ffprobe`。文件存在不等于完整，遇到中断或 ffmpeg 报错时不要把 `.tmp_parts/` 内片段当成果交付。
