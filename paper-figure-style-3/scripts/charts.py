"""Reusable day/night trajectory and three-panel ablation plots.

Example values below are manually transcribed from the *displayed labels* in
LatentEvolve Figure 3 and Figure 4, not recovered experimental observations.
Replace them with authoritative data for a new scientific result.
"""
from __future__ import annotations

import math

import matplotlib.pyplot as plt
from matplotlib import patches

from style3 import (
    COOL, COOL_DARK, GREEN, INK, MUTED, VIOLET, WARM, WARM_DARK,
    save_pdf, theme,
)

TRAJECTORY = {
    "MATH-500": (57.6, 65.0, 69.5, 78.6, 78.6, 80.2, 80.2, 80.2),
    "MMLU": (65.8, 65.8, 67.3, 67.3, 69.4, 72.8, 72.8, 75.3),
    "GPQA": (49.5, 49.5, 49.8, 50.0, 49.8, 50.4, 53.6, 58.0),
    "JAMA": (30.7, 35.2, 35.6, 37.3, 37.3, 39.0, 39.9, 42.4),
}

ABLATION = {
    "Full LatentEvolve": {
        "MATH-500": (77.9, 78.6, 79.5, 80.3, 79.7),
        "SciBench": (29.0, 31.9, 32.5, 33.4, 30.5),
    },
    "Without daytime": {
        "MATH-500": (69.6, 72.4, 76.4, 77.2, 74.0),
        "SciBench": (27.5, 30.4, 31.3, 28.5, 28.1),
    },
    "Without nighttime": {
        "MATH-500": (67.0, 68.4, 68.4, 68.0, 68.0),
        "SciBench": (25.9, 27.0, 27.5, 26.6, 26.2),
    },
}
LATENT_LENGTHS = (10, 15, 20, 30, 50)


def _check_percentages(values, count):
    if len(values) != count:
        raise ValueError(f"expected {count} percentages, got {len(values)}")
    if any(not isinstance(v, (int, float)) or not math.isfinite(v)
           or not 0 <= v <= 100 for v in values):
        raise ValueError("all percentages must be finite and between 0 and 100")


def figure_3(path, data=None):
    """Alternating day/night bands with two-domain, two-axis trajectories."""
    source_example = data is None
    data = TRAJECTORY if source_example else data
    expected = ("MATH-500", "MMLU", "GPQA", "JAMA")
    if set(data) != set(expected):
        raise ValueError(f"trajectory data must contain {expected}")
    for values in data.values():
        _check_percentages(values, 8)
    with theme():
        fig = plt.figure(figsize=(14.4, 4.8))
        ax = fig.add_axes((.065, .23, .685, .65))
        twin = ax.twinx()
        for i in range(8):
            ax.axvspan(i - .5, i + .5,
                       color=WARM if i % 2 == 0 else COOL,
                       alpha=.72, zorder=0)
            ax.text(i, 1.055, "DAY" if i % 2 == 0 else "NIGHT",
                    transform=ax.get_xaxis_transform(), ha="center",
                    va="bottom", fontsize=9.8, fontweight="bold",
                    color=WARM_DARK if i % 2 == 0 else COOL_DARK)
        for edge in (1.5, 3.5, 5.5):
            ax.axvline(edge, color="#88919A", lw=.8, zorder=1)
        x = list(range(8))
        series = (
            ("MATH-500", ax, GREEN, "o", -10, 8),
            ("MMLU", ax, "#7E956B", "D", 10, -9),
            ("GPQA", twin, VIOLET, "^", 10, 8),
            ("JAMA", twin, "#9B8AB5", "v", 0, -9),
        )
        for name, axis, color, marker, dx, dy in series:
            vals = data[name]
            axis.plot(x, vals, color=color, lw=1.6, marker=marker,
                      markersize=7.2, markerfacecolor="white",
                      markeredgewidth=1.25, zorder=5)
            for xi, yi in zip(x, vals):
                axis.annotate(f"{yi:.1f}", (xi, yi), xytext=(dx, dy),
                              textcoords="offset points", ha="center",
                              va="bottom" if dy > 0 else "top", fontsize=6.7,
                              color=color, zorder=6)
        ax.set_xlim(-.5, 7.5)
        if source_example:
            ax.set_ylim(48, 84)
            twin.set_ylim(28, 64)
            ax.set_yticks((50, 60, 70, 80))
            twin.set_yticks((30, 40, 50, 60))
        else:
            for axis, names in ((ax, ("MATH-500", "MMLU")),
                                (twin, ("GPQA", "JAMA"))):
                values = [v for name in names for v in data[name]]
                axis.set_ylim(max(0, min(values) - 6),
                              min(100, max(values) + 6))
        ax.tick_params(axis="y", colors=GREEN, labelsize=9)
        twin.tick_params(axis="y", colors=VIOLET, labelsize=9)
        ax.set_ylabel("In-domain accuracy (%)", color=GREEN, fontsize=10)
        twin.set_ylabel("Out-of-domain accuracy (%)", color=VIOLET,
                        fontsize=10)
        ax.set_xticks((.5, 2.5, 4.5, 6.5),
                      ("MATH 200", "MATH 200", "MMLU 200", "MMLU 200"))
        ax.tick_params(axis="x", labelsize=9.5, length=0, pad=8)
        ax.grid(axis="y", color="white", lw=1.1)
        ax.spines[["top", "right"]].set_visible(False)
        twin.spines[["top", "left"]].set_visible(False)
        legend = fig.add_axes((.825, .15, .15, .70))
        legend.set_xlim(0, 1); legend.set_ylim(0, 1); legend.axis("off")
        for i, (title, color) in enumerate((("Daytime scaling", WARM),
                                             ("Nighttime scaling", COOL))):
            yy = .92 - i * .12
            legend.add_patch(patches.Rectangle((.01, yy - .038), .25, .075,
                              facecolor=color, edgecolor=MUTED, lw=.7,
                              linestyle=(0, (2, 2))))
            legend.text(.32, yy, title, fontsize=9.1, va="center")
        legend.text(.01, .57, "IN-DOMAIN", fontsize=8.5,
                    color=GREEN, fontweight="bold")
        for i, (name, marker, color) in enumerate((("MATH-500", "o", GREEN),
                                                    ("MMLU", "D", "#7E956B"))):
            yy = .49 - i * .10
            legend.plot(.10, yy, marker=marker, ms=8, mfc="white",
                        mec=color, linestyle="none")
            legend.text(.26, yy, name, va="center", fontsize=9)
        legend.text(.01, .27, "OUT-OF-DOMAIN", fontsize=8.5,
                    color=VIOLET, fontweight="bold")
        for i, (name, marker, color) in enumerate((("GPQA", "^", VIOLET),
                                                    ("JAMA", "v", "#9B8AB5"))):
            yy = .19 - i * .10
            legend.plot(.10, yy, marker=marker, ms=8, mfc="white",
                        mec=color, linestyle="none")
            legend.text(.26, yy, name, va="center", fontsize=9)
        return save_pdf(fig, path, title="Day-night performance trajectories")


