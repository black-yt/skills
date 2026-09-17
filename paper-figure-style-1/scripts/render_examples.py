"""Render independent diagram and statistical examples as vector PDFs."""
from __future__ import annotations

import argparse
import importlib
from pathlib import Path

EXAMPLES = {
    "pipeline":"research_pipeline",
    "architecture":"system_architecture",
    "factory":"task_factory",
    "validation":"validation_matrix",
    "learning":"learning_loop",
    "leaderboard":"evaluation_leaderboard",
    "model-logos":"model_leaderboard",
    "budget":"budget_profiles",
    "efficiency":"efficiency_frontier",
    "gains":"benchmark_gains",
    "training":"training_dashboard",
    "outcomes":"failure_outcomes",
    "domains":"domain_specialization",
    "mechanisms":"failure_mechanisms",
    "coverage":"coverage_overview",
    "runtime":"resource_runtime",
    "cycle":"research_cycle",
}

GROUPS = {
    "diagrams": ["pipeline","architecture","factory","validation","learning","runtime","cycle"],
    "statistics": ["leaderboard","model-logos","budget","efficiency","gains","training","outcomes","domains","mechanisms","coverage"],
    "extension": list(EXAMPLES)[5:],
    "all": list(EXAMPLES),
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    selection=parser.add_mutually_exclusive_group()
    selection.add_argument("--examples",nargs="+",choices=EXAMPLES)
    selection.add_argument("--group",choices=GROUPS,default=None)
    parser.add_argument("--list",action="store_true",help="Show the user request demonstrated by each example")
    parser.add_argument("--book",action="store_true",help="Also bundle the generated PDFs into examples.pdf")
    parser.add_argument("--book-name",default="examples.pdf",help="PDF basename for --book, inside --output-dir")
    parser.add_argument("--output-dir",type=Path,default=Path(__file__).resolve().parents[1]/"outputs")
    parser.add_argument("--width-in",type=float,default=7.2)
    parser.add_argument("--font-regular",type=Path)
    parser.add_argument("--font-bold",type=Path)
    args=parser.parse_args()
    if Path(args.book_name).name!=args.book_name or not args.book_name.lower().endswith(".pdf"):
        parser.error("--book-name must be a PDF basename, without directories")
    selected=args.examples or GROUPS[args.group or "all"]
    if args.book and args.book_name in {EXAMPLES[key]+".pdf" for key in selected}:
        parser.error("The gallery filename must differ from individual example filenames")
    outputs=[]
    for num in dict.fromkeys(selected):
        stem=EXAMPLES[num]
        module=importlib.import_module("examples."+stem)
        if args.list:
            print(f"{num}: {module.__doc__}")
            continue
        output=module.draw(args.output_dir/(stem+".pdf"),width_in=args.width_in,
                           font_regular=args.font_regular,font_bold=args.font_bold)
        print(output)
        outputs.append(output)
    if args.book and outputs:
        import pymupdf
        with pymupdf.open() as book:
            for output in outputs:
                with pymupdf.open(output) as source:
                    book.insert_pdf(source)
            book.set_metadata({"title":"Paper figure style 1 — Example gallery","author":"paper-figure-style-1"})
            target=args.output_dir/args.book_name
            book.save(target,garbage=4,deflate=True)
            print(target)


if __name__=="__main__":
    main()
