"""Reusable deterministic pen strokes for editable scientific diagrams.

The small normal displacement is computed from geometry, so rerendering the
same scene yields the same path. Fills and text stay crisp; only contours and
connectors carry the controlled hand-drawn irregularity.
"""
from __future__ import annotations

import math

from matplotlib import patches
from matplotlib.path import Path


def _samples(points, *, closed=False, amplitude=.32, step=4.5):
    out = []
    segments = list(zip(points, points[1:] + ([points[0]] if closed else [])))
    phase = points[0][0] * .071 + points[0][1] * .113
    for segment, (start, end) in enumerate(segments):
        dx, dy = end[0] - start[0], end[1] - start[1]
        length = math.hypot(dx, dy)
        count = max(1, math.ceil(length / step))
        nx, ny = (-dy / length, dx / length) if length else (0.0, 0.0)
        for i in range(count):
            t = i / count
            wave = (math.sin((i + segment * 7) * .43 + phase) * .63 +
                    math.sin((i + segment * 5) * .91 + phase * .43) * .37)
            offset = amplitude * math.sin(math.pi * t) * wave
            out.append((start[0] + dx * t + nx * offset,
                        start[1] + dy * t + ny * offset))
    if not closed:
        out.append(points[-1])
    return out


def polygon(ax, points, *, fill, edge="#26303A", lw=1.25, zorder=5,
            amplitude=.32, step=4.5, linestyle="solid"):
    """Filled vector polygon with softly uneven, fully editable outlines."""
    points = [tuple(map(float, point)) for point in points]
    vertices = _samples(points, closed=True, amplitude=amplitude, step=step)
    path = Path(vertices + [vertices[0]],
                [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 1) + [Path.CLOSEPOLY])
    result = patches.PathPatch(path, facecolor=fill, edgecolor=edge,
                               linewidth=lw, linestyle=linestyle,
                               joinstyle="round", capstyle="round",
                               zorder=zorder)
    ax.add_patch(result)
    return result


def line(ax, points, *, color="#26303A", lw=1.4, zorder=6,
         amplitude=.34, step=4.5, linestyle="solid"):
    points = [tuple(map(float, point)) for point in points]
    vertices = _samples(points, amplitude=amplitude, step=step)
    path = Path(vertices, [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 1))
    result = patches.PathPatch(path, facecolor="none", edgecolor=color,
                               linewidth=lw, linestyle=linestyle,
                               joinstyle="round", capstyle="round", zorder=zorder)
    ax.add_patch(result)
    return result


def ellipse(ax, x, y, rx, ry, *, fill, edge="#26303A", lw=1.35,
            zorder=5, amplitude=.34):
    count = max(32, int(math.pi * (rx + ry) / 3.8))
    pts = []
    for i in range(count):
        a = 2 * math.pi * i / count
        wobble = amplitude * (.54 * math.sin(9 * a + x * .03) +
                              .46 * math.sin(17 * a + y * .04))
        pts.append((x + (rx + wobble) * math.cos(a),
                    y + (ry + wobble) * math.sin(a)))
    return polygon(ax, pts, fill=fill, edge=edge, lw=lw, zorder=zorder,
                   amplitude=0, step=1000)


def bezier_shape(ax, start, segments, *, fill, edge="#26303A",
                 lw=1.35, zorder=5, amplitude=.20):
    """Closed, pen-drawn silhouette from reusable cubic Bezier segments."""
    points=[tuple(start)]
    previous=tuple(start)
    for c1,c2,end in segments:
        for i in range(1,9):
            t=i/8
            u=1-t
            points.append((u**3*previous[0]+3*u*u*t*c1[0]+
                           3*u*t*t*c2[0]+t**3*end[0],
                           u**3*previous[1]+3*u*u*t*c1[1]+
                           3*u*t*t*c2[1]+t**3*end[1]))
        previous=tuple(end)
    return polygon(ax, points, fill=fill, edge=edge,
                   lw=lw, zorder=zorder, amplitude=amplitude,
                   step=1000)


def bezier_line(ax, start, segments, *, color="#26303A", lw=1.35,
                zorder=6, amplitude=.22):
    """Open cubic pen stroke for braces and organic connectors."""
    points=[tuple(start)]
    previous=tuple(start)
    for c1,c2,end in segments:
        for i in range(1,9):
            t=i/8
            u=1-t
            points.append((u**3*previous[0]+3*u*u*t*c1[0]+
                           3*u*t*t*c2[0]+t**3*end[0],
                           u**3*previous[1]+3*u*u*t*c1[1]+
                           3*u*t*t*c2[1]+t**3*end[1]))
        previous=tuple(end)
    return line(ax,points,color=color,lw=lw,zorder=zorder,
                amplitude=amplitude,step=1000)


def rect(ax, x, y, w, h, *, fill, edge="#26303A", lw=1.35,
         radius=2, zorder=5, amplitude=.32, linestyle="solid"):
    """A nearly square hand-drawn card; radius only softens its corners."""
    r = min(max(radius, 0), w / 4, h / 4)
    points=[]
    for cx,cy,lo,hi in ((x+w-r,y+r,-math.pi/2,0),
                        (x+w-r,y+h-r,0,math.pi/2),
                        (x+r,y+h-r,math.pi/2,math.pi),
                        (x+r,y+r,math.pi,3*math.pi/2)):
        for i in range(5):
            a=lo+(hi-lo)*i/4
            points.append((cx+r*math.cos(a),cy+r*math.sin(a)))
    return polygon(ax, points, fill=fill, edge=edge, lw=lw,
                   zorder=zorder, amplitude=amplitude, linestyle=linestyle)


