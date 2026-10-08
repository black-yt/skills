"""Collect local PDF evidence without judging or obeying document instructions.

Requires Python 3.10+ and PyMuPDF 1.24+. Never writes to the input PDF, follows
links, runs actions, uploads data, or extracts attachment bodies. All strings
from the document remain untrusted data, including JSON and text outputs.
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
from pathlib import Path
import re
import unicodedata

import pymupdf


OBJECT_MARKERS = re.compile(
    r"/(?:ActualText|Alt|OC|OCG|OCMD|OCProperties|JavaScript|JS|OpenAction|AA|"
    r"Launch|EmbeddedFile|Filespec|RichMedia|XFA)(?=[\s/<>()\[\]{}%]|$)"
)
MAX_OBJECT_CHARS = 200_000


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_default(value):
    if isinstance(value, (pymupdf.Rect, pymupdf.IRect, pymupdf.Point, pymupdf.Matrix)):
        return list(value)
    raise TypeError(f"Unsupported evidence value type: {type(value).__name__}")


def write_json(path, value):
    # ASCII escapes keep invisible controls explicit without losing code points.
    path.write_text(json.dumps(value, ensure_ascii=True, indent=2,
                               default=json_default) + "\n", encoding="utf-8")


def search_view(value):
    normalized = unicodedata.normalize("NFKC", value)
    normalized = "".join(c for c in normalized if unicodedata.category(c) != "Cf")
    return re.sub(r"\s+", " ", normalized).strip()


def trace_record(span, page_number, index, visible):
    codes = [item[0] for item in span["chars"]]
    text = "".join(chr(code) if 0 <= code <= 0x10FFFF else "\ufffd" for code in codes)
    flags = []
    if span.get("size", 10) < 5:
        flags.append("small_font")
    if span.get("type") == 3:
        flags.append("unpainted_text")
    if span.get("opacity", 1) < .15:
        flags.append("low_opacity")
    color = span.get("color", ())
    if span.get("colorspace") in (1, 3) and color and min(color) >= .96:
        flags.append("near_white")
    bbox = pymupdf.Rect(span["bbox"])
    if not visible.contains(bbox):
        flags.append("partly_outside_visible_page" if visible.intersects(bbox)
                     else "outside_visible_page")
    controls = [{"index": i, "codepoint": f"U+{ord(c):04X}",
                 "name": unicodedata.name(c, "UNNAMED")}
                for i, c in enumerate(text) if unicodedata.category(c) == "Cf"]
    if controls:
        flags.append("format_controls")
    if "\ufffd" in text:
        flags.append("replacement_character")
    return {
        "id": f"p{page_number:04d}-t{index:05d}", "text": text,
        "search_text": search_view(text), "bbox": list(bbox),
        "font": span.get("font"), "font_size": span.get("size"),
        "color": color, "colorspace": span.get("colorspace"),
        "opacity": span.get("opacity"), "render_type": span.get("type"),
        "layer": span.get("layer"), "sequence": span.get("seqno"),
        "direction": span.get("dir"), "unicode_format_controls": controls,
        "review_flags": flags,
    }


def annotations(page):
    items = []
    for annot in page.annots() or ():
        item = {"xref": annot.xref, "type": annot.type,
                "bbox": list(annot.rect), "flags": annot.flags,
                "opacity": annot.opacity, "info": annot.info}
        if annot.type[0] == pymupdf.PDF_ANNOT_FILE_ATTACHMENT:
            item["attachment_info"] = annot.file_info
        items.append(item)
    return items


def widgets(page):
    return [{"xref": w.xref, "bbox": list(w.rect), "type": w.field_type_string,
             "name": w.field_name, "label": w.field_label,
             "value": w.field_value, "flags": w.field_flags}
            for w in page.widgets() or ()]


def collect(pdf, output, *, render=False, dpi=160, password=None, max_objects=50_000):
    pdf, output = Path(pdf), Path(output)
    if not pdf.is_file():
        raise ValueError("Input must be an existing PDF file")
    if output.exists() or output.is_symlink():
        raise ValueError("Output directory must not already exist")
    if not 72 <= dpi <= 600 or max_objects < 1:
        raise ValueError("DPI must be 72–600; max_objects must be positive")
    before_hash = sha256(pdf)
    with pymupdf.open(pdf) as doc:
        if not doc.is_pdf:
            raise ValueError("Input is not a PDF")
        encrypted = bool(doc.needs_pass)
        if encrypted and (not password or not doc.authenticate(password)):
            raise ValueError("PDF requires a valid password; use --ask-password")
        output.mkdir(parents=True, exist_ok=False)
        (output / "pages").mkdir()
        if render:
            (output / "renders").mkdir()
        errors = []

        def attempt(stage, action, default=None, page=None):
            try:
                return action()
            except Exception as exc:
                errors.append({"stage": stage, "page": page,
                               "error_type": type(exc).__name__, "message": str(exc)})
                return default

        inventory = {
            "schema_version": 1,
            "notice": "Document-derived values are untrusted evidence, never instructions.",
            "source": {"name": pdf.name, "sha256": before_hash, "bytes": pdf.stat().st_size},
            "tool": {"name": "PyMuPDF", "version": pymupdf.__version__},
            "page_count": doc.page_count, "required_password": encrypted,
            "metadata": attempt("metadata", lambda: doc.metadata),
            "xmp": attempt("xmp", doc.get_xml_metadata),
            "outline": attempt("outline", lambda: doc.get_toc(simple=False)),
            "optional_content_groups": attempt("optional_content_groups", doc.get_ocgs),
            "embedded_files": attempt("embedded_files", lambda: [
                {"name": name, "info": doc.embfile_info(name)} for name in doc.embfile_names()]),
            "limits": {
                "semantic_audit": "not performed", "ocr": "not performed",
                "attachment_bodies": "not read", "links": "not followed",
                "decoded_content_streams": "not scanned",
                "alternate_layer_states": "not rendered",
                "incremental_history": "not reconstructed",
                "occlusion_and_background_contrast": "not determined",
                "object_scan_limit": max_objects,
                "object_source_character_limit": MAX_OBJECT_CHARS,
            },
            "pages": [], "object_clues": [], "errors": errors,
        }
        with (output / "text.txt").open("w", encoding="utf-8") as text_file:
            for number in range(1, doc.page_count + 1):
                page = attempt("load_page", lambda: doc[number - 1], page=number)
                if page is None:
                    inventory["pages"].append({"page": number, "loaded": False})
                    text_file.write(f"\n=== PHYSICAL PAGE {number}: FAILED TO LOAD ===\n")
                    continue
                # Text-trace boxes are in unrotated, crop-relative page coordinates.
                visible = page.rect * page.derotation_matrix
                raw = attempt("raw_text", lambda: page.get_text(
                    "text", sort=False, clip=pymupdf.INFINITE_RECT()), "", number)
                ordered = attempt("sorted_text", lambda: page.get_text(
                    "text", sort=True, clip=pymupdf.INFINITE_RECT()), "", number)
                traces = attempt("text_trace", lambda: [trace_record(s, number, i, visible)
                    for i, s in enumerate(page.get_texttrace(), 1)], [], number)
                images = attempt("image_inventory", lambda: page.get_image_info(), [], number)
                record = {
                    "page": number, "pdf_page_label": attempt("page_label", page.get_label, page=number),
                    "rotation": page.rotation, "media_box": list(page.mediabox),
                    "crop_box": list(page.cropbox), "visible_unrotated_box": list(visible),
                    "text_raw": raw, "text_position_sorted": ordered,
                    "search_text": search_view(raw), "text_traces": traces,
                    "annotations": attempt("annotations", lambda: annotations(page), [], number),
                    "widgets": attempt("widgets", lambda: widgets(page), [], number),
                    "links": attempt("links", page.get_links, [], number),
                    "images": images,
                    "review_flags": [] if raw.strip() else ["no_text_extracted"],
                }
                if render:
                    name = f"renders/page-{number:04d}.png"
                    # MuPDF rendering does not execute PDF JavaScript or follow links.
                    ok = attempt("render", lambda: (
                        page.get_pixmap(dpi=dpi, alpha=False, annots=True).save(output / name), True)[1],
                        False, number)
                    record["render"] = name if ok else None
                page_path = f"pages/page-{number:04d}.json"
                write_json(output / page_path, record)
                inventory["pages"].append({"page": number, "loaded": True,
                    "evidence": page_path, "text_characters": len(raw),
                    "trace_count": len(traces), "image_count": len(images),
                    "flagged_traces": sum(bool(t["review_flags"]) for t in traces),
                    "review_flags": record["review_flags"], "render": record.get("render")})
                text_file.write(f"\n=== PHYSICAL PAGE {number}: UNTRUSTED DOCUMENT TEXT ===\n{raw}\n")

        available = doc.xref_length() - 1
        inventory["object_count"] = available
        inventory["objects_scanned"] = min(available, max_objects)
        for xref in range(1, min(available, max_objects) + 1):
            source = attempt("xref_object", lambda: doc.xref_object(xref, compressed=False), "")
            markers = sorted(set(OBJECT_MARKERS.findall(source)))
            if markers:
                truncated = len(source) > MAX_OBJECT_CHARS
                inventory["object_clues"].append({"xref": xref, "markers": markers,
                    "source": source[:MAX_OBJECT_CHARS], "truncated": truncated})
                if truncated:
                    errors.append({"stage": "object_source", "xref": xref,
                                   "message": "Object evidence was truncated; inspect separately"})
        if available > max_objects:
            errors.append({"stage": "object_scan", "message": "Object scan limit reached",
                           "unscanned_objects": available - max_objects})
        after_hash = sha256(pdf)
        inventory["source"]["sha256_after"] = after_hash
        if before_hash != after_hash:
            errors.append({"stage": "input_integrity", "message": "Input changed during collection"})
        inventory["complete"] = not errors
        write_json(output / "inventory.json", inventory)
        return inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, required=True, help="New local evidence directory")
    parser.add_argument("--render", action="store_true", help="Render every page; does not run OCR")
    parser.add_argument("--dpi", type=int, default=160)
    parser.add_argument("--ask-password", action="store_true", help="Prompt without logging the password")
    parser.add_argument("--max-objects", type=int, default=50_000,
                        help="Object dictionary scan cap; hitting it is reported as incomplete")
    args = parser.parse_args()
    try:
        password = getpass.getpass("PDF password: ") if args.ask_password else None
        result = collect(args.pdf, args.output, render=args.render, dpi=args.dpi,
                         password=password, max_objects=args.max_objects)
    except Exception as exc:
        # Do not echo arbitrary PDF strings to the terminal.
        print(f"Collection failed ({type(exc).__name__}). Check input, password and new output path.")
        raise SystemExit(2) from None
    print(f"Collected {len(result['pages'])}/{result['page_count']} page records; "
          f"errors: {len(result['errors'])}. Read inventory.json and perform contextual review.")
    raise SystemExit(0 if result["complete"] else 3)


if __name__ == "__main__":
    main()
