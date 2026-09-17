"""示例需求：为检索增强系统画架构图，展示知识源、可选模块和四个可验证的系统能力。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example


def draw(output, **options):
    """Three-zone architecture with an expert input and a 2 × 2 capability panel."""
    f=Figure(output,365,title="A modular retrieval system with verifiable outputs",**options)
    f.background()
    f.zone(10,47,153,207,P.peach)
    f.zone(196,47,175,207)
    f.header("A modular retrieval system with verifiable outputs")
    for x,right,label in ((16,151,"Collect"),(205,361,"Select modules"),(404,696,"Build the system")):
        f.text(x,62.31,label,size=12)
        f.line((x,73),(right,73),color=P.border,width=.85)
    f.box(16,94,137,116,fill=P.peach)
    f.icon("folder",84,118,size=23,color=P.rust)
    f.text(84.5,151.31,"Knowledge sources",size=12,align="center")
    f.lines(84.5,174.8,["Papers and notes","Versioned snapshots"],color=P.muted,align="center",leading=12.48)
    f.text(10.97,240.04,"Shared data and interfaces",color=P.muted)
    f.line((153,152),(180,152),color=P.purple)
    f.line((180,103.5),(180,213.5),color=P.border)
    for y,label in ((81,"Sparse retrieval"),(136,"Dense retrieval"),(191,"Hybrid retrieval")):
        selected=label=="Dense retrieval"
        color=P.purple if selected else P.muted
        f.arrow([(180,y+22.5),(202,y+22.5)],color=color,width=.8)
        f.box(205,y,156,45,fill=P.lavender if selected else P.white,stroke=P.purple if selected else P.border)
        f.icon("cube",222,y+22.5,size=13,color=color)
        f.text(239,y+25.54,label)
    f.arrow([(363,158.5),(390,158.5)],width=.9)
    f.box(16,274,345,63,fill=P.peach)
    f.icon("expert",39,304,size=17,color=P.rust)
    f.text(61,298.31,"Domain-aware configuration",size=12)
    f.text(61,319.04,"Corpus scope · retrieval policy · quality targets",color=P.muted)
    f.arrow([(283,272),(283,240)],color=P.rust)
    f.box(393,81,315,256,fill=P.lavender,stroke=P.purple)
    f.text(550.5,99.31,"Retrieval workspace",size=12,align="center")
    f.line((403,109),(698,109),color=P.border,width=.7)
    cards=[
        (403,115,"flask",P.rust,"Index builder",["Chunking and","embeddings"]),
        (555,115,"shield",P.rust,"Quality checks",["Coverage and","groundedness"]),
        (403,218,"workspace",P.purple,"Query engine",["Retrieval and","answer synthesis"]),
        (555,218,"cube",P.purple,"Private test set",["Held-out queries","and references"]),
    ]
    for x,y,icon,color,title,details in cards:
        f.box(x,y,143,88)
        f.icon(icon,x+71.5,y+17,size=14,color=color)
        f.text(x+71.5,y+43.31,title,size=12,align="center")
        f.lines(x+71.5,y+63.8,details,align="center",color=P.muted,leading=12.48)
    return f.save()


if __name__=="__main__":
    run_example(draw,"system_architecture")
