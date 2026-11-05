#!/usr/bin/env python3
"""Compose floating panels, an independent secondary player, and selective pointer close-ups."""
import argparse
import math
import subprocess
from pathlib import Path

from media_common import (ffmpeg_bin, load_config, read_json, write_json, probe, check_output,
                          export, encode_args, smooth_expr, validate)


def distance(np, width, height, rect, radius):
    x, y, w, h = rect
    xx = np.arange(width, dtype=np.float32)[None, :]+.5
    yy = np.arange(height, dtype=np.float32)[:, None]+.5
    qx, qy = np.abs(xx-x-w/2)-(w/2-radius), np.abs(yy-y-h/2)-(h/2-radius)
    return np.sqrt(np.maximum(qx, 0)**2+np.maximum(qy, 0)**2)+np.minimum(np.maximum(qx, qy), 0)-radius


def prepare_assets(cfg, root, directory):
    import numpy as np
    from PIL import Image, ImageOps
    directory.mkdir(parents=True, exist_ok=True)
    width, height = cfg["canvas"]
    if cfg.get("background"):
        image = ImageOps.exif_transpose(Image.open(root/cfg["background"])).convert("RGB")
        image = ImageOps.fit(image, (width, height), Image.Resampling.LANCZOS)
    else:
        image = Image.new("RGB", (width, height), cfg.get("background_color", "#f6ede4"))
    image.save(directory/"background.png")
    main = cfg["main"]
    initial, final = main["initial_rect"], main.get("final_rect", main["initial_rect"])
    maximum = [0, 0, max(initial[2], final[2]), max(initial[3], final[3])]
    panels = [("main", maximum)]
    if cfg.get("secondary"):
        panels.append(("secondary", cfg["secondary"]["rect"]))
    for name, rect in panels:
        _, _, w, h = rect
        scale = w/initial[2] if name == "main" else 1
        radius = cfg.get("corner_radius", 16)*scale
        d = distance(np, w, h, [0, 0, w, h], radius)
        mask = np.round(np.clip(.5-d, 0, 1)*255).astype(np.uint8)
        Image.fromarray(mask).save(directory/f"{name}_mask.png")
        pad = 128
        shadow = cfg.get("shadow", {})
        d = distance(np, w+2*pad, h+2*pad,
                     [pad, pad+shadow.get("offset_y", 14)*scale, w, h], radius)
        alpha = shadow.get("opacity", .35)*np.exp(-.5*(np.maximum(d, 0)/(shadow.get("blur", 20)*scale))**2)
        rgba = np.zeros((h+2*pad, w+2*pad, 4), dtype=np.uint8)
        rgba[:, :, 3] = np.round(alpha*255).astype(np.uint8)
        Image.fromarray(rgba).save(directory/f"{name}_shadow.png")
    return maximum[2:]


def camera_windows(cfg, duration):
    camera = cfg.get("camera", {})
    result = []
    gap = camera.get("merge_gap", 0)
    for start, end in sorted(camera.get("windows", [])):
        if not 0 <= start < end <= duration+.001:
            raise ValueError("Camera windows must fit the finished timeline")
        if result and start <= result[-1][1]+gap:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    if camera.get("max_segments") is not None and len(result) > camera["max_segments"]:
        raise ValueError("Camera segment limit exceeded; curate or merge neighboring windows")
    return result


