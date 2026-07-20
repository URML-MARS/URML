"""The CRAM validate-before-actuate example must be deterministic and true.

Mirrors the lang2ltl / vitra / robotiq-hande guards. From a conversation with the
CRAM group (U. Bremen IAI): URML is the necessary-not-sufficient admissibility gate
below CRAM's action decomposition. The example validates one grounded transport plan
three ways: admissible; an out-of-envelope grounded grasp (refused statically); and a
grounded object outside the perception vocabulary (refused before dispatch).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "cram"
GEN_PATH = EX / "run_cram.py"
COMMITTED = EX / "cram-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_cram", GEN_PATH)
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
        "examples/cram/cram-report.txt is stale; "
        "run `python examples/cram/run_cram.py` and commit."
    )


def test_three_cases_decide_correctly() -> None:
    gen = _load_gen()
    from urml_validator import validate

    manifest = gen._load(gen.MANIFEST)

    # 1. In-envelope grasp of an in-vocabulary object -> admissible.
    ok = validate(gen._transport_program("mug", 60.0), manifest, profiles=gen._PROFILES, policy=None)
    assert ok.accepted

    # 2. A grounded grasp above the gripper's rated range -> refused statically.
    over = validate(gen._transport_program("mug", 250.0), manifest, profiles=gen._PROFILES, policy=None)
    assert not over.accepted
    assert "envelope.force_exceeded" in {e.code_str for e in over.errors}

    # 3. A grounded object outside the perception vocabulary -> refused before dispatch.
    unknown = validate(gen._transport_program("tray", 60.0), manifest, profiles=gen._PROFILES, policy=None)
    assert not unknown.accepted
    assert "capability.missing_object_class" in {e.code_str for e in unknown.errors}


def test_report_states_the_honest_boundary() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "necessary-not-sufficient" in report
    assert "capability.missing_object_class" in report
    assert "does not, and cannot, promise" in report
