"""Unit tests for RFC-0616 declared-intent for opaque programs.

A `call_program` body is opaque and a general program cannot be statically
verified (the halting problem). RFC-0616 lets a `Program` opt in to a
`declared_intent`: a best-effort, attested list of the primitives it exercises,
validated as a *claim* against the manifest. Surfaced by the bluesky maintainers
(RFC-0590), who noted a plan can run arbitrary code so any upfront check must be
best-effort and made-correct-by-hand.

Two layers: the claim is checked (unknown primitive, unsupported capability,
over-claimed force) and an `asserted` attestation raises a best-effort advisory
warning so a reader knows the check covered the declaration, not the body.
"""

from __future__ import annotations

from typing import Any

from urml_validator import ErrorCode, validate


def _manifest(declared_intent: dict[str, Any], **blocks: Any) -> dict[str, Any]:
    m: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "di_test",
        "frames": [{"name": "w", "parent": None}],
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "w"}
        ],
        "programs": [{"name": "opaque_routine", "declared_intent": declared_intent}],
    }
    m.update(blocks)
    return m


_MOBILITY = {"drive_type": "differential", "max_velocity": 1.0}
_MANIP = {
    "arm_count": 1,
    "grippers": [{"name": "g", "kind": "servo_electric", "force_min_n": 1.0, "force_max_n": 50.0}],
}


def _call_program() -> dict[str, Any]:
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"call_program": {"name": "opaque_routine"}}],
        },
    }


def _codes(result) -> list[str]:
    return [e.code.value for e in result.errors]


def _warn_codes(result) -> list[str]:
    return [w.code.value for w in result.warnings]


def test_asserted_intent_accepted_with_advisory() -> None:
    m = _manifest(
        {"primitives": ["move_to", "grasp"], "attestation": "asserted"},
        mobility=_MOBILITY,
        manipulation=_MANIP,
    )
    r = validate(_call_program(), m, policy=None)
    assert r.accepted, _codes(r)
    assert ErrorCode.CAPABILITY_DECLARED_INTENT_ASSERTED.value in _warn_codes(r)


def test_verified_intent_no_advisory() -> None:
    m = _manifest(
        {"primitives": ["move_to"], "attestation": "verified"},
        mobility=_MOBILITY,
    )
    r = validate(_call_program(), m, policy=None)
    assert r.accepted, _codes(r)
    assert ErrorCode.CAPABILITY_DECLARED_INTENT_ASSERTED.value not in _warn_codes(r)


def test_unsupported_capability_rejected() -> None:
    m = _manifest({"primitives": ["grasp"]}, mobility=_MOBILITY)  # no manipulation
    r = validate(_call_program(), m, policy=None)
    assert not r.accepted
    assert ErrorCode.CAPABILITY_DECLARED_INTENT_UNSUPPORTED.value in _codes(r)


def test_unknown_primitive_rejected() -> None:
    m = _manifest({"primitives": ["teleport"]})
    r = validate(_call_program(), m, policy=None)
    assert not r.accepted
    assert ErrorCode.CAPABILITY_DECLARED_INTENT_PRIMITIVE_UNKNOWN.value in _codes(r)


def test_force_over_claim_rejected() -> None:
    m = _manifest({"primitives": ["grasp"], "max_force_n": 200.0}, manipulation=_MANIP)
    r = validate(_call_program(), m, policy=None)
    assert not r.accepted
    assert ErrorCode.CAPABILITY_DECLARED_INTENT_UNSUPPORTED.value in _codes(r)


def test_force_within_gripper_ok() -> None:
    m = _manifest(
        {"primitives": ["grasp"], "max_force_n": 30.0, "attestation": "verified"},
        manipulation=_MANIP,
    )
    r = validate(_call_program(), m, policy=None)
    assert r.accepted, _codes(r)


def test_no_declared_intent_unaffected() -> None:
    # A program without declared_intent is unchanged (additive).
    m: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "di_test",
        "frames": [{"name": "w", "parent": None}],
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "w"}
        ],
        "programs": [{"name": "opaque_routine"}],
    }
    r = validate(_call_program(), m, policy=None)
    assert r.accepted, _codes(r)
    assert ErrorCode.CAPABILITY_DECLARED_INTENT_ASSERTED.value not in _warn_codes(r)
