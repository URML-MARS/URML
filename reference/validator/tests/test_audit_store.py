"""The audit-store example must be deterministic and true.

Mirrors the VLA / fieldbus / planning export guards: the generator is
deterministic, the committed ``audit-records.txt`` matches it, and the audit
records carry the right verdicts (two dispatched, three refused with the right
codes). The worked example for the ReductStore engagement
(reductstore/reductstore#1434): URML's validated-intent verdicts as a robotics
time series.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "audit-store"
GEN_PATH = EX / "emit_audit_records.py"
COMMITTED = EX / "audit-records.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("emit_audit_records", GEN_PATH)
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
        "examples/audit-store/audit-records.txt is stale; "
        "run `python examples/audit-store/emit_audit_records.py` and commit."
    )


def test_records_capture_verdicts() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # Two dispatched, three refused, one record per intent.
    assert report.count("[DISPATCHED]") == 2
    assert report.count("[REFUSED]") == 3
    # Refused records carry their codes (the audit value).
    for code in (
        "envelope.force_exceeded",
        "envelope.occupancy_zone_intrusion",
        "capability.missing_location",
    ):
        assert code in report
    # The ReductStore write plan is present and labeled.
    assert "bucket=urml_audit" in report
    assert '"verdict":"refused"' in report


def test_build_records_shape() -> None:
    gen = _load_gen()
    manifest = gen._load(gen.MANIFEST)
    envelope = gen._load(gen.ENVELOPE)
    intents = gen._load(gen.INTENTS)["intents"]
    records = gen.build_records(manifest, envelope, intents)
    assert len(records) == 5
    # Timestamps are strictly increasing (a valid time series).
    ts = [r["ts"] for r in records]
    assert ts == sorted(ts) and len(set(ts)) == len(ts)
    # Every record has the audit fields.
    for r in records:
        assert set(r) == {"ts", "robot_id", "intent", "primitives", "verdict", "failing_pass", "codes"}
