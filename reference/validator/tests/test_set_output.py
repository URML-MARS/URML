"""Unit tests for RFC-0017 `set_output` digital/analog actuation.

Covers the Pass-2 capability checks: a declared line is accepted, an undeclared
line is rejected, a digital line rejects a non-bool, and an analog value is
range-checked. Also covers the manifest-level `OutputLine` coherence rules.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import validate
from urml_validator.errors import ErrorCode
from urml_validator.schemas.manifest import OutputLine


def _manifest() -> dict:
    return {
        "manifest_version": "0.1",
        "robot_id": "cobot_outputs",
        "frames": [{"name": "cell", "parent": None}],
        "mobility": {"drive_type": "manipulator_base", "max_velocity": 0.5, "station_keeping": True},
        "outputs": {
            "lines": [
                {"name": "glue_gun", "kind": "digital", "safe_state": False},
                {"name": "spray_rate", "kind": "analog", "range": [0.0, 100.0], "safe_state": 0.0},
            ]
        },
    }


def _program(step: dict) -> dict:
    return {
        "profile": "industrial",
        "behavior": {"type": "sequence", "on_error": "abort_and_report", "steps": [step]},
    }


def test_set_output_digital_accepted() -> None:
    result = validate(
        _program({"set_output": {"output": "glue_gun", "value": True, "pulse_ms": 500}}),
        _manifest(),
        policy=None,
    )
    assert result.accepted, [e.code for e in result.errors]


def test_set_output_analog_in_range_accepted() -> None:
    result = validate(
        _program({"set_output": {"output": "spray_rate", "value": 60.0}}),
        _manifest(),
        policy=None,
    )
    assert result.accepted, [e.code for e in result.errors]


def test_set_output_undeclared_line_rejected() -> None:
    result = validate(
        _program({"set_output": {"output": "weld_tip", "value": True}}),
        _manifest(),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.CAPABILITY_OUTPUT_LINE_NOT_DECLARED in {e.code for e in result.errors}


def test_set_output_analog_out_of_range_rejected() -> None:
    result = validate(
        _program({"set_output": {"output": "spray_rate", "value": 150.0}}),
        _manifest(),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.CAPABILITY_OUTPUT_VALUE_OUT_OF_RANGE in {e.code for e in result.errors}


def test_set_output_digital_non_bool_rejected() -> None:
    result = validate(
        _program({"set_output": {"output": "glue_gun", "value": 0.5}}),
        _manifest(),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.CAPABILITY_OUTPUT_VALUE_TYPE_MISMATCH in {e.code for e in result.errors}


def test_set_output_analog_bool_rejected() -> None:
    result = validate(
        _program({"set_output": {"output": "spray_rate", "value": True}}),
        _manifest(),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.CAPABILITY_OUTPUT_VALUE_TYPE_MISMATCH in {e.code for e in result.errors}


def test_output_line_digital_with_range_rejected() -> None:
    with pytest.raises(PydanticValidationError):
        OutputLine(name="x", kind="digital", range=(0.0, 1.0), safe_state=False)


def test_output_line_analog_requires_range() -> None:
    with pytest.raises(PydanticValidationError):
        OutputLine(name="x", kind="analog", safe_state=0.0)


def test_output_line_analog_safe_state_out_of_range_rejected() -> None:
    with pytest.raises(PydanticValidationError):
        OutputLine(name="x", kind="analog", range=(0.0, 10.0), safe_state=50.0)


def test_output_line_digital_safe_state_must_be_bool() -> None:
    with pytest.raises(PydanticValidationError):
        OutputLine(name="x", kind="digital", safe_state=1.0)
