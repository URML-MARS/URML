"""RFC-0383: learned-policy training-envelope coherence.

A deployment must stay inside the envelope a learned controller was trained
under. The validator checks the admissible ceiling (strictest of mobility and
the safety envelope) against the trained command/payload ranges, and the
declared terrain against the trained terrain classes. Severity follows
`enforcement`. Pass 5 disabled (`policy=None`) to isolate Pass 2/3.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest
from pydantic import ValidationError as PydErr

from urml_validator import ErrorCode, validate
from urml_validator.schemas.manifest import CommandRange

PROGRAM: dict[str, Any] = {
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [{"wait": {"duration": "1s"}}]},
}

BASE: dict[str, Any] = {
    "manifest_version": "0.1",
    "robot_id": "policy_bot",
    "mobility": {"drive_type": "differential", "max_velocity": 1.0, "max_payload": 5.0, "station_keeping": False},
    "learned_policy": {
        "policy_ref": "isaac-lab://demo-v1",
        "command_ranges": [{"quantity": "linear_velocity_x", "min": -0.5, "max": 1.0, "unit": "m_per_s"}],
        "terrain_classes": ["rigid", "deformable"],
        "payload_range": {"min": 0.0, "max": 5.0, "unit": "kg"},
        "enforcement": "reject",
    },
}


def _m(**overrides: Any) -> dict[str, Any]:
    m = copy.deepcopy(BASE)
    for k, v in overrides.items():
        m[k] = v
    return m


def _codes(result: Any) -> list[str]:
    return [e.code_str for e in result.errors]


def _warn_codes(result: Any) -> list[str]:
    return [w.code_str for w in result.warnings]


def test_within_training_envelope_accepted() -> None:
    result = validate(PROGRAM, _m(), {}, policy=None)
    assert result.accepted, _codes(result)


def test_velocity_ceiling_exceeds_training_rejected() -> None:
    mob = {"drive_type": "differential", "max_velocity": 2.0, "max_payload": 5.0, "station_keeping": False}
    result = validate(PROGRAM, _m(mobility=mob), {}, policy=None)
    assert not result.accepted
    assert ErrorCode.CAPABILITY_LEARNED_POLICY_EXCEEDS_TRAINING.value in _codes(result)


def test_envelope_tightening_keeps_within_training() -> None:
    """A higher mechanical max is fine if the envelope caps it below the trained max."""
    mob = {"drive_type": "differential", "max_velocity": 2.0, "max_payload": 5.0, "station_keeping": False}
    result = validate(PROGRAM, _m(mobility=mob), {"max_velocity": 0.8}, policy=None)
    assert result.accepted, _codes(result)


def test_enforcement_warn_does_not_reject() -> None:
    m = _m(mobility={"drive_type": "differential", "max_velocity": 2.0, "station_keeping": False})
    m["learned_policy"]["enforcement"] = "warn"
    result = validate(PROGRAM, m, {}, policy=None)
    assert result.accepted
    assert ErrorCode.CAPABILITY_LEARNED_POLICY_EXCEEDS_TRAINING.value in _warn_codes(result)


def test_terrain_mismatch_rejected() -> None:
    m = _m()
    m["validation"] = {"terrain_fidelity": "granular"}  # not in [rigid, deformable]
    result = validate(PROGRAM, m, {}, policy=None)
    assert not result.accepted
    assert ErrorCode.CAPABILITY_LEARNED_POLICY_TERRAIN_MISMATCH.value in _codes(result)


def test_terrain_within_trained_accepted() -> None:
    m = _m()
    m["validation"] = {"terrain_fidelity": "deformable"}
    result = validate(PROGRAM, m, {}, policy=None)
    assert result.accepted, _codes(result)


def test_payload_ceiling_exceeds_training_rejected() -> None:
    mob = {"drive_type": "differential", "max_velocity": 1.0, "max_payload": 10.0, "station_keeping": False}
    result = validate(PROGRAM, _m(mobility=mob), {}, policy=None)
    assert not result.accepted
    assert ErrorCode.CAPABILITY_LEARNED_POLICY_EXCEEDS_TRAINING.value in _codes(result)


def test_no_learned_policy_unaffected() -> None:
    m = _m()
    del m["learned_policy"]
    result = validate(PROGRAM, m, {}, policy=None)
    assert result.accepted, _codes(result)


def test_command_range_max_below_min_rejected_at_parse() -> None:
    with pytest.raises(PydErr):
        CommandRange.model_validate({"quantity": "yaw_rate", "min": 1.0, "max": -1.0, "unit": "rad_per_s"})
