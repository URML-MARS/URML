"""Unit tests for the drone-profile primitives.

Authorized by RFC-0002 §Profile-extensibility (drone: take_off, land, return_to_home).
Specified by spec/profiles/drone/README.md §Layer-2 primitives this profile adds.
"""

from __future__ import annotations

from typing import Any

import pytest

from urml_validator import ErrorCode, validate


def _drone_manifest(**overrides: Any) -> dict[str, Any]:
    """A minimal multirotor drone manifest with a service ceiling and home location."""
    base: dict[str, Any] = {
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
            "drive_type": "multirotor",
            "max_velocity": 15.0,
            "station_keeping": True,
            "service_ceiling": 120.0,
        },
        "perception": {
            "cameras": [{"name": "downward", "supports_photo": True, "supports_video": True}],
            "sensors": [],
            "object_vocabulary": [],
        },
    }
    base.update(overrides)
    return base


def _drone_envelope(max_altitude: float = 120.0) -> dict[str, Any]:
    """A minimal drone safety envelope."""
    return {
        "envelope_version": "0.1",
        "deployment_id": "test",
        "max_velocity": 10.0,
        "max_altitude": max_altitude,
    }


def _program_with_step(step: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [step],
        },
    }


# ---------------------------------------------------------------------------
# take_off
# ---------------------------------------------------------------------------


class TestTakeOff:
    def test_take_off_accepted_on_multirotor_within_ceiling(self) -> None:
        program = _program_with_step({"take_off": {"altitude": 50.0}})
        result = validate(program, _drone_manifest(), _drone_envelope(), profiles=("drone",))
        assert result.accepted, result.codes()

    def test_take_off_rejected_on_non_aerial_drive_type(self) -> None:
        manifest = _drone_manifest()
        manifest["mobility"]["drive_type"] = "differential"
        program = _program_with_step({"take_off": {"altitude": 50.0}})
        result = validate(program, manifest, _drone_envelope(), profiles=("drone",))
        assert not result.accepted
        assert ErrorCode.CAPABILITY_DRIVE_TYPE_NOT_AERIAL.value in result.codes()

    def test_take_off_rejected_without_service_ceiling(self) -> None:
        manifest = _drone_manifest()
        manifest["mobility"].pop("service_ceiling")
        program = _program_with_step({"take_off": {"altitude": 50.0}})
        result = validate(program, manifest, _drone_envelope(), profiles=("drone",))
        assert not result.accepted
        assert ErrorCode.CAPABILITY_MISSING_SERVICE_CEILING.value in result.codes()

    def test_take_off_rejected_above_service_ceiling(self) -> None:
        program = _program_with_step({"take_off": {"altitude": 200.0}})
        result = validate(program, _drone_manifest(), _drone_envelope(max_altitude=300.0), profiles=("drone",))
        assert not result.accepted
        # 200 > service_ceiling 120 → capability check fires.
        assert ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED.value in result.codes()

    def test_take_off_rejected_above_envelope_cap(self) -> None:
        program = _program_with_step({"take_off": {"altitude": 100.0}})
        # service_ceiling=120 (ok), envelope=50 (tighter — should fire).
        result = validate(program, _drone_manifest(), _drone_envelope(max_altitude=50.0), profiles=("drone",))
        assert not result.accepted
        assert ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED.value in result.codes()

    def test_take_off_requires_positive_altitude(self) -> None:
        program = _program_with_step({"take_off": {"altitude": 0.0}})
        result = validate(program, _drone_manifest(), _drone_envelope(), profiles=("drone",))
        assert not result.accepted
        # 0 fails Field(gt=0) → Pass 1 (argument).
        assert any(c.startswith("argument.") for c in result.codes())


# ---------------------------------------------------------------------------
# land
# ---------------------------------------------------------------------------


