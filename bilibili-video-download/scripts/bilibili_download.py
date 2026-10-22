#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B站视频下载器

用法:
    python3 bilibili_download.py <视频URL或BV号> [选项]

示例:
    python3 bilibili_download.py "https://www.bilibili.com/video/[BV_ID]/"
    python3 bilibili_download.py [BV_ID] --qn 1080P
    python3 bilibili_download.py <URL> --interactive          # 交互式选择画质
    python3 bilibili_download.py <URL> --cookie-file [PRIVATE_COOKIE_FILE] --all
    python3 bilibili_download.py <URL> --mp3                  # 下载MP4并同时导出MP3
    python3 bilibili_download.py <URL> --mp3-only             # 只导出MP3（不下载视频流）

说明:
    - 通过 B站 Web 接口获取视频信息，下载 DASH 格式的独立视频/音频流，再用 ffmpeg 合并。
    - 仅使用 Python 标准库，无第三方依赖；播放接口的 WBI 签名已内置实现。
    - 高画质可能需要登录态和对应权益，优先用 --cookie-file 读取私有 Cookie 文件。
    - ffmpeg 查找顺序: --ffmpeg 参数 > FFMPEG_BIN 环境变量 > 系统 PATH。
    - 导出 MP3 需要 ffmpeg 带 libmp3lame 编码器（静态版已包含）。
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.request
import urllib.error
import urllib.parse
from functools import reduce
from pathlib import Path

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# 画质代号表（B站 playurl 接口的 qn 参数）
QN_NAMES = {
    127: "8K 超高清", 126: "杜比视界", 125: "HDR 真彩", 120: "4K 超清",
    116: "1080P60帧", 112: "1080P 高码率", 111: "1080P 高帧率", 80: "1080P",
    64: "720P", 32: "480P", 16: "360P",
}

# --qn 的文本别名（小写匹配）
QN_ALIASES = {
    "8k": 127, "8k超高清": 127,
    "dolby": 126, "杜比视界": 126,
    "hdr": 125, "hdr真彩": 125,
    "4k": 120, "4k超清": 120,
    "1080p60": 116, "1080p60帧": 116,
    "1080p+": 112, "1080p高码率": 112,
    "1080p高帧率": 111, "1080p_hfr": 111,
    "1080p": 80, "1080": 80,
    "720p": 64, "720": 64,
    "480p": 32, "480": 32,
    "360p": 16, "360": 16,
}


def parse_qn(text) -> int | None:
    """把 --qn 参数解析为画质代号，支持数字（80）或文本（1080P）。"""
    if text is None:
        return None
    t = str(text).strip().lower().replace(" ", "").replace("_", "")
    if t in ("", "max", "best", "最高", "自动"):
        return None
    if t.isdigit():
        return int(t)
    if t in QN_ALIASES:
        return QN_ALIASES[t]
    raise argparse.ArgumentTypeError(
        f"无法识别的画质: {text}（可选: 数字代号 或 1080P/720P/480P/4K/8K 等）"
    )


def parse_mp3_bitrate(text: str) -> str:
    """解析 MP3 质量：0-9 为 VBR，或 192k/320k 等固定码率。"""
    value = str(text).strip().lower()
    if re.fullmatch(r"[0-9]|[1-9][0-9]*k", value):
        return value
    raise argparse.ArgumentTypeError("MP3 码率须为 0-9 的 VBR 质量，或 192k/320k 等固定码率")


# WBI 签名当前使用的固定打乱表；接口变化时需重新核对。
MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52,
]


def get_wbi_keys(cookie: str = "") -> tuple[str, str]:
    """从 nav 接口取出 WBI 签名所需的 img_key / sub_key。

    注意: nav 接口对游客返回 code=-101（账号未登录），但 data 里的 wbi_img 仍可正常使用，
    所以这里不做错误码校验。
    """
    req = urllib.request.Request("https://api.bilibili.com/x/web-interface/nav")
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Referer", "https://www.bilibili.com/")
    if cookie:
        req.add_header("Cookie", cookie)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8")).get("data") or {}
    wbi_img = data.get("wbi_img") or {}
    img_url = wbi_img.get("img_url", "")
    sub_url = wbi_img.get("sub_url", "")
    if not img_url or not sub_url:
        raise RuntimeError("无法从 nav 接口获取 WBI 密钥，请稍后重试。")
    img_key = img_url.rsplit("/", 1)[-1].split(".")[0]
    sub_key = sub_url.rsplit("/", 1)[-1].split(".")[0]
    return img_key, sub_key


