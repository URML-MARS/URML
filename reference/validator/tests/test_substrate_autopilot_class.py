"""Unit tests for RFC-0250 substrate.autopilot_class.

Drone-class deployments (mobility.drive_type in multirotor / fixed_wing /
vtol) must declare substrate.autopilot_class as one of px4 / ardupilot /
pixhawk_classic / custom. When `custom`, an autopilot_class_note is
required.

These tests exercise the validator pass in isolation: a minimal program
plus a drone-class manifest, varying only the substrate declaration.
"""

from __future__ import annotations

from typing import Any

import pytest

from urml_validator import ErrorCode, validate


def _drone_manifest(
    *,
    substrate: dict[str, Any] | None = None,
    drive_type: str = "multirotor",
) -> dict[str, Any]:
    """A minimal drone manifest. `substrate` is set verbatim if not None."""
    m: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "test_drone",
        "frames": [
            {"name": "wgs84", "parent": None},
            {"name": "agl", "parent": "wgs84"},
        ],
        "declared_locations": [
            {
                "name": "home",
                "pose": {"x": 0.0, "y": 0.0, "z": 0.0},
                "frame": "agl",
            }
        ],
        "mobility": {
            "drive_type": drive_type,
            "max_velocity": 15.0,
            "station_keeping": True,
            "service_ceiling": 120.0,
        },
        "perception": {"cameras": [], "sensors": [], "object_vocabulary": []},
    }
    if substrate is not None:
        m["substrate"] = substrate
    return m


def _take_off_program() -> dict[str, Any]:
    return {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"take_off": {"altitude": 30.0}}, {"land": {}}],
        },
    }


# ---------------------------------------------------------------------------
# Positive cases: each allowed autopilot_class value validates
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "autopilot_class",
    ["px4", "ardupilot", "pixhawk_classic"],
)
def test_known_autopilot_class_validates(autopilot_class: str) -> None:
    manifest = _drone_manifest(substrate={"autopilot_class": autopilot_class})
    result = validate(_take_off_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_custom_autopilot_class_with_note_validates() -> None:
    manifest = _drone_manifest(
        substrate={
            "autopilot_class": "custom",
            "autopilot_class_note": "Proprietary in-house autopilot v3.2.",
        }
    )
    result = validate(_take_off_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


@pytest.mark.parametrize("drive_type", ["fixed_wing", "vtol"])
def test_other_drone_drive_types_require_autopilot_class(drive_type: str) -> None:
    # Positive: declared substrate passes for any drone-class drive_type.
    manifest = _drone_manifest(
        drive_type=drive_type,
        substrate={"autopilot_class": "px4"},
    )
    result = validate(_take_off_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


@pytest.mark.parametrize("drive_type", ["fixed_wing", "vtol"])
def test_other_drone_drive_types_without_substrate_rejected(drive_type: str) -> None:
    manifest = _drone_manifest(drive_type=drive_type, substrate=None)
    result = validate(_take_off_program(), manifest, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_AUTOPILOT_CLASS)


# ---------------------------------------------------------------------------
# Negative cases: rejected when substrate / note missing
# ---------------------------------------------------------------------------


def test_drone_without_substrate_rejected() -> None:
    manifest = _drone_manifest(substrate=None)
    result = validate(_take_off_program(), manifest, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_AUTOPILOT_CLASS)


def test_drone_with_substrate_but_no_autopilot_class_rejected() -> None:
    manifest = _drone_manifest(substrate={})
    result = validate(_take_off_program(), manifest, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_AUTOPILOT_CLASS)


def test_custom_autopilot_class_without_note_rejected() -> None:
    manifest = _drone_manifest(substrate={"autopilot_class": "custom"})
    result = validate(_take_off_program(), manifest, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_AUTOPILOT_CLASS_NOTE_REQUIRED)


def test_custom_autopilot_class_with_empty_note_rejected() -> None:
    manifest = _drone_manifest(
        substrate={"autopilot_class": "custom", "autopilot_class_note": "   "}
    )
    result = validate(_take_off_program(), manifest, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_AUTOPILOT_CLASS_NOTE_REQUIRED)


# ---------------------------------------------------------------------------
# Backward compatibility: non-drone manifests don't need substrate
# ---------------------------------------------------------------------------


def test_ground_robot_without_substrate_validates() -> None:
    manifest: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "test_ground",
        "frames": [{"name": "world", "parent": None}],
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "world"}
        ],
        "mobility": {
            "drive_type": "differential",
            "max_velocity": 1.0,
        },
        "perception": {"cameras": [], "sensors": [], "object_vocabulary": []},
    }
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"move_to": {"location": "home"}}],
        },
    }
    result = validate(program, manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_quadruped_without_substrate_validates() -> None:
    """RFC-0250's required-when-drone rule does not apply to quadruped."""
    manifest: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "test_quad",
        "frames": [{"name": "world", "parent": None}],
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "world"}
        ],
        "mobility": {
            "drive_type": "quadruped",
            "max_velocity": 1.5,
        },
        "perception": {"cameras": [], "sensors": [], "object_vocabulary": []},
    }
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"move_to": {"location": "home"}}],
        },
    }
    result = validate(program, manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]
