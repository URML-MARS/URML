"""RFC-0006 — Pass-2 connectivity capability checks.

Negative-test convention (see test_validator.py): isolate one failure mode,
assert the stable ErrorCode is present; do not assert on message wording.

Pass 5 is disabled (`policy=None`) so these tests isolate Pass 2/3 behavior.
"""

from __future__ import annotations

from typing import Any

from urml_validator import ErrorCode, validate

# A minimal, capability-free program. `wait` needs no manifest capability, so
# the only errors a test can see come from the connectivity/link-loss checks.
PROGRAM: dict[str, Any] = {
    "profile": "drone",
    "behavior": {"type": "sequence", "steps": [{"wait": {"duration": "1s"}}]},
}


def _drone_manifest(*, connectivity: dict | None = None) -> dict[str, Any]:
    m: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "test_drone",
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "agl"}
        ],
        "frames": [{"name": "agl", "parent": None}],
        "mobility": {
            "drive_type": "multirotor",
            "max_velocity": 15.0,
            "station_keeping": True,
            "service_ceiling": 120.0,
        },
    }
    if connectivity is not None:
        m["connectivity"] = connectivity
    return m


def test_link_loss_rule_without_connectivity_block_rejected() -> None:
    """Envelope governs command_link, manifest declares no connectivity at all."""
    envelope = {"link_loss_policy": [{"role": "command_link", "action": "return_to_home"}]}
    result = validate(PROGRAM, _drone_manifest(), envelope, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_MISSING_LINK_ROLE)


def test_no_link_loss_rules_is_noop() -> None:
    """Connectivity is opt-in: no rules, no connectivity block, no errors."""
    result = validate(PROGRAM, _drone_manifest(), {"link_loss_policy": []}, policy=None)
    assert result.accepted, [e.render() for e in result.errors]
    assert not result.has(ErrorCode.CAPABILITY_MISSING_LINK_ROLE)


def test_missing_connectivity_deduped_by_role() -> None:
    """Two rules on the same missing role produce a single Pass-2 error."""
    envelope = {
        "link_loss_policy": [
            {"role": "command_link", "action": "return_to_home"},
            {"role": "command_link", "action": "hover"},
        ]
    }
    result = validate(PROGRAM, _drone_manifest(), envelope, policy=None)
    missing = [c for c in result.codes() if c == ErrorCode.CAPABILITY_MISSING_LINK_ROLE]
    assert len(missing) == 1, result.codes()


def test_connectivity_present_but_role_missing_is_pass3_not_pass2() -> None:
    """If connectivity exists but omits the role, Pass 2 stays silent.

    The narrower 'connectivity present, this role missing' case is owned by
    Pass 3's `envelope.link_loss_undeclared_role`, by construction — so a
    single root cause never double-reports.
    """
    connectivity = {"links": [{"role": "telemetry_link"}]}
    envelope = {"link_loss_policy": [{"role": "command_link", "action": "halt_and_report"}]}
    result = validate(PROGRAM, _drone_manifest(connectivity=connectivity), envelope, policy=None)
    assert not result.accepted
    assert not result.has(ErrorCode.CAPABILITY_MISSING_LINK_ROLE)
    assert result.has(ErrorCode.ENVELOPE_LINK_LOSS_UNDECLARED_ROLE)


def test_legacy_scalar_link_loss_policy_is_argument_error() -> None:
    """The breaking change is detected loudly at Pass 1, not silently dropped."""
    result = validate(
        PROGRAM, _drone_manifest(), {"link_loss_policy": "return_to_home"}, policy=None
    )
    assert not result.accepted
    assert result.has(ErrorCode.ARGUMENT_TYPE)


def test_duplicate_link_roles_rejected_at_parse() -> None:
    """connectivity.links must not declare the same role twice."""
    connectivity = {
        "links": [{"role": "command_link"}, {"role": "command_link"}],
    }
    result = validate(PROGRAM, _drone_manifest(connectivity=connectivity), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.ARGUMENT_CONSTRAINT)
