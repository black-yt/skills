"""Example request: I need a three-benchmark, three-model harness comparison with task uncertainty."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style2 import theme, run_example
from plots import harness_grid as render


def draw(output, *, width_in=11):
    """I need a three-benchmark, three-model harness comparison with task uncertainty."""
    with theme():
        return render(output, width_in=width_in)


if __name__ == "__main__":
    run_example(draw, "harness_grid")
