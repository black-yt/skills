"""Statistical marks with native PDF paths and selectable axis/legend text.

Data coordinates increase right/up. Layout coordinates follow Figure (right/down).
Intervals are supplied by the caller; this module does not infer uncertainty.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, sin, tan, pi, isfinite, log10, ceil
from reportlab.lib.colors import HexColor
from style1 import P


COLORS = ("#A36840", "#3E846B", "#7261D3", "#4874C5", "#3E8495", "#927333", "#BE5378")
DEMO_NOTE = "Illustrative data · not measured results"


def finite(*values):
    if not all(isfinite(float(v)) for v in values):
        raise ValueError("Chart data must be finite numbers")


@dataclass(frozen=True)
class Scale:
    low: float
    high: float
    start: float
    end: float
    log: bool = False

    def __post_init__(self):
        finite(self.low,self.high,self.start,self.end)
        if self.low >= self.high or self.start == self.end:
            raise ValueError("Scale needs increasing data limits and distinct pixel endpoints")
        if self.log and self.low <= 0:
            raise ValueError("Log scale requires positive limits")

    def __call__(self, value):
        finite(value)
        tolerance=1e-9*max(1,abs(self.low),abs(self.high))
        if not self.low-tolerance <= value <= self.high+tolerance:
            raise ValueError(f"Value {value} outside axis [{self.low}, {self.high}]")
        if self.log and value <= 0:
            raise ValueError("Log data must be positive")
        transform=log10 if self.log else float
        t=(transform(value)-transform(self.low))/(transform(self.high)-transform(self.low))
        return self.start+t*(self.end-self.start)


class Axes:
    """Thin-spine axes. Explicit limits and ticks make units and ranges reviewable."""

    def __init__(self, f, x, y, w, h, xlim, ylim, *, logx=False):
        if min(w,h) <= 0:
            raise ValueError("Axes dimensions must be positive")
        self.f,self.x,self.y,self.w,self.h=f,x,y,w,h
        self.sx=Scale(*xlim,x,x+w,log=logx)
        self.sy=Scale(*ylim,y+h,y)

    def point(self,x,y):
        return self.sx(x),self.sy(y)

    def frame(self, *, xticks=(), yticks=(), xformat=lambda v:f"{v:g}",
              yformat=lambda v:f"{v:g}", xlabel=None, ylabel=None,
              ylabels=True, grid=True, size=9, xlabel_offset=30):
        f=self.f
        for value in yticks:
            py=self.sy(value)
            if grid:
                f.line((self.x,py),(self.x+self.w,py),color="#DFDCE3",width=.45)
            f.line((self.x-2,py),(self.x,py),color=P.muted,width=.55)
            if ylabels:
                f.text(self.x-6,py+size*.32,yformat(value),size=size,align="right",color=P.muted)
        for value in xticks:
            px=self.sx(value)
            f.line((px,self.y+self.h),(px,self.y+self.h+2),color=P.muted,width=.55)
            f.text(px,self.y+self.h+size+5,xformat(value),size=size,align="center",color=P.muted)
        f.line((self.x,self.y),(self.x,self.y+self.h),color=P.border,width=.75)
        f.line((self.x,self.y+self.h),(self.x+self.w,self.y+self.h),color=P.border,width=.75)
        if xlabel:
            f.text(self.x+self.w/2,self.y+self.h+xlabel_offset,xlabel,size=10,align="center")
        if ylabel:
            f.text(self.x-32,self.y+self.h/2,ylabel,size=10,align="center",angle=90)

    def _series(self,x,y):
        x,y=list(x),list(y)
        if len(x)!=len(y) or len(x)<2:
            raise ValueError("Series needs matching arrays with at least two points")
        if any(b<=a for a,b in zip(x,x[1:])):
            raise ValueError("Series x must be strictly increasing")
        return [self.point(a,b) for a,b in zip(x,y)]

    @staticmethod
    def _steps(points):
        result=[points[0]]
        for a,b in zip(points,points[1:]):
            result.extend([(b[0],a[1]),b])
        return result

    def series(self,x,y, *, color=P.purple, width=1.35, dash=None, step=False):
        points=self._series(x,y)
        self.f.polyline(self._steps(points) if step else points,color=color,width=width,dash=dash)

    def band(self,x,low,high, *, color=P.purple, alpha=.13, step=False, center=None):
        x,low,high=list(x),list(low),list(high)
        if not len(x)==len(low)==len(high):
            raise ValueError("Band arrays must have equal length")
        if any(a>b for a,b in zip(low,high)):
            raise ValueError("Band lower bound exceeds upper bound")
        if center is not None:
            center=list(center)
            if len(center)!=len(x) or any(not a<=v<=b for a,v,b in zip(low,center,high)):
                raise ValueError("Band must enclose its supplied central series")
        a,b=self._series(x,low),self._series(x,high)
        if step:
            a,b=self._steps(a),self._steps(b)
        self.f.polyline(a+b[::-1],color=color,width=0,fill=color,close=True,alpha=alpha)

    def error(self,x,y,low,high, *, horizontal=False, color=P.ink, cap=2.5, width=.75):
        value=x if horizontal else y
        finite(value,low,high)
        if not low<=value<=high:
            raise ValueError("Interval must enclose its estimate")
        px,py=self.point(x,y)
        if horizontal:
            a,b=self.sx(low),self.sx(high)
            self.f.line((a,py),(b,py),color=color,width=width)
            for p in (a,b):
                self.f.line((p,py-cap),(p,py+cap),color=color,width=width)
        else:
            a,b=self.sy(low),self.sy(high)
            self.f.line((px,a),(px,b),color=color,width=width)
            for p in (a,b):
                self.f.line((px-cap,p),(px+cap,p),color=color,width=width)

    def bar(self,x,value, *, width=.7, color=P.purple, interval=None):
        if self.sy.low!=0 or value<0:
            raise ValueError("Vertical magnitude bars require zero-based nonnegative y")
        a,b=self.point(x-width/2,value),self.point(x+width/2,0)
        self.f.box(a[0],a[1],b[0]-a[0],b[1]-a[1],radius=0,fill=color,stroke=None)
        if interval is not None:
            self.error(x,value,*interval)

    def hbar(self,y,value, *, height=.35, color=P.purple, interval=None, endpoint=True):
        if self.sx.low!=0 or self.sx.log or value<0:
            raise ValueError("Horizontal magnitude bars require zero-based linear x")
        a,b=self.point(0,y+height/2),self.point(value,y-height/2)
        self.f.box(a[0],a[1],b[0]-a[0],b[1]-a[1],radius=0,fill=color,stroke=None)
        if interval is not None:
            self.error(value,y,*interval,horizontal=True,cap=2)
        if endpoint:
            marker(self.f,*self.point(value,y),color=color,radius=1.8)

    def dot(self,x,y, *, color=P.purple, filled=True, shape="circle", radius=3):
        marker(self.f,*self.point(x,y),color=color,filled=filled,shape=shape,radius=radius)


def marker(f,x,y, *, color=P.purple, radius=3, filled=True, shape="circle"):
    fill=color if filled else P.white
    if shape=="circle":
        f.circle(x,y,radius,stroke=color,fill=fill,width=.9)
    elif shape=="square":
        f.box(x-radius,y-radius,2*radius,2*radius,radius=0,stroke=color,fill=fill,line_width=.9)
    elif shape in ("diamond","triangle"):
        points=([(x,y-radius*1.2),(x+radius*1.2,y),(x,y+radius*1.2),(x-radius*1.2,y)]
                if shape=="diamond" else [(x,y-radius*1.25),(x+radius*1.1,y+radius),(x-radius*1.1,y+radius)])
        f.polyline(points,color=color,fill=fill,close=True,width=.9)
    else:
        raise ValueError(f"Unknown marker: {shape}")


def legend_item(f,x,y,label,color, *, dash=None, shape=None, size=10):
    """y is the baseline of the label."""
    if shape:
        marker(f,x+6,y-3,color=color,shape=shape,radius=3)
    else:
        f.line((x,y-3),(x+15,y-3),color=color,width=1.5,dash=dash)
    f.text(x+22,y,label,size=size)


def pareto_frontier(cost,score):
    """Indices nondominated under minimum cost / maximum score, sorted by cost.

    Equal duplicate points are both nondominated; ties with a worse score are not.
    """
    cost,score=list(cost),list(score)
    if len(cost)!=len(score) or not cost:
        raise ValueError("Pareto inputs need equal nonzero lengths")
    finite(*cost,*score)
    return sorted([i for i,(c,s) in enumerate(zip(cost,score))
                   if not any(c2<=c and s2>=s and (c2<c or s2>s)
                              for c2,s2 in zip(cost,score))],key=lambda i:cost[i])


def ring_segment(f,cx,cy,inner,outer,start,end,color):
    """Native cubic-arc annular sector; angles in radians, clockwise from +x."""
    finite(cx,cy,inner,outer,start,end)
    if not 0 < inner < outer or not 0 < end-start <= 2*pi+1e-9:
        raise ValueError("Invalid annular sector radii or angle span")
    path=f.c.beginPath()
    def point(r,a):
        return cx+r*cos(a),cy+r*sin(a)
    path.moveTo(*f.xy(*point(outer,start)))
    def arc(r,a,b):
        count=max(1,ceil(abs(b-a)/(pi/2)))
        for i in range(count):
            u=a+(b-a)*i/count
            v=a+(b-a)*(i+1)/count
            k=4/3*tan((v-u)/4)
            x1,y1=point(r,u)
            x2,y2=point(r,v)
            path.curveTo(*f.xy(x1-k*r*sin(u),y1+k*r*cos(u)),
                         *f.xy(x2+k*r*sin(v),y2-k*r*cos(v)),*f.xy(x2,y2))
    arc(outer,start,end)
    path.lineTo(*f.xy(*point(inner,end)))
    arc(inner,end,start)
    path.close()
    f.c.saveState()
    f.c.setFillColor(HexColor(color))
    f.c.setStrokeColor(HexColor(P.white))
    f.c.setLineWidth(.8)
    f.c.drawPath(path,stroke=1,fill=1)
    f.c.restoreState()


def nested_donut(f,cx,cy,groups, *, inner=45, split=75, outer=101):
    """groups: [{label, color, children: [{label, value, color}]}].

    Parent spans are derived from children, ensuring both rings share boundaries.
    Returns segment centers for optional external labels.
    """
    if not groups or not 0<inner<split<outer:
        raise ValueError("Donut needs groups and increasing positive radii")
    counts=[]
    for group in groups:
        children=group["children"]
        if not children:
            raise ValueError("Each group needs children")
        values=[child["value"] for child in children]
        finite(*values)
        if any(v<=0 for v in values):
            raise ValueError("Donut values must be positive; omit zero-valued segments")
        counts.append(sum(values))
    total=sum(counts)
    a=-pi/2
    result=[]
    for group,count in zip(groups,counts):
        b=a+2*pi*count/total
        ring_segment(f,cx,cy,inner,split,a,b,group["color"])
        start=a
        for child in group["children"]:
            end=start+2*pi*child["value"]/total
            ring_segment(f,cx,cy,split,outer,start,end,child["color"])
            mid=(start+end)/2
            result.append(dict(label=child["label"],value=child["value"],
                               angle=mid,x=cx+(split+outer)/2*cos(mid),y=cy+(split+outer)/2*sin(mid)))
            start=end
        a=b
    return total,result


def footer(f, *, detail=None):
    f.line((14,f.height-31),(f.width-14,f.height-31),color=P.border,width=.6)
    f.text(16,f.height-13,DEMO_NOTE,size=9,color=P.muted)
    if detail:
        f.text(f.width-16,f.height-13,detail,size=9,color=P.muted,align="right")


def bar_matrix(f,x,y,width,labels,columns,colors, *, row_height=19,label_width=147):
    """Aligned horizontal bar panels with independent, explicitly labelled units.

    columns: [{title: [lines], maximum, ticks, format, values: [number | None |
              {value, low, high}]}]. None draws an em dash, never a false zero.
    Returns bottom y including ticks. Magnitudes start at zero in every panel.
    """
    n=len(labels)
    if not n or len(colors)!=n or not columns:
        raise ValueError("Matrix needs rows, one color per row, and columns")
    col_width=(width-label_width)/len(columns)
    if col_width<55:
        raise ValueError("Matrix columns are too narrow; widen or split the figure")
    top=y+47
    for i,label in enumerate(labels):
        f.text(x+5,top+(i+.5)*row_height+3.3,label,size=10,max_width=label_width-12)
    for j,column in enumerate(columns):
        if len(column["values"])!=n:
            raise ValueError("Matrix column length does not match row labels")
        left=x+label_width+j*col_width
        f.lines(left+col_width/2,y+15,column["title"],size=10.5,align="center",leading=12)
        f.line((left+9,y+38),(left+col_width-9,y+38),color=P.border,width=.7)
        show_values=column.get("show_values",False)
        axis=Axes(f,left+10,top,col_width-(46 if show_values else 27),n*row_height,(0,column["maximum"]),(-.5,n-.5))
        for i,(cell,color) in enumerate(zip(column["values"],colors)):
            yy=n-1-i
            if cell is None:
                f.text(left+col_width/2,axis.sy(yy)+3,"—",size=10,align="center",color=P.muted)
                continue
            estimate=cell["value"] if isinstance(cell,dict) else cell
            interval=(cell["low"],cell["high"]) if isinstance(cell,dict) and "low" in cell else None
            axis.hbar(yy,estimate,height=.29,color=color,interval=interval)
            if show_values:
                f.text(left+col_width-3,axis.sy(yy)+3.3,f"+{estimate:g}",size=9,align="right")
        fmt=column.get("format",lambda v:f"{v:g}")
        for value in column.get("ticks",(0,column["maximum"])):
            f.text(axis.sx(value),top+n*row_height+14,fmt(value),size=9,color=P.muted,align="center")
    return top+n*row_height+20


def gain_table(f,x,y,width,rows, *, title, max_gain=20,row_height=24):
    """Rows contain model, benchmark, n, before, after (percent). Gains are pp."""
    height=69+len(rows)*row_height
    f.box(x,y,width,height,fill=P.white,alpha=.53,stroke=P.border,radius=7)
    f.text(x+12,y+21,title,size=12,bold=True)
    fractions=(.02,.28,.46,.55,.76,.88)
    cols=[x+width*t for t in fractions]
    for pos,label in zip(cols,("Model","Benchmark","n","Before → after","Gain","Δ (pp)")):
        f.text(pos,y+44,label,size=9,color=P.muted)
    f.line((x+12,y+53),(x+width-12,y+53),color=P.border,width=.6)
    scale=Scale(0,max_gain,cols[5],x+width-17)
    for i,row in enumerate(rows):
        yy=y+72+i*row_height
        before,after=row["before"],row["after"]
        finite(before,after,row["n"])
        if not (0<=before<=after<=100) or row["n"]<=0 or int(row["n"])!=row["n"]:
            raise ValueError("Gain table needs percentages, after >= before and positive integer n; use forest for signed gains")
        gain=after-before
        end=scale(gain)
        for pos,value,limit in ((cols[0],row["model"],width*.24),(cols[1],row["benchmark"],width*.16),
                                (cols[2],row["n"],width*.07)):
            f.text(pos,yy,value,size=10,max_width=limit)
        f.text(cols[3],yy,f"{before:.1f} → {after:.1f}",size=10)
        f.text(cols[4],yy,f"+{gain:.1f}",size=10,bold=True,color=P.green)
        f.box(cols[5],yy-6,x+width-17-cols[5],5,fill="#E8E5ED",stroke=None,radius=2)
        f.box(cols[5],yy-6,end-cols[5],5,fill=P.green,stroke=None,radius=2)
    return y+height


def forest(f,x,y,width,rows, *, limits=(-10,20),ticks=(-10,0,10,20),row_height=24,label_width=176):
    """Signed effects and caller-provided bounds; zero remains visible."""
    if not limits[0]<0<limits[1] or not rows:
        raise ValueError("Forest limits must straddle zero and rows must be nonempty")
    axis=Axes(f,x+label_width,y,width-label_width-75,len(rows)*row_height,limits,(-.5,len(rows)-.5))
    axis.frame(xticks=ticks,grid=False,size=9)
    f.line((axis.sx(0),y),(axis.sx(0),y+len(rows)*row_height),color=P.muted,dash=(3,3),width=.75)
    for i,row in enumerate(rows):
        yy=len(rows)-1-i
        color=P.green if row["value"]>=0 else P.rust
        axis.error(row["value"],yy,row["low"],row["high"],horizontal=True,color=color,cap=3)
        axis.dot(row["value"],yy,color=color,radius=3)
        baseline=axis.sy(yy)+3.3
        f.text(x,baseline,row["label"],size=10,max_width=label_width-12)
        f.text(x+width,baseline,f"{row['value']:+.1f} pp",size=10,align="right",color=color)
    return y+len(rows)*row_height+20
