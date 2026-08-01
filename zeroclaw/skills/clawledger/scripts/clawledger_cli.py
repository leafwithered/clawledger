"""Reviewed ZeroClaw Skill entry point for the ClawLedger CLI.

ZeroClaw's shell policy deliberately rejects `python -m` because interpreter
module execution is broader than a reviewed script path. This tiny shim keeps
the policy narrow while delegating to the installed, tested ClawLedger CLI.
"""

import sys
from pathlib import Path


# The reviewed script is invoked from the source checkout so it remains usable
# even when ZeroClaw launches a different Python installation than the operator
# shell. A normal editable/package install still resolves the same module.
repo_src = Path(__file__).resolve().parents[4] / "src"
if repo_src.is_dir():
    sys.path.insert(0, str(repo_src))

from clawledger.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
