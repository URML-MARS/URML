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
from urml_validator.schemas.manifest import CapabilityManifest
from urml_validator.validator import _polygons_overlap, _resolve_place


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


# ---------------------------------------------------------------------------
# The place resolver and the polygon helper
# ---------------------------------------------------------------------------


class TestPlaceResolver:
    def test_location_resolves_to_a_point_with_altitude(self) -> None:
        place = _resolve_place("roof", CapabilityManifest.model_validate(_drone_manifest()))
        assert place is not None
        assert (place.frame, place.vertices, place.z, place.is_area) == (
            "agl",
            ((10.0, 5.0),),
            30.0,
            False,
        )

    def test_area_resolves_to_its_polygon(self) -> None:
        place = _resolve_place("field", CapabilityManifest.model_validate(_drone_manifest()))
        assert place is not None
        assert place.is_area and place.z is None
        assert place.vertices == ((0.0, 0.0), (30.0, 0.0), (30.0, 10.0), (0.0, 10.0))

    def test_station_resolves_only_when_asked(self) -> None:
        manifest = CapabilityManifest.model_validate(_cell_manifest())
        assert _resolve_place("tool_rack", manifest) is None
        station = _resolve_place("tool_rack", manifest, station=True)
        assert station is not None and station.vertices == ((0.2, 0.5),) and station.z == 0.2

    def test_unknown_name_resolves_to_none(self) -> None:
        manifest = CapabilityManifest.model_validate(_drone_manifest())
        assert _resolve_place("nowhere", manifest) is None
        assert _resolve_place("nowhere", manifest, station=True) is None


_SQUARE = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]


class TestPolygonsOverlap:
    def test_zone_entirely_inside_the_area(self) -> None:
        # No vertex of the area lies in the zone: a vertex-only test misses this.
        assert _polygons_overlap(_SQUARE, [(4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0)])

    def test_area_entirely_inside_the_zone(self) -> None:
        assert _polygons_overlap([(4.0, 4.0), (6.0, 4.0), (6.0, 6.0), (4.0, 6.0)], _SQUARE)

    def test_crossing_without_any_vertex_inside(self) -> None:
        # A plus sign: two bars cross, no vertex of either lies inside the other.
        bar = [(-5.0, 4.0), (15.0, 4.0), (15.0, 6.0), (-5.0, 6.0)]
        post = [(4.0, -5.0), (6.0, -5.0), (6.0, 15.0), (4.0, 15.0)]
        assert _polygons_overlap(bar, post)

    def test_disjoint(self) -> None:
        assert not _polygons_overlap(_SQUARE, [(20.0, 20.0), (30.0, 20.0), (30.0, 30.0)])

    def test_shared_edge_counts_as_overlap(self) -> None:
        assert _polygons_overlap(_SQUARE, [(10.0, 2.0), (20.0, 2.0), (20.0, 8.0), (10.0, 8.0)])


# ---------------------------------------------------------------------------
# Spatial checks on every place a step names (spec §1.2 Pass 3, L105-108)
# ---------------------------------------------------------------------------

_BOX = [[-5.0, -5.0], [15.0, -5.0], [15.0, 15.0], [-5.0, 15.0]]
_CROWD = [[-3.0, -3.0], [3.0, -3.0], [3.0, 3.0], [-3.0, 3.0]]


def _geofenced(frame: str = "agl", vertices: Any = None, **band: float) -> dict[str, Any]:
    fence = {"name": "box", "frame": frame, "vertices": vertices or _BOX, **band}
    return {"geofences": [fence]}


def _zoned(frame: str = "agl", vertices: Any = None, allow_override: bool = False) -> dict[str, Any]:
    zone = {
        "name": "crowd",
        "frame": frame,
        "vertices": vertices or _CROWD,
        "allow_override": allow_override,
    }
    return {"people_occupancy_zones": [zone]}


# The cell manifest's places: pick_bin (0.4, -0.3), tray (-0.4, 0.2),
# high_shelf (0.0, 0.4, z 1.5), tool_rack station (0.2, 0.5, z 0.2), bench area.
_CELL_FENCE = [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.35], [-0.5, 0.35]]
_TRAY_ZONE = [[-0.5, 0.1], [-0.3, 0.1], [-0.3, 0.3], [-0.5, 0.3]]
_RACK_ZONE = [[0.1, 0.4], [0.3, 0.4], [0.3, 0.6], [0.1, 0.6]]


