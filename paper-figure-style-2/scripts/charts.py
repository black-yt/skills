"""Reusable statistical artists and calculations for paper-figure-style-2.

Values are supplied by the caller. Missing groups remain missing; confidence
intervals come from counts rather than decorative random error bars.
"""
from __future__ import annotations

from statistics import NormalDist
import numpy as np
from matplotlib import colors, patches

from style2 import BLUE, CATEGORY, CYAN, GRID, INK, MUTED, clean_axes, tint


def count_array(values, name="counts"):
    a = np.asarray(values, dtype=float)
    if np.any(~np.isfinite(a)) or np.any(a < 0) or np.any(a != np.floor(a)):
        raise ValueError(f"{name} must contain finite nonnegative integers")
    return a


def wilson(successes, totals, confidence=.95):
    """Binomial Wilson intervals as fractions. Empty groups return NaN."""
    k, n = count_array(successes, "successes"), count_array(totals, "totals")
    if k.shape != n.shape or np.any(k > n) or not 0 < confidence < 1:
        raise ValueError("Counts must have the same shape and 0 <= k <= n; confidence in (0,1)")
    z = NormalDist().inv_cdf((1+confidence)/2)
    safe = np.where(n > 0, n, 1)
    p = k / safe
    center = (p + z*z/(2*safe)) / (1 + z*z/safe)
    half = z*np.sqrt(p*(1-p)/safe + z*z/(4*safe*safe))/(1 + z*z/safe)
    return (np.where(n > 0, p, np.nan),
            np.where(n > 0, np.minimum(p, np.maximum(0, center-half)), np.nan),
            np.where(n > 0, np.maximum(p, np.minimum(1, center+half)), np.nan))


def grouped_bars(ax, values, groups, series, palette, *, intervals=None,
                 counts=None, sparse_below=20, labels=False, legend=False):
    """Percent bars: arrays have shape (series, groups), with NaN for missing."""
    values = np.asarray(values, dtype=float)
    if values.shape != (len(series), len(groups)) or len(palette) != len(series):
        raise ValueError("values and palette must match series and groups")
    if np.any(np.isinf(values)) or np.any((values < 0) | (values > 100)):
        raise ValueError("Bar percentages must be in [0,100], or NaN for missing")
    if intervals is not None:
        lo, hi = (np.asarray(a, dtype=float) for a in intervals)
        valid = np.isfinite(values)
        if lo.shape != values.shape or hi.shape != values.shape:
            raise ValueError("Interval arrays must match values")
        if (np.any(~np.isfinite(lo[valid])) or np.any(~np.isfinite(hi[valid]))
                or np.any(lo[valid] > values[valid]) or np.any(hi[valid] < values[valid])
                or np.any(lo[valid] < 0) or np.any(hi[valid] > 100)):
            raise ValueError("Intervals must contain their values within [0,100]")
    if counts is not None:
        counts = count_array(counts)
        if counts.shape != values.shape or np.any((counts == 0) & np.isfinite(values)):
            raise ValueError("Counts must match values; a group with zero tasks must be missing")
    width = .82 / len(series)
    artists = []
    for s, (name, color) in enumerate(zip(series, palette)):
        for j, value in enumerate(values[s]):
            x = j + (s-(len(series)-1)/2)*width
            if np.isnan(value):
                ax.text(x, 2, "–", ha="center", va="bottom", fontsize=5, color=MUTED)
                continue
            alpha = .32 if counts is not None and counts[s, j] < sparse_below else 1
            bar = ax.bar(x, value, width, color=color, edgecolor="#6F7780", linewidth=.35,
                         alpha=alpha, label=name if j == 0 else None, zorder=3)
            artists.extend(bar.patches)
            if intervals is not None:
                ax.errorbar(x, value, yerr=[[max(0, value-lo[s,j])], [max(0, hi[s,j]-value)]],
                            fmt="none", ecolor="#555B63", elinewidth=.45, capsize=1.2, capthick=.4, zorder=4)
            if labels:
                ax.text(x, value+1.8, f"{value:.1f}", ha="center", va="bottom", fontsize=5.5)
    ax.set_xticks(range(len(groups)), groups)
    ax.set_xlim(-.6, len(groups)-.4)
    ax.set_ylim(0, 112 if labels else 102)
    ax.set_yticks(range(0,101,20))
    clean_axes(ax)
    if legend:
        ax.legend(handles=[patches.Patch(facecolor=c, edgecolor="#6F7780", linewidth=.4, label=s)
                           for c,s in zip(palette,series)], ncol=len(series), loc="lower center",
                  bbox_to_anchor=(.5,1.04), columnspacing=1.1, handlelength=1.5)
    return artists


