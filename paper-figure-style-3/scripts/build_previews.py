"""Make public contact sheets from PNGs exported by the draw.io renderer."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]


def font(size,bold=False):
    try:return ImageFont.truetype("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",size)
    except OSError:return ImageFont.load_default(size=size)


def sheet(source,destination,items,heading):
    width=1640;padding=28
    figures=[]
    for number,label in items:
        image=Image.open(source/f"figure-{number}.png").convert("RGB")
        height=round(image.height*(width-2*padding)/image.width)
        figures.append((number,label,image.resize((width-2*padding,height),Image.Resampling.LANCZOS)))
    height=105+sum(im.height+64 for _,_,im in figures)+47
    canvas=Image.new("RGB",(width,height),"#F6F8FA")
    draw=ImageDraw.Draw(canvas)
    draw.text((padding,20),"PAPER FIGURE STYLE 3 · DRAW.IO",font=font(19,True),fill="#356D91")
    draw.text((padding,52),heading,font=font(31,True),fill="#29313B")
    y=105
    for number,label,image in figures:
        draw.rounded_rectangle((padding-3,y,width-padding+3,y+image.height+48),radius=12,fill="white",outline="#CBD3DC",width=1)
        draw.text((padding+14,y+12),f"{number:02d}  {label}",font=font(19,True),fill="#5C6573")
        canvas.paste(image,(padding,y+44))
        y+=image.height+64
    draw.text((padding,y+2),"Native draw.io cells · Tabler icons by Paweł Kuna (MIT) · Figure 3/4 data transcribed from paper labels",font=font(13),fill="#707887")
    destination.parent.mkdir(parents=True,exist_ok=True)
    canvas.save(destination,optimize=True)
    print(destination)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir",type=Path,default=ROOT/"outputs")
    parser.add_argument("--output-dir",type=Path,default=ROOT/"assets/previews")
    args=parser.parse_args()
    sheet(args.input_dir,args.output_dir/"01_method_figures.png",[(1,"Complementary learning analogy"),(2,"LatentEvolve method architecture")],"Editable method figures")
    sheet(args.input_dir,args.output_dir/"02_data_figures.png",[(3,"Day/night performance trajectories"),(4,"Ablation and latent-length sensitivity")],"Editable scientific charts")


if __name__=="__main__":main()