def build_filter(cfg, root, size, source_info, overlay_indices, has_secondary_input, offset):
    fps = cfg.get("fps", source_info["fps"])
    windows = camera_windows(cfg, source_info["duration"])
    t, clock = f"(t+{offset})", f"(on/{fps}+{offset})"
    initial = cfg["main"]["initial_rect"]
    final = cfg["main"].get("final_rect", initial)
    transition = cfg.get("transition")
    if transition:
        start = transition["start"]
        if isinstance(start, dict):
            field = start.get("field", "executed_at")
            event = next((e for e in read_json(root/cfg["events"])["events"]
                          if e.get("step") == start["event_step"] and field in e), None)
            if event is None:
                raise ValueError(f"No event for step {start['event_step']} contains {field}")
            start = event[field]
        if not 0 <= start < source_info["duration"] or transition["duration"] <= 0:
            raise ValueError("Invalid transition timing")
        end = start+transition["duration"]
        ease = smooth_expr(f"({t}-{start})/{transition['duration']}")
    else:
        start, end, ease = None, None, "0"
    w0, wf = initial[2], final[2]
    width = f"2*floor(({w0}+({wf}-{w0})*{ease})/2+.5)"
    x = f"{initial[0]}+({final[0]}-{initial[0]})*{ease}"
    y = f"{initial[1]}+({final[1]}-{initial[1]})*{ease}"
    crop = cfg["main"]["crop"]
    cx0, cy0, cw, ch = crop
    if (min(crop) < 0 or cw <= 0 or ch <= 0 or cx0+cw > source_info["width"] or
            cy0+ch > source_info["height"]):
        raise ValueError("Main crop is outside the recording")
    for rect in [initial, final]:
        if rect[2] % 2 or rect[3] % 2 or abs((rect[2]/rect[3])/(cw/ch)-1) > .01:
            raise ValueError("Main rectangles must be even-sized and preserve the crop aspect ratio")
    camera = cfg.get("camera", {})
    fraction = camera.get("visible_fraction", .6)
    ramp = camera.get("ramp_seconds", .25)
    if not 0 < fraction <= 1 or ramp <= 0:
        raise ValueError("visible_fraction must be in (0,1]; ramp must be positive")
    active = []
    for a, b in windows:
        effective = min(ramp, (b-a)/2)
        active.append(f"({smooth_expr(f'({clock}-{a})/{effective}')}*"
                      f"(1-{smooth_expr(f'({clock}-{b-effective})/{effective}')}))")
    zoom = f"1+{1/fraction-1}*min(1,{' + '.join(active) or '0'})"
    moves = read_json(root/camera["moves_file"])["moves"] if camera.get("moves_file") else camera.get("moves", [])
    centers = []
    initial_center = camera.get("initial_center", [cx0+cw/2, cy0+ch/2])
    for axis, field in enumerate(["x", "y"]):
        current = initial_center[axis]
        terms = [str(current-[cx0, cy0][axis])]
        for move in sorted(moves, key=lambda m: m["time"]):
            target = move[field]
            if not math.isfinite(target):
                raise ValueError("Pointer coordinates must be finite")
            phase = f"({clock}-{move['time']})/{camera.get('follow_seconds', .4)}"
            terms.append(f"({target-current})*{smooth_expr(phase)}")
            current = target
        centers.append("+".join(terms))
    xp = f"max(0,min(iw-iw/zoom,({centers[0]})-iw/(2*zoom)))"
    yp = f"max(0,min(ih-ih/zoom,({centers[1]})-ih/(2*zoom)))"
    mw, mh = size
    shadow_width = f"2*floor(({width})*{mw+256}/{mw}/2+.5)"
    pad = f"128*({width})/{mw}"
    native_secondary = bool(cfg.get("secondary")) and not has_secondary_input
    graph = ["[0:v]split=2[main_source][secondary_source]" if native_secondary else "[0:v]null[main_source]",
             f"[main_source]crop={cw}:{ch}:{cx0}:{cy0},zoompan=z='{zoom}':x='{xp}':y='{yp}':"
             f"d=1:s={mw}x{mh}:fps={fps},scale=w='{width}':h=-2:eval=frame,"
             f"pad={mw}:{mh}:0:0:color=black:eval=frame,setsar=1,format=rgb24[main_rgb]",
             f"[2:v]scale=w='{width}':h=-2:eval=frame,pad={mw}:{mh}:0:0:color=black:eval=frame,format=gray[main_mask]",
             "[main_rgb][main_mask]alphamerge=shortest=1[main_rgba]",
             f"[3:v]scale=w='{shadow_width}':h=-2:eval=frame,format=rgba[main_shadow]",
             "[1:v]format=rgb24[background]",
             f"[background][main_shadow]overlay=x='({x})-({pad})':y='({y})-({pad})':"
             "eval=frame:format=rgb[shaded]"]
    base = "shaded"
    if cfg.get("secondary"):
        secondary = cfg["secondary"]
        sx, sy, sw, sh = secondary["rect"]
        dx = f"{sx}+({transition.get('secondary_exit_x', cfg['canvas'][0]+128)}-{sx})*{ease}" if transition else str(sx)
        enabled = f"lt({t},{end+1/fps})" if transition else "1"
        source = "6:v" if has_secondary_input else "secondary_source"
        scrop = secondary.get("crop")
        scrop_filter = f"crop={scrop[2]}:{scrop[3]}:{scrop[0]}:{scrop[1]}," if scrop else ""
        graph += [f"[{source}]{scrop_filter}scale={sw}:{sh}:flags=lanczos,setsar=1,format=rgb24[secondary_rgb]",
                  "[4:v]format=gray[secondary_mask]",
                  "[secondary_rgb][secondary_mask]alphamerge=shortest=1[secondary_rgba]",
                  f"[{base}][5:v]overlay=x='({dx})-128':y={sy-128}:format=rgb:enable='{enabled}'[shadows]"]
        base = "shadows"
    graph.append(f"[{base}][main_rgba]overlay=x='{x}':y='{y}':eval=frame:format=rgb:shortest=1[desktop]")
    base = "desktop"
    if cfg.get("secondary"):
        graph.append(f"[{base}][secondary_rgba]overlay=x='{dx}':y={sy}:format=rgb:"
                     f"shortest=0:eof_action=repeat:enable='{enabled}'[panels]")
        base = "panels"
    for n, (index, overlay) in enumerate(overlay_indices):
        source = f"{index}:v"
        if overlay.get("crop"):
            a, b, w, h = overlay["crop"]
            graph.append(f"[{source}]crop={w}:{h}:{a}:{b}[overlay{n}]")
            source = f"overlay{n}"
        ox, oy = overlay.get("position", [0, 0])
        graph.append(f"[{base}][{source}]overlay=x={ox}:y={oy}:format=rgb:shortest=0:eof_action=repeat[layer{n}]")
        base = f"layer{n}"
    if cfg.get("encoding", {}).get("codec")=="ffv1":
        graph.append(f"[{base}]format=bgr0[v]")
    else:
        graph.append(f"[{base}]scale=iw:ih:in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p[v]")
    return ";".join(graph), {"transition_start": start, "transition_end": end, "camera_windows": windows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--ffmpeg")
    parser.add_argument("--preview-at", type=float)
    parser.add_argument("--duration", type=float)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--progress")
    args = parser.parse_args()
    cfg, root = load_config(args.config)
    ffmpeg, source = ffmpeg_bin(args.ffmpeg), root/cfg["source"]
    info = probe(ffmpeg, source)
    fps = cfg.get("fps", info["fps"])
    offset = args.preview_at or 0
    if not 0 <= offset < info["duration"]:
        raise ValueError("Preview is outside the video")
    directory = root/cfg.get("assets_dir", "render_assets")
    size = prepare_assets(cfg, root, directory)
    cmd = [ffmpeg, "-v", "warning", "-nostdin", "-y", "-ss", str(offset), "-i", str(source)]
    image_names = ["background.png", "main_mask.png", "main_shadow.png"]
    if cfg.get("secondary"):
        image_names += ["secondary_mask.png", "secondary_shadow.png"]
    for name in image_names:
        cmd += ["-framerate", str(fps), "-i", str(directory/name)]
    static_indices = list(range(1, 1+len(image_names)))
    index = 1+len(image_names)
    has_secondary = bool(cfg.get("secondary", {}).get("source"))
    if has_secondary:
        cmd += ["-ss", str(offset), "-i", str(root/cfg["secondary"]["source"])]
        index += 1
    overlays = []
    for overlay in cfg.get("overlays", []):
        path = root/overlay["source"]
        if path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            cmd += ["-framerate", str(fps), "-i", str(path)]
            static_indices.append(index)
        else:
            seek = offset
            if overlay.get("loop"):
                loop_duration = probe(ffmpeg, path)["duration"]
                if loop_duration<=0:
                    raise ValueError("Loop overlay needs a positive duration")
                seek %= loop_duration
                cmd += ["-stream_loop", "-1"]
            cmd += ["-ss", str(seek), "-i", str(path)]
        overlays.append((index, overlay))
        index += 1
    graph, timeline = build_filter(cfg, root, size, info, overlays, has_secondary, offset)
    # Decode large static PNGs once; cache their decoded frame in the loop filter.
    for index in static_indices:
        graph = graph.replace(f"[{index}:v]", f"[static{index}]")
    cache = [f"[{index}:v]loop=loop=-1:size=1:start=0,setpts=N/({fps}*TB)[static{index}]"
             for index in static_indices]
    graph = ";".join(cache+[graph])
    cmd += ["-filter_complex_threads", "2", "-filter_complex", graph, "-map", "[v]"]
    if args.preview_at is not None:
        output = check_output(directory/f"preview_{offset:07.2f}.png", [source], args.overwrite)
        cmd += ["-frames:v", "1", "-update", "1"]
    else:
        output = check_output(root/cfg["output"], [source], args.overwrite)
        cmd += ["-map", "0:a?", "-c:a", "copy"]
        if cfg.get("encoding", {}).get("codec")=="ffv1":
            if output.suffix.lower()!=".mkv":
                raise ValueError("Use .mkv for a lossless FFV1 composition")
            cmd += ["-c:v", "ffv1", "-level", "3", "-g", "1", "-pix_fmt", "bgr0", "-threads", "4",
                    "-r", str(fps), "-fps_mode", "cfr"]
        else:
            cmd += encode_args(cfg.get("encoding", {}), fps)
        cmd += ["-t", str(args.duration or info["duration"])]
        if args.progress:
            cmd += ["-progress", str(Path(args.progress).resolve()), "-nostats"]
    export(cmd, output)
    if args.preview_at is None:
        timeline["validation"] = validate(ffmpeg, output, args.duration or info["duration"], cfg.get("burned_only", False))
        write_json(output.with_suffix(".presentation.json"), timeline)
    print(output)


if __name__ == "__main__":
    main()
