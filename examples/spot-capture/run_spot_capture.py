#!/usr/bin/env python3
"""Selecting the camera a `capture` shoots with, checked before dispatch.

For the rai-opensource spot_ros2 conversation (Discussion #805). A Spot carries
five fixed body fisheyes and one movable hand camera. A program that says "photograph
that valve" means the hand camera: a fixed fisheye cannot be pointed at a subject.

Before RFC-0699 `capture` had no way to name a camera, so a targeted capture
validated as long as *any* declared camera was movable. RFC-0699 adds an optional
`camera` selector naming a declared `perception.cameras` entry, and scopes the
media-support and movable-for-target checks to that one camera. Now:

  - capture(camera: hand_color, target: ...) validates: hand_color is movable.
  - capture(camera: nonexistent) is rejected: no such declared camera.
  - capture(camera: frontleft_fisheye, target: ...) is rejected: that fisheye is
    fixed, even though the movable hand_color exists on the same robot.

Hermetic and deterministic (validator only, no ROS, no robot), so the committed
``spot-capture-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "spot-capture.manifest.yaml"
_PROFILES = ("home",)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _capture_program(cap: dict[str, Any], *, detect: bool = False) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    if detect:
        steps.append({"detect": {"object": "person", "store_as": "subject"}})
    steps.append({"capture": cap})
    return {
        "profile": _PROFILES[0],
        "behavior": {"type": "sequence", "on_error": "abort_and_report", "steps": steps},
    }


def _run(program: dict[str, Any], manifest: Any) -> tuple[bool, list[str], dict[str, str]]:
    res = validate(program, manifest, profiles=_PROFILES, policy=None)
    codes = sorted({e.code_str for e in res.errors})
    msgs = {e.code_str: e.message for e in res.errors}
    return res.accepted, codes, msgs


def render_report() -> str:
    manifest = _load(MANIFEST)

    lines = [
        "URML: selecting the camera a capture shoots with, checked before dispatch.",
        "RFC-0699 adds an optional `camera` selector to the `capture` primitive, naming a",
        "declared perception.cameras entry. The validator scopes the media-support and",
        "movable-for-target checks to that one camera, statically, before any command is",
        "dispatched. For the rai-opensource spot_ros2 conversation (Discussion #805).",
        "",
        "The Spot Arm declares five fixed body fisheyes (photo-only) and one movable hand",
        "camera (hand_color, photo + video). A targeted capture means the hand camera; a",
        "fixed fisheye cannot be pointed at a subject.",
        "",
        "# 1. A targeted capture on the movable hand camera validates",
        "",
    ]

    ok, ok_codes, _ = _run(
        _capture_program(
            {"media": "photo", "camera": "hand_color", "target": "$subject", "store_as": "shot"},
            detect=True,
        ),
        manifest,
    )
    lines.append(f"[{'VALID' if ok else 'REJECTED'}] capture(media: photo, camera: hand_color, target: $subject)")
    if ok:
        lines.append("   Admissible: hand_color is movable and supports photo. Dispatch may proceed.")
    else:
        lines.append("   -> " + ", ".join(ok_codes))
    lines.append("")

    lines += ["# 2. A capture naming a camera the robot does not have is rejected", ""]
    bad_c, bad_c_codes, bad_c_msgs = _run(
        _capture_program({"media": "photo", "camera": "chest_cam", "store_as": "shot"}),
        manifest,
    )
    lines.append("[{}] capture(media: photo, camera: chest_cam)".format("VALID" if bad_c else "REJECTED"))
    lines.append("   -> " + ", ".join(bad_c_codes))
    if "capability.missing_camera" in bad_c_msgs:
        lines.append(f"   capability.missing_camera: {bad_c_msgs['capability.missing_camera']}")
    lines.append("")

    lines += [
        "# 3. A targeted capture on a fixed fisheye is rejected, even though a movable",
        "#    camera exists on the same robot (the motivating case from #805)",
        "",
    ]
    bad_f, bad_f_codes, bad_f_msgs = _run(
        _capture_program(
            {"media": "photo", "camera": "frontleft_fisheye", "target": "$subject", "store_as": "shot"},
            detect=True,
        ),
        manifest,
    )
    lines.append(
        f"[{'VALID' if bad_f else 'REJECTED'}] capture(media: photo, camera: frontleft_fisheye, target: $subject)"
    )
    lines.append("   -> " + ", ".join(bad_f_codes))
    if "capability.fixed_camera_target" in bad_f_msgs:
        lines.append(f"   capability.fixed_camera_target: {bad_f_msgs['capability.fixed_camera_target']}")
    lines.append("   Before RFC-0699 this validated against the movable hand_color camera, so a")
    lines.append("   program that named the wrong camera passed the static gate.")
    lines.append("")

    lines += [
        "# What the selector buys",
        "",
        "The `camera` selector turns capture's existing checks (mode support, movable for a",
        "targeted shot) from any-eligible-camera into this-camera. Omitting it keeps the old",
        "behavior, so existing programs are unaffected. URML validates the intent against the",
        "declared manifest before dispatch; the per-robot adapter still drives the actual",
        "camera. No code is vendored and there is no dependency on spot_ros2.",
    ]

    # Assert the claims, so a behavior drift fails CI.
    assert ok, "a targeted capture on the movable hand camera should validate"
    assert not bad_c, "a capture naming an undeclared camera should be rejected"
    assert "capability.missing_camera" in bad_c_codes, "the undeclared-camera case should carry missing_camera"
    assert not bad_f, "a targeted capture on a fixed camera should be rejected"
    assert "capability.fixed_camera_target" in bad_f_codes, "the fixed-camera case should carry fixed_camera_target"

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "spot-capture-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
