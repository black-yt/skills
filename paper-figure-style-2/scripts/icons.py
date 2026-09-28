"""Small vector icons with independent vivid accents; no bitmap assets."""
from math import cos, sin, pi
from style2 import tint


# Semantic icon colors stay independent of the pastel group and phase colors.
ICON_PALETTES = {
    "terminal": ("#242526", "#6268C6"),
    "code": ("#438C98", "#68C6DC"),
    "screen": ("#4C7CEF", "#A5A3F0"),
    "cube": ("#0879FA", "#61CEF2"),
    "sandbox": ("#12BD8C", "#9FE3CE"),
    "network": ("#168EF0", "#17BAD0"),
    "loop": ("#709EDD", "#EA5C6F"),
    "tools": ("#407FE4", "#56B8E6"),
    "search": ("#70CDE2", "#F2C34E"),
    "robot": ("#8273CF", "#ADA0EB"),
    "model": ("#8273CF", "#ADA0EB"),
    "document": ("#637486", "#41B1B5"),
    "report": ("#147F8C", "#F2C34E"),
    "science": ("#3C728A", "#D6B270"),
    "records": ("#85B8AE", "#D25D7D"),
    "sliders": ("#5074E8", "#6CC04A"),
    "schedule": ("#5074E8", "#6CC04A"),
    "adapter": ("#EE009B", "#FFABE4"),
    "chart": ("#19628A", "#F0C94F"),
    "analysis": ("#467D91", "#E1B451"),
    "clock": ("#594C9C", "#EAC84E"),
    "play": ("#292A26", "#F2D164"),
    "trash": ("#FF6060", "#DC3C3C"),
    "folder": ("#DFC04F", "#57B9C8"),
}


