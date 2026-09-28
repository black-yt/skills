"""Example request: I need four lifecycle lanes with normal execution, error handling and resource cleanup."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style2 import theme, run_example
from diagrams import lifecycle as render


def draw(output, *, width_in=11):
    """I need four lifecycle lanes with normal execution, error handling and resource cleanup."""
    with theme():
        return render(output, width_in=width_in)


if __name__ == "__main__":
    run_example(draw, "evaluation_lifecycle")