def figure_4(path, data=None, lengths=LATENT_LENGTHS):
    """Three-panel five-setting ablation; bars start at zero by design."""
    data = ABLATION if data is None else data
    if len(lengths) != 5 or len(set(lengths)) != 5:
        raise ValueError("lengths must have five unique settings")
    if len(data) != 3:
        raise ValueError("ablation needs exactly three panels")
    for panel in data.values():
        if set(panel) != {"MATH-500", "SciBench"}:
            raise ValueError("each panel needs MATH-500 and SciBench")
        for values in panel.values():
            _check_percentages(values, 5)
    colors = ("#8DBBCB", "#A5CBC3", "#BED0B5", "#E7DBAE", "#F2D79E")
    hatches = ("//", "|||", "--", "\\\\", "++")
    top = max(94, max(v for panel in data.values() for row in panel.values()
                      for v in row) + 7)
    with theme():
        fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.8), sharey=True)
        fig.subplots_adjust(left=.057, right=.99, bottom=.18, top=.81, wspace=.15)
        for ax, (panel_name, datasets) in zip(axes, data.items()):
            for group, name in enumerate(("MATH-500", "SciBench")):
                for j, value in enumerate(datasets[name]):
                    center = group * 1.24 + (j - 2) * .17
                    ax.bar(center, value, width=.16, color=colors[j],
                           hatch=hatches[j], edgecolor="#4B5960", lw=.65,
                           zorder=3)
                    ax.text(center, value + 1.2, f"{value:.1f}", ha="center",
                            va="bottom", fontsize=7.1, color=INK)
            ax.set_title(panel_name, fontsize=12.5, fontweight="bold", pad=10)
            ax.set_xlim(-.58, 1.82)
            ax.set_ylim(0, top)
            ax.set_xticks((0, 1.24), ("MATH-500", "SciBench"))
            ax.set_yticks((0, 20, 40, 60, 80))
            ax.tick_params(axis="both", labelsize=9, length=0)
            ax.grid(axis="y", color="#E1E5E8", lw=.6, zorder=0)
            ax.spines[["top", "right"]].set_visible(False)
        axes[0].set_ylabel("Accuracy (%)", fontsize=10)
        handles = [patches.Patch(facecolor=color, edgecolor="#4B5960",
                                 hatch=hatch, label=f"L'={length}")
                   for color, hatch, length in zip(colors, hatches, lengths)]
        fig.legend(handles=handles, loc="upper center", ncol=5,
                   bbox_to_anchor=(.5, .975), frameon=False, fontsize=9)
        return save_pdf(fig, path, title="Latent-length sensitivity and ablations")