def draw_icon(d, name, x, y, *, size=30, color=None, accent=None):
    if name not in ICON_PALETTES:
        raise ValueError(f"Unknown vector icon: {name}")
    primary, secondary = ICON_PALETTES[name]
    # An explicit primary alone requests a coherent two-tone override.
    accent = accent if accent is not None else (secondary if color is None else tint(color, .32))
    color = primary if color is None else color
    def xy(a, b): return x+a*size, y+b*size
    def line(points, *, stroke=None, **kw): d.line([xy(a,b) for a,b in points], color=color if stroke is None else stroke, lw=1.5, **kw)
    def rect(a,b,w,h, **kw): return d.rect(*xy(a,b), w*size, h*size, **kw)
    def circle(a,b,r, **kw): return d.circle(*xy(a,b), r*size, **kw)
    pale = tint(color, .18)
    if name in ("terminal", "code", "screen"):
        rect(.06,.13,.88,.7,fill=color,edge=color,radius=size*.08)
        if name=="terminal":
            rect(.11,.16,.78,.06,fill=accent,edge=None)
            d.line([xy(.2,.34),xy(.36,.48),xy(.2,.62)],color="white",lw=2)
            d.line([xy(.49,.65),xy(.73,.65)],color="white",lw=2)
        else:
            rect(.13,.24,.74,.49,fill=tint(accent,.25),edge=None)
            line([(.4,.35),(.27,.47),(.4,.59)])
            line([(.6,.35),(.73,.47),(.6,.59)])
        line([(.32,.96),(.68,.96)])
        line([(.5,.83),(.5,.96)])
    elif name in ("cube", "sandbox"):
        rect(.02,.02,.96,.96,fill=color,edge=None,radius=size*.19)
        d.polygon([xy(.5,.18),xy(.8,.35),xy(.5,.52),xy(.2,.35)],fill="white",edge=pale)
        d.polygon([xy(.2,.35),xy(.5,.52),xy(.5,.83),xy(.2,.65)],fill=pale,edge="white")
        d.polygon([xy(.5,.52),xy(.8,.35),xy(.8,.65),xy(.5,.83)],fill=accent,edge="white")
    elif name in ("network", "loop", "tools", "search"):
        if name=="search":
            circle(.41,.41,.29,fill=tint(color,.8),edge=color,lw=1.5)
            d.line([xy(.62,.63),xy(.9,.94)],color="#38444C",lw=4)
            line([(.13,.41),(.7,.41)],stroke="white")
            line([(.41,.13),(.41,.7)],stroke="white")
            circle(.41,.41,.17,fill=None,edge="white",lw=.6)
            d.polygon([xy(.83,.04),xy(.87,.14),xy(.98,.18),xy(.87,.22),xy(.83,.33),xy(.79,.22),xy(.68,.18),xy(.79,.14)],fill=accent,edge=None)
        else:
            center=(.5,.5)
            points=[(.5+.34*cos(a),.5+.34*sin(a)) for a in (0,2*pi/3,4*pi/3)]
            for p in points: line([center,p])
            if name=="loop":
                circle(.5,.5,.37,fill=None,edge=accent,lw=2)
            circle(.5,.5,.13,fill=color,edge="white")
            for a,b in points: circle(a,b,.115,fill=accent,edge=color,lw=1)
    elif name in ("robot", "model"):
        line([(.5,.07),(.5,.24)])
        circle(.5,.06,.05,fill=accent,edge=None)
        rect(.12,.26,.76,.49,fill=accent,edge=color,radius=size*.1)
        for a in (.33,.67): circle(a,.45,.07,fill="white",edge=None)
        line([(.32,.64),(.68,.64)],stroke="white")
        line([(.2,.85),(.8,.85)])
    elif name in ("document", "report", "science", "records"):
        rect(.17,.04,.68,.88,fill=color if name=="report" else pale,edge=color,radius=size*.03)
        for b,w in ((.27,.4),(.42,.4),(.57,.25),(.72,.34)):
            line([(.28,b),(.28+w,b)],stroke=tint(color,.25) if name=="report" else color)
        if name=="report":
            d.polygon([xy(.67,.04),xy(.85,.22),xy(.67,.22)],fill=accent,edge=None)
            circle(.29,.83,.085,fill=accent,edge=None)
        elif name=="records":
            rect(.23,.13,.56,.09,fill=color,edge=None)
            rect(.5,.52,.2,.26,fill=accent,edge=None)
        if name=="science":
            circle(.7,.72,.22,fill=tint(accent,.35),edge=accent)
            line([(.6,.72),(.68,.8),(.81,.62)])
    elif name in ("sliders", "schedule"):
        rect(.04,.05,.92,.9,fill=color,edge=None,radius=size*.18)
        for yy,xx in ((.28,.36),(.53,.67),(.78,.42)):
            d.line([xy(.17,yy),xy(.83,yy)],color="white",lw=1.5)
            circle(xx,yy,.09,fill=accent,edge="white",lw=1.5)
    elif name=="adapter":
        rect(.04,.05,.92,.9,fill=color,edge=None,radius=size*.18)
        rect(.23,.18,.54,.64,fill=None,edge="white",radius=size*.08)
        line([(.35,.7),(.35,.52),(.65,.36)],stroke="white")
        for a,b in ((.35,.7),(.35,.52),(.65,.36)):
            circle(a,b,.055,fill=accent,edge="white",lw=1)
    elif name in ("chart", "analysis"):
        rect(.05,.08,.9,.8,fill=pale,edge=color,radius=size*.04)
        for i,(xx,hh) in enumerate(((.19,.2),(.41,.44),(.63,.59))):
            rect(xx,.76-hh,.13,hh,fill=accent if i==1 else color,edge=None)
    elif name in ("clock", "play"):
        circle(.5,.5,.42,fill=tint(accent,.22),edge=color,lw=2)
        if name=="clock": line([(.5,.21),(.5,.5),(.73,.61)])
        else: d.polygon([xy(.4,.27),xy(.4,.74),xy(.73,.5)],fill=color,edge=None)
    elif name=="trash":
        d.polygon([xy(.24,.27),xy(.76,.27),xy(.69,.95),xy(.31,.95)],fill=color,edge=None)
        line([(.1,.19),(.9,.19)],stroke=accent)
        line([(.38,.08),(.62,.08)],stroke=accent)
        for a in (.43,.57): d.line([xy(a,.39),xy(a,.79)],color="white",lw=1.6)
    elif name=="folder":
        d.polygon([xy(.07,.2),xy(.41,.2),xy(.51,.33),xy(.93,.33),xy(.93,.86),xy(.07,.86)],fill=pale,edge=color)
        line([(.09,.43),(.9,.43)],stroke=accent)
