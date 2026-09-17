"""Small reusable outline icons, drawn from geometric primitives, not font glyphs.

Coordinates are centered on (x,y); normalized artboards are 24 × 24.
All paths below are independently constructed and configurable at call time.
"""
from __future__ import annotations


def draw_icon(f, name, x, y, *, size=16, color="#584B9A"):
    s=size/24
    def p(a,b): return (x+(a-12)*s,y+(b-12)*s)
    def line(points, **kw):
        f.polyline([p(*pt) for pt in points],color=color,width=1.7*s,**kw)
    def circle(a,b,r,fill=None): f.circle(*p(a,b),r*s,stroke=color,fill=fill,width=1.6*s)
    def box(a,b,w,h,fill=None): f.box(*p(a,b),w*s,h*s,fill=fill,stroke=color,radius=.7*s,line_width=1.6*s)
    if name in ("code","workspace"):
        if name=="workspace": box(1,3,22,18)
        line([(8,7),(4,12),(8,17)])
        line([(16,7),(20,12),(16,17)])
        line([(14,4),(10,20)])
    elif name=="folder":
        line([(2,21),(2,3),(9,3),(12,7),(22,7),(22,21)],close=True)
        line([(5,11),(19,11)])
    elif name=="document":
        line([(6,2),(15,2),(20,7),(20,22),(6,22)],close=True)
        line([(15,2),(15,7),(20,7)])
        for yy in (11,15,19): line([(9,yy),(16,yy)])
    elif name=="cube":
        line([(12,2),(22,7),(22,17),(12,23),(2,17),(2,7)],close=True)
        line([(2,7),(12,12),(22,7)])
        line([(12,12),(12,23)])
    elif name=="flask":
        line([(9,2),(15,2)])
        line([(10,2),(10,10),(4,21),(5,23),(19,23),(20,21),(14,10),(14,2)])
        line([(8,15),(16,15)])
        circle(11,19,.6,fill=color)
    elif name=="shield":
        line([(12,2),(21,5),(19,16),(12,24),(5,16),(3,5)],close=True)
        line([(7,13),(11,17),(17,9)])
    elif name=="expert":
        circle(12,5,3.7)
        line([(3,24),(5,15),(9,12),(15,12),(19,15),(21,24)])
        line([(7,14),(12,19),(17,14)])
        line([(10,13),(12,21),(14,13)])
    elif name=="robot":
        box(4,7,16,12)
        line([(12,7),(12,3)])
        circle(12,2,1.1)
        circle(8,12,.9,fill=color); circle(16,12,.9,fill=color)
        line([(9,16),(15,16)])
        line([(1,14),(4,14)]); line([(20,14),(23,14)])
        line([(6,22),(18,22)])
    elif name=="search":
        circle(9,9,6)
        line([(14,14),(21,21)])
    elif name=="layers":
        line([(12,3),(22,8),(12,13),(2,8)],close=True)
        line([(3,12),(12,17),(21,12)])
        line([(3,16),(12,21),(21,16)])
    elif name=="pencil":
        line([(3,21),(5,14),(17,2),(22,7),(10,19)],close=True)
        line([(14,5),(19,10)])
        line([(5,14),(10,19)])
    elif name=="bolt":
        line([(13,1),(5,14),(11,14),(9,24),(20,10),(14,10)],close=True)
    elif name=="target":
        for r in (10,6,2): circle(12,12,r)
    elif name=="network":
        line([(12,4),(6,18),(19,18),(12,4)])
        for a,b in ((12,4),(6,18),(19,18)): circle(a,b,2.6,fill=color)
    elif name=="refresh":
        f.curve([p(3,11),p(4,0),p(18,0),p(21,8)],color=color,width=1.8*s)
        f.curve([p(21,13),p(20,25),p(6,25),p(3,16)],color=color,width=1.8*s)
        line([(21,2),(21,8),(15,8)])
        line([(3,22),(3,16),(9,16)])
    elif name=="bars":
        line([(2,2),(2,22),(23,22)])
        for a,b,w,h in ((6,12,3,10),(12,16,3,6),(18,5,3,17)): box(a,b,w,h,fill=color)
    elif name=="check":
        line([(4,12),(9,17),(20,5)])
    elif name=="cross":
        line([(6,6),(18,18)]); line([(18,6),(6,18)])
    elif name=="minus":
        line([(5,12),(19,12)])
    else:
        raise ValueError(f"Unknown icon: {name}")


