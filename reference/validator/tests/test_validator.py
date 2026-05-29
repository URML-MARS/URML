"""Validator behavior tests.

Each test loads the canonical fixtures and either confirms that an
intentionally-correct program is accepted, or that an intentionally-broken
program produces the expected stable error code.

The negative-test convention: produce a small dict-shaped program that
isolates a single failure mode. Assert exactly that the matching ErrorCode
appears in the result; do not assert on message text (messages are wording-
level and may be tweaked between releases).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from urml_validator import ErrorCode, validate

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = Path(__file__).parent / "fixtures"
EXAMPLES_ROOT = REPO_ROOT / "examples"


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def turtlebot_manifest() -> dict:
    return _load_yaml(FIXTURE_ROOT / "manifests" / "turtlebot4_home.yaml")


@pytest.fixture
def home_envelope() -> dict:
    return _load_yaml(FIXTURE_ROOT / "envelopes" / "home_default.yaml")


@pytest.fixture
def red_mug_program() -> dict:
    return _load_yaml(EXAMPLES_ROOT / "home" / "red-mug.urml.yaml")


@pytest.fixture
def industrial_cell_manifest() -> dict:
    return _load_yaml(FIXTURE_ROOT / "manifests" / "industrial_cell.yaml")


# ---------------------------------------------------------------------------
# End-to-end: the canonical example is accepted.
# ---------------------------------------------------------------------------


def test_red_mug_is_accepted(
    red_mug_program: dict,
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    result = validate(red_mug_program, turtlebot_manifest, home_envelope, profiles=("home",))
    assert result.accepted, f"red-mug should validate; got: {[e.render() for e in result.errors]}"
    assert result.errors == []


def test_red_mug_accepts_without_envelope(
    red_mug_program: dict,
    turtlebot_manifest: dict,
) -> None:
    """The envelope is optional; the program must still validate."""
    result = validate(red_mug_program, turtlebot_manifest, envelope=None, profiles=("home",))
    assert result.accepted, [e.render() for e in result.errors]


# ---------------------------------------------------------------------------
# Argument pass — pydantic-driven failures surface as `argument.*`.
# ---------------------------------------------------------------------------


def test_argument_missing_required(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"wait": {}},  # `duration` is required
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.ARGUMENT_MISSING_REQUIRED)


def test_argument_unknown_field(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"move_to": {"location": "kitchen", "definitely_not_a_field": True}},
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.ARGUMENT_UNKNOWN_FIELD)


def test_argument_constraint_violation(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    """move_to requires exactly one of location/pose."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"move_to": {}}],  # no location, no pose
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.ARGUMENT_CONSTRAINT)


# ---------------------------------------------------------------------------
# Capability pass.
# ---------------------------------------------------------------------------


def test_missing_mobility_rejects_move_to(home_envelope: dict) -> None:
    bare_manifest = {
        "manifest_version": "0.1",
        "robot_id": "bare_bot",
        "frames": [{"name": "map", "parent": None}],
        "declared_locations": [
            {"name": "anywhere", "pose": {"x": 0, "y": 0}, "frame": "map"}
        ],
    }
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"move_to": {"location": "anywhere"}}],
        },
    }
    result = validate(program, bare_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_MOBILITY)


def test_missing_location(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"move_to": {"location": "the_moon"}}],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_LOCATION)


def test_missing_frame_for_pose(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"move_to": {"pose": {"x": 1, "y": 1}, "frame": "nonexistent"}}],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_FRAME)


def test_missing_station_keeping_rejects_hover(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    no_keep = dict(turtlebot_manifest)
    no_keep["mobility"] = dict(turtlebot_manifest["mobility"])
    no_keep["mobility"]["station_keeping"] = False
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {"type": "sequence", "steps": [{"hover": {"duration": "5s"}}]},
    }
    result = validate(program, no_keep, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_STATION_KEEPING)


def test_unknown_docking_service(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"dock": {"at": "charging_dock", "service": "swap_tool"}}],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_DOCKING_SERVICE)


# ---------------------------------------------------------------------------
# Industrial-profile primitives (RFC-0013): pick_from / place_at / swap_tool
# ---------------------------------------------------------------------------


def _industrial_seq(*steps: dict) -> dict[str, Any]:
    return {
        "profile": "industrial",
        "behavior": {"type": "sequence", "on_error": "abort_and_report",
                     "steps": list(steps)},
    }


