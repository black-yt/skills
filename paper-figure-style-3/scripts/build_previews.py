"""Build two browsing sheets from the newly drawn PDFs, never source images."""
from __future__ import annotations

import argparse
from pathlib import Path

from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
import pymupdf

from style3 import ROOT

SHEETS = (
    ("01_dual_phase_diagrams.png", "Dual-phase method diagrams", (
        ("01_brain_analogy", "01", "Fast/slow learning analogy"),
        ("02_dual_phase_architecture", "02", "Daytime + nighttime architecture"),
    )),
    ("02_statistical_figures.png", "Trajectories and ablations", (
        ("03_day_night_trajectories", "03", "Cross-domain day/night evolution"),
        ("04_latent_ablation", "04", "Latent-length sensitivity and ablation"),
    )),
)


def font(size, bold=False):
    path = font_manager.findfont(font_manager.FontProperties(
        family="DejaVu Sans", weight="bold" if bold else "normal"),
        fallback_to_default=False)
    return ImageFont.truetype(path, size)


def render(pdf: Path, width=1800):
    with pymupdf.open(pdf) as doc:
        if len(doc) != 1:
            raise ValueError(f"expected one page: {pdf}")
        page = doc[0]
        scale = width / page.rect.width
        pix = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
        return Image.frombytes("RGB", (pix.width, pix.height), pix.samples)


def build(pdf_dir: Path, output_dir: Path, width=1800):
    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, heading, panels in SHEETS:
        images = [render(pdf_dir / (stem + ".pdf"), width) for stem, _, _ in panels]
        outer, gap, title_h, label_h, footer_h = 42, 38, 112, 56, 56
        card_heights = [label_h + im.height + 26 for im in images]
        total_h = title_h + sum(card_heights) + gap + footer_h
        canvas = Image.new("RGB", (width + 2 * outer, total_h), "#F7F8FA")
        draw = ImageDraw.Draw(canvas)
        draw.text((outer, 18), "PAPER FIGURE STYLE 3",
                  font=font(22, True), fill="#3A6791")
        draw.text((outer, 52), heading, font=font(36, True), fill="#272936")
        y = title_h
        for (stem, number, caption), im, h in zip(panels, images, card_heights):
            draw.rounded_rectangle((outer, y, outer + width, y + h),
                                   radius=16, fill="white", outline="#D7DDE5", width=2)
            draw.text((outer + 20, y + 14), number, font=font(21, True),
                      fill="#B85C61")
            draw.text((outer + 70, y + 14), caption, font=font(21),
                      fill="#5D6270")
            canvas.paste(im, (outer, y + label_h))
            y += h + gap
        draw.text((outer, total_h - 39),
                  "Rendered from original vector redraws  ·  Figure 3/4 values transcribed from printed labels",
                  font=font(17), fill="#5D6270")
        path = output_dir / filename
        canvas.save(path, optimize=True)
        print(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets" / "previews")
    args = parser.parse_args()
    build(args.pdf_dir, args.output_dir)


if __name__ == "__main__":
    main()
