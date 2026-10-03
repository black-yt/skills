#!/usr/bin/env python3
"""Temporary curl shim: authenticate one GitHub API URL without putting tokens in argv."""

import os
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import urlsplit


def main():
    args = sys.argv[1:]
    real = Path(os.environ.get("CODEX_REAL_CURL", "/usr/bin/curl"))
    if not real.is_absolute() or not real.is_file() or real.resolve() == Path(__file__).resolve():
        raise ValueError("Set CODEX_REAL_CURL to the real absolute curl executable")
    urls = [arg for arg in args if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*://", arg)]
    if len(urls) != 1 or any(a.startswith("--url=") for a in args):
        raise ValueError("Wrapper requires exactly one URL argument")
    parsed = urlsplit(urls[0])
    if parsed.hostname != "api.github.com":
        return subprocess.call([str(real), *args])
    if parsed.scheme != "https" or parsed.port not in (None, 443) or parsed.username:
        raise ValueError("GitHub API URL must be credential-free HTTPS on its standard port")
    switches = {"--fail", "--silent", "--show-error", "--location"}
    value_options = {"--output", "--retry", "--retry-delay", "--connect-timeout", "--max-time", "-o"}
    remaining = iter(args)
    url_seen = False
    for arg in remaining:
        if arg == urls[0]:
            url_seen = True
            continue
        if arg in switches:
            continue
        if arg in value_options:
            if next(remaining, None) is None:
                raise ValueError("Missing curl option value")
            continue
        if re.fullmatch(r"-[fsSL]+", arg):
            continue
        raise ValueError("Unsupported option for authenticated API request")
    if not url_seen:
        raise ValueError("URL was used as an option value rather than a request destination")
    auth = subprocess.run(["gh", "auth", "token", "--hostname", "github.com"],
                          capture_output=True, text=True, timeout=15)
    token = auth.stdout.strip()
    if auth.returncode or not re.fullmatch(r"[A-Za-z0-9_]+", token):
        raise ValueError("No usable token from existing gh authentication")
    config = f'header = "Authorization: Bearer {token}"\nheader = "Accept: application/vnd.github+json"\n'
    # -q must be first: ignore ~/.curlrc so it cannot add destinations or redirects.
    # -L from a reviewed installer is allowed, but a redirect fails before following it.
    result = subprocess.run([str(real), "-q", *args, "--globoff", "--max-redirs", "0", "--config", "-"],
                            input=config, text=True)
    return result.returncode


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, subprocess.TimeoutExpired):
        print("GitHub API curl wrapper refused this call; check URL, options, real curl and gh login.",
              file=sys.stderr)
        sys.exit(2)