def test_pick_from_place_at_swap_tool_accepted(
    industrial_cell_manifest: dict,
) -> None:
    """The canonical RFC-0013 happy path validates against the industrial cell."""
    program = _industrial_seq(
        {"wait_for": {"condition": {"event": "safety_door_closed"}}},
        {"swap_tool": {"at": "tool_change_station", "to": "gripper_wide"}},
        {"pick_from": {"source": "pick_bin", "object": "widget_red",
                       "attributes": {"color": "red"}, "force": "firm",
                       "store_as": "red_widget"}},
        {"place_at": {"target": "kitting_tray_red", "held": "$red_widget"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_pick_from_undeclared_source_rejected(
    industrial_cell_manifest: dict,
) -> None:
    program = _industrial_seq(
        {"pick_from": {"source": "no_such_bin", "object": "widget_red",
                       "store_as": "w"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_LOCATION)


def test_pick_from_undeclared_object_rejected(
    industrial_cell_manifest: dict,
) -> None:
    program = _industrial_seq(
        {"pick_from": {"source": "pick_bin", "object": "widget_purple",
                       "store_as": "w"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_OBJECT_CLASS)


def test_place_at_held_must_resolve_to_an_object(
    industrial_cell_manifest: dict,
) -> None:
    """place_at.held referencing an unbound name is a binding error."""
    program = _industrial_seq(
        {"place_at": {"target": "kitting_tray_red", "held": "$nope"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.BINDING_UNRESOLVED_REFERENCE)


def test_swap_tool_undeclared_station_rejected(
    industrial_cell_manifest: dict,
) -> None:
    program = _industrial_seq(
        {"swap_tool": {"at": "pick_bin", "to": "gripper_wide"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_DOCKING_STATION)


def test_swap_tool_station_without_service_rejected(
    industrial_cell_manifest: dict,
) -> None:
    """A docking station that does not declare `swap_tool` is rejected."""
    industrial_cell_manifest["docking_stations"] = [
        {"name": "park_only", "pose": {"x": 0.0, "y": 0.0, "z": 0.0},
         "frame": "cell", "services": ["park"]}
    ]
    program = _industrial_seq(
        {"swap_tool": {"at": "park_only", "to": "gripper_wide"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_DOCKING_SERVICE)


def test_call_program_declared_accepted(
    industrial_cell_manifest: dict,
) -> None:
    """call_program against a declared program validates (RFC-0015)."""
    program = _industrial_seq(
        {"call_program": {"name": "pick_place_cycle"}},
        {"call_program": {"name": "home_all"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_call_program_undeclared_rejected(
    industrial_cell_manifest: dict,
) -> None:
    """An undeclared program name is rejected at Pass 2 (the actuate gate)."""
    program = _industrial_seq(
        {"call_program": {"name": "nonexistent_program"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_PROGRAM)


def test_call_program_arg_signature_mismatch_rejected(
    industrial_cell_manifest: dict,
) -> None:
    """A passed arg whose type does not match the declared signature is rejected."""
    industrial_cell_manifest["programs"] = [
        {"name": "run_with_speed", "args": [{"name": "speed", "type": "number"}]},
    ]
    program = _industrial_seq(
        {"call_program": {"name": "run_with_speed",
                          "args": {"speed": "fast"}}},  # string, declared number
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_PROGRAM_ARG_MISMATCH)


def test_call_program_undeclared_arg_rejected(
    industrial_cell_manifest: dict,
) -> None:
    """A passed arg the program does not declare is rejected."""
    industrial_cell_manifest["programs"] = [{"name": "no_arg_job"}]
    program = _industrial_seq(
        {"call_program": {"name": "no_arg_job", "args": {"extra": 1}}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_PROGRAM_ARG_MISMATCH)


def test_call_program_value_binding_is_unconsumable(
    industrial_cell_manifest: dict,
) -> None:
    """A stored program_result cannot be fed to a typed consumer like grasp."""
    industrial_cell_manifest["programs"] = [{"name": "probe_job"}]
    program = _industrial_seq(
        {"call_program": {"name": "probe_job", "expect": "value",
                          "store_as": "probe"}},
        {"grasp": {"target": "$probe", "force": "firm"}},
    )
    result = validate(program, industrial_cell_manifest, None,
                      profiles=("industrial",), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.BINDING_TYPE_MISMATCH)


def test_unknown_object_class(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"detect": {"object": "elephant", "store_as": "x"}}],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_OBJECT_CLASS)


def test_unknown_event(turtlebot_manifest: dict, home_envelope: dict) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"wait_for": {"condition": {"event": "spaceship_landed"}}}],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_EVENT)


def test_unknown_output_endpoint(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"report": {"to": "external_log_server", "facts": {"msg": "ok"}}}],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_OUTPUT)


def test_video_capture_against_photo_only_camera(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    photo_only = _deep_copy(turtlebot_manifest)
    for cam in photo_only["perception"]["cameras"]:
        cam["supports_video"] = False
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"capture": {"media": "video", "duration": "3s", "store_as": "v"}}],
        },
    }
    result = validate(program, photo_only, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_VIDEO_UNSUPPORTED)


def test_capture_target_with_fixed_camera(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"detect": {"object": "mug", "store_as": "m"}},
                {"capture": {"media": "photo", "target": "$m", "store_as": "p"}},
            ],
        },
    }
    # The TurtleBot manifest declares a fixed camera, so target+capture is rejected.
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_FIXED_CAMERA_TARGET)


# ---------------------------------------------------------------------------
# Envelope pass.
# ---------------------------------------------------------------------------


def test_velocity_exceeded(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"move_to": {"location": "kitchen", "speed": 2.0}}],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_VELOCITY_EXCEEDED)


def test_altitude_exceeded() -> None:
    drone_manifest = {
        "manifest_version": "0.1",
        "robot_id": "test_drone",
        "frames": [{"name": "world", "parent": None}],
        "mobility": {
            "drive_type": "multirotor",
            "max_velocity": 12.0,
            "station_keeping": True,
            "service_ceiling": 120.0,
        },
        "perception": {"cameras": [], "sensors": [], "object_vocabulary": []},
    }
    envelope = {"envelope_version": "0.1", "max_altitude": 50.0}
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"move_to": {"pose": {"x": 0, "y": 0, "z": 100}, "frame": "world"}},
            ],
        },
    }
    result = validate(program, drone_manifest, envelope)
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_ALTITUDE_EXCEEDED)


