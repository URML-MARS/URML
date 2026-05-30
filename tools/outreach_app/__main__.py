"""Entry point: `python -m tools.outreach_app`.

Refreshes the SQLite mirror on startup (so the user does not have to
run `make outreach-refresh` first), then launches NiceGUI on port 8001.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from nicegui import ui

from . import app as _app  # noqa: F401 — registers pages
from .data import DEFAULT_DB

REPO_ROOT = Path(__file__).resolve().parents[2]


def _refresh_db_on_startup() -> None:
    """Ensure the SQLite mirror exists and is fresh."""
    script = REPO_ROOT / "tools" / "scripts" / "refresh_outreach_db.py"
    if not script.exists():
        print(f"warning: {script} not found; using existing {DEFAULT_DB}", file=sys.stderr)
        return
    subprocess.run([sys.executable, str(script)], check=False)


def main() -> None:
    _refresh_db_on_startup()
    ui.run(
        title="URML outreach",
        port=8001,
        show=False,
        reload=False,
        favicon="🛰",
        dark=None,  # follow system
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
