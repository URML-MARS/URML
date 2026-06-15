"""RFC-0617: multiple named, per-domain learned policies.

A multi-skill robot runs more than one learned controller (a locomotion policy
and a manipulation policy, say). RFC-0383's single `learned_policy` cannot model
that. RFC-0617 adds `learned_policies`: a list of named policies, each carrying a
`governs` domain and validated independently by the RFC-0383 logic, scoped by its
own `command_ranges`. Surfaced by the RL-framework engagements (rl_games, rsl_rl,
legged_gym; Move #29). Pass 5 disabled (`policy=None`) to isolate Pass 2/3.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
from pydantic import ValidationError as PydErr

from urml_validator import ErrorCode, validate
from urml_validator.schemas.manifest import CapabilityManifest

PROGRAM: dict[str, Any] = {
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [{"wait": {"duration": "1s"}}]},
}

BASE: dict[str, Any] = {
    "manifest_version": "0.1",
    "robot_id": "multiskill_bot",
    "mobility": {"drive_type": "quadruped", "max_velocity": 1.0, "max_payload": 5.0, "station_keeping": False},
    "manipulation": {
        "arm_count": 1,
        "grippers": [{"name": "g", "kind": "servo_electric", "force_min_n": 1.0, "force_max_n": 50.0}],
    },
    "learned_policies": [
        {
            "name": "locomotion",
            "governs": "locomotion",
            "policy_ref": "registry://loco-v3",
            "command_ranges": [{"quantity": "linear_velocity_x", "min": -1.0, "max": 1.5, "unit": "m_per_s"}],
            "enforcement": "reject",
        },
        {
            "name": "grasping",
            "governs": "manipulation",
            "policy_ref": "registry://grasp-v2",
            "payload_range": {"min": 0.0, "max": 5.0, "unit": "kg"},
            "enforcement": "reject",
        },
    ],
}


def _m(**overrides: Any) -> dict[str, Any]:
    m = copy.deepcopy(BASE)
    for k, v in overrides.items():
        m[k] = v
    return m


def _codes(result: Any) -> list[str]:
    return [e.code_str for e in result.errors]


def test_two_named_policies_within_accepted() -> None:
    result = validate(PROGRAM, _m(), {}, policy=None)
    assert result.accepted, _codes(result)


def test_one_policy_velocity_exceeds_rejected() -> None:
    # Raise mobility above the locomotion policy's trained max; the grasping
    # policy (no velocity range) is untouched, proving per-policy scoping.
    mob = {"drive_type": "quadruped", "max_velocity": 2.5, "max_payload": 5.0, "station_keeping": False}
    result = validate(PROGRAM, _m(mobility=mob), {}, policy=None)
    assert not result.accepted
    assert ErrorCode.CAPABILITY_LEARNED_POLICY_EXCEEDS_TRAINING.value in _codes(result)


def test_manipulation_policy_payload_exceeds_rejected() -> None:
    mob = {"drive_type": "quadruped", "max_velocity": 1.0, "max_payload": 9.0, "station_keeping": False}
    result = validate(PROGRAM, _m(mobility=mob), {}, policy=None)
    assert not result.accepted
    assert ErrorCode.CAPABILITY_LEARNED_POLICY_EXCEEDS_TRAINING.value in _codes(result)


def test_governs_without_capability_rejected() -> None:
    # A manipulation-governing policy on a manifest with no manipulation block.
    m = _m(manipulation=None, learned_policies=[{"name": "hand", "governs": "manipulation", "enforcement": "reject"}])
    m.pop("manipulation")
    result = validate(PROGRAM, m, {}, policy=None)
    assert not result.accepted
    assert ErrorCode.CAPABILITY_LEARNED_POLICY_GOVERNS_UNSUPPORTED.value in _codes(result)


def test_per_policy_enforcement_warn_does_not_reject() -> None:
    # The locomotion policy is over its trained max but declared warn-only.
    mob = {"drive_type": "quadruped", "max_velocity": 2.5, "max_payload": 5.0, "station_keeping": False}
    pols = copy.deepcopy(BASE["learned_policies"])
    pols[0]["enforcement"] = "warn"
    result = validate(PROGRAM, _m(mobility=mob, learned_policies=pols), {}, policy=None)
    assert result.accepted, _codes(result)


def test_duplicate_policy_names_rejected() -> None:
    with pytest.raises(PydErr):
        CapabilityManifest.model_validate(_m(learned_policies=[{"name": "x"}, {"name": "x"}]))


def test_unnamed_list_entry_rejected() -> None:
    with pytest.raises(PydErr):
        CapabilityManifest.model_validate(_m(learned_policies=[{"governs": "locomotion"}]))


def test_singular_learned_policy_still_works() -> None:
    # RFC-0383 back-compat: the single top-level block is unchanged and unnamed.
    m = {
        "manifest_version": "0.1",
        "robot_id": "legacy",
        "mobility": {"drive_type": "differential", "max_velocity": 2.0, "station_keeping": False},
        "learned_policy": {
            "command_ranges": [{"quantity": "linear_velocity_x", "min": 0.0, "max": 1.0, "unit": "m_per_s"}],
            "enforcement": "reject",
        },
    }
    result = validate(PROGRAM, m, {}, policy=None)
    assert not result.accepted
    assert ErrorCode.CAPABILITY_LEARNED_POLICY_EXCEEDS_TRAINING.value in _codes(result)
