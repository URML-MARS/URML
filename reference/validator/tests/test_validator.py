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
