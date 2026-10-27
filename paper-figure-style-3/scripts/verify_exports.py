"""Check draw.io exports for editable XML/text and vector-only primary PDFs."""
import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET

from PIL import Image
import pymupdf

ROOT=Path(__file__).resolve().parents[1]


def verify(directory,stem):
    problems=[]
    svg=ET.parse(directory/(stem+".svg")).getroot()
    if "mxfile" not in svg.get("content",""):problems.append("SVG lacks embedded diagram XML")
    images=[n for n in svg.iter() if n.tag.endswith("}image")]
    if images:problems.append("primary SVG contains image elements")
    text_count=sum(n.tag.endswith("}text") for n in svg.iter())
    if text_count<10:problems.append("SVG has too few text elements")
    with Image.open(directory/(stem+".png")) as image:
        image.load()
        size=image.size
        if "mxfile" not in image.info:problems.append("PNG lacks embedded mxfile")
    with pymupdf.open(directory/(stem+".pdf")) as doc:
        if len(doc)!=1:problems.append("PDF must have one page")
        pdf_text=" ".join(p.get_text() for p in doc)
        raster_count=sum(len(p.get_images(full=True)) for p in doc)
        if raster_count:problems.append("primary PDF contains raster images")
        if len(pdf_text.strip())<100:problems.append("PDF lacks extractable text")
        if "\ufffd" in pdf_text:problems.append("PDF has replacement glyphs")
    return {"figure":stem,"ok":not problems,"svg_text_elements":text_count,
            "pdf_text_characters":len(pdf_text),"pdf_raster_images":raster_count,
            "png_size":size,"problems":problems}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir",type=Path,default=ROOT/"outputs")
    args=parser.parse_args()
    results=[verify(args.input_dir,f"figure-{n}") for n in range(1,5)]
    (args.input_dir/"exports-validation.json").write_text(json.dumps(results,indent=2)+"\n")
    for item in results:
        print(("PASS " if item["ok"] else "FAIL ")+item["figure"])
        for problem in item["problems"]:print(" ",problem)
    if not all(item["ok"] for item in results):raise SystemExit(1)


if __name__=="__main__":main()
