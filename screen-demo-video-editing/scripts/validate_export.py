#!/usr/bin/env python3
"""Inspect streams, fully decode an export, and optionally prove unchanged video packets."""
import argparse
import json
from media_common import ffmpeg_bin, validate, video_hash, write_json


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("video")
    p.add_argument("--ffmpeg")
    p.add_argument("--expected-duration", type=float)
    p.add_argument("--burned-only", action="store_true")
    p.add_argument("--compare-video")
    p.add_argument("--report")
    args = p.parse_args()
    ffmpeg = ffmpeg_bin(args.ffmpeg)
    result = validate(ffmpeg, args.video, args.expected_duration, args.burned_only)
    if args.compare_video:
        original, actual = video_hash(ffmpeg, args.compare_video), video_hash(ffmpeg, args.video)
        if original != actual:
            raise ValueError("Compressed video differs")
        result.update(video_payload_unchanged=True, video_sha256=actual)
    if args.report:
        write_json(args.report, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
