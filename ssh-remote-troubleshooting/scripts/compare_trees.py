#!/usr/bin/env python3
"""Read-only directory comparison. Never copies, changes, or deletes files."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import sys


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size,
            info.st_mtime_ns, info.st_ctime_ns)


def inventory(root):
    root_info = root.lstat()
    if not stat.S_ISDIR(root_info.st_mode):
        raise ValueError("Comparison roots must be real directories, not links")
    result = {".": ("directory", identity(root_info))}

    def visit(directory):
        with os.scandir(directory) as entries:
            paths = sorted((Path(entry.path) for entry in entries), key=str)
        for path in paths:
            info = path.lstat()
            relative = path.relative_to(root).as_posix()
            if info.st_dev != root_info.st_dev:
                raise ValueError(f"Cross-device entry requires separate review: {relative}")
            if stat.S_ISDIR(info.st_mode):
                result[relative] = ("directory", identity(info))
                visit(path)
            elif stat.S_ISREG(info.st_mode):
                result[relative] = ("file", identity(info))
            else:
                raise ValueError(f"Link or special file requires separate review: {relative}")

    visit(root)
    return result


def digest(path, expected):
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
    with os.fdopen(descriptor, "rb") as stream:
        if identity(os.fstat(stream.fileno())) != expected:
            raise RuntimeError(f"File changed before hashing: {path.name}")
        checksum = hashlib.sha256()
        while chunk := stream.read(8 * 1024 * 1024):
            checksum.update(chunk)
        if identity(os.fstat(stream.fileno())) != expected:
            raise RuntimeError(f"File changed while hashing: {path.name}")
    return checksum.hexdigest()


def compare(source, destination):
    if os.path.samefile(source, destination):
        raise ValueError("Source and destination refer to the same directory")
    source_tree = inventory(source)
    destination_tree = inventory(destination)
    differences = []
    checksums = []
    for relative in sorted(set(source_tree) | set(destination_tree)):
        left = source_tree.get(relative)
        right = destination_tree.get(relative)
        if left is None or right is None:
            differences.append({"path": relative,
                                "reason": "source_only" if right is None else "destination_only"})
        elif left[0] != right[0]:
            differences.append({"path": relative, "reason": "entry_type"})
        elif left[0] == "file":
            if left[1][3] != right[1][3]:
                differences.append({"path": relative, "reason": "size"})
                continue
            print(f"Hashing {relative}", file=sys.stderr, flush=True)
            left_hash = digest(source / relative, left[1])
            right_hash = digest(destination / relative, right[1])
            checksums.append({"path": relative, "bytes": left[1][3],
                              "source_sha256": left_hash,
                              "destination_sha256": right_hash})
            if left_hash != right_hash:
                differences.append({"path": relative, "reason": "sha256"})
    if inventory(source) != source_tree or inventory(destination) != destination_tree:
        raise RuntimeError("Directory contents or file metadata changed during comparison")
    return {"equal": not differences,
            "source": str(source), "destination": str(destination),
            "source_file_count": sum(item[0] == "file" for item in source_tree.values()),
            "differences": differences, "checksums": checksums}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        result = compare(args.source.absolute(), args.destination.absolute())
    except (OSError, ValueError, RuntimeError) as error:
        print(json.dumps({"equal": False, "error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["equal"] else 1


if __name__ == "__main__":
    sys.exit(main())