def sign_wbi(params: dict, img_key: str, sub_key: str) -> str:
    """对请求参数做 WBI 签名，返回带 wts 和 w_rid 的查询串。"""
    mixin_key = reduce(lambda s, i: s + (img_key + sub_key)[i], MIXIN_KEY_ENC_TAB, "")[:32]
    params = dict(params)
    params["wts"] = int(time.time())
    query = urllib.parse.urlencode(sorted(params.items()))
    w_rid = hashlib.md5((query + mixin_key).encode()).hexdigest()
    return f"{query}&w_rid={w_rid}"


def extract_bvid(text: str) -> str:
    """从 URL 或纯 BV 号中提取 bvid。"""
    m = re.search(r"BV[0-9A-Za-z]{10}", text)
    if not m:
        raise ValueError(f"无法从输入中解析 BV 号: {text}")
    return m.group(0)


def api_get(url: str, cookie: str = "") -> dict:
    """请求 B站 API，返回 JSON 数据。"""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Referer", "https://www.bilibili.com/")
    if cookie:
        req.add_header("Cookie", cookie)
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 0:
        raise RuntimeError(f"接口返回错误 {data.get('code')}: {data.get('message')}")
    return data["data"]


def get_video_info(bvid: str, cookie: str = "") -> dict:
    """获取视频标题、aid、cid 及分P列表。"""
    data = api_get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", cookie)
    pages = [
        {"page": p["page"], "cid": p["cid"], "part": p.get("part", "")}
        for p in data.get("pages", [])
    ]
    return {
        "bvid": bvid,
        "aid": data["aid"],
        "title": data["title"],
        "owner": data.get("owner", {}).get("name", ""),
        "pages": pages or [{"page": 1, "cid": data["cid"], "part": data["title"]}],
    }


def get_play_url(bvid: str, cid: int, cookie: str = "", qn: int = 127,
                 wbi_keys: tuple[str, str] | None = None) -> dict:
    """获取 DASH 播放地址。fnval=16 表示请求 DASH 格式（需要 WBI 签名）。"""
    params = {
        "bvid": bvid, "cid": cid, "qn": qn if qn is not None else 127,
        "fnval": 16, "fourk": 1, "otype": "json",
    }
    if wbi_keys:
        query = sign_wbi(params, *wbi_keys)
    else:
        query = urllib.parse.urlencode(params)
    data = api_get(f"https://api.bilibili.com/x/player/playurl?{query}", cookie)
    if "dash" not in data:
        raise RuntimeError("未返回 DASH 格式，可能是 Salvo 风控或接口变更，可稍后重试。")
    return data


def pick_streams(play_data: dict, prefer_qn: int | None):
    """选择目标画质的视频流和最高质量音频流。返回 (video, audio)。"""
    videos = play_data["dash"]["video"]
    if not videos:
        raise RuntimeError("播放接口未返回可下载的视频流")
    audios = play_data["dash"].get("audio") or []

    # accept_quality 只是“理论上可选”的画质，实际下发的流以 dash.video 为准
    accept = play_data.get("accept_quality") or []
    if accept:
        print(f"账号可选画质: {', '.join(QN_NAMES.get(q, str(q)) for q in accept)}")

    # 以实际下发的流为准，取不超过期望画质的最高清晰度；同画质下选带宽最大的
    have = sorted({v["id"] for v in videos}, reverse=True)
    if prefer_qn is None:
        target = have[0]
    else:
        target = next((q for q in have if q <= prefer_qn), have[-1])
    candidates = [v for v in videos if v["id"] == target]
    video = max(candidates, key=lambda v: v.get("bandwidth", 0))
    print(f"已选择画质: {QN_NAMES.get(target, str(target))}（编码 {video.get('codecid')}）")

    audio = max(audios, key=lambda a: a.get("bandwidth", 0)) if audios else None
    return video, audio