def arrow(ax, x1, y1, x2, y2, *, color="#26303A", lw=1.45,
          curve=0.0, zorder=7, head=7.0, amplitude=.35,
          linestyle="solid"):
    """Bezier connector with a separately editable triangular arrow head."""
    dx, dy = x2-x1, y2-y1
    length = math.hypot(dx, dy)
    if length < 1:
        return None
    nx, ny = -dy/length, dx/length
    control = ((x1+x2)/2+nx*curve*length, (y1+y2)/2+ny*curve*length)
    count = max(8, math.ceil(length/6))
    pts = []
    for i in range(count+1):
        t = i/count
        bx = (1-t)**2*x1+2*(1-t)*t*control[0]+t*t*x2
        by = (1-t)**2*y1+2*(1-t)*t*control[1]+t*t*y2
        pts.append((bx,by))
    tx, ty = x2-control[0], y2-control[1]
    direction = math.hypot(tx,ty)
    ux, uy = tx/direction, ty/direction
    shaft_end = (x2-ux*head*.72, y2-uy*head*.72)
    pts[-1] = shaft_end
    shaft = line(ax, pts, color=color, lw=lw, zorder=zorder,
                 amplitude=amplitude, linestyle=linestyle)
    polygon(ax, [(x2,y2), (x2-ux*head-uy*head*.43,
                          y2-uy*head+ux*head*.43),
                 (x2-ux*head+uy*head*.43,
                  y2-uy*head-ux*head*.43)],
            fill=color, edge=color, lw=.5, zorder=zorder+1,
            amplitude=.15)
    return shaft


def prism(ax, x, y, w, h, *, fill="#B8DFCB", edge="#252B35",
          depth=.22, top=None, side=None, lw=1.3, zorder=6):
    """Three separate vector faces of a small latent-state prism."""
    d = min(w*depth, h*.50)
    top = top or "#F8F1C6"
    side = side or "#9AB3A4"
    front = [(x,y),(x+w-d,y),(x+w-d,y+h),(x,y+h)]
    cap = [(x,y),(x+d,y-d),(x+w,y-d),(x+w-d,y)]
    flank = [(x+w-d,y),(x+w,y-d),(x+w,y+h-d),(x+w-d,y+h)]
    polygon(ax, flank, fill=side, edge=edge, lw=lw, zorder=zorder)
    polygon(ax, front, fill=fill, edge=edge, lw=lw, zorder=zorder+1)
    polygon(ax, cap, fill=top, edge=edge, lw=lw, zorder=zorder+2)


def wash(ax, quadrilateral, top, bottom, *, bands=256, zorder=0):
    """Smooth looking vector colour wash in a four-corner region."""
    from matplotlib.colors import to_rgb
    a,b,c,d = quadrilateral
    top_rgb, bottom_rgb = to_rgb(top), to_rgb(bottom)
    for i in range(bands):
        t0,t1=i/bands,min(1,(i+1.4)/bands)
        mid=(i+.5)/bands
        color=tuple(top_rgb[k]*(1-mid)+bottom_rgb[k]*mid
                    for k in range(3))
        left0=(a[0]*(1-t0)+d[0]*t0,a[1]*(1-t0)+d[1]*t0)
        right0=(b[0]*(1-t0)+c[0]*t0,b[1]*(1-t0)+c[1]*t0)
        right1=(b[0]*(1-t1)+c[0]*t1,b[1]*(1-t1)+c[1]*t1)
        left1=(a[0]*(1-t1)+d[0]*t1,a[1]*(1-t1)+d[1]*t1)
        ax.add_patch(patches.Polygon([left0,right0,right1,left1],
                                      closed=True, facecolor=color,
                                      edgecolor="none", zorder=zorder))


def circle_wash(ax, x, y, radius, top, bottom, *, edge="#232B38",
                lw=1.8, zorder=4, bands=128):
    """Editable vertical colour wash clipped by a circular emblem."""
    from matplotlib.colors import to_rgb
    mask=patches.Circle((x,y),radius, transform=ax.transData)
    a,b=to_rgb(top),to_rgb(bottom)
    for i in range(bands):
        t=(i+.5)/bands
        color=tuple(a[k]*(1-t)+b[k]*t for k in range(3))
        strip=patches.Rectangle((x-radius,y-radius+2*radius*i/bands),
                                2*radius,2*radius*1.25/bands,
                                facecolor=color,edgecolor="none",zorder=zorder)
        strip.set_clip_path(mask)
        ax.add_patch(strip)
    ring=patches.Circle((x,y),radius,facecolor="none",
                         edgecolor=edge,lw=lw,zorder=zorder+1)
    ax.add_patch(ring)
    return ring


def brace(ax, x, y1, y2, *, side="left", color="#26303A",
          lw=1.35, zorder=7):
    """Editable grouping brace with a centered hook toward grouped items."""
    sign=-1 if side=="left" else 1
    mid=(y1+y2)/2
    return bezier_line(ax,(x+sign*8,y1),[
        ((x+sign*2,y1),(x,y1+4),(x,y1+10)),
        ((x,y1+20),(x,mid-14),(x+sign*7,mid)),
        ((x,mid+14),(x,y2-20),(x,y2-10)),
        ((x,y2-4),(x+sign*2,y2),(x+sign*8,y2)),
    ],color=color,lw=lw,zorder=zorder,amplitude=.12)
