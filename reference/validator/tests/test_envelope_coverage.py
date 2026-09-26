"""Envelope coverage: every limit the spec requires, on every verb that can break it.

Regression tests for the Pass-3 holes closed by the envelope-coverage work.
Each test isolates one failure mode against a small in-memory manifest and
envelope, and asserts on the stable error code (and, where it matters, on the
primitive the error is attributed to). Messages are not asserted.

The conformance fixtures under ``conformance/fixtures/`` pin the same cells
end to end; ``docs/safety/envelope-coverage.md`` is the matrix.
"""

from __future__ import annotations

import copy
from typing import Any

from urml_validator import ErrorCode, validate


def _program(*steps: dict[str, Any], profile: str = "industrial") -> dict[str, Any]:
    return {
        "profile": profile,
        "behavior": {"type": "sequence", "on_error": "abort_and_report", "steps": list(steps)},
    }


def _codes_for(result: Any, primitive: str) -> set[str]:
    """Error codes the validator attributed to ``primitive``."""
    return {e.code.value for e in result.errors if e.primitive == primitive}


# ---------------------------------------------------------------------------
# Shared manifests
# ---------------------------------------------------------------------------


def _cell_manifest() -> dict[str, Any]:
    """A single-arm cell: two point locations, one area, one docking station."""
    return {
        "robot_id": "cell",
        "frames": [{"name": "cell"}, {"name": "base_link", "parent": "cell"}],
        "declared_locations": [
            {"name": "pick_bin", "pose": {"x": 0.4, "y": -0.3, "z": 0.1}, "frame": "cell"},
            {"name": "tray", "pose": {"x": -0.4, "y": 0.2, "z": 0.1}, "frame": "cell"},
            {"name": "high_shelf", "pose": {"x": 0.0, "y": 0.4, "z": 1.5}, "frame": "cell"},
        ],
        "declared_areas": [
            {
                "name": "bench",
                "frame": "cell",
                "polygon": [
                    {"x": 0.1, "y": 0.1},
                    {"x": 0.3, "y": 0.1},
                    {"x": 0.3, "y": 0.3},
                    {"x": 0.1, "y": 0.3},
                ],
            }
        ],
        "docking_stations": [
            {
                "name": "tool_rack",
                "pose": {"x": 0.2, "y": 0.5, "z": 0.2},
                "frame": "cell",
                "services": ["park", "swap_tool"],
            }
        ],
        "mobility": {"drive_type": "manipulator_base", "max_velocity": 0.5, "station_keeping": True},
        "manipulation": {
            "arm_count": 2,
            "grippers": [
                {
                    "name": "fingers",
                    "kind": "servo_electric",
                    "force_min_n": 1.0,
                    "force_max_n": 40.0,
                    "accepted_classes": ["widget"],
                }
            ],
        },
        "perception": {
            "cameras": [{"name": "wrist", "supports_photo": True}],
            "sensors": [],
            "object_vocabulary": ["widget"],
        },
    }


def _drone_manifest() -> dict[str, Any]:
    """A multirotor with three point locations and one declared area, all in `agl`."""
    return {
        "robot_id": "drone",
        "frames": [{"name": "wgs84"}, {"name": "agl", "parent": "wgs84"}],
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "agl"},
            {"name": "roof", "pose": {"x": 10.0, "y": 5.0, "z": 30.0}, "frame": "agl"},
            {"name": "far", "pose": {"x": 40.0, "y": 20.0, "z": 30.0}, "frame": "agl"},
            {"name": "tower_top", "pose": {"x": 5.0, "y": 5.0, "z": 500.0}, "frame": "agl"},
        ],
        "declared_areas": [
            {
                "name": "field",
                "frame": "agl",
                "polygon": [
                    {"x": 0.0, "y": 0.0},
                    {"x": 30.0, "y": 0.0},
                    {"x": 30.0, "y": 10.0},
                    {"x": 0.0, "y": 10.0},
                ],
            }
        ],
        "mobility": {
            "drive_type": "multirotor",
            "max_velocity": 15.0,
            "station_keeping": True,
            "service_ceiling": 120.0,
        },
        "substrate": {"autopilot_class": "px4"},
        "perception": {
            "cameras": [{"name": "downward", "supports_photo": True}],
            "sensors": [],
            "object_vocabulary": ["vehicle"],
        },
    }


def _flight(*steps: dict[str, Any]) -> dict[str, Any]:
    return _program({"take_off": {"altitude": 30.0}}, *steps, profile="drone")


# ---------------------------------------------------------------------------
# Grip-force cap: pick_from and each bimanual side (spec L738-740, L895-896)
# ---------------------------------------------------------------------------


