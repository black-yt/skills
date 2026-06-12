#!/usr/bin/env python3
"""
One-way sync for Codex history between two CODEX_HOME directories.

The script is intentionally conservative:
- copies message/history files from source to destination while preserving paths;
- excludes auth/config-like files by default;
- can filter files by path/content regex for a specific project;
- syncs thread titles/names found in JSON, JSONL, and SQLite files.

Example:
  python3 scripts/sync_codex_history.py \
    --source [SOURCE_CODEX_HOME]/.codex \
    --dest [DEST_CODEX_HOME]/.codex \
    --filter [PROJECT_OR_PATH_REGEX] \
    --force
"""

from __future__ import annotations

import argparse
import filecmp
import json
import os
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


DEFAULT_EXCLUDED_NAMES = {
    "auth.json",
    "config.toml",
    "credentials.json",
    "settings.json",
    ".env",
}

DEFAULT_EXCLUDED_DIRS = {
    "bin",
    "cache",
    "logs",
    "node_modules",
    "tmp",
}

TEXT_SUFFIXES = {".json", ".jsonl", ".md", ".txt", ".toml", ".yaml", ".yml"}
JSON_SUFFIXES = {".json", ".jsonl"}
SQLITE_SUFFIXES = {".db", ".sqlite", ".sqlite3"}

ID_KEYS = ("id", "thread_id", "threadId", "session_id", "sessionId", "conversation_id", "conversationId")
TITLE_KEYS = ("title", "name")


@dataclass
class CopyStats:
    copied: int = 0
    overwritten: int = 0
    skipped_existing: int = 0
    skipped_filtered: int = 0
    skipped_sensitive: int = 0
    unchanged: int = 0


@dataclass
class RenameStats:
    titles_found: int = 0
    json_files_changed: int = 0
    jsonl_files_changed: int = 0
    sqlite_rows_changed: int = 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync Codex message records and thread names from one .codex directory to another."
    )
    parser.add_argument("--source", required=True, type=Path, help="Source .codex directory")
    parser.add_argument("--dest", required=True, type=Path, help="Destination .codex directory")
    parser.add_argument(
        "--filter",
        help="Optional regex. Only copy files whose relative path or text content matches it.",
    )
    parser.add_argument(
        "--all-folders",
        action="store_true",
        help="Sync all source folders, still excluding auth/config-like files unless --include-sensitive is set.",
    )
    parser.add_argument(
        "--folders",
        nargs="*",
        default=["sessions"],
        help="Top-level folders to sync when --all-folders is not set. Default: sessions",
    )
    parser.add_argument(
        "--root-files",
        nargs="*",
        default=["history.jsonl"],
        help="Root-level files to sync if present. Default: history.jsonl",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite different destination files. Without this, existing different files are left in place.",
    )
    parser.add_argument(
        "--rename-only",
        action="store_true",
        help="Do not copy files; only sync title/name metadata from source to destination.",
    )
    parser.add_argument(
        "--include-sensitive",
        action="store_true",
        help="Allow copying auth/config-like files. Not recommended for normal history sync.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print actions without writing anything.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print each copied or changed path.",
    )
    return parser.parse_args()


def is_sensitive(path: Path) -> bool:
    parts = set(path.parts)
    return path.name in DEFAULT_EXCLUDED_NAMES or bool(parts & DEFAULT_EXCLUDED_DIRS)


def is_probably_text(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES


def read_text_sample(path: Path, limit: int = 2_000_000) -> str:
    try:
        with path.open("rb") as fh:
            data = fh.read(limit)
        return data.decode("utf-8", errors="ignore")
    except OSError:
        return ""


def file_matches_filter(path: Path, rel: Path, pattern: re.Pattern[str] | None) -> bool:
    if pattern is None:
        return True
    rel_text = rel.as_posix()
    if pattern.search(rel_text):
        return True
    if is_probably_text(path):
        return bool(pattern.search(read_text_sample(path)))
    return False


def top_level_sources(source: Path, args: argparse.Namespace) -> list[Path]:
    items: list[Path] = []
    if args.all_folders:
        items.extend(p for p in source.iterdir() if p.is_dir())
    else:
        items.extend(source / name for name in args.folders)
    items.extend(source / name for name in args.root_files)
    return [p for p in items if p.exists()]


def iter_files(source: Path, args: argparse.Namespace) -> Iterable[Path]:
    for item in top_level_sources(source, args):
        if item.is_file():
            yield item
            continue
        for root, dirs, files in os.walk(item):
            root_path = Path(root)
            if not args.include_sensitive:
                dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDED_DIRS]
            for name in files:
                yield root_path / name


