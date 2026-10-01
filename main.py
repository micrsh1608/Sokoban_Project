"""Run from the project root: python main.py --help."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "source" / "task1"))

if __name__ == "__main__":
    from sokoban.cli import main
    raise SystemExit(main(ROOT))
