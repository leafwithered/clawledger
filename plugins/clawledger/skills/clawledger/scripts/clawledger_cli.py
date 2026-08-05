import sys
from pathlib import Path


repo_src = Path(__file__).resolve().parents[5] / "src"
if repo_src.is_dir():
    sys.path.insert(0, str(repo_src))

from clawledger.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