def copy_files(source: Path, dest: Path, args: argparse.Namespace) -> CopyStats:
    stats = CopyStats()
    pattern = re.compile(args.filter) if args.filter else None
    for src_file in iter_files(source, args):
        rel = src_file.relative_to(source)
        if not args.include_sensitive and is_sensitive(rel):
            stats.skipped_sensitive += 1
            continue
        if not file_matches_filter(src_file, rel, pattern):
            stats.skipped_filtered += 1
            continue

        dst_file = dest / rel
        if dst_file.exists():
            try:
                same = filecmp.cmp(src_file, dst_file, shallow=False)
            except OSError:
                same = False
            if same:
                stats.unchanged += 1
                continue
            if not args.force:
                stats.skipped_existing += 1
                continue
            if args.verbose or args.dry_run:
                print(f"overwrite {dst_file}")
            if not args.dry_run:
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dst_file)
            stats.overwritten += 1
            continue

        if args.verbose or args.dry_run:
            print(f"copy {src_file} -> {dst_file}")
        if not args.dry_run:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)
        stats.copied += 1
    return stats


def walk_json_values(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json_values(child)


def extract_titles_from_obj(value: Any, titles: dict[str, str]) -> None:
    for obj in walk_json_values(value):
        found_id = None
        for key in ID_KEYS:
            raw = obj.get(key)
            if isinstance(raw, str) and raw:
                found_id = raw
                break
        if not found_id:
            continue
        for key in TITLE_KEYS:
            raw_title = obj.get(key)
            if isinstance(raw_title, str) and raw_title.strip():
                titles[found_id] = raw_title
                break


def update_titles_in_obj(value: Any, titles: dict[str, str]) -> bool:
    changed = False
    for obj in walk_json_values(value):
        found_id = None
        for key in ID_KEYS:
            raw = obj.get(key)
            if isinstance(raw, str) and raw in titles:
                found_id = raw
                break
        if not found_id:
            continue
        for key in TITLE_KEYS:
            if key in obj and isinstance(obj[key], str) and obj[key] != titles[found_id]:
                obj[key] = titles[found_id]
                changed = True
    return changed


def iter_json_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDED_DIRS]
        for name in files:
            path = Path(current_root) / name
            if path.suffix.lower() in JSON_SUFFIXES:
                yield path


def load_json_file(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_jsonl_file(path: Path) -> list[Any] | None:
    items: list[Any] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                items.append(line)
                continue
            items.append(json.loads(line))
        return items
    except (OSError, json.JSONDecodeError):
        return None


def collect_json_titles(root: Path, titles: dict[str, str]) -> None:
    for path in iter_json_files(root):
        if path.suffix.lower() == ".jsonl":
            items = load_jsonl_file(path)
            if items is None:
                continue
            for item in items:
                extract_titles_from_obj(item, titles)
        else:
            data = load_json_file(path)
            if data is not None:
                extract_titles_from_obj(data, titles)


def apply_json_titles(root: Path, titles: dict[str, str], args: argparse.Namespace) -> tuple[int, int]:
    json_changed = 0
    jsonl_changed = 0
    for path in iter_json_files(root):
        if path.suffix.lower() == ".jsonl":
            items = load_jsonl_file(path)
            if items is None:
                continue
            changed = False
            out_lines: list[str] = []
            for item in items:
                if isinstance(item, str):
                    out_lines.append(item)
                    continue
                changed = update_titles_in_obj(item, titles) or changed
                out_lines.append(json.dumps(item, ensure_ascii=False, separators=(",", ":")))
            if changed:
                jsonl_changed += 1
                if args.verbose or args.dry_run:
                    print(f"rename-jsonl {path}")
                if not args.dry_run:
                    path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")
        else:
            data = load_json_file(path)
            if data is None:
                continue
            if update_titles_in_obj(data, titles):
                json_changed += 1
                if args.verbose or args.dry_run:
                    print(f"rename-json {path}")
                if not args.dry_run:
                    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return json_changed, jsonl_changed


def iter_sqlite_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in DEFAULT_EXCLUDED_DIRS]
        for name in files:
            path = Path(current_root) / name
            if path.suffix.lower() in SQLITE_SUFFIXES:
                yield path


def is_sqlite(path: Path) -> bool:
    try:
        with path.open("rb") as fh:
            return fh.read(16) == b"SQLite format 3\x00"
    except OSError:
        return False


