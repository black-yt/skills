"""Example request: I need two pastel pies that compare categories within analyzed failure records."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style2 import theme, run_example
from plots import failure_distributions as render


def draw(output, *, width_in=11):
    """I need two pastel pies that compare categories within analyzed failure records."""
    with theme():
        return render(output, width_in=width_in)


if __name__ == "__main__":
    run_example(draw, "failure_distributions")
