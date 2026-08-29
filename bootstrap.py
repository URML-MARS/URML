#!/usr/bin/env python3
"""One-command local onboarding for URML — no PyPI, fully reversible.

URML is in Phase 0 (pre-public draft). The reference packages are not on
PyPI yet; you install them editable from this clone. This script does
exactly that, in one step, on any OS:

  1. Verifies Python >= 3.11 (the packages' minimum).
  2. Picks a virtual environment: if one is already active ($VIRTUAL_ENV
     is set) it installs into that one (so a custom-named venv such as
     `.venv_urml` is respected); otherwise it reuses or creates the
     project-local `.venv/`. Re-running is safe and idempotent.
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
import os
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
    "reference/ardupilot-runtime",
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


def _venv_python(venv_dir: Path) -> Path:
    """Path to a venv's interpreter, cross-platform."""
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _ensure_venv() -> tuple[Path, Path]:
    """Return (venv_dir, interpreter), honoring an already-active venv.

    If a virtual environment is active ($VIRTUAL_ENV is set), bootstrap installs
    into *that* venv, so a custom-named one (e.g. `.venv_urml`) is respected
    rather than ignored in favour of a fresh `.venv`. With no active venv, the
    project-local `.venv` is reused if present, else created.
    """
    active = os.environ.get("VIRTUAL_ENV")
    if active:
        venv_dir = Path(active)
        py = _venv_python(venv_dir)
        if py.exists():
            print(f"  bootstrap: using the already-active venv at {venv_dir}")
            return venv_dir, py
        print(
            f"  bootstrap: $VIRTUAL_ENV={venv_dir} has no interpreter; "
            f"falling back to {VENV_DIR}"
        )

    py = _venv_python(VENV_DIR)
    if py.exists():
        print(f"  bootstrap: reusing existing venv at {VENV_DIR}")
        return VENV_DIR, py
    print(f"  bootstrap: creating venv at {VENV_DIR}")
    venv.EnvBuilder(with_pip=True, clear=False).create(VENV_DIR)
    if not py.exists():  # pragma: no cover - platform anomaly
        _fail(f"venv created but interpreter not found at {py}")
    return VENV_DIR, py


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
    parser.add_argument(
        "--llm",
        action="append",
        choices=["openai", "anthropic"],
        default=[],
        metavar="PROVIDER",
        help=(
            "Also install an LLM provider extra for the bridge (repeatable): "
            "--llm openai and/or --llm anthropic. Needed to `urml translate` "
            "against that provider; the core install omits these heavy, "
            "provider-specific SDKs."
        ),
    )
    args = parser.parse_args()

    _check_python()
    venv_dir, py = _ensure_venv()
    rel = os.path.relpath(venv_dir, REPO_ROOT)

    # Newer pip handles PEP 660 editable installs more reliably.
    _run([str(py), "-m", "pip", "install", "--upgrade", "pip"])

    # One combined resolved install. The `-e` targets satisfy each
    # other's `urml-*` requirements locally, so nothing is fetched for
    # the internal graph. `[dev]` applies to every package; an `--llm`
    # provider extra applies only to the bridge.
    def _extras_for(pkg: str) -> str:
        extras: list[str] = []
        if args.dev:
            extras.append("dev")
        if pkg == "reference/llm-bridge":
            extras += list(dict.fromkeys(args.llm))  # dedup, keep order
        return f"[{','.join(extras)}]" if extras else ""

    install_args: list[str] = [str(py), "-m", "pip", "install"]
    for pkg in PACKAGES:
        install_args += ["-e", f"{pkg}{_extras_for(pkg)}"]
    _run(install_args)

    activate = (
        rf"{rel}\Scripts\activate"
        if sys.platform == "win32"
        else f"source {rel}/bin/activate"
    )
    bin_dir = "Scripts" if sys.platform == "win32" else "bin"
    print(
        f"\n  bootstrap: done. URML is installed editable in {rel}/\n\n"
        "  Next:\n"
        f"    {activate}\n"
        "    make demo         # validate the canonical red-mug example end-to-end\n"
        "  (or, without make:)\n"
        f"    {rel}/{bin_dir}/urml validate examples/home/red-mug.urml.yaml \\\n"
        "        -m examples/home/red-mug.manifest.yaml --profile home\n"
    )
    if not args.llm:
        print(
            "  To `urml translate` against a real LLM, add a provider extra:\n"
            "    python bootstrap.py --llm openai      # or --llm anthropic\n"
            "  (a local OpenAI-compatible server like Ollama also uses --llm openai).\n"
        )


if __name__ == "__main__":
    main()
