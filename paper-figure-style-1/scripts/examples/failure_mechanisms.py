"""示例需求：用成组横条统计失败原因，再用任务卡和轨迹流程解释重复出现的修复错误。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import Axes, COLORS, legend_item, footer


CATEGORIES = [("Reference-convention","mismatch"),("Wrong repair target",),("Incomplete restoration",),
              ("Incomplete delivery",),("Unresolved numerical","mismatch")]
PLANNING = [65,12,9,5,9]
SEARCH = [59,18,4,3,16]


def draw(output, **options):
    f=Figure(output,615,title="Failure mechanisms in paired repair trajectories",**options)
    f.background()
    f.header("Failure mechanisms in paired repair trajectories")
    f.text(24,63,"(a) Attributed share of failures",size=12)
    f.text(24,82,"One primary cause per failed run",size=10,color=P.muted)
    legend_item(f,470,63,"Planning",COLORS[0])
    legend_item(f,588,63,"Search",COLORS[1])
    axis=Axes(f,222,95,451,139,(0,80),(-.5,4.5))
    if sum(PLANNING)!=100 or sum(SEARCH)!=100:
        raise ValueError("Failure category shares must sum to 100% within each method")
    for i,(category,a,b) in enumerate(zip(CATEGORIES,PLANNING,SEARCH)):
        yy=4-i
        baseline=axis.sy(yy)
        f.lines(24,baseline+(0 if len(category)>1 else 3),category,size=11,leading=12)
        for offset,value,color in ((.19,a,COLORS[0]),(-.19,b,COLORS[1])):
            axis.hbar(yy+offset,value,height=.26,color=color,endpoint=False)
            f.text(axis.sx(value)+5,axis.sy(yy+offset)+3,f"{value:.1f}%",size=10)
    f.text(24,273,"(b) Different defects, the same wrong repair",size=12)
    cases=[("Task 014","Unit conversion","3 attempts"),("Task 027","Boundary condition","4 attempts"),
           ("Task 041","Normalization","2 attempts")]
    for i,(task,label,count) in enumerate(cases):
        x=24+230*i
        f.box(x,290,212,62,fill=P.white,alpha=.45,radius=6)
        f.text(x+106,307,task,size=10,align="center",color=P.muted)
        f.text(x+106,327,label,size=12,align="center")
        f.text(x+106,344,count,size=10,align="center")
        f.line((x+106,352),(x+106,366),color=P.rust)
    f.line((130,366),(590,366),color=P.rust)
    f.arrow([(360,366),(360,377)],color=P.rust)
    f.box(150,380,420,48,fill=P.white,alpha=.6,stroke=P.rust,radius=5)
    f.text(360,398,"Shared non-target edit",size=12,align="center")
    f.text(360,417,"Change output scaling while leaving the defect intact",size=10,align="center")
    f.text(360,448,"9 of 21 wrong-target attempts across 3 tasks",size=11,align="center")
    f.line((24,459),(696,459),color=P.border,width=.6)
    f.text(24,479,"Task 041 · two repair paths",size=11)
    for j,(tag,steps,color) in enumerate([
        ("Path A",[("Non-target edit","output adapter"),("Candidate tests","pass"),("Independent check","fails")],P.rust),
        ("Path B",[("Targeted repair","normalizer"),("Candidate tests","pass"),("Independent check","passes")],P.purple)]):
        y=489+j*45
        f.text(26,y+22,tag,size=10)
        for i,lines in enumerate(steps):
            x=112+i*200
            f.box(x,y,182,37,fill=P.white,alpha=.45,radius=5)
            f.lines(x+91,y+15,lines,size=10.5,leading=13,align="center")
            if i<2:
                f.arrow([(x+184,y+18),(x+197,y+18)],color=color)
    footer(f)
    return f.save()


if __name__=="__main__":
    run_example(draw,"failure_mechanisms")
