"""Unit tests for RFC-0251 substrate.rmw_implementation + rmw_options.

The Substrate block (introduced by RFC-0250) gains:
  - `rmw_implementation` closed-enum field (px4-style escape hatch)
  - `rmw_implementation_note` required when class is 'custom'
  - `rmw_options.qos_profile` with reliability / durability / history /
    history_depth / deadline_ms / lifespan_ms
  - `rmw_options.discovery_topology` closed enum
  - `rmw_options.config_reference` opaque string

Validator rules:
  - rmw_implementation == 'custom' requires rmw_implementation_note
  - qos_profile.history == 'keep_last' requires history_depth

The 'required-when-substrate.class==ros2' rule from the RFC is deferred
until a substrate.class field exists (no such field in v0.1).
"""

from __future__ import annotations

from typing import Any

import pytest

from urml_validator import ErrorCode, validate


def _ground_manifest(*, substrate: dict[str, Any] | None = None) -> dict[str, Any]:
    """Minimal ground-robot manifest. RMW rules don't depend on drive_type."""
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


# ---------------------------------------------------------------------------
# Positive: each allowed rmw_implementation value validates
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "rmw_implementation",
    ["rmw_fastrtps_cpp", "rmw_cyclonedds_cpp", "rmw_zenoh_cpp", "rmw_connextdds"],
)
def test_known_rmw_implementation_validates(rmw_implementation: str) -> None:
    manifest = _ground_manifest(substrate={"rmw_implementation": rmw_implementation})
    result = validate(_move_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_custom_rmw_implementation_with_note_validates() -> None:
    manifest = _ground_manifest(
        substrate={
            "rmw_implementation": "custom",
            "rmw_implementation_note": "Internal RMW shim layered on Fast DDS for testbench.",
        }
    )
    result = validate(_move_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


# ---------------------------------------------------------------------------
# Positive: rmw_options + qos_profile + discovery_topology accepted
# ---------------------------------------------------------------------------


def test_qos_profile_keep_last_with_depth_validates() -> None:
    manifest = _ground_manifest(
        substrate={
            "rmw_implementation": "rmw_fastrtps_cpp",
            "rmw_options": {
                "qos_profile": {
                    "reliability": "reliable",
                    "durability": "volatile",
                    "history": "keep_last",
                    "history_depth": 10,
                    "deadline_ms": 100,
                    "lifespan_ms": 1000,
                },
                "discovery_topology": "simple",
                "config_reference": "/etc/urml/fastdds.xml",
            },
        }
    )
    result = validate(_move_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_qos_profile_keep_all_no_depth_validates() -> None:
    # keep_all does NOT require history_depth.
    manifest = _ground_manifest(
        substrate={
            "rmw_implementation": "rmw_cyclonedds_cpp",
            "rmw_options": {
                "qos_profile": {"reliability": "best_effort", "history": "keep_all"},
            },
        }
    )
    result = validate(_move_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


@pytest.mark.parametrize(
    "topology",
    ["simple", "discovery_server", "xml_configured", "peer", "client", "router"],
)
def test_discovery_topology_values_validate(topology: str) -> None:
    manifest = _ground_manifest(
        substrate={
            "rmw_implementation": "rmw_fastrtps_cpp",
            "rmw_options": {"discovery_topology": topology},
        }
    )
    result = validate(_move_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


# ---------------------------------------------------------------------------
# Negative: rmw_implementation == custom requires non-empty note
# ---------------------------------------------------------------------------


def test_custom_rmw_without_note_rejected() -> None:
    manifest = _ground_manifest(substrate={"rmw_implementation": "custom"})
    result = validate(_move_program(), manifest, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_RMW_IMPLEMENTATION_NOTE_REQUIRED)


def test_custom_rmw_with_whitespace_only_note_rejected() -> None:
    manifest = _ground_manifest(
        substrate={"rmw_implementation": "custom", "rmw_implementation_note": "  "}
    )
    result = validate(_move_program(), manifest, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_RMW_IMPLEMENTATION_NOTE_REQUIRED)


# ---------------------------------------------------------------------------
# Negative: keep_last without history_depth
# ---------------------------------------------------------------------------


def test_keep_last_without_history_depth_rejected() -> None:
    manifest = _ground_manifest(
        substrate={
            "rmw_implementation": "rmw_fastrtps_cpp",
            "rmw_options": {
                "qos_profile": {"history": "keep_last"},
            },
        }
    )
    result = validate(_move_program(), manifest, policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_QOS_KEEP_LAST_REQUIRES_DEPTH)


# ---------------------------------------------------------------------------
# Negative: history_depth < 1 caught at parse time (Pydantic constraint)
# ---------------------------------------------------------------------------


def test_history_depth_zero_rejected_by_parser() -> None:
    manifest = _ground_manifest(
        substrate={
            "rmw_implementation": "rmw_fastrtps_cpp",
            "rmw_options": {
                "qos_profile": {"history": "keep_last", "history_depth": 0},
            },
        }
    )
    result = validate(_move_program(), manifest, policy=None)
    assert not result.accepted
    # Pydantic constraint error surfaces as Pass 1 argument.* error.
    codes = [str(e.code) for e in result.errors]
    assert any("argument." in c for c in codes)


# ---------------------------------------------------------------------------
# Backward compatibility: no substrate / no rmw declarations both pass
# ---------------------------------------------------------------------------


def test_no_substrate_block_validates() -> None:
    manifest = _ground_manifest(substrate=None)
    result = validate(_move_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_substrate_without_rmw_validates() -> None:
    manifest = _ground_manifest(substrate={})
    result = validate(_move_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_rmw_implementation_without_rmw_options_validates() -> None:
    manifest = _ground_manifest(
        substrate={"rmw_implementation": "rmw_fastrtps_cpp"}
    )
    result = validate(_move_program(), manifest, policy=None)
    assert result.accepted, [e.code for e in result.errors]
