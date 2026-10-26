"""Editable Figure 1 example assembled from reusable paper-diagram parts.

Coordinates follow the 948 × 326 reference image. The source pixels are never
used while rendering; every label, document, prism, emblem, and arrow is drawn.
Pass ``labels`` to reuse the arrangement with another problem and vocabulary.
"""
from __future__ import annotations

from collections.abc import Mapping

from matplotlib import patches
from handdrawn import (bezier_shape, circle_wash, ellipse as pen_ellipse,
                      polygon as pen_polygon,
                      rect as pen_rect, wash)

from style3 import (box, diagram, diagram_theme, diamond, document, flame,
                    head_brain, label, notebook,
                    phase_emblem, save_pdf, snowflake, weaver, arrow)


DEFAULT_LABELS = {
    "fast_title": "Fast hippocampus",
    "day_title": "Daytime Scaling",
    "slow_title": "Slow neocortex",
    "night_title": "Nighttime Scaling",
    "left_emblem": "Human\nBrain",
    "right_emblem": "Latent\nEvolve",
    "memory_note": "Superficial, fast recall of\nmemory clues",
    "day_task": "Write a\nkaggle code",
    "day_recall": "- recall previous Kaggle solutions\n- fast adaptation to the codes ...",
    "night_task_1": "Write a\nkaggle code",
    "night_task_2": "leetcode task",
    "night_task_3": "use numpy for\nstatistic course",
    "skill_1": "kaggle coding",
    "skill_2": "use numpy for\nstatistic course",
    "skill_3": "use pandas\nfor homework",
    "learned_skill": "coding +\ndata analysis",
    "consolidation": "Consolidate\nknowledge and\nexperiences",
}


def _cloud(ax):
    bezier_shape(ax, (127,64), [
        ((119,54),(139,48),(153,49)),
        ((162,39),(182,37),(203,46)),
        ((224,44),(244,44),(254,61)),
        ((266,73),(252,77),(249,79)),
        ((265,86),(266,96),(249,102)),
        ((235,110),(215,103),(204,108)),
        ((180,113),(157,108),(146,103)),
        ((121,101),(122,89),(137,80)),
        ((118,77),(118,68),(127,64)),
    ], fill="#C9DD91", edge="#42693D", lw=1.55,
       zorder=3, amplitude=.15)
    pen_ellipse(ax, 248, 106, 8, 5, fill="#D6E7A4",
                edge="#42693D", lw=.8, zorder=3)


def _small_task(ax, x, y, w, h, text, size=8.2):
    return document(ax, x, y, w, h, text, fill="#A7D69D",
                    edge="#315733", size=size)


def _heading(ax, x, y, text, size=17.5):
    label(ax, x, y, text, size=size, weight="bold", style="italic", color="#1B1719")


def _gray_panel(ax, x, y, w, h, fill):
    ax.add_patch(patches.Rectangle((x, y), w, h, facecolor=fill,
                                   edgecolor="none", zorder=1))


def _brain_emblem(ax, text):
    circle_wash(ax, 64, 172, 62, "#E1E7F4", "#F4B9C5",
                edge="#20263B", lw=2.0, zorder=4)
    head_brain(ax, 64, 169, 1.08)
    label(ax, 64, 268, text, size=18.3, weight="bold", color="#18161A")


def _cue_and_skills(ax, words):
    _cloud(ax)
    _small_task(ax, 142, 121, 72, 40, "Write a\nkaggle code", 8.0)
    document(ax, 154, 50, 18, 29, "", fill="#F9F9EA",
             edge="#4B6E48", size=6)
    pen_rect(ax, 157, 55, 11, 14, fill="#2D87B3", edge="#225B84",
             radius=1, lw=.7, zorder=7)
    document(ax, 207, 54, 16, 25, "", fill="#F7F8E8",
             edge="#4B6E48", size=6)
    pen_rect(ax, 198, 66, 5, 14, fill="#E6B448", edge="#656B44",
             radius=1, lw=.5, zorder=7)
    pen_rect(ax, 204, 61, 5, 19, fill="#6EBD92", edge="#4E7655",
             radius=1, lw=.5, zorder=7)
    label(ax, 145, 87, "tree.py", size=7.3, weight="bold")
    label(ax, 202, 87, "data science\nhandbook", size=7.2,
          weight="bold")
    label(ax, 361, 62, words["memory_note"], size=9.7)
    pen_polygon(ax, [(212,139),(233,148),(251,134),(247,129),
                     (268,127),(251,113),(251,121),(231,138)],
                fill="#C1C0C0", edge="#5F6467", lw=1.05,
                zorder=4, amplitude=.25)
    head_brain(ax, 286, 126, .63)
    arrow(ax, 309, 126, 325, 126, color="#334F6E", lw=1.5, zorder=4)
    pen_polygon(ax, [(329,94),(451,95),(453,157),(330,157),
                     (327,148),(329,140),(321,135),(328,126)],
                fill="#3C9599", edge="#203B46", lw=1.55,
                zorder=4)
    label(ax, 390, 130, "- use tree search\n  func(x_node, 1)\n- analyze data ...",
          size=8.9, color="white")

    _gray_panel(ax, 136, 179, 105, 125, "#C7C8C2")
    for y, key, h in ((184, "skill_1", 32),
                      (225, "skill_2", 29),
                      (271, "skill_3", 31)):
        _small_task(ax, 143, y, 91, h, words[key], 7.5)
        arrow(ax, 235, y + h/2, 267, 248, color="#232A2F", lw=1.35, zorder=4)
    label(ax, 188, 260, "... ...", size=6.6, weight="bold")
    head_brain(ax, 291, 251, .74)
    label(ax, 388, 203,
          "Silent, long-term\nconsolidation of seen tasks\nand skills",
          size=8.9)
    arrow(ax, 318, 262, 334, 270, color="#68717B", lw=1.2, zorder=4)
    notebook(ax, 338, 235, 120, 68, words["learned_skill"])


