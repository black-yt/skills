"""Source-aligned, editable Figure 2 assembled from reusable vector components.

All coordinates use the 1098 × 617 reference frame. Labels can be replaced
without copying any pixels from the paper image into the rendered PDF.
"""
from __future__ import annotations

from collections.abc import Mapping

from matplotlib import patches
from handdrawn import brace, polygon as pen_polygon

from style3 import (INK, arrow, box, diagram, diagram_theme, diamond,
                    head_brain, label, memory_cylinder,
                    save_pdf, snowflake, weaver)


DEFAULT_LABELS = {
    "day_title": "Daytime Scaling",
    "night_title": "Nighttime Scaling",
    "task_line_1": ": Write a data analysis code for this",
    "task_line_2": "Excel file and visualize the geometric data",
    "backbone": "LLM\nBackbone\n(frozen)",
    "base": "Initial base\nlatent z_base,i",
    "refined": "Refined\nlatent z_0,i",
    "optimization": "Iterative test-time optimization",
    "weaver": "Latent\nWeaver",
    "consolidation": "Consolidation\nfrom experiences",
    "buffer": "Episodic Buffer",
    "subset": "High confidence\nlatent subset",
}


def _token(ax, x, y, name="", *, fill="#DBE9F7", w=34, h=35):
    box(ax, x, y, w, h, fill=fill, edge="#315774", radius=2, lw=1.15)
    if name:
        label(ax, x + w / 2, y - 9, name, size=8.4, style="italic")


def _panel(ax, x, y, w, h, fill, *, edge="none", radius=0, lw=0):
    if radius:
        return box(ax, x, y, w, h, fill=fill, edge=edge, radius=radius, lw=lw)
    panel = patches.Rectangle((x, y), w, h, facecolor=fill,
                              edgecolor=edge, lw=lw, zorder=1)
    ax.add_patch(panel)
    return panel


def _title_and_task(ax, words):
    _panel(ax, 0, 0, 770, 617, "#FFF9E9")
    _panel(ax, 770, 0, 328, 617, "#ECF3FB")
    ax.plot([770, 770], [0, 617], color="#C2CAD3", lw=1.0, zorder=2)
    ax.add_patch(patches.Circle((-6, -10), 77, facecolor="#FFE2A1",
                                 edgecolor="#77776E", lw=1.9, zorder=1))
    label(ax, 164, 27, words["day_title"], size=25.2,
          color="#9A5A1F", weight="bold", style="italic")
    label(ax, 937, 26, words["night_title"], size=23.3,
          color="#24598B", weight="bold", style="italic")
    box(ax, 84, 62, 657, 63, fill="#F9F9F5", edge="#5E6065",
        radius=6, lw=1.5)
    label(ax, 94, 83, "Task c_i", size=15.4, weight="bold", ha="left")
    ax.add_patch(patches.Circle((216, 85), 12, facecolor="#F4C5CC",
                                 edgecolor="#993C4A", lw=1.3, zorder=5))
    label(ax, 246, 84, words["task_line_1"], size=13.1,
          family="DejaVu Sans Mono", ha="left")
    label(ax, 94, 111, words["task_line_2"], size=12.9,
          family="DejaVu Sans Mono", ha="left")
    pen_polygon(ax, [(107,126),(124,126),(122,150),(134,150),
                     (115,171),(96,151),(106,151)],
                fill="#A9CEA3", edge="#678363", lw=1.6, zorder=4)


