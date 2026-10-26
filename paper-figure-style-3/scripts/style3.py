"""Pastel day/night vector primitives for paper-figure-style-3.

The axes use top-left coordinates. All diagrams and charts are drawn with
Matplotlib artists; the source paper's raster images are never embedded.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.font_manager import findfont, fontManager
from matplotlib.ft2font import FT2Font
from matplotlib.text import Text
from handdrawn import (arrow as pen_arrow, ellipse as pen_ellipse,
                      line as pen_line, polygon as pen_polygon,
                      prism as pen_prism, rect as pen_rect)

ROOT = Path(__file__).resolve().parents[1]
for _font_name in ("Kalam-Regular.ttf", "Kalam-Bold.ttf"):
    fontManager.addfont(str(ROOT / "assets" / "fonts" / _font_name))
INK = "#272936"
MUTED = "#5D6270"
WARM = "#F8DCDD"
WARM_DARK = "#B85C61"
COOL = "#DDEBF7"
COOL_DARK = "#3A6791"
MINT = "#C8E5D1"
TEAL = "#97CFCC"
YELLOW = "#F4E6AD"
PURPLE = "#D8CBE8"
GREEN = "#5C8763"
VIOLET = "#8063A4"


@contextmanager
def theme():
    """Keep styling local; preserve TrueType text in the vector PDF."""
    with plt.rc_context({
        "font.family": "DejaVu Sans", "font.size": 10,
        "pdf.fonttype": 42, "ps.fonttype": 42,
        "text.color": INK, "axes.edgecolor": MUTED,
        "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "savefig.facecolor": "white", "savefig.transparent": False,
    }):
        yield


@contextmanager
def diagram_theme(font_family="DejaVu Serif"):
    """Use a reproducible paper-like typeface; Kalam remains an option."""
    with theme(), plt.rc_context({"font.family": font_family}):
        yield


def diagram(width: float, height: float, *, inches_per_100: float = 1.2):
    fig, ax = plt.subplots(figsize=(width / 100 * inches_per_100,
                                    height / 100 * inches_per_100))
    fig.subplots_adjust(0, 0, 1, 1)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def label(ax, x, y, value, *, size=11, color=INK, weight="normal", ha="center",
          va="center", style="normal", rotation=0, zorder=6, family=None):
    return ax.text(x, y, value, fontsize=size, color=color, fontweight=weight,
                   ha=ha, va=va, style=style, rotation=rotation, zorder=zorder,
                   multialignment=ha, linespacing=1.12, fontfamily=family)


def box(ax, x, y, w, h, *, fill="white", edge=INK, radius=12, lw=1.4,
        text=None, size=10, weight="normal", text_color=INK, zorder=2,
        linestyle="solid"):
    patch = pen_rect(ax, x, y, w, h, fill=fill, edge=edge, radius=radius,
                     lw=lw, zorder=zorder, linestyle=linestyle)
    if text is not None:
        label(ax, x + w / 2, y + h / 2, text, size=size,
              color=text_color, weight=weight, zorder=zorder + 1)
    return patch


def arrow(ax, x1, y1, x2, y2, *, color=INK, lw=1.7, curved=0.0,
          linestyle="solid", zorder=5):
    return pen_arrow(ax, x1, y1, x2, y2, color=color, lw=lw,
                     curve=curved, linestyle=linestyle, zorder=zorder)


def diamond(ax, x, y, w=35, h=25, *, fill=YELLOW, edge=INK):
    """Editable latent block drawn with three independent pen paths."""
    return pen_prism(ax, x, y, w, h, fill=fill, edge=edge)


def sun(ax, x, y, radius=17, color="#ED8B60"):
    import math
    ax.add_patch(patches.Circle((x, y), radius * .46, facecolor=color,
                                 edgecolor="none", zorder=6))
    for i in range(8):
        angle = i * math.pi / 4
        a, b = radius * .66, radius
        ax.plot([x + a * math.cos(angle), x + b * math.cos(angle)],
                [y + a * math.sin(angle), y + b * math.sin(angle)],
                color=color, linewidth=2.3, zorder=6)


def moon(ax, x, y, radius=17, color="#2F547E", mask="white"):
    ax.add_patch(patches.Circle((x, y), radius, facecolor=color, edgecolor="none", zorder=6))
    ax.add_patch(patches.Circle((x + radius * .45, y - radius * .32), radius * .87,
                                 facecolor=mask, edgecolor="none", zorder=7))


def brain(ax, x, y, scale=1):
    """Layered vector brain emblem; no source-paper image assets."""
    ax.add_patch(patches.Circle((x, y), 36 * scale, facecolor="#F7CDD3",
                                 edgecolor=INK, linewidth=1.8, zorder=5))
    ax.add_patch(patches.Circle((x - 7 * scale, y - 6 * scale), 14 * scale,
                                 facecolor="#91C7D7", edgecolor=COOL_DARK,
                                 linewidth=1.4, zorder=6))
    ax.add_patch(patches.Circle((x + 6 * scale, y - 6 * scale), 14 * scale,
                                 facecolor="#91C7D7", edgecolor=COOL_DARK,
                                 linewidth=1.4, zorder=6))
    ax.add_patch(patches.Circle((x, y + 3 * scale), 13 * scale,
                                 facecolor="#91C7D7", edgecolor=COOL_DARK,
                                 linewidth=1.4, zorder=6))
    ax.plot([x, x], [y - 22 * scale, y + 14 * scale], color="#B35E9D",
            lw=2.1, zorder=7)
    ax.plot([x - 16 * scale, x - 7 * scale, x - 11 * scale],
            [y - 3 * scale, y + 1 * scale, y + 11 * scale],
            color="#B35E9D", lw=1.7, zorder=7)
    ax.plot([x + 16 * scale, x + 7 * scale, x + 11 * scale],
            [y - 3 * scale, y + 1 * scale, y + 11 * scale],
            color="#B35E9D", lw=1.7, zorder=7)


def head_brain(ax, x, y, scale=1):
    """Hand-inked profile and a single folded brain silhouette."""
    profile = [(-23,-31),(-13,-36),(3,-35),(19,-30),(28,-19),(29,-6),
               (24,1),(33,7),(22,13),(20,27),(8,31),(10,39),
               (-19,39),(-18,22),(-27,10),(-31,-5),(-29,-20)]
    pen_polygon(ax, [(x+a*scale,y+b*scale) for a,b in profile],
                fill="#F6C28A", edge="#28568D", lw=2.0, zorder=6,
                amplitude=.42*scale)
    import math
    gear=[]
    for i in range(36):
        a=2*math.pi*i/36
        r=26 if i%3 else 29
        gear.append((x+(-1+r*math.cos(a))*scale,
                     y+(-13+r*math.sin(a))*scale))
    pen_polygon(ax, gear, fill="#47B8D1", edge="#245D94",
                lw=1.45, zorder=7, amplitude=.25*scale)
    lobes = [(-19,-15),(-21,-23),(-15,-29),(-8,-27),(-3,-32),(6,-31),
             (10,-26),(17,-25),(21,-17),(19,-10),(22,-5),(17,2),
             (8,4),(3,9),(-6,8),(-11,4),(-18,4),(-22,-3),(-19,-9)]
    pen_polygon(ax, [(x+a*scale,y+b*scale) for a,b in lobes],
                fill="#F4A6BC", edge="#265E9D", lw=1.6, zorder=8,
                amplitude=.35*scale)
    folds = [((-11,-25),(-11,-15),(-5,-9),(-8,2)),
             ((3,-28),(1,-19),(8,-14),(9,-5),(4,3)),
             ((-18,-9),(-11,-4),(-13,4)),
             ((16,-22),(12,-15),(17,-10)),
             ((-2,-31),(-3,-24),(4,-21))]
    for fold in folds:
        pen_line(ax, [(x+a*scale,y+b*scale) for a,b in fold],
                 color="#793273", lw=1.45, zorder=9,
                 amplitude=.28*scale)


def phase_emblem(ax, x, y, radius):
    """Two-tone day/night medallion with independently editable symbols."""
    ax.add_patch(patches.Wedge((x, y), radius, 90, 270, facecolor="#EF8255",
                                edgecolor="none", zorder=5))
    ax.add_patch(patches.Wedge((x, y), radius, 270, 90, facecolor="#173858",
                                edgecolor="none", zorder=5))
    ax.add_patch(patches.Circle((x, y), radius, facecolor="none", edgecolor=INK,
                                lw=2.0, zorder=8))
    sun(ax, x - radius * .48, y + 1, radius * .48, color="white")
    moon(ax, x + radius * .37, y - radius * .07, radius * .36,
         color="white", mask="#173858")
    for dx, dy, r in ((.05, -.54, 2.5), (.45, -.50, 1.9),
                      (.61, .37, 2.3), (.12, .55, 1.5)):
        ax.add_patch(patches.Circle((x + dx * radius, y + dy * radius), r,
                                    facecolor="white", edgecolor="none", zorder=8))


def snowflake(ax, x, y, radius=19, *, color="#2C7AA7", lw=2.0):
    """Six-arm frozen-backbone mark, including branch tips."""
    import math
    for k in range(6):
        a = k * math.pi / 3
        ux, uy = math.cos(a), math.sin(a)
        ax.plot([x, x + radius * ux], [y, y + radius * uy],
                color=color, lw=lw, zorder=8)
        for side in (-1, 1):
            base = radius * .66
            tip_x, tip_y = x + radius * ux, y + radius * uy
            ax.plot([x + base * ux + side * 5 * -uy, tip_x],
                    [y + base * uy + side * 5 * ux, tip_y],
                    color=color, lw=lw * .75, zorder=8)
    ax.add_patch(patches.Circle((x, y), 3.3, facecolor="white",
                                edgecolor=color, lw=1, zorder=9))


def flame(ax, x, y, scale=1):
    """Editable two-colour insight flame for a consolidation module."""
    outer=[(-7,9),(-8,0),(-5,-7),(-2,-3),(0,-14),(4,-9),(5,-13),
           (9,-4),(8,4),(4,10)]
    inner=[(-3,8),(-3,2),(-1,-3),(2,0),(3,-6),(6,2),(4,8)]
    pen_polygon(ax, [(x+a*scale,y+b*scale) for a,b in outer],
                fill="#E86A35", edge="#7E2833", lw=1.3,
                zorder=8, amplitude=.2)
    pen_polygon(ax, [(x+a*scale,y+b*scale) for a,b in inner],
                fill="#F5C34A", edge="#A2522D", lw=.8,
                zorder=9, amplitude=.15)


def document(ax, x, y, w, h, text, *, fill=MINT, edge=GREEN, size=7.8):
    """Folded-corner task sheet with selectable multiline label."""
    fold = min(w, h) * .23
    vertices = [(x, y), (x + w - fold, y), (x + w, y + fold),
                (x + w, y + h), (x, y + h)]
    pen_polygon(ax, vertices, fill=fill, edge=edge, lw=1.4, zorder=5)
    pen_polygon(ax, [(x + w - fold, y), (x + w - fold, y + fold),
                     (x + w, y + fold)], fill="white", edge=edge,
                lw=1.0, zorder=6, amplitude=.3)
    label(ax, x + (w - fold) / 2, y + h * .54, text, size=size,
          weight="bold", zorder=7)


def weaver(ax, x, y, radius=33, *, fill="#E9A8BB", edge="#75334A"):
    """Vector yarn ball with clipped winding strands."""
    circle = patches.Circle((x, y), radius, facecolor=fill,
                             edgecolor=edge, lw=1.9, zorder=7)
    ax.add_patch(circle)
    for shift in (-.52, -.27, 0, .27, .52):
        x0 = x + shift * radius
        strand, = ax.plot([x0 - radius * .45, x0 + radius * .45],
                          [y - radius * .92, y + radius * .92],
                          color=edge, lw=1.3, zorder=8)
        strand.set_clip_path(circle)
    for shift in (-.32, .12, .46):
        y0 = y + shift * radius
        strand, = ax.plot([x - radius * .88, x + radius * .88],
                          [y0 + radius * .24, y0 - radius * .24],
                          color=edge, lw=1.0, zorder=8)
        strand.set_clip_path(circle)
    ax.add_patch(patches.Arc((x + radius * .57, y - radius * .69),
                             radius * 1.3, radius * .9, theta1=20,
                             theta2=115, color=edge, lw=1.3, zorder=9))


def notebook(ax, x, y, w, h, title, *, fill="#C6D887"):
    """Cylindrical skills journal with editable icons and labels."""
    pen_polygon(ax, [(x,y+9),(x+w,y+9),(x+w,y+h-9),(x,y+h-9)],
                fill=fill, edge=GREEN, lw=1.4, zorder=5)
    pen_ellipse(ax, x+w/2, y+h-9, w/2, 9, fill=fill,
                edge=GREEN, lw=1.4, zorder=5)
    pen_ellipse(ax, x+w/2, y+9, w/2, 9, fill="#E0EAA5",
                edge=GREEN, lw=1.4, zorder=6)
    pen_rect(ax, x+8, y+23, 14, 11, fill="#72A5BE", edge="#366780",
             lw=.6, radius=1, zorder=7)
    pen_rect(ax, x+9, y+40, 18, 8, fill="#86BAC5", edge="#366780",
             lw=.6, radius=1, zorder=7)
    label(ax, x+w*.56, y+h*.58, title, size=8.5,
          weight="bold", zorder=7, ha="center")


def memory_cylinder(ax, x, y, w, h, *, fill="#EDE1F1", edge=VIOLET):
    """Editable buffer with elliptical top/bottom surfaces."""
    ax.add_patch(patches.Rectangle((x, y + 11), w, h - 22,
                                   facecolor=fill, edgecolor=edge,
                                   lw=1.5, zorder=3))
    pen_ellipse(ax, x + w/2, y + h - 11, w/2, 11,
                fill=fill, edge=edge, lw=1.5, zorder=4)
    pen_ellipse(ax, x + w/2, y + 11, w/2, 11,
                fill="#F6EFF8", edge=edge, lw=1.5, zorder=5)


def save_pdf(fig, path: str | Path, *, title: str):
    """Save a one-page PDF with actual extractable labels and no raster layers."""
    path = Path(path)
    if path.suffix.lower() != ".pdf":
        raise ValueError("output must end in .pdf")
    fig.canvas.draw()
    charmaps = {}
    for artist in fig.findobj(match=Text):
        if not artist.get_visible() or not artist.get_text():
            continue
        font_path = findfont(artist.get_fontproperties(), fallback_to_default=False)
        if font_path not in charmaps:
            charmaps[font_path] = FT2Font(font_path).get_charmap()
        missing = [char for char in artist.get_text()
                   if char not in "\n\t\r" and ord(char) not in charmaps[font_path]]
        if missing:
            raise ValueError(f"font lacks glyphs {sorted(set(missing))!r}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, format="pdf", metadata={
        "Title": title, "Author": "paper-figure-style-3",
        "Subject": "Original vector redraw based on a paper figure",
        "CreationDate": None, "ModDate": None,
    })
    plt.close(fig)
    return path
