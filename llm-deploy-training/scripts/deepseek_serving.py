#!/usr/bin/env python3
"""Launch the DeepSeek TP4 example or render SMG and HAProxy configuration."""

import argparse
import json
import os
from pathlib import Path
import re
import shlex
import sys
from urllib.parse import urlsplit


MODEL = "deepseek-v4.1-flash-1017"
CONTEXT = 524288
PORT = 32100
HEALTH_PORT = 32102
CAP = 4
TIMEOUT = 28800


def model_args(weights):
    return [
        sys.executable, "-m", "sglang.launch_server",
        "--model-path", str(weights), "--served-model-name", MODEL,
        "--trust-remote-code", "--host", "0.0.0.0", "--port", "31000",
        "--tp-size", "4", "--ep-size", "1", "--dp-size", "1",
        "--mem-fraction-static", "0.65", "--chunked-prefill-size", "16384",
        "--context-length", str(CONTEXT), "--max-running-requests", "32",
        "--speculative-algorithm", "DSPARK", "--speculative-dspark-block-size", "5",
        "--moe-runner-backend", "marlin", "--speculative-moe-runner-backend", "marlin",
        "--reasoning-parser", "auto", "--tool-call-parser", "auto",
        "--default-chat-template-kwargs", '{"thinking":true}', "--enable-metrics",
    ]


def origin(text):
    if re.search(r"\s", text):
        raise ValueError("Whitespace in worker origin")
    url = urlsplit(text)
    if (url.scheme != "http" or not re.fullmatch(r"[A-Za-z0-9.-]+", url.hostname or "")
            or not url.port or url.username is not None or url.path not in ("", "/")
            or url.query or url.fragment):
        raise ValueError("Expected a plain HTTP origin with IPv4 or DNS name and explicit port")
    return f"{url.hostname}:{url.port}"


def defaults():
    return [
        "global", "  maxconn 1024",
        "defaults", "  mode http", "  retries 0",
        "  timeout connect 10s", "  timeout client 8h", "  timeout server 8h",
        "  timeout queue 8h", "  timeout http-request 60s", "  timeout check 30s",
    ]


def worker_config(workers):
    lines = defaults()
    for i, worker in enumerate(workers):
        lines += [
            f"frontend worker_{i}", f"  bind 127.0.0.1:{32301 + i}",
            "  acl read_only method GET", f"  use_backend observe_{i} if read_only",
            f"  default_backend inference_{i}",
            f"backend inference_{i}", "  option httpchk GET /health",
            "  http-check expect status 200",
            f"  server engine {worker} check inter 10s fall 3 rise 2 maxconn {CAP}",
            f"backend observe_{i}", f"  server engine {worker} maxconn 32",
        ]
    return "\n".join(lines) + "\n"


def router_args(worker_count, total):
    return [
        sys.executable, "-m", "smg", "launch",
        "--host", "0.0.0.0", "--port", str(PORT), "--worker-urls",
        *[f"http://127.0.0.1:{32301 + i}" for i in range(worker_count)],
        "--backend", "sglang", "--policy", "cache_aware", "--cache-threshold", "0.3",
        "--balance-abs-threshold", "4", "--balance-rel-threshold", "1.5",
        "--balance-prefix-margin-tokens", "1024", "--balance-uncached-credit",
        "--max-tree-size", str(2 ** 27), "--load-monitor-interval", "2", "--engine-metrics",
        "--worker-overload-token-usage", "0.85", "--worker-overload-waiting-requests", "1",
        "--health-check-timeout-secs", "30", "--health-check-interval-secs", "10",
        "--health-failure-threshold", "3", "--health-success-threshold", "2",
        "--disable-retries", "--request-timeout-secs", str(TIMEOUT),
        "--queue-timeout-secs", str(TIMEOUT), "--shutdown-grace-period-secs", str(TIMEOUT),
        "--stream-body-stall-timeout-secs", str(TIMEOUT),
        "--max-concurrent-requests", str(total), "--queue-size", "128",
        "--max-payload-size", str(512 * 1024 * 1024), "--sse-keepalive-secs", "0",
        "--prometheus-host", "0.0.0.0", "--prometheus-port", "32101",
        "--health-check-port", str(HEALTH_PORT), "--admin-host", "127.0.0.1",
        "--admin-port", "32103", "--log-level", "info", "--log-json",
        "--access-log-fields", "worker", "request_bytes",
    ]


def ingress_config(workers, router, total):
    lines = defaults() + [
        "frontend inference", "  bind :32000",
        "  acl catalog_method method GET", "  acl catalog_path path /v1/models",
        "  use_backend catalog if catalog_method catalog_path",
        "  default_backend cache_router",
        "backend cache_router", "  option httpchk GET /readiness",
        "  http-check expect status 200",
        f"  server router {router} check port {HEALTH_PORT} inter 10s fall 3 rise 2 maxconn {total}",
        "backend catalog", "  option httpchk GET /health", "  http-check expect status 200",
    ]
    for i, worker in enumerate(workers):
        role = " backup" if i else ""
        lines.append(f"  server engine_{i} {worker} check inter 10s fall 3 rise 2 maxconn 16{role}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="operation", required=True)
    model = sub.add_parser("model", help="Print the pinned-engine command or start it in the foreground")
    model.add_argument("weights", type=Path)
    model.add_argument("--run", action="store_true")
    for operation in ("router", "ingress"):
        command = sub.add_parser(operation)
        command.add_argument("--worker", action="append", required=True, help="One HTTP engine origin")
        command.add_argument("--total", type=int, required=True, help="Measured global inference cap")
        if operation == "router":
            command.add_argument("--output", type=Path, required=True, help="New configuration directory")
        else:
            command.add_argument("--router", required=True, help="SMG data origin on port 32100")
    args = parser.parse_args()
    if args.operation == "model":
        command = model_args(args.weights)
        if args.run:
            if not (args.weights / "config.json").is_file():
                parser.error("model snapshot must be mounted locally")
            os.execv(sys.executable, command)
        print(shlex.join(command))
        return
    try:
        workers = [origin(item) for item in args.worker]
        if len(workers) != len(set(workers)):
            raise ValueError("Worker origins must be distinct")
        if not 1 <= args.total <= CAP * len(workers):
            raise ValueError(f"Global inference cap must be 1..{CAP * len(workers)}")
        if args.operation == "ingress":
            router = origin(args.router)
            if urlsplit(args.router).port != PORT:
                raise ValueError(f"SMG data port must be {PORT}")
            print(ingress_config(workers, router, args.total), end="")
            return
    except ValueError as exc:
        parser.error(str(exc))
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output / "workers.cfg").write_text(worker_config(workers))
    (args.output / "smg-argv.json").write_text(json.dumps(router_args(len(workers), args.total), indent=2) + "\n")


if __name__ == "__main__":
    main()
