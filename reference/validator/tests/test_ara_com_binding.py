"""Unit tests for RFC-0019: AUTOSAR ara::com program binding.

AUTOSAR rides `call_program` (RFC-0015) rather than a new primitive; a declared
program may carry an `ara_com` binding (service/instance/method id triple). The
validator requires the full triple when a binding is present
(capability.ara_com_binding_incomplete). AUTOSAR Execution Management timing
rides the `realtime` block (RFC-0016).
"""

from __future__ import annotations

import copy
from typing import Any

from urml_validator import ErrorCode, validate


def _manifest(*, binding: dict[str, Any] | None) -> dict[str, Any]:
    program: dict[str, Any] = {
        "name": "set_wheel_torque",
        "args": [{"name": "torque_nm", "type": "number"}],
    }
    if binding is not None:
        program["binding"] = binding
    return {
        "manifest_version": "0.1",
        "robot_id": "test_autosar",
        "frames": [{"name": "base", "parent": None}],
        "declared_locations": [{"name": "home", "pose": {"x": 0.0, "y": 0.0}, "frame": "base"}],
        "mobility": {"drive_type": "differential", "max_velocity": 1.0},
        "programs": [program],
    }


def _call_program() -> dict[str, Any]:
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"call_program": {"name": "set_wheel_torque", "args": {"torque_nm": 5.0}}}],
        },
    }


_FULL = {"kind": "ara_com", "service_id": 4097, "instance_id": 1, "method_id": 12}


def test_complete_ara_com_binding_accepted() -> None:
    result = validate(_call_program(), _manifest(binding=_FULL), policy=None)
    assert result.accepted, [e.code.value for e in result.errors]


def test_program_without_binding_accepted() -> None:
    """Regression: a program with no binding (plain RFC-0015) is unaffected."""
    result = validate(_call_program(), _manifest(binding=None), policy=None)
    assert result.accepted, [e.code.value for e in result.errors]


def test_incomplete_ara_com_binding_rejected() -> None:
    for missing in ("service_id", "instance_id", "method_id"):
        binding = {k: v for k, v in _FULL.items() if k != missing}
        result = validate(_call_program(), _manifest(binding=binding), policy=None)
        assert not result.accepted, missing
        assert result.has(ErrorCode.CAPABILITY_ARA_COM_BINDING_INCOMPLETE), missing
