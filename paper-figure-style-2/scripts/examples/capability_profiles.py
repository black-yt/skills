"""Example request: I need grouped coverage bars and concentric radial profiles for six benchmark suites."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style2 import theme, run_example
from plots import capability_profiles as render


def draw(output, *, width_in=11):
    """I need grouped coverage bars and concentric radial profiles for six benchmark suites."""
    with theme():
        return render(output, width_in=width_in)


if __name__ == "__main__":
    run_example(draw, "capability_profiles")
