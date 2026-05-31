"""Guard: the engaged-partners fleet demo (examples/fleet/run_partners_demo.py) runs.

Same don't-rot discipline as test_fleet_demo.py — a schema, runtime, or manifest
change can never silently rot the four-real-robot choreography. Loaded by path.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_DEMO = Path(__file__).resolve().parents[3] / "examples" / "fleet" / "run_partners_demo.py"


def _load_demo():
    spec = importlib.util.spec_from_file_location("partners_run_demo", _DEMO)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_demo_file_present():
    assert _DEMO.is_file(), f"partners demo not found at {_DEMO}"


def test_partners_demo_runs_hermetically():
    result = _load_demo().main(verbose=False)
    assert result.success
    # 4 members x 3 primitives each = 12 steps (the barriers are not steps).
    assert result.steps_executed == 12
    assert set(result.per_member_audit) == {"marty", "petoi", "feather", "arm"}
    walk = ["send_navigation_goal", "take_measurement", "send_navigation_goal"]
    for member in ("marty", "petoi", "feather"):
        methods = [c.get("method") for c in result.per_member_audit[member]]
        assert methods == walk, f"{member}: {methods}"
    arm = [c.get("method") for c in result.per_member_audit["arm"]]
    assert arm == ["send_navigation_goal", "take_measurement", "call_named_program"]
