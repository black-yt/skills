#!/usr/bin/env python3
"""Fit source segments and completed-frame holds into an exact CFR frame budget."""
import argparse
from fractions import Fraction
import math
from pathlib import Path
import subprocess
import tempfile

from media_common import (ffmpeg_bin, load_config, frame_rate, check_output, encode_args, export,
                          write_json, validate, probe, file_sha256, packet_hashes)


def frames(seconds, fps):
    value = Fraction(str(seconds))*fps
    if value.denominator!=1:
        raise ValueError(f"{seconds}s is not an exact frame boundary at {fps} fps")
    return int(value)


def budget(cfg):
    fps = frame_rate(cfg.get("fps", 20))
    total = frames(cfg["target_seconds"], fps)
    result, fit, fixed = [], [], 0
    for i, segment in enumerate(cfg["segments"]):
        s = dict(segment)
        s["id"] = s.get("id", str(i))
        s["hold_frames"] = frames(s.get("hold_seconds", 0), fps)
        if s["hold_frames"]<0:
            raise ValueError("Hold time cannot be negative")
        if s.get("fit"):
            if "duration_seconds" in s:
                raise ValueError("A fit segment cannot also specify duration_seconds")
            fit.append(i)
            s["motion_frames"] = None
        else:
            s["motion_frames"] = frames(s["duration_seconds"], fps)
            if s["motion_frames"]<1:
                raise ValueError("Each segment needs at least one motion/still frame")
            fixed += s["motion_frames"]
        fixed += s["hold_frames"]
        result.append(s)
    if len(fit)>1:
        raise ValueError("Exactly one fit segment may absorb the remaining frame budget")
    if fit:
        result[fit[0]]["motion_frames"] = total-fixed
        if total-fixed<1:
            raise ValueError("Fixed scenes and holds leave no time for the fit segment")
    elif fixed!=total:
        raise ValueError("Segment frames do not add up to target_seconds")
    if not result or len({s["id"] for s in result})!=len(result):
        raise ValueError("Segment IDs must be nonempty and unique")
    cursor = 0
    for s in result:
        s["start_frame"] = cursor
        s["hold_start_frame"] = cursor+s["motion_frames"]
        cursor += s["motion_frames"]+s["hold_frames"]
        s["end_frame"] = cursor
    return fps, total, result


def map_source_time(segment, source_seconds, fps):
    a, b = segment["source_start"], segment["source_end"]
    if not a<=source_seconds<b:
        return None
    return segment["start_frame"]/float(fps)+(source_seconds-a)/(b-a)*segment["motion_frames"]/float(fps)


def run(cfg, root, ffmpeg, output):
    fps, total, segments = budget(cfg)
    size = cfg["canvas"]
    timebase = math.lcm(fps.numerator, 1000)
    # Temporary clips belong to this invocation, so failed attempts cannot
    # accidentally reuse another run's cached end frame or stale retiming.
    source_hashes = {}
    with tempfile.TemporaryDirectory(prefix=".retime-", dir=output.parent) as work:
        work = Path(work)
        paths = []
        for i, s in enumerate(segments):
            source = (root/s["source"]).resolve()
            path = work/f"segment-{i:03}.mp4"
            count = s["motion_frames"]+s["hold_frames"]
            kind = s.get("kind", "video")
            if kind=="copy":
                info = probe(ffmpeg, source)
                if info["has_audio"] and not cfg.get("discard_source_audio", False):
                    raise ValueError("Picture-only retiming requires discard_source_audio=true or a separate synchronized audio workflow")
                if s["hold_frames"] or s.get("source_start", 0)!=0 or "source_end" in s or info["codec"]!="h264":
                    raise ValueError("copy accepts only an H.264 prefix with no extra hold")
                if [info["width"], info["height"]]!=size or abs(info["fps"]-float(fps))>1e-5:
                    raise ValueError("Copied clips must already match canvas and fps")
                cmd = [ffmpeg, "-v", "warning", "-nostdin", "-y", "-i", str(source), "-map", "0:v:0",
                       "-an", "-c:v", "copy", "-frames:v", str(count), "-video_track_timescale", str(timebase)]
            else:
                if kind=="still":
                    inputs = ["-loop", "1", "-framerate", str(fps), "-i", str(source)]
                    clock = "setpts=PTS-STARTPTS"
                elif kind=="video":
                    info = probe(ffmpeg, source)
                    if info["has_audio"] and not cfg.get("discard_source_audio", False):
                        raise ValueError("Picture-only retiming requires discard_source_audio=true or a separate synchronized audio workflow")
                    a, b = float(s.get("source_start", 0)), float(s.get("source_end", info["duration"]))
                    if not 0<=a<b<=info["duration"]+.001:
                        raise ValueError("Source segment is outside its input")
                    s["source_start"], s["source_end"] = a, b
                    inputs = ["-ss", str(a), "-t", str(b-a), "-i", str(source)]
                    clock = f"setpts=(PTS-STARTPTS)*{s['motion_frames']/float(fps)}/{b-a}"
                else:
                    raise ValueError("kind must be video, still or copy")
                vf = (f"{clock},fps={fps},tpad=stop_mode=clone:stop_duration={float(2/fps)},"
                      f"trim=end_frame={s['motion_frames']},setpts=N/({fps}*TB),"
                      f"scale={size[0]}:{size[1]}:force_original_aspect_ratio=decrease,"
                      f"pad={size[0]}:{size[1]}:(ow-iw)/2:(oh-ih)/2:color={cfg.get('background_color','black')},"
                      f"setsar=1,tpad=stop_mode=clone:stop_duration={s['hold_frames']/float(fps)}")
                cmd = [ffmpeg, "-v", "warning", "-nostdin", "-y", *inputs, "-map", "0:v:0", "-an",
                       "-vf", vf, *encode_args(cfg.get("encoding", {}), fps),
                       "-video_track_timescale", str(timebase), "-frames:v", str(count)]
            export(cmd, path)
            report = validate(ffmpeg, path, count/float(fps))
            if report["frames"]!=count:
                raise ValueError("Segment did not decode to the requested frame count; copy needs a closed GOP")
            if kind=="copy":
                if packet_hashes(ffmpeg, path)!=packet_hashes(ffmpeg, source)[:count]:
                    raise ValueError("Copied prefix packet identity could not be verified")
                s["video_packets_unchanged"] = True
            if source not in source_hashes:
                source_hashes[source] = file_sha256(source)
            s["source_sha256"] = source_hashes[source]
            s["validation"] = report
            paths.append(path)
        concat = work/"segments.ffconcat"
        concat.write_text("ffconcat version 1.0\n"+"".join(f"file '{p.name}'\n" for p in paths))
        joined = work/"joined.mp4"
        export([ffmpeg, "-v", "warning", "-nostdin", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
                "-map", "0:v:0", "-c:v", "copy", "-video_track_timescale", str(timebase), "-movflags", "+faststart"], joined)
        final = validate(ffmpeg, joined, total/float(fps))
        if final["frames"]!=total:
            raise ValueError("Final frame budget mismatch")
        joined.replace(output)
    write_json(output.with_suffix(".retiming.json"), {"fps": str(fps), "total_frames": total,
        "duration_seconds": total/float(fps), "segments": segments, "validation": final,
        "audio_policy": "video only; retime composition and add/mux audio afterward"})


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    cfg, root = load_config(args.config)
    inputs = [root/s["source"] for s in cfg["segments"]]
    output = check_output(root/cfg["output"], inputs, args.overwrite)
    run(cfg, root, ffmpeg_bin(args.ffmpeg), output)
    print(output)


if __name__=="__main__":
    main()
