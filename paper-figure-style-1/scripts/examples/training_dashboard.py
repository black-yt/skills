"""示例需求：用两行五列的仪表盘展示两个实验的逐步训练指标，以及训练前后的留出集表现。"""
from pathlib import Path
import sys
from random import Random
from math import sin
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import Axes, marker, legend_item, footer


def training_trace(seed,second=False):
    """Deterministic synthetic per-step traces, drawn without smoothing."""
    rng=Random(seed)
    steps=list(range(1,31))
    reward=[.32+(.008 if second else .017)*i+rng.uniform(-.06,.06) for i in steps]
    completed=[min(.98,v+.13+rng.uniform(-.025,.025)) for v in reward]
    truncation=[max(2,(34-.35*i if second else 44-1.25*i)+rng.uniform(-5,5)) for i in steps]
    tokens=[(780+4*i if second else 1090+2*i)+rng.uniform(-60,60) for i in steps]
    entropy=[.66-.008*i+.035*sin(i)+rng.uniform(-.025,.025) for i in steps]
    return steps,[reward,completed,truncation,tokens,entropy]


def draw(output, **options):
    f=Figure(output,494,title="Training dynamics with verified feedback",**options)
    f.background()
    f.header("Training dynamics with verified feedback")
    for row,(dataset,detail,before,after) in enumerate([
        ("(a) Data repair","96 training / 24 held-out tasks",.34,.82),
        ("(b) Tool planning","80 training / 20 held-out tasks",.29,.59)]):
        top=70+row*197
        f.text(15,top-13,dataset,size=11,bold=True)
        f.text(158,top-13,detail,size=9.5,color=P.muted)
        steps,values=training_trace(31+row,second=bool(row))
        configs=[("Training reward",(0,1),(0,.5,1),[values[0],values[1]]),
                 ("Truncation (%)",(0,50),(0,20,40),[values[2]]),
                 ("Tokens per turn",((650,1050) if row else (950,1250)),((700,850,1000) if row else (1000,1100,1200)),[values[3]]),
                 ("Entropy",(.25,.75),(.3,.5,.7),[values[4]]),
                 ("Held-out reward",(0,1),(0,.5,1),[])]
        for col,(title,limits,ticks,series) in enumerate(configs):
            x=13+col*141
            f.box(x,top,134,172,fill=P.white,alpha=.3,stroke=P.border,radius=5)
            f.text(x+9,top+16,title,size=10,bold=True,max_width=121)
            axis=Axes(f,x+29,top+44,95,98,(0,31) if col<4 else (-.35,1.35),limits)
            axis.frame(xticks=(1,10,20,30) if col<4 else (0,1),yticks=ticks,
                       xformat=(lambda v:f"{v:g}") if col<4 else (lambda v:"Base" if v==0 else "Tuned"),size=8)
            if col==0:
                legend_item(f,x+35,top+29,"All",P.purple,size=7.8)
                legend_item(f,x+75,top+29,"Done",P.rust,dash=(2,2),size=7.8)
            for k,ys in enumerate(series):
                color=P.purple if k==0 else P.rust
                axis.series(steps,ys,color=color,width=.55,dash=(2,2) if k else None)
                for step,value in zip(steps,ys):
                    axis.dot(step,value,color=color,radius=1.2,shape="diamond" if k else "circle")
            if col==4:
                f.line(axis.point(0,before),axis.point(1,after),color=P.purple,width=1.25)
                for t,value,color,dy in ((0,before,P.rust,14),(1,after,P.purple,-7)):
                    axis.dot(t,value,color=color,radius=2.7)
                    px,py=axis.point(t,value)
                    f.text(px,py+dy,f"{value:.2f}",size=9,color=color,align="center")
            f.text(x+77,top+164,"Training step" if col<4 else "Same held-out set",size=8,align="center",color=P.muted)
    footer(f,detail="Every step shown · no smoothing")
    return f.save()


if __name__=="__main__":
    run_example(draw,"training_dashboard")
