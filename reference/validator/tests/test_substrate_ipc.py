"""Unit tests for RFC-0385 substrate.ipc (zero-copy IPC sub-substrate).

The Substrate block gains an optional `ipc` declaration of the zero-copy IPC
transport beneath the RMW middleware (an Eclipse iceoryx generation, or a
custom equivalent). Validator coherence rules:

  - generation == 'iceoryx1' requires runtime_name (the RouDi daemon);
  - generation == 'iceoryx2' requires config_path and forbids runtime_name
    (iceoryx2 is decentralized; the RouDi daemon is gone);
  - generation == 'custom' requires generation_note.

The block is optional; a deployment without substrate.ipc is unaffected.
Surfaced by the engaged iceoryx / iceoryx2 thread (RFC-0210 / RFC-0305).
"""

from __future__ import annotations

from typing import Any

import pytest

from urml_validator import ErrorCode, validate


def _ground_manifest(*, ipc: dict[str, Any] | None = None) -> dict[str, Any]:
    """Minimal ground-robot manifest; IPC rules don't depend on drive_type."""
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
    if ipc is not None:
        m["substrate"] = {"ipc": ipc}
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
# Positive
# ---------------------------------------------------------------------------


def test_no_ipc_block_validates() -> None:
    """Regression: a manifest without substrate.ipc is unaffected."""
    result = validate(_move_program(), _ground_manifest(), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_iceoryx2_with_config_validates() -> None:
    ipc = {
        "generation": "iceoryx2",
        "config_path": "/etc/iceoryx2/config.toml",
        "messaging_pattern": "pub_sub",
        "shared_memory_budget_mb": 256.0,
        "max_publishers": 8,
        "max_subscribers": 16,
    }
    result = validate(_move_program(), _ground_manifest(ipc=ipc), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_iceoryx1_with_runtime_name_validates() -> None:
    ipc = {"generation": "iceoryx1", "runtime_name": "roudi"}
    result = validate(_move_program(), _ground_manifest(ipc=ipc), policy=None)
    assert result.accepted, [e.code for e in result.errors]


def test_custom_with_note_validates() -> None:
    ipc = {"generation": "custom", "generation_note": "vendor shared-memory bus"}
    result = validate(_move_program(), _ground_manifest(ipc=ipc), policy=None)
    assert result.accepted, [e.code for e in result.errors]


# ---------------------------------------------------------------------------
# Negative: generation coherence
# ---------------------------------------------------------------------------


def test_iceoryx2_without_config_rejected() -> None:
    result = validate(
        _move_program(), _ground_manifest(ipc={"generation": "iceoryx2"}), policy=None
    )
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_IPC_CONFIG_PATH_REQUIRED)


def test_iceoryx2_with_runtime_name_rejected() -> None:
    ipc = {"generation": "iceoryx2", "config_path": "/x", "runtime_name": "roudi"}
    result = validate(_move_program(), _ground_manifest(ipc=ipc), policy=None)
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_IPC_RUNTIME_NAME_NOT_APPLICABLE)


def test_iceoryx1_without_runtime_name_rejected() -> None:
    result = validate(
        _move_program(), _ground_manifest(ipc={"generation": "iceoryx1"}), policy=None
    )
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_IPC_RUNTIME_NAME_REQUIRED)


def test_custom_without_note_rejected() -> None:
    result = validate(
        _move_program(), _ground_manifest(ipc={"generation": "custom"}), policy=None
    )
    assert not result.accepted
    assert result.has(ErrorCode.CAPABILITY_IPC_GENERATION_NOTE_REQUIRED)