def download_stream(url: str, out_path: Path, cookie: str, bvid: str) -> None:
    """带进度显示地下载一个流文件。"""
    req = urllib.request.Request(url)
    req.add_header("User-Agent", USER_AGENT)
    req.add_header("Referer", f"https://www.bilibili.com/video/{bvid}")
    if cookie:
        req.add_header("Cookie", cookie)

    # B站 CDN 会对请求做 Referer 校验，且可能 302 跳转（urllib 自动跟随）
    with urllib.request.urlopen(req, timeout=60) as resp, open(out_path, "wb") as f:
        total = int(resp.headers.get("Content-Length") or 0)
        done = 0
        while True:
            chunk = resp.read(1 << 20)
            if not chunk:
                break
            f.write(chunk)
            done += len(chunk)
            if total:
                pct = done * 100 // total
                bar = "█" * (pct // 2) + "▏" * (1 if pct % 2 >= 50 else 0)
                sys.stdout.write(f"\r    下载中 {pct:3d}% [{bar:<50}] {done // 1048576}MB")
                sys.stdout.flush()
        sys.stdout.write("\n")
        if total and done != total:
            raise RuntimeError(f"媒体流下载不完整：预期 {total} 字节，实际 {done} 字节")


def get_ffmpeg(args) -> str | None:
    """返回可用的 ffmpeg 可执行文件路径：优先 --ffmpeg 参数和 FFMPEG_BIN 环境变量。"""
    candidates = [getattr(args, "ffmpeg", None), os.environ.get("FFMPEG_BIN"), "ffmpeg"]
    for c in candidates:
        if not c:
            continue
        try:
            subprocess.run([c, "-version"], capture_output=True, check=True, timeout=10)
            return c
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
    return None


def run_ffmpeg_to_output(cmd: list[str], out_file: Path, action: str) -> None:
    """先生成同目录临时文件，ffmpeg 成功后再替换成品。"""
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{out_file.stem}.", suffix=out_file.suffix, dir=out_file.parent
    )
    os.close(fd)
    temp_file = Path(temp_name)
    try:
        res = subprocess.run([*cmd, str(temp_file)], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"ffmpeg {action}失败:\n{res.stderr}")
        if temp_file.stat().st_size == 0:
            raise RuntimeError(f"ffmpeg {action}失败：输出文件为空")
        os.replace(temp_file, out_file)
    finally:
        temp_file.unlink(missing_ok=True)


def merge_av(ffmpeg: str, video_file: Path, audio_file: Path, out_file: Path) -> None:
    """用 ffmpeg 无损合并音视频流。"""
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "warning",
        "-i", str(video_file), "-i", str(audio_file),
        "-c", "copy", "-movflags", "+faststart",
    ]
    run_ffmpeg_to_output(cmd, out_file, "合并")


def remux(ffmpeg: str, in_file: Path, out_file: Path) -> None:
    """无音频流时，把单独的视频流重封装为 mp4。"""
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "warning",
        "-i", str(in_file), "-c", "copy", "-movflags", "+faststart",
    ]
    run_ffmpeg_to_output(cmd, out_file, "重封装")


def export_mp3(ffmpeg: str, src: Path, out_file: Path, bitrate: str,
               title: str, artist: str, comment: str) -> None:
    """从 mp4 或音频流转码导出 MP3（VBR，写入 ID3 元数据）。"""
    cmd = [
        ffmpeg, "-y", "-hide_banner", "-loglevel", "warning",
        "-i", str(src),
        "-vn", "-map_metadata", "-1",
        "-c:a", "libmp3lame",
    ]
    if bitrate.lower().endswith("k") and bitrate[:-1].isdigit():
        # 固定码率，如 "320k"
        cmd += ["-b:a", bitrate]
    else:
        # VBR 质量等级 0（最佳）~9；默认 0，约 220-260kbps
        cmd += ["-q:a", bitrate if bitrate.isdigit() else "0"]
    cmd += [
        "-id3v2_version", "3",
        "-write_id3v1", "1",
        "-metadata", f"title={title}",
        "-metadata", f"artist={artist}",
        "-metadata", f"comment={comment}",
    ]
    run_ffmpeg_to_output(cmd, out_file, "导出 MP3")


def choose_quality(play_data: dict) -> int:
    """交互式让用户选择画质，返回画质代号。"""
    accept = play_data.get("accept_quality") or []
    have = sorted({v["id"] for v in play_data["dash"]["video"]}, reverse=True)
    if not accept:
        accept = have
    print("可选画质（✔ = 当前可实际下载，✘ = 需要登录/大会员）:")
    for i, q in enumerate(accept, 1):
        mark = "✔" if q in have else "✘"
        print(f"  {i:2d}. {QN_NAMES.get(q, str(q))} {mark}")
    while True:
        raw = input("输入序号或画质代号（回车=最高可用）: ").strip()
        if not raw:
            return have[0]
        if raw.isdigit() and 1 <= int(raw) <= len(accept):
            return accept[int(raw) - 1]
        try:
            qn = parse_qn(raw)
            if qn is not None and qn in accept:
                return qn
        except argparse.ArgumentTypeError:
            pass
        print("  输入无效，请重试。")


def sanitize(name: str) -> str:
    """清理文件名中的非法字符。"""
    return re.sub(r'[\\/:*?"<>|\r\n\t]', "_", name).strip().rstrip(".") or "video"


