"""Validate native draw.io cells, stencils, labels and renderer round-trip IDs."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET
import zlib

ROOT=Path(__file__).resolve().parents[1]
LABELS={
    "figure-1":["Fast hippocampus","Slow neocortex","Daytime Scaling","Nighttime Scaling","Latent","Weaver"],
    "figure-2":["Daytime Scaling","Nighttime Scaling","Standard decoding","Truncate","Momentum","Transfer","Episodic Buffer","High confidence"],
    "figure-3":["MATH-500","MMLU","GPQA","JAMA","Daytime Scaling","Nighttime Scaling"],
    "figure-4":["Full LatentEvolve","w/o Daytime","w/o Nighttime","MATH-500","SciBench"]}


def validate(path,roundtrip=None,allow_icon_images=False):
    problems=[]
    root=ET.parse(path).getroot()
    if root.tag!="mxfile":
        problems.append("expected an mxfile root")
    results=[]
    if not root.findall("diagram"):
        problems.append("diagram has no pages")
    for page in root.findall("diagram"):
        model=page.find("mxGraphModel")
        if model is None:
            problems.append("expected uncompressed mxGraphModel")
            continue
        cells=model.findall("./root/mxCell")
        ids=[cell.get("id") for cell in cells]
        if len(set(ids))!=len(ids):problems.append("duplicate cell IDs")
        byid={cell.get("id"):cell for cell in cells}
        if "0" not in byid or "1" not in byid or byid["1"].get("parent")!="0":
            problems.append("root cells 0 and 1 are missing/invalid")
        texts=[];stencils=0;edges=0;connected=0;images=0
        for cell in cells:
            identifier=cell.get("id")
            if identifier in ("0","1"):continue
            if cell.get("parent") not in byid:problems.append(f"{identifier}: missing parent")
            style=cell.get("style","")
            if "image=" in style or "shape=image" in style:
                images+=1
                if not allow_icon_images:problems.append(f"{identifier}: image in native-only diagram")
            if "http://" in style or "https://" in style:
                problems.append(f"{identifier}: remote asset reference")
            if "shape=stencil(" in style:
                encoded=style.split("shape=stencil(",1)[1].split(")",1)[0]
                shape=ET.fromstring(unquote(zlib.decompress(base64.b64decode(encoded),-15).decode()))
                if shape.tag!="shape" or any(n.tag in ("image","include-shape") for n in shape.iter()):
                    problems.append(f"{identifier}: unsupported native stencil")
                stencils+=1
            if cell.get("value"):texts.append(cell.get("value"))
            geometry=cell.find("mxGeometry")
            if geometry is None:
                problems.append(f"{identifier}: missing geometry")
                continue
            if cell.get("vertex")=="1":
                values=[float(geometry.get(key,"0")) for key in ("x","y","width","height")]
                if not all(math.isfinite(n) for n in values) or min(values[2:])<=0:
                    problems.append(f"{identifier}: invalid vertex dimensions")
            elif cell.get("edge")=="1":
                edges+=1
                if geometry.get("relative")!="1":problems.append(f"{identifier}: edge geometry must be relative")
                for terminal,point in (("source","sourcePoint"),("target","targetPoint")):
                    ref=cell.get(terminal)
                    if ref and ref not in byid:problems.append(f"{identifier}: invalid {terminal}")
                    if not ref and geometry.find(f"mxPoint[@as='{point}']") is None:
                        problems.append(f"{identifier}: missing {terminal} or point")
                connected+=int(bool(cell.get("source") and cell.get("target")))
            else:problems.append(f"{identifier}: neither vertex nor edge")
        text=" ".join(" ".join(texts).split()).casefold()
        for label in LABELS.get(path.stem,[]):
            if label.casefold() not in text:problems.append("missing required label: "+label)
        if roundtrip:
            engine_path=roundtrip/(path.stem+".json")
            evidence_path=roundtrip/(path.stem+".render.json")
            if not engine_path.is_file() or not evidence_path.is_file():
                problems.append("draw.io round-trip evidence is missing")
            else:
                engine=json.loads(engine_path.read_text(encoding="utf-8"))
                actual={str(cell["id"]) for cell in engine["pages"][0]["cells"]}
                if actual!=set(ids)-{"0"}:problems.append("draw.io round-trip cell IDs differ")
                evidence=json.loads(evidence_path.read_text(encoding="utf-8"))
                if evidence.get("source_sha256")!=hashlib.sha256(path.read_bytes()).hexdigest():
                    problems.append("render evidence is stale for this source file")
        results.append({"page":page.get("name"),"cells":len(cells),"text_cells":len(texts),
                        "native_stencils":stencils,"icon_image_cells":images,"edges":edges,"connected_edges":connected})
    return {"file":path.name,"ok":not problems,"pages":results,"problems":problems}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files",nargs="*",type=Path)
    parser.add_argument("--roundtrip-dir",type=Path)
    parser.add_argument("--allow-icon-images",action="store_true",help="only for an explicitly reviewed icon acquisition demo")
    parser.add_argument("--report",type=Path,default=ROOT/"outputs/validation.json")
    args=parser.parse_args()
    files=args.files or sorted((ROOT/"assets/examples").glob("figure-*.drawio"))
    if not files:parser.error("no .drawio files found")
    results=[validate(p,args.roundtrip_dir,args.allow_icon_images) for p in files]
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    for result in results:
        print(("PASS " if result["ok"] else "FAIL ")+result["file"])
        for problem in result["problems"]:print(" ",problem)
    if not all(result["ok"] for result in results):raise SystemExit(1)


if __name__=="__main__":
    main()
