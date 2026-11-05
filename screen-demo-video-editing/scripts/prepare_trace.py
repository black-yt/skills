#!/usr/bin/env python3
"""Normalize public message text and calibrated pointer events onto an edited timeline."""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
from pathlib import Path

from media_common import load_config, read_json, write_json, merge_cuts, edited_time


def point_id(value):
    m = re.fullmatch(r"([GL])-([0-9.]+)-([0-9.]+)", value)
    if not m:
        raise ValueError(f"Unrecognized grid ID: {value}")
    return m[1], float(m[2]), float(m[3])


def iso(value):
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    cfg, root = load_config(args.config)
    source = root/cfg["trace"]
    rows = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
    anchor = cfg["anchor"]
    clock = iso(anchor["log_timestamp"])
    cuts = cfg.get("cuts", [])
    if cfg.get("edit_plan"):
        plan, _ = load_config(root/cfg["edit_plan"])
        cuts = merge_cuts(plan["cuts"], plan.get("source_end", plan.get("source_trim_end")))
    def mapped(value):
        seconds = anchor["source_seconds"]+(iso(value)-clock).total_seconds()
        return edited_time(seconds, cuts)
    executions = {row["step"]: row for row in rows if row.get("direction") == "execution"}
    grid = cfg.get("grid")
    mouse = list(grid["initial_cursor"]) if grid else None
    events, moves, unmapped = [], [], 0
    for row in rows:
        if cfg.get("include_screenshots") and row.get("direction")=="input":
            filename = (row.get("images") or {}).get("screenshot")
            if filename:
                path = (root/cfg.get("screenshot_dir", ".")/filename).resolve()
                if not path.is_file():
                    raise FileNotFoundError(f"Raw screenshot is missing: {path}")
                events.append({"time": mapped(row["timestamp"]), "step": row.get("step"),
                               "role": "observation", "text": cfg.get("observation_label", "Screen observation"),
                               "image": os.path.relpath(path, root),
                               "image_sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
        output = (row.get("direction") == "output" or
                  (not row.get("direction") and row.get("role") == "assistant"))
        if not output:
            continue
        time = mapped(row["timestamp"])
        event = {"time": time, "step": row.get("step"), "role": "model",
                 "text": (row.get("content") or "").strip()}
        if row.get("step") in executions:
            event["executed_at"] = mapped(executions[row["step"]]["timestamp"])
        model = (row.get("response") or {}).get("model")
        if model:
            event["recorded_model"] = model
        events.append(event)
        for tool in row.get("tool") or []:
            if cfg.get("include_tools"):
                arguments = tool.get("arguments") or {}
                if isinstance(arguments, str):
                    arguments = json.loads(arguments)
                allowed = cfg.get("tool_argument_fields", [])
                events.append({"time": time, "step": row.get("step"), "role": "tool", "text": "",
                               "tool": {"name": tool.get("name", "tool"),
                                        "arguments": {k:arguments[k] for k in allowed if k in arguments}}})
            if tool.get("name") not in {"move", "mouse_move", "move_mouse"}:
                continue
            fields = tool.get("arguments", {})
            if isinstance(fields, str):
                fields = json.loads(fields)
            target = None
            if "x" in fields and "y" in fields:
                target = [float(fields["x"]), float(fields["y"])]
            elif fields.get("point_id") and grid:
                view, column, line = point_id(fields["point_id"])
                if view == "G":
                    spacing = grid["global_spacing"]
                    target = [column*spacing[0], line*spacing[1]]
                else:
                    label = row.get("cursor_grid_id")
                    origin = point_id(label)[1:] if label else grid["local_cursor_label"]
                    spacing = grid["local_spacing"]
                    target = [mouse[0]+(column-origin[0])*spacing[0], mouse[1]+(line-origin[1])*spacing[1]]
            if target is None:
                unmapped += 1
                continue
            mouse = target
            moves.append({"time": time, "x": target[0], "y": target[1]})
    events.sort(key=lambda e:e["time"])
    write_json(args.output, {"task_summary": cfg.get("task_summary", ""), "events": events,
                             "moves": moves, "unmapped_pointer_calls": unmapped,
                             "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()})
    print(f"{len(events)} public messages, {len(moves)} pointer events; {unmapped} require calibration")


if __name__ == "__main__":
    main()
