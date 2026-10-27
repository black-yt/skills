"""Exercise the two tested acquisition routes and write a local draw.io demo.

Flaticon PNG is downloaded to outputs only, with attribution. It is not a
redistributable skill asset; review that site's current license before reuse.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import struct
from xml.etree import ElementTree as ET

from drawio import Diagram, save, stencil_xml
from fetch_icons import convert, get

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,default=ROOT/"outputs/icon-acquisition")
    args=parser.parse_args()
    out=args.output_dir
    out.mkdir(parents=True,exist_ok=True)
    metadata=json.loads(get("https://yesicon.app/api/icon/tabler:brain?locale=en"))
    if metadata["license"]["spdx"]!="MIT":raise ValueError("review updated icon license")
    svg=get("https://api.iconify.design/tabler/brain.svg")
    ET.fromstring(svg)
    shape=convert(svg,"tabler-brain")
    (out/"yesicon-tabler-brain.svg").write_bytes(svg)
    (out/"yesicon-tabler-brain.shape.xml").write_text(shape,encoding="utf-8")
    png=get("https://cdn-icons-png.flaticon.com/512/11000/11000244.png")
    if png[:8]!=b"\x89PNG\r\n\x1a\n":raise ValueError("Flaticon response is not PNG")
    width,height=struct.unpack(">II",png[16:24])
    if (width,height)!=(512,512):raise ValueError("unexpected Flaticon image dimensions")
    (out/"flaticon-yarn.png").write_bytes(png)
    records=[{"site":"Yesicon","page":"https://yesicon.app/tabler/brain","author":metadata["author"]["name"],"license":"MIT","format":"SVG converted to native draw.io stencil","sha256":hashlib.sha256(svg).hexdigest()},
             {"site":"Flaticon","page":"https://www.flaticon.com/free-icon/yarn_11000244","author":"Pop Vectors","license":"Flaticon free license with attribution; review current terms","format":"PNG 512x512 only","sha256":hashlib.sha256(png).hexdigest(),"redistribution":"Keep raw downloaded PNG local; not bundled in the public skill"}]
    (out/"sources.json").write_text(json.dumps(records,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    d=Diagram("Tested icon acquisition",960,370)
    d.text("title",20,15,920,42,"Tested icon acquisition",size=26,bold=True)
    d.shape("yesicon-native-brain",142,85,125,125,kind=stencil_xml(shape),fill="none",stroke="#386A92",sw=3,sketch=False)
    d.text("yesicon-caption",30,233,420,80,"Yesicon → Tabler brain → native stencil\nPaweł Kuna · MIT\nyesicon.app/tabler/brain",size=17)
    d.shape("flaticon-yarn-icon",670,85,125,125,kind="image",fill="none",stroke="none",sketch=False,
            image="data:image/png,"+base64.b64encode(png).decode(),imageAspect=1)
    d.text("flaticon-caption",490,233,440,80,"Yarn icon by Pop Vectors from Flaticon\nFree PNG with attribution\nflaticon.com/free-icon/yarn_11000244",size=16)
    d.text("format-boundary",30,329,900,25,"Text and layout are native. Left icon is an editable stencil; right icon is a separate PNG image cell.",size=13)
    print(save([d],out/"icon-acquisition.drawio"))
    print("PASS Yesicon metadata/SVG/stencil and Flaticon 512×512 PNG")


if __name__=="__main__":
    main()
