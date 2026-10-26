"""Check that redraws remain text-rich, vector-only one-page PDFs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pymupdf

from style3 import ROOT


def verify(path: Path, *, preview_dir: Path | None = None):
    problems = []
    pages = []
    with pymupdf.open(path) as doc:
        if len(doc) != 1:
            problems.append(f"expected one page, got {len(doc)}")
        for page_no, page in enumerate(doc, 1):
            text = page.get_text()
            if len(text.strip()) < 100:
                problems.append(f"page {page_no}: too little extractable text")
            if "\ufffd" in text:
                problems.append(f"page {page_no}: replacement glyph in extracted text")
            images = len(page.get_images(full=True))
            if images:
                problems.append(f"page {page_no}: {images} raster image(s) embedded")
            fonts = []
            for font in page.get_fonts(full=True):
                xref = font[0]
                embedded = bool(doc.extract_font(xref)[3])
                to_unicode = doc.xref_get_key(xref, "ToUnicode")[0] != "null"
                fonts.append({"name": font[3], "embedded": embedded,
                              "to_unicode": to_unicode})
                if not embedded or not to_unicode:
                    problems.append(f"page {page_no}: font {font[3]} not fully embedded/mapped")
            if path.name.startswith(("01_", "02_")):
                names = {font["name"].split("+")[-1] for font in fonts}
                if not any(name.startswith("DejaVuSerif") for name in names):
                    problems.append(f"page {page_no}: diagram serif font missing")
            spans = [span for block in page.get_text("dict")["blocks"]
                     for line in block.get("lines", []) for span in line["spans"]]
            bounds = page.rect + (-1, -1, 1, 1)
            for span in spans:
                if not bounds.contains(pymupdf.Rect(span["bbox"])):
                    problems.append(f"page {page_no}: text outside page: {span['text']!r}")
            if preview_dir is not None:
                preview_dir.mkdir(parents=True, exist_ok=True)
                scale = 2000 / page.rect.width
                page.get_pixmap(matrix=pymupdf.Matrix(scale, scale),
                                alpha=False).save(preview_dir / (path.stem + ".png"))
            pages.append({"page": page_no, "text_characters": len(text),
                          "fonts": fonts, "raster_images": images,
                          "vector_paths": len(page.get_drawings())})
    return {"file": path.name, "ok": not problems,
            "pages": pages, "problems": problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs", nargs="*", type=Path)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--previews", action="store_true")
    args = parser.parse_args()
    paths = args.pdfs or sorted(args.output_dir.glob("[0-9][0-9]_*.pdf"))
    if not paths:
        parser.error("no single-page PDFs found; run render_examples.py first")
    results = [verify(path, preview_dir=args.output_dir / "previews"
                      if args.previews else None) for path in paths]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "validation.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for result in results:
        print(("PASS" if result["ok"] else "FAIL") + " " + result["file"])
        for problem in result["problems"]:
            print("  " + problem)
    if not all(result["ok"] for result in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
