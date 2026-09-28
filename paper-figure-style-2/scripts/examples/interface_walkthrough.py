"""Example request: I need five clean product views arranged as a paper walkthrough figure."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style2 import theme, run_example
from diagrams import interface_walkthrough as render


def draw(output, *, width_in=11):
    """I need five clean product views arranged as a paper walkthrough figure."""
    with theme():
        return render(output, width_in=width_in)


if __name__ == "__main__":
    run_example(draw, "interface_walkthrough")
