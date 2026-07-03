"""The Robotiq Hand-E worked example must be deterministic and true.

Mirrors the other example guards (turtlebot4, gopigo3): the generator is
deterministic, the committed ``robotiq-hande-report.txt`` matches it, and the
example shows the answer promised on AGH-CEAI/robotiq_hande_driver#44 (a Hand-E
is a simple force-envelope gripper; a grasp inside the envelope validates, a
grasp over the force cap is refused pre-dispatch). Hermetic: validator only, no
ros2_control and no hardware.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "robotiq-hande"
GEN_PATH = EX / "run_robotiq_hande.py"
COMMITTED = EX / "robotiq-hande-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_robotiq_hande", GEN_PATH)
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
        "examples/robotiq-hande/robotiq-hande-report.txt is stale; "
        "run `python examples/robotiq-hande/run_robotiq_hande.py` and commit."
    )


def test_in_envelope_grasp_is_accepted_over_force_is_refused() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # A grasp inside the declared 20-185 N envelope validates.
    assert "[VALID] grasp small_part at 60.0 N" in report
    # A grasp over the force cap is refused, on both honest grounds.
    assert "[REJECTED] grasp small_part at 250.0 N" in report
    assert "envelope.force_exceeded" in report
    assert "capability.missing_gripper" in report
    # The honest limitation is stated: no explicit aperture field on a simple gripper.
    assert "no explicit aperture field" in report
