"""White-paper plotting theme and native-vector diagram primitives.

Diagram coordinates are logical units, with y increasing downwards. Font sizes
in Diagram methods use the same units. Charts use ordinary Matplotlib points.
No paper, network service, system font or sibling skill is needed at runtime.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors, patches
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.ft2font import FT2Font
from matplotlib.textpath import TextToPath
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INK = "#191B20"
MUTED = "#68717C"
GRID = "#D9DDE1"
BLUE = "#3070B5"
CYAN = "#77BCEB"
TEAL = "#239C88"
MINT = "#6CD6B4"
CATEGORY = ("#A1B8DC", "#A9DDBB", "#F6C99B", "#D0C6E7", "#FBE8C7", "#A7DBE2")
ACCENT = ("#5594CC", "#39A680", "#E7A252", "#9A82C4", "#DAB951", "#239FAE")
ZONES = {
    "green": ("#F3F9F4", "#E2F0E5", "#467B61"),
    "blue": ("#F1F7FD", "#DEECF9", "#183F70"),
    "purple": ("#F6F3FA", "#EDE6F4", "#776497"),
    "gold": ("#FCF6E9", "#F5EACF", "#846224"),
    "rose": ("#FCF3F5", "#F5E3E9", "#97556B"),
}
# Background, card fill, and phase accent read from the reference vector PDF.
PHASES = (
    ("#F0EDFE", "#F9F6FF", "#594C9C"),
    ("#E6F4FE", "#F2FAFF", "#5E85CF"),
    ("#EAFAF2", "#F6FCFA", "#499B7D"),
    ("#FAF8F4", "#FFFDFC", "#B0344C"),
)


@contextmanager
def theme(font="DejaVu Sans"):
    """Keep rcParams local and embed TrueType text rather than Type 3 glyphs."""
    with plt.rc_context({
        "font.family": font, "font.size": 9, "text.color": INK,
        "axes.labelcolor": INK, "axes.edgecolor": "#656970",
        "axes.linewidth": .5, "axes.titlesize": 10, "axes.titleweight": "normal",
        "xtick.color": "#42464D", "ytick.color": "#42464D",
        "xtick.labelsize": 8, "ytick.labelsize": 8,
        "xtick.major.width": .4, "ytick.major.width": .4,
        "xtick.major.size": 2, "ytick.major.size": 2,
        "legend.fontsize": 8, "legend.frameon": False,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "pdf.fonttype": 42, "ps.fonttype": 42, "text.usetex": False,
        "savefig.transparent": False,
    }):
        yield


def tint(color, amount):
    """Mix color with white; amount=1 preserves color, amount=0 is white."""
    rgb = np.asarray(colors.to_rgb(color))
    return tuple(1 - amount * (1 - rgb))


def clean_axes(ax, *, grid="y", full_box=False):
    ax.set_axisbelow(True)
    if not full_box:
        ax.spines[["top", "right"]].set_visible(False)
    if grid:
        ax.grid(axis=grid, color=GRID, linestyle=(0, (2, 2)), linewidth=.5)


def footer(fig, text="Illustrative data · not measured benchmark results"):
    fig.text(.012, .012, text, fontsize=6.5, color=MUTED, va="bottom")


def save_pdf(fig, output, *, title, width_in=None):
    """Write vector PDF with selectable labels. Never rasterize the canvas."""
    output = Path(output)
    if output.suffix.lower() != ".pdf":
        raise ValueError("The publication artifact must have a .pdf extension")
    from matplotlib.text import Text
    fig.canvas.draw()
    charmaps={}
    for artist in fig.findobj(match=Text):
        if not artist.get_visible(): continue
        path=findfont(artist.get_fontproperties(),fallback_to_default=False)
        if path not in charmaps: charmaps[path]=FT2Font(path).get_charmap()
        missing={c for c in artist.get_text() if c not in "\n\t\r" and ord(c) not in charmaps[path]}
        if missing:
            raise ValueError(f"Font lacks glyphs {sorted(missing)!r}; choose a suitable font in theme()")
    if width_in is not None:
        if not np.isfinite(width_in) or width_in <= 0:
            raise ValueError("Physical width must be positive and finite")
        from matplotlib.text import Text
        from matplotlib.lines import Line2D
        from matplotlib.collections import Collection
        fig.canvas.draw()
        factor=width_in/fig.get_figwidth()
        for artist in fig.findobj():
            if isinstance(artist,Text): artist.set_fontsize(artist.get_fontsize()*factor)
            elif isinstance(artist,Line2D):
                artist.set_linewidth(artist.get_linewidth()*factor)
                artist.set_markersize(artist.get_markersize()*factor)
            elif isinstance(artist,patches.Patch): artist.set_linewidth(artist.get_linewidth()*factor)
            elif isinstance(artist,Collection):
                artist.set_linewidths(np.asarray(artist.get_linewidths())*factor)
                if hasattr(artist,"get_sizes"):
                    artist.set_sizes(artist.get_sizes()*factor*factor)
        fig.set_size_inches(fig.get_size_inches()*factor)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, format="pdf", facecolor="white", metadata={
        "Title": title, "Author": "paper-figure-style-2",
        "Subject": "Reusable vector example; illustrative content",
        "CreationDate": None, "ModDate": None,
    })
    plt.close(fig)
    return output


def run_example(draw, stem):
    parser = argparse.ArgumentParser(description=draw.__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "outputs" / (stem + ".pdf"))
    parser.add_argument("--width-in", type=float, default=11)
    args = parser.parse_args()
    if not np.isfinite(args.width_in) or args.width_in <= 0:
        parser.error("--width-in must be a positive finite number")
    print(draw(args.output, width_in=args.width_in))


class Diagram:
    """Editable vector canvas with top-left coordinates and proportional text."""

    def __init__(self, height, *, width=1100, width_in=11):
        if not all(np.isfinite(v) and v > 0 for v in (width, height, width_in)):
            raise ValueError("Canvas dimensions must be positive and finite")
        self.width, self.height = width, height
        self.scale = width_in * 72 / width
        self.fig = plt.figure(figsize=(width_in, width_in * height / width))
        self.ax = self.fig.add_axes([0, 0, 1, 1], xlim=(0, width), ylim=(height, 0))
        self.ax.set_axis_off()

    def rect(self, x, y, w, h, *, fill="white", edge=GRID, radius=0, lw=.8, dash="solid", z=1):
        if radius:
            patch = patches.FancyBboxPatch((x, y), w, h,
                boxstyle=f"round,pad=0,rounding_size={radius}")
        else:
            patch = patches.Rectangle((x, y), w, h)
        patch.set(facecolor=fill or "none", edgecolor=edge or "none",
                  linewidth=lw*self.scale, linestyle=dash, zorder=z)
        self.ax.add_patch(patch)
        return patch

    def text_width(self, value, size=14, bold=False):
        prop=FontProperties(family=plt.rcParams["font.family"],size=size*self.scale,weight="bold" if bold else "normal")
        return max(TextToPath().get_text_width_height_descent(line,prop,False)[0]/self.scale
                   for line in str(value).split("\n"))

    def text(self, x, y, value, *, size=14, color=INK, bold=False, ha="left", va="center", rotation=0, z=5, max_width=None):
        if max_width is not None:
            measured=self.text_width(value,size,bold)
            if measured>max_width: size*=max_width/measured
        return self.ax.text(x, y, str(value), fontsize=size*self.scale, color=color,
            weight="bold" if bold else "normal", ha=ha, va=va, rotation=rotation,
            linespacing=1.2, zorder=z)

    def line(self, points, *, color=INK, lw=1, dash="solid", z=3):
        x, y = zip(*points)
        return self.ax.plot(x, y, color=color, linewidth=lw*self.scale,
                            linestyle=dash, solid_capstyle="round", zorder=z)[0]

    def arrow(self, points, *, color=INK, lw=1.3, dash="solid", head=7):
        if len(points) > 2:
            self.line(points[:-1], color=color, lw=lw, dash=dash)
        arrow = patches.FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>",
            mutation_scale=head*self.scale, linewidth=lw*self.scale, color=color,
            linestyle=dash, shrinkA=0, shrinkB=0, zorder=4)
        self.ax.add_patch(arrow)

    def circle(self, x, y, r, *, fill="white", edge=INK, lw=1, z=3):
        c = patches.Circle((x, y), r, facecolor=fill or "none", edgecolor=edge or "none",
                           linewidth=lw*self.scale, zorder=z)
        self.ax.add_patch(c)
        return c

    def polygon(self, points, *, fill="white", edge=INK, lw=1, z=3):
        p = patches.Polygon(points, closed=True, facecolor=fill or "none",
                            edgecolor=edge or "none", linewidth=lw*self.scale, zorder=z)
        self.ax.add_patch(p)
        return p

    def icon(self, name, x, y, *, size=30, color=None, accent=None):
        """Use the icon's vivid palette by default, independent of its section."""
        from icons import draw_icon
        draw_icon(self, name, x, y, size=size, color=color, accent=accent)

    def group(self, x, y, w, h, title, *, zone="blue", icon="network", icon_color=None, icon_accent=None):
        fill, header, color = ZONES[zone]
        self.rect(x, y, w, h, fill=fill, edge=tint(color, .5))
        self.rect(x+1, y+1, w-2, 30, fill=header, edge=None)
        title_w=self.text_width(title,20,True)
        left=x+(w-title_w-33)/2
        self.icon(icon, left, y+3, size=25, color=icon_color, accent=icon_accent)
        self.text(left+33, y+17, title, size=20, color=color, bold=True)
        return color

    def card(self, x, y, w, h, title, body, *, color=BLUE, icon=None, title_size=13, icon_color=None, icon_accent=None):
        self.rect(x, y, w, h, radius=3, edge=tint(color, .25), fill="white")
        left = x+8
        if icon:
            self.icon(icon, x+6, y+(h-30)/2, size=30, color=icon_color, accent=icon_accent)
            left = x+44
        self.text(left, y+14, title, size=title_size, color=color, bold=True,max_width=x+w-left-7)
        self.text(left, y+h-12, body, size=9.5,max_width=x+w-left-7)

    def note(self, value="Illustrative system design · components and values are configurable"):
        self.text(8, self.height-9, value, size=8, color=MUTED)

    def save(self, output, title):
        return save_pdf(self.fig, output, title=title)
