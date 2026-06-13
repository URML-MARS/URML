"""Unit tests for RFC-0518 base-level mobility bounds.

The Mobility block gains optional base-level motion bounds for a velocity-
controlled mobile base: max angular velocity, linear/angular acceleration, and
terrain bounds (traversable slope, obstacle height). Surfaced by the
quadruped_ros2_control engagement, where the quadruped is exposed as an
omnidirectional base and intent is validated at the base-velocity level (the
whole-body internals are not exposed).

Field validity is schema-enforced (non-negative; slope in (0, 90]). The one
validator coherence rule: terrain bounds are not applicable to an aerial drive
(`capability.terrain_bound_not_applicable`). The fields are optional; a manifest
without them is unaffected.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import ErrorCode, validate
from urml_validator.schemas.manifest import CapabilityManifest


def _manifest(*, drive_type: str = "omnidirectional", **mobility: Any) -> dict[str, Any]:
    m: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "test_base",
        "frames": [{"name": "world", "parent": None}],
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "world"}
        ],
        "mobility": {"drive_type": drive_type, "max_velocity": 1.0, **mobility},
        "perception": {"cameras": [], "sensors": [], "object_vocabulary": []},
    }
    return m


def _move_program() -> dict[str, Any]:
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"move_to": {"location": "home"}}],
        },
    }


def test_base_bounds_validate() -> None:
    m = _manifest(
        max_angular_velocity=1.5,
        max_linear_acceleration=2.0,
        max_angular_acceleration=3.0,
        max_traversable_slope_deg=25.0,
        max_obstacle_height_m=0.12,
        max_payload=20.0,
    )
    result = validate(_move_program(), m, policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_no_base_bounds_validates() -> None:
    result = validate(_move_program(), _manifest(), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_aerial_terrain_slope_rejected() -> None:
    m = _manifest(drive_type="multirotor", max_traversable_slope_deg=20.0)
    result = validate(_move_program(), m, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_TERRAIN_BOUND_NOT_APPLICABLE)


def test_aerial_obstacle_height_rejected() -> None:
    m = _manifest(drive_type="vtol", max_obstacle_height_m=0.3)
    result = validate(_move_program(), m, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_TERRAIN_BOUND_NOT_APPLICABLE)


def test_ground_terrain_bounds_allowed() -> None:
    """A quadruped exposed as a base may declare terrain bounds."""
    m = _manifest(drive_type="quadruped", max_traversable_slope_deg=30.0, max_obstacle_height_m=0.2)
    result = validate(_move_program(), m, policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_negative_angular_velocity_rejected_by_schema() -> None:
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(_manifest(max_angular_velocity=-1.0))


def test_slope_over_90_rejected_by_schema() -> None:
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(_manifest(max_traversable_slope_deg=120.0))