def test_grasp_force_exceeded(turtlebot_manifest: dict) -> None:
    stringent = {"envelope_version": "0.1", "max_grip_force_n": 1.0}
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"detect": {"object": "mug", "store_as": "m"}},
                {"grasp": {"target": "$m", "force": "firm"}},  # firm -> 8 N, cap 1 N
            ],
        },
    }
    result = validate(program, turtlebot_manifest, stringent)
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_FORCE_EXCEEDED)


# ---------------------------------------------------------------------------
# Binding pass.
# ---------------------------------------------------------------------------


def test_unresolved_reference(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"grasp": {"target": "$never_bound"}}],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.BINDING_UNRESOLVED_REFERENCE)


def test_duplicate_store_as(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"detect": {"object": "mug", "store_as": "m"}},
                {"detect": {"object": "cup", "store_as": "m"}},  # duplicate!
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.BINDING_DUPLICATE_STORE_AS)


def test_forward_reference_rejected(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    """Reference used before its binding step is rejected."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"grasp": {"target": "$mug"}},  # used before bound below
                {"detect": {"object": "mug", "store_as": "mug"}},
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.BINDING_UNRESOLVED_REFERENCE)


# ---------------------------------------------------------------------------
# Pass 4: cross-primitive variable type checking
# ---------------------------------------------------------------------------


def test_grasp_target_must_be_an_object(turtlebot_manifest: dict, home_envelope: dict) -> None:
    """A measure binding (type `measurement`) cannot satisfy grasp.target (`object`)."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"measure": {"what": "speech", "sensor": "mic_array", "store_as": "reading"}},
                {"grasp": {"target": "$reading"}},
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.BINDING_TYPE_MISMATCH)


