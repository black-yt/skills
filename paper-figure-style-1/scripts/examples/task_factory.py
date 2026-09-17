"""示例需求：为自动评测任务生成方法画流程图，展示模板适配、候选任务和七类覆盖范围。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example


VOCABULARY=[("Retrieval","folder",P.rust),("Analysis","search",P.purple),
            ("Reasoning","network",P.rust),("Robustness","shield",P.purple),
            ("Synthesis","layers",P.rust),("Calibration","target",P.purple),
            ("Generation","code",P.purple)]


def draw(output, **options):
    """Converging inputs, a specialization card, candidate documents and taxonomy strip."""
    f=Figure(output,365,title="Build diverse evaluation tasks from reusable templates",**options)
    f.background()
    for x,y,w,h,color in ((8,54,201,163,P.lavender),(246,54,239,163,P.lavender),(510,54,204,203,P.peach)):
        f.zone(x,y,w,h,color)
    f.header("Build diverse evaluation tasks from reusable templates")
    f.box(510,54,204,203,fill=None,stroke=P.rust)
    for y,icon,title,detail,color,tint in (
        (67,"document","Task templates","Reusable procedures",P.purple,P.lavender),
        (145,"cube","Domain context","Data · rules · checks",P.rust,P.peach)):
        f.box(14,y,187,62,fill=tint)
        f.icon(icon,34,y+29,size=16,color=color)
        f.text(54,y+23.04,title)
        f.text(54,y+44.04,detail,color=P.muted)
    f.polyline([(202,98),(224,98),(224,176),(202,176)],color=P.border,width=.85)
    f.arrow([(224,137),(250,137)],width=.9)
    f.icon("robot",279,70,size=15)
    f.text(298,74.31,"Template adaptation",size=12)
    f.arrow([(365,83),(365,97)],width=.9)
    f.box(254,100,223,107,fill=P.lavender,stroke=P.purple)
    f.text(365.5,122.31,"Domain-specific task builder",size=12,align="center")
    f.line((264,133),(467,133),color=P.border,width=.7)
    for y,icon,text in ((153.04,"search","Domain vocabulary"),(175.04,"code","Controlled perturbations"),(197.04,"layers","Seeded task expansion")):
        f.icon(icon,275,y-4,size=12)
        f.text(292,y,text)
    f.arrow([(479,137),(506,137)])
    f.text(612,74.31,"Candidate tasks",size=12,align="center")
    for x,y,icon,color in ((520,96,"code",P.purple),(564,88,"pencil",P.rust),(608,96,"flask",P.purple)):
        f.box(x+4,y-4,83,60,fill="#FAFAFC",line_width=.6)
        f.box(x,y,83,60,line_width=.6)
        f.icon(icon,x+18,y+19,size=13,color=color)
        for dy,length in ((33,38),(42,54),(51,36)):
            f.line((x+14,y+dy),(x+14+length,y+dy),color=P.border,width=.65)
    f.text(612,178.04,"Pending quality review",align="center",color=P.muted)
    f.arrow([(612,188),(612,211)])
    f.box(517,214,190,36,fill=P.peach)
    f.icon("shield",537,231,size=13,color=P.rust)
    f.text(555,235.04,"Quality validation")
    f.text(14,263.31,"Task coverage vocabulary",size=12)
    f.line((14,274),(707,274),color=P.border,width=.7)
    for i,(label,icon,color) in enumerate(VOCABULARY):
        x=14+100*i
        f.box(x,288,93,58,fill=P.peach if color==P.rust else P.lavender)
        f.icon(icon,x+46.5,307,size=15,color=color)
        f.text(x+46.5,334.04,label,align="center",max_width=92)
    return f.save()


if __name__=="__main__":
    run_example(draw,"task_factory")
