"""The evidence-traceability worked example must be deterministic and true.

Mirrors the OPC UA / fieldbus example guards: the generator is deterministic,
the committed ``evidence-report.txt`` matches it, and the report demonstrates the
RFC-0631 behavior NVIDIA Isaac asked for on isaac-sim/IsaacSim#649 (a manifest
claim records whether it was derived from USD, declared, verified, or inferred).
Hermetic: validator only, no runtime and no extras.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "evidence"
GEN_PATH = EX / "trace_evidence.py"
COMMITTED = EX / "evidence-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("trace_evidence", GEN_PATH)
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
        "examples/evidence/evidence-report.txt is stale; "
        "run `python examples/evidence/trace_evidence.py` and commit."
    )


def test_advisory_then_gated() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # Advisory by default: the manifest validates with no policy.
    assert "[VALID] the manifest validates" in report
    # Opt-in policy rejects, catching the hand-declared sensor.
    assert "[REJECTED] under the evidence policy." in report
    assert "sensor 'bumper': source declared < required derived" in report
    # The LLM-inferred camera is a warning, not an error.
    assert "camera 'wrist_cam': source inferred < required derived" in report
    # The strong claims pass: no error names the derived gripper / verified lidar.
    assert "gripper 'panda_hand'" not in report.split("errors:")[1].split("warnings:")[0]
    assert "front_lidar" not in report.split("errors:")[1]