def test_move_to_carrying_must_be_an_object(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    """A capture binding (type `media_handle`) cannot satisfy move_to.carrying (`object`)."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"capture": {"media": "photo", "store_as": "snapshot"}},
                {"move_to": {"location": "kitchen", "carrying": "$snapshot"}},
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.BINDING_TYPE_MISMATCH)


def test_object_binding_satisfies_grasp_target(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    """Sanity: a detect binding (type `object`) DOES satisfy grasp.target."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"detect": {"object": "mug", "store_as": "target"}},
                {"grasp": {"target": "$target"}},
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    # Sanity test for the *opposite* of the rejection above: a binding
    # of the right type must NOT trigger a type-mismatch error. We don't
    # assert result.accepted overall because envelope/policy passes may
    # have unrelated complaints — we only check the specific code.
    assert not result.has(ErrorCode.BINDING_TYPE_MISMATCH)


def test_report_attachments_accepts_any_binding(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    """report.attachments is intentionally loose — any binding type is allowed."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"measure": {"what": "speech", "sensor": "mic_array", "store_as": "r"}},
                {
                    "report": {
                        "to": "user",
                        "facts": {"message": "done"},
                        "attachments": ["$r"],
                        "status": "success",
                    }
                },
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.has(ErrorCode.BINDING_TYPE_MISMATCH)


# ---------------------------------------------------------------------------
# Pass 3: geofence polygon containment
# ---------------------------------------------------------------------------


def _drone_civilian_manifest() -> dict:
    return _load_yaml(FIXTURE_ROOT / "manifests" / "drone_civilian.yaml")


def _drone_geofence_envelope() -> dict:
    return _load_yaml(FIXTURE_ROOT / "envelopes" / "drone_with_geofence.yaml")


def test_move_to_pose_outside_geofence_rejected() -> None:
    """A move_to pose outside the only declared geofence triggers the violation."""
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                {"move_to": {"pose": {"x": 50.0, "y": 50.0, "z": 30.0}, "frame": "agl"}},
                {"land": {}},
            ],
        },
    }
    result = validate(
        program,
        _drone_civilian_manifest(),
        _drone_geofence_envelope(),
        profiles=("drone",),
        policy="DEFAULT",
    )
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)


def test_move_to_pose_inside_geofence_accepted() -> None:
    """A move_to pose inside the declared geofence does NOT trigger the violation."""
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                {"move_to": {"pose": {"x": 5.0, "y": 5.0, "z": 30.0}, "frame": "agl"}},
                {"land": {}},
            ],
        },
    }
    result = validate(
        program,
        _drone_civilian_manifest(),
        _drone_geofence_envelope(),
        profiles=("drone",),
        policy="DEFAULT",
    )
    assert not result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)


def test_geofence_check_is_noop_when_envelope_declares_none(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    """Programs targeting any pose are accepted when the envelope declares no geofences."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"move_to": {"pose": {"x": 9999.0, "y": 9999.0}, "frame": "map"}},
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    # The envelope declares no geofences, so this check abstains entirely.
    assert not result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)


def test_move_to_pose_inside_footprint_but_above_altitude_band_rejected() -> None:
    """A pose inside the polygon footprint but above max_altitude is rejected
    with an altitude-band failure (distinct from a footprint failure)."""
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                # Inside the [-5,-5]..[15,15] footprint, but above the band.
                {"move_to": {"pose": {"x": 5.0, "y": 5.0, "z": 150.0}, "frame": "agl"}},
                {"land": {}},
            ],
        },
    }
    envelope = _drone_geofence_envelope()
    # Attach an altitude band to the existing geofence so this test is
    # self-contained — the on-disk fixture only declares the footprint.
    envelope["geofences"][0]["max_altitude"] = 100.0
    result = validate(
        program,
        _drone_civilian_manifest(),
        envelope,
        profiles=("drone",),
        policy="DEFAULT",
    )
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)
    # The geofence error's message should mention "altitude band" so a
    # human (or LLM) revising the program knows it's the altitude that's
    # wrong, not the footprint.
    geofence_errs = [
        e for e in result.errors if e.code == ErrorCode.ENVELOPE_GEOFENCE_VIOLATION
    ]
    assert any("altitude band" in e.message for e in geofence_errs)


def test_move_to_pose_inside_footprint_with_z_in_band_accepted() -> None:
    """When both footprint and altitude band are satisfied, no violation fires."""
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                {"move_to": {"pose": {"x": 5.0, "y": 5.0, "z": 30.0}, "frame": "agl"}},
                {"land": {}},
            ],
        },
    }
    envelope = _drone_geofence_envelope()
    envelope["geofences"][0]["min_altitude"] = 0.0
    envelope["geofences"][0]["max_altitude"] = 100.0
    result = validate(
        program,
        _drone_civilian_manifest(),
        envelope,
        profiles=("drone",),
        policy="DEFAULT",
    )
    assert not result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)


# ---------------------------------------------------------------------------
# Pass 3: people-occupancy zones (denylist)
# ---------------------------------------------------------------------------


