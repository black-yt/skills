"""示例需求：为异步学习系统绘制阶段、工作进程、共享资源池与物理节点的分层架构。"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from style1 import Figure, P, run_example


def chevron(f,x,y,w,h,number,title,detail,color):
    f.polyline([(x,y),(x+w-13,y),(x+w,y+h/2),(x+w-13,y+h),(x,y+h)],
               color=color,fill=color,close=True,width=.5)
    f.circle(x+17,y+h/2,8,stroke=None,fill=P.white)
    f.text(x+17,y+h/2+3,number,size=10,align="center")
    f.text(x+34,y+18,title,size=11,color=P.white)
    f.text(x+34,y+33,detail,size=10,color=P.white)


def tiles(f,x,y,count, *, shared=False,size=16,gap=6):
    for i in range(count):
        xx=x+i*(size+gap)
        f.box(xx,y,size,size*.7,fill="#E7F0F0" if shared else P.purple,
              stroke=P.teal if shared else None,line_width=.75,radius=2)


def draw(output, **options):
    f=Figure(output,458,title="A resource-aware asynchronous learning runtime",**options)
    f.background()
    f.header("A resource-aware asynchronous learning runtime")
    f.text(15,77,"Stages",size=12,bold=True)
    for x,number,title,detail,color in [(117,1,"Rollout","multi-turn generation",P.purple),
                                      (314,2,"Reward evaluation","independent verifier",P.rust),
                                      (511,3,"Training","one update per batch","#42366E")]:
        chevron(f,x,47,183,44,number,title,detail,color)
    f.polyline([(602,94),(602,105),(207,105),(207,96)],color=P.purple,dash=(3,3),width=.9)
    f.arrow([(207,98),(207,93)],color=P.purple,head=3)
    f.box(324,97,183,16,fill=P.midpoint,stroke=None,radius=0)
    f.text(415,108,"Asynchronous weight update",size=9,align="center",color=P.purple)
    f.text(15,137,"Worker types",size=12,bold=True)
    f.text(113,137,"· what claims the resources",size=10,color=P.muted)
    workers=[(15,183,"Rollout worker",P.purple),(210,183,"Training worker","#42366E"),(405,300,"Agent loop worker",P.rust)]
    for x,w,title,color in workers:
        f.box(x,150,w,68,fill=P.white,alpha=.3,radius=6)
        f.line((x+2,159),(x+2,208),color=color,width=2)
        f.text(x+12,168,title,size=12)
        if w<200:
            f.box(x+12,178,69,18,fill=P.white,stroke=color,radius=5)
            f.text(x+46,191,"GPU only",size=10,align="center",color=color)
            f.text(x+w-12,191,"Engine" if x==15 else "Trainer",size=10,align="right",color=color)
            f.text(x+12,209,"Exclusive device ownership",size=9,color=P.muted)
        else:
            for xx,title,detail in [(x+12,"CPU only","shared cores"),(x+159,"CPU + GPU","mixed resources")]:
                f.box(xx,177,132,31,fill=P.peach,stroke="#E4CFC1",radius=5)
                f.text(xx+9,190,title,size=10,color=P.rust)
                f.text(xx+9,203,detail,size=9,color=P.muted)
    f.arrow([(484,220),(484,238)],color=P.muted)
    f.text(496,232,"Workers claim from the pools",size=9,color=P.muted)
    f.text(15,251,"Unified resource pools",size=12,bold=True)
    for x,title,subtitle,shared in [(15,"GPU pool","exclusive devices",False),(366,"CPU pool","shareable cores",True)]:
        f.box(x,263,339,47,fill="#F0ECF7" if not shared else "#E9F2F3",alpha=.5,radius=6)
        f.text(x+12,282,title,size=12)
        f.text(x+86,282,"· "+subtitle,size=10,color=P.muted)
        tiles(f,x+12,289,14,shared=shared,size=16,gap=6)
        f.text(x+325,299,"…",size=11,color=P.teal if shared else P.purple,align="center")
    f.arrow([(353,331),(353,314)],color=P.muted)
    f.text(368,325,"One logical pool spans all physical nodes",size=9,color=P.muted)
    f.text(15,348,"Physical cluster",size=12,bold=True)
    f.text(130,348,"· CPUs plus accelerators on each node",size=10,color=P.muted)
    for i in range(3):
        x=15+i*232
        f.box(x,360,216,62,fill=P.white,alpha=.3,radius=6)
        f.text(x+12,378,f"Compute node {i+1}",size=11)
        f.text(x+202,378,"CPU shared",size=9,color=P.teal,align="right")
        tiles(f,x+12,388,8,size=18,gap=6)
        for j in range(8):
            f.box(x+17+j*24,391,7,6,fill=P.white,stroke=None,radius=1)
        f.text(x+12,414,"8 accelerators · exclusive allocation",size=9,color=P.muted)
    f.text(16,446,"Illustrative system design · resource counts are configurable",size=9,color=P.muted)
    return f.save()


if __name__=="__main__":
    run_example(draw,"resource_runtime")
