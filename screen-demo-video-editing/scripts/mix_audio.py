#!/usr/bin/env python3
"""Mix music and an optional supplied voiceover; preserve the compressed video."""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path

from media_common import ffmpeg_bin, load_config, check_output, export, probe, video_hash, validate, write_json


def audio_duration(ffmpeg, path):
    result = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)], text=True, capture_output=True)
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", result.stderr)
    if not m:
        raise ValueError(f"Cannot read audio duration: {path}")
    return int(m[1])*3600+int(m[2])*60+float(m[3])


def measure(ffmpeg, path, duration, target, start=0, loop=False):
    cmd = [ffmpeg, "-hide_banner", "-nostdin"]
    if loop:
        cmd += ["-stream_loop", "-1"]
    result = subprocess.run([*cmd, "-ss", str(start), "-i", str(path), "-map", "0:a:0",
                             "-af", f"atrim=duration={duration},asetpts=PTS-STARTPTS,"
                             f"loudnorm=I={target}:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
                            capture_output=True, text=True, check=True)
    match = re.search(r'\{\s*"input_i"[\s\S]*?\}', result.stderr)
    if not match:
        raise ValueError(result.stderr)
    values = json.loads(match[0])
    if not math.isfinite(float(values["input_i"])):
        raise ValueError(f"The selected audio is silent: {path}")
    return values


def normalization(values, target):
    return (f"loudnorm=I={target}:TP=-2:LRA=11:measured_I={values['input_i']}:"
            f"measured_TP={values['input_tp']}:measured_LRA={values['input_lra']}:"
            f"measured_thresh={values['input_thresh']}:offset={values['target_offset']}:linear=true")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--ffmpeg")
    p.add_argument("--overwrite", action="store_true")
    args = p.parse_args()
    cfg, root = load_config(args.config)
    ffmpeg, source = ffmpeg_bin(args.ffmpeg), root/cfg["source_video"]
    info = probe(ffmpeg, source)
    duration, rate = info["duration"], cfg.get("sample_rate", 44100)
    inputs = [source]+[root/cfg[k]["path"] for k in ["music", "voiceover"] if cfg.get(k)]
    output = check_output(root/cfg["output"], inputs, args.overwrite)
    audio_assets = output.parent/(output.stem+".audio-assets")
    audio_assets.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-v", "warning", "-nostdin", "-y", "-i", str(source)]
    filters, mix, measurements = [], [], {}
    next_index = 1
    for kind in ["music", "voiceover"]:
        settings = cfg.get(kind)
        if not settings:
            continue
        path = root/settings["path"]
        start, offset = settings.get("start_seconds", 0), settings.get("offset_seconds", 0)
        if start < 0 or not 0 <= offset < duration:
            raise ValueError("Invalid audio start or timeline offset")
        available = audio_duration(ffmpeg, path)-start
        loop = kind == "music" and settings.get("loop", False)
        if kind == "music" and available < duration and not loop:
            raise ValueError("Music is shorter than the video; explicitly enable looping or choose another excerpt")
        length = duration if loop else min(available, duration-offset)
        target = settings.get("target_lufs", -22 if kind == "music" else -16)
        values = measure(ffmpeg, path, length, target, start, loop)
        measurements[kind] = values
        # Materialize a normalized PCM intermediate before sample-domain delay.
        # Short loudnorm inputs can flush as one huge/NOPTS frame; passing that
        # straight into adelay can lose the intended silence in some builds.
        pcm = audio_assets/f"{kind}.wav"
        prepare = [ffmpeg, "-v", "warning", "-nostdin", "-y"]
        if loop:
            prepare += ["-stream_loop", "-1"]
        prepare += ["-ss", str(start), "-i", str(path), "-map", "0:a:0", "-af",
                    f"atrim=duration={length},asetpts=PTS-STARTPTS,{normalization(values, target)},"
                    f"aresample={rate},asetpts=N/SR/TB", "-ar", str(rate), "-ac", "2", "-c:a", "pcm_f32le"]
        export(prepare, pcm)
        cmd += ["-i", str(pcm)]
        chain = (f"[{next_index}:a:0]atrim=duration={length},asetpts=PTS-STARTPTS,"
                 f"aresample={rate},aformat=channel_layouts=stereo,"
                 f"volume={settings.get('gain_db', 0)}dB")
        if kind == "music":
            fade_in, fade_out = settings.get("fade_in_seconds", 2), settings.get("fade_out_seconds", 4)
            if min(fade_in, fade_out) < 0 or max(fade_in, fade_out) > duration:
                raise ValueError("Fades must fit the video")
            if fade_in:
                chain += f",afade=t=in:st=0:d={fade_in}"
            if fade_out:
                chain += f",afade=t=out:st={duration-fade_out}:d={fade_out}"
        if offset:
            chain += f",adelay={round(offset*1000)}:all=1"
        # These newly authored tracks have an explicit sample-domain delay.
        # Rebase after resampling/adelay so frame PTS jumps cannot become holes
        # in the muxed AAC track (unlike the original-time EDL case).
        chain += f",apad,atrim=duration={duration},asetpts=N/SR/TB[{kind}]"
        filters.append(chain)
        next_index += 1
    if cfg.get("voiceover") and cfg.get("music") and cfg.get("duck_music", True):
        filters += ["[voiceover]asplit=2[voice_mix][voice_key]",
                    "[music][voice_key]sidechaincompress=threshold=0.03:ratio=8:attack=30:release=350[music_ducked]"]
        mix += ["[voice_mix]", "[music_ducked]"]
    else:
        mix += [f"[{kind}]" for kind in ["music", "voiceover"] if cfg.get(kind)]
    if info["has_audio"] and cfg.get("preserve_original_audio", True):
        filters.append(f"[0:a:0]aresample={rate}:async=1:first_pts=0,aformat=channel_layouts=stereo,"
                       f"volume={cfg.get('source_gain_db', 0)}dB,apad,atrim=duration={duration}[original]")
        mix.append("[original]")
    if not mix:
        raise ValueError("Supply music or voiceover")
    filters.append("".join(mix)+f"amix=inputs={len(mix)}:duration=longest:normalize=0,"
                   "alimiter=limit=0.95:level=0:latency=1,asetpts=N/SR/TB[a]")
    cmd += ["-filter_complex", ";".join(filters), "-map", "0:v:0", "-map", "[a]",
            "-c:v", "copy", "-c:a", "aac", "-b:a", cfg.get("audio_bitrate", "256k"),
            "-ar", str(rate), "-ac", "2", "-t", str(duration), "-map_metadata", "0", "-movflags", "+faststart"]
    export(cmd, output)
    source_hash, actual_hash = video_hash(ffmpeg, source), video_hash(ffmpeg, output)
    if source_hash != actual_hash:
        raise ValueError("The compressed video changed during audio-only finishing")
    validation = validate(ffmpeg, output, duration, cfg.get("burned_only", False))
    final = measure(ffmpeg, output, duration, -22)
    if float(final["input_tp"]) >= 0:
        raise ValueError("Final audio clips")
    write_json(output.with_suffix(".audio.json"), {"validation": validation, "video_payload_unchanged": True,
               "video_sha256": actual_hash, "input_measurements": measurements, "final_measurement": final,
               "configuration": cfg, "synthesized_voice": False})
    print(output)


if __name__ == "__main__":
    main()