class TestIndustrialPlaces:
    def test_pick_from_source_outside_geofence_rejected(self) -> None:
        program = _program({"pick_from": {"source": "high_shelf", "object": "widget"}})
        env = _geofenced("cell", _CELL_FENCE)
        result = validate(program, _cell_manifest(), env, policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "pick_from")

    def test_place_at_target_outside_geofence_rejected(self) -> None:
        program = _program(
            {"pick_from": {"source": "pick_bin", "object": "widget", "store_as": "w"}},
            {"place_at": {"target": "high_shelf", "held": "$w"}},
        )
        result = validate(program, _cell_manifest(), _geofenced("cell", _CELL_FENCE), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "place_at")
        assert "envelope.geofence_violation" not in _codes_for(result, "pick_from")

    def test_pick_from_and_place_at_in_a_zone_rejected(self) -> None:
        program = _program(
            {"pick_from": {"source": "tray", "object": "widget", "store_as": "w"}},
            {"place_at": {"target": "tray", "held": "$w"}},
        )
        result = validate(program, _cell_manifest(), _zoned("cell", _TRAY_ZONE), policy=None)
        assert "envelope.occupancy_zone_intrusion" in _codes_for(result, "pick_from")
        assert "envelope.occupancy_zone_intrusion" in _codes_for(result, "place_at")

    def test_places_inside_fence_and_clear_of_zone_accepted(self) -> None:
        program = _program(
            {"pick_from": {"source": "pick_bin", "object": "widget", "store_as": "w"}},
            {"place_at": {"target": "bench", "held": "$w"}},
        )
        env = {**_geofenced("cell", _CELL_FENCE), **_zoned("cell", _TRAY_ZONE)}
        result = validate(program, _cell_manifest(), env, policy=None)
        assert result.accepted, result.codes()

    def test_place_altitude_over_the_cap_rejected(self) -> None:
        # high_shelf sits at z 1.5; the deployment keeps the tool below 1.0 m.
        program = _program(
            {"pick_from": {"source": "high_shelf", "object": "widget", "store_as": "w"}},
            {"place_at": {"target": "high_shelf", "held": "$w"}},
        )
        result = validate(program, _cell_manifest(), {"max_altitude": 1.0}, policy=None)
        assert "envelope.altitude_exceeded" in _codes_for(result, "pick_from")
        assert "envelope.altitude_exceeded" in _codes_for(result, "place_at")

    def test_dock_station_outside_geofence_rejected(self) -> None:
        program = _program({"dock": {"at": "tool_rack", "service": "park"}})
        result = validate(program, _cell_manifest(), _geofenced("cell", _CELL_FENCE), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "dock")

    def test_dock_default_station_is_checked(self) -> None:
        program = _program({"dock": {"service": "park"}})
        result = validate(program, _cell_manifest(), _zoned("cell", _RACK_ZONE), policy=None)
        assert "envelope.occupancy_zone_intrusion" in _codes_for(result, "dock")

    def test_dock_station_altitude_over_the_cap_rejected(self) -> None:
        program = _program({"dock": {"at": "tool_rack", "service": "park"}})
        result = validate(program, _cell_manifest(), {"max_altitude": 0.1}, policy=None)
        assert "envelope.altitude_exceeded" in _codes_for(result, "dock")

    def test_frames_without_a_transform_abstain(self) -> None:
        """RFC-0290: a place in a frame with no transform to the fence's frame is not judged."""
        manifest = _cell_manifest()
        manifest["frames"].append({"name": "arm", "parent": "cell"})
        manifest["declared_locations"].append(
            {"name": "arm_rest", "pose": {"x": 100.0, "y": 100.0}, "frame": "arm"}
        )
        program = _program({"pick_from": {"source": "arm_rest", "object": "widget"}})
        result = validate(program, manifest, _geofenced("cell", _CELL_FENCE), policy=None)
        assert result.accepted, result.codes()

    def test_frames_with_a_transform_are_resolved(self) -> None:
        manifest = _cell_manifest()
        manifest["frames"].append(
            {"name": "arm", "parent": "cell", "transform": {"translation": {"x": 10.0}}}
        )
        manifest["declared_locations"].append(
            {"name": "arm_rest", "pose": {"x": 0.0, "y": 0.0}, "frame": "arm"}
        )
        program = _program({"pick_from": {"source": "arm_rest", "object": "widget"}})
        result = validate(program, manifest, _geofenced("cell", _CELL_FENCE), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "pick_from")


