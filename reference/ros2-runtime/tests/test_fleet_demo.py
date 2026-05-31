"""Guard: the published fleet demo (examples/fleet/run_demo.py) actually runs.

Analogous to the README hero-SVG guard — it asserts the shipped, human-facing
artifact executes hermetically and produces the expected per-member trace, so a
schema or runtime change can never silently rot the multi-robot demo.

The demo script lives under examples/ (not an installed package), so it is loaded
by path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_DEMO = Path(__file__).resolve().parents[3] / "examples" / "fleet" / "run_demo.py"


def _load_demo():
    spec = importlib.util.spec_from_file_location("fleet_run_demo", _DEMO)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_demo_file_present():
    assert _DEMO.is_file(), f"fleet demo not found at {_DEMO}"


def test_demo_runs_hermetically():
    result = _load_demo().main(verbose=False)
    assert result.success
    assert result.steps_executed == 5
    assert set(result.per_member_audit) == {"courier", "arm"}
    # The courier navigates twice and holds; the arm manipulates twice.
    courier = [c.get("method") for c in result.per_member_audit["courier"]]
    arm = [c.get("method") for c in result.per_member_audit["arm"]]
    assert courier == ["send_navigation_goal", "wait_passively", "send_navigation_goal"]
    assert arm.count("send_manipulation_goal") == 2