def _drone_envelope_with_occupancy_zone(allow_override: bool = False) -> dict:
    """Drone envelope with a single people-occupancy zone near origin."""
    return {
        "envelope_version": "0.1",
        "deployment_id": "drone_occupied_site",
        "description": "Drone envelope with a declared people-occupancy zone.",
        "max_velocity": 10.0,
        "max_altitude": 120.0,
        "people_occupancy_zones": [
            {
                "name": "spectator_area",
                "frame": "agl",
                "vertices": [
                    [-3.0, -3.0],
                    [3.0, -3.0],
                    [3.0, 3.0],
                    [-3.0, 3.0],
                ],
                "allow_override": allow_override,
            }
        ],
    }


def test_move_to_pose_inside_occupancy_zone_rejected() -> None:
    """A pose inside a declared people-occupancy zone is rejected."""
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                {"move_to": {"pose": {"x": 0.0, "y": 0.0, "z": 30.0}, "frame": "agl"}},
                {"land": {}},
            ],
        },
    }
    result = validate(
        program,
        _drone_civilian_manifest(),
        _drone_envelope_with_occupancy_zone(),
        profiles=("drone",),
        policy="DEFAULT",
    )
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_OCCUPANCY_ZONE_INTRUSION)


def test_occupancy_zone_with_allow_override_accepts_intrusion() -> None:
    """A zone marked allow_override:true is a deployer-acknowledged risk; abstain."""
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                {"move_to": {"pose": {"x": 0.0, "y": 0.0, "z": 30.0}, "frame": "agl"}},
                {"land": {}},
            ],
        },
    }
    result = validate(
        program,
        _drone_civilian_manifest(),
        _drone_envelope_with_occupancy_zone(allow_override=True),
        profiles=("drone",),
        policy="DEFAULT",
    )
    assert not result.has(ErrorCode.ENVELOPE_OCCUPANCY_ZONE_INTRUSION)


def test_occupancy_zone_no_intrusion_when_target_outside() -> None:
    """A target outside every declared occupancy zone does not trigger the check."""
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                # Far outside the (-3,-3)..(3,3) occupancy zone.
                {"move_to": {"pose": {"x": 10.0, "y": 5.0, "z": 30.0}, "frame": "agl"}},
                {"land": {}},
            ],
        },
    }
    result = validate(
        program,
        _drone_civilian_manifest(),
        _drone_envelope_with_occupancy_zone(),
        profiles=("drone",),
        policy="DEFAULT",
    )
    assert not result.has(ErrorCode.ENVELOPE_OCCUPANCY_ZONE_INTRUSION)


def test_occupancy_zone_check_is_noop_when_envelope_declares_none(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    """No occupancy zones declared → check abstains entirely."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"move_to": {"pose": {"x": 0.0, "y": 0.0}, "frame": "map"}},
            ],
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.has(ErrorCode.ENVELOPE_OCCUPANCY_ZONE_INTRUSION)


def test_scan_bounding_box_partially_outside_geofence_rejected() -> None:
    """A scan whose bounding-box corners straddle the geofence is rejected."""
    program: dict[str, Any] = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                {
                    "scan": {
                        "area": {
                            "bounding_box": {
                                "min_x": 0.0,
                                "max_x": 100.0,
                                "min_y": 0.0,
                                "max_y": 100.0,
                            },
                        },
                        "altitude": 30.0,
                        "store_as": "survey",
                    }
                },
                {"land": {}},
            ],
        },
    }
    result = validate(
        program,
        _drone_civilian_manifest(),
        _drone_geofence_envelope(),
        profiles=("drone",),
        policy="DEFAULT",
    )
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_GEOFENCE_VIOLATION)


# ---------------------------------------------------------------------------
# Composition coverage: the walker visits steps inside nested behaviors.
# ---------------------------------------------------------------------------


def test_walker_visits_branch_and_retry(
    turtlebot_manifest: dict, home_envelope: dict
) -> None:
    """A capability error inside Retry+Branch must surface."""
    program: dict[str, Any] = {
        "profile": "home",
        "behavior": {
            "type": "retry",
            "max_attempts": 3,
            "behavior": {
                "type": "sequence",
                "steps": [
                    {"detect": {"object": "mug", "store_as": "m"}},
                    {
                        "type": "branch",
                        "condition": "found",
                        "if_true": {"grasp": {"target": "$m"}},
                        "if_false": {"move_to": {"location": "the_moon"}},  # bad
                    },
                ],
            },
        },
    }
    result = validate(program, turtlebot_manifest, home_envelope)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_LOCATION)


# ---------------------------------------------------------------------------
# Helper.
# ---------------------------------------------------------------------------


def _deep_copy(d: dict) -> dict:
    """Tiny deep-copy helper so tests can mutate manifest fixtures locally."""
    import copy

    return copy.deepcopy(d)
