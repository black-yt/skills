"""Check selectable text, embedded fonts, vector shading and page bounds.

Optional PNGs are inspection previews rendered FROM the finished PDFs. They are
never used as drawing inputs or substituted for the vector deliverables.
"""
from __future__ import annotations

import argparse
import json
from hashlib import sha256
from pathlib import Path

import pymupdf


def verify_small_logos(doc,page):
    """Only bundled pixel-exact logos at icon size may be raster placements.

    An arbitrary image, screenshot, changed alpha mask or enlarged logo still
    fails. Native shadings synthesized by MuPDF are not actual image paint ops.
    """
    from model_logos import approved_logo_pixels
    approved=approved_logo_pixels()
    placements=[]
    problems=[]
    for item in page.get_images(full=True):
        xref,smask,width,height,bpc,space,*_=item
        alpha=doc.xref_stream(smask) if smask else bytes([255])*(width*height)
        key=(width,height,sha256(doc.xref_stream(xref) or b"").hexdigest(),sha256(alpha or b"").hexdigest())
        provider=approved.get(key) if bpc==8 and space=="DeviceRGB" else None
        if not provider:
            problems.append(f"Unrecognized image resource xref={xref}; only bundled model logos are allowed")
            continue
        for rect in page.get_image_rects(xref):
            limit=page.rect.width*.06
            if rect.width>limit or rect.height>limit or not page.rect.contains(rect):
                problems.append(f"Model logo {provider} exceeds icon size or page bounds")
            placements.append(dict(provider=provider,bbox=list(rect)))
    return placements,problems


def verify(path: Path, *, expected=(), min_chars=80, preview_dir=None, strict_vector=False):
    problems=[]
    pages=[]
    with pymupdf.open(path) as doc:
        full_text="\n".join(p.get_text() for p in doc)
        for phrase in expected:
            if phrase not in full_text:
                problems.append(f"Expected text not recoverable: {phrase}")
        for i,page in enumerate(doc):
            text=page.get_text()
            spans=[span for block in page.get_text("dict")["blocks"]
                   for line in block.get("lines",[]) for span in line["spans"]]
            used_fonts={span["font"].replace(" ","") for span in spans}
            font_info=[]
            for font in page.get_fonts(full=True):
                xref,ext,kind,base,*_=font
                base=base.split("+")[-1].replace(" ","")
                if base not in used_fonts:
                    continue
                embedded=bool(doc.extract_font(xref)[3])
                unicode_map=doc.xref_get_key(xref,"ToUnicode")[0]!="null"
                font_info.append(dict(name=base,embedded=embedded,to_unicode=unicode_map))
                if not embedded or not unicode_map:
                    problems.append(f"Page {i+1}: font {base} needs embedding and ToUnicode")
            covered={v["name"] for v in font_info}
            if used_fonts-covered:
                problems.append(f"Page {i+1}: unverified used fonts: {sorted(used_fonts-covered)}")
            if len(text.strip()) < min_chars:
                problems.append(f"Page {i+1}: too little extractable text")
            if "\ufffd" in text or "\x00" in text:
                problems.append(f"Page {i+1}: replacement/null characters in extracted text")
            # MuPDF can synthesize an xref=0 bitmap of a shading for extraction.
            # Inspect actual PDF painting operations and resources instead.
            paint_ops=page.get_bboxlog()
            image_count=sum(kind=="fill-image" for kind,*_ in paint_ops)
            image_resources=len(page.get_images(full=True))
            logo_placements=[]
            if image_count or image_resources:
                if strict_vector:
                    problems.append(f"Page {i+1}: strict vector check found {image_count} raster placements / {image_resources} resources")
                else:
                    logo_placements,logo_problems=verify_small_logos(doc,page)
                    problems.extend(f"Page {i+1}: {problem}" for problem in logo_problems)
                    if len(logo_placements)!=image_count:
                        problems.append(f"Page {i+1}: not all raster paint operations match approved small model logos")
            shadings=sum(kind=="fill-shade" for kind,*_ in paint_ops)
            if not shadings:
                problems.append(f"Page {i+1}: no native PDF gradient shading")
            margin=page.rect+(-.5,-.5,.5,.5)
            for span in spans:
                if not margin.contains(pymupdf.Rect(span["bbox"])):
                    problems.append(f"Page {i+1}: text outside page: {span['text']}")
            if preview_dir:
                preview_dir.mkdir(parents=True,exist_ok=True)
                suffix=f"_{i+1}" if len(doc)>1 else ""
                scale=1440/page.rect.width
                page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).save(preview_dir/(path.stem+suffix+".png"))
            pages.append(dict(page=i+1,text_characters=len(text),raster_images=image_count,image_resources=image_resources,
                              model_logos=logo_placements,
                              native_gradients=shadings,vector_paths=len(page.get_drawings()),fonts=font_info))
    return dict(file=path.name,ok=not problems,pages=pages,problems=problems)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs",nargs="*",type=Path)
    parser.add_argument("--output-dir",type=Path,default=Path(__file__).resolve().parents[1]/"outputs")
    parser.add_argument("--previews",action="store_true")
    parser.add_argument("--expect",action="append",default=[],help="Required copyable phrase (repeatable)")
    parser.add_argument("--strict-vector",action="store_true",help="Reject every raster image, including original PNG model logos")
    args=parser.parse_args()
    pdfs=args.pdfs or sorted(args.output_dir.glob("*.pdf"))
    if not pdfs:
        parser.error("No PDFs found. Run render_examples.py first.")
    preview=args.output_dir/"previews" if args.previews else None
    results=[verify(p,expected=args.expect,preview_dir=preview,strict_vector=args.strict_vector) for p in pdfs]
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/"validation.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for result in results:
        chars=sum(p["text_characters"] for p in result["pages"])
        images=sum(p["raster_images"] for p in result["pages"])
        logos=sum(len(p["model_logos"]) for p in result["pages"])
        print(f"{'PASS' if result['ok'] else 'FAIL'} {result['file']}: {chars} text characters, {images} raster images ({logos} approved logos)")
        for problem in result["problems"]:
            print("  "+problem)
    if not all(result["ok"] for result in results):
        raise SystemExit(1)


if __name__=="__main__":
    main()
