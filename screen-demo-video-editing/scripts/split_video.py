#!/usr/bin/env python3
"""Split paired editing assets; metadata cropping is opt-in and pixel-verified."""
import argparse
import subprocess
from pathlib import Path
from media_common import (ffmpeg_bin, probe, check_output, export, frame_hash,
                          encode_args, write_json)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source")
    p.add_argument("--split-x", type=int, required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--method", choices=["encode", "h264-metadata"], default="encode")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--ffmpeg")
    args = p.parse_args()
    ffmpeg, source = ffmpeg_bin(args.ffmpeg), Path(args.source).resolve()
    info = probe(ffmpeg, source)
    if not 0 < args.split_x < info["width"] or args.split_x % 2:
        raise ValueError("The split must be an even interior pixel column")
    if args.method == "h264-metadata" and info["codec"] != "h264":
        raise ValueError("Metadata display cropping requires H.264")
    report = {"source": str(source), "method": args.method, "files": []}
    for side, x, width, metadata in [
        ("part1", 0, args.split_x, f"crop_left=0:crop_right={info['width']-args.split_x}"),
        ("part2", args.split_x, info["width"]-args.split_x, f"crop_left={args.split_x}:crop_right=0"),
    ]:
        output = check_output(Path(args.output_dir)/side/source.with_suffix(".mp4").name, [source], args.overwrite)
        cmd = [ffmpeg, "-v", "warning", "-nostdin", "-y", "-i", str(source),
               "-map", "0:v:0", "-map", "0:a?"]
        crop = f"crop={width}:{info['height']}:{x}:0"
        if args.method == "h264-metadata":
            # Set only horizontal SPS offsets; preserve existing bottom padding.
            cmd += ["-c", "copy", "-bsf:v", f"h264_metadata={metadata}", "-movflags", "+faststart"]
        else:
            cmd += ["-vf", crop, "-c:a", "copy", *encode_args({}, info["fps"])]
        export(cmd, output)
        actual = probe(ffmpeg, output)
        if (actual["width"], actual["height"]) != (width, info["height"]):
            raise ValueError(f"Unexpected decoded size: {output}")
        checks = []
        if args.method == "h264-metadata":
            for at in [0, info["duration"]/2, max(0, info["duration"]-.2)]:
                expected, decoded = frame_hash(ffmpeg, source, at, crop), frame_hash(ffmpeg, output, at)
                if expected != decoded:
                    raise ValueError(f"Metadata crop is not pixel-exact at {at}: {output}")
                checks.append({"time": at, "decoded_sha256": decoded})
        report["files"].append({"path": str(output), "width": width, "height": actual["height"],
                                "duration": actual["duration"], "pixel_checks": checks})
    write_json(Path(args.output_dir)/"split_manifest.json", report)
    print(Path(args.output_dir).resolve())


if __name__ == "__main__":
    main()
