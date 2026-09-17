"""Native-vector PDF primitives for paper-figure-style-1.

Coordinates use a 720-unit-wide artboard, with y increasing downwards.
Text y coordinates are baselines. Physical output size is independent of layout.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from math import atan2, cos, sin, radians

from matplotlib import font_manager
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


@dataclass(frozen=True)
class Palette:
    ink: str = "#16151C"
    muted: str = "#5C5C66"
    purple: str = "#584B9A"
    rust: str = "#A4592F"
    blue: str = "#4C6D91"
    green: str = "#537D58"
    teal: str = "#427F7D"
    border: str = "#CBCBD2"
    peach: str = "#FBF3EE"
    lavender: str = "#F3F2FC"
    midpoint: str = "#F6F2F5"
    white: str = "#FFFFFF"


P = Palette()


class Figure:
    """A single-page, editable-text PDF; all visual primitives stay vector.

    Fonts can be overridden with a regular and bold TrueType font pair. Missing
    glyphs and text running off the artboard fail before an output is finalized.
    """

    def __init__(self, output, height, *, width=720, width_in=7.2,
                 title="Scientific diagram", palette=P,
                 font_regular=None, font_bold=None):
        if min(width, height, width_in) <= 0:
            raise ValueError("Artboard dimensions and width_in must be positive")
        self.output = Path(output)
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.width, self.height = width, height
        self.p = palette
        self.scale = width_in * 72 / width
        self.c = canvas.Canvas(str(self.output), pagesize=(width*self.scale, height*self.scale),
                               pageCompression=1, invariant=1, pdfVersion=(1, 4))
        self.c.setTitle(title)
        self.c.setAuthor("paper-figure-style-1")
        self.c.setSubject("Paper diagram; native PDF shading and selectable Unicode text")
        self.c.scale(self.scale, self.scale)
        self.c.setLineJoin(1)
        self.c.setLineCap(1)
        self.fonts = {}
        for weight, override in (("regular", font_regular), ("bold", font_bold)):
            path = Path(override) if override else Path(font_manager.findfont(
                font_manager.FontProperties(family="DejaVu Sans", weight=weight),
                fallback_to_default=False))
            if not path.is_file():
                raise FileNotFoundError(path)
            # Register by resolved font file, allowing multiple Figure instances.
            import hashlib
            tag = "Style1-" + hashlib.sha256(str(path.resolve()).encode()).hexdigest()[:12]
            if tag not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(tag, str(path)))
            self.fonts[weight] = tag
        self._saved = False

    def xy(self, x, y):
        return x, self.height-y

    def _rounded_path(self, x, y, w, h, radius):
        """Soft quadratic-style corners with cubic control points at 2/3 radius."""
        r = min(radius, w/2, h/2)
        k = 2*r/3
        c = self.c.beginPath()
        c.moveTo(*self.xy(x+r, y))
        c.lineTo(*self.xy(x+w-r, y))
        c.curveTo(*self.xy(x+w-r+k, y), *self.xy(x+w, y+r-k), *self.xy(x+w, y+r))
        c.lineTo(*self.xy(x+w, y+h-r))
        c.curveTo(*self.xy(x+w, y+h-r+k), *self.xy(x+w-r+k, y+h), *self.xy(x+w-r, y+h))
        c.lineTo(*self.xy(x+r, y+h))
        c.curveTo(*self.xy(x+r-k, y+h), *self.xy(x, y+h-r+k), *self.xy(x, y+h-r))
        c.lineTo(*self.xy(x, y+r))
        c.curveTo(*self.xy(x, y+r-k), *self.xy(x+r-k, y), *self.xy(x+r, y))
        c.close()
        return c

    def box(self, x, y, w, h, *, fill=P.white, stroke=P.border,
            radius=6, line_width=.8, alpha=1):
        self.c.saveState()
        if fill:
            self.c.setFillColor(HexColor(fill))
        if stroke:
            self.c.setStrokeColor(HexColor(stroke))
        self.c.setFillAlpha(alpha)
        self.c.setStrokeAlpha(alpha)
        self.c.setLineWidth(line_width)
        self.c.drawPath(self._rounded_path(x,y,w,h,radius), stroke=int(bool(stroke)), fill=int(bool(fill)))
        self.c.restoreState()

    def gradient(self, x, y, w, h, *, colors=None, positions=None, radius=6):
        """A clipped PDF axial shading, never imshow() or an embedded bitmap."""
        colors = colors or (self.p.peach, self.p.midpoint, self.p.lavender)
        if len(colors) < 2:
            raise ValueError("A gradient needs at least two colors")
        positions = positions if positions is not None else [i/(len(colors)-1) for i in range(len(colors))]
        if len(positions) != len(colors) or list(positions) != sorted(positions):
            raise ValueError("A gradient needs at least two matching colors/stops")
        self.c.saveState()
        self.c.clipPath(self._rounded_path(x,y,w,h,radius), stroke=0, fill=0)
        self.c.linearGradient(x, 0, x+w, 0, [HexColor(v) for v in colors], positions=positions, extend=True)
        self.c.restoreState()

    def background(self):
        self.box(0,0,self.width,self.height,fill=P.white,stroke=None,radius=0)
        self.gradient(1,1,self.width-2,self.height-2)

    def zone(self, x, y, w, h, color=P.lavender):
        self.box(x,y,w,h,fill=color,stroke=None,alpha=.5)

    def header(self, title, *, brand=None):
        if brand:
            self.text(16,23.37,brand,size=12,color=self.p.purple)
            self.text(134,23.13,title,size=15)
        else:
            self.text(14,22.13,title,size=15,bold=True)
        self.line((14,36),(self.width-14,36),color=self.p.border,width=.7)

    def text(self, x, y, value, *, size=11, color=None, bold=False, align="left", max_width=None, angle=0):
        """Draw actual text at a baseline; refuse missing glyphs and overflow."""
        value = str(value)
        if "\n" in value:
            raise ValueError("Use lines() for multiline text")
        font = self.fonts["bold" if bold else "regular"]
        face = pdfmetrics.getFont(font).face
        missing = sorted({ch for ch in value if ord(ch) not in face.charWidths})
        if missing:
            raise ValueError(f"Font lacks glyphs {missing!r}; provide a suitable TrueType font")
        width = pdfmetrics.stringWidth(value,font,size)
        if align not in ("left","center","right"):
            raise ValueError("align must be left, center, or right")
        left = x - (width/2 if align=="center" else width if align=="right" else 0)
        if max_width is not None and width > max_width + .1:
            raise ValueError(f"Text exceeds its allocated width: {value!r} ({width:.1f} > {max_width})")
        if angle:
            ascent,descent=pdfmetrics.getAscentDescent(font,size)
            a=radians(angle)
            for dx in (left-x,left-x+width):
                for dy in (descent,ascent):
                    px,py=x+dx*cos(a)-dy*sin(a),y-dx*sin(a)-dy*cos(a)
                    if not (-.5 <= px <= self.width+.5 and -.5 <= py <= self.height+.5):
                        raise ValueError(f"Rotated text exceeds the artboard: {value!r}")
        elif left < -.5 or left+width > self.width+.5 or y > self.height or y-size < -2:
            raise ValueError(f"Text exceeds the artboard: {value!r}")
        self.c.saveState()
        self.c.setFont(font,size)
        self.c.setFillColor(HexColor(color or self.p.ink))
        if angle:
            self.c.translate(*self.xy(x,y))
            self.c.rotate(angle)
            self.c.drawString(left-x,0,value)
        else:
            self.c.drawString(*self.xy(left,y),value)
        self.c.restoreState()

    def lines(self, x, y, values, *, leading=13.5, **kwargs):
        if isinstance(values,str):
            values=values.splitlines()
        for i,value in enumerate(values):
            self.text(x,y+i*leading,value,**kwargs)

    def line(self, a, b, *, color=P.purple, width=.9, alpha=1, dash=None):
        self.polyline([a,b],color=color,width=width,alpha=alpha,dash=dash)

    def polyline(self, points, *, color=P.purple, width=.9, fill=None, close=False, alpha=1, dash=None):
        self.c.saveState()
        self.c.setStrokeColor(HexColor(color))
        self.c.setLineWidth(width)
        if fill:
            self.c.setFillColor(HexColor(fill))
        self.c.setStrokeAlpha(alpha)
        self.c.setFillAlpha(alpha)
        if dash:
            self.c.setDash(dash)
        p=self.c.beginPath()
        p.moveTo(*self.xy(*points[0]))
        for point in points[1:]:
            p.lineTo(*self.xy(*point))
        if close:
            p.close()
        self.c.drawPath(p,stroke=1,fill=int(bool(fill)))
        self.c.restoreState()

    def curve(self, points, *, color=P.purple, width=.9, arrow_at=None):
        if len(points)!=4:
            raise ValueError("A cubic curve needs four points")
        self.c.saveState()
        self.c.setLineWidth(width)
        self.c.setStrokeColor(HexColor(color))
        p=self.c.beginPath()
        p.moveTo(*self.xy(*points[0]))
        p.curveTo(*(v for point in points[1:] for v in self.xy(*point)))
        self.c.drawPath(p,stroke=1,fill=0)
        self.c.restoreState()
        if arrow_at is not None:
            if not 0 < arrow_at <= 1:
                raise ValueError("arrow_at must be a curve fraction in (0, 1]")
            def at(t):
                weights=((1-t)**3,3*(1-t)**2*t,3*(1-t)*t*t,t**3)
                return tuple(sum(w*point[d] for w,point in zip(weights,points)) for d in (0,1))
            self.arrow([at(max(0,arrow_at-.02)),at(arrow_at)],color=color,width=width,head=5)

    def circle(self, cx, cy, radius, *, stroke=P.purple, fill=None, width=.9):
        self.c.saveState()
        self.c.setLineWidth(width)
        if stroke:
            self.c.setStrokeColor(HexColor(stroke))
        if fill:
            self.c.setFillColor(HexColor(fill))
        self.c.circle(*self.xy(cx,cy),radius,stroke=int(bool(stroke)),fill=int(bool(fill)))
        self.c.restoreState()

    def arrow(self, points, *, color=P.purple, width=.95, head=4):
        """Straight or orthogonal connector; final segment determines arrowhead."""
        self.polyline(points,color=color,width=width)
        x,y=points[-1]
        px,py=points[-2]
        a=atan2(y-py,x-px)
        dx,dy=cos(a),sin(a)
        self.polyline([(x,y),(x-head*dx-head*.48*dy,y-head*dy+head*.48*dx),
                       (x-head*dx+head*.48*dy,y-head*dy-head*.48*dx)],
                      color=color,width=.4,fill=color,close=True)

    def icon(self, name, x, y, *, size=16, color=P.purple):
        from icons import draw_icon
        draw_icon(self,name,x,y,size=size,color=color)

    def save(self):
        if self._saved:
            raise RuntimeError("Figure already saved")
        self.c.showPage()
        self.c.save()
        self._saved=True
        return self.output


def run_example(draw, stem):
    """Shared CLI for an independently executable example."""
    import argparse
    parser=argparse.ArgumentParser(description=draw.__doc__)
    parser.add_argument("--output",type=Path,default=Path(__file__).resolve().parents[1]/"outputs"/(stem+".pdf"))
    parser.add_argument("--width-in",type=float,default=7.2)
    parser.add_argument("--font-regular",type=Path)
    parser.add_argument("--font-bold",type=Path)
    args=parser.parse_args()
    print(draw(args.output,width_in=args.width_in,font_regular=args.font_regular,font_bold=args.font_bold))