def radial_profile(ax, values, dimensions, color, title, *, maximum=5):
    """Six radial sectors with concentric tint bands, not a polygon radar."""
    a = np.asarray(values, dtype=float)
    if a.shape != (len(dimensions),) or len(a) < 3 or maximum <= 0:
        raise ValueError("One value per dimension and a positive maximum are required")
    if np.any(~np.isfinite(a)) or np.any((a < 0) | (a > maximum)):
        raise ValueError("Radial values must be finite and within the displayed scale")
    inner, radius = .14, 1.
    ax.set_aspect("equal")
    ax.set(xlim=(-1.4,1.4), ylim=(-1.4,1.4))
    ax.set_axis_off()
    sectors = []
    for i, value in enumerate(a):
        angle = 90-i*360/len(a)
        start, stop = angle-180/len(a), angle+180/len(a)
        ax.add_patch(patches.Wedge((0,0), radius, start, stop, width=radius-inner,
                                  facecolor=tint(color,.055), edgecolor="none"))
        rtop = inner + (radius-inner)*value/maximum
        for level in range(int(np.ceil(value))):
            r0 = inner+(radius-inner)*level/maximum
            r1 = min(rtop,inner+(radius-inner)*(level+1)/maximum)
            wedge = patches.Wedge((0,0),r1,start,stop,width=r1-r0,
                                  facecolor=tint(color,.85-.115*level),edgecolor="none")
            ax.add_patch(wedge); sectors.append(wedge)
        theta = np.deg2rad(start)
        ax.plot([inner*np.cos(theta),radius*np.cos(theta)],
                [inner*np.sin(theta),radius*np.sin(theta)],lw=.45,color="#616971")
        rad = np.deg2rad(angle)
        ax.text(1.23*np.cos(rad),1.23*np.sin(rad),f"{dimensions[i]}\n{value:.2f}",
                ha="center",va="center",fontsize=5.8,linespacing=1.5)
    for level in range(1,int(maximum)+1):
        r = inner+(radius-inner)*level/maximum
        ax.add_patch(patches.Circle((0,0),r,facecolor="none",edgecolor="#AEB6BF",lw=.4))
        ax.text(0,r-.045,str(level),ha="center",va="top",fontsize=4.7,color="#949DA7")
    ax.add_patch(patches.Circle((0,0),inner,facecolor="white",edgecolor="white",lw=.6))
    ax.set_title(title,fontsize=8.2,pad=3)
    return sectors


def logistic_fit(levels, successes, totals, *, ridge=.02, max_iter=100):
    """Regularized binomial logistic fit using trial counts as weights.

    No fabricated observations are added. ridge is an explicit weak L2 penalty
    on both coefficients. Returns intercept and slope in original x units.
    """
    x = np.asarray(levels, dtype=float)
    k, n = count_array(successes), count_array(totals)
    if x.ndim != 1 or x.shape != k.shape or k.shape != n.shape or np.any(k > n):
        raise ValueError("One-dimensional levels, successes and totals must match")
    if np.any(~np.isfinite(x)) or ridge <= 0 or not np.isfinite(ridge):
        raise ValueError("Finite levels and a positive ridge penalty are required")
    use = n > 0
    x, k, n = x[use], k[use], n[use]
    if len(x) < 2 or len(np.unique(x)) < 2:
        raise ValueError("At least two distinct observed levels are needed")
    center, scale = x.mean(), max(x.std(), 1.)
    X = np.column_stack([np.ones(len(x)), (x-center)/scale])
    beta = np.zeros(2)
    def loss(b):
        eta = X@b
        return np.sum(n*np.logaddexp(0,eta)-k*eta)+ridge*np.dot(b,b)/2
    for _ in range(max_iter):
        p = 1/(1+np.exp(-np.clip(X@beta,-40,40)))
        gradient = X.T@(n*p-k)+ridge*beta
        hessian = X.T@((n*p*(1-p))[:,None]*X)+ridge*np.eye(2)
        step = np.linalg.solve(hessian,gradient)
        amount = 1.
        while loss(beta-amount*step) > loss(beta)+1e-10 and amount > 1e-8:
            amount *= .5
        beta -= amount*step
        if np.max(np.abs(amount*step)) < 1e-8:
            return np.array([beta[0]-beta[1]*center/scale, beta[1]/scale])
    raise RuntimeError("Logistic fit did not converge")


def response_curve(ax, levels, successes, totals, *, color, label, end=10):
    x = np.asarray(levels,dtype=float)
    p, _, _ = wilson(successes,totals)
    valid = np.isfinite(p)
    beta = logistic_fit(x,successes,totals)
    boundary = x[valid].max()
    if not np.isfinite(end) or end < boundary:
        raise ValueError("Curve end cannot precede observed levels")
    for a,b,ls in ((x[valid].min(),boundary,"-"),(boundary,end,(0,(3,2)))):
        t = np.linspace(a,b,160)
        rate = 100/(1+np.exp(-np.clip(beta[0]+beta[1]*t,-40,40)))
        ax.plot(t,rate,color=color,lw=1.05,linestyle=ls,label=label if ls=="-" else None)
    ax.scatter(x[valid],100*p[valid],s=10,color=color,edgecolors="white",linewidths=.3,zorder=4)
    return beta