class TestFlightPlaces:
    """drone manifest: home (0, 0, 0), roof (10, 5, 30), far (40, 20, 30), tower_top z 500."""

    def test_hover_over_outside_geofence_rejected(self) -> None:
        program = _flight({"hover": {"over": "far", "duration": "5s"}})
        result = validate(program, _drone_manifest(), _geofenced(), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "hover")

    def test_hover_over_a_zone_rejected(self) -> None:
        program = _flight({"hover": {"over": "home", "duration": "5s"}})
        result = validate(program, _drone_manifest(), _zoned(), policy=None)
        assert "envelope.occupancy_zone_intrusion" in _codes_for(result, "hover")

    def test_hover_over_above_the_ceiling_rejected(self) -> None:
        program = _flight({"hover": {"over": "tower_top", "duration": "5s"}})
        result = validate(program, _drone_manifest(), None, policy=None)
        assert "envelope.altitude_exceeded" in _codes_for(result, "hover")

    def test_hover_over_inside_accepted(self) -> None:
        program = _flight({"hover": {"over": "roof", "duration": "5s"}})
        env = {**_geofenced(), **_zoned()}
        result = validate(program, _drone_manifest(), env, policy=None)
        assert result.accepted, result.codes()

    def test_land_outside_geofence_rejected(self) -> None:
        program = _flight({"land": {"at": "far"}})
        result = validate(program, _drone_manifest(), _geofenced(), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "land")

    def test_land_in_a_zone_rejected(self) -> None:
        program = _flight({"move_to": {"location": "roof"}}, {"land": {"at": "home"}})
        result = validate(program, _drone_manifest(), _zoned(), policy=None)
        assert "envelope.occupancy_zone_intrusion" in _codes_for(result, "land")

    def test_land_is_judged_by_footprint_not_altitude_band(self) -> None:
        """A landing ends on the ground, so the fence's altitude floor does not apply."""
        program = _flight({"move_to": {"location": "roof"}}, {"land": {"at": "home"}})
        env = _geofenced(min_altitude=10.0, max_altitude=50.0)
        result = validate(program, _drone_manifest(), env, policy=None)
        assert result.accepted, result.codes()

    def test_land_at_an_area_checks_every_vertex(self) -> None:
        # The field spans x 0..30: two vertices lie outside the -5..15 fence.
        program = _flight({"land": {"at": "field"}})
        result = validate(program, _drone_manifest(), _geofenced(), policy=None)
        errs = [
            e
            for e in result.errors
            if e.code == ErrorCode.ENVELOPE_GEOFENCE_VIOLATION and e.primitive == "land"
        ]
        assert len(errs) == 2

    def test_detect_near_outside_geofence_rejected(self) -> None:
        program = _flight({"detect": {"object": "vehicle", "where": {"near": "far"}}})
        result = validate(program, _drone_manifest(), _geofenced(), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "detect")

    def test_detect_near_is_not_an_occupancy_check(self) -> None:
        """detect only searches near the place; spec §2.8 asks for the operational area."""
        program = _flight({"detect": {"object": "vehicle", "where": {"near": "home"}}})
        result = validate(program, _drone_manifest(), _zoned(), policy=None)
        assert result.accepted, result.codes()

    def test_detect_search_radius_inside_geofence_accepted(self) -> None:
        # roof (10, 5) is 5 m from the fence edge at x 15; a 3 m radius fits.
        where = {"near": "roof", "within": 3.0}
        program = _flight({"detect": {"object": "vehicle", "where": where}})
        result = validate(program, _drone_manifest(), _geofenced(), policy=None)
        assert result.accepted, result.codes()

    def test_detect_search_radius_crossing_the_fence_rejected(self) -> None:
        # An 8 m radius around roof reaches x 18, past the fence edge at x 15.
        where = {"near": "roof", "within": 8.0}
        program = _flight({"detect": {"object": "vehicle", "where": where}})
        result = validate(program, _drone_manifest(), _geofenced(), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "detect")

    def test_detect_search_radius_without_geofence_accepted(self) -> None:
        where = {"near": "roof", "within": 8.0}
        program = _flight({"detect": {"object": "vehicle", "where": where}})
        assert validate(program, _drone_manifest(), None, policy=None).accepted

    def test_detect_search_radius_abstains_without_a_transform(self) -> None:
        manifest = _drone_manifest()
        manifest["frames"].append({"name": "cam", "parent": "agl"})
        manifest["declared_locations"].append(
            {"name": "gate", "pose": {"x": 0.0, "y": 0.0}, "frame": "cam"}
        )
        where = {"near": "gate", "within": 500.0}
        program = _flight({"detect": {"object": "vehicle", "where": where}})
        assert validate(program, manifest, _geofenced(), policy=None).accepted

    def test_detect_search_radius_around_an_area_checks_each_vertex(self) -> None:
        # field spans x 0..30; with a fence out to x 32, a 1 m radius fits, 3 m does not.
        wide = [[-5.0, -5.0], [32.0, -5.0], [32.0, 15.0], [-5.0, 15.0]]
        fits = _flight({"detect": {"object": "vehicle", "where": {"near": "field", "within": 1.0}}})
        assert validate(fits, _drone_manifest(), _geofenced(vertices=wide), policy=None).accepted
        spills = _flight({"detect": {"object": "vehicle", "where": {"near": "field", "within": 3.0}}})
        result = validate(spills, _drone_manifest(), _geofenced(vertices=wide), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "detect")

    def test_move_to_named_location_above_the_ceiling_rejected(self) -> None:
        program = _flight({"move_to": {"location": "tower_top"}})
        result = validate(program, _drone_manifest(), None, policy=None)
        assert "envelope.altitude_exceeded" in _codes_for(result, "move_to")

    def test_move_to_named_location_above_the_envelope_cap_rejected(self) -> None:
        program = _program({"take_off": {"altitude": 20.0}}, {"move_to": {"location": "roof"}}, profile="drone")
        result = validate(program, _drone_manifest(), {"max_altitude": 25.0}, policy=None)
        assert "envelope.altitude_exceeded" in _codes_for(result, "move_to")

    def test_move_to_area_outside_geofence_rejected(self) -> None:
        program = _flight({"move_to": {"location": "field"}})
        result = validate(program, _drone_manifest(), _geofenced(), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "move_to")

    def test_move_to_area_inside_geofence_accepted(self) -> None:
        program = _flight({"move_to": {"location": "field"}})
        wide = [[-5.0, -5.0], [35.0, -5.0], [35.0, 15.0], [-5.0, 15.0]]
        result = validate(program, _drone_manifest(), _geofenced(vertices=wide), policy=None)
        assert result.accepted, result.codes()


