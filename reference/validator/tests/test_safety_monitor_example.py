"""The safety-monitor worked example must be deterministic and true.

Mirrors the spot-capture / epically-powerful guards: the generator is deterministic,
the committed ``safety-monitor-report.txt`` matches it, the well-formed envelope
validates while the malformed and undeclared-signal variants are rejected with the
RFC-0382 codes, and the slow_near_people property is satisfied by a compliant trace
and violated by a fast-near-a-person trace.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "safety-monitor"
GEN_PATH = EX / "run_safety_monitor.py"
COMMITTED = EX / "safety-monitor-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_safety_monitor", GEN_PATH)
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
        "examples/safety-monitor/safety-monitor-report.txt is stale; "
        "run `python examples/safety-monitor/run_safety_monitor.py` and commit."
    )


def test_validate_leg_accepts_and_rejects() -> None:
    """RFC-0382 Pass-3: well-formed validates, malformed + undeclared-signal are rejected."""
    gen = _load_gen()
    manifest = gen._load(gen.MANIFEST)
    program = gen._load(gen.PROGRAM)
    envelope = gen._load(gen.ENVELOPE)

    ok, _, _ = gen._validate(program, manifest, envelope)
    assert ok, "the well-formed monitorable envelope should validate"

    bad_parse, parse_codes, _ = gen._validate(
        program, manifest, gen._with_property(envelope, "unterminated", "always (")
    )
    assert not bad_parse
    assert "envelope.monitorable_parse_error" in parse_codes

    bad_sig, sig_codes, _ = gen._validate(
        program, manifest, gen._with_property(envelope, "battery_guard", "always (battery_temp < 80)")
    )
    assert not bad_sig
    assert "envelope.monitorable_undeclared_signal" in sig_codes


def test_monitor_leg_satisfied_and_violated() -> None:
    gen = _load_gen()
    node = gen.parse_property(gen._SLOW_NEAR_PEOPLE, dialect="stl")
    compliant = [
        gen.Sample(t=0.0, signals={"speed": 1.0, "person_distance": 5.0}),
        gen.Sample(t=1.0, signals={"speed": 0.2, "person_distance": 1.0}),
    ]
    violating = [
        gen.Sample(t=0.0, signals={"speed": 1.0, "person_distance": 5.0}),
        gen.Sample(t=1.0, signals={"speed": 1.0, "person_distance": 1.0}),
    ]
    assert gen.evaluate_trace(node, compliant), "compliant trace should satisfy the property"
    assert not gen.evaluate_trace(node, violating), "fast-near-a-person trace should violate it"


def test_report_shows_both_layers() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "# 1. Validate before dispatch" in report
    assert "# 2. Monitor at run time" in report
    assert "[VIOLATED] trace: holds 1.0 m/s with a person at 1 m" in report
    assert "it declares the property and provides the checker and the evaluator." in report
