"""示例需求：展示统一实验接口如何产生可验证记录，供模型比较、监督学习和策略优化复用。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example


def draw(output, **options):
    """Two sources converge into an episode; a shared bus fans out to three uses."""
    f=Figure(output,370,title="One evaluation interface, multiple research workflows",**options)
    f.background()
    f.zone(8,48,704,117,"#F7F4F9")
    f.zone(8,264,704,75)
    f.header("One evaluation interface, multiple research workflows")
    top=[(14,"workspace",P.purple,P.lavender,"Experiment workspace", "Code · datasets · candidate outputs","Prepare → run → inspect → revise"),
         (409,"shield",P.rust,P.peach,"Independent evaluation","Held-out data · acceptance criteria","Score reproducible outputs")]
    for x,icon,color,tint,title,detail,sub in top:
        f.box(x,57,297,100,fill=tint,stroke=color)
        f.icon(icon,x+24,80,size=19,color=color)
        f.text(x+47,83.31,title,size=12)
        f.text(x+15,110.04,detail)
        f.text(x+15,133.04,sub,color=P.muted)
    f.text(360,95.04,"Delivery",align="center")
    f.arrow([(315,109),(405,109)],color=P.rust)
    f.arrow([(161,161),(161,171),(262,171),(262,180)])
    f.arrow([(558,161),(558,171),(458,171),(458,180)],color=P.rust)
    f.box(189,185,342,56)
    f.icon("document",210,201,size=16)
    f.text(231,205.31,"Verified experiment record",size=12)
    f.text(204,229.04,"Artifacts · metrics · status · compute cost",color=P.muted)
    f.line((360,245),(360,254),width=.9)
    f.line((120,254),(600,254),width=.9)
    for cx in (120,360,600): f.arrow([(cx,254),(cx,266)])
    cards=[(14,"bars",P.rust,"Model comparison","Held-out tasks · fixed budgets"),
           (254,"layers",P.purple,"Supervised learning","Curated successful examples"),
           (494,"target",P.purple,"Policy optimization","Feedback-driven exploration")]
    for x,icon,color,title,detail in cards:
        f.box(x,271,212,60)
        f.icon(icon,x+17,285,size=14,color=color)
        f.text(x+34,289.31,title,size=12)
        f.text(x+12,322.04,detail,color=P.muted,max_width=196)
    f.text(360,356.04,"Keep the evaluation contract stable as models and methods change.",align="center",color=P.muted)
    return f.save()


if __name__=="__main__":
    run_example(draw,"learning_loop")
