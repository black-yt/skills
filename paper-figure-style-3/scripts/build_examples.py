"""Generate four native .drawio files and a multi-page editable collection."""
import argparse
import json
from pathlib import Path

from drawio import save
from examples import figure1,figure2,figure3,figure4

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figures",nargs="+",choices=("1","2","3","4"),default=["1","2","3","4"])
    parser.add_argument("--output-dir",type=Path,default=ROOT/"outputs")
    parser.add_argument("--data",type=Path,help="JSON with trajectories, ablation and latent_lengths")
    args=parser.parse_args()
    data=json.loads(args.data.read_text(encoding="utf-8")) if args.data else None
    constructors={"1":figure1,"2":figure2,
                  "3":lambda:figure3(data["trajectories"] if data else None),
                  "4":lambda:figure4(data["ablation"] if data else None,data["latent_lengths"] if data else None)}
    diagrams=[]
    for number in dict.fromkeys(args.figures):
        diagram=constructors[number]()
        diagrams.append(diagram)
        print(save([diagram],args.output_dir/f"figure-{number}.drawio"))
    print(save(diagrams,args.output_dir/"all-figures.drawio"))


if __name__=="__main__":
    main()