def _decode_and_latents(ax, words):
    box(ax, 1, 165, 181, 192, fill="#D4EAD0", edge="#5C805A",
        radius=10, lw=1.7)
    snowflake(ax, 47, 170, 29, lw=2.3)
    label(ax, 94, 261, words["backbone"], size=19.1, weight="bold")
    label(ax, 302, 152, "Standard decoding", size=13.5, style="italic")
    pen_polygon(ax, [(145,179),(179,169),(179,157),(213,187),
                     (178,210),(180,194),(146,202),(158,188)],
                fill="#C7C7C7", edge="#555A59", lw=1.8, zorder=6)
    box(ax, 184, 165, 505, 80, fill="#9FC9C6", edge="#437D7E",
        radius=8, lw=1.6)
    for x, name in ((210, "z1"), (251, "z2"), (292, "z3"),
                    (333, "z4"), (374, "z5"), (415, "z6"),
                    (518, "z80"), (559, "z81"), (600, "z82"),
                    (641, "z83")):
        _token(ax, x, 198, name, w=34, h=33)
    label(ax, 478, 213, "... ...", size=14, weight="bold")
    ax.plot([198, 451], [246, 246], color=INK, lw=1.1)
    ax.plot([198, 198], [238, 246], color=INK, lw=1.1)
    ax.plot([451, 451], [238, 246], color=INK, lw=1.1)
    label(ax, 269, 260, "Truncate", size=12, style="italic")
    arrow(ax, 326, 246, 326, 273, color=INK, lw=1.2)

    box(ax, 193, 274, 197, 81, fill="#9CD0CE", edge="#467578",
        radius=6, lw=1.5)
    label(ax, 204, 313, words["base"], size=12.6, ha="left")
    diamond(ax, 321, 298, 57, 38, fill="#F4E79F")
    arrow(ax, 391, 306, 417, 306, color=INK, lw=1.5)
    box(ax, 419, 274, 188, 81, fill="#9CD0CE", edge="#467578",
        radius=6, lw=1.5)
    label(ax, 431, 313, words["refined"], size=12.6, ha="left")
    diamond(ax, 540, 298, 57, 38, fill="#B9E0D3")
    label(ax, 640, 275, "Refine\nWeave", size=11.8, style="italic")
    arrow(ax, 688, 304, 609, 304, color="#342D32", lw=1.5)
    arrow(ax, 566, 383, 566, 357, color="#334961", lw=1.4)


def _rollouts(ax, words):
    box(ax, 34, 392, 468, 215, fill="#9FC5D0", edge="#326B8A",
        radius=18, lw=1.8, zorder=1, linestyle=(0, (5, 4)))
    label(ax, 307, 373, words["optimization"], size=15.7,
          style="italic", weight="bold")
    ax.add_patch(patches.Circle((46, 396), 21, facecolor="#F3E5B7",
                                 edgecolor=INK, lw=1.2, zorder=5))
    arrow(ax, 31, 379, 59, 379, color="#BC6372", curved=.6, lw=1.5)
    label(ax, 112, 407, "update", size=10.2, style="italic")
    snowflake(ax, 67, 489, 32, lw=2.1)
    snowflake(ax, 454, 489, 32, lw=2.1)
    for row, prob in enumerate(("0.5", "0.3", "0.7")):
        yy = 441 + row * 45
        label(ax, 160, yy + 14, prob, size=10.7, ha="right")
        tint = "#B6DFA9" if row == 1 else "#DCE9F6"
        _token(ax, 190, yy, fill=tint, w=32, h=31)
        label(ax, 233, yy + 16, "...", size=11.2)
        _token(ax, 250, yy, fill=tint, w=32, h=31)
        arrow(ax, 105, 489, 185, yy + 15, color=INK,
              curved=(row - 1) * .14, lw=1.3)
    arrow(ax, 81, 442, 382, 467, color="#1F2529", lw=2.1,
          curved=-.25)
    diamond(ax, 350, 481, 61, 41, fill="#E8DDA1")
    for end_y in (455, 500, 544):
        arrow(ax, 349, 496, 282, end_y, color="#1F2529", lw=1.6,
              curved=(end_y-500)*.002)
    label(ax, 378, 549, "Optimized\nlatent", size=10.4)
    ax.plot([414, 436], [501, 501], color="#213A39", lw=1.6)
    label(ax, 74, 572, "Self\nreward", size=12.0, style="italic")
    label(ax, 451, 549, "Frozen\nLLM", size=11.6)
    label(ax, 230, 587, "Multiple rollouts", size=12.2, style="italic")
    arrow(ax, 503, 492, 525, 492, color="#304A61", lw=1.4)
    pen_polygon(ax, [(481,356),(488,381),(469,412),(440,441),
                     (439,459),(417,452),(427,424),(437,430),
                     (460,400),(473,374)],
                fill="#9BAEAF", edge="#526B6B", lw=1.4,
                zorder=7, amplitude=.38)


