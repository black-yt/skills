#!/usr/bin/env python3
"""Render loopable moving dashes along rounded orthogonal paths, with alpha."""
import argparse
import math

import numpy as np
from PIL import Image, ImageDraw, ImageColor

from media_common import load_config, ffmpeg_bin, check_output, frame_rate, FrameWriter, write_json, validate
from render_overlays import font_for


def rounded_path(points, radius):
    points = np.asarray(points, dtype=float)
    if points.ndim!=2 or points.shape[1]!=2 or len(points)<2 or not np.isfinite(points).all():
        raise ValueError("Each path needs finite x/y points")
    if np.any(np.linalg.norm(np.diff(points, axis=0), axis=1)==0) or radius<0:
        raise ValueError("Path segments must have length; corner radius cannot be negative")
    result = [points[0]]
    for i in range(1, len(points)-1):
        before, p, after = points[i-1:i+2]
        a, b = (p-before)/np.linalg.norm(p-before), (after-p)/np.linalg.norm(after-p)
        dot = float(np.dot(a, b))
        if dot>.999999:
            result.append(p)
            continue
        if abs(dot)>1e-6:
            raise ValueError("Use orthogonal corners (or collinear points), not arbitrary bends")
        r = min(radius, np.linalg.norm(p-before)/2, np.linalg.norm(after-p)/2)
        if r==0:
            result.append(p)
            continue
        center = p-a*r+b*r
        start = p-a*r-center
        end = p+b*r-center
        angle = math.atan2(start[1], start[0])
        turn = math.atan2(start[0]*end[1]-start[1]*end[0], np.dot(start, end))
        result += [center+r*np.array([math.cos(t), math.sin(t)])
                   for t in np.linspace(angle, angle+turn, max(6, math.ceil(r/2)))]
    result.append(points[-1])
    p = np.array(result)
    # Corner samples can include a repeated tangent point.
    return p[np.r_[True, np.linalg.norm(np.diff(p, axis=0), axis=1)>1e-8]]


def position(path, distance):
    lengths = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    return np.array([np.interp(distance, lengths, path[:, k]) for k in (0, 1)])


def render_frame(cfg, paths, phase, label_font=None):
    im = Image.new("RGBA", tuple(cfg["canvas"]))
    d = ImageDraw.Draw(im)
    stroke = cfg.get("stroke", 10)
    dash, period = cfg.get("dash_length", 36), cfg.get("dash_period", 64)
    if not 0<dash<period or stroke<=0:
        raise ValueError("Need 0 < dash_length < dash_period and a positive stroke")
    color = ImageColor.getcolor(cfg.get("color", "#45494f"), "RGBA")
    for spec, path in zip(cfg["paths"], paths):
        length = np.linalg.norm(np.diff(path, axis=0), axis=1).sum()
        for start in np.arange(phase*period-period, length, period):
            a, b = max(0, start), min(length, start+dash)
            if b<=a:
                continue
            points = [position(path, t) for t in np.linspace(a, b, max(2, math.ceil((b-a)/2)))]
            d.line([tuple(p) for p in points], fill=color, width=stroke)
            for p in (points[0], points[-1]):
                r = stroke/2
                d.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=color)
        end = path[-1]
        tangent = (end-path[-2])/np.linalg.norm(end-path[-2])
        normal = np.array([-tangent[1], tangent[0]])
        head = cfg.get("arrow_size", stroke*2)
        left, right = end-head*tangent+head*.6*normal, end-head*tangent-head*.6*normal
        d.line([tuple(left), tuple(end), tuple(right)], fill=color, width=stroke)
        for p in (left, end, right):
            r = stroke/2
            d.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), fill=color)
        if spec.get("label"):
            if label_font is None:
                raise ValueError("Labels require a configured label_font")
            d.text(tuple(spec["label_position"]), spec["label"], font=label_font, fill=color, anchor="mm")
    return im


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    cfg, root = load_config(args.config)
    output = check_output(root/cfg["output"], overwrite=args.overwrite)
    fps = frame_rate(cfg.get("fps", 20))
    count = round(cfg.get("cycle_seconds", 2)*float(fps))
    if count<2 or not cfg.get("paths"):
        raise ValueError("A flow loop needs paths and at least two frames")
    paths = [rounded_path(s["points"], cfg.get("corner_radius", 20)) for s in cfg["paths"]]
    label = font_for(cfg["label_font"], root) if cfg.get("label_font") else None
    ffmpeg = ffmpeg_bin(args.ffmpeg)
    with FrameWriter(ffmpeg, output, cfg["canvas"], fps, alpha=True) as writer:
        for n in range(count):
            # One dash period per loop: last -> first advances by a normal frame,
            # rather than resetting a dot from the arrowhead to the path origin.
            writer.write(render_frame(cfg, paths, n/count, label))
    write_json(output.with_suffix(".flow.json"), {"validation": validate(ffmpeg, output, count/float(fps)),
        "direction": "from first point to last point", "cycle_frames": count,
        "dash_period_pixels": cfg.get("dash_period", 64), "phase_advance_per_frame": 1/count,
        "alpha_preserved": True})
    print(output)


if __name__=="__main__":
    main()
