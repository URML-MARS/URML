"""Unit tests for RFC-0016 realtime (cyclic / real-time timing declaration).

The capability manifest gains an optional `realtime` block declaring the
substrate's cyclic timing contract (control period, watchdog deadline, RPI,
honesty `guarantee`). v0.1 enforces only internal coherence, not a real-time
guarantee: the watchdog must allow at least one control cycle
(watchdog_ms >= cyclic_period_ms). The envelope-dwell Pass-3 rule is deferred.

The block is optional; a manifest without it is unaffected.
"""

from __future__ import annotations

from typing import Any

from urml_validator import ErrorCode, validate


def _ground_manifest(*, realtime: dict[str, Any] | None = None) -> dict[str, Any]:
    m: dict[str, Any] = {
        "manifest_version": "0.1",
        "robot_id": "test_ground",
        "frames": [{"name": "world", "parent": None}],
        "declared_locations": [
            {"name": "home", "pose": {"x": 0.0, "y": 0.0, "z": 0.0}, "frame": "world"}
        ],
        "mobility": {"drive_type": "differential", "max_velocity": 1.0},
        "perception": {"cameras": [], "sensors": [], "object_vocabulary": []},
    }
    if realtime is not None:
        m["realtime"] = realtime
    return m


def _move_program() -> dict[str, Any]:
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"move_to": {"location": "home"}}],
        },
    }


def test_no_realtime_block_validates() -> None:
    """Regression: a manifest without a realtime block is unaffected."""
    result = validate(_move_program(), _ground_manifest(), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_coherent_realtime_validates() -> None:
    rt = {
        "cyclic_period_ms": 10.0,
        "watchdog_ms": 50.0,
        "requested_packet_interval_ms": 10.0,
        "guarantee": "soft",
    }
    result = validate(_move_program(), _ground_manifest(realtime=rt), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_watchdog_equal_to_cycle_validates() -> None:
    """A watchdog of exactly one cycle is the boundary case and is allowed."""
    rt = {"cyclic_period_ms": 10.0, "watchdog_ms": 10.0, "guarantee": "hard"}
    result = validate(_move_program(), _ground_manifest(realtime=rt), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_watchdog_shorter_than_cycle_rejected() -> None:
    rt = {"cyclic_period_ms": 10.0, "watchdog_ms": 5.0, "guarantee": "best_effort"}
    result = validate(_move_program(), _ground_manifest(realtime=rt), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_WATCHDOG_SHORTER_THAN_CYCLE)


# --- RFC-0469: the acyclic (SDO / mailbox) regime ---------------------------


def test_acyclic_regime_validates() -> None:
    """A cyclic block with a coherent acyclic sub-block is accepted."""
    rt = {
        "cyclic_period_ms": 10.0,
        "watchdog_ms": 50.0,
        "guarantee": "soft",
        "acyclic": {"timeout_ms": 500.0, "requires_goal_check": True},
    }
    result = validate(_move_program(), _ground_manifest(realtime=rt), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_acyclic_requires_goal_check_defaults_true() -> None:
    """`requires_goal_check` is optional and defaults to honest (True)."""
    rt = {
        "cyclic_period_ms": 10.0,
        "watchdog_ms": 50.0,
        "guarantee": "soft",
        "acyclic": {"timeout_ms": 200.0},
    }
    result = validate(_move_program(), _ground_manifest(realtime=rt), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_acyclic_timeout_equal_to_cycle_validates() -> None:
    """A timeout of exactly one cycle is the boundary case and is allowed."""
    rt = {
        "cyclic_period_ms": 10.0,
        "watchdog_ms": 50.0,
        "guarantee": "hard",
        "acyclic": {"timeout_ms": 10.0},
    }
    result = validate(_move_program(), _ground_manifest(realtime=rt), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_acyclic_timeout_shorter_than_cycle_rejected() -> None:
    """An acyclic command that must return inside one cycle is cyclic traffic."""
    rt = {
        "cyclic_period_ms": 10.0,
        "watchdog_ms": 50.0,
        "guarantee": "soft",
        "acyclic": {"timeout_ms": 5.0},
    }
    result = validate(_move_program(), _ground_manifest(realtime=rt), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_ACYCLIC_TIMEOUT_SHORTER_THAN_CYCLE)


def test_acyclic_unknown_field_rejected() -> None:
    """The acyclic sub-block forbids extra keys (extra='forbid')."""
    rt = {
        "cyclic_period_ms": 10.0,
        "watchdog_ms": 50.0,
        "guarantee": "soft",
        "acyclic": {"timeout_ms": 200.0, "bogus": 1},
    }
    result = validate(_move_program(), _ground_manifest(realtime=rt), policy=None)
    assert not result.accepted
