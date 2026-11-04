#!/usr/bin/env python3
"""Find redundant preview-blink cycles, masking only reviewed cursor regions.

The region configuration belongs to this recording; review it before using
another video. Export always uses original frames at their original size.
"""

import argparse
import json
import os
import subprocess
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")

from media_common import ffmpeg_bin as find_ffmpeg, read_json as load_json, write_json as save_json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--regions", required=True)
    parser.add_argument("--output", default="cycle_report.json")
    parser.add_argument("--ffmpeg")
    args = parser.parse_args()
    try:
        import numpy as np
    except ImportError as error:
        raise SystemExit("Install NumPy: python -m pip install numpy") from error
    cfg = load_json(args.regions)
    ffmpeg = find_ffmpeg(args.ffmpeg)
    fps, width, height = cfg["fps"], cfg["width"], cfg["height"]
    if fps <= 0 or cfg["source_duration"] <= 0 or min(width, height) < 1:
        raise ValueError("Invalid analysis dimensions or duration")
    for roi in [cfg["signal_roi"], *cfg["static_regions"], *cfg["cursor_ignore_regions"]]:
        x1, y1, x2, y2 = roi
        if not (0 <= x1 < x2 <= width and 0 <= y1 < y2 <= height):
            raise ValueError(f"ROI outside the analysis frame: {roi}")
    raw = subprocess.check_output([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-threads", "4",
        "-ss", str(cfg["source_start"]), "-t", str(cfg["source_duration"]),
        "-i", str(Path(args.source).resolve()), "-map", "0:v:0", "-an",
        "-vf", f"fps={fps},scale={width}:{height}:flags=area", "-pix_fmt", "gray",
        "-f", "rawvideo", "-",
    ])
    frames = np.frombuffer(raw, dtype=np.uint8).reshape(-1, height, width)
    x1, y1, x2, y2 = cfg["signal_roi"]
    signal = frames[:, y1:y2, x1:x2].mean(axis=(1, 2))
    threshold = (np.percentile(signal, 10) + np.percentile(signal, 90)) / 2
    crossings = np.where((signal[:-1] < threshold) & (signal[1:] >= threshold))[0] + 1
    crossings = [int(v) for i, v in enumerate(crossings)
                 if i == 0 or v-crossings[i-1] >= cfg["minimum_period_seconds"]*fps]
    if len(crossings) < 3:
        raise SystemExit("Not enough complete cycles; adjust the reviewed region/configuration")
    cycles = [{"a": a, "b": b} for a, b in zip(crossings[:-1], crossings[1:])]
    unmasked = np.zeros((height, width), dtype=bool)
    for x1, y1, x2, y2 in cfg["static_regions"]:
        unmasked[y1:y2, x1:x2] = True
    mask = unmasked.copy()
    for x1, y1, x2, y2 in cfg["cursor_ignore_regions"]:
        mask[y1:y2, x1:x2] = False
    x1, y1, x2, y2 = cfg["signal_roi"]
    if not mask.any():
        raise ValueError("Reviewed static regions must contain unmasked pixels")
    reps = [np.median(frames[c["a"]:c["b"]], axis=0).astype(np.float32) for c in cycles]
    comparisons, changes = [], []
    for i in range(1, len(cycles)):
        prev, curr = cycles[i-1], cycles[i]
        a = frames[prev["a"]:prev["b"], y1:y2, x1:x2].astype(np.float32).reshape(prev["b"]-prev["a"], -1)
        b = frames[curr["a"]:curr["b"], y1:y2, x1:x2].astype(np.float32).reshape(curr["b"]-curr["a"], -1)
        squared = np.maximum(0, (a*a).sum(1)[:, None] + (b*b).sum(1)[None, :] - 2*a@b.T)
        nearest = np.argmin(squared, axis=1)
        content_error = float(np.median(np.abs(a-b[nearest]).mean(axis=1)))
        difference = np.abs(reps[i]-reps[i-1])
        pixels = int(np.count_nonzero((difference > 15) & mask))
        original_pixels = int(np.count_nonzero((difference > 15) & unmasked))
        mean = float(difference[mask].mean())
        changed = pixels >= 10 or mean >= 0.25 or content_error >= 0.5
        changes.append(changed)
        comparisons.append({"cycle": i, "source_time": cfg["source_start"]+curr["a"]/fps,
                            "changed_pixels_before_cursor_mask": original_pixels,
                            "changed_pixels_after_cursor_mask": pixels,
                            "static_mae": mean, "phase_matched_content_mae": content_error,
                            "changed": changed})
    bounds = [0] + [i+1 for i, value in enumerate(changes) if value] + [len(cycles)]
    runs = []
    for first, last in zip(bounds[:-1], bounds[1:]):
        if last-first < 3:
            continue
        # Keep half a cycle on each side, preserving about one cycle of thought
        # time while cutting a whole number of otherwise redundant cycles.
        a = (cycles[first]["a"] + cycles[first]["b"]) // 2
        b = (cycles[last-1]["a"] + cycles[last-1]["b"]) // 2
        candidates = []
        for da in range(-5, 6):
            for db in range(-5, 6):
                start, stop = a+da, b+db
                if not (1 <= start < stop < len(frames)):
                    continue
                diff = np.abs(frames[start-1].astype(np.int16)-frames[stop].astype(np.int16))
                content_pixels = int(np.count_nonzero((diff > 15) & mask))
                mean = float(diff.mean())
                cost = mean + content_pixels*0.05 + 0.0003*(abs(da)+abs(db))
                candidates.append((cost, mean, start, stop, content_pixels))
        _, mean, start, stop, content_pixels = min(candidates)
        if content_pixels >= 10:
            continue  # Keep this run for manual review instead of forcing a cut.
        runs.append({"first_cycle": first, "last_cycle": last-1,
                     "removed_cycles": last-first-1,
                     "source_start": round(cfg["source_start"]+start/fps, 6),
                     "source_end": round(cfg["source_start"]+stop/fps, 6),
                     "seam_mae": mean, "seam_content_changed_pixels": content_pixels})
    report = {"source": Path(args.source).name,
              "period_seconds": float(np.median(np.diff(crossings))/fps),
              "cycle_count": len(cycles), "comparisons": comparisons, "runs": runs,
              "removed_cycles": sum(r["removed_cycles"] for r in runs),
              "removed_seconds": sum(r["source_end"]-r["source_start"] for r in runs)}
    save_json(args.output, report)
    print(f"Period {report['period_seconds']:.2f}s; remove {report['removed_cycles']} cycles, "
          f"{report['removed_seconds']:.2f}s -> {args.output}")


if __name__ == "__main__":
    main()