def pipeline_illustration(f, name, cx, cy):
    """Larger layered illustrations composed from the same small vector marks."""
    from style1 import P
    if name=="repository":
        f.box(cx-11,cy-28,34,41,fill="#F7FAFD",stroke="#97ACBC",radius=3,line_width=.7)
        f.box(cx-17,cy-23,32,40,fill=P.white,stroke=P.blue,radius=3,line_width=.8)
        f.line((cx-12,cy-14),(cx+7,cy-14),color=P.blue,width=.7)
        f.polyline([(cx-30,cy+23),(cx-30,cy-14),(cx-9,cy-14),(cx-1,cy-7),
                    (cx+30,cy-7),(cx+30,cy+23)],color=P.blue,fill="#E9F0F8",width=1.3,close=True)
        f.icon("code",cx,cy+6,size=16,color=P.blue)
        f.circle(cx+30,cy+17,9,stroke="#98B397",fill=P.white,width=.65)
        f.icon("check",cx+30,cy+17,size=12,color=P.green)
    elif name=="package":
        f.polyline([(cx-19,cy-8),(cx+2,cy-20),(cx+23,cy-8),(cx+2,cy+4)],
                   color=P.rust,fill="#FAEDE4",width=1.2,close=True)
        f.polyline([(cx-19,cy-8),(cx+2,cy+4),(cx+2,cy+28),(cx-19,cy+16)],
                   color=P.rust,fill="#F5E3D5",width=1.2,close=True)
        f.polyline([(cx+2,cy+4),(cx+23,cy-8),(cx+23,cy+16),(cx+2,cy+28)],
                   color=P.rust,fill="#F9EBDD",width=1.2,close=True)
        f.circle(cx-26,cy-11,14,stroke="#CBA890",fill=P.white,width=.6)
        f.icon("expert",cx-26,cy-12,size=23,color=P.rust)
        f.box(cx+14,cy-9,23,32,fill=P.white,stroke="#B78C70",radius=2,line_width=.65)
        for yy in (-1,8,17):
            f.icon("check",cx+21,cy+yy,size=8,color=P.rust)
            f.line((cx+27,cy+yy),(cx+33,cy+yy),color="#B78C70",width=.6)
    elif name=="recipe":
        f.box(cx-24,cy-28,50,53,fill="#F2EFFA",stroke="#C9C1E1",radius=4,line_width=.7)
        f.box(cx-28,cy-32,50,53,fill=P.white,stroke=P.purple,radius=4,line_width=1.15)
        for yy,xx in ((-16,-8),(-3,6),(10,-13)):
            f.line((cx-20,cy+yy),(cx+13,cy+yy),color="#AFA5C9",width=.75)
            f.box(cx+xx-3,cy+yy-3,6,6,fill="#D8CFE9",stroke=P.purple,radius=.7,line_width=.65)
        f.circle(cx+27,cy-20,12,stroke="#B1A9CC",fill=P.white,width=.7)
        f.icon("network",cx+27,cy-20,size=20,color=P.purple)
    elif name=="validation":
        for x,y,color,edge in ((-16,-31,"#EDF4ED","#BED0BB"),(-21,-26,"#F5F8F3","#A9C0A3"),(-26,-21,P.white,P.green)):
            f.box(cx+x,cy+y,43,45,fill=color,stroke=edge,radius=4,line_width=.9)
        for yy in (-11,-1,9):
            f.icon("check",cx-16,cy+yy,size=8,color=P.green)
            f.line((cx-8,cy+yy),(cx+9,cy+yy),color="#A6BFA5",width=.7)
        f.circle(cx+22,cy+11,16,stroke="#CAD7C7",fill=P.white,width=.6)
        f.icon("shield",cx+22,cy+11,size=27,color=P.green)
    elif name=="interaction":
        f.box(cx-36,cy-27,72,49,fill=P.white,stroke=P.purple,radius=4,line_width=1.2)
        for xx in (-27,-20,-13): f.circle(cx+xx,cy-21,1.2,stroke=None,fill="#A5A2B0")
        f.line((cx-31,cy-16),(cx+31,cy-16),color="#CAC6D8",width=.65)
        f.icon("robot",cx-18,cy+2,size=22,color=P.purple)
        f.polyline([(cx+2,cy-4),(cx+10,cy-4),(cx+10,cy-8),(cx+27,cy-8)],color=P.teal,width=1.2)
        for xx,hh in ((5,5),(13,7),(21,10)):
            f.box(cx+xx,cy+17-hh,4,hh,fill="#D4E9E5",stroke=P.teal,radius=.3,line_width=.6)
    else:
        raise ValueError(name)
