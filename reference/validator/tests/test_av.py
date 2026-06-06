"""Unit tests for RFC-0020 AV profile: plan_path / follow_trajectory.

`plan_path` is a compute verb that binds a `trajectory`; `follow_trajectory`
consumes it (the detect -> object -> grasp precedent). Validator rules:

  - plan_path requires `av.hd_map` (capability.missing_hd_map);
  - follow_trajectory.trajectory must be a `trajectory` binding
    (binding.type_mismatch otherwise);
  - follow_trajectory.speed_envelope.max_velocity_mps must not exceed the
    strictest of the ODD cap / mobility max / envelope max
    (envelope.velocity_exceeded).
"""

from __future__ import annotations

import copy
from typing import Any

from urml_validator import ErrorCode, validate


def _av_manifest() -> dict[str, Any]:
    return {
        "manifest_version": "0.1",
        "robot_id": "test_av",
        "frames": [{"name": "map", "parent": None}],
        "declared_locations": [
            {"name": "depot", "pose": {"x": 0.0, "y": 0.0}, "frame": "map"},
            {"name": "dropoff", "pose": {"x": 120.0, "y": 40.0}, "frame": "map"},
        ],
        "mobility": {"drive_type": "ackermann", "max_velocity": 20.0},
        "perception": {"cameras": [], "sensors": [], "object_vocabulary": ["cone"]},
        "av": {
            "hd_map": {"format": "lanelet2", "uri": "./city.osm"},
            "odd": {"max_velocity_mps": 15.0},
            "mrm": {"strategy": "pull_over"},
        },
    }


def _plan_follow(speed: float | None = 12.0) -> dict[str, Any]:
    follow: dict[str, Any] = {"trajectory": "$route"}
    if speed is not None:
        follow["speed_envelope"] = {"max_velocity_mps": speed}
    return {
        "profile": "av",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"plan_path": {"from": "depot", "to": "dropoff", "store_as": "route"}},
                {"follow_trajectory": follow},
            ],
        },
    }


def test_plan_follow_accepted() -> None:
    result = validate(_plan_follow(), _av_manifest(), policy=None)
    assert result.accepted, [e.code.value for e in result.errors]


def test_plan_path_requires_hd_map() -> None:
    m = _av_manifest()
    del m["av"]["hd_map"]
    result = validate(_plan_follow(), m, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_HD_MAP)


def test_follow_speed_over_odd_cap_rejected() -> None:
    result = validate(_plan_follow(speed=50.0), _av_manifest(), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_VELOCITY_EXCEEDED)


def test_follow_requires_trajectory_binding() -> None:
    """follow_trajectory consuming a detect-bound object is a type mismatch."""
    program = {
        "profile": "av",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"detect": {"object": "cone", "store_as": "c"}},
                {"follow_trajectory": {"trajectory": "$c"}},
            ],
        },
    }
    result = validate(program, _av_manifest(), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.BINDING_TYPE_MISMATCH)


def test_alt_trajectory_binding_resolves() -> None:
    """store_alt_as binds a second trajectory that follow_trajectory may consume."""
    program = {
        "profile": "av",
        "behavior": {
            "type": "sequence",
            "steps": [
                {
                    "plan_path": {
                        "from": "depot",
                        "to": "dropoff",
                        "store_as": "route",
                        "store_alt_as": "fallback",
                    }
                },
                {"follow_trajectory": {"trajectory": "$fallback"}},
            ],
        },
    }
    result = validate(program, _av_manifest(), policy=None)
    assert result.accepted, [e.code.value for e in result.errors]
