#!/usr/bin/env python3
"""One-command local onboarding for URML — no PyPI, fully reversible.

URML is in Phase 0 (pre-public draft). The reference packages are not on
PyPI yet; you install them editable from this clone. This script does
exactly that, in one step, on any OS:

  1. Verifies Python >= 3.11 (the packages' minimum).
  2. Creates a project-local virtual environment at `.venv/` (skipped if
     one already exists — re-running is safe and idempotent).
  3. Installs all five reference packages **editable** into that venv,
     in dependency order, in a single resolved pip invocation so the
     internal `urml-*` dependencies resolve against the local checkouts
     instead of trying (and failing) to reach PyPI.
  4. Prints the two things to do next.

Nothing here touches the network beyond pip fetching third-party deps
(pydantic, PyYAML) from PyPI. No URML package is published, claimed, or
uploaded. Everything lands in `.venv/` (git-ignored); `make clean` —
or just `rm -rf .venv` — removes every trace.

Usage:
    python bootstrap.py            # core install (enough for the demo)
    python bootstrap.py --dev      # also install dev extras (tests, lint)
    python bootstrap.py --help
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import venv
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
VENV_DIR = REPO_ROOT / ".venv"

# Dependency order: validator has no internal deps; ros2-runtime depends
# on validator; the rest depend on those two. pip resolves a combined
# editable set regardless of order, but listing deps first is a cheap
# belt-and-suspenders and documents the graph.
PACKAGES: tuple[str, ...] = (
    "reference/validator",
    "reference/ros2-runtime",
    "reference/llm-bridge",
    "reference/px4-runtime",
    "conformance",
)

MIN_PY = (3, 11)


def _fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"\n  bootstrap: {msg}\n", file=sys.stderr)
    raise SystemExit(1)


def _check_python() -> None:
    if sys.version_info < MIN_PY:
        _fail(
            f"Python {MIN_PY[0]}.{MIN_PY[1]}+ required; this is "
            f"{sys.version_info.major}.{sys.version_info.minor}. "
            "Install a newer Python and re-run."
        )


def _venv_python() -> Path:
    """Path to the venv's interpreter, cross-platform."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _ensure_venv() -> Path:
    py = _venv_python()
    if py.exists():
        print(f"  bootstrap: reusing existing venv at {VENV_DIR}")
        return py
    print(f"  bootstrap: creating venv at {VENV_DIR}")
    venv.EnvBuilder(with_pip=True, clear=False).create(VENV_DIR)
    if not py.exists():  # pragma: no cover - platform anomaly
        _fail(f"venv created but interpreter not found at {py}")
    return py


def _run(cmd: list[str]) -> None:
    print("  bootstrap: $ " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=REPO_ROOT)
    if result.returncode != 0:
        _fail(f"command failed ({result.returncode}): {' '.join(cmd)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="bootstrap.py",
        description="One-command local URML onboarding (editable installs, no PyPI).",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Also install each package's [dev] extra (pytest, ruff, mypy).",
    )
    args = parser.parse_args()

    _check_python()
    py = _ensure_venv()

    # Newer pip handles PEP 660 editable installs more reliably.
    _run([str(py), "-m", "pip", "install", "--upgrade", "pip"])

    # One combined resolved install. The `-e` targets satisfy each
    # other's `urml-*` requirements locally, so nothing is fetched for
    # the internal graph.
    suffix = "[dev]" if args.dev else ""
    install_args: list[str] = [str(py), "-m", "pip", "install"]
    for pkg in PACKAGES:
        install_args += ["-e", f"{pkg}{suffix}"]
    _run(install_args)

    activate = (
        r".venv\Scripts\activate"
        if sys.platform == "win32"
        else "source .venv/bin/activate"
    )
    print(
        "\n  bootstrap: done. URML is installed editable in .venv/\n\n"
        "  Next:\n"
        f"    {activate}\n"
        "    make demo         # validate the canonical red-mug example end-to-end\n"
        "  (or, without make:)\n"
        "    .venv/bin/urml validate examples/home/red-mug.urml.yaml \\\n"
        "        -m examples/home/red-mug.manifest.yaml --profile home\n"
    )


if __name__ == "__main__":
    main()
