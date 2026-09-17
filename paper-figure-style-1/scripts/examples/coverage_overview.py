"""示例需求：用双环图展示任务类别及其子领域构成，并在同页给出研究助手的成功率概览。"""
from pathlib import Path
import sys
from math import pi,cos,sin
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import Axes, nested_donut, footer
from demo_data import METHODS


GROUPS = [
    dict(label="Repair",color="#D6C8E7",children=[dict(label="Tables",value=280,color="#BAB0D6"),dict(label="Documents",value=200,color="#D3B8CE")]),
    dict(label="Planning",color="#C6DCCA",children=[dict(label="Search",value=210,color="#A9CBAF"),dict(label="Scheduling",value=150,color="#BAD8C7")]),
    dict(label="Discovery",color="#BDD5E3",children=[dict(label="Materials",value=240,color="#97B6D4"),dict(label="Molecules",value=180,color="#B4C8DB")]),
    dict(label="Reproduce",color="#E7C7D7",children=[dict(label="Vision",value=160,color="#D6AABE"),dict(label="Language",value=140,color="#DAB8D5")]),
    dict(label="Integrate",color="#DDDFC0",children=[dict(label="Sensors",value=150,color="#C2C49C"),dict(label="Robotics",value=150,color="#D2D5AD")]),
    dict(label="Calibrate",color="#F0D6AC",children=[dict(label="Climate",value=190,color="#EAC48F"),dict(label="Dynamics",value=170,color="#E2CBAA")]),
    dict(label="Optimize",color="#C5DEDA",children=[dict(label="Solvers",value=100,color="#A9C9C2"),dict(label="Compilers",value=80,color="#BED0CC")]),
]


def draw(output, **options):
    f=Figure(output,540,title="Task coverage and research assistant capability",**options)
    f.background()
    f.header("Task coverage and research assistant capability")
    f.text(18,64,"(a) A reusable task collection",size=12,bold=True)
    f.text(18,83,"7 task types · 14 subdomains",size=10,color=P.muted)
    f.text(373,64,"(b) Evaluation snapshot",size=12,bold=True)
    f.text(373,83,"Same methods as the leaderboard demo",size=10,color=P.muted)
    total,segments=nested_donut(f,234,208,GROUPS,inner=44,split=74,outer=103)
    f.text(234,208,f"{total:,}",size=18,bold=True,align="center")
    f.text(234,225,"demo tasks",size=10,align="center",color=P.muted)
    for i,segment in enumerate(segments):
        f.circle(segment["x"],segment["y"],5,stroke=None,fill=P.white)
        f.text(segment["x"],segment["y"]+2.7,i+1,size=7.5,align="center")
    a=-pi/2
    for i,group in enumerate(GROUPS):
        count=sum(v["value"] for v in group["children"])
        mid=a+pi*count/total
        x,y=234+58*cos(mid),208+58*sin(mid)
        f.circle(x,y,5.4,stroke=None,fill=P.white)
        f.text(x,y+3,chr(97+i),size=8.5,align="center")
        a+=2*pi*count/total
        yy=145+i*20
        f.circle(29,yy-3,5.5,stroke=group["color"],fill=P.white)
        f.text(29,yy,chr(97+i),size=8.5,align="center")
        f.text(42,yy,group["label"],size=10)
    f.box(15,330,330,162,fill=P.white,alpha=.25,radius=6)
    f.text(25,350,"Subdomains · number of tasks",size=11)
    for i,segment in enumerate(segments):
        col,row=divmod(i,7)
        x,y=25+col*157,372+row*18
        f.circle(x+4,y-3,5,stroke="#D7CCD5",fill=P.white,width=.6)
        f.text(x+4,y,i+1,size=8,align="center")
        f.text(x+15,y,segment["label"],size=9)
        f.text(x+143,y,segment["value"],size=9,align="right")
    f.line((358,99),(358,490),color=P.border,width=.6)
    axis=Axes(f,467,113,207,330,(0,80),(-.5,len(METHODS)-.5))
    for i,m in enumerate(METHODS):
        yy=len(METHODS)-1-i
        f.text(371,axis.sy(yy)+3,m["name"],size=9)
        axis.hbar(yy,m["score"],height=.5,color=m["color"],interval=(m["low"],m["high"]),endpoint=False)
        f.text(axis.sx(m["high"])+5,axis.sy(yy)+3,f"{m['score']:.1f}",size=9)
    axis.frame(xticks=(0,20,40,60,80),xlabel="Task success (%)",size=9)
    footer(f,detail="Bars: illustrative bounds")
    return f.save()


if __name__=="__main__":
    run_example(draw,"coverage_overview")