def song_title(info: dict, page: dict) -> str:
    """MP3 的标题元数据：单P用视频标题，多P用分P标题。"""
    if len(info["pages"]) > 1 and page["part"]:
        return f"{info['title']} - {page['part']}"
    return info["title"]


def download_part(info: dict, page: dict, args, out_dir: Path, wbi_keys) -> list[Path]:
    """下载一个分P。返回生成的文件列表（mp4 和/或 mp3）。

    三种工作模式:
      - 默认:     下载并合并为 MP4
      - --mp3:     下载 MP4，并同时导出 MP3
      - --mp3-only: 只下载音频流并导出 MP3（省去视频流的带宽和时间）
    已存在且未指定 --force 的文件会跳过；MP4 已存在时直接从它转码出 MP3，不重新下载。
    """
    suffix = f" P{page['page']}" if len(info["pages"]) > 1 else ""
    base = sanitize(info["title"] + suffix)
    mp4 = out_dir / f"{base}.mp4"
    mp3 = out_dir / f"{base}.mp3"

    want_video = not args.mp3_only
    mp4_ok = mp4.exists() and not args.force
    mp3_ok = mp3.exists() and not args.force

    outputs: list[Path] = []
    if mp4_ok and want_video:
        outputs.append(mp4)
    if mp3_ok and (args.mp3 or args.mp3_only):
        outputs.append(mp3)

    need_mp4 = want_video and not mp4_ok
    need_mp3 = (args.mp3 or args.mp3_only) and not mp3_ok

    if not need_mp4 and not need_mp3:
        for f in outputs:
            print(f"  已存在，跳过: {f.name}（--force 可覆盖）")
        return outputs

    ffmpeg_bin = get_ffmpeg(args)
    if not ffmpeg_bin and (need_mp4 or need_mp3):
        raise RuntimeError("未找到 ffmpeg，无法合并/转码。请安装 ffmpeg，或用 --ffmpeg / FFMPEG_BIN 指定路径。")

    # 情况A: MP4 已存在、只需导出 MP3 —— 直接从本地 MP4 转码，不访问网络
    if not need_mp4 and need_mp3 and mp4.exists():
        print(f"  从本地 MP4 导出 MP3 ...")
        export_mp3(
            ffmpeg_bin, mp4, mp3, args.mp3_bitrate,
            title=song_title(info, page),
            artist=info["owner"],
            comment=f"来源: 哔哩哔哩 {info['bvid']}",
        )
        outputs.append(mp3)
        print(f"  ✔ 完成: {mp3}")
        return outputs

    # 情况B/C: 需要下载
    print(f"  获取播放地址 ...")
    play_data = get_play_url(info["bvid"], page["cid"], args.cookie, args.qn, wbi_keys)
    audios = play_data["dash"].get("audio") or []

    if need_mp4:
        video, audio = pick_streams(play_data, args.qn)
    else:
        # --mp3-only：只取最高质量音频流
        if not audios:
            raise RuntimeError("该视频没有独立音频流，无法导出 MP3")
        video, audio = None, max(audios, key=lambda a: a.get("bandwidth", 0))
        print("  仅下载音频流（用于导出 MP3，跳过视频流）...")

    tmp_dir = out_dir / ".tmp_parts"
    tmp_dir.mkdir(exist_ok=True)
    v_file = tmp_dir / f"{base}_video.m4s"
    a_file = tmp_dir / f"{base}_audio.m4s"

    if video is not None:
        print(f"  下载视频流 ...")
        download_stream(video["baseUrl"], v_file, args.cookie, info["bvid"])
    if audio is not None:
        print(f"  下载音频流 ...")
        download_stream(audio["baseUrl"], a_file, args.cookie, info["bvid"])

    if need_mp4:
        print(f"  合并音视频 ...")
        if audio is not None:
            merge_av(ffmpeg_bin, v_file, a_file, mp4)
        else:
            # 纯视频（无音频流）：直接重封装为 mp4
            remux(ffmpeg_bin, v_file, mp4)
        outputs.append(mp4)

    if need_mp3:
        # 优先从已合并的 MP4 转码；--mp3-only 时直接转码音频流
        src = mp4 if mp4.exists() else a_file
        print(f"  导出 MP3（来源: {'MP4' if src == mp4 else '音频流'}）...")
        export_mp3(
            ffmpeg_bin, src, mp3, args.mp3_bitrate,
            title=song_title(info, page),
            artist=info["owner"],
            comment=f"来源: 哔哩哔哩 {info['bvid']}",
        )
        outputs.append(mp3)

    v_file.unlink(missing_ok=True)
    a_file.unlink(missing_ok=True)
    for f in outputs:
        print(f"  ✔ 完成: {f}")
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(
        description="B站视频下载器（DASH + ffmpeg 合并，无第三方依赖，可导出 MP3）"
    )
    parser.add_argument("url", help="B站视频 URL 或 BV 号")
    parser.add_argument("-q", "--qn", type=parse_qn, default=None, metavar="画质",
                        help="期望画质：数字代号（80）或文本（1080P/720P/480P/4K/8K），"
                             "不传则取可用最高")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="交互式选择画质（列出可选项后等待输入）")
    parser.add_argument("-l", "--list", action="store_true",
                        help="只列出可选画质，不下载")
    cookie_options = parser.add_mutually_exclusive_group()
    cookie_options.add_argument("-c", "--cookie", default="",
                                help="登录态 Cookie；命令行参数可能进入 shell 历史，优先用 --cookie-file")
    cookie_options.add_argument("--cookie-file", type=Path,
                                help="从仓库外的私有文本文件读取 Cookie（推荐）")
    parser.add_argument("-d", "--dir", default=".", help="保存目录，默认当前目录")
    parser.add_argument("-p", "--page", type=int, default=None,
                        help="只下载指定分P（从1开始）")
    parser.add_argument("--all", action="store_true", help="下载全部分P")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的文件")
    parser.add_argument("--mp3", action="store_true",
                        help="下载 MP4 的同时也导出 MP3")
    parser.add_argument("--mp3-only", action="store_true",
                        help="只导出 MP3（跳过视频流下载，更快）")
    parser.add_argument("--mp3-bitrate", type=parse_mp3_bitrate, default="0", metavar="码率",
                        help='MP3 码率：数字 0-9 为 VBR 质量（0最佳，默认），'
                             '或固定码率如 "320k"/"192k"')
    parser.add_argument("--ffmpeg", default=None,
                        help="ffmpeg 可执行文件路径（也可用环境变量 FFMPEG_BIN）")
    args = parser.parse_args()

    if args.cookie_file:
        try:
            args.cookie = args.cookie_file.expanduser().read_text(encoding="utf-8").strip()
        except OSError as e:
            print(f"✘ 无法读取 Cookie 文件: {e}", file=sys.stderr)
            return 2
        if not args.cookie:
            print("✘ Cookie 文件为空", file=sys.stderr)
            return 2

    if args.mp3 and args.mp3_only:
        print("✘ --mp3 与 --mp3-only 不能同时使用", file=sys.stderr)
        return 2

    try:
        bvid = extract_bvid(args.url)
        print(f"解析 BV 号: {bvid}")
        info = get_video_info(bvid, args.cookie)
        print(f"标题: {info['title']}（UP主: {info['owner']}，共 {len(info['pages'])} 个分P）")

        out_dir = Path(args.dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        if args.all:
            targets = info["pages"]
        elif args.page is not None:
            targets = [p for p in info["pages"] if p["page"] == args.page]
            if not targets:
                raise ValueError(f"不存在第 {args.page}P，该视频共 {len(info['pages'])}P")
        else:
            targets = info["pages"][:1]

        # WBI 密钥取一次即可复用
        wbi_keys = get_wbi_keys(args.cookie)

        # 列出画质 / 交互选择画质：基于第一个目标分P的播放信息
        if args.list or args.interactive:
            first = get_play_url(bvid, targets[0]["cid"], args.cookie, args.qn, wbi_keys)
            if args.list:
                have = sorted({v["id"] for v in first["dash"]["video"]}, reverse=True)
                accept = first.get("accept_quality") or have
                print("\n可选画质（✔ = 当前可实际下载，✘ = 需要登录/大会员）:")
                for q in accept:
                    mark = "✔" if q in have else "✘"
                    print(f"  {QN_NAMES.get(q, str(q))} {mark}")
                return 0
            args.qn = choose_quality(first)
            print(f"已选择: {QN_NAMES.get(args.qn, str(args.qn))}")

        results = []
        for page in targets:
            print(f"\n▶ 下载 P{page['page']} {page['part']}")
            results.extend(download_part(info, page, args, out_dir, wbi_keys))

        # 清理临时目录
        tmp_dir = out_dir / ".tmp_parts"
        if tmp_dir.exists() and not any(tmp_dir.iterdir()):
            tmp_dir.rmdir()

        print(f"\n全部完成，共 {len(results)} 个文件")
        return 0
    except (ValueError, RuntimeError, urllib.error.URLError) as e:
        print(f"\n✘ 出错: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
