"""Fetch tested Yesicon/Iconify SVGs and compile native draw.io stencils.

Run only when obtaining/refreshing icons; normal diagram generation is offline.
Uses svgpathtools for SVG arcs. Supported SVGs have paths/basic shapes and no
transforms, masks, gradients, text, scripts, or remote references.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
ICONS=("tabler:brain","tabler:snowflake","tabler:file-code","tabler:chart-bar","tabler:yarn")


def get(url):
    request=Request(url,headers={"User-Agent":"Mozilla/5.0 paper-figure-style-3 icon acquisition"})
    with urlopen(request,timeout=45) as response:
        return response.read()


def commands(path):
    from svgpathtools import Arc, CubicBezier, Line, QuadraticBezier, parse_path
    output=[]
    for subpath in parse_path(path).continuous_subpaths():
        output.append(f'<move x="{subpath.start.real:.5f}" y="{subpath.start.imag:.5f}"/>')
        for segment in subpath:
            segments=segment.as_cubic_curves(curves=max(1,math.ceil(abs(segment.delta)/80))) if isinstance(segment,Arc) else [segment]
            for part in segments:
                if isinstance(part,Line):
                    output.append(f'<line x="{part.end.real:.5f}" y="{part.end.imag:.5f}"/>')
                elif isinstance(part,CubicBezier):
                    output.append(f'<curve x1="{part.control1.real:.5f}" y1="{part.control1.imag:.5f}" x2="{part.control2.real:.5f}" y2="{part.control2.imag:.5f}" x3="{part.end.real:.5f}" y3="{part.end.imag:.5f}"/>')
                elif isinstance(part,QuadraticBezier):
                    output.append(f'<quad x1="{part.control.real:.5f}" y1="{part.control.imag:.5f}" x2="{part.end.real:.5f}" y2="{part.end.imag:.5f}"/>')
                else:
                    raise ValueError(f"unsupported segment: {type(part).__name__}")
        if subpath.isclosed():
            output.append("<close/>")
    return "".join(output)


def convert(svg_bytes,name):
    root=ET.fromstring(svg_bytes)
    view=[float(n) for n in root.attrib["viewBox"].split()]
    if view[:2] != [0,0]:
        raise ValueError("nonzero viewBox origin requires an explicit transform")
    foreground=[]
    def walk(node,inherited):
        tag=node.tag.split("}")[-1]
        attrs={**inherited,**node.attrib}
        if "transform" in node.attrib or "style" in node.attrib:
            raise ValueError("SVG transforms and inline CSS require explicit conversion")
        if tag in ("svg","g"):
            for child in node:
                walk(child,attrs)
            return
        if tag in ("title","desc","metadata"):
            return
        if tag=="path":
            data=node.attrib["d"]
        elif tag=="circle":
            cx,cy,r=(float(attrs.get(k,0)) for k in ("cx","cy","r"))
            data=f"M {cx-r} {cy} a {r} {r} 0 1 0 {2*r} 0 a {r} {r} 0 1 0 {-2*r} 0 Z"
        elif tag=="line":
            data=f'M {attrs["x1"]} {attrs["y1"]} L {attrs["x2"]} {attrs["y2"]}'
        elif tag in ("polyline","polygon"):
            data="M "+attrs["points"]+(" Z" if tag=="polygon" else "")
        elif tag=="rect":
            x,y,w,h=(float(attrs.get(k,0)) for k in ("x","y","width","height"))
            data=f"M {x} {y} h {w} v {h} h {-w} Z"
        else:
            raise ValueError(f"unsupported SVG element: {tag}")
        fill,stroke=attrs.get("fill","black"),attrs.get("stroke","none")
        if fill not in ("none","black","#000","#000000","currentColor") or stroke not in ("none","black","#000","#000000","currentColor"):
            raise ValueError("use a single-color icon with inherited colors")
        paint="fillstroke" if fill!="none" and stroke!="none" else "fill" if fill!="none" else "stroke"
        foreground.append("<path>"+commands(data)+f"</path><{paint}/>")
    walk(root,{})
    xml=f'<shape name="{name}" w="{view[2]:g}" h="{view[3]:g}" aspect="fixed" strokewidth="inherit"><foreground><linecap cap="round"/><linejoin join="round"/>'+"".join(foreground)+"</foreground></shape>"
    ET.fromstring(xml)
    return xml


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,default=ROOT/"assets/icons")
    parser.add_argument("--icons",nargs="+",default=list(ICONS))
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=True)
    records=[]
    for identifier in args.icons:
        prefix,icon=identifier.split(":",1)
        metadata_url=f"https://yesicon.app/api/icon/{identifier}?locale=en"
        metadata=json.loads(get(metadata_url))
        if metadata["license"]["spdx"] not in ("MIT","CC-BY-3.0"):
            raise ValueError(f"review license before bundling {identifier}")
        download_url=f"https://api.iconify.design/{prefix}/{icon}.svg"
        svg=get(download_url)
        stem=identifier.replace(":","-")
        native=convert(svg,stem)
        (args.output/(stem+".svg")).write_bytes(svg)
        (args.output/(stem+".shape.xml")).write_text(native+"\n",encoding="utf-8")
        author=metadata["author"]["name"]
        if identifier=="game-icons:yarn":
            author="Delapouite"
        records.append({"id":identifier,"discovery_page":f"https://yesicon.app/{prefix}/{icon}",
                        "metadata_url":metadata_url,"download_url":download_url,
                        "author":author,"license":metadata["license"],
                        "verified_license_url":"https://github.com/tabler/tabler-icons/blob/main/LICENSE" if prefix=="tabler" else metadata["license"]["url"],
                        "collection_version":metadata.get("version"),
                        "svg_sha256":hashlib.sha256(svg).hexdigest(),
                        "native_shape":stem+".shape.xml","tested":"2026-10-27"})
        print(identifier,"SVG and native stencil OK")
    (args.output/"sources.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    licenses={"TABLER-LICENSE.txt":"https://raw.githubusercontent.com/tabler/tabler-icons/main/LICENSE"}
    for filename,url in licenses.items():
        (args.output/filename).write_bytes(get(url))


if __name__=="__main__":
    main()