def _daytime(ax, words):
    _gray_panel(ax, 593, 39, 215, 63, "#C5C5C6")
    _small_task(ax, 508, 40, 70, 51, words["day_task"], 7.8)
    box(ax, 493, 95, 73, 61, fill="#C7D8BE", edge="#416647",
        radius=3, lw=1.3, text="LLM\nBackbone", size=9.0, weight="bold")
    snowflake(ax, 575, 97, 12, lw=1.4)
    arrow(ax, 538, 92, 538, 96, color="#5B6B56", lw=1.2)
    label(ax, 687, 47, "Episodic Buffer M", size=9.1, weight="bold")
    for x, y, fill in ((600, 70, "#D9DC84"), (631, 65, "#A5D6AF"),
                       (662, 70, "#8AD2CD"), (691, 65, "#69BAB9"),
                       (741, 68, "#67B4C9"), (773, 72, "#60A6BF")):
        diamond(ax, x, y, 30, 14, fill=fill)
    arrow(ax, 719, 91, 568, 112, color="#1F242B", curved=-.16, lw=1.4, zorder=4)
    arrow(ax, 655, 87, 569, 115, color="#1F242B", curved=-.22,
          lw=1.1, zorder=4)
    label(ax, 751, 105, "Fast Retrieval", size=8.9, style="italic")
    pen_polygon(ax, [(578,118),(811,118),(815,156),(577,157),
                     (572,150),(573,143),(566,138),(573,130)],
                fill="#399498", edge="#243944", lw=1.4,
                zorder=4)
    label(ax, 695, 139, words["day_recall"], size=8.1, color="white")
    arrow(ax, 574, 134, 576, 134, color="#263D42", lw=1.2)


def _nighttime(ax, words):
    _gray_panel(ax, 485, 181, 333, 123, "#CBC9D1")
    for y, key, h in ((187, "night_task_1", 34),
                      (225, "night_task_2", 25),
                      (266, "night_task_3", 35)):
        _small_task(ax, 497, y, 89, h, words[key], 7.2)
        arrow(ax, 587, y + h / 2, 626, 262, color="#202226", lw=1.3, zorder=4)
    label(ax, 554, 258, "... ...", size=6.6, weight="bold")
    box(ax, 619, 185, 72, 43, fill="#C3D7BA", edge="#4E7450",
        radius=4, lw=1.2, text="LLM\nBackbone", size=8.0, weight="bold")
    snowflake(ax, 691, 187, 11, lw=1.4)
    label(ax, 758, 207, words["consolidation"], size=8.6)
    arrow(ax, 653, 229, 653, 239, color="#111519", lw=1.3)
    arrow(ax, 679, 239, 679, 228, color="#111519", lw=1.3)
    box(ax, 619, 239, 88, 64, fill="#F1B9C5", edge="#A34D5B",
        radius=2, lw=1.4)
    weaver(ax, 667, 252, 12)
    flame(ax, 694, 242, .72)
    label(ax, 663, 283, "Latent\nWeaver", size=8.7, weight="bold")
    label(ax, 754, 256, "Learn to generate", size=8.5, style="italic",
          color="#673A42")
    arrow(ax, 708, 272, 723, 277, color="#22202A", lw=1.4)
    diamond(ax, 723, 268, 42, 16, fill="#BFE9D0")
    diamond(ax, 773, 268, 39, 16, fill="#B7DFD2")


def figure_1(path, *, labels: Mapping[str, str] | None = None):
    """Draw the fast/slow analogy with editable semantic components."""
    words = DEFAULT_LABELS.copy()
    if labels:
        unknown = set(labels) - set(words)
        if unknown:
            raise ValueError(f"unknown Figure 1 label(s): {sorted(unknown)}")
        words.update(labels)
    with diagram_theme():
        fig, ax = diagram(948, 326)
        wash(ax, [(132, 8), (809, 8), (840, 166), (109, 166)],
             "#F5CDCE", "#E9D5DE")
        wash(ax, [(109, 166), (840, 166), (809, 326), (132, 326)],
             "#E4D7E1", "#D4E1F4")
        ax.plot([470, 470], [8, 326], color="#24242E", lw=2.4, zorder=2)
        ax.plot([134, 818], [169, 169], color="#1F2329", lw=1.6,
                linestyle=(0, (5, 4)), zorder=2)
        _brain_emblem(ax, words["left_emblem"])
        phase_emblem(ax, 887, 169, 59)
        label(ax, 887, 266, words["right_emblem"], size=18.1,
              weight="bold", color="#18161A")
        _heading(ax, 301, 21, words["fast_title"])
        _heading(ax, 640, 21, words["day_title"])
        _heading(ax, 334, 316, words["slow_title"], size=17.2)
        _heading(ax, 643, 316, words["night_title"], size=17.2)
        _cue_and_skills(ax, words)
        _daytime(ax, words)
        _nighttime(ax, words)
        return save_pdf(fig, path, title="Fast and slow complementary learning")
