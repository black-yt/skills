"""Reusable native draw.io groups for scientific method diagrams."""
from __future__ import annotations

import math
from pathlib import Path
from drawio import INK, gear_points, stencil_xml

ICON_ROOT=Path(__file__).resolve().parents[1]/"assets/icons"

def native_icon(d,name,icon,x,y,size,*,color=INK,fill="none",parent="1",sw=2):
    shape=stencil_xml((ICON_ROOT/(icon+".shape.xml")).read_text(encoding="utf-8"))
    return d.shape(name,x,y,size,size,kind=shape,fill=fill,stroke=color,sw=sw,parent=parent,sketch=False)

GREEN = "#ABD49F"
TEAL = "#96C7C4"
YELLOW = "#E9E7A0"
MINT = "#B9DDC9"


def card(d, name, x, y, w, h, text="", *, fill=GREEN, size=15,
         stroke="#4D7048", bold=True, kind="rectangle", parent="1"):
    group=d.group(name,x,y,w,h,parent=parent)
    d.shape(name+"-body",0,0,w,h,kind=kind,fill=fill,stroke=stroke,
            rounded=1,arcSize=8,parent=group)
    if text:
        d.text(name+"-label",7,4,w-14,h-8,text,size=size,bold=bold,parent=group)
    return group


def document(d,name,x,y,w,h,text,*,size=14,parent="1",fill=GREEN):
    group=d.group(name,x,y,w,h,parent=parent)
    d.shape(name+"-sheet",0,0,w,h,kind="note",fill=fill,stroke="#466942",
            size=min(16,h*.23),parent=group)
    d.text(name+"-label",7,5,w-17,h-10,text,size=size,bold=True,parent=group)
    return group


def cube(d,name,x,y,w=46,h=36,*,fill=MINT,parent="1"):
    group=d.group(name,x,y,w,h,parent=parent)
    depth=min(w*.29,h*.35)
    d.polygon(name+"-front",[(0,depth),(w-depth,depth),(w-depth,h),(0,h)],
              fill=fill,stroke="#283A33",sw=1.7,parent=group)
    d.polygon(name+"-top",[(0,depth),(depth,0),(w,0),(w-depth,depth)],
              fill="#F4F0C4",stroke="#283A33",sw=1.7,parent=group)
    d.polygon(name+"-side",[(w-depth,depth),(w,0),(w,h-depth),(w-depth,h)],
              fill="#8FAFA1",stroke="#283A33",sw=1.7,parent=group)
    return group


def brain(d,name,x,y,size=80,parent="1"):
    group=d.group(name,x,y,size,size,parent=parent)
    d.contour(name+"-profile",0,0,size,size,
        '<move x="24" y="68"/><curve x1="8" y1="53" x2="10" y2="30" x3="24" y3="16"/>'
        '<curve x1="39" y1="2" x2="64" y2="5" x3="77" y3="19"/>'
        '<curve x1="89" y1="31" x2="84" y2="47" x3="85" y3="51"/>'
        '<line x="94" y="61"/><line x="81" y="67"/><line x="79" y="80"/>'
        '<line x="63" y="84"/><line x="66" y="97"/><line x="26" y="97"/>'
        '<line x="27" y="78"/><close/>',fill="#F4C48F",stroke="#2C548A",sw=2.2,parent=group)
    d.polygon(name+"-gear",gear_points(size*.50,size*.39,size*.30,12),
              fill="#48B5CD",stroke="#235A8D",sw=1.8,parent=group)
    d.contour(name+"-brain",size*.28,size*.17,size*.45,size*.45,
        '<move x="48" y="6"/><curve x1="32" y1="-2" x2="24" y2="8" x3="24" y3="18"/>'
        '<curve x1="7" y1="14" x2="0" y2="29" x3="9" y3="43"/>'
        '<curve x1="-2" y1="53" x2="6" y2="72" x3="20" y3="73"/>'
        '<curve x1="23" y1="91" x2="39" y2="99" x3="50" y3="88"/>'
        '<curve x1="64" y1="101" x2="80" y2="91" x3="79" y3="78"/>'
        '<curve x1="97" y1="77" x2="103" y2="57" x3="91" y3="47"/>'
        '<curve x1="102" y1="32" x2="89" y2="15" x3="76" y3="18"/>'
        '<curve x1="74" y1="0" x2="56" y2="-3" x3="48" y3="6"/><close/>',
        fill="#F4AAC1",stroke="#2B5795",sw=1.7,parent=group)
    native_icon(d,name+"-tabler-brain","tabler-brain",size*.25,size*.12,size*.51,
                color="#854277",parent=group,sw=1.5)
    return group


