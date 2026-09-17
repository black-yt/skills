"""示例需求：同时展示成功率与成本、耗时、输出 token 的关系，突出各自的 Pareto 前沿。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import Axes, pareto_frontier, marker, footer
from demo_data import METHODS


def scatter(axis,key, *, labels=False,offsets=None):
    costs=[m[key] for m in METHODS]
    scores=[m["score"] for m in METHODS]
    front=pareto_frontier(costs,scores)
    axis.f.polyline([axis.point(costs[i],scores[i]) for i in front],color="#9B97A3",width=.9)
    for i,m in enumerate(METHODS):
        axis.dot(m[key],m["score"],color=m["color"],filled=i in front,radius=3)
        px,py=axis.point(m[key],m["score"])
        dx,dy=(offsets or {}).get(i,(7,-6))
        label=m["name"] if labels else str(m["id"])
        axis.f.text(px+dx,py+dy,label,size=9 if labels else 9.5,align="center" if labels else "left")


def draw(output, **options):
    f=Figure(output,525,title="Success, cost and effort reveal different trade-offs",**options)
    f.background()
    f.header("Success, cost and effort reveal different trade-offs")
    f.text(15,55,"One evaluation cohort · three resource views",size=11,color=P.muted)
    f.text(26,80,"(a) Cost versus success",size=12)
    left=Axes(f,54,99,298,287,(.45,11),(0,80),logx=True)
    left.frame(xticks=(.5,1,2,5,10),yticks=(0,25,50,75),xlabel="Estimated USD / task",ylabel="Success (%)")
    offsets={0:(0,-10),1:(0,16),2:(0,-11),3:(0,17),4:(13,-8),5:(-13,-10),6:(10,16),
             7:(0,17),8:(0,-10),9:(0,17),10:(18,17),11:(0,17),12:(5,-10),13:(-7,-18),14:(24,12)}
    scatter(left,"cost",labels=True,offsets=offsets)
    for j,(key,title,label,limit,ticks) in enumerate([
        ("time","(b) Time versus success","Minutes / task",(0,48),(0,10,20,30,40)),
        ("tokens","(c) Output versus success","Output tokens / task (k)",(0,200),(0,50,100,150,200))]):
        y=100+j*180
        f.text(401,y-20,title,size=12)
        axis=Axes(f,425,y,272,112,limit,(0,80))
        axis.frame(xticks=ticks,yticks=(0,35,70),xlabel=label)
        offsets_small=({0:(6,-6),1:(5,-5),2:(-15,2),3:(-6,15),4:(-3,-8),5:(-7,-9),6:(4,12),
                        7:(-4,-9),8:(-4,15),9:(-2,17),10:(6,3),11:(-21,5),12:(5,10),13:(-19,-3),14:(5,-5)}
                       if key=="time" else {0:(4,-5),1:(-9,16),2:(-4,16),3:(-4,16),4:(-4,-8),5:(-3,-8),
                                             6:(-4,-9),7:(-4,-9),8:(-4,-10),9:(-10,16),10:(-4,-8),11:(-5,16),12:(3,10),13:(-19,-5),14:(-13,-8)})
        scatter(axis,key,offsets=offsets_small)
    f.text(16,429,"Filled points and connecting lines: observed Pareto frontier",size=10,color=P.muted)
    for i,m in enumerate(METHODS):
        x=17+(i%5)*140
        y=451+(i//5)*18
        marker(f,x+3,y-3,color=m["color"],radius=2.5)
        f.text(x+13,y,f"{m['id']:2}  {m['name']}",size=9)
    footer(f)
    return f.save()


if __name__=="__main__":
    run_example(draw,"efficiency_frontier")