class TestLand:
    def test_land_accepted_on_multirotor(self) -> None:
        program = _program_with_step({"land": {}})
        result = validate(program, _drone_manifest(), _drone_envelope(), profiles=("drone",))
        assert result.accepted, result.codes()

    def test_land_rejected_on_ground_robot(self) -> None:
        manifest = _drone_manifest()
        manifest["mobility"]["drive_type"] = "differential"
        program = _program_with_step({"land": {}})
        result = validate(program, manifest, _drone_envelope(), profiles=("drone",))
        assert not result.accepted
        assert ErrorCode.CAPABILITY_DRIVE_TYPE_NOT_AERIAL.value in result.codes()

    def test_land_with_named_location(self) -> None:
        manifest = _drone_manifest()
        manifest["declared_locations"].append(
            {"name": "landing_pad", "pose": {"x": 5.0, "y": 5.0}, "frame": "agl"}
        )
        program = _program_with_step({"land": {"at": "landing_pad", "precision": "precise"}})
        result = validate(program, manifest, _drone_envelope(), profiles=("drone",))
        assert result.accepted, result.codes()


# ---------------------------------------------------------------------------
# return_to_home
# ---------------------------------------------------------------------------


class TestReturnToHome:
    def test_rth_accepted_with_home_location(self) -> None:
        program = _program_with_step({"return_to_home": {}})
        result = validate(program, _drone_manifest(), _drone_envelope(), profiles=("drone",))
        assert result.accepted, result.codes()

    def test_rth_rejected_without_home_location(self) -> None:
        manifest = _drone_manifest()
        manifest["declared_locations"] = []  # remove 'home'
        program = _program_with_step({"return_to_home": {}})
        result = validate(program, manifest, _drone_envelope(), profiles=("drone",))
        assert not result.accepted
        assert ErrorCode.CAPABILITY_MISSING_HOME_LOCATION.value in result.codes()

    def test_rth_altitude_within_caps(self) -> None:
        program = _program_with_step({"return_to_home": {"altitude": 80.0}})
        result = validate(program, _drone_manifest(), _drone_envelope(), profiles=("drone",))
        assert result.accepted, result.codes()

    def test_rth_altitude_above_service_ceiling(self) -> None:
        program = _program_with_step({"return_to_home": {"altitude": 200.0}})
        result = validate(program, _drone_manifest(), _drone_envelope(max_altitude=300.0), profiles=("drone",))
        assert not result.accepted
        assert ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED.value in result.codes()

    def test_rth_altitude_above_envelope_cap(self) -> None:
        program = _program_with_step({"return_to_home": {"altitude": 100.0}})
        result = validate(program, _drone_manifest(), _drone_envelope(max_altitude=50.0), profiles=("drone",))
        assert not result.accepted
        assert ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED.value in result.codes()

    def test_rth_optional_altitude(self) -> None:
        """Omitting altitude is allowed — substrate uses its default RTH altitude."""
        program = _program_with_step({"return_to_home": {"speed": 5.0}})
        result = validate(program, _drone_manifest(), _drone_envelope(), profiles=("drone",))
        assert result.accepted, result.codes()


# ---------------------------------------------------------------------------
# Inspection-flight sequence (the canonical drone scenario)
# ---------------------------------------------------------------------------


class TestInspectionFlight:
    def test_full_inspection_flight(self) -> None:
        manifest = _drone_manifest()
        manifest["declared_locations"].append(
            {
                "name": "roof_north",
                "pose": {"x": 10.0, "y": 5.0, "z": 30.0},
                "frame": "agl",
            }
        )
        program = {
            "profile": "drone",
            "behavior": {
                "type": "sequence",
                "on_error": "abort_and_report",
                "steps": [
                    {"take_off": {"altitude": 30.0}},
                    {"move_to": {"location": "roof_north"}},
                    {"capture": {"media": "photo", "store_as": "photo1"}},
                    {"return_to_home": {}},
                    {"land": {}},
                ],
            },
        }
        result = validate(program, manifest, _drone_envelope(), profiles=("drone",))
        assert result.accepted, result.codes()