def yarn(d,name,x,y,size=42,parent="1"):
    group=d.group(name,x,y,size,size,parent=parent)
    d.shape(name+"-base",size*.12,size*.12,size*.76,size*.76,kind="ellipse",
            fill="#F1B2C5",stroke="none",parent=group,sketch=False)
    native_icon(d,name+"-tabler-yarn","tabler-yarn",0,0,size,
                color="#7D4259",fill="none",parent=group,sw=2)
    return group


def snowflake(d,name,x,y,size=40,parent="1"):
    return native_icon(d,name,"tabler-snowflake",x,y,size,color="#2D7C9B",parent=parent,sw=1.8)


def phase(d,name,x,y,size=116,parent="1"):
    group=d.group(name,x,y,size,size,parent=parent)
    d.contour(name+"-day",0,0,size,size,
        '<move x="50" y="0"/><curve x1="-17" y1="0" x2="-17" y2="100" x3="50" y3="100"/><close/>',
        fill="#EF8658",stroke="none",sketch=False,parent=group)
    d.contour(name+"-night",0,0,size,size,
        '<move x="50" y="0"/><curve x1="117" y1="0" x2="117" y2="100" x3="50" y3="100"/><close/>',
        fill="#173B56",stroke="none",sketch=False,parent=group)
    d.shape(name+"-ring",0,0,size,size,kind="ellipse",fill="none",stroke=INK,sw=2.2,parent=group)
    d.shape(name+"-sun",size*.16,size*.39,size*.20,size*.20,kind="ellipse",fill="white",stroke="none",parent=group,sketch=False)
    for i in range(8):
        a=i*math.pi/4
        d.line(name+f"-ray-{i}",[(size*(.26+.15*math.cos(a)),size*(.49+.15*math.sin(a))),
                                 (size*(.26+.22*math.cos(a)),size*(.49+.22*math.sin(a)))],
               color="white",sw=1.8,parent=group)
    d.contour(name+"-moon",size*.57,size*.28,size*.34,size*.43,
        '<move x="70" y="0"/><curve x1="-25" y1="2" x2="-21" y2="100" x3="69" y3="99"/>'
        '<curve x1="12" y1="80" x2="11" y2="19" x3="70" y3="0"/><close/>',
        fill="white",stroke="none",sketch=False,parent=group)
    for i,(dx,dy) in enumerate(((.58,.19),(.82,.20),(.85,.75),(.62,.80))):
        d.shape(name+f"-star-{i}",size*dx,size*dy,3,3,kind="ellipse",fill="white",stroke="none",sketch=False,parent=group)
    return group


def buffer(d,name,x,y,w,h,title="Episodic Buffer",parent="1",fill="#E4D6EA",
           edge="#725A83",top="#F4EAF5"):
    group=d.group(name,x,y,w,h,parent=parent)
    rim=min(25,h*.24)
    d.shape(name+"-body",0,rim/2,w,h-rim,fill=fill,
            stroke=edge,sw=1.8,parent=group,sketch=False)
    d.shape(name+"-bottom",0,h-rim,w,rim,kind="ellipse",fill=fill,
            stroke=edge,sw=1.8,parent=group,sketch=False)
    d.shape(name+"-top",0,0,w,rim,kind="ellipse",fill=top,
            stroke=edge,sw=1.8,parent=group,sketch=False)
    d.text(name+"-title",8,0,w-16,rim,title,size=17,bold=True,parent=group)
    return group


def network(d,name,x,y,w=80,h=70,parent="1"):
    group=d.group(name,x,y,w,h,parent=parent)
    layers=[[(5,h*.24),(5,h*.50),(5,h*.76)],
            [(w*.48,h*.08),(w*.48,h*.36),(w*.48,h*.64),(w*.48,h*.92)],
            [(w-5,h*.28),(w-5,h*.72)]]
    for k in range(2):
        for i,a in enumerate(layers[k]):
            for j,b in enumerate(layers[k+1]):
                d.line(name+f"-link-{k}-{i}-{j}",[a,b],color="#525B64",sw=.8,parent=group)
    for k,layer in enumerate(layers):
        for i,(cx,cy) in enumerate(layer):
            d.shape(name+f"-node-{k}-{i}",cx-4,cy-4,8,8,kind="ellipse",
                    fill=("#D9B1D2","#E6C16C","#9ED1C2")[k],stroke=INK,sw=.9,parent=group)
    return group
