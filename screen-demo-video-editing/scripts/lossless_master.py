#!/usr/bin/env python3
"""Build a video-only FFV1 master from original-time cuts and verify every decoded frame."""
import argparse
from pathlib import Path
import subprocess
import tempfile

from media_common import (load_config, ffmpeg_bin, probe, check_output, merge_cuts, frame_rate,
                          file_sha256, write_json)


def hashes(text):
    return [line.split(",")[-1].strip() for line in text.splitlines() if line and not line.startswith("#")]


def build(cfg, root, ffmpeg, output):
    source = (root/cfg["source"]).resolve()
    info = probe(ffmpeg, source)
    fps = frame_rate(cfg.get("fps", info["fps"]))
    fmt = info.get("pixel_format")
    if not fmt:
        raise ValueError("Cannot determine native pixel format; install ffprobe")
    end = cfg.get("source_end", info["duration"])
    if not 0<end<=info["duration"]+.001:
        raise ValueError("Invalid source_end")
    cuts = merge_cuts(cfg.get("cuts", []), end)
    selection = "+".join(f"gte(t,{a:.9f})*lt(t,{b:.9f})" for a, b in cuts)
    shift = "+".join(f"gte(PTS*TB,{b:.9f})*{b-a:.9f}" for a, b in cuts)
    vf = f"select='not({selection})',setpts='PTS-({shift})/TB'" if cuts else "setpts=PTS-STARTPTS"
    if cfg.get("crop"):
        x, y, w, h = cfg["crop"]
        if any(int(v)!=v for v in [x,y,w,h]) or min(x,y)<0 or min(w,h)<=0 or x+w>info["width"] or y+h>info["height"]:
            raise ValueError("Crop must use integer pixels inside the input")
        if (fmt.startswith("yuv420") and any(v%2 for v in [x,y,w,h]) or
                fmt.startswith("yuv422") and any(v%2 for v in [x,w])):
            raise ValueError("Align chroma-subsampled crop coordinates and size to native sample boundaries")
        vf = f"crop={w}:{h}:{x}:{y},"+vf
    graph = f"[0:v:0]{vf},split=2[master][proof]"
    limit = []
    if cfg.get("duration_seconds") is not None:
        if cfg["duration_seconds"]<=0:
            raise ValueError("duration_seconds must be positive")
        limit = ["-t", str(cfg["duration_seconds"])]
    with tempfile.TemporaryDirectory(prefix=".master-", dir=output.parent) as directory:
        directory = Path(directory)
        master, proof = directory/"master.mkv", directory/"source.framehash"
        command = [ffmpeg, "-v", "warning", "-nostdin", "-y", "-threads", "4", "-t", str(end), "-i", str(source),
            "-filter_complex_threads", "2", "-filter_complex", graph,
            "-map", "[master]", "-an", "-c:v", "ffv1", "-level", "3", "-g", "1", "-threads", "4",
            "-pix_fmt", fmt, "-r", str(fps), "-fps_mode", "cfr", *limit, str(master),
            "-map", "[proof]", "-an", "-c:v", "rawvideo", "-threads", "2", "-pix_fmt", fmt,
            "-r", str(fps), "-fps_mode", "cfr", *limit, "-f", "framehash", str(proof)]
        with output.with_suffix(".encode.log").open("w") as log:
            subprocess.run(command, stderr=log, check=True)
        actual = probe(ffmpeg, master)
        if actual.get("pixel_format")!=fmt:
            raise ValueError("FFV1 could not retain the native pixel format; refusing a lossless claim")
        decoded = subprocess.check_output([ffmpeg, "-v", "error", "-xerror", "-threads", "4", "-i", str(master),
            "-map", "0:v:0", "-c:v", "rawvideo", "-threads", "2", "-pix_fmt", fmt, "-f", "framehash", "-"], text=True)
        before, after = hashes(proof.read_text()), hashes(decoded)
        if not before or before!=after:
            raise ValueError("Decoded master differs from the original decode/crop/CFR pipeline")
        master.replace(output)
        proof.replace(output.with_suffix(".source.framehash"))
        output.with_suffix(".decoded.framehash").write_text(decoded)
    write_json(output.with_suffix(".master.json"), {"source_sha256": file_sha256(source),
        "source": cfg["source"], "cuts": cuts, "crop": cfg.get("crop"), "fps": str(fps),
        "pixel_format": fmt, "frames": len(after), "duration_seconds": actual["duration"],
        "all_decoded_frames_equal": True, "verification_scope": "selected/cropped original after explicit CFR sampling",
        "original_audio_included": False, "codec": "FFV1"})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    cfg, root = load_config(args.config)
    output = check_output(root/cfg["output"], [root/cfg["source"]], args.overwrite)
    if output.suffix.lower()!=".mkv":
        raise ValueError("Use .mkv for the FFV1 master")
    build(cfg, root, ffmpeg_bin(args.ffmpeg), output)
    print(output)


if __name__=="__main__":
    main()
