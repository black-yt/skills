"""Render eight finished example PDFs into two distributable 2-by-2 PNG sheets.

The PDFs remain the publication artifacts. These sheets are browsing previews,
with aspect ratios preserved and complete pages visible. Prefer pdftoppm when
available; fall back to the skill's existing PyMuPDF dependency otherwise.
"""
from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import shutil
import subprocess
import tempfile

from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
import pymupdf


ROOT = Path(__file__).resolve().parents[1]
SHEETS = (
    ("01_methods_and_coverage.png", "Methods, systems & task coverage", (
        ("research_pipeline", "01", "Research workflow"),
        ("system_architecture", "02", "System architecture"),
        ("resource_runtime", "03", "Resource runtime"),
        ("coverage_overview", "04", "Task coverage"),
    )),
    ("02_evaluation_and_training.png", "Evaluation & training statistics", (
        ("model_leaderboard", "05", "Model leaderboard with logos"),
        ("budget_profiles", "06", "Budget-response curves"),
        ("efficiency_frontier", "07", "Efficiency and Pareto frontiers"),
        ("training_dashboard", "08", "Training dashboard"),
    )),
)


def render_page(pdf, width, renderer):
    """Render exactly one full page at a known pixel width, without cropping."""
    with pymupdf.open(pdf) as doc:
        if len(doc)!=1:
            raise ValueError(f"Expected a single-page example: {pdf.name}")
        if renderer=="pymupdf":
            page=doc[0]
            pix=page.get_pixmap(matrix=pymupdf.Matrix(width/page.rect.width,width/page.rect.width),alpha=False)
            return Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
    result=subprocess.run(
        ["pdftoppm","-f","1","-l","1","-singlefile","-scale-to-x",str(width),
         "-scale-to-y","-1","-png",str(pdf)],
        check=True,capture_output=True,
    )
    with Image.open(BytesIO(result.stdout)) as image:
        return image.convert("RGB")


def font(size, *, bold=False):
    path=font_manager.findfont(font_manager.FontProperties(
        family="DejaVu Sans",weight="bold" if bold else "normal"),fallback_to_default=False)
    return ImageFont.truetype(path,size)


def compose(title,panels,images,width):
    # All dimensions follow the requested tile width so labels stay proportional.
    unit=width/1440
    px=lambda v:round(v*unit)
    margin,gap,padding,label_h=px(40),px(28),px(12),px(54)
    header,footer=px(116),px(64)
    card_w=width+2*padding
    row_heights=[max(images[i].height for i in (row*2,row*2+1))+label_h+2*padding
                 for row in range(2)]
    canvas=Image.new("RGB",(2*margin+2*card_w+gap,
                             header+sum(row_heights)+gap+footer),"#FAF9FC")
    draw=ImageDraw.Draw(canvas)
    draw.text((margin,px(20)),"PAPER FIGURE STYLE 1",font=font(px(18),bold=True),fill="#584B9A")
    draw.text((margin,px(50)),title,font=font(px(31),bold=True),fill="#16151C")
    draw.text((canvas.width-margin,px(61)),"EXAMPLE PREVIEWS  /  2 × 2",
              font=font(px(17)),fill="#5C5C66",anchor="rt")
    y=header
    for row,row_h in enumerate(row_heights):
        for col in range(2):
            i=row*2+col
            x=margin+col*(card_w+gap)
            draw.rounded_rectangle((x,y,x+card_w,y+row_h),radius=px(14),
                                   fill="#FFFFFF",outline="#DAD5E2",width=px(2))
            _,number,label=panels[i]
            draw.text((x+padding+px(8),y+px(16)),number,font=font(px(19),bold=True),fill="#584B9A")
            draw.text((x+padding+px(51),y+px(16)),label,font=font(px(19)),fill="#5C5C66")
            image=images[i]
            top=y+label_h+padding+(row_h-label_h-2*padding-image.height)//2
            canvas.paste(image,(x+padding+(width-image.width)//2,top))
        y+=row_h+gap
    draw.text((margin,canvas.height-px(37)),"Rendered from the example PDFs · full pages, original aspect ratios",
              font=font(px(17)),fill="#5C5C66")
    draw.text((canvas.width-margin,canvas.height-px(37)),"Statistical values are illustrative",
              font=font(px(17)),fill="#5C5C66",anchor="rt")
    return canvas


def build(pdf_dir,output_dir, *, tile_width=1440,renderer="auto"):
    if not 720<=tile_width<=2400:
        raise ValueError("tile_width must be between 720 and 2400 pixels")
    if renderer not in ("auto","pdftoppm","pymupdf"):
        raise ValueError("renderer must be auto, pdftoppm or pymupdf")
    if renderer=="auto":
        renderer="pdftoppm" if shutil.which("pdftoppm") else "pymupdf"
    if renderer=="pdftoppm" and not shutil.which("pdftoppm"):
        raise RuntimeError("pdftoppm is unavailable; use --renderer pymupdf")
    missing=[stem+".pdf" for _,_,panels in SHEETS for stem,_,_ in panels
             if not (pdf_dir/(stem+".pdf")).is_file()]
    if missing:
        raise FileNotFoundError("Missing example PDFs: "+", ".join(missing)+
                                ". Run scripts/render_examples.py first.")
    output_dir.mkdir(parents=True,exist_ok=True)
    # Finish both sheets before replacing the published previews.
    with tempfile.TemporaryDirectory(prefix=".preview-build-",dir=output_dir) as temporary:
        generated=[]
        for filename,title,panels in SHEETS:
            images=[render_page(pdf_dir/(stem+".pdf"),tile_width,renderer) for stem,_,_ in panels]
            sheet=compose(title,panels,images,tile_width)
            staged=Path(temporary)/filename
            sheet.save(staged,format="PNG",optimize=True)
            generated.append((staged,output_dir/filename))
        for staged,target in generated:
            staged.replace(target)
            print(f"{target} ({target.stat().st_size//1024} KiB; {renderer})")
    return [target for _,target in generated]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir",type=Path,default=ROOT/"outputs")
    parser.add_argument("--output-dir",type=Path,default=ROOT/"assets/previews")
    parser.add_argument("--tile-width",type=int,default=1440,help="Pixel width of each full-page example (720–2400)")
    parser.add_argument("--renderer",choices=("auto","pdftoppm","pymupdf"),default="auto")
    args=parser.parse_args()
    build(args.pdf_dir,args.output_dir,tile_width=args.tile_width,renderer=args.renderer)


if __name__=="__main__":
    main()
