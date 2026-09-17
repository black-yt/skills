"""示例需求：把研究助手按四个家族分组，绘制任务完成率随时间预算增长的阶梯曲线和区间。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import Axes, legend_item, marker, footer
from demo_data import METHODS, FAMILIES, FAMILY_COLORS, FAMILY_SHAPES, budget_curve


def draw(output, **options):
    f=Figure(output,385,title="Budget-response profiles by method family",**options)
    f.background()
    f.header("Budget-response profiles by method family")
    for j,family in enumerate(FAMILIES):
        x=12+j*175
        f.box(x,49,170,281,fill=P.white,alpha=.3,stroke="#CFC9DE",radius=6)
        marker(f,x+16,69,color=FAMILY_COLORS[family],shape=FAMILY_SHAPES[family],radius=4)
        f.text(x+29,73,family+" family",size=11)
        axis=Axes(f,x+29,97,131,132,(0,60),(0,75))
        axis.frame(xticks=(0,30,60),yticks=(0,35,70),ylabels=j==0,size=9)
        members=[m for m in METHODS if m["family"]==family]
        for k,m in enumerate(members):
            dash=(None,(5,3),(5,2,1,2),(1,3))[k]
            times,values,low,high=budget_curve(m)
            axis.band(times,low,high,center=values,color=m["color"],step=True,alpha=.11)
            axis.series(times,values,color=m["color"],dash=dash,step=True)
            legend_item(f,x+14,266+k*17,m["name"],m["color"],dash=dash,size=10)
    f.text(360,343,"Elapsed time (minutes); cumulative task success (%)",size=10,align="center",color=P.muted)
    footer(f,detail="Shaded bands: illustrative bounds")
    return f.save()


if __name__=="__main__":
    run_example(draw,"budget_profiles")
