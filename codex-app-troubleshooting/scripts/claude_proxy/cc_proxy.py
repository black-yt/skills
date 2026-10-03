#!/usr/bin/env python3
"""Manage this user's shared loopback relay; never signal an unverified process."""

import argparse
import fcntl
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import time


def process_identity(pid, script):
    if pid <= 1:
        return None
    try:
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        arguments = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
        if fields[0] == "Z" or len(arguments) < 2 or arguments[1] != os.fsencode(script):
            return None
        return {"pid": pid, "starttime": fields[19],
                "boot_id": Path('/proc/sys/kernel/random/boot_id').read_text().strip()}
    except (FileNotFoundError, ProcessLookupError):
        return None


def read_record(path):
    if path.is_symlink():
        raise ValueError("Refusing symlink pidfile")
    if not path.exists():
        return None
    record = json.loads(path.read_text())
    if not isinstance(record, dict) or not isinstance(record.get("pid"), int):
        raise ValueError("Unrecognized pidfile; inspect manually")
    return record


def matches(record, script):
    if record is None:
        return False
    actual = process_identity(record["pid"], script)
    return actual is not None and all(record.get(key) == value for key, value in actual.items())


def relay_configuration():
    result = {}
    for name in ("UPSTREAM_HOST", "UPSTREAM_PORT", "TARGET_HOST", "TARGET_PORT", "LISTEN_PORT"):
        result["CHAIN_" + name] = os.environ["CC_" + name]
    return result


def ready(port):
    try:
        with socket.create_connection(("127.0.0.1", int(port)), timeout=0.2):
            return True
    except OSError:
        return False


def operate(action, directory):
    script = directory / "cc_proxy_chain.py"
    pidfile = directory / "cc_proxy_chain.pid"
    record = read_record(pidfile)
    live = matches(record, script)
    if record and not live and Path(f'/proc/{record["pid"]}').exists():
        raise RuntimeError("PID belongs to another process or cannot be verified; no signal sent")
    if action == "status":
        print("Relay running (identity verified)." if live else "Relay stopped.")
        return 0 if live else 1
    if action == "stop":
        if live:
            os.kill(record["pid"], signal.SIGTERM)
            deadline = time.monotonic() + 5
            while time.monotonic() < deadline and matches(record, script):
                time.sleep(0.1)
            if matches(record, script):
                os.kill(record["pid"], signal.SIGKILL)
        pidfile.unlink(missing_ok=True)
        print("Relay stopped; other terminals using it lose this proxy route.")
        return 0
    if live:
        if record.get("configuration") != relay_configuration():
            raise RuntimeError("A relay with different settings is active; do not silently reuse it")
        print("Existing relay reused.")
        return 0
    if not script.is_file() or script.is_symlink():
        raise ValueError("Missing real relay script")
    config = relay_configuration()
    environment = {**os.environ, **config}
    log_path = directory / "cc_proxy_chain.log"
    if log_path.is_symlink():
        raise ValueError("Refusing symlink log")
    temporary = pidfile.with_suffix(".new")
    if temporary.exists() or temporary.is_symlink():
        raise RuntimeError("Pending pidfile exists; inspect previous start")
    with log_path.open("ab") as log:
        child = subprocess.Popen([sys.executable, str(script)], stdin=subprocess.DEVNULL,
                                 stdout=log, stderr=log, env=environment, start_new_session=True)
    committed = False
    try:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and child.poll() is None:
            created = process_identity(child.pid, script)
            if created and ready(config["CHAIN_LISTEN_PORT"]):
                time.sleep(0.1)
                if child.poll() is None:
                    record = {**created, "configuration": config}
                    with temporary.open("x") as stream:
                        stream.write(json.dumps(record))
                    temporary.replace(pidfile)
                    committed = True
                    print("Relay started on loopback; verify target HTTP response separately.")
                    return 0
            time.sleep(0.1)
        raise RuntimeError("Relay failed to start; check private log and port ownership, do not kill other listeners")
    finally:
        # A failed metadata write must not leave an untracked shared daemon.
        if not committed and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("start", "stop", "status"))
    args = parser.parse_args()
    if sys.platform != "linux":
        raise ValueError("This manager requires Linux/WSL /proc")
    directory = Path(os.environ.get("CC_DIR", str(Path.home() / '.cc'))).absolute()
    if directory.is_symlink():
        raise ValueError("Refusing symlink directory")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.stat().st_uid != os.getuid():
        raise ValueError("Proxy directory is owned by another user")
    lock_path = directory / "cc_proxy.lock"
    if lock_path.is_symlink():
        raise ValueError("Refusing symlink lock")
    os.umask(0o077)
    with lock_path.open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return operate(args.action, directory)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print(f"Relay manager: {error}", file=sys.stderr)
        sys.exit(2)
