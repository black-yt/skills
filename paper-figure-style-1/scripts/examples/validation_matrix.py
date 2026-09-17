"""示例需求：画一张任务质量控制图，明确参考解、扰动解和运行故障的不同判定。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example


def status(f,x,y,label,kind):
    color={"check":P.purple,"cross":P.rust,"minus":P.muted}[kind]
    f.circle(x,y-4,6,stroke=color,fill=P.white,width=.65)
    f.icon(kind,x,y-4,size=9,color=color)
    f.text(x+12,y,label)


def draw(output, **options):
    """Readable vector evidence table; status icons complement text labels."""
    f=Figure(output,350,title="Validate generated tasks with executable evidence",**options)
    f.background()
    f.zone(172,48,364,188,P.peach)
    f.zone(8,241,704,99)
    f.header("Validate generated tasks with executable evidence")
    for x,text in ((14,"Task proposal"),(179,"Evidence collected by the validator"),(552,"Reproducible task")):
        f.text(x,62.31,text,size=12)
    f.box(14,76,142,153,fill=P.lavender,stroke=P.purple)
    f.icon("code",85,106,size=25)
    f.lines(85,142.04,["Controlled change","+ expected behavior"],align="center",leading=17)
    f.line((30,176),(140,176),color=P.border,width=.7)
    f.text(85,204.04,"Pending checks",color=P.muted,align="center")
    f.arrow([(159,152),(175,152)])
    f.box(179,76,350,153)
    for x,text in ((192,"Test case"),(345,"Execution"),(437,"Quality")):
        f.text(x,97.1,text,color=P.muted)
    for y in (109,149,187): f.line((192,y),(516,y),color=P.border,width=.65)
    for x in (331,420): f.line((x,83),(x,218),color=P.border,width=.65)
    rows=[("Reference solution",133.1,"Runs","check","Passes","check"),
          ("Perturbed solution",172.1,"Runs","check","Fails","cross"),
          ("Runtime failure",211.1,"Error","cross","Ungraded","minus")]
    for label,y,a,ka,b,kb in rows:
        f.text(192,y,label)
        status(f,344,y,a,ka)
        status(f,434,y,b,kb)
    f.arrow([(532,152),(548,152)],color=P.rust)
    f.box(552,76,154,153,fill=P.peach,stroke=P.rust)
    f.icon("shield",629,103,size=26,color=P.rust)
    for y,text in ((142.04,"Solvable objective"),(162.1,"Measurable contrast"),(181.1,"Versioned reference")):
        f.text(629,y,text,align="center")
    f.text(629,207.76,"Verified before use",size=10,color=P.muted,align="center")
    f.text(14,252.31,"After validation: estimate difficulty and refine the task pool",size=12)
    for i,(x,icon,title,detail) in enumerate(((14,"robot","Pilot runs","Outcomes + trajectories"),
                   (255,"bars","Observed difficulty","Model · tools · budget"),
                   (497,"refresh","Task refinement","Revise rules and coverage"))):
        f.box(x,268,209,64)
        f.icon(icon,x+17,282,size=13)
        f.text(x+34,286.31,title,size=12)
        f.text(x+12,323.04,detail,color=P.muted)
        if i<2: f.arrow([(x+212,300),(x+237,300)])
    return f.save()


if __name__=="__main__":
    run_example(draw,"validation_matrix")
