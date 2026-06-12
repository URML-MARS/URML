"""The URML intent-gate (VLM coexistence) example must be deterministic and true.

Mirrors the esmini / ros2_kortex / crazyswarm2 export guards: the generator is
deterministic, the committed ``gate-report.txt`` matches it, and the gate decides
correctly (safe intents dispatch, unsafe ones are rejected with the right reason).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "vla"
GEN_PATH = EX / "validate_intents.py"
COMMITTED = EX / "gate-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("validate_intents", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    assert gen.render_gate_report() == gen.render_gate_report()


def test_committed_report_matches_generator() -> None:
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    assert COMMITTED.read_text(encoding="utf-8") == gen.render_gate_report(), (
        "examples/vla/gate-report.txt is stale; "
        "run `python examples/vla/validate_intents.py` and commit."
    )


def test_gate_decides_correctly() -> None:
    gen = _load_gen()
    report = gen.render_gate_report()
    # Two safe intents dispatch, three unsafe are rejected.
    assert report.count("[DISPATCH]") == 2
    assert report.count("[REJECTED]") == 3
    # The unsafe intents are caught for the right reasons, before any actuation.
    assert "envelope.force_exceeded" in report
    assert "envelope.occupancy_zone_intrusion" in report
    assert "capability.missing_location" in report  # the hallucinated-target catch
    assert "No actuator command sent." in report