def _momentum_and_memory(ax, words):
    _panel(ax, 526, 383, 136, 174, "#E9E4DE")
    label(ax, 594, 417, "Momentum\nTransfer", size=13.5, style="italic")
    for x, y, tint in ((557, 457, "#EEDFA5"), (607, 457, "#BFE0BE"),
                       (557, 509, "#F1DDA3"), (607, 509, "#CAE4B7")):
        diamond(ax, x, y, 42, 31, fill=tint)
    ax.plot([542, 542, 551], [447, 548, 548], color=INK, lw=1.4)
    arrow(ax, 573, 383, 573, 357, color=INK, lw=1.1)

    memory_cylinder(ax, 676, 414, 190, 192, fill="#E4D7E9", edge="#715185")
    label(ax, 771, 425, words["buffer"], size=11.5, weight="bold")
    for yy, task in ((467, "c_i"), (532, "c_m")):
        ax.add_patch(patches.Circle((713, yy + 12), 19,
                                     facecolor="#F6D1D1", edgecolor="#AE6269",
                                     lw=1.2, zorder=6))
        label(ax, 713, yy + 12, task, size=9.9, style="italic")
        diamond(ax, 746, yy, 47, 31, fill="#ECE8AC")
        diamond(ax, 800, yy, 47, 31, fill="#C8E5C9")
    label(ax, 770, 574, "query-latent pairs", size=11.5)
    arrow(ax, 747, 414, 747, 396, color="#98545B", lw=1.4)
    arrow(ax, 503, 580, 672, 580, color=INK, lw=1.3,
          linestyle=(0, (4, 3)))
    label(ax, 576, 604, "(c_i, z_base,i, z*_i)", size=8.8, style="italic")

    _panel(ax, 951, 415, 126, 131, "#A6D4CA")
    _panel(ax, 939, 424, 126, 131, "#B7DBD2")
    label(ax, 1010, 571, words["subset"], size=11.8)
    brace(ax, 929, 450, 531, side="left", lw=1.5)
    brace(ax, 1063, 450, 531, side="right", lw=1.5)
    ax.add_patch(patches.Circle((978, 465), 15, facecolor="#F5D3D2",
                                 edgecolor="#AE6770", lw=1.1, zorder=5))
    diamond(ax, 945, 486, 53, 34, fill="#F0E5A3")
    diamond(ax, 1006, 468, 57, 37, fill="#BBE1CA")
    arrow(ax, 864, 483, 921, 483, color="#1D3028", lw=1.4)
    label(ax, 879, 521, "E(Q|v_i) > γ", size=8.5, rotation=90)