def recovery_bars(ax, one, two, totals, labels):
    one, two, totals = count_array(one),count_array(two),count_array(totals)
    if one.shape != two.shape or two.shape != totals.shape or one.shape != (len(labels),):
        raise ValueError("Each row requires one-run, two-run and total counts")
    rate, lo, hi = wilson(one+two,totals)
    y = np.arange(len(labels))
    divisor = np.where(totals>0,totals,1)
    ax.barh(y,100*one/divisor,color="#D4D4D4",edgecolor="#444B53",linewidth=.65,label="1 of 3")
    ax.barh(y,100*two/divisor,left=100*one/divisor,color="#B6ECFD",edgecolor="#444B53",linewidth=.65,label="2 of 3")
    valid = totals>0
    ax.errorbar(rate[valid]*100,y[valid],xerr=np.array([rate[valid]-lo[valid],hi[valid]-rate[valid]])*100,
                fmt="none",ecolor="#40464E",elinewidth=.7,capsize=2,zorder=4)
    for i,p in enumerate(rate):
        ax.text(1.02,i,"–" if not np.isfinite(p) else f"{p*100:.1f}%",
                transform=ax.get_yaxis_transform(),fontsize=8,va="center")
    ax.set_yticks(y,labels)
    ax.invert_yaxis()
    ax.set_xlim(0,max(60, int(np.nanmax(hi)*10+1)*10) if valid.any() else 100)
    ax.set_xlabel("Tasks with 1–2 high-score runs (%)",fontsize=9)
    clean_axes(ax,grid="x",full_box=True)
    ax.legend(ncol=2,loc="lower right",bbox_to_anchor=(1,1.01),handlelength=1.2)
    return rate,lo,hi


def rate_heatmap(ax, successes, totals, rows, columns, *, sparse_below=5):
    k,n=count_array(successes),count_array(totals)
    rate,_,_=wilson(k,n)
    if rate.shape != (len(rows),len(columns)):
        raise ValueError("Heatmap counts must match row and column labels")
    cmap=colors.LinearSegmentedColormap.from_list("pale-blue",["#F7FAFC","#D5EEF5","#78BDDD",BLUE])
    # pcolormesh retains true rectangles in PDF; imshow would be a bitmap.
    mesh=ax.pcolormesh(np.ma.masked_invalid(rate),vmin=0,vmax=1,cmap=cmap,
                       edgecolors="white",linewidth=.8,rasterized=False)
    ax.set_facecolor("#D4D4D4")
    for i in range(len(rows)):
        for j in range(len(columns)):
            value=rate[i,j]
            label="–" if n[i,j]==0 else f"{100*value:.1f}%"+("†" if n[i,j]<sparse_below else "")
            ax.text(j+.5,i+.5,label,ha="center",va="center",fontsize=8,
                    color="white" if np.isfinite(value) and value>=.76 else INK)
    ax.set_xticks(np.arange(len(columns))+.5,columns)
    ax.set_yticks(np.arange(len(rows))+.5,rows)
    ax.set_ylim(len(rows),0)
    ax.tick_params(length=0,pad=5)
    for spine in ax.spines.values(): spine.set_visible(False)
    ax.set_xlabel("Capability demand level",fontsize=9)
    return mesh


def failure_pie(ax, counts, labels, palette, *, title, inside_min=.065):
    values=count_array(counts)
    if values.shape!=(len(labels),) or len(palette)!=len(labels) or values.sum()<=0:
        raise ValueError("Positive total and aligned counts, labels and colors required")
    wedges,_=ax.pie(values,colors=palette,startangle=90,counterclock=False,
                    wedgeprops=dict(edgecolor="white",linewidth=.7),radius=.92)
    external=[]
    for value,label,wedge in zip(values,labels,wedges):
        if value==0: continue
        fraction=value/values.sum()
        a=np.deg2rad((wedge.theta1+wedge.theta2)/2)
        if fraction>=inside_min:
            ax.text(.57*np.cos(a),.57*np.sin(a),label+f"\n{100*fraction:.2f}%",
                    ha="center",va="center",fontsize=6.3 if fraction<.13 else 7,linespacing=1.2)
        else:
            external.append((np.cos(a),np.sin(a),label+f"\n{100*fraction:.2f}%"))
    # Label positions are separated per side, with explicit thin leaders.
    for side in (-1,1):
        items=sorted((p for p in external if (p[0]>=0)==(side==1)),key=lambda p:p[1])
        ys=[]
        for _,yy,_ in items: ys.append(max(yy*1.2,ys[-1]+.31 if ys else -1.2))
        if ys and ys[-1]>1.25:
            offset=ys[-1]-1.25; ys=[yy-offset for yy in ys]
        for j,((xx,yy,label),label_y) in enumerate(zip(items,ys)):
            # Leave the sector radially before routing outside the pie; this
            # keeps leaders out of the larger sectors' interior text.
            lane=side*(1.01+.017*j)
            ax.plot([.88*xx,1.015*xx,lane,lane,side*1.10],
                    [.88*yy,1.015*yy,1.015*yy,label_y,label_y],
                    color="#444B53",lw=.45)
            ax.text(side*1.13,label_y,label,ha="left" if side>0 else "right",
                    va="center",fontsize=6.7)
    ax.set(xlim=(-1.8,1.8),ylim=(-1.2,1.6))
    ax.set_title(title,y=-.03,fontsize=9,fontweight="bold")
    return wedges
