#!/usr/bin/env python3
"""Inspect only proxy settings; redact URL credentials and all URL suffixes."""

import argparse
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


PROXY_KEYS = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY",
              "http_proxy", "https_proxy", "all_proxy")
BYPASS_KEYS = ("NO_PROXY", "no_proxy")


def redact_proxy(value):
    if not value:
        return None
    try:
        if "://" not in value:
            return "[set; missing scheme]"
        parsed = urlsplit(value)
        if parsed.scheme not in ("http", "https", "socks5", "socks5h", "socks4"):
            return "[set; unsupported scheme]"
        hostname = parsed.hostname
        if not hostname or not re.fullmatch(r"[A-Za-z0-9._:%-]+", hostname):
            return "[set; unrecognized host]"
        host = f"[{hostname}]" if ":" in hostname else hostname
        port = f":{parsed.port}" if parsed.port is not None else ""
        return f"{parsed.scheme}://{host}{port}"
    except ValueError:
        return "[set; invalid proxy URL]"


def summarize(environment):
    return {"proxies": {key: redact_proxy(environment.get(key)) for key in PROXY_KEYS},
            "bypass_configured": {key: bool(environment.get(key)) for key in BYPASS_KEYS},
            "codex_home_override_present": bool(environment.get("CODEX_HOME"))}


def process_start(pid):
    # Linux comm can contain spaces and parentheses; fields begin after the last ')'.
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return fields[19]


def read_process_environment(pid):
    if sys.platform != "linux":
        raise ValueError("--pid requires Linux/WSL /proc; inspect Windows through its own tools")
    before = process_start(pid)
    allowed = set(PROXY_KEYS + BYPASS_KEYS + ("CODEX_HOME",))
    result = {}
    for item in Path(f"/proc/{pid}/environ").read_bytes().split(b"\0"):
        key, separator, value = item.partition(b"=")
        name = key.decode("utf-8", errors="replace")
        if separator and name in allowed:
            result[name] = value.decode("utf-8", errors="replace")
    if process_start(pid) != before:
        raise RuntimeError("Process identity changed while reading its environment")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pid", type=int, help="Known Linux/WSL backend PID (positive integer)")
    args = parser.parse_args()
    if args.pid is not None and args.pid <= 0:
        parser.error("--pid must be positive")
    try:
        environment = read_process_environment(args.pid) if args.pid else os.environ
        report = summarize(environment)
        report["source"] = f"process:{args.pid}" if args.pid else "current process"
    except (OSError, ValueError, RuntimeError, IndexError) as error:
        # Do not print exceptions containing raw environment values.
        print(json.dumps({"error": type(error).__name__,
                          "detail": "Cannot inspect this process; check platform, PID and permissions"}))
        return 2
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