def _consolidation_and_weaver(ax, words):
    box(ax, 791, 61, 292, 181, fill="#F4DDE4", edge="#B76671",
        radius=10, lw=1.7)
    head_brain(ax, 835, 102, .55)
    label(ax, 939, 108, words["consolidation"], size=14.4)
    ax.add_patch(patches.Circle((838, 160), 22, facecolor="#F6D1D1",
                                 edgecolor="#784653", lw=1.3, zorder=5))
    label(ax, 838, 160, "c_i", size=12.4, style="italic")
    diamond(ax, 816, 184, 54, 34, fill="#D3E8BD")
    brace(ax, 882, 139, 227, side="right", color="#42303A",
          lw=1.45)
    weaver(ax, 929, 178, 24)
    label(ax, 980, 147, "Weave", size=10.0, style="italic")
    arrow(ax, 953, 178, 999, 178, color=INK, lw=1.3)
    diamond(ax, 1006, 177, 61, 37, fill="#C0E3CB")
    label(ax, 1032, 229, "latent z_0,i", size=9.4)

    ax.add_patch(patches.Circle((768, 321), 74, facecolor="#F3DBE5",
                                 edgecolor="#B4616B", lw=2.0, zorder=5))
    weaver(ax, 769, 280, 24)
    label(ax, 769, 332, words["weaver"], size=17.0, weight="bold")
    arrow(ax, 791, 252, 815, 241, color="#AE6972", curved=.12, lw=1.4)
    pen_polygon(ax, [(941,432),(920,410),(849,375),(850,363),
                     (817,370),(828,397),(836,386),(911,430)],
                fill="#D6ABA6", edge="#835E68", lw=1.4,
                zorder=4, amplitude=.36)
    label(ax, 879, 407, "Finetune", size=10.1, style="italic", rotation=-27)

    pen_polygon(ax, [(766,326),(848,251),(848,391)],
                fill="#DEDDDC", edge="none", lw=0, zorder=1,
                amplitude=0)
    _panel(ax, 848, 251, 236, 140, "#E8E7E5")
    label(ax, 1008, 270, "Instantiation\nchoices", size=12.1)
    points = ((865, 327), (865, 347), (865, 367),
              (889, 317), (889, 337), (889, 357), (889, 377),
              (914, 328), (914, 348), (914, 368))
    for left, middle in ((0, 3), (0, 4), (1, 4), (1, 5),
                         (2, 5), (2, 6)):
        ax.plot([points[left][0], points[middle][0]],
                [points[left][1], points[middle][1]],
                color="#28313D", lw=.8, zorder=6)
    for middle, right in ((3, 7), (4, 7), (4, 8), (5, 8),
                          (5, 9), (6, 9)):
        ax.plot([points[middle][0], points[right][0]],
                [points[middle][1], points[right][1]],
                color="#28313D", lw=.8, zorder=6)
    for i, (x, y) in enumerate(points):
        tint = ("#EDC074", "#A7D9C6", "#D7BDD8")[i % 3]
        ax.add_patch(patches.Circle((x, y), 4.0, facecolor=tint,
                                     edgecolor=INK, lw=.7, zorder=7))
    label(ax, 890, 312, "SLM", size=10.0, style="italic")
    label(ax, 924, 339, "+", size=18)
    for top, symbol in ((307, "A"), (345, "B")):
        pen_polygon(ax, [(936,top),(978,top),(972,top+28),(942,top+28)],
                    fill="#DCE5A3", edge="#537354", lw=1.0,
                    zorder=6, amplitude=.25)
        label(ax, 957, top+15, symbol, size=9.1)
    label(ax, 953, 383, "LoRA", size=10.2)
    box(ax, 1003, 311, 72, 60, fill="#D6E4C0", edge="#577B5F",
        radius=2, lw=1.0, text="Emb.\nProjector", size=8.4)
    label(ax, 1042, 383, "Adapter", size=10.2)
    arrow(ax, 848, 325, 837, 324, color="#915260", lw=1.3)


def figure_2(path, *, labels: Mapping[str, str] | None = None):
    """Draw the dense day/night pipeline while retaining editable components."""
    words = DEFAULT_LABELS.copy()
    if labels:
        unknown = set(labels) - set(words)
        if unknown:
            raise ValueError(f"unknown Figure 2 label(s): {sorted(unknown)}")
        words.update(labels)
    with diagram_theme():
        fig, ax = diagram(1098, 617)
        _title_and_task(ax, words)
        _decode_and_latents(ax, words)
        _rollouts(ax, words)
        _momentum_and_memory(ax, words)
        _consolidation_and_weaver(ax, words)
        return save_pdf(fig, path, title="Detailed daytime and nighttime dataflow")
