"""The dynamic-target-grasp worked example must be deterministic and true.

Mirrors the spot-capture / epically-powerful guards: the generator is deterministic,
the committed ``dynamic-grasp-report.txt`` matches it, a ballistic catch on a hand that
declares ballistic interception validates, and the same catch is rejected on a hand with
no interception (target_motion_not_supported) or one declaring only tracked
(target_motion_mode_not_declared). For RFC-0671.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "dynamic-grasp"
GEN_PATH = EX / "run_dynamic_grasp.py"
COMMITTED = EX / "dynamic-grasp-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_dynamic_grasp", GEN_PATH)
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
        "examples/dynamic-grasp/dynamic-grasp-report.txt is stale; "
        "run `python examples/dynamic-grasp/run_dynamic_grasp.py` and commit."
    )


def test_interception_admits_and_refuses() -> None:
    """RFC-0671: target_motion is admissible only on a gripper declaring the mode."""
    gen = _load_gen()
    manifest = gen._load(gen.MANIFEST)
    program = gen._load(gen.PROGRAM)

    ok, _, _ = gen._validate(program, manifest)
    assert ok, "a ballistic catch on a hand declaring ballistic should validate"

    bad_ns, ns_codes, _ = gen._validate(program, gen._without_interception(manifest))
    assert not bad_ns
    assert "capability.target_motion_not_supported" in ns_codes

    bad_md, md_codes, _ = gen._validate(program, gen._tracked_only(manifest))
    assert not bad_md
    assert "capability.target_motion_mode_not_declared" in md_codes


def test_report_shows_cases_and_framing() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "[VALID] phantom_hand declares interception modes [tracked, ballistic]" in report
    assert "capability.target_motion_not_supported" in report
    assert "capability.target_motion_mode_not_declared" in report
    assert "No new primitive: a catch is a grasp." in report
