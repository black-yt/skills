"""示例需求：为论文画五阶段研究流程，从研究问题到可信证据，区分每阶段输入和产物。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from icons import pipeline_illustration


STAGES = [
    dict(title=["Research","question"], detail=["Scope and claims","Prior evidence"],
         footer="Study brief", icon="repository", color=P.blue, tint="#EDF2F8"),
    dict(title=["Data curation","and protocols"],detail=["Source selection","Quality policies"],
         footer="Curated inputs",icon="package",color=P.rust,tint="#FAF0E9"),
    dict(title=["Model design","and adaptation"],detail=["Reusable methods","Task-specific rules"],
         footer="Model recipes",icon="recipe",color=P.purple,tint="#F0EDFA"),
    dict(title=["Evaluation","and validation"],detail=["Held-out tasks","Reliability checks"],
         footer="Verified results",icon="validation",color=P.green,tint="#EDF4ED"),
    dict(title=["Analysis","and release"],detail=["Error analysis","Reproducible runs"],
         footer="Open artifacts",icon="interaction",color=P.purple,tint="#F0EDFA"),
]


def draw(output, **options):
    """Five-stage pipeline with numbered cards, semantic accents and native gradient."""
    f=Figure(output,294,title="From research question to reliable evidence",**options)
    f.background()
    f.header("From research question to reliable evidence",brand="RESEARCH")
    for i,stage in enumerate(STAGES):
        x=14+142*i
        cx=x+62
        f.box(x,54,124,224,radius=7,stroke="#DDCDBF" if i<2 else "#D0C9E1",line_width=.85)
        f.circle(x+17,72,9,stroke=stage["color"],fill=P.white,width=.8)
        f.text(x+17,76,str(i+1),size=11,align="center")
        f.line((x+34,72),(x+110,72),color=P.border,width=.65)
        f.lines(cx,100.16,stage["title"],size=12,align="center",leading=14.0,max_width=122)
        pipeline_illustration(f,stage["icon"],cx,163)
        f.lines(cx,211.39,stage["detail"],size=11,align="center",color=P.muted,leading=13.42)
        f.box(x+8,241,108,25,fill=stage["tint"],stroke=None,radius=2)
        f.text(cx,257.60,stage["footer"],size=11,align="center",max_width=107)
        if i<4:
            f.arrow([(x+126,162),(x+139,162)],color=P.rust if i==0 else P.purple,width=1.05)
    return f.save()


if __name__=="__main__":
    run_example(draw,"research_pipeline")
