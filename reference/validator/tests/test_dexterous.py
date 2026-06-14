"""Unit tests for RFC-0586 dexterous (multi-fingered) hand declaration.

A `Gripper` may declare `kind: dexterous` with a `dexterity` block (dof,
finger_count, supported grasp_types). The `grasp` primitive gains an optional
`grasp_type`; when set, the addressed gripper must be dexterous and must
declare that strategy. Surfaced by the LEAP Hand / Shadow Robot engagements
(Move #27): a multi-DoF hand could not be expressed by the single-DoF gripper
model.

Two layers: schema (dexterity present iff kind is dexterous) and validator
(grasp_type requires a dexterous hand that declares the strategy). The fields
are additive: grasp_type defaults None, so pre-RFC-0586 programs are
unaffected.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import ErrorCode, validate
from urml_validator.schemas.manifest import Dexterity, Gripper


# ---------------------------------------------------------------------------
# Schema: dexterity present iff kind is dexterous
# ---------------------------------------------------------------------------


def test_dexterous_gripper_with_dexterity_ok() -> None:
    g = Gripper(
        name="leap",
        kind="dexterous",
        force_min_n=0.5,
        force_max_n=20.0,
        dexterity=Dexterity(dof=16, finger_count=4, grasp_types=["power", "precision", "pinch"]),
    )
    assert g.dexterity is not None
    assert "precision" in g.dexterity.grasp_types


def test_dexterous_without_dexterity_rejected() -> None:
    with pytest.raises(PydanticValidationError):
        Gripper(name="bad", kind="dexterous", force_min_n=0.5, force_max_n=20.0)


def test_non_dexterous_with_dexterity_rejected() -> None:
    with pytest.raises(PydanticValidationError):
        Gripper(
            name="bad",
            kind="servo_electric",
            force_min_n=1.0,
            force_max_n=100.0,
            dexterity=Dexterity(dof=16, finger_count=4, grasp_types=["power"]),
        )


def test_dexterity_requires_at_least_one_grasp_type() -> None:
    with pytest.raises(PydanticValidationError):
        Dexterity(dof=16, finger_count=4, grasp_types=[])


# ---------------------------------------------------------------------------
# Validator: grasp_type gating
# ---------------------------------------------------------------------------


def _manifest(grippers: list[dict[str, Any]], *, arms: list[dict[str, str]] | None = None) -> dict[str, Any]:
    manip: dict[str, Any] = {"arm_count": len(arms) if arms else 1, "grippers": grippers}
    if arms is not None:
        manip["arms"] = arms
    return {
        "manifest_version": "0.1",
        "robot_id": "dex_test",
        "frames": [{"name": "cell", "parent": None}],
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "cell"}
        ],
        "manipulation": manip,
        "perception": {
            "cameras": [
                {
                    "name": "wrist_rgb",
                    "movable": True,
                    "supports_photo": True,
                    "supports_video": False,
                    "supports_stream": False,
                    "max_resolution": "1080p",
                }
            ],
            "sensors": [],
            "object_vocabulary": ["peg"],
        },
    }


_DEX_GRIPPER = {
    "name": "leap_hand",
    "kind": "dexterous",
    "force_min_n": 0.5,
    "force_max_n": 20.0,
    "accepted_classes": ["peg"],
    "dexterity": {"dof": 16, "finger_count": 4, "grasp_types": ["power", "precision", "pinch"]},
}
_PLAIN_GRIPPER = {
    "name": "two_finger",
    "kind": "servo_electric",
    "force_min_n": 1.0,
    "force_max_n": 100.0,
    "accepted_classes": ["peg"],
}


def _grasp_program(grasp: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"detect": {"object": "peg", "store_as": "the_peg"}},
                {"grasp": {"target": "$the_peg", **grasp}},
            ],
        },
    }


def test_grasp_type_on_dexterous_accepted() -> None:
    result = validate(
        _grasp_program({"force": "gentle", "grasp_type": "precision"}),
        _manifest([_DEX_GRIPPER]),
        policy=None,
    )
    assert result.accepted, [e.code for e in result.errors]


def test_dexterous_grasp_without_type_accepted() -> None:
    # Backward compatibility: a dexterous hand still grasps with no grasp_type.
    result = validate(
        _grasp_program({"force": "gentle"}), _manifest([_DEX_GRIPPER]), policy=None
    )
    assert result.accepted, [e.code for e in result.errors]


def test_grasp_type_on_non_dexterous_rejected() -> None:
    result = validate(
        _grasp_program({"force": "firm", "grasp_type": "precision"}),
        _manifest([_PLAIN_GRIPPER]),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.CAPABILITY_GRASP_TYPE_REQUIRES_DEXTEROUS.value in [
        e.code for e in result.errors
    ]


def test_grasp_type_not_declared_rejected() -> None:
    result = validate(
        _grasp_program({"force": "gentle", "grasp_type": "hook"}),
        _manifest([_DEX_GRIPPER]),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.CAPABILITY_GRASP_TYPE_NOT_DECLARED.value in [
        e.code for e in result.errors
    ]


def test_grasp_type_resolves_to_addressed_arm_gripper() -> None:
    # Two arms: `left` holds the dexterous hand, `right` a plain gripper.
    manifest = _manifest(
        [_DEX_GRIPPER, _PLAIN_GRIPPER],
        arms=[
            {"name": "left", "gripper_ref": "leap_hand"},
            {"name": "right", "gripper_ref": "two_finger"},
        ],
    )
    # grasp_type on the dexterous left arm: accepted.
    ok = validate(
        _grasp_program({"force": "gentle", "grasp_type": "precision", "arm": "left"}),
        manifest,
        policy=None,
    )
    assert ok.accepted, [e.code for e in ok.errors]
    # grasp_type on the non-dexterous right arm: rejected (resolves to that arm's gripper).
    bad = validate(
        _grasp_program({"force": "gentle", "grasp_type": "precision", "arm": "right"}),
        manifest,
        policy=None,
    )
    assert not bad.accepted
    assert ErrorCode.CAPABILITY_GRASP_TYPE_REQUIRES_DEXTEROUS.value in [
        e.code for e in bad.errors
    ]
