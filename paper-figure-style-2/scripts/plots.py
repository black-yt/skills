"""Complete statistical layouts, parameterized by task data where appropriate."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import patches
from charts import (grouped_bars, radial_profile, response_curve, wilson,
                    recovery_bars, rate_heatmap, failure_pie)
from style2 import (CATEGORY, ACCENT, BLUE, CYAN, MINT, TEAL, MUTED, INK,
                    clean_axes, footer, save_pdf, theme)
from demo_data import (DIMENSIONS, SUITES, MODELS, benchmark_demands, response_observations,
                       harness_counts, recovery_counts, repeated_tasks, FAILURE_LABELS, FAILURE_COLORS)


def capability_profiles(output, *, width_in=11, demands=None, names=SUITES, dimensions=DIMENSIONS):
    """Request: compare task coverage and mean demand for six benchmark suites."""
    demands=benchmark_demands() if demands is None else [np.asarray(a) for a in demands]
    if len(demands)!=6 or len(names)!=6 or len(dimensions)!=6:
        raise ValueError("This composition expects six benchmarks and six dimensions")
    for matrix in demands:
        if (matrix.ndim!=2 or matrix.shape[1]!=6 or len(matrix)==0 or np.any(~np.isfinite(matrix))
                or np.any((matrix<0)|(matrix>5)) or np.any(matrix!=np.floor(matrix))):
            raise ValueError("Task demands must be nonempty integer arrays with six columns in [0,5]")
    with theme():
        fig=plt.figure(figsize=(11,5.15))
        ax=fig.add_axes([.063,.565,.922,.35])
        coverage=np.array([(a>0).mean(axis=0)*100 for a in demands])
        grouped_bars(ax,coverage,dimensions,names,CATEGORY,labels=True,legend=True)
        ax.set_ylabel("Task coverage (%)",fontsize=9)
        ax.set_yticklabels([f"{v}%" for v in range(0,101,20)])
        fig.text(.52,.497,"(a) Capability coverage",ha="center",fontsize=11)
        for i,(matrix,name,color) in enumerate(zip(demands,names,ACCENT)):
            polar=fig.add_axes([.005+i*.166,.081,.164,.343])
            radial_profile(polar,matrix.mean(axis=0),dimensions,color,name)
        fig.text(.52,.043,"(b) Mean capability demand level",ha="center",fontsize=11)
        footer(fig)
        return save_pdf(fig,output,title="Benchmark capability translation",width_in=width_in)


def demand_response(output, *, width_in=11, observations=None, names=("Model A","Model B")):
    """Request: show observed success rates and logistic fits in six small panels."""
    levels,successes,totals=response_observations() if observations is None else observations
    levels,successes,totals=map(np.asarray,(levels,successes,totals))
    if successes.shape!=(2,6,len(levels)) or totals.shape!=(6,len(levels)) or len(names)!=2:
        raise ValueError("Provide two models, six capabilities, and matching demand levels")
    with theme():
        fig,axes=plt.subplots(1,6,figsize=(11,2.18))
        fig.subplots_adjust(left=.048,right=.992,bottom=.28,top=.77,wspace=.29)
        for c,ax in enumerate(axes):
            for m,color in enumerate(("#0072BD","#29CFA9")):
                response_curve(ax,levels,successes[m,c],totals[c],color=color,label=names[m],end=10)
            ax.axvline(5,color="#D9DDE1",lw=.6,linestyle=":")
            ax.set(xlim=(0,10),ylim=(0,103),xticks=[0,2,4,6,8,10],yticks=[0,20,40,60,80,100])
            ax.set_title(DIMENSIONS[c],fontsize=9,fontweight="bold",pad=4)
            ax.tick_params(labelsize=6.4,pad=1)
            ax.set_xlabel("Demand level",fontsize=7,labelpad=3)
            clean_axes(ax)
        axes[0].set_ylabel("Success rate (%)",fontsize=8,labelpad=3)
        handles,labels=axes[0].get_legend_handles_labels()
        fig.legend(handles,labels,ncol=2,loc="upper center",bbox_to_anchor=(.5,1),fontsize=8,handlelength=2.4)
        footer(fig,"Illustrative counts · binomial logistic fit · dashed segments beyond level 5 are extrapolations")
        return save_pdf(fig,output,title="Demand sensitivity by capability",width_in=width_in)


def harness_grid(output, *, width_in=11, successes=None, totals=None):
    """Request: compare three harnesses for three models across task-demand groups."""
    if successes is None and totals is None: successes,totals=harness_counts()
    elif successes is None or totals is None: raise ValueError("Supply both successes and totals")
    successes,totals=np.asarray(successes),np.asarray(totals)
    if successes.shape!=(3,3,6,3,3) or totals.shape!=successes.shape:
        raise ValueError("Counts shape must be benchmark(3), model(3), capability(6), harness(3), group(3)")
    rate,low,high=wilson(successes,totals)
    with theme():
        fig=plt.figure(figsize=(11,11.8))
        names=("Code Suite","Terminal Suite","Research Suite")
        harnesses=(("Planner","Reactive","Toolchain"),("Planner","Terminal","Toolchain"),("Planner","Research","Toolchain"))
        palettes=((BLUE,CYAN,MINT),(BLUE,"#AFD9E6",MINT),(BLUE,"#83CADF",TEAL))
        for b,(name,series,palette) in enumerate(zip(names,harnesses,palettes)):
            top=.964-b*.314
            fig.text(.38,top,name,ha="right",fontsize=11)
            handles=[patches.Patch(facecolor=c,label=s) for c,s in zip(palette,series)]
            fig.legend(handles=handles,ncol=3,loc="center left",bbox_to_anchor=(.40,top+.003),fontsize=7.7)
            for m in range(3):
                bottom=top-.1-m*.089
                for c in range(6):
                    ax=fig.add_axes([.078+c*.152,bottom,.131,.073])
                    grouped_bars(ax,rate[b,m,c]*100,("Low","Medium","High"),series,palette,
                                 intervals=(low[b,m,c]*100,high[b,m,c]*100),counts=totals[b,m,c])
                    ax.set_yticks([0,50,100]); ax.tick_params(labelsize=5.9,pad=1,length=1.5)
                    if m==0: ax.set_title(DIMENSIONS[c],fontsize=7.7,pad=4)
                    if m<2: ax.set_xticklabels([])
                    if c==0: ax.set_ylabel(f"{MODELS[m]}\nAccuracy (%)",fontsize=6.4,labelpad=5)
        footer(fig,"Illustrative binary outcomes · 95% Wilson intervals · translucent: n < 20 · dash: no tasks · all bars start at zero")
        return save_pdf(fig,output,title="Harness outcomes across models and demands",width_in=width_in)


def recovery_analysis(output, *, width_in=11, counts=None):
    """Request: locate repeat-run instability by capability and task difficulty."""
    one,two,total,hits,ns=recovery_counts() if counts is None else counts
    one,two,total,hits,ns=map(np.asarray,(one,two,total,hits,ns))
    if one.shape!=(6,) or two.shape!=(6,) or total.shape!=(6,) or hits.shape!=(6,5) or ns.shape!=(6,5):
        raise ValueError("Recovery summary needs six capabilities and five demand levels")
    if not np.array_equal(one+two,hits.sum(axis=1)) or not np.array_equal(total,ns.sum(axis=1)):
        raise ValueError("Bar totals and heatmap counts must describe the same task population")
    order=np.argsort(-np.divide(np.asarray(one)+two,total,out=np.zeros(len(total),dtype=float),where=np.asarray(total)>0))
    labels=np.asarray(DIMENSIONS)[order]
    with theme():
        fig=plt.figure(figsize=(11,3.55))
        bars=fig.add_axes([.075,.25,.35,.62])
        recovery_bars(bars,np.asarray(one)[order],np.asarray(two)[order],np.asarray(total)[order],labels)
        heat=fig.add_axes([.61,.25,.37,.62])
        rate_heatmap(heat,np.asarray(hits)[order],np.asarray(ns)[order],labels,[1,2,3,4,5])
        fig.text(.25,.084,"(a) By capability",ha="center",fontsize=11)
        fig.text(.79,.084,"(b) By demand level",ha="center",fontsize=11)
        footer(fig,"Illustrative repeated runs · high score ≥ 0.8 · 95% Wilson intervals · †: n < 5 · dash: no tasks")
        return save_pdf(fig,output,title="Intermittent high-score outcomes",width_in=width_in)


def failure_distributions(output, *, width_in=11, counts=None):
    """Request: compare failure composition for research and coding evaluations."""
    arrays=([157,120,48,34,21,20,19,11,1],[17,22,0,15,10,12,0,16,6]) if counts is None else counts
    if len(arrays)!=2 or any(np.asarray(a).shape!=(9,) for a in arrays):
        raise ValueError("Provide two failure populations with nine categories each")
    with theme():
        fig,axes=plt.subplots(1,2,figsize=(11,4.1))
        fig.subplots_adjust(left=.08,right=.92,top=.98,bottom=.14,wspace=.37)
        for i,(ax,data,title) in enumerate(zip(axes,arrays,("(a) Research workflows","(b) Coding workflows"))):
            order=np.arange(9) if i==0 else np.array([1,0,7,3,5,4,8,2,6])
            failure_pie(ax,np.asarray(data)[order],np.asarray(FAILURE_LABELS)[order],np.asarray(FAILURE_COLORS)[order],title=title)
        footer(fig,"Illustrative failure records · percentages use each panel's analyzed failures as the denominator")
        return save_pdf(fig,output,title="Recorded failure categories",width_in=width_in)


def evidence_table(output, *, width_in=11, tasks=None, threshold=.8, max_rows=17):
    """Request: inspect three run scores together with capability requirements."""
    ids,scores,demands=repeated_tasks() if tasks is None else tasks
    scores,demands=np.asarray(scores,dtype=float),np.asarray(demands,dtype=float)
    if scores.shape!=(len(ids),3) or demands.shape!=(len(ids),6):
        raise ValueError("Each task needs three scores and six capability levels")
    if (np.any(~np.isfinite(scores)) or np.any((scores<0)|(scores>1)) or np.any(~np.isfinite(demands))
            or np.any((demands<0)|(demands>5)) or np.any(demands!=np.floor(demands))):
        raise ValueError("Scores must be finite in [0,1]; demands must be integers in [0,5]")
    if not 0<=threshold<=1 or not isinstance(max_rows,int) or max_rows<1:
        raise ValueError("Threshold must be in [0,1] and max_rows must be a positive integer")
    high=(scores>=threshold).sum(axis=1)
    twice,once=np.flatnonzero(high==2),np.flatnonzero(high==1)
    quota=min(len(twice),int(np.ceil(max_rows*.75)))
    selected=np.r_[twice[:quota],once[:max_rows-quota]]
    if len(selected)<max_rows: selected=np.r_[selected,twice[quota:max_rows-len(selected)+quota]]
    if not len(selected): raise ValueError("No intermittently high-scoring tasks to display")
    with theme():
        fig=plt.figure(figsize=(11,.95+len(selected)*.25))
        ax=fig.add_axes([.025,.065,.95,.86]); ax.set_axis_off()
        ax.set(xlim=(0,1),ylim=(len(selected)+2,0))
        edges=np.r_[0,.405,.465,.525,.585,.68,np.linspace(.68,1,7)[1:]]
        centers=(edges[:-1]+edges[1:])/2
        ax.text(.002,.62,"Task ID",fontsize=8,va="center")
        ax.text((edges[1]+edges[4])/2,-.09,"Task score",ha="center",fontsize=8.5)
        ax.text(centers[4],.25,"High-score\nruns",ha="center",va="center",fontsize=7.8)
        ax.text((edges[5]+1)/2,-.09,"Capability demand level",ha="center",fontsize=8.5)
        for i,label in enumerate(("Run 1","Run 2","Run 3")):
            ax.text(centers[i+1],.62,label,ha="center",va="center",fontsize=7.8)
        for i,label in enumerate(DIMENSIONS): ax.text(centers[i+5],.62,label,ha="center",va="center",fontsize=7.5)
        ax.axhline(1,color="#969DA5",lw=.65)
        for r,index in enumerate(selected):
            y=r+1
            label=ids[index]
            if len(label)>53: raise ValueError("Task ID too long; supply a concise display label (<=53 characters)")
            ax.text(.002,y+.5,label,fontsize=7.4,va="center")
            for run,score in enumerate(scores[index]):
                x=edges[run+1]; w=edges[run+2]-x
                ax.add_patch(patches.Rectangle((x+.001,y+.04),w-.002,.92,
                             facecolor="#B6ECFD" if score>=threshold else "#D4D4D4",edgecolor="white",lw=.4))
                ax.text(x+w/2,y+.5,f"{score:.3f}",ha="center",va="center",fontsize=7.5)
            ax.text(centers[4],y+.5,f"{high[index]} of 3",ha="center",va="center",fontsize=7.5)
            for c,value in enumerate(demands[index]): ax.text(centers[c+5],y+.5,str(int(value)),ha="center",va="center",fontsize=7.5)
            ax.axhline(y+1,color="#E2E5E9",lw=.4)
        fig.legend(handles=[patches.Patch(facecolor=c,label=s) for c,s in
                   (("#D4D4D4",f"Score < {threshold:g}"),("#B6ECFD",f"Score ≥ {threshold:g}"))],
                   ncol=2,loc="upper left",bbox_to_anchor=(.019,1.008),fontsize=8)
        footer(fig,"Illustrative stratified subset · threshold applied to unrounded scores · shared data with the repeat-run analysis")
        return save_pdf(fig,output,title="Task-level evidence and capability requirements",width_in=width_in)
