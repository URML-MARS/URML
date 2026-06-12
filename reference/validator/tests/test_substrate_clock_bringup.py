"""Unit tests for RFC-0477 (substrate.clock) and RFC-0478 (substrate.bringup).

Both blocks were surfaced by the ethercat_driver_ros2 engagement (RFC-0320):
the maintainer raised that a fieldbus clock cannot always be hidden once events
outside the bus must be synchronized, and that the order of element bring-up and
error recovery is the most under-specified area.

`substrate.clock` (RFC-0477) declares the time-synchronization regime:
  - reference == 'master_synced' requires a sync_protocol other than 'none';
  - user_clock_max_offset_ms is only applicable when reference == 'master_synced'.

`substrate.bringup` (RFC-0478) declares ordered element dependencies:
  - element ids are unique;
  - every depends_on / recovery_after references a declared element;
  - neither dependency graph contains a cycle.

Both blocks are optional; a manifest without them is unaffected.
"""

from __future__ import annotations

from typing import Any

from urml_validator import ErrorCode, validate


def _ground_manifest(*, substrate: dict[str, Any] | None = None) -> dict[str, Any]:
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
    if substrate is not None:
        m["substrate"] = substrate
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


def _validate(substrate: dict[str, Any] | None):
    return validate(_move_program(), _ground_manifest(substrate=substrate), policy=None)


# --- RFC-0477: substrate.clock ----------------------------------------------


def test_no_substrate_clock_validates() -> None:
    result = _validate(None)
    assert result.accepted, [e.code for e in result.errors]


def test_clock_bus_reference_validates() -> None:
    clock = {"reference": "bus", "hardware_timestamping": True, "sync_protocol": "ethercat_dc"}
    result = _validate({"clock": clock})
    assert result.accepted, [e.code for e in result.errors]


def test_clock_master_synced_with_protocol_validates() -> None:
    clock = {
        "reference": "master_synced",
        "sync_protocol": "ieee1588",
        "user_clock_max_offset_ms": 2.0,
    }
    result = _validate({"clock": clock})
    assert result.accepted, [e.code for e in result.errors]


def test_clock_master_synced_without_protocol_rejected() -> None:
    result = _validate({"clock": {"reference": "master_synced"}})
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_CLOCK_SYNC_PROTOCOL_REQUIRED)


def test_clock_master_synced_protocol_none_rejected() -> None:
    clock = {"reference": "master_synced", "sync_protocol": "none"}
    result = _validate({"clock": clock})
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_CLOCK_SYNC_PROTOCOL_REQUIRED)


def test_clock_offset_with_bus_reference_rejected() -> None:
    clock = {"reference": "bus", "user_clock_max_offset_ms": 1.0}
    result = _validate({"clock": clock})
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_CLOCK_OFFSET_NOT_APPLICABLE)


# --- RFC-0478: substrate.bringup --------------------------------------------


def test_no_bringup_validates() -> None:
    result = _validate(None)
    assert result.accepted, [e.code for e in result.errors]


def test_bringup_linear_chain_validates() -> None:
    bringup = {
        "elements": [
            {"id": "power_bus"},
            {"id": "drive_axis_1", "depends_on": ["power_bus"]},
            {"id": "gripper", "depends_on": ["drive_axis_1"]},
        ]
    }
    result = _validate({"bringup": bringup})
    assert result.accepted, [e.code for e in result.errors]


def test_bringup_distinct_recovery_order_validates() -> None:
    bringup = {
        "elements": [
            {"id": "power_bus"},
            {"id": "drive_axis_1", "depends_on": ["power_bus"], "recovery_after": ["power_bus"]},
        ]
    }
    result = _validate({"bringup": bringup})
    assert result.accepted, [e.code for e in result.errors]


def test_bringup_undeclared_dependency_rejected() -> None:
    bringup = {"elements": [{"id": "drive_axis_1", "depends_on": ["power_bus"]}]}
    result = _validate({"bringup": bringup})
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_BRINGUP_DEPENDENCY_UNDECLARED)


def test_bringup_duplicate_element_rejected() -> None:
    bringup = {"elements": [{"id": "drive_axis_1"}, {"id": "drive_axis_1"}]}
    result = _validate({"bringup": bringup})
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_BRINGUP_DUPLICATE_ELEMENT)


def test_bringup_dependency_cycle_rejected() -> None:
    bringup = {
        "elements": [
            {"id": "a", "depends_on": ["b"]},
            {"id": "b", "depends_on": ["a"]},
        ]
    }
    result = _validate({"bringup": bringup})
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_BRINGUP_DEPENDENCY_CYCLE)


def test_bringup_recovery_cycle_rejected() -> None:
    bringup = {
        "elements": [
            {"id": "a", "recovery_after": ["b"]},
            {"id": "b", "recovery_after": ["a"]},
        ]
    }
    result = _validate({"bringup": bringup})
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_BRINGUP_DEPENDENCY_CYCLE)
