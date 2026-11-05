#!/usr/bin/env python3
"""Forward-test animation, source provenance and exact retiming with synthetic pixels."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

from animate_cards import CardScene
from render_flow import rounded_path, render_frame
from retime_video import budget
from render_presentation import build_filter
from media_common import (FrameWriter, ffmpeg_bin, frame_rate, read_json, write_json, validate)

SCRIPTS = Path(__file__).resolve().parent


def pixel_frame(ffmpeg, path, time, rgba=False, crop=None):
    cmd = [ffmpeg, "-v", "error", "-ss", str(time), "-i", str(path), "-frames:v", "1"]
    if crop:
        cmd += ["-vf", crop]
    return subprocess.check_output([*cmd, "-pix_fmt", "rgba" if rgba else "rgb24", "-f", "rawvideo", "-"])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work-dir", required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--font", required=True)
    args = p.parse_args()
    root = Path(args.work_dir).resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError("Use a new/empty smoke-test directory")
    root.mkdir(parents=True, exist_ok=True)
    ffmpeg, font = ffmpeg_bin(args.ffmpeg), str(Path(args.font).resolve())
    commands = []
    def call(script, *params):
        cmd = [sys.executable, str(SCRIPTS/script), *map(str, params)]
        if script not in {"prepare_trace.py"}:
            cmd += ["--ffmpeg", ffmpeg]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL)
        commands.append([script, *map(str, params)])
    def config(name, data):
        path = root/(name+".json")
        write_json(path, data)
        return path
    images = root/"images"
    images.mkdir()
    colors = []
    for i in range(24):
        color = ((43+i*47)%180+35, (61+i*29)%180+35, (77+i*19)%180+35)
        colors.append(color)
        im = Image.new("RGB", (64, 40), color)
        ImageDraw.Draw(im).text((2, 2), str(i), fill="white")
        im.save(images/f"card-{i:03}.png")
    cards = {"images_glob": "images/card-*.png", "output": "cards.mkv", "canvas": [640, 400], "fps": 20,
        "background_color": "#f6e2ce", "grid": {"rows": 4, "columns": 6, "rect": [20, 80, 600, 240], "gap": 4},
        "first_view": {"row": 1, "column": 2, "rows": 2, "columns": 2},
        "stack": {"quad": [[60,160],[260,110],[310,250],[110,300]], "depth_offset": [-10,-20], "visible_layers": 4},
        "flight_scope": "first", "edge_policy": "whole",
        "timing": {"stack": .4, "spread": .4, "near_hold": .2, "pullback": .4, "full_hold": .2}}
    call("animate_cards.py", "--config", config("cards", cards))
    scene = CardScene(cards, root)
    for phase, point in [("near_hold", .8), ("full_hold", 1.5)]:
        rgb = np.frombuffer(pixel_frame(ffmpeg, root/"cards.mkv", point), dtype="uint8").reshape(400,640,3)
        ids = scene.first_ids if phase=="near_hold" else list(range(24))
        for idx in ids:
            q = scene.full[idx].mean(axis=0)
            if phase=="near_hold":
                q = scene.final_center+scene.zoom*(q-scene.center)
            x, y = np.round(q+scene.rect[:2]).astype(int)
            assert np.max(np.abs(rgb[y,x].astype(int)-colors[idx]))<=1, (phase, idx, rgb[y,x], colors[idx])
    report = read_json(root/"cards.animation.json")
    assert len(report["flight_ids"])==4 and len(report["source_images"])==24
    assert len(report["visibility"][0]["visible_ids"])==4
    cards_all = dict(cards, output="cards-all.mkv", flight_scope="all")
    call("animate_cards.py", "--config", config("cards-all", cards_all))
    assert len(read_json(root/"cards-all.animation.json")["flight_ids"])==24

    flow = {"output": "flow.mkv", "canvas": [640,180], "fps": 20, "cycle_seconds": 1,
        "stroke": 8, "corner_radius": 12, "dash_length": 28, "dash_period": 60,
        "paths": [{"points": [[20,85],[20,50],[620,50],[620,85]]},
                  {"points": [[620,95],[620,130],[20,130],[20,95]]}]}
    call("render_flow.py", "--config", config("flow", flow))
    paths = [rounded_path(s["points"], 12) for s in flow["paths"]]
    assert render_frame(flow, paths, 0).tobytes()==render_frame(flow, paths, 1).tobytes()
    a = np.frombuffer(pixel_frame(ffmpeg, root/"flow.mkv", 0, True), dtype="uint8").reshape(180,640,4)
    b = np.frombuffer(pixel_frame(ffmpeg, root/"flow.mkv", .25, True), dtype="uint8").reshape(180,640,4)
    assert a[0,0,3]==0 and a[:,:,3].max()==255
    assert np.array_equal(a[50,150:450,3], b[50,165:465,3]), "Upper dashes did not travel toward the right arrow"
    assert np.array_equal(a[130,150:450,3], b[130,135:435,3]), "Lower dashes did not travel toward the left arrow"

    with FrameWriter(ffmpeg, root/"original.mp4", (320,180), frame_rate(20), {"crf": 10}) as writer:
        for n in range(80):
            im = Image.new("RGB", (320,180), "#e1e9ef")
            d = ImageDraw.Draw(im)
            d.rectangle((0,0,319,22), fill="#23445b")
            d.rectangle((30+n*2,50,65+n*2,140), fill="#d34e52")
            writer.write(im)
    master = {"source": "original.mp4", "output": "master.mkv", "fps": 20,
              "source_end": 4, "cuts": [[0,.25],[1.5,2]], "crop": [0,0,320,180]}
    call("lossless_master.py", "--config", config("master", master))
    assert read_json(root/"master.master.json")["all_decoded_frames_equal"]
    poster = Image.new("RGB", (320,180), "#e8e2d7")
    ImageDraw.Draw(poster).text((100,80), "Demo", fill="black")
    poster.save(root/"poster.png")
    retime = {"output": "retimed.mp4", "canvas": [320,180], "fps": 20, "target_seconds": 6,
        "encoding": {"preset": "fast", "crf": 16},
        "segments": [{"id": "intro", "kind": "copy", "source": "original.mp4", "duration_seconds": 2},
            {"id": "actions", "source": "master.mkv", "source_start": 0, "source_end": 2, "fit": True},
            {"id": "rock", "source": "master.mkv", "source_start": 2, "source_end": 2.5, "duration_seconds": .5},
            {"id": "delivery", "source": "master.mkv", "source_start": 2.5, "source_end": 3.25,
             "duration_seconds": .25, "hold_seconds": .5},
            {"id": "logo", "kind": "still", "source": "poster.png", "duration_seconds": .5}]}
    call("retime_video.py", "--config", config("retime", retime))
    timeline = read_json(root/"retimed.retiming.json")
    assert timeline["total_frames"]==120 and timeline["segments"][1]["motion_frames"]==45
    raw = subprocess.check_output([ffmpeg,"-v","error","-ss","5","-i",str(root/"retimed.mp4"),
        "-t","0.5","-vf","scale=80:45,format=gray","-f","rawvideo","-"])
    hold = np.frombuffer(raw,dtype="uint8").reshape(-1,45,80).astype(float)
    assert len(hold)==10 and np.abs(np.diff(hold,axis=0)).mean(axis=(1,2)).max()<1
    alternate = json.loads(json.dumps(retime))
    alternate["output"] = "short-logo.mp4"
    alternate["segments"][-1]["duration_seconds"] = .25
    call("retime_video.py", "--config", config("short-logo", alternate))
    assert read_json(root/"short-logo.retiming.json")["segments"][1]["motion_frames"]==50
    try:
        budget(dict(retime, target_seconds=2))
        raise AssertionError("Impossible fixed budget accepted")
    except ValueError:
        pass

    Image.new("RGB", (320,180), (220,20,230)).save(images/"raw-screen.png")
    Image.new("RGB", (320,180), (20,210,70)).save(images/"raw-result.png")
    rows = [{"step": 1, "direction": "input", "timestamp": "2030-01-01T00:00:00.4+00:00",
             "images": {"screenshot": "raw-screen.png"}},
            {"step": 1, "direction": "output", "timestamp": "2030-01-01T00:00:00.6+00:00", "content": "Open data",
             "tool": [{"name": "click", "arguments": {"button": "left", "private": "DO_NOT_EXPORT_SENTINEL"}}],
             "response": {"model": "RecordedModel", "reasoning": "DO_NOT_EXPORT_SENTINEL"}},
            {"step": 1, "direction": "execution", "timestamp": "2030-01-01T00:00:00.7+00:00"}]
    (root/"trace.jsonl").write_text("\n".join(json.dumps(r) for r in rows)+"\n")
    trace_cfg = {"trace":"trace.jsonl", "include_tools":True, "tool_argument_fields":["button"],
        "include_screenshots":True, "screenshot_dir":"images", "task_summary":"Load demo",
        "anchor":{"log_timestamp":"2030-01-01T00:00:00+00:00", "source_seconds":0}}
    call("prepare_trace.py", "--config", config("trace", trace_cfg), "--output", root/"rich-events.json")
    assert "DO_NOT_EXPORT_SENTINEL" not in (root/"rich-events.json").read_text()
    events = read_json(root/"rich-events.json")
    events["events"] += [{"time":1,"role":"tool","tool":{"name":"click","arguments":{"private":"DO_NOT_EXPORT_SENTINEL"}}},
        {"time":2,"role":"result","text":"Delivered","image":"images/raw-result.png"}]
    write_json(root/"rich-events.json", events)
    chat = {"events":"rich-events.json","output":"chat.mkv","duration":4,"fps":20,"size":[320,844],
        "rich_cards":True,"tool_argument_fields":["button"],"display_name":"Demo Model", "header_height":80,
        "margin":12,"padding":10,"line_height":20,"image_max_height":140,
        "body_font":{"path":font,"size":14},"title_font":{"path":font,"size":20},"label_font":{"path":font,"size":12}}
    call("render_overlays.py", "chat", "--config", config("chat",chat))
    assert "DO_NOT_EXPORT_SENTINEL" not in (root/"chat.overlay.json").read_text()
    counts=[]
    for t in [.2,1.5]:
        rgb=np.frombuffer(pixel_frame(ffmpeg,root/"chat.mkv",t),dtype="uint8").reshape(844,320,3)
        counts.append(int(((rgb[:,:,0]>180)&(rgb[:,:,1]<50)&(rgb[:,:,2]>180)).sum()))
    assert counts[0]==0 and counts[1]>100, "Screenshot leaked early or was never displayed"

    presentation={"source":"original.mp4","output":"persistent.mp4","canvas":[800,560],"fps":20,
        "main":{"crop":[0,0,320,180],"initial_rect":[24,128,600,338]},
        "secondary":{"source":"chat.mkv","rect":[648,128,128,338]},
        "overlays":[{"source":"flow.mkv","position":[80,-40],"loop":True}],
        "encoding":{"preset":"fast","crf":16}}
    anchored = dict(presentation, events="rich-events.json", transition={
        "start":{"event_step":1,"field":"executed_at"},"duration":.2})
    _, timing = build_filter(anchored, root, [600,338],
        {"width":320,"height":180,"duration":4,"fps":20}, [(8, anchored["overlays"][0])], True, 0)
    assert timing["transition_start"]==.7, "Observation card displaced the execution-feedback anchor"
    call("render_presentation.py","--config",config("persistent",presentation))
    assert validate(ffmpeg,root/"persistent.mp4",4)["frames"]==80
    same=[np.frombuffer(pixel_frame(ffmpeg,root/"persistent.mp4",t,crop="crop=320:12:180:5"),dtype="uint8").astype(float)
          for t in [.25,3.25,3.55]]
    assert np.abs(same[0]-same[1]).mean()<3, "Loop overlay did not keep its phase after the first cycle"
    assert np.abs(same[1]-same[2]).mean()>1, "Loop overlay froze instead of continuing to animate"
    secondary=np.frombuffer(pixel_frame(ffmpeg,root/"persistent.mp4",3.5,crop="crop=100:300:660:140"),dtype="uint8").astype(float)
    assert secondary.std()>20, "Persistent agent panel disappeared"
    lossless = dict(presentation, output="composition.mkv", encoding={"codec":"ffv1"})
    call("render_presentation.py", "--config", config("composition", lossless))
    call("render_presentation.py", "--config", root/"composition.json", "--preview-at", 3.5)
    actual = np.frombuffer(pixel_frame(ffmpeg, root/"composition.mkv", 3.5),dtype="uint8").reshape(560,800,3)
    expected = np.asarray(Image.open(root/"render_assets/preview_0003.50.png").convert("RGB"))
    assert np.abs(actual.astype(int)-expected.astype(int)).max()<=1, "Lossless composition differed from its source-frame preview"
    write_json(root/"animation_smoke_report.json", {"commands":commands,
        "card_identities_preserved_in_decoded_near_and_full_views":True,"both_flight_scopes_tested":True,
        "dash_flow_direction_and_cycle_verified":True,"alpha_preserved":True,"source_master_pixels_verified":True,
        "exact_retiming_and_shorter_logo_budget_verified":True,"completed_frame_hold_verified":True,
        "raw_screenshot_future_leak_test_passed":True,"tool_argument_allowlist_verified":True,
        "persistent_panel_and_loop_overlay_verified":True,"lossless_composition_matches_preview":True,
        "mixed_event_execution_anchor_verified":True})
    print(f"PASS: {root/'animation_smoke_report.json'}")


if __name__=="__main__":
    main()
