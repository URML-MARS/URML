"""RFC-0006 — Pass-3 link-loss policy coherence checks.

Each rule's action must be satisfiable by the manifest. Negative-test
convention: isolate one failure mode, assert the stable code. Pass 5 is
disabled (`policy=None`) to isolate Pass 2/3.
"""

from __future__ import annotations

from typing import Any

from urml_validator import ErrorCode, validate

PROGRAM: dict[str, Any] = {
    "profile": "drone",
    "behavior": {"type": "sequence", "steps": [{"wait": {"duration": "1s"}}]},
}


def _aerial_manifest(
    *, home: bool = True, links: list[dict] | None = None
) -> dict[str, Any]:
    m: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "test_drone",
        "frames": [{"name": "agl", "parent": None}],
        "declared_locations": (
            [{"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "agl"}]
            if home
            else []
        ),
        "mobility": {
            "drive_type": "multirotor",
            "max_velocity": 15.0,
            "station_keeping": True,
            "service_ceiling": 120.0,
        },
        "connectivity": {"links": links if links is not None else [{"role": "command_link"}]},
    }
    return m


def _ground_manifest(*, links: list[dict] | None = None) -> dict[str, Any]:
    return {
        "manifest_version": "0.1",
        "robot_id": "test_ground",
        "mobility": {
            "drive_type": "differential",
            "max_velocity": 0.5,
            "station_keeping": False,
        },
        "connectivity": {"links": links if links is not None else [{"role": "command_link"}]},
    }


def _env(role: str, action: str, **extra: Any) -> dict[str, Any]:
    rule: dict[str, Any] = {"role": role, "action": action, **extra}
    return {"link_loss_policy": [rule]}


# --- return_to_home -------------------------------------------------------


def test_return_to_home_without_home_location_rejected() -> None:
    result = validate(
        PROGRAM, _aerial_manifest(home=False), _env("command_link", "return_to_home"), policy=None
    )
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT)


def test_return_to_home_fully_declared_is_accepted() -> None:
    result = validate(
        PROGRAM, _aerial_manifest(home=True), _env("command_link", "return_to_home"), policy=None
    )
    assert result.accepted, [e.render() for e in result.errors]


def test_return_to_home_on_ground_robot_rejected() -> None:
    result = validate(
        PROGRAM, _ground_manifest(), _env("command_link", "return_to_home"), policy=None
    )
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT)


# --- land_now / hover -----------------------------------------------------


def test_land_now_on_ground_robot_rejected() -> None:
    result = validate(PROGRAM, _ground_manifest(), _env("command_link", "land_now"), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT)


def test_hover_without_station_keeping_rejected() -> None:
    result = validate(PROGRAM, _ground_manifest(), _env("command_link", "hover"), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT)


# --- halt_and_report ------------------------------------------------------


def test_halt_and_report_on_ground_robot_is_accepted() -> None:
    result = validate(
        PROGRAM, _ground_manifest(), _env("command_link", "halt_and_report"), policy=None
    )
    assert result.accepted, [e.render() for e in result.errors]


# --- continue_autonomous --------------------------------------------------


def test_continue_autonomous_without_capability_rejected() -> None:
    m = _aerial_manifest(
        links=[{"role": "command_link", "autonomous_when_lost": False}]
    )
    result = validate(PROGRAM, m, _env("command_link", "continue_autonomous"), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_LINK_LOSS_INCOHERENT)


def test_continue_autonomous_with_capability_is_accepted() -> None:
    m = _aerial_manifest(
        links=[{"role": "command_link", "autonomous_when_lost": True}]
    )
    result = validate(PROGRAM, m, _env("command_link", "continue_autonomous"), policy=None)
    assert result.accepted, [e.render() for e in result.errors]


# --- undeclared role within a present connectivity block ------------------


def test_rule_role_not_in_connectivity_block_rejected() -> None:
    m = _aerial_manifest(links=[{"role": "telemetry_link"}])
    result = validate(PROGRAM, m, _env("command_link", "halt_and_report"), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_LINK_LOSS_UNDECLARED_ROLE)
    # Pass 2 stays silent: connectivity exists, so this is a Pass-3 concern.
    assert not result.has(ErrorCode.CAPABILITY_MISSING_LINK_ROLE)


# --- outage tightening ----------------------------------------------------


def test_rule_outage_looser_than_manifest_rejected() -> None:
    m = _aerial_manifest(
        links=[{"role": "command_link", "max_outage_seconds": 5.0}]
    )
    result = validate(
        PROGRAM,
        m,
        _env("command_link", "return_to_home", max_outage_seconds=30.0),
        policy=None,
    )
    assert not result.accepted
    assert result.has(ErrorCode.ENVELOPE_LINK_OUTAGE_EXCEEDS_DECLARED)


def test_rule_outage_tighter_than_manifest_is_accepted() -> None:
    m = _aerial_manifest(
        links=[{"role": "command_link", "max_outage_seconds": 30.0}]
    )
    result = validate(
        PROGRAM,
        m,
        _env("command_link", "return_to_home", max_outage_seconds=5.0),
        policy=None,
    )
    assert result.accepted, [e.render() for e in result.errors]
