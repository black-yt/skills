"""Example request: I need to locate unstable high-score tasks using repeat runs and demand levels."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style2 import theme, run_example
from plots import recovery_analysis as render


def draw(output, *, width_in=11):
    """I need to locate unstable high-score tasks using repeat runs and demand levels."""
    with theme():
        return render(output, width_in=width_in)


if __name__ == "__main__":
    run_example(draw, "recovery_analysis")
