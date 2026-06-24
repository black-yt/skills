#!/usr/bin/env python3
"""Download an Overleaf project ZIP, then compare or update a local folder.

The script intentionally accepts the Overleaf ZIP URL and Cookie at runtime.
Do not hard-code session cookies or project-specific URLs in this file.
"""

from __future__ import annotations

import argparse
import filecmp
import fnmatch
import os
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile


DEFAULT_IGNORE_PATTERNS = (
    ".git/**",
    ".codex/**",
    ".claude/**",
    "__pycache__/**",
    "node_modules/**",
    ".overleaf-sync/**",
    "overleaf_tmp/**",
    "latex_cache/**",
    "backups/**",
    "raw/**",
    "context/**",
    "__MACOSX/**",
    "*.py",
    "*.pyc",
    "*.md",
    "*.log",
    "*.aux",
    "*.out",
    "*.toc",
    "*.synctex.gz",
    ".gitignore",
    ".gitmodules",
    "AGENTS.md",
    "CLAUDE.md",
    "overleaf_tmp.zip",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare or update a local folder from an Overleaf ZIP download."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="check",
        choices=("check", "update"),
        help="Defaults to check. Use update with --overwrite to copy remote files into the target without deleting local-only files.",
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("OVERLEAF_ZIP_URL"),
        help="Overleaf project ZIP download URL. Can also be set with OVERLEAF_ZIP_URL.",
    )
    parser.add_argument(
        "--cookie",
        default=os.environ.get("OVERLEAF_COOKIE"),
        help="Cookie header value copied from the browser Network panel. Can also be set with OVERLEAF_COOKIE.",
    )
    parser.add_argument(
        "--cookie-file",
        help="Read the Cookie header value from a local file. The file is stripped of leading/trailing whitespace.",
    )
    parser.add_argument(
        "--target",
        default=".",
        help="Local folder to compare or update. Defaults to the current directory.",
    )
    parser.add_argument(
        "--ignore",
        action="append",
        default=[],
        help="Additional fnmatch-style ignore pattern, relative to project root. May be repeated.",
    )
    parser.add_argument(
        "--no-default-ignores",
        action="store_true",
        help="Disable built-in ignore patterns such as .git/**, *.py, *.md, latex_cache/**.",
    )
    parser.add_argument(
        "--no-strip-single-root",
        action="store_true",
        help="Do not strip a single top-level directory from the extracted ZIP.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="For update mode, print files that would be copied without writing them.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow update mode to write files. Without this flag, update mode is a dry run.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=60.0,
        help="HTTP timeout in seconds.",
    )
    return parser.parse_args()


def read_cookie(args: argparse.Namespace) -> str:
    if args.cookie_file:
        cookie = Path(args.cookie_file).read_text(encoding="utf-8").strip()
    else:
        cookie = (args.cookie or "").strip()
    if not cookie:
        raise SystemExit(
            "Missing Cookie. Pass --cookie, --cookie-file, or set OVERLEAF_COOKIE."
        )
    return cookie


def require_url(args: argparse.Namespace) -> str:
    url = (args.url or "").strip()
    if not url:
        raise SystemExit("Missing URL. Pass --url or set OVERLEAF_ZIP_URL.")
    return url


