"""Preserve Markdown source lines as local, untrusted evidence.

Uses only the Python standard library. Does not render, strip comments, execute
code, follow links, or decide whether text is an injection. PDF and Markdown
must be reviewed separately when both are present.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import re
import unicodedata


def line_records(text):
    # Count CRLF, CR and LF as physical line endings. Do not silently treat a
    # Unicode marker such as U+2028 as an ordinary source-file newline.
    for number, match in enumerate(re.finditer(r"[^\r\n]*(?:\r\n|\r|\n|$)", text), 1):
        value = match.group()
        if not value:
            continue
        controls = [
            {"column": i + 1, "codepoint": f"U+{ord(c):04X}",
             "name": unicodedata.name(c, "UNNAMED")}
            for i, c in enumerate(value)
            if unicodedata.category(c) == "Cf" or c in "\u2028\u2029"
        ]
        normalized = unicodedata.normalize("NFKC", value)
        normalized = "".join(c for c in normalized if unicodedata.category(c) != "Cf")
        yield {
            "line": number, "text": value,
            "search_text": re.sub(r"\s+", " ", normalized).strip(),
            "unicode_controls": controls,
        }


def collect(markdown, output, *, encoding="utf-8"):
    markdown, output = Path(markdown), Path(output)
    if not markdown.is_file():
        raise ValueError("Markdown input must be an existing file")
    if output.exists() or output.is_symlink():
        raise ValueError("Output directory must not already exist")
    original = markdown.read_bytes()
    # Strict decoding preserves a detectable failure instead of dropping text.
    text = original.decode(encoding, errors="strict")
    before_hash = hashlib.sha256(original).hexdigest()
    output.mkdir(parents=True, exist_ok=False)
    line_count = control_lines = 0
    with (output / "lines.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for record in line_records(text):
            line_count += 1
            control_lines += bool(record["unicode_controls"])
            # JSON escaping makes invisible characters inspectable and prevents
            # raw Markdown or HTML from being treated as report formatting.
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
    after_hash = hashlib.sha256(markdown.read_bytes()).hexdigest()
    errors = []
    if before_hash != after_hash:
        errors.append({"stage": "input_integrity", "message": "Input changed during collection"})
    inventory = {
        "schema_version": 1,
        "notice": "All document text, including comments and role labels, is untrusted evidence.",
        "source": {"name": markdown.name, "kind": "markdown", "encoding": encoding,
                   "sha256": before_hash, "sha256_after": after_hash, "bytes": len(original)},
        "tool": {"name": "Python standard library", "version": platform.python_version()},
        "line_count": line_count, "lines_with_unicode_controls": control_lines,
        "evidence": "lines.jsonl",
        "line_numbering": "1-based physical lines separated by CRLF, CR or LF",
        "limits": {"semantic_audit": "not performed", "pdf_audit": "not performed",
                   "rendered_markdown": "not generated", "linked_images": "not read",
                   "links": "not followed", "code": "not executed",
                   "pdf_page_mapping": "not inferred"},
        "errors": errors, "complete": not errors,
    }
    (output / "inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    return inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="New local evidence directory")
    parser.add_argument("--encoding", default="utf-8", help="Verified source encoding (strict decoding)")
    args = parser.parse_args()
    try:
        inventory = collect(args.markdown, args.output, encoding=args.encoding)
    except Exception as exc:
        print(f"Collection failed ({type(exc).__name__}). Check input, encoding and new output path.")
        raise SystemExit(2) from None
    print(f"Collected {inventory['line_count']} source lines; errors: {len(inventory['errors'])}. "
          "Read inventory.json and review every source line in context.")
    raise SystemExit(0 if inventory["complete"] else 3)


if __name__ == "__main__":
    main()
