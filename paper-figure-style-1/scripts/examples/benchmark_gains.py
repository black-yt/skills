"""示例需求：展示训练前后的多基准结果，用表内增益条和带区间的森林图表达收益与退化。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import gain_table, forest, footer


CORE = [
    dict(model="Cedar Core",benchmark="LabTasks",n=240,before=28.4,after=41.6),
    dict(model="Cedar Core",benchmark="CodeChecks",n=320,before=31.7,after=43.1),
    dict(model="Cedar Pro",benchmark="LabTasks",n=240,before=43.8,after=55.4),
    dict(model="Cedar Pro",benchmark="CodeChecks",n=320,before=49.5,after=58.6),
    dict(model="Iris Plus",benchmark="LabTasks",n=240,before=22.1,after=32.8),
    dict(model="Iris Plus",benchmark="CodeChecks",n=320,before=25.6,after=34.7),
]
TRANSFER = [
    dict(model="Cedar Core",benchmark="DataRepair",n=180,before=33.2,after=39.6),
    dict(model="Cedar Core",benchmark="ToolBench",n=200,before=41.3,after=46.8),
    dict(model="Cedar Pro",benchmark="DataRepair",n=180,before=52.4,after=59.2),
    dict(model="Iris Plus",benchmark="ToolBench",n=200,before=30.7,after=34.2),
]
EFFECTS = [
    dict(label="Structured data",value=12.4,low=8.4,high=16.4),
    dict(label="Simulation tasks",value=10.6,low=6.2,high=15.0),
    dict(label="Model debugging",value=7.2,low=3.5,high=10.9),
    dict(label="Tool planning",value=4.8,low=1.1,high=8.5),
    dict(label="Long-context reading",value=1.2,low=-2.4,high=4.8),
    dict(label="Open-domain retrieval",value=-2.1,low=-5.3,high=1.1),
    dict(label="Exact formatting",value=-4.2,low=-7.1,high=-1.3),
]


def draw(output, **options):
    f=Figure(output,768,title="Adaptation improves task performance",**options)
    f.background()
    f.header("Adaptation improves task performance")
    gain_table(f,13,49,694,CORE,title="(a) In-domain evaluation",max_gain=16)
    gain_table(f,13,271,694,TRANSFER,title="(b) Transfer to held-out benchmarks",max_gain=16)
    f.box(13,445,694,274,fill=P.white,alpha=.5,stroke=P.border,radius=7)
    f.text(26,468,"(c) Where the gains concentrate",size=12,bold=True)
    f.text(26,488,"Absolute success-rate change after adaptation",size=10,color=P.muted)
    forest(f,27,506,661,EFFECTS,limits=(-10,20),ticks=(-10,0,10,20))
    f.text(439,704,"Change in success (percentage points)",size=10,align="center")
    footer(f,detail="Intervals: illustrative bounds")
    return f.save()


if __name__=="__main__":
    run_example(draw,"benchmark_gains")
