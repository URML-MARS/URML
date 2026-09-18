"""The Spot capture camera-selector worked example must be deterministic and true.

Mirrors the epically-powerful / rtic-timing / cram guards: the generator is
deterministic, the committed ``spot-capture-report.txt`` matches it, a targeted
capture on the movable hand camera validates, and a capture naming an undeclared
camera or a fixed fisheye (with a target) is rejected with the RFC-0699 codes.
For the rai-opensource spot_ros2 conversation (Discussion #805).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "spot-capture"
GEN_PATH = EX / "run_spot_capture.py"
COMMITTED = EX / "spot-capture-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("run_spot_capture", GEN_PATH)
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
        "examples/spot-capture/spot-capture-report.txt is stale; "
        "run `python examples/spot-capture/run_spot_capture.py` and commit."
    )


def test_named_camera_selector_validates_and_rejects() -> None:
    """RFC-0699: the `camera` selector scopes capture's checks to one camera."""
    gen = _load_gen()
    manifest = gen._load(gen.MANIFEST)

    ok, _, _ = gen._run(
        gen._capture_program(
            {"media": "photo", "camera": "hand_color", "target": "$subject", "store_as": "shot"},
            detect=True,
        ),
        manifest,
    )
    assert ok, "a targeted capture on the movable hand_color camera should validate"

    bad_c, bad_c_codes, _ = gen._run(
        gen._capture_program({"media": "photo", "camera": "chest_cam", "store_as": "shot"}),
        manifest,
    )
    assert not bad_c, "a capture naming an undeclared camera should be rejected"
    assert "capability.missing_camera" in bad_c_codes

    bad_f, bad_f_codes, _ = gen._run(
        gen._capture_program(
            {"media": "photo", "camera": "frontleft_fisheye", "target": "$subject", "store_as": "shot"},
            detect=True,
        ),
        manifest,
    )
    assert not bad_f, "a targeted capture on a fixed fisheye should be rejected"
    assert "capability.fixed_camera_target" in bad_f_codes


def test_report_shows_cases_and_framing() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert "[VALID] capture(media: photo, camera: hand_color, target: $subject)" in report
    assert "[REJECTED] capture(media: photo, camera: chest_cam)" in report
    assert "[REJECTED] capture(media: photo, camera: frontleft_fisheye, target: $subject)" in report
    # Honest about altitude and provenance.
    assert "the per-robot adapter still drives the actual" in report
    assert "no dependency on spot_ros2" in report