def table_columns(conn: sqlite3.Connection, table: str) -> list[str]:
    rows = conn.execute(f"PRAGMA table_info({quote_ident(table)})").fetchall()
    return [str(row[1]) for row in rows]


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def collect_sqlite_titles(root: Path, titles: dict[str, str]) -> None:
    for path in iter_sqlite_files(root):
        if not is_sqlite(path):
            continue
        try:
            with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                for (table,) in tables:
                    cols = table_columns(conn, table)
                    id_col = next((c for c in ID_KEYS if c in cols), None)
                    title_col = next((c for c in TITLE_KEYS if c in cols), None)
                    if not id_col or not title_col:
                        continue
                    sql = (
                        f"SELECT {quote_ident(id_col)}, {quote_ident(title_col)} "
                        f"FROM {quote_ident(table)} WHERE {quote_ident(title_col)} IS NOT NULL"
                    )
                    for row_id, title in conn.execute(sql):
                        if isinstance(row_id, str) and isinstance(title, str) and title.strip():
                            titles[row_id] = title
        except sqlite3.Error:
            continue


def apply_sqlite_titles(root: Path, titles: dict[str, str], args: argparse.Namespace) -> int:
    changed_rows = 0
    for path in iter_sqlite_files(root):
        if not is_sqlite(path):
            continue
        try:
            with sqlite3.connect(path) as conn:
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                for (table,) in tables:
                    cols = table_columns(conn, table)
                    id_col = next((c for c in ID_KEYS if c in cols), None)
                    title_col = next((c for c in TITLE_KEYS if c in cols), None)
                    if not id_col or not title_col:
                        continue
                    select_sql = (
                        f"SELECT {quote_ident(id_col)}, {quote_ident(title_col)} "
                        f"FROM {quote_ident(table)}"
                    )
                    updates: list[tuple[str, str]] = []
                    for row_id, current_title in conn.execute(select_sql):
                        if isinstance(row_id, str) and row_id in titles and current_title != titles[row_id]:
                            updates.append((titles[row_id], row_id))
                    if not updates:
                        continue
                    changed_rows += len(updates)
                    if args.verbose or args.dry_run:
                        print(f"rename-sqlite {path}:{table} rows={len(updates)}")
                    if not args.dry_run:
                        update_sql = (
                            f"UPDATE {quote_ident(table)} SET {quote_ident(title_col)} = ? "
                            f"WHERE {quote_ident(id_col)} = ?"
                        )
                        conn.executemany(update_sql, updates)
                if args.dry_run:
                    conn.rollback()
                else:
                    conn.commit()
        except sqlite3.Error:
            continue
    return changed_rows


def sync_titles(source: Path, dest: Path, args: argparse.Namespace) -> RenameStats:
    titles: dict[str, str] = {}
    collect_json_titles(source, titles)
    collect_sqlite_titles(source, titles)

    stats = RenameStats(titles_found=len(titles))
    json_changed, jsonl_changed = apply_json_titles(dest, titles, args)
    sqlite_changed = apply_sqlite_titles(dest, titles, args)
    stats.json_files_changed = json_changed
    stats.jsonl_files_changed = jsonl_changed
    stats.sqlite_rows_changed = sqlite_changed
    return stats


def ensure_codex_home(path: Path, label: str) -> None:
    if not path.exists():
        raise SystemExit(f"{label} does not exist: {path}")
    if not path.is_dir():
        raise SystemExit(f"{label} is not a directory: {path}")


def main() -> int:
    args = parse_args()
    source = args.source.expanduser().resolve()
    dest = args.dest.expanduser().resolve()

    ensure_codex_home(source, "source")
    if not args.dry_run:
        dest.mkdir(parents=True, exist_ok=True)
    elif not dest.exists():
        print(f"dry-run: destination does not exist yet: {dest}")

    if source == dest:
        raise SystemExit("source and dest are the same directory")

    copy_stats = CopyStats()
    if not args.rename_only:
        copy_stats = copy_files(source, dest, args)

    rename_stats = sync_titles(source, dest, args)

    print("\nSummary")
    print(f"  source: {source}")
    print(f"  dest:   {dest}")
    print(f"  copied: {copy_stats.copied}")
    print(f"  overwritten: {copy_stats.overwritten}")
    print(f"  unchanged: {copy_stats.unchanged}")
    print(f"  skipped_existing: {copy_stats.skipped_existing}")
    print(f"  skipped_filtered: {copy_stats.skipped_filtered}")
    print(f"  skipped_sensitive: {copy_stats.skipped_sensitive}")
    print(f"  titles_found: {rename_stats.titles_found}")
    print(f"  json_files_renamed: {rename_stats.json_files_changed}")
    print(f"  jsonl_files_renamed: {rename_stats.jsonl_files_changed}")
    print(f"  sqlite_rows_renamed: {rename_stats.sqlite_rows_changed}")

    if copy_stats.skipped_existing and not args.force:
        print("\nNote: existing different files were skipped. Re-run with --force to overwrite from source.")
    if args.dry_run:
        print("\nDry run only: no files were changed.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
