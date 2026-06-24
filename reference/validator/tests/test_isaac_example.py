"""The Isaac Sim worked example must be deterministic and true.

Mirrors the OPC UA / evidence example guards: the generator is deterministic, the
committed ``motion-report.txt`` matches it, and the example demonstrates the flow
NVIDIA Isaac asked for on isaac-sim/IsaacSim#649 (a USD-derived manifest with
RFC-0631 evidence, validated, then driven through IsaacAdapter). Hermetic: the
example injects a fake ``isaacsim``, so no wheel, no GPU, no engine.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "isaac"
GEN_PATH = EX / "usd_to_motion.py"
COMMITTED = EX / "motion-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("usd_to_motion", GEN_PATH)
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
        "examples/isaac/motion-report.txt is stale; "
        "run `python examples/isaac/usd_to_motion.py` and commit."
    )


def test_usd_derived_validates_and_drives() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # The USD-derived claims trace to prim paths.
    assert "usd_prim:/World/arm/base/ArticulationRoot" in report
    # Validate before actuate, and the listing-grade evidence policy both pass.
    assert "[VALID] navigate to sim_waypoint" in report
    assert "[VALID] under the listing evidence policy" in report
    assert "[REJECTED]" not in report
    # Each move_to lowered to one control-vector write; the engine advanced.
    assert "move_to sim_waypoint  ->  ctrl = [0.4, 0.2, -0.1, 0.0]" in report
    assert "2 move_to commands dispatched; 100 physics steps advanced." in report
