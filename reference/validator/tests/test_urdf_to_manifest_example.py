"""The URDF-to-manifest worked example must be deterministic and true.

Mirrors the epically-powerful / rtic guards: the generator is deterministic, the
committed ``urdf-to-manifest-report.txt`` matches it, the URDF's gripper effort limit
is read out and used as the force cap, a grasp within it validates, and a grasp over it
is refused with envelope.force_exceeded. For clemense/yourdfpy#69.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "urdf-to-manifest"
GEN_PATH = EX / "run_urdf_to_manifest.py"
COMMITTED = EX / "urdf-to-manifest-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_urdf_to_manifest", GEN_PATH)
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
        "examples/urdf-to-manifest/urdf-to-manifest-report.txt is stale; "
        "run `python examples/urdf-to-manifest/run_urdf_to_manifest.py` and commit."
    )


def test_urdf_effort_becomes_force_cap() -> None:
    """The gripper finger joint's effort limit is read from the URDF and used as the cap."""
    gen = _load_gen()
    joints = gen.parse_joint_limits(gen.URDF)
    gripper = gen._gripper_joint(joints)
    assert gripper["effort"] == 185.0, "the URDF finger joint declares effort=185.0"

    manifest = gen.manifest_from_urdf(gripper["effort"])
    assert manifest["manipulation"]["grippers"][0]["force_max_n"] == 185.0


def test_in_cap_validates_over_cap_rejected() -> None:
    gen = _load_gen()
    from urml_validator import validate

    manifest = gen.manifest_from_urdf(185.0)

    ok = validate(gen._grasp_program(60.0), manifest, profiles=gen._PROFILES, policy=None)
    assert ok.accepted, "60 N is within the 185 N URDF-sourced cap"

    over = validate(gen._grasp_program(250.0), manifest, profiles=gen._PROFILES, policy=None)
    assert not over.accepted, "250 N exceeds the 185 N URDF-sourced cap"
    assert "envelope.force_exceeded" in {e.code_str for e in over.errors}


def test_report_shows_mapping_and_altitude() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "left_finger_joint" in report
    assert "force_max_n = 185.0 N" in report
    assert "[VALID] grasp small_part at 60.0 N" in report
    assert "[REJECTED] grasp small_part at 250.0 N" in report
    assert "it does no" in report  # the honest-altitude note
