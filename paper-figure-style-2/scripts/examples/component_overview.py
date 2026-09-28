"""Example request: I need a compact overview connecting benchmark suites, agent harnesses, execution and analysis."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style2 import theme, run_example
from diagrams import component_overview as render


def draw(output, *, width_in=11):
    """I need a compact overview connecting benchmark suites, agent harnesses, execution and analysis."""
    with theme():
        return render(output, width_in=width_in)


if __name__ == "__main__":
    run_example(draw, "component_overview")