def download_zip(url: str, cookie: str, output_path: Path, timeout: float) -> None:
    request = urllib.request.Request(
        url,
        headers={
            "Cookie": cookie,
            "User-Agent": "overleaf-project-sync/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            if status is not None and status != 200:
                raise RuntimeError(f"download failed with HTTP status {status}")
            total = int(response.headers.get("content-length") or 0)
            downloaded = 0
            with output_path.open("wb") as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        percent = downloaded * 100 / total
                        print(
                            f"\rDownloading ZIP: {downloaded}/{total} bytes ({percent:.1f}%)",
                            end="",
                            file=sys.stderr,
                        )
            if total:
                print(file=sys.stderr)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"Download failed with HTTP {exc.code}. Check ZIP URL and Cookie."
        ) from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Download failed: {exc.reason}") from exc


def safe_extract(zip_path: Path, extract_dir: Path) -> None:
    root = extract_dir.resolve()
    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            destination = (root / member.filename).resolve()
            if destination != root and root not in destination.parents:
                raise SystemExit(f"Unsafe ZIP member path: {member.filename}")
        archive.extractall(root)


def choose_remote_root(extract_dir: Path, strip_single_root: bool) -> Path:
    if not strip_single_root:
        return extract_dir
    entries = [p for p in extract_dir.iterdir() if p.name != "__MACOSX"]
    dirs = [p for p in entries if p.is_dir()]
    files = [p for p in entries if p.is_file()]
    if len(dirs) == 1 and not files:
        return dirs[0]
    return extract_dir


def build_ignore_patterns(args: argparse.Namespace) -> tuple[str, ...]:
    patterns: list[str] = []
    if not args.no_default_ignores:
        patterns.extend(DEFAULT_IGNORE_PATTERNS)
    patterns.extend(args.ignore)
    return tuple(patterns)


def is_ignored(rel_path: str, patterns: tuple[str, ...], is_dir: bool = False) -> bool:
    rel_path = rel_path.replace(os.sep, "/").strip("/")
    candidates = {rel_path, Path(rel_path).name}
    if is_dir:
        candidates.add(f"{rel_path}/")
        candidates.add(f"{rel_path}/**")
    for pattern in patterns:
        pattern = pattern.replace("\\", "/").strip("/")
        for candidate in candidates:
            if fnmatch.fnmatch(candidate, pattern) or fnmatch.fnmatch(rel_path, pattern):
                return True
    return False


def collect_files(root: Path, patterns: tuple[str, ...]) -> dict[str, Path]:
    files_by_rel: dict[str, Path] = {}
    for current_root, dirnames, filenames in os.walk(root):
        current = Path(current_root)
        rel_dir = current.relative_to(root).as_posix()
        if rel_dir == ".":
            rel_dir = ""

        kept_dirs = []
        for dirname in dirnames:
            rel = f"{rel_dir}/{dirname}" if rel_dir else dirname
            if not is_ignored(rel, patterns, is_dir=True):
                kept_dirs.append(dirname)
        dirnames[:] = kept_dirs

        for filename in filenames:
            rel = f"{rel_dir}/{filename}" if rel_dir else filename
            if is_ignored(rel, patterns):
                continue
            files_by_rel[rel] = current / filename
    return files_by_rel


def compare_files(remote_root: Path, target_root: Path, patterns: tuple[str, ...]):
    remote_files = collect_files(remote_root, patterns)
    target_files = collect_files(target_root, patterns)

    changed = []
    missing = []
    for rel, remote_path in sorted(remote_files.items()):
        target_path = target_files.get(rel)
        if target_path is None:
            missing.append(rel)
        elif not filecmp.cmp(remote_path, target_path, shallow=False):
            changed.append(rel)

    extra = sorted(rel for rel in target_files if rel not in remote_files)
    return changed, missing, extra, remote_files


def print_group(title: str, paths: list[str]) -> None:
    if not paths:
        return
    print(title)
    for path in paths:
        print(f"  - {path}")
    print()


def copy_remote_files(
    remote_files: dict[str, Path], target_root: Path, dry_run: bool
) -> None:
    for rel, remote_path in sorted(remote_files.items()):
        target_path = target_root / rel
        if dry_run:
            print(f"DRY-RUN copy: {rel}")
            continue
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(remote_path, target_path)
        print(f"copied: {rel}")


def main() -> int:
    args = parse_args()
    url = require_url(args)
    cookie = read_cookie(args)
    target_root = Path(args.target).resolve()
    if not target_root.exists() or not target_root.is_dir():
        raise SystemExit(f"Target directory does not exist: {target_root}")

    patterns = build_ignore_patterns(args)

    with tempfile.TemporaryDirectory(prefix="overleaf-sync-") as temp_name:
        temp_dir = Path(temp_name)
        zip_path = temp_dir / "project.zip"
        extract_dir = temp_dir / "extract"
        extract_dir.mkdir()

        print("Downloading Overleaf project ZIP...")
        download_zip(url, cookie, zip_path, args.timeout)

        print("Extracting ZIP...")
        safe_extract(zip_path, extract_dir)
        remote_root = choose_remote_root(
            extract_dir, strip_single_root=not args.no_strip_single_root
        )

        changed, missing, extra, remote_files = compare_files(
            remote_root, target_root, patterns
        )

        print()
        print("Comparison result")
        print("=================")
        if not changed and not missing and not extra:
            print("OK: local target matches the Overleaf ZIP under current ignore rules.")
        else:
            print_group("Changed files:", changed)
            print_group("Missing locally, present in Overleaf:", missing)
            print_group("Extra locally, absent from Overleaf:", extra)

        if args.mode == "check":
            return 0 if not changed and not missing and not extra else 2

        effective_dry_run = args.dry_run or not args.overwrite
        if effective_dry_run and not args.dry_run:
            print("Update requested without --overwrite; running as dry run.")
        print("Updating local target from Overleaf ZIP...")
        copy_remote_files(remote_files, target_root, dry_run=effective_dry_run)
        if effective_dry_run:
            print("Dry run complete. No files were written.")
        else:
            print("Update complete. Local-only files were not deleted.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
