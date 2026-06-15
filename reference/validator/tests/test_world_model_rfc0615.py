"""Unit tests for RFC-0615: declared areas (rooms) + object-detection responsibility.

The manifest gains two optional, declaration-only world-model fields, surfaced by
the linorobot2 / Dallas PRG feedback:

- `declared_areas`: named regions (rooms / zones) a primitive may target by name,
  alongside point `declared_locations`. An area's frame must be declared.
- `perception.object_detection`: which declared sensor detects which declared
  object class. The class must be in `object_vocabulary`; the sensor must be a
  declared camera or sensor.

URML does not map areas or perform detection; these are bounded, robot-specific
declarations the validator checks for self-consistency. Both are optional; a
manifest without them is unaffected.
"""

from __future__ import annotations

from typing import Any

from urml_validator import ErrorCode, validate


def _manifest(
    *,
    areas: list[dict[str, Any]] | None = None,
    object_detection: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    m: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "test_home",
        "frames": [{"name": "map", "parent": None}],
        "declared_locations": [
            {"name": "dock", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "map"}
        ],
        "mobility": {"drive_type": "differential", "max_velocity": 1.0},
        "perception": {
            "cameras": [{"name": "head_rgb", "supports_photo": True}],
            "sensors": [],
            "object_vocabulary": ["mug", "cup"],
        },
    }
    if areas is not None:
        m["declared_areas"] = areas
    if object_detection is not None:
        m["perception"]["object_detection"] = object_detection
    return m


def _move_to(name: str) -> dict[str, Any]:
    return {
        "profile": "home",
        "behavior": {"type": "sequence", "on_error": "abort_and_report", "steps": [{"move_to": {"location": name}}]},
    }


def _poly(*xy: tuple[float, float]) -> list[dict[str, float]]:
    return [{"x": x, "y": y} for x, y in xy]


_KITCHEN = {"name": "kitchen", "frame": "map", "polygon": _poly((0.0, 0.0), (2.0, 0.0), (2.0, 2.0), (0.0, 2.0))}


def test_move_to_a_declared_area_validates() -> None:
    result = validate(_move_to("kitchen"), _manifest(areas=[_KITCHEN]), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_move_to_point_location_still_validates() -> None:
    result = validate(_move_to("dock"), _manifest(areas=[_KITCHEN]), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_move_to_undeclared_name_rejected() -> None:
    result = validate(_move_to("garage"), _manifest(areas=[_KITCHEN]), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_LOCATION)


def test_area_with_undeclared_frame_rejected() -> None:
    bad = {"name": "lab", "frame": "nowhere", "polygon": _poly((0.0, 0.0), (1.0, 0.0), (1.0, 1.0))}
    result = validate(_move_to("dock"), _manifest(areas=[bad]), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_AREA_FRAME_UNDECLARED)


def test_object_detection_validates() -> None:
    od = [{"object_class": "mug", "sensor": "head_rgb"}]
    result = validate(_move_to("dock"), _manifest(object_detection=od), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_object_detection_unknown_class_rejected() -> None:
    od = [{"object_class": "banana", "sensor": "head_rgb"}]
    result = validate(_move_to("dock"), _manifest(object_detection=od), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_DETECTOR_UNKNOWN_OBJECT_CLASS)


def test_object_detection_unknown_sensor_rejected() -> None:
    od = [{"object_class": "mug", "sensor": "lidar_42"}]
    result = validate(_move_to("dock"), _manifest(object_detection=od), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_DETECTOR_UNKNOWN_SENSOR)


def test_no_world_model_fields_unaffected() -> None:
    result = validate(_move_to("dock"), _manifest(), policy=None)
    assert result.accepted, [e.code for e in result.errors]