class TestGripForceCap:
    def test_pick_from_over_envelope_cap_rejected(self) -> None:
        program = _program({"pick_from": {"source": "pick_bin", "object": "widget", "force": 30.0}})
        result = validate(program, _cell_manifest(), {"max_grip_force_n": 25.0}, policy=None)
        assert not result.accepted
        assert "envelope.force_exceeded" in _codes_for(result, "pick_from")
        # 30 N is inside the gripper's 1..40 N range: only the envelope refuses it.
        assert ErrorCode.CAPABILITY_MISSING_GRIPPER not in {e.code for e in result.errors}

    def test_pick_from_within_envelope_cap_accepted(self) -> None:
        program = _program({"pick_from": {"source": "pick_bin", "object": "widget", "force": 20.0}})
        result = validate(program, _cell_manifest(), {"max_grip_force_n": 25.0}, policy=None)
        assert result.accepted, result.codes()

    def test_pick_from_over_gripper_max_also_hits_envelope_cap(self) -> None:
        """Above the gripper's own maximum, both the capability and envelope checks fire."""
        program = _program({"pick_from": {"source": "pick_bin", "object": "widget", "force": 250.0}})
        result = validate(program, _cell_manifest(), None, policy=None)
        assert ErrorCode.CAPABILITY_MISSING_GRIPPER in {e.code for e in result.errors}
        assert "envelope.force_exceeded" in _codes_for(result, "pick_from")

    def test_pick_from_level_force_resolves(self) -> None:
        """`firm` resolves to 8 N, above a 5 N deployment cap."""
        program = _program({"pick_from": {"source": "pick_bin", "object": "widget", "force": "firm"}})
        result = validate(program, _cell_manifest(), {"max_grip_force_n": 5.0}, policy=None)
        assert "envelope.force_exceeded" in _codes_for(result, "pick_from")

    def test_bimanual_each_side_over_cap_rejected(self) -> None:
        program = _program(
            {"detect": {"object": "widget", "store_as": "w"}},
            {
                "bimanual": {
                    "mode": "together",
                    "left": {"target": "$w", "force": 30.0},
                    "right": {"target": "$w", "force": 30.0},
                }
            },
        )
        result = validate(program, _cell_manifest(), {"max_grip_force_n": 10.0}, policy=None)
        assert not result.accepted
        errs = [
            e
            for e in result.errors
            if e.code == ErrorCode.ENVELOPE_FORCE_EXCEEDED and e.primitive == "bimanual"
        ]
        assert sorted(e.path[-1] for e in errs) == ["left", "right"]

    def test_bimanual_one_side_over_cap_rejected(self) -> None:
        program = _program(
            {"detect": {"object": "widget", "store_as": "w"}},
            {
                "bimanual": {
                    "mode": "independent",
                    "left": {"target": "$w", "force": "gentle"},
                    "right": {"target": "$w", "force": 12.0},
                }
            },
        )
        result = validate(program, _cell_manifest(), {"max_grip_force_n": 10.0}, policy=None)
        errs = [
            e
            for e in result.errors
            if e.code == ErrorCode.ENVELOPE_FORCE_EXCEEDED and e.primitive == "bimanual"
        ]
        assert [e.path[-1] for e in errs] == ["right"]

    def test_bimanual_release_side_has_no_force(self) -> None:
        program = _program(
            {"detect": {"object": "widget", "store_as": "w"}},
            {
                "bimanual": {
                    "mode": "independent",
                    "left": {"target": "$w", "force": "gentle"},
                    "right": {"mode": "drop"},
                }
            },
        )
        result = validate(program, _cell_manifest(), {"max_grip_force_n": 10.0}, policy=None)
        assert result.accepted, result.codes()

    def test_grasp_cap_unchanged_by_the_helper(self) -> None:
        """The single-arm grasp check keeps its behavior after the helper refactor."""
        program = _program(
            {"detect": {"object": "widget", "store_as": "w"}},
            {"grasp": {"target": "$w", "force": 12.0}},
        )
        result = validate(program, _cell_manifest(), {"max_grip_force_n": 10.0}, policy=None)
        assert "envelope.force_exceeded" in _codes_for(result, "grasp")
        ok = copy.deepcopy(program)
        ok["behavior"]["steps"][1]["grasp"]["force"] = 9.0
        assert validate(ok, _cell_manifest(), {"max_grip_force_n": 10.0}, policy=None).accepted


# ---------------------------------------------------------------------------
# Fraction speeds (spec L88: a fraction of the manifest maximum; L147-148)
# ---------------------------------------------------------------------------


def _move_to_tray(speed: Any) -> dict[str, Any]:
    return _program({"move_to": {"location": "tray", "speed": speed}})


