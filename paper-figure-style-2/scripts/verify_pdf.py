"""Verify actual PDF text, embedded Unicode fonts, vector content and bounds."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pymupdf


def verify(path, *, expected=(), preview_dir=None):
    problems=[]; pages=[]
    with pymupdf.open(path) as doc:
        text="\n".join(page.get_text() for page in doc)
        for label in expected:
            if label not in text: problems.append(f"Missing extractable label: {label}")
        for i,page in enumerate(doc):
            spans=[s for b in page.get_text("dict")["blocks"] for l in b.get("lines",[]) for s in l["spans"]]
            used={s["font"].replace(" ","") for s in spans}
            fonts=[]
            for xref,ext,kind,base,*_ in page.get_fonts(full=True):
                name=base.split("+")[-1].replace(" ","")
                if name not in used: continue
                embedded=bool(doc.extract_font(xref)[3])
                unicode_map=doc.xref_get_key(xref,"ToUnicode")[0]!="null"
                fonts.append(dict(name=name,embedded=embedded,to_unicode=unicode_map))
                if not embedded or not unicode_map: problems.append(f"Page {i+1}: font {name} lacks embedded font or ToUnicode")
            if used-{f["name"] for f in fonts}: problems.append(f"Page {i+1}: unverified fonts")
            page_text=page.get_text()
            if len(page_text.strip())<70: problems.append(f"Page {i+1}: too little extractable text")
            if "\ufffd" in page_text or "\x00" in page_text: problems.append(f"Page {i+1}: invalid text characters")
            paints=page.get_bboxlog()
            images=sum(kind=="fill-image" for kind,*_ in paints)
            if images or page.get_images(full=True): problems.append(f"Page {i+1}: raster content detected")
            rect=page.rect+(-.6,-.6,.6,.6)
            for span in spans:
                if not rect.contains(pymupdf.Rect(span["bbox"])): problems.append(f"Page {i+1}: text outside canvas: {span['text']}")
            if preview_dir:
                preview_dir=Path(preview_dir); preview_dir.mkdir(parents=True,exist_ok=True)
                suffix=f"_{i+1}" if len(doc)>1 else ""
                scale=1800/page.rect.width
                page.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False).save(preview_dir/(Path(path).stem+suffix+".png"))
            pages.append(dict(page=i+1,text_characters=len(page_text),fonts=fonts,raster_images=images,
                              vector_paths=len(page.get_drawings())))
    return dict(file=Path(path).name,ok=not problems,pages=pages,problems=problems)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdfs",type=Path,nargs="*")
    parser.add_argument("--output-dir",type=Path,default=Path(__file__).resolve().parents[1]/"outputs")
    parser.add_argument("--previews",action="store_true")
    parser.add_argument("--expect",action="append",default=[])
    args=parser.parse_args()
    paths=args.pdfs or sorted(args.output_dir.glob("*.pdf"))
    if not paths: parser.error("No PDFs found; run render_examples.py first")
    results=[verify(p,expected=args.expect,preview_dir=args.output_dir/"previews" if args.previews else None) for p in paths]
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/"validation.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
    for r in results:
        print(("PASS" if r["ok"] else "FAIL")+" "+r["file"])
        for problem in r["problems"]: print("  "+problem)
    if not all(r["ok"] for r in results): raise SystemExit(1)


if __name__=="__main__": main()
