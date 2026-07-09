"""The VITRA worked example must be deterministic and true.

Mirrors the robotiq-hande guard: the generator is deterministic, the committed
``vitra-report.txt`` matches it, and the example shows the same policy-emitted
action admissible on one robot manifest and refused on another (gripper force
envelope), with no ROS in the loop. For microsoft/VITRA#41.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "vitra"
GEN_PATH = EX / "run_vitra.py"
COMMITTED = EX / "vitra-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_vitra", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    assert gen.render_report() == gen.render_report()


def test_committed_report_matches_generator() -> None:
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    assert COMMITTED.read_text(encoding="utf-8") == gen.render_report(), (
        "examples/vitra/vitra-report.txt is stale; "
        "run `python examples/vitra/run_vitra.py` and commit."
    )


def test_same_action_admissible_on_a_refused_on_b() -> None:
    """The whole point: one action, two manifests, different verdicts."""
    gen = _load_gen()
    from urml_validator import validate

    program = gen._grasp_program(gen._GRASP_FORCE_N)
    manifest_a = gen._load(gen.MANIFEST_A)
    manifest_b = gen._load(gen.MANIFEST_B)

    result_a = validate(program, manifest_a, profiles=gen._PROFILES, policy=None)
    result_b = validate(program, manifest_b, profiles=gen._PROFILES, policy=None)

    # Same program, admissible on the higher-force arm.
    assert result_a.accepted
    # Refused on the gentler arm, for the force reason (both passes fire).
    assert not result_b.accepted
    codes_b = {e.code_str for e in result_b.errors}
    assert "capability.missing_gripper" in codes_b
    assert "envelope.force_exceeded" in codes_b


def test_report_states_both_verdicts() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "[VALID] grasp workpiece at 150.0 N on Robot A" in report
    assert "[REJECTED] grasp workpiece at 150.0 N on Robot B" in report
    assert "no planner and no ROS" in report
