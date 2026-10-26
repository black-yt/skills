"""Render the four self-contained paper-style examples as vector PDFs."""
from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf

from charts import figure_3, figure_4
from diagrams import figure_1, figure_2
from style3 import ROOT

FIGURES = {
    "1": ("01_brain_analogy", figure_1),
    "2": ("02_dual_phase_architecture", figure_2),
    "3": ("03_day_night_trajectories", figure_3),
    "4": ("04_latent_ablation", figure_4),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figures", nargs="+", choices=tuple(FIGURES),
                        default=list(FIGURES), help="source figure numbers")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs")
    parser.add_argument("--book", action="store_true", help="merge examples into one PDF")
    args = parser.parse_args()
    paths = []
    for key in dict.fromkeys(args.figures):
        stem, draw = FIGURES[key]
        path = args.output_dir / (stem + ".pdf")
        paths.append(draw(path))
        print(path, flush=True)
    if args.book:
        with pymupdf.open() as book:
            for path in paths:
                with pymupdf.open(path) as page:
                    book.insert_pdf(page)
            path = args.output_dir / "examples.pdf"
            book.save(path, garbage=4, deflate=True)
            print(path)


if __name__ == "__main__":
    main()
