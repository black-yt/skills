#!/usr/bin/env python3
"""Detect idle candidates, build an original-time EDL, and render synchronized cuts."""
import argparse
import math
import re
import subprocess
from pathlib import Path

from media_common import (ffmpeg_bin, probe, write_json, read_json, load_config, merge_cuts,
                          edited_time, check_output, export, encode_args, validate)


def detect(args):
    ffmpeg = ffmpeg_bin(args.ffmpeg)
    source = Path(args.source).resolve()
    info = probe(ffmpeg, source)
    result = subprocess.run([ffmpeg, "-hide_banner", "-nostdin", "-i", str(source), "-map", "0:v:0", "-an",
                             "-vf", f"scale={args.width}:-2:flags=area,fps={args.analysis_fps},"
                             f"freezedetect=n={args.noise}:d={args.minimum}", "-f", "null", "-"],
                            capture_output=True, text=True, check=True)
    intervals, start = [], None
    for line in result.stderr.splitlines():
        value = re.search(r"freeze_start: ([\d.]+)", line)
        if value:
            start = float(value[1])
        value = re.search(r"freeze_end: ([\d.]+)", line)
        if value and start is not None:
            intervals.append([start, float(value[1])])
            start = None
    if start is not None:
        intervals.append([start, info["duration"]])
    write_json(args.output, {"source": str(source), "source_duration": info["duration"],
                             "fps": info["fps"], "freezes": intervals,
                             "analysis": {"width": args.width, "fps": args.analysis_fps, "noise": args.noise}})


def build(args):
    frozen = read_json(args.freezes)
    end = frozen["source_duration"]-args.tail
    fps = args.fps or frozen["fps"]
    if (args.tail < 0 or not 0 <= args.head < end or fps <= 0 or
            not 0 <= args.keep_fraction <= 1 or args.minimum_pause < 0):
        raise ValueError("Invalid trim or pause settings")
    cuts = [[0, args.head]] if args.head else []
    for start, stop in frozen["freezes"]:
        keep = max(args.minimum_pause, (stop-start)*args.keep_fraction)
        a = math.ceil((start+keep/2)*fps-1e-8)/fps
        b = math.floor((stop-keep/2)*fps+1e-8)/fps
        if b > a:
            cuts.append([a, b])
    if args.cycles:
        cuts += [[r["source_start"], r["source_end"]] for r in read_json(args.cycles)["runs"]]
    cuts = merge_cuts(cuts, end)
    opening = None
    if args.first_motion is not None:
        a, b = args.first_motion-args.still_before_motion, args.first_motion+args.protect_after_motion
        if a < 0 or b > end:
            raise ValueError("Protected real opening is outside the recording")
        # Protect original still footage AND the complete first movement.
        cuts = merge_cuts([[x, min(y, a)] for x, y in cuts if x < a]+
                          [[max(x, b), y] for x, y in cuts if y > b]+[[0, a]], end)
        opening = {"source_start": a, "first_motion": args.first_motion,
                   "stationary_seconds": args.still_before_motion, "protected_until": b}
    write_json(args.output, {"source": frozen["source"], "output": args.video_output,
                             "source_end": end, "fps": fps, "cuts": cuts, "opening": opening,
                             "estimated_duration": edited_time(end, cuts), "encoding": {"crf": 18}})


def render(args):
    cfg, root = load_config(args.plan)
    ffmpeg = ffmpeg_bin(args.ffmpeg)
    source = root/cfg["source"]
    output = check_output(root/cfg["output"], [source], args.overwrite)
    info = probe(ffmpeg, source)
    end = cfg.get("source_end", info["duration"])
    if end > info["duration"]+.01:
        raise ValueError("source_end exceeds input duration")
    cuts = merge_cuts(cfg.get("cuts", []), end)
    selection = "+".join(f"gte(t,{a:.9f})*lt(t,{b:.9f})" for a, b in cuts)
    shift = "+".join(f"gte(PTS*TB,{b:.9f})*{b-a:.9f}" for a, b in cuts)
    video = f"select='not({selection})',setpts='PTS-({shift})/TB'" if cuts else "null"
    audio = f"aselect='not({selection})',asetpts='PTS-({shift})/TB'" if cuts else "anull"
    filters = f"[0:v:0]{video}[v]"
    if info["has_audio"]:
        filters += f";[0:a:0]{audio}[a]"
    cmd = [ffmpeg, "-v", "warning", "-nostdin", "-y", "-t", str(end), "-i", str(source),
           "-filter_complex_threads", "2", "-filter_complex", filters, "-map", "[v]"]
    if info["has_audio"]:
        cmd += ["-map", "[a]", "-c:a", "aac", "-b:a", "160k"]
    cmd += encode_args(cfg.get("encoding", {}), cfg.get("fps", info["fps"]))
    export(cmd, output)
    report = validate(ffmpeg, output, edited_time(end, cuts))
    write_json(output.with_suffix(".validation.json"), report)
    print(output)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    d = sub.add_parser("detect-static")
    d.add_argument("source")
    d.add_argument("--output", required=True)
    d.add_argument("--width", type=int, default=832)
    d.add_argument("--analysis-fps", type=float, default=8)
    d.add_argument("--noise", default="-60dB")
    d.add_argument("--minimum", type=float, default=1.5)
    d.add_argument("--ffmpeg")
    d.set_defaults(func=detect)
    b = sub.add_parser("build-plan")
    b.add_argument("--freezes", required=True)
    b.add_argument("--cycles")
    b.add_argument("--output", required=True)
    b.add_argument("--video-output", default="edited.mp4")
    b.add_argument("--head", type=float, default=0)
    b.add_argument("--tail", type=float, default=0)
    b.add_argument("--fps", type=float)
    b.add_argument("--keep-fraction", type=float, default=.02)
    b.add_argument("--minimum-pause", type=float, default=.5)
    b.add_argument("--first-motion", type=float)
    b.add_argument("--still-before-motion", type=float, default=3)
    b.add_argument("--protect-after-motion", type=float, default=1)
    b.set_defaults(func=build)
    r = sub.add_parser("render")
    r.add_argument("--plan", required=True)
    r.add_argument("--overwrite", action="store_true")
    r.add_argument("--ffmpeg")
    r.set_defaults(func=render)
    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
