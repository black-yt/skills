"""示例需求：按同一方法顺序对齐六种评估指标，分别显示失败类型、时间和重复不稳定性。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import bar_matrix, footer
from demo_data import METHODS


def bounded(values,half,maximum=100):
    return [None if v is None else dict(value=v,low=max(0,v-half),high=min(maximum,v+half)) for v in values]


def draw(output, **options):
    f=Figure(output,457,title="Failure outcomes, runtime and repeat instability",**options)
    f.background()
    f.header("Failure outcomes, runtime and repeat instability")
    solved=[m["score"] for m in METHODS]
    # First four columns form one outcome partition; time and instability do not.
    budget=[2,10,2,5,31,14,6,27,30,9,13,6,17,1,26]
    partial=[19,18,19,21,12,27,27,18,20,31,29,17,27,23,25]
    baseline=[100-a-b-c for a,b,c in zip(solved,budget,partial)]
    percent=lambda v:f"{v:g}%" if v else "0"
    columns=[
        dict(title=["Solved"],maximum=100,values=[dict(value=m["score"],low=m["low"],high=m["high"]) for m in METHODS],format=percent),
        dict(title=["Budget","exhausted"],maximum=100,values=bounded(budget,2),format=percent),
        dict(title=["Partial","credit"],maximum=100,values=bounded(partial,2.5),format=percent),
        dict(title=["At / below","baseline"],maximum=100,values=bounded(baseline,3),format=percent),
        dict(title=["Failed-run","time"],maximum=60,values=bounded([24,39,14,28,54,32,27,46,49,25,35,22,34,9,40],2,60),format=lambda v:f"{v:g}m" if v else "0"),
        dict(title=["Repeat","instability"],maximum=50,values=[None,34,11,38,39,32,34,48,37,29,27,41,35,9,13],format=percent),
    ]
    bar_matrix(f,14,54,692,[m["name"] for m in METHODS],columns,[m["color"] for m in METHODS],row_height=18)
    f.text(19,406,"Outcome shares use all tasks; runtime uses failed runs. — denotes unavailable repeats.",size=9.5,color=P.muted)
    footer(f,detail="Error bars: illustrative bounds")
    return f.save()


if __name__=="__main__":
    run_example(draw,"failure_outcomes")
