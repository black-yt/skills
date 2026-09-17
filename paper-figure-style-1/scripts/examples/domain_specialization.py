"""示例需求：比较研究助手在四个任务领域的能力，并显示各方法相对指定参考方法的额外覆盖。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import bar_matrix, footer
from demo_data import METHODS


DOMAINS = [
    ("Data repair",40,[81,77,79,73,54,51,47,41,36,39,33,28,25,4,6]),
    ("Simulation",32,[63,65,48,50,30,26,29,20,24,31,28,17,26,9,4]),
    ("Model checks",24,[42,46,38,28,19,34,6,33,36,2,3,39,2,5,6]),
    ("Tool planning",20,[78,79,85,39,52,42,35,36,29,11,25,5,10,2,9]),
]


def domain_results():
    """Create feasible per-domain solved sets; derive scores and extra coverage."""
    results=[]
    marginal=[0]*len(METHODS)
    for j,(title,n,values) in enumerate(DOMAINS):
        counts=[round(n*v/100) for v in values]
        reference=set(range(counts[0]))
        sets=[]
        for i,count in enumerate(counts):
            extra=0 if i==0 else min(count,n-counts[0],(i+j)%3)
            inside=min(count-extra,len(reference))
            extra=count-inside
            solved=set(range(inside))|set(range(counts[0],counts[0]+extra))
            if len(solved)!=count or not solved<=set(range(n)):
                raise ValueError("Invalid synthetic task set")
            sets.append(solved)
            marginal[i]+=len(solved-reference)
        results.append((title,n,[100*len(s)/n for s in sets]))
    return results,marginal


def draw(output, **options):
    f=Figure(output,457,title="Domain specialization and complementary coverage",**options)
    f.background()
    f.header("Domain specialization and complementary coverage")
    columns=[]
    results,marginal=domain_results()
    for title,n,scores in results:
        columns.append(dict(title=[title,f"n = {n}"],maximum=100,
                            values=[dict(value=v,low=max(0,v-4),high=min(100,v+4)) for v in scores],
                            format=lambda v:f"{v:g}%" if v else "0"))
    columns.append(dict(title=["Beyond Atlas Pro","single demo run"],maximum=8,values=marginal,show_values=True))
    bar_matrix(f,14,54,692,[m["name"] for m in METHODS],columns,[m["color"] for m in METHODS],row_height=18,label_width=147)
    f.text(19,406,"Domain success (%), illustrative bounds; right column counts additional solved tasks.",size=9.5,color=P.muted)
    footer(f)
    return f.save()


if __name__=="__main__":
    run_example(draw,"domain_specialization")
