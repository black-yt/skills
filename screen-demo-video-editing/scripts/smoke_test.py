#!/usr/bin/env python3
"""Exercise the toolkit with generated GUI pixels and tones, never private recordings."""
import argparse
import hashlib
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from media_common import ffmpeg_bin, read_json, write_json, edited_time, validate


SCRIPTS = Path(__file__).resolve().parent
ASSETS = SCRIPTS.parent/"assets"


def make_video(ffmpeg, path, width, height, seconds, fps, draw):
    with path.with_suffix(".encode.log").open("w") as log:
        process = subprocess.Popen([ffmpeg, "-v", "warning", "-nostdin", "-y", "-f", "rawvideo",
                                    "-pix_fmt", "rgb24", "-s", f"{width}x{height}", "-r", str(fps),
                                    "-i", "pipe:0", "-f", "lavfi", "-i",
                                    f"sine=frequency=220:sample_rate=44100:duration={seconds}",
                                    "-c:v", "libx264", "-preset", "fast", "-crf", "12",
                                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-t", str(seconds), str(path)],
                                   stdin=subprocess.PIPE, stdout=log, stderr=log)
        try:
            for frame in range(round(seconds*fps)):
                process.stdin.write(draw(frame/fps).convert("RGB").tobytes())
            process.stdin.close()
            if process.wait() != 0:
                raise RuntimeError(path.with_suffix(".encode.log").read_text())
        except BaseException:
            process.kill()
            process.wait()
            raise


def gui_frame(t):
    image = Image.new("RGB", (640, 300), "#243044")
    d = ImageDraw.Draw(image)
    d.rectangle([0, 0, 479, 299], fill="#d8eef2")
    d.rectangle([0, 0, 479, 27], fill="#16436a")
    d.rectangle([18, 42, 135, 270], fill="#ffffff")
    d.rectangle([160, 55, 455, 276], fill="#80b9d6")
    d.rectangle([30, 80, 115, 100], fill="#24658b")
    if t >= 8:
        d.rectangle([30, 80, 115, 100], fill="#9c4e32")
    if t >= 9:
        x = 300+int(25*math.sin(t*2))
        d.ellipse([x-45, 115, x+45, 240], fill="#345647")
    movement = min(1, max(0, t-1))
    x, y = 80+round(movement*200), 60+round(movement*60)
    d.ellipse([x-3, y-3, x+3, y+3], fill="#000000")
    return image


def cycle_frame(t):
    image = Image.new("RGB", (128, 72), "#777777")
    d = ImageDraw.Draw(image)
    d.rectangle([45, 10, 109, 59], fill="#dddddd" if int(t*2) % 2 == 0 else "#222222")
    d.rectangle([3, 30, 7, 41], fill="#ffffff" if int(t) % 2 else "#000000")
    d.rectangle([15, 10, 25, 20], fill="#dddddd" if t >= 8 else "#222222")
    return image


def tone(path, duration, frequency, amplitude):
    sample_rate = 44100
    t = np.arange(round(duration*sample_rate))/sample_rate
    signal = amplitude*np.sin(2*np.pi*frequency*t)
    signal *= np.minimum(1, np.minimum(t/.03, (duration-t)/.03))
    stereo = np.repeat((signal*32767).astype("<i2")[:, None], 2, axis=1)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(stereo.tobytes())


def pixels(ffmpeg, path, at=None, vf=None):
    cmd = [ffmpeg, "-v", "error"]
    if at is not None:
        cmd += ["-ss", str(at)]
    cmd += ["-i", str(path), "-frames:v", "1"]
    if vf:
        cmd += ["-vf", vf]
    return np.frombuffer(subprocess.check_output([*cmd, "-pix_fmt", "rgb24", "-f", "rawvideo", "-"]),
                         dtype=np.uint8).astype(np.int16)


def spectrum_amplitude(ffmpeg, path, at, frequency):
    raw = subprocess.check_output([ffmpeg, "-v", "error", "-ss", str(at), "-i", str(path),
                                   "-map", "0:a:0", "-t", "0.4", "-ar", "44100", "-ac", "1",
                                   "-f", "f32le", "-"])
    audio = np.frombuffer(raw, dtype="<f4")
    if not len(audio):
        raise AssertionError(f"No audio samples at {at}s; inspect stream timestamps: {path}")
    phase = np.exp(-2j*np.pi*frequency*np.arange(len(audio))/44100)
    return float(abs(np.dot(audio, phase))/len(audio))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work-dir", required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--font")
    args = p.parse_args()
    root = Path(args.work_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    if any(root.iterdir()):
        raise ValueError("Use an empty test directory; existing artifacts are not deleted")
    ffmpeg = ffmpeg_bin(args.ffmpeg)
    candidates = [args.font] if args.font else []
    candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                   "/mnt/c/Windows/Fonts/NotoSansSC-VF.ttf", "C:/Windows/Fonts/segoeui.ttf",
                   "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"]
    font = next((str(Path(f).resolve()) for f in candidates if f and Path(f).is_file()), None)
    if not font:
        raise ValueError("Pass --font /path/to/a/font.ttf")
    commands = []
    def call(name, *arguments, use_ffmpeg=True, success=True):
        cmd = [sys.executable, str(SCRIPTS/name), *map(str, arguments)]
        if use_ffmpeg:
            cmd += ["--ffmpeg", ffmpeg]
        result = subprocess.run(cmd, capture_output=True, text=True)
        commands.append({"tool": name, "returncode": result.returncode})
        if (result.returncode == 0) != success:
            raise RuntimeError(f"{cmd}\n{result.stdout}\n{result.stderr}")
        return result
    def config(name):
        return read_json(ASSETS/f"{name}.example.json")
    def save(name, value):
        path = root/f"{name}.json"
        write_json(path, value)
        return path
    print(f"Synthetic GUI and timeline: {root}", flush=True)
    make_video(ffmpeg, root/"source.mp4", 640, 300, 12, 20, gui_frame)
    edit = config("edit-plan")
    save("edit-plan", edit)
    call("edit_timeline.py", "render", "--plan", root/"edit-plan.json")
    edited = validate(ffmpeg, root/"edited.mp4", 8)
    if edited["frames"] != 160:
        raise AssertionError(edited)
    call("edit_timeline.py", "detect-static", root/"source.mp4", "--output", root/"freezes.json", "--minimum", ".5")
    detected = read_json(root/"freezes.json")
    if not detected["freezes"]:
        raise AssertionError("No stationary GUI interval detected")
    call("edit_timeline.py", "build-plan", "--freezes", root/"freezes.json", "--output", root/"opening.json",
         "--video-output", "opening.mp4", "--first-motion", "1.05", "--still-before-motion", ".5",
         "--protect-after-motion", ".95", use_ffmpeg=False)
    opening = read_json(root/"opening.json")
    if abs(edited_time(1.05, opening["cuts"])-.5) > .001:
        raise AssertionError(opening)
    call("edit_timeline.py", "render", "--plan", root/"opening.json")
    before = pixels(ffmpeg, root/"opening.mp4", 0, "crop=40:40:65:45")
    still = pixels(ffmpeg, root/"opening.mp4", .45, "crop=40:40:65:45")
    moved = pixels(ffmpeg, root/"opening.mp4", .55, "crop=40:40:65:45")
    if np.abs(before-still).mean() > 2 or np.abs(before-moved).mean() < 1:
        raise AssertionError("The real first movement was not preserved after the still interval")
    call("split_video.py", root/"source.mp4", "--split-x", "480", "--output-dir", root/"parts",
         "--method", "h264-metadata")
    call("split_video.py", root/"source.mp4", "--split-x", "480", "--output-dir", root/"encoded-parts")
    subprocess.run([ffmpeg, "-v", "error", "-i", str(root/"source.mp4"), "-map", "0:v:0",
                    "-c:v", "copy", "-an", str(root/"silent.mp4")], check=True)
    silent = dict(edit, source="silent.mp4", output="silent-edited.mp4")
    save("silent-plan", silent)
    call("edit_timeline.py", "render", "--plan", root/"silent-plan.json")
    if validate(ffmpeg, root/"silent-edited.mp4", 8)["has_audio"]:
        raise AssertionError("Silent input unexpectedly gained an audio track")
    print("Periodic signal and cursor-mask discrimination", flush=True)
    make_video(ffmpeg, root/"cycles.mp4", 128, 72, 12, 8, cycle_frame)
    cycle_cfg = {"source_start": 0, "source_duration": 12, "fps": 8, "width": 128, "height": 72,
                 "signal_roi": [45, 10, 110, 60], "static_regions": [[0, 0, 32, 72]],
                 "cursor_ignore_regions": [[3, 30, 8, 42]], "minimum_period_seconds": .7}
    save("cycles", cycle_cfg)
    call("analyze_cycles.py", "--source", root/"cycles.mp4", "--regions", root/"cycles.json",
         "--output", root/"cycle_report.json")
    cycles = read_json(root/"cycle_report.json")
    if cycles["removed_cycles"] <= 0 or not any(c["changed_pixels_before_cursor_mask"] > 0 and
             c["changed_pixels_after_cursor_mask"] == 0 for c in cycles["comparisons"]):
        raise AssertionError(cycles)
    if not any(c["changed_pixels_after_cursor_mask"] >= 10 for c in cycles["comparisons"]):
        raise AssertionError("A true parameter update was masked")
    if any(r["source_start"] < 8 < r["source_end"] for r in cycles["runs"]):
        raise AssertionError("A proposed cut crosses the parameter update")
    print("Continuous chat, transparent captions, and animated geometry", flush=True)
    events = config("events")
    for event in events["events"]:
        event["text"] = f"Public output {event['step']}"
    events["task_summary"] = "Load the sample and show the result."
    save("events", events)
    # Exercise the JSONL adapter independently of already-normalized events.
    rows = [{"step": 1, "timestamp": "2030-01-01T12:00:01+00:00", "direction": "output",
             "content": "Visible text", "reasoning_content": "not exported", "tool": [
                 {"name": "move", "arguments": {"point_id": "G-02-03"}}]},
            {"step": 1, "timestamp": "2030-01-01T12:00:01.4+00:00", "direction": "execution"},
            {"step": 2, "timestamp": "2030-01-01T12:00:02+00:00", "direction": "output",
             "content": "Second visible text", "tool": [
                 {"name": "move", "arguments": '{"point_id":"L-10.5-10.25"}'}]},
            {"step": 3, "timestamp": "2030-01-01T12:00:02.5+00:00", "direction": "output",
             "content": None, "tool": None, "response": None}]
    (root/"trace.jsonl").write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    save("trace", config("trace"))
    call("prepare_trace.py", "--config", root/"trace.json", "--output", root/"normalized.json", use_ffmpeg=False)
    normalized = read_json(root/"normalized.json")
    if (normalized["moves"][0]["x"] != 40 or normalized["moves"][1]["x"] != 42 or
            normalized["moves"][1]["y"] != 61 or "not exported" in json.dumps(normalized)):
        raise AssertionError(normalized)
    chat = config("chat")
    chat.update(size=[148, 278], header_height=48, margin=8, padding=7, line_height=14, tagline="GUI demo")
    for key, size in [("body_font", 10), ("title_font", 12), ("label_font", 8)]:
        chat[key].update(path=font, size=size)
    save("chat", chat)
    call("render_overlays.py", "chat", "--config", root/"chat.json")
    expected = pixels(ffmpeg, root/"overlay_frames/chat/chat_0004.png")
    actual = pixels(ffmpeg, root/"chat.mkv", 5.5)
    if not np.array_equal(actual, expected):
        raise AssertionError("The independent chat froze at the second message")
    captions = config("captions")
    captions.update(size=[640, 60], header_height=24, stage_position=[16, 4], horizontal_margin=15)
    captions["body_font"].update(path=font, size=14)
    captions["title_font"].update(path=font, size=12)
    for i, cue in enumerate(captions["cues"]):
        cue.update(title=f"0{i+1} / Stage", text=f"Explain the scientific workflow, phase {i+1}.")
    save("captions", captions)
    call("render_overlays.py", "captions", "--config", root/"captions.json")
    presentation = config("presentation")
    presentation.update(canvas=[640, 480], corner_radius=8)
    presentation["main"].update(initial_rect=[16, 96, 444, 278], final_rect=[16, 40, 608, 380])
    presentation["secondary"]["rect"] = [476, 96, 148, 278]
    presentation["transition"]["secondary_exit_x"] = 720
    presentation["overlays"] = [
        {"source": "captions.mkv", "crop": [0, 0, 640, 24], "position": [0, 0]},
        {"source": "captions.mkv", "crop": [0, 24, 640, 36], "position": [0, 432]}]
    save("presentation", presentation)
    for at in [.5, 3.5, 6.5]:
        call("render_presentation.py", "--config", root/"presentation.json", "--preview-at", at)
    call("render_presentation.py", "--config", root/"presentation.json")
    visual = {}
    for at in [.5, 3.5, 6.5]:
        reference = pixels(ffmpeg, root/f"render_assets/preview_{at:07.2f}.png")
        actual = pixels(ffmpeg, root/"presentation.mp4", at)
        error = float(np.abs(reference-actual).mean())
        if error >= 4:
            raise AssertionError(f"Encoded geometry differs from its preview at {at}: {error}")
        visual[str(at)] = error
    single = dict(presentation, assets_dir="single_assets")
    single.pop("secondary")
    single.pop("events")
    single["transition"] = dict(presentation["transition"], start=2.4)
    single["overlays"] = []
    single["camera"] = dict(presentation["camera"], moves=events["moves"])
    single["camera"].pop("moves_file")
    save("single-main", single)
    call("render_presentation.py", "--config", root/"single-main.json", "--preview-at", "3.5")
    sidecar = root/"presentation.zh.srt"
    sidecar.write_text("1\n00:00:00,000 --> 00:00:01,000\nDuplicate\n")
    call("validate_export.py", root/"presentation.mp4", "--burned-only", success=False)
    sidecar.unlink()
    print("Music, supplied-voice alignment, and real sidechain attenuation", flush=True)
    tone(root/"music.wav", 10, 440, .08)
    tone(root/"voiceover.wav", 1.4, 1000, .25)
    audio = config("audio")
    audio.update(preserve_original_audio=False)
    audio["voiceover"]["offset_seconds"] = 3
    save("audio", audio)
    call("mix_audio.py", "--config", root/"audio.json")
    audio.update(output="control.mp4", duck_music=False)
    save("audio-control", audio)
    call("mix_audio.py", "--config", root/"audio-control.json")
    ducked = spectrum_amplitude(ffmpeg, root/"final.mp4", 3.5, 440)
    control = spectrum_amplitude(ffmpeg, root/"control.mp4", 3.5, 440)
    if not ducked < control*.75:
        raise AssertionError(f"Background music was not attenuated: {ducked} vs {control}")
    voice_before = spectrum_amplitude(ffmpeg, root/"final.mp4", 1.5, 1000)
    voice_during = spectrum_amplitude(ffmpeg, root/"final.mp4", 3.5, 1000)
    if not voice_during > voice_before*10:
        raise AssertionError("The supplied voice was not aligned to its requested offset")
    music_only = dict(audio, output="music-only.mp4", preserve_original_audio=True, source_gain_db=-24)
    music_only.pop("voiceover")
    save("music-only", music_only)
    call("mix_audio.py", "--config", root/"music-only.json")
    if spectrum_amplitude(ffmpeg, root/"music-only.mp4", 2, 440) < .001:
        raise AssertionError("The music-only export is silent")
    report = {"commands": commands, "edited_frames": edited["frames"], "real_opening_preserved": True,
              "metadata_crop_pixel_exact": True, "cycles_removed": cycles["removed_cycles"],
              "parameter_update_protected": True, "chat_continues_after_exit": True,
              "encoded_preview_mae": visual, "duplicate_sidecar_rejected": True,
              "ducked_music_amplitude_ratio": ducked/control, "voice_offset_verified": True,
              "final_validation": validate(ffmpeg, root/"final.mp4", 8, True)}
    write_json(root/"smoke_report.json", report)
    print(f"PASS: {root/'smoke_report.json'}", flush=True)


if __name__ == "__main__":
    main()
