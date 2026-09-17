"""示例需求：用双向循环概念图解释实验平台如何积累研究能力，以及这些能力怎样反哺科学实践。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example


def draw(output, **options):
    f=Figure(output,426,title="A shared platform connects learning and discovery",**options)
    f.background()
    f.header("A shared platform connects learning and discovery")
    f.text(20,63,"(a) Build research capability",size=12,bold=True)
    f.text(392,63,"(b) Accelerate scientific practice",size=12,bold=True)
    # Two intertwined cubic loops; cards overlay the paths at each stage.
    for points,color in [
        ([(360,229),(300,157),(278,97),(211,97)],P.purple),
        ([(211,97),(18,60),(17,385),(211,359)],P.purple),
        ([(211,359),(286,349),(305,295),(360,229)],P.rust),
        ([(360,229),(415,163),(434,109),(509,97)],P.rust),
        ([(509,97),(703,60),(702,384),(509,359)],P.rust),
        ([(509,359),(442,359),(421,301),(360,229)],P.purple),
    ]:
        f.curve(points,color=color,width=1.25,arrow_at=.5)
    left=[(147,80,["Environment","construction"],"cube"),
          (15,137,["Task","manufacturing"],"pencil"),
          (15,272,["Verified","trajectory records"],"document"),
          (147,335,["Policy learning","and evaluation"],"target")]
    right=[(438,80,["Evaluation and","leaderboards"],"bars"),
           (570,137,["Scientific","reproducibility"],"refresh"),
           (570,272,["Code repair","and acceleration"],"bolt"),
           (438,335,["Discovery","and new evidence"],"flask")]
    for group,color,start in ((left,P.purple,1),(right,P.rust,5)):
        for i,(x,y,label,icon) in enumerate(group):
            f.box(x,y,135,51,fill=P.white,stroke=color,radius=6)
            f.circle(x+3,y+3,7.5,stroke=P.white,fill=color)
            f.text(x+3,y+6,str(start+i),size=9,color=P.white,align="center")
            f.icon(icon,x+67.5,y+11,size=13,color=color)
            f.lines(x+67.5,y+31,label,size=10,leading=12,align="center")
    f.text(202,218,"LEARNING",size=18,bold=True,align="center")
    f.lines(202,240,["Reusable experience","for better decisions"],size=10,leading=14,align="center")
    f.text(518,218,"DISCOVERY",size=18,bold=True,align="center")
    f.lines(518,240,["Reliable tools","for stronger evidence"],size=10,leading=14,align="center")
    f.box(287,211,146,38,fill=P.purple,stroke="#42366E",radius=15)
    f.text(360,235,"Research platform",size=12,bold=True,color=P.white,align="center")
    f.text(360,409,"Illustrative concept · each cycle produces reusable, verifiable artifacts",size=10,color=P.muted,align="center")
    return f.save()


if __name__=="__main__":
    run_example(draw,"research_cycle")
