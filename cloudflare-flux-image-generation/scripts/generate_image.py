#!/usr/bin/env python3
"""Generate one JPEG with Cloudflare Workers AI FLUX.1 schnell (stdlib only).

Environment: CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN.
Run `python3 generate_image.py --help` for CLI usage.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import json
import os
import re
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MODEL = "@cf/black-forest-labs/flux-1-schnell"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
MAX_RESPONSE_BYTES = 20 * 1024 * 1024


def _api_error(raw: bytes, token: str) -> str:
    """Return a short API error without printing the credential."""
    try:
        body = json.loads(raw.decode("utf-8"))
        errors = body.get("errors") or []
        if errors:
            first = errors[0]
            if isinstance(first, dict):
                message = f"{first.get('code', '')} {first.get('message', '')}"
            else:
                message = str(first)
        else:
            message = "API returned no error details"
    except (UnicodeDecodeError, json.JSONDecodeError, AttributeError, TypeError):
        message = "API returned an unreadable error"
    return message.replace(token, "[REDACTED]")[:200]


def generate(
    prompt: str,
    output: str | Path | None = None,
    steps: int = 4,
    overwrite: bool = False,
    timeout: int = 120,
) -> dict[str, str | float]:
    """Generate and save one JPEG; return path and elapsed seconds.

    Raises ValueError for invalid input and RuntimeError for API or output errors.
    """
    if not isinstance(prompt, str) or not 1 <= len(prompt) <= 2048 or not prompt.strip():
        raise ValueError("prompt must contain 1–2048 characters")
    if type(steps) is not int or not 1 <= steps <= 8:
        raise ValueError("steps must be an integer from 1 to 8")
    if type(timeout) is not int or timeout <= 0:
        raise ValueError("timeout must be a positive integer")

    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not account or not token:
        raise RuntimeError("set CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN")
    if not re.fullmatch(r"[0-9a-fA-F]{32}", account):
        raise ValueError("CLOUDFLARE_ACCOUNT_ID must be a 32-digit hexadecimal ID")

    destination = Path(output) if output is not None else Path(
        "generated_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".jpg"
    )
    if destination.suffix.lower() not in {".jpg", ".jpeg"}:
        raise ValueError("output filename must end in .jpg or .jpeg")
    if destination.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {destination}")

    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/{MODEL}"
    body = json.dumps({"prompt": prompt, "steps": steps}).encode("utf-8")
    started = time.monotonic()
    response_data = None

    for attempt in range(3):
        request = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise RuntimeError("API response exceeded 20 MiB limit")
            response_data = json.loads(raw.decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            detail = _api_error(exc.read(4096), token)
            if exc.code in RETRYABLE_STATUS and attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"Cloudflare HTTP {exc.code}: {detail}") from None
        except urllib.error.URLError as exc:
            if attempt < 2:
                time.sleep(2 ** attempt)
                continue
            raise RuntimeError(f"network request failed: {type(exc.reason).__name__}") from None
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise RuntimeError("Cloudflare returned invalid JSON") from None

    if not isinstance(response_data, dict) or response_data.get("success") is not True:
        detail = _api_error(json.dumps(response_data).encode("utf-8"), token)
        raise RuntimeError(f"Cloudflare API error: {detail}")
    result = response_data.get("result")
    image_text = result.get("image") if isinstance(result, dict) else None
    if not isinstance(image_text, str):
        raise RuntimeError("Cloudflare response has no result.image")
    try:
        image_bytes = base64.b64decode(image_text, validate=True)
    except (ValueError, binascii.Error):
        raise RuntimeError("Cloudflare returned invalid base64 image data") from None
    if not (image_bytes.startswith(b"\xff\xd8\xff") and image_bytes.endswith(b"\xff\xd9")):
        raise RuntimeError("Cloudflare response is not a complete JPEG")

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", prefix=".cloudflare-flux-", suffix=".tmp",
            dir=destination.parent, delete=False,
        ) as handle:
            temp_path = Path(handle.name)
            handle.write(image_bytes)
        if destination.exists() and not overwrite:
            raise FileExistsError(f"output already exists: {destination}")
        os.replace(temp_path, destination)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    return {
        "path": str(destination.resolve()),
        "duration_seconds": round(time.monotonic() - started, 2),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="text description (1–2048 characters)")
    parser.add_argument("--output", "-o", help="JPEG output path")
    parser.add_argument("--steps", type=int, default=4, help="diffusion steps, 1–8 (default: 4)")
    parser.add_argument("--timeout", type=int, default=120, help="request timeout in seconds")
    parser.add_argument("--overwrite", action="store_true", help="replace an existing output file")
    args = parser.parse_args(argv)
    try:
        result = generate(args.prompt, args.output, args.steps, args.overwrite, args.timeout)
    except (ValueError, RuntimeError, FileExistsError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(result["path"])
    print(f"duration_seconds={result['duration_seconds']}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
