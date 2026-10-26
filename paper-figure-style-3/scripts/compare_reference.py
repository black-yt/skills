"""Compare a rendered redraw with a user-supplied paper figure by pixel MSE.

The paper figure is read locally and never copied into this skill's assets.
MSE is sensitive to crop, resolution, compression, colour, and fonts; inspect
the heatmap and regional scores before changing diagram geometry.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageFilter


def compare(reference: Path, redraw: Path, output: Path, rows: int, cols: int):
    ref_image = Image.open(reference).convert("RGB")
    raw_image = Image.open(redraw).convert("RGB")
    resized = raw_image.resize(ref_image.size, Image.Resampling.LANCZOS)
    ref = np.asarray(ref_image, dtype=np.float32) / 255
    got = np.asarray(resized, dtype=np.float32) / 255
    squared = np.mean((ref - got) ** 2, axis=2)
    absolute = np.mean(np.abs(ref - got), axis=2)
    height, width = squared.shape
    blur_radius = max(2.0, width / 160)
    ref_blur = np.asarray(ref_image.filter(ImageFilter.GaussianBlur(blur_radius)),
                          dtype=np.float32) / 255
    got_blur = np.asarray(resized.filter(ImageFilter.GaussianBlur(blur_radius)),
                          dtype=np.float32) / 255
    total_error = float(squared.sum())
    region_scores = []
    for row in range(rows):
        for col in range(cols):
            x0, x1 = width * col // cols, width * (col + 1) // cols
            y0, y1 = height * row // rows, height * (row + 1) // rows
            crop = squared[y0:y1, x0:x1]
            region_scores.append({
                "row": row + 1, "col": col + 1,
                "box": [x0, y0, x1, y1],
                "mse": round(float(crop.mean()), 6),
                "share_of_total_error": round(float(crop.sum()) / total_error, 4)
                if total_error else 0.0,
            })
    metrics = {
        "reference_size": list(ref_image.size),
        "redraw_size": list(raw_image.size),
        "redraw_resized_to_reference": True,
        "rgb_mse_0_to_1": round(float(squared.mean()), 6),
        "rgb_mae_0_to_1": round(float(absolute.mean()), 6),
        "rgb_rmse_0_to_255": round(float(np.sqrt(squared.mean()) * 255), 3),
        "coarse_rgb_mse_0_to_1": round(float(np.mean((ref_blur - got_blur) ** 2)), 6),
        "coarse_blur_radius_px": round(blur_radius, 2),
        "regions": region_scores,
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    fig_height = 2.8 if width / height > 2.5 else 4.3
    fig, axes = plt.subplots(1, 3, figsize=(15, fig_height), dpi=160)
    for ax, image, title in zip(
        axes, (ref_image, resized, squared),
        ("Paper figure", "Vector redraw (resized)", "RGB squared error"),
    ):
        ax.imshow(image, cmap="inferno" if title.startswith("RGB") else None,
                  vmin=0 if title.startswith("RGB") else None,
                  vmax=.3 if title.startswith("RGB") else None)
        ax.set_title(title, fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
        for row in range(1, rows):
            ax.axhline(height * row / rows, color="white", lw=.6, alpha=.6)
        for col in range(1, cols):
            ax.axvline(width * col / cols, color="white", lw=.6, alpha=.6)
    fig.suptitle(f"MSE {metrics['rgb_mse_0_to_1']:.4f}  |  coarse MSE {metrics['coarse_rgb_mse_0_to_1']:.4f}",
                 fontsize=13)
    fig.tight_layout()
    fig.savefig(output / "comparison.png")
    plt.close(fig)
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("redraw", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grid", type=int, nargs=2, default=(2, 2),
                        metavar=("ROWS", "COLS"))
    args = parser.parse_args()
    metrics = compare(args.reference, args.redraw, args.output, *args.grid)
    print(json.dumps({"mse": metrics["rgb_mse_0_to_1"],
                      "rmse": metrics["rgb_rmse_0_to_255"],
                      "coarse_mse": metrics["coarse_rgb_mse_0_to_1"],
                      "worst_regions": sorted(metrics["regions"],
                                              key=lambda r: r["mse"], reverse=True)[:3]},
                     indent=2))


if __name__ == "__main__":
    main()