class TestFractionSpeed:
    """A fraction is of mobility.max_velocity (0.5 m/s in the cell manifest)."""

    def test_fraction_within_cap_accepted(self) -> None:
        # 0.4 x 0.5 m/s = 0.2 m/s, under the 0.25 m/s deployment cap.
        speed = {"value": 0.4, "units": "fraction"}
        result = validate(_move_to_tray(speed), _cell_manifest(), {"max_velocity": 0.25}, policy=None)
        assert result.accepted, result.codes()

    def test_fraction_over_envelope_cap_rejected(self) -> None:
        # 0.8 x 0.5 m/s = 0.4 m/s, over the 0.25 m/s deployment cap.
        speed = {"value": 0.8, "units": "fraction"}
        result = validate(_move_to_tray(speed), _cell_manifest(), {"max_velocity": 0.25}, policy=None)
        assert not result.accepted
        assert "envelope.velocity_exceeded" in _codes_for(result, "move_to")

    def test_fraction_above_one_exceeds_the_manifest_maximum(self) -> None:
        # 1.5 x 0.5 m/s = 0.75 m/s, over the manifest's own 0.5 m/s, with no envelope.
        speed = {"value": 1.5, "units": "fraction"}
        result = validate(_move_to_tray(speed), _cell_manifest(), None, policy=None)
        assert not result.accepted
        assert "envelope.velocity_exceeded" in _codes_for(result, "move_to")

    def test_fraction_of_exactly_one_accepted(self) -> None:
        speed = {"value": 1.0, "units": "fraction"}
        result = validate(_move_to_tray(speed), _cell_manifest(), None, policy=None)
        assert result.accepted, result.codes()

    def test_fraction_without_mobility_reports_only_the_capability_gap(self) -> None:
        manifest = _cell_manifest()
        del manifest["mobility"]
        speed = {"value": 1.5, "units": "fraction"}
        result = validate(_move_to_tray(speed), manifest, None, policy=None)
        assert ErrorCode.CAPABILITY_MISSING_MOBILITY in {e.code for e in result.errors}
        assert ErrorCode.ENVELOPE_VELOCITY_EXCEEDED not in {e.code for e in result.errors}

    def test_absolute_speeds_unchanged(self) -> None:
        for speed in ({"value": 0.3, "units": "m_per_s"}, 0.3):
            result = validate(
                _move_to_tray(speed), _cell_manifest(), {"max_velocity": 0.25}, policy=None
            )
            assert "envelope.velocity_exceeded" in _codes_for(result, "move_to"), speed


# ---------------------------------------------------------------------------
# Named targets resolve before any spatial check can run (Pass 2)
# ---------------------------------------------------------------------------


class TestNamedTargetsResolve:
    """land.at, hover.over, detect.where.near and release.at must name a declared place."""

    def test_land_at_undeclared_rejected(self) -> None:
        result = validate(_flight({"land": {"at": "helipad_9"}}), _drone_manifest(), None, policy=None)
        assert "capability.missing_location" in _codes_for(result, "land")

    def test_land_at_declared_location_and_area_accepted(self) -> None:
        for at in ("home", "field"):
            result = validate(_flight({"land": {"at": at}}), _drone_manifest(), None, policy=None)
            assert result.accepted, (at, result.codes())

    def test_hover_over_undeclared_rejected(self) -> None:
        program = _flight({"hover": {"over": "helipad_9", "duration": "5s"}})
        result = validate(program, _drone_manifest(), None, policy=None)
        assert "capability.missing_location" in _codes_for(result, "hover")

    def test_hover_over_a_binding_is_left_to_the_binding_pass(self) -> None:
        program = _flight(
            {"detect": {"object": "vehicle", "store_as": "car"}},
            {"hover": {"over": "$car", "duration": "5s"}},
        )
        result = validate(program, _drone_manifest(), None, policy=None)
        assert result.accepted, result.codes()

    def test_detect_near_undeclared_rejected(self) -> None:
        program = _flight({"detect": {"object": "vehicle", "where": {"near": "parking_lot"}}})
        result = validate(program, _drone_manifest(), None, policy=None)
        assert "capability.missing_location" in _codes_for(result, "detect")

    def test_detect_near_declared_area_accepted(self) -> None:
        program = _flight({"detect": {"object": "vehicle", "where": {"near": "field", "within": 5.0}}})
        result = validate(program, _drone_manifest(), None, policy=None)
        assert result.accepted, result.codes()

    def test_detect_without_perception_still_reports_the_name(self) -> None:
        manifest = _drone_manifest()
        del manifest["perception"]
        program = _flight({"detect": {"object": "vehicle", "where": {"near": "parking_lot"}}})
        result = validate(program, manifest, None, policy=None)
        assert "capability.missing_location" in _codes_for(result, "detect")

    def test_release_at_undeclared_rejected(self) -> None:
        program = _program({"release": {"mode": "place", "at": "garage_shelf"}})
        result = validate(program, _cell_manifest(), None, policy=None)
        assert "capability.missing_location" in _codes_for(result, "release")

    def test_release_at_declared_location_and_area_accepted(self) -> None:
        for at in ("tray", "bench"):
            program = _program({"release": {"mode": "place", "at": at}})
            result = validate(program, _cell_manifest(), None, policy=None)
            assert result.accepted, (at, result.codes())

    def test_release_side_of_bimanual_resolves_too(self) -> None:
        program = _program(
            {"detect": {"object": "widget", "store_as": "w"}},
            {
                "bimanual": {
                    "mode": "independent",
                    "left": {"target": "$w", "force": "gentle"},
                    "right": {"mode": "place", "at": "garage_shelf"},
                }
            },
        )
        result = validate(program, _cell_manifest(), None, policy=None)
        errs = [e for e in result.errors if e.code == ErrorCode.CAPABILITY_MISSING_LOCATION]
        assert errs and errs[0].path[-1] == "right"
