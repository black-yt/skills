"""示例需求：比较十五种研究助手的任务完成率，用误差线、数值与家族配色展示排行榜。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example
from charts import Axes, marker, legend_item, footer
from demo_data import METHODS, FAMILIES, FAMILY_COLORS, FAMILY_SHAPES


def draw(output, **options):
    f=Figure(output,340,title="Research assistant evaluation",**options)
    f.background()
    f.header("Research assistant evaluation")
    axis=Axes(f,53,61,647,175,(-.7,len(METHODS)-.3),(0,80))
    axis.frame(yticks=(0,20,40,60,80),ylabel="Task success (%)",size=9)
    for i,m in enumerate(METHODS):
        axis.bar(i,m["score"],color=m["color"],interval=(m["low"],m["high"]))
        f.text(axis.sx(i),axis.sy(m["high"])-6,f"{m['score']:.1f}",size=10,align="center")
        marker(f,axis.sx(i),248,color=m["color"],shape=m["shape"],radius=3)
        f.lines(axis.sx(i),264,m["name"].split(),size=9.5,align="center",leading=12)
    for i,family in enumerate(FAMILIES):
        legend_item(f,106+i*139,297,family,FAMILY_COLORS[family],shape=FAMILY_SHAPES[family])
    footer(f,detail="Error bars: illustrative bounds")
    return f.save()


if __name__=="__main__":
    run_example(draw,"evaluation_leaderboard")
