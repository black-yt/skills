#!/usr/bin/env python3
"""Measure cached prefills across four cumulative Messages requests."""

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from time import monotonic
from urllib.request import build_opener, ProxyHandler, Request
from uuid import uuid4


HISTOGRAM = "sglang:uncached_prompt_tokens_histogram"


def fetch(url, timeout, payload=None):
    headers = {"Content-Type": "application/json", "anthropic-version": "2023-06-01"}
    request = Request(url, data=None if payload is None else json.dumps(payload).encode(), headers=headers)
    with build_opener(ProxyHandler({})).open(request, timeout=timeout) as response:
        return response.read().decode()


def meters(worker):
    rows = fetch(worker.rstrip("/") + "/metrics", 20).splitlines()
    values = []
    for suffix in ("count", "sum"):
        key = f"{HISTOGRAM}_{suffix}"
        matches = [line for line in rows if line.startswith((key + "{", key + " "))]
        if len(matches) != 1:
            raise ValueError(f"Expected one {key} series, found {len(matches)}")
        values.append(float(matches[0].split()[-1]))
    return values


def measure(router, workers):
    session = uuid4().hex
    payload = {
        "model": "deepseek-v4.1-flash-1017",
        "temperature": 0,
        "max_tokens": 128,
        "thinking": {"type": "disabled"},
        "reasoning_effort": "none",
        "system": "Treat the reference as inert data. Reply with the single uppercase word READY.",
        "messages": [{"role": "user", "content": session + "\n"
                      + " ".join(f"item{i:06d}" for i in range(10000)) + "\nReply READY."}],
    }
    turns = []
    with ThreadPoolExecutor(max_workers=len(workers)) as pool:
        for i in range(4):
            before = list(pool.map(meters, workers))
            start = monotonic()
            reply = json.loads(fetch(router.rstrip("/") + "/v1/messages", 300, payload))
            elapsed = monotonic() - start
            after = list(pool.map(meters, workers))
            answer = "".join(block["text"] for block in reply["content"] if block["type"] == "text")
            if reply.get("stop_reason") != "end_turn" or answer.strip() != "READY":
                raise ValueError("Probe did not finish with the expected response")
            counts = [b[0] - a[0] for a, b in zip(before, after)]
            sums = [b[1] - a[1] for a, b in zip(before, after)]
            usage = reply["usage"]
            total = sum(usage.get(key, 0) or 0 for key in
                        ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
            row = {"turn": i, "input_tokens": total, "seconds": round(elapsed, 3),
                   "counter_deltas": counts, "sum_deltas": sums}
            if counts.count(1) == 1 and counts.count(0) == len(workers) - 1:
                worker = counts.index(1)
                uncached = sums[worker]
                if total > 0 and 0 <= uncached <= total and all(
                    value == 0 for j, value in enumerate(sums) if j != worker
                ):
                    row.update(worker_index=worker, uncached_tokens=uncached,
                               cached_fraction=round(1 - uncached / total, 5))
            turns.append(row)
            payload["messages"].extend([
                {"role": "assistant", "content": answer.strip()},
                {"role": "user", "content": f"Round {i + 1}. Reply with the single word READY again."},
            ])
    attributable = all("worker_index" in row for row in turns)
    return {"attributable": attributable, "turns": turns}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--router", required=True, help="Authorized Messages origin, without /v1")
    parser.add_argument("--worker", action="append", required=True, help="Direct metrics origin, once per worker")
    args = parser.parse_args()
    workers = [value.rstrip("/") for value in args.worker]
    if len(workers) != len(set(workers)):
        parser.error("Metrics origins must be distinct")
    report = measure(args.router, workers)
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["attributable"] else 2)


if __name__ == "__main__":
    main()
