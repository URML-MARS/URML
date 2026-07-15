"""The gym-pybullet-drones gate example must be deterministic and true.

Mirrors the vitra / lang2ltl guards. For learnsyslab/gym-pybullet-drones#312:
URML validates a drone command against the declared aircraft and arena envelope
before any target reaches the gym-pybullet-drones controller. Hermetic (validator
only, nothing imported from gym-pybullet-drones).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "gym-pybullet-drones"
GEN_PATH = EX / "run_gym_pybullet_drones.py"
COMMITTED = EX / "gym-pybullet-drones-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_gym_pybullet_drones", GEN_PATH)
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
        "examples/gym-pybullet-drones/gym-pybullet-drones-report.txt is stale; "
        "run `python examples/gym-pybullet-drones/run_gym_pybullet_drones.py` and commit."
    )


def test_gate_decides_the_three_cases() -> None:
    gen = _load_gen()
    from urml_validator import validate

    manifest = gen._load(gen.MANIFEST)
    envelope = gen._load(gen.ENVELOPE)

    ok = validate(gen._flight(1.5, (1.0, 1.0, 1.5)), manifest, envelope=envelope, profiles=gen._PROFILES, policy=None)
    assert ok.accepted

    hi = validate(gen._flight(3.0, (1.0, 1.0, 1.5)), manifest, envelope=envelope, profiles=gen._PROFILES, policy=None)
    assert not hi.accepted
    assert "envelope.altitude_exceeded" in {e.code_str for e in hi.errors}

    oob = validate(gen._flight(1.5, (5.0, 5.0, 1.5)), manifest, envelope=envelope, profiles=gen._PROFILES, policy=None)
    assert not oob.accepted
    assert "envelope.geofence_violation" in {e.code_str for e in oob.errors}


def test_report_shows_the_hermetic_control_mapping() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "URML never imports" in report
    assert "target_pos = (0, 0, 1.5)" in report  # take_off -> controller target
    assert "target_pos = (1, 1, 0)" in report  # land -> controller target