def _scan(area: dict[str, Any], altitude: float = 30.0) -> dict[str, Any]:
    return _flight({"scan": {"area": area, "altitude": altitude, "store_as": "survey"}})


class TestScanArea:
    def test_area_that_contains_a_zone_rejected(self) -> None:
        # Every corner is outside the zone, the zone is inside the area.
        area = {"bounding_box": {"min_x": -10.0, "max_x": 10.0, "min_y": -10.0, "max_y": 10.0}}
        result = validate(_scan(area), _drone_manifest(), _zoned(), policy=None)
        assert "envelope.occupancy_zone_intrusion" in _codes_for(result, "scan")

    def test_area_clear_of_the_zone_accepted(self) -> None:
        area = {"bounding_box": {"min_x": 5.0, "max_x": 20.0, "min_y": 5.0, "max_y": 10.0}}
        result = validate(_scan(area), _drone_manifest(), _zoned(), policy=None)
        assert result.accepted, result.codes()

    def test_zone_with_override_is_not_judged(self) -> None:
        area = {"bounding_box": {"min_x": -10.0, "max_x": 10.0, "min_y": -10.0, "max_y": 10.0}}
        result = validate(_scan(area), _drone_manifest(), _zoned(allow_override=True), policy=None)
        assert result.accepted, result.codes()

    def test_polygon_area_crossing_a_zone_rejected(self) -> None:
        strip = [(-10.0, -1.0), (10.0, -1.0), (10.0, 1.0), (-10.0, 1.0)]
        area = {"polygon": [{"x": x, "y": y} for x, y in strip]}
        result = validate(_scan(area), _drone_manifest(), _zoned(), policy=None)
        assert "envelope.occupancy_zone_intrusion" in _codes_for(result, "scan")

    def test_named_region_resolves_through_declared_areas(self) -> None:
        area = {"named_region": "field"}
        result = validate(_scan(area), _drone_manifest(), _geofenced(), policy=None)
        assert "envelope.geofence_violation" in _codes_for(result, "scan")
        result = validate(_scan(area), _drone_manifest(), _zoned(), policy=None)
        assert "envelope.occupancy_zone_intrusion" in _codes_for(result, "scan")

    def test_named_region_that_is_not_a_declared_area_is_not_judged(self) -> None:
        result = validate(_scan({"named_region": "somewhere_else"}), _drone_manifest(), _zoned(), policy=None)
        assert result.accepted, result.codes()

    def test_corner_labels_unchanged(self) -> None:
        area = {"bounding_box": {"min_x": 0.0, "max_x": 100.0, "min_y": 0.0, "max_y": 100.0}}
        result = validate(_scan(area), _drone_manifest(), _geofenced(), policy=None)
        fields = sorted(e.field for e in result.errors if e.code == ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)
        assert fields == [
            "area.bounding_box[max_x,max_y]",
            "area.bounding_box[max_x,min_y]",
            "area.bounding_box[min_x,max_y]",
        ]
