#!/usr/bin/env python3
"""Convert a Hugging Face hub cache directory into a flat model directory.

The input should usually look like:

  models--Qwen--Qwen3.5-35B-A3B/
  ├── blobs/
  ├── refs/
  │   └── main
  └── snapshots/
      └── <commit>/

The output is a standard checkpoint/model folder that can be passed to
Transformers or vLLM as MODEL_PATH.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"WARNING: {message}", file=sys.stderr)


def resolve_snapshot(cache_dir: Path, revision: str) -> Path:
    if not cache_dir.exists():
        fail(f"cache directory does not exist: {cache_dir}")
    if not cache_dir.is_dir():
        fail(f"cache path is not a directory: {cache_dir}")

    refs_dir = cache_dir / "refs"
    snapshots_dir = cache_dir / "snapshots"
    if not snapshots_dir.is_dir():
        fail(
            "cache directory does not contain snapshots/. "
            "Pass a Hugging Face hub cache folder such as models--Org--Model."
        )

    ref_file = refs_dir / revision
    if ref_file.is_file():
        commit = ref_file.read_text(encoding="utf-8").strip()
        snapshot = snapshots_dir / commit
        if snapshot.is_dir():
            return snapshot
        fail(f"refs/{revision} points to missing snapshot: {snapshot}")

    direct_snapshot = snapshots_dir / revision
    if direct_snapshot.is_dir():
        return direct_snapshot

    snapshots = sorted(p for p in snapshots_dir.iterdir() if p.is_dir())
    if len(snapshots) == 1:
        warn(f"refs/{revision} not found; using the only snapshot: {snapshots[0].name}")
        return snapshots[0]

    known = ", ".join(p.name for p in snapshots[:10])
    fail(
        f"cannot resolve revision {revision!r}. "
        f"Known snapshots: {known or '<none>'}. "
        "Use --revision with a refs/ name or snapshot commit."
    )


def ensure_output_dir(out_dir: Path, overwrite: bool, dry_run: bool) -> None:
    if out_dir.exists() and not out_dir.is_dir():
        fail(f"output path exists and is not a directory: {out_dir}")

    if out_dir.exists() and any(out_dir.iterdir()):
        if not overwrite:
            fail(
                f"output directory is not empty: {out_dir}. "
                "Use --overwrite only after checking the target path."
            )
        if dry_run:
            print(f"DRY-RUN: would remove existing contents under {out_dir}")
            return
        for item in out_dir.iterdir():
            if item.is_dir() and not item.is_symlink():
                shutil.rmtree(item)
            else:
                item.unlink()

    if not dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)


def resolve_source(path: Path) -> Path:
    if path.is_symlink():
        target = Path(os.readlink(path))
        if not target.is_absolute():
            target = path.parent / target
        return target.resolve()
    return path


def copy_or_link_file(src: Path, dst: Path, link_mode: str, dry_run: bool) -> str:
    if dry_run:
        return f"would {link_mode} {src} -> {dst}"

    dst.parent.mkdir(parents=True, exist_ok=True)

    if dst.exists() or dst.is_symlink():
        if dst.is_dir() and not dst.is_symlink():
            shutil.rmtree(dst)
        else:
            dst.unlink()

    if link_mode == "hardlink":
        try:
            os.link(src, dst)
            return f"hardlinked {src} -> {dst}"
        except OSError as exc:
            warn(f"hardlink failed for {src}: {exc}; falling back to copy")

    shutil.copy2(src, dst)
    return f"copied {src} -> {dst}"


def convert_cache(
    cache_dir: Path,
    out_dir: Path,
    revision: str,
    link_mode: str,
    overwrite: bool,
    dry_run: bool,
    strict: bool,
) -> None:
    cache_dir = cache_dir.expanduser().resolve()
    out_dir = out_dir.expanduser().resolve()
    if cache_dir == out_dir:
        fail("cache directory and output directory must be different")

    snapshot = resolve_snapshot(cache_dir, revision)
    config = snapshot / "config.json"
    if not config.exists():
        message = f"snapshot does not contain config.json: {snapshot}"
        if strict:
            fail(message)
        warn(message)

    ensure_output_dir(out_dir, overwrite=overwrite, dry_run=dry_run)

    entries = sorted(snapshot.rglob("*"))
    file_count = 0
    dir_count = 0
    shown = 0

    for entry in entries:
        rel = entry.relative_to(snapshot)
        dst = out_dir / rel

        if entry.is_dir() and not entry.is_symlink():
            dir_count += 1
            if dry_run:
                if shown < 25:
                    print(f"DRY-RUN: would create directory {dst}")
                    shown += 1
            else:
                dst.mkdir(parents=True, exist_ok=True)
            continue

        src = resolve_source(entry)
        if not src.exists():
            warn(f"skipping broken symlink or missing file: {entry} -> {src}")
            continue
        if src.is_dir():
            if dry_run:
                if shown < 25:
                    print(f"DRY-RUN: would copy directory {src} -> {dst}")
                    shown += 1
            else:
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst, symlinks=False)
            dir_count += 1
            continue
        if not src.is_file():
            warn(f"skipping unsupported entry: {entry}")
            continue

        file_count += 1
        result = copy_or_link_file(src, dst, link_mode=link_mode, dry_run=dry_run)
        if shown < 25:
            print(("DRY-RUN: " if dry_run else "") + result)
            shown += 1

    if shown == 25 and len(entries) > 25:
        print(f"... skipped printing {len(entries) - 25} additional entries")

    mode = "DRY-RUN complete" if dry_run else "conversion complete"
    print(f"{mode}: snapshot={snapshot}")
    print(f"output={out_dir}")
    print(f"files={file_count}, directories={dir_count}, link_mode={link_mode}")
    if not dry_run:
        print("Next check:")
        print(f"  test -f {out_dir / 'config.json'}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert Hugging Face hub cache snapshots into a standard model directory."
    )
    parser.add_argument("--cache-dir", required=True, help="Hugging Face hub cache model folder.")
    parser.add_argument("--out-dir", required=True, help="Output standard model/checkpoint folder.")
    parser.add_argument("--revision", default="main", help="refs/ name or snapshot commit. Default: main.")
    parser.add_argument(
        "--link-mode",
        choices=["hardlink", "copy"],
        default="hardlink",
        help="Use hardlinks to save space when possible, or copy files. Default: hardlink.",
    )
    parser.add_argument("--overwrite", action="store_true", help="Delete existing output contents first.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned actions without writing files.")
    parser.add_argument("--strict", action="store_true", help="Fail when config.json is missing.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    convert_cache(
        cache_dir=Path(args.cache_dir),
        out_dir=Path(args.out_dir),
        revision=args.revision,
        link_mode=args.link_mode,
        overwrite=args.overwrite,
        dry_run=args.dry_run,
        strict=args.strict,
    )


if __name__ == "__main__":
    main()
