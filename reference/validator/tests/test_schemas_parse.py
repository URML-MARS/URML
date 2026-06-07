"""Smoke tests: every schema model parses the canonical fixtures.

These tests do not run the four-pass validator (capability lookup,
safety-envelope tightening, variable-binding resolution). Those land in the
next milestone. What they confirm today:

  1. The red-mug example in `examples/home/red-mug.urml.yaml` parses against
     URMLProgram without raising.
  2. The TurtleBot 4 manifest fixture parses against CapabilityManifest.
  3. The home-default envelope fixture parses against SafetyEnvelope.
  4. Every primitive arg-model in the registry instantiates from its
     documented minimal valid form.
  5. The Step union rejects a multi-primitive YAML node, and the registry
     covers exactly the twelve primitives RFC-0002 lists.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from urml_validator.schemas.envelope import SafetyEnvelope
from urml_validator.schemas.manifest import CapabilityManifest
from urml_validator.schemas.primitives import PRIMITIVE_MODELS, PRIMITIVE_NAMES
from urml_validator.schemas.program import URMLProgram

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = Path(__file__).parent / "fixtures"
EXAMPLES_ROOT = REPO_ROOT / "examples"


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# End-to-end fixture parses
# ---------------------------------------------------------------------------


def test_red_mug_example_parses() -> None:
    """The canonical home example parses against URMLProgram."""
    path = EXAMPLES_ROOT / "home" / "red-mug.urml.yaml"
    assert path.is_file(), f"fixture missing: {path}"
    program = URMLProgram.model_validate(_load_yaml(path))
    assert program.profiles == ["home"]
    assert program.behavior is not None


def test_turtlebot_manifest_parses() -> None:
    """The TurtleBot 4 manifest fixture parses against CapabilityManifest."""
    manifest = CapabilityManifest.model_validate(
        _load_yaml(FIXTURE_ROOT / "manifests" / "turtlebot4_home.yaml")
    )
    assert manifest.robot_id == "turtlebot4_demo"
    assert manifest.mobility is not None
    assert manifest.manipulation is not None
    assert manifest.perception is not None
    # The red-mug example references location `kitchen` and class `mug`;
    # confirm the manifest declares both.
    assert any(loc.name == "kitchen" for loc in manifest.declared_locations)
    assert "mug" in (manifest.perception.object_vocabulary if manifest.perception else [])


def test_home_envelope_parses() -> None:
    """The default home envelope fixture parses against SafetyEnvelope."""
    envelope = SafetyEnvelope.model_validate(
        _load_yaml(FIXTURE_ROOT / "envelopes" / "home_default.yaml")
    )
    assert envelope.deployment_id == "home_demo"
    assert envelope.max_velocity == 0.4


# ---------------------------------------------------------------------------
# Primitive registry coverage
# ---------------------------------------------------------------------------


def test_primitive_registry_covers_rfc_0002_set() -> None:
    """RFC-0002 names exactly twelve core primitives; the registry must include
    those plus any profile-extension primitives authorized by RFC-0002
    §Profile-extensibility (currently: home-profile `speak` and `listen`).
    """
    core = {
        "move_to",
        "dock",
        "hover",
        "wait",
        "wait_for",
        "grasp",
        "release",
        "detect",
        "scan",
        "measure",
        "capture",
        "report",
    }
    # Profile-extension primitives. New entries here track profile specs.
    home_extensions = {"speak", "listen"}
    drone_extensions = {"take_off", "land", "return_to_home"}
    industrial_extensions = {"pick_from", "place_at", "swap_tool"}  # RFC-0013
    # bimanual: whole-body / two-arm coordination (RFC-0010), available to any
    # manifest declaring two arms; not profile-gated.
    manipulation_extensions = {"bimanual"}
    # call_program: substrate-program invocation (RFC-0015), gated by the
    # manifest `programs:` declaration rather than by profile.
    cross_profile_extensions = {"call_program"}
    # av: plan_path (compute) + follow_trajectory (actuate), the research-grade
    # autonomous-vehicle pair (RFC-0020); gated by the manifest `av` block.
    av_extensions = {"plan_path", "follow_trajectory"}
    # set_output: digital/analog line actuation (RFC-0017), gated by the
    # manifest `outputs.lines` declaration rather than by profile.
    actuation_extensions = {"set_output"}
    expected = (
        core
        | home_extensions
        | drone_extensions
        | industrial_extensions
        | manipulation_extensions
        | cross_profile_extensions
        | av_extensions
        | actuation_extensions
    )
    assert set(PRIMITIVE_NAMES) == expected
    assert set(PRIMITIVE_MODELS.keys()) == expected
    # The RFC-0002 core set must remain a subset of the registry — the
    # twelve are non-negotiable.
    assert core.issubset(set(PRIMITIVE_NAMES))


@pytest.mark.parametrize(
    ("name", "args"),
    [
        ("move_to", {"location": "kitchen"}),
        ("dock", {}),
        ("hover", {"duration": "10s"}),
        ("wait", {"duration": "3s"}),
        ("wait_for", {"condition": {"event": "user_present"}}),
        ("grasp", {"target": "$target_mug"}),
        ("release", {"mode": "hand_to_user"}),
        ("detect", {"object": "mug", "store_as": "target_mug"}),
        (
            "scan",
            {
                "area": {"named_region": "kitchen_counter"},
                "store_as": "kitchen_scan",
            },
        ),
        (
            "measure",
            {"what": "distance", "store_as": "dist"},
        ),
        (
            "capture",
            {"media": "photo", "store_as": "photo_1"},
        ),
        (
            "report",
            {"to": "user", "facts": {"message": "done"}},
        ),
        (
            "pick_from",
            {"source": "pick_bin", "object": "widget_red", "store_as": "w"},
        ),
        (
            "place_at",
            {"target": "kitting_tray_red", "held": "$w"},
        ),
        (
            "swap_tool",
            {"at": "tool_change_station", "to": "gripper_wide"},
        ),
        (
            "call_program",
            {"name": "pick_place_cycle"},
        ),
    ],
)
def test_each_primitive_minimal_valid_form(name: str, args: dict) -> None:
    """Every primitive accepts its documented minimum-valid argument set."""
    model = PRIMITIVE_MODELS[name]
    model.model_validate(args)


# ---------------------------------------------------------------------------
# Step union: exactly one primitive
# ---------------------------------------------------------------------------


def test_step_rejects_multiple_primitives() -> None:
    """A Step with two primitive keys must fail validation."""
    from urml_validator.schemas.composition import Step

    with pytest.raises(ValidationError):
        Step.model_validate(
            {
                "move_to": {"location": "kitchen"},
                "wait": {"duration": "1s"},
            }
        )


def test_step_rejects_no_primitive() -> None:
    """A Step with no primitive set must fail."""
    from urml_validator.schemas.composition import Step

    with pytest.raises(ValidationError):
        Step.model_validate({})


# ---------------------------------------------------------------------------
# Cross-field rules on individual primitives
# ---------------------------------------------------------------------------


def test_move_to_requires_exactly_one_target() -> None:
    """move_to without location or pose, or with both, is rejected."""
    from urml_validator.schemas.primitives import MoveToArgs

    with pytest.raises(ValidationError):
        MoveToArgs.model_validate({})
    with pytest.raises(ValidationError):
        MoveToArgs.model_validate(
            {"location": "kitchen", "pose": {"x": 0.0, "y": 0.0}, "frame": "map"}
        )


def test_move_to_pose_requires_frame() -> None:
    """move_to with a pose but no frame is rejected."""
    from urml_validator.schemas.primitives import MoveToArgs

    with pytest.raises(ValidationError):
        MoveToArgs.model_validate({"pose": {"x": 1.0, "y": 0.0}})


def test_release_place_requires_at() -> None:
    """release(mode: place) requires an `at` argument."""
    from urml_validator.schemas.primitives import ReleaseArgs

    with pytest.raises(ValidationError):
        ReleaseArgs.model_validate({"mode": "place"})
    ReleaseArgs.model_validate({"mode": "place", "at": "user"})


def test_capture_video_requires_duration() -> None:
    """capture(media: video) without duration is rejected; with duration accepted."""
    from urml_validator.schemas.primitives import CaptureArgs

    with pytest.raises(ValidationError):
        CaptureArgs.model_validate({"media": "video", "store_as": "v"})
    CaptureArgs.model_validate({"media": "video", "duration": "5s", "store_as": "v"})
