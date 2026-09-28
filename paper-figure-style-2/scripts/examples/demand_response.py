"""Example request: I need six panels comparing model success rates against capability demand."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from style2 import theme, run_example
from plots import demand_response as render


def draw(output, *, width_in=11):
    """I need six panels comparing model success rates against capability demand."""
    with theme():
        return render(output, width_in=width_in)


if __name__ == "__main__":
    run_example(draw, "demand_response")
