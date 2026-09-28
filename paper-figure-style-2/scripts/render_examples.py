"""Run independent examples and optionally merge their editable PDF pages."""
from __future__ import annotations
import argparse
import importlib
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[1]
EXAMPLES={
    "overview": ("component_overview","Component overview"),
    "lifecycle": ("evaluation_lifecycle","Evaluation lifecycle"),
    "profiles": ("capability_profiles","Capability profiles"),
    "response": ("demand_response","Demand response curves"),
    "harness": ("harness_grid","Harness outcome grid"),
    "recovery": ("recovery_analysis","Repeat-run analysis"),
    "failures": ("failure_distributions","Failure composition"),
    "interface": ("interface_walkthrough","Product walkthrough"),
    "evidence": ("evidence_table","Task-level evidence"),
}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--examples",nargs="+",choices=tuple(EXAMPLES),default=list(EXAMPLES))
    parser.add_argument("--output-dir",type=Path,default=ROOT/"outputs")
    parser.add_argument("--width-in",type=float,default=11)
    parser.add_argument("--book",action="store_true")
    args=parser.parse_args()
    outputs=[]
    for key in dict.fromkeys(args.examples):
        stem,_=EXAMPLES[key]
        module=importlib.import_module("examples."+stem)
        path=args.output_dir/(stem+".pdf")
        module.draw(path,width_in=args.width_in)
        outputs.append(path)
        print(path,flush=True)
    if args.book:
        with pymupdf.open() as book:
            for path in outputs:
                with pymupdf.open(path) as doc: book.insert_pdf(doc)
            path=args.output_dir/"examples.pdf"
            book.save(path,garbage=4,deflate=True)
            print(path)


if __name__=="__main__": main()
