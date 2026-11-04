#!/usr/bin/env python3
"""Render continuous log chat or packed transparent captions; no sidecar by default."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from media_common import ffmpeg_bin, load_config, read_json, write_json, check_output, export, smooth


def font_for(spec, root):
    path = root/spec["path"]
    font = ImageFont.truetype(str(path), spec["size"])
    if spec.get("weight") is not None:
        try:
            axes = font.get_variation_axes()
        except OSError:
            axes = []
        if axes:
            values = [spec["weight"] if a["name"].lower() == b"weight" else a["default"] for a in axes]
            font.set_variation_by_axes(values)
    return font


def wrap(draw, text, font, width):
    result, line = [], ""
    for character in text:
        if character == "\n":
            result.append(line)
            line = ""
        elif line and draw.textlength(line+character, font=font) > width:
            result.append(line)
            line = character
        else:
            line += character
    return result+[line] if line else result


def make_clip(ffmpeg, directory, entries, duration, fps, output, alpha=False):
    lines = ["ffconcat version 1.0"]
    active = None
    for filename, seconds in entries:
        if seconds > 1e-8:
            lines += [f"file '{filename}'", f"duration {seconds:.9f}"]
            active = filename
    if active is None:
        raise ValueError("No overlay frames to render")
    lines.append(f"file '{active}'")
    concat = directory/"states.ffconcat"
    concat.write_text("\n".join(lines)+"\n", encoding="utf-8")
    export([ffmpeg, "-v", "warning", "-nostdin", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
            "-vf", f"fps={fps}", "-t", str(duration), "-c:v", "ffv1", "-level", "3", "-g", "1",
            "-pix_fmt", "bgra" if alpha else "bgr0"], output)


def render_chat(cfg, root, directory):
    transcript = read_json(root/cfg["events"])
    events = sorted([e for e in transcript["events"] if e.get("role") == "model" and e.get("text")],
                    key=lambda e: e["time"])
    width, height = cfg["size"]
    body, title = font_for(cfg["body_font"], root), font_for(cfg.get("title_font", cfg["body_font"]), root)
    margin, pad = cfg.get("margin", 24), cfg.get("padding", 20)
    line_height = cfg.get("line_height", round(cfg["body_font"]["size"]*1.45))
    header_height = cfg.get("header_height", 110)
    name = cfg.get("display_name", "Model")
    description = cfg.get("tagline", "")
    label = font_for(cfg.get("label_font", cfg["body_font"]), root)
    logo = Image.open(root/cfg["logo"]).convert("RGBA") if cfg.get("logo") else None
    bg = cfg.get("background", "#f6f7fb")
    messages = [{"role": "user", "text": cfg.get("task_summary", transcript.get("task_summary", ""))}]+events
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    box_width = width-2*margin
    layouts = []
    bottom = header_height+margin
    for message in messages:
        lines = wrap(measure, message["text"], body, box_width-2*pad)
        h = max(1, len(lines))*line_height+2*pad
        top = bottom
        layouts.append({"top": top, "bottom": top+h, "lines": lines, "role": message["role"]})
        bottom = top+h+margin
    document = Image.new("RGB", (width, max(height, bottom+height)), bg)
    draw = ImageDraw.Draw(document)
    for item in layouts:
        color = "#e7efff" if item["role"] == "user" else "#ffffff"
        draw.rounded_rectangle([margin, item["top"], width-margin, item["bottom"]], radius=16,
                               fill=color, outline="#dfe5ef", width=1)
        for i, line in enumerate(item["lines"]):
            draw.text((margin+pad, item["top"]+pad+i*line_height), line, font=body, fill="#243043", anchor="lt")
    states, entries = [], []
    for count, item in enumerate(layouts):
        scroll = max(0, item["bottom"]-(height-margin))
        image = Image.new("RGB", (width, height), bg)
        image.paste(document.crop((0, header_height+scroll, width, height+scroll)), (0, header_height))
        d = ImageDraw.Draw(image)
        d.rectangle([0, item["bottom"]-scroll+1, width, height], fill=bg)
        text_x = margin
        if logo:
            size = min(header_height-2*margin, 72)
            icon = logo.resize((size, size), Image.Resampling.LANCZOS)
            image.paste(icon, (margin, margin), icon)
            text_x += size+12
        d.text((text_x, margin), name, font=title, fill="#17243b", anchor="lt")
        if description:
            d.text((text_x, margin+cfg.get("title_font", cfg["body_font"])["size"]+8), description,
                   font=label, fill="#748099", anchor="lt")
        d.line([(margin, header_height-1), (width-margin, header_height-1)], fill="#dfe5ed")
        name_png = f"chat_{count:04}.png"
        image.save(directory/name_png)
        states.append(name_png)
    times = [0]+[max(0, e["time"]) for e in events]+[cfg["duration"]]
    for name_png, start, stop in zip(states, times, times[1:]):
        seconds = min(stop, cfg["duration"])-start
        if seconds > 0:
            entries.append((name_png, seconds))
    return entries, {"events": events, "display_name": name, "continuous_playback": True,
                     "note": "Exit timing belongs to the compositor, not the message player"}


def render_captions(cfg, root, directory):
    width, height = cfg["size"]
    body = font_for(cfg["body_font"], root)
    title = font_for(cfg.get("title_font", cfg["body_font"]), root)
    header = cfg["header_height"]
    blank = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    previous = blank
    entries, previous_end = [], 0
    for index, cue in enumerate(cfg["cues"]):
        if abs(cue["start"]-previous_end) > .001 or cue["end"] <= cue["start"]:
            raise ValueError("Caption cues must be contiguous and increasing")
        image, color = blank.copy(), cfg.get("color", "#25212b")
        draw = ImageDraw.Draw(image)
        position = cfg.get("stage_position", [24, 12])
        box = draw.textbbox(tuple(position), cue.get("title", ""), font=title, anchor="lt")
        if box[3] > header or box[2] > width:
            raise ValueError("Stage label exceeds its reserved header strip")
        if draw.textlength(cue["text"], font=body) > width-2*cfg.get("horizontal_margin", 30):
            raise ValueError("Single-line caption is too wide; shorten it or adjust typography")
        draw.text(tuple(position), cue.get("title", ""), font=title, fill=color, anchor="lt")
        draw.text((width/2, header+(height-header)/2), cue["text"], font=body, fill=color, anchor="mm")
        name = f"caption_{index:03}.png"
        image.save(directory/name)
        count = max(0, round(cfg.get("fade_seconds", .2)*cfg["fps"]))
        if count/cfg["fps"] >= cue["end"]-cue["start"]:
            raise ValueError("A caption is shorter than its transition")
        for frame in range(1, count+1):
            transition = f"fade_{index:03}_{frame:02}.png"
            Image.blend(previous, image, smooth(frame/count)).save(directory/transition)
            entries.append((transition, 1/cfg["fps"]))
        entries.append((name, cue["end"]-cue["start"]-count/cfg["fps"]))
        previous, previous_end = image, cue["end"]
    if abs(previous_end-cfg["duration"]) > .001:
        raise ValueError("Caption cues must cover the configured duration")
    return entries, {"cues": cfg["cues"], "header_height": header, "background_plate": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("kind", choices=["chat", "captions"])
    p.add_argument("--config", required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--srt-output", help="Only when explicitly requested; do not co-locate with a burned export")
    args = p.parse_args()
    cfg, root = load_config(args.config)
    output = check_output(root/cfg["output"], [root/cfg["events"]] if cfg.get("events") else [], args.overwrite)
    directory = root/cfg.get("frames_dir", f"overlay_frames/{args.kind}")
    directory.mkdir(parents=True, exist_ok=True)
    entries, manifest = (render_chat if args.kind == "chat" else render_captions)(cfg, root, directory)
    make_clip(ffmpeg_bin(args.ffmpeg), directory, entries, cfg["duration"], cfg["fps"], output, args.kind == "captions")
    if args.srt_output:
        if args.kind != "captions":
            raise ValueError("SRT applies only to captions")
        def stamp(t):
            m = round(t*1000)
            return f"{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}"
        srt = check_output(root/args.srt_output, [output], args.overwrite)
        srt.write_text("\n\n".join(f"{i+1}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}"
                                      for i, c in enumerate(cfg["cues"]))+"\n", encoding="utf-8")
    manifest.update(duration=cfg["duration"], states=len(entries), kind=args.kind,
                    config_sha256=hashlib.sha256(Path(args.config).read_bytes()).hexdigest(),
                    external_subtitles=bool(args.srt_output))
    write_json(output.with_suffix(".overlay.json"), manifest)
    print(output)


if __name__ == "__main__":
    main()
