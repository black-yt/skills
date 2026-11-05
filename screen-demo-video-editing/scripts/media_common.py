"""Shared FFmpeg helpers; paths in JSON are relative to that JSON's media_root."""
from __future__ import annotations

import json
import hashlib
import math
import os
import re
import shutil
import subprocess
import uuid
from fractions import Fraction
from pathlib import Path


def ffmpeg_bin(explicit=None):
    candidate = explicit or os.environ.get("FFMPEG_BIN") or shutil.which("ffmpeg")
    if candidate:
        return str(candidate)
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError as exc:
        raise RuntimeError("Install FFmpeg or imageio-ffmpeg, or pass --ffmpeg PATH") from exc


def load_config(path):
    path = Path(path).resolve()
    cfg = json.loads(path.read_text(encoding="utf-8"))
    return cfg, (path.parent / cfg.get("media_root", ".")).resolve()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024*1024), b""):
            digest.update(block)
    return digest.hexdigest()


def packet_hashes(ffmpeg, path):
    report = subprocess.check_output([ffmpeg, "-v", "error", "-i", str(path), "-map", "0:v:0",
                                      "-c:v", "copy", "-f", "framehash", "-"], text=True)
    return [line.split(",")[-1].strip() for line in report.splitlines() if line and not line.startswith("#")]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def probe(ffmpeg, path):
    """Prefer ffprobe; portable FFmpeg-only installations use its input report."""
    sibling = Path(ffmpeg).with_name("ffprobe.exe" if str(ffmpeg).endswith(".exe") else "ffprobe")
    ffprobe = str(sibling) if sibling.is_file() else shutil.which("ffprobe")
    report = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], capture_output=True, text=True).stderr
    if ffprobe:
        data = json.loads(subprocess.check_output([
            ffprobe, "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)], text=True))
        video = next(s for s in data["streams"] if s["codec_type"] == "video"
                     and not s.get("disposition", {}).get("attached_pic"))
        from fractions import Fraction
        rate = video.get("avg_frame_rate") or video.get("r_frame_rate", "0/1")
        return {"duration": float(data["format"]["duration"]), "width": video["width"],
                "height": video["height"], "fps": float(Fraction(rate)),
                "codec": video["codec_name"], "pixel_format": video.get("pix_fmt"),
                "has_audio": any(s["codec_type"] == "audio" for s in data["streams"]),
                "has_subtitles": any(s["codec_type"] == "subtitle" for s in data["streams"]),
                "report": report}
    duration = re.search(r"Duration: (\d+):(\d+):([\d.]+)", report)
    line = next((line for line in report.splitlines() if "Video:" in line and "attached pic" not in line), "")
    # Do not accidentally parse stream IDs or 0x31637661 codec tags as dimensions.
    dimensions = re.search(r",\s*(\d+)x(\d+)(?:\s|,)", line.split("Video:")[-1])
    rate = re.search(r"([\d.]+) fps", line)
    if not duration or not dimensions or not rate:
        raise ValueError(f"Cannot inspect video; install ffprobe for this input:\n{report}")
    pixel_format = re.search(r",\s*(\w+)(?:\([^)]*\))?,\s*\d+x\d+", line)
    return {"duration": int(duration[1])*3600+int(duration[2])*60+float(duration[3]),
            "width": int(dimensions[1]), "height": int(dimensions[2]), "fps": float(rate[1]),
            "codec": line.split("Video:")[1].strip().split()[0].rstrip(","),
            "pixel_format": pixel_format[1] if pixel_format else None,
            "has_audio": "Audio:" in report, "has_subtitles": "Subtitle:" in report, "report": report}


def check_output(output, inputs=(), overwrite=False):
    output = Path(output).resolve()
    if output in [Path(path).resolve() for path in inputs]:
        raise ValueError("An output must not replace an input")
    if output.exists() and not overwrite:
        raise FileExistsError(f"Already exists: {output}; use --overwrite for a derived export")
    output.parent.mkdir(parents=True, exist_ok=True)
    return output


def export(command, output):
    """Publish a complete container only after the encoder succeeds."""
    output = Path(output)
    temporary = output.with_name(f".{output.stem}.{uuid.uuid4().hex[:8]}.partial{output.suffix}")
    try:
        subprocess.run([*command, str(temporary)], check=True)
        temporary.replace(output)
    finally:
        if temporary.exists():
            temporary.unlink()


def smooth(value):
    value = max(0.0, min(1.0, value))
    return value*value*(3-2*value)


def smooth_expr(value):
    u = f"clip(({value}),0,1)"
    return f"({u}*{u}*(3-2*{u}))"


def merge_cuts(cuts, end):
    if not math.isfinite(end) or end <= 0:
        raise ValueError("Invalid source end")
    result = []
    for start, stop in sorted(cuts):
        if not all(math.isfinite(v) for v in (start, stop)):
            raise ValueError("Cut times must be finite")
        start, stop = max(0, start), min(end, stop)
        if stop <= start:
            continue
        if result and start <= result[-1][1]+1e-8:
            result[-1][1] = max(stop, result[-1][1])
        else:
            result.append([start, stop])
    return result


def edited_time(source_time, cuts):
    return source_time-sum(max(0, min(source_time, b)-a) for a, b in cuts if source_time > a)


def encode_args(cfg, fps):
    args = ["-c:v", "libx264", "-threads", str(cfg.get("threads", 4)),
            "-preset", cfg.get("preset", "medium"), "-crf", str(cfg.get("crf", 18)),
            "-pix_fmt", "yuv420p", "-g", str(max(1, round(fps*2))),
            "-r", str(fps), "-fps_mode", "cfr", "-movflags", "+faststart"]
    if cfg.get("maxrate"):
        args += ["-maxrate", cfg["maxrate"], "-bufsize", cfg.get("bufsize", cfg["maxrate"])]
    return args


def frame_rate(value):
    fps = Fraction(str(value))
    if fps <= 0:
        raise ValueError("fps must be positive")
    return fps


class FrameWriter:
    """Atomic raw-image encoder; alpha is preserved in FFV1 Matroska outputs."""
    def __init__(self, ffmpeg, output, size, fps, encoding=None, alpha=False):
        self.output = Path(output)
        self.temporary = self.output.with_name(f".{self.output.stem}.{uuid.uuid4().hex[:8]}.partial{self.output.suffix}")
        self.mode = "RGBA" if alpha else "RGB"
        self.size = tuple(size)
        self.log = self.output.with_suffix(self.output.suffix+".encode.log").open("w")
        command = [ffmpeg, "-v", "warning", "-nostdin", "-y", "-f", "rawvideo", "-pix_fmt",
                   "rgba" if alpha else "rgb24", "-s", f"{size[0]}x{size[1]}", "-framerate", str(fps),
                   "-i", "pipe:0", "-an"]
        if self.output.suffix.lower() == ".mkv":
            command += ["-c:v", "ffv1", "-level", "3", "-g", "1", "-threads", "2",
                        "-pix_fmt", "bgra" if alpha else "bgr0"]
        elif alpha:
            self.log.close()
            raise ValueError("Transparent animation requires .mkv (FFV1)")
        else:
            command += ["-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709"]
            command += encode_args(encoding or {}, fps)
            command += ["-colorspace", "bt709", "-color_trc", "bt709", "-color_primaries", "bt709"]
        self.process = subprocess.Popen([*command, str(self.temporary)], stdin=subprocess.PIPE, stderr=self.log)

    def __enter__(self):
        return self

    def write(self, image):
        if image.size != self.size:
            raise ValueError("Animation frame size changed")
        self.process.stdin.write(image.convert(self.mode).tobytes())

    def __exit__(self, kind, value, traceback):
        try:
            if kind:
                self.process.kill()
                self.process.wait()
            else:
                self.process.stdin.close()
                if self.process.wait():
                    raise RuntimeError(f"Animation encoder failed; inspect {self.log.name}")
                self.temporary.replace(self.output)
        finally:
            self.log.close()
            if self.temporary.exists():
                self.temporary.unlink()


def video_hash(ffmpeg, source):
    return subprocess.check_output([ffmpeg, "-v", "error", "-i", str(source), "-map", "0:v:0",
                                    "-c:v", "copy", "-f", "hash", "-hash", "sha256", "-"], text=True).strip()


def frame_hash(ffmpeg, source, at, crop=None):
    cmd = [ffmpeg, "-v", "error", "-threads", "1", "-ss", str(at), "-i", str(source),
           "-map", "0:v:0", "-frames:v", "1", "-an"]
    if crop:
        cmd += ["-vf", crop]
    return subprocess.check_output([*cmd, "-pix_fmt", "yuv420p", "-f", "hash", "-hash", "sha256", "-"], text=True).strip()


def validate(ffmpeg, path, duration=None, burned_only=False):
    data = probe(ffmpeg, path)
    if duration is not None and abs(data["duration"]-duration) > max(.06, 1/data["fps"]):
        raise ValueError(f"Unexpected export duration: {data['duration']} vs {duration}")
    if burned_only:
        sidecars = [p for p in Path(path).parent.glob(Path(path).stem+"*")
                    if p.suffix.lower() in {".srt", ".ass", ".ssa", ".vtt", ".sub", ".idx"}]
        if data["has_subtitles"] or sidecars:
            raise ValueError(f"Extra subtitles can duplicate burned captions: {sidecars}")
    result = subprocess.run([ffmpeg, "-v", "error", "-xerror", "-threads", "4", "-i", str(path),
                             "-progress", "pipe:1", "-nostats", "-f", "null", "-"],
                            capture_output=True, text=True, check=True)
    counts = re.findall(r"frame=(\d+)", result.stdout)
    return {k: v for k, v in data.items() if k != "report"} | {
        "frames": int(counts[-1]) if counts else None, "full_decode_passed": True}
