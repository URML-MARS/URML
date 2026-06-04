"""RFC-0382: validator integration for envelope monitorable properties.

Pass 5 is disabled (`policy=None`) to isolate the Pass-3 monitorable check.
A monitorable property must parse and reference only declared signals: the
built-in quantities (speed, altitude, payload, grip_force, person_distance),
a declared sensor, or a declared event.
"""

from __future__ import annotations

from typing import Any

from urml_validator import ErrorCode, validate

PROGRAM: dict[str, Any] = {
    "profile": "home",
    "behavior": {"type": "sequence", "steps": [{"wait": {"duration": "1s"}}]},
}

MANIFEST: dict[str, Any] = {
    "manifest_version": "0.1",
    "robot_id": "test_bot",
    "mobility": {"drive_type": "differential", "max_velocity": 0.5, "station_keeping": False},
    "declared_events": ["stop_requested"],
    "perception": {
        "sensors": [
            {"name": "range", "measurement_type": "distance", "range_min": 0.0, "range_max": 10.0, "units": "m"}
        ]
    },
}


def _env(*props: dict[str, Any]) -> dict[str, Any]:
    return {"monitorable_properties": list(props)}


def _codes(result: Any) -> list[str]:
    return [e.code_str for e in result.errors]


def test_baseline_no_properties_accepted() -> None:
    """The manifest/program validate cleanly with no monitorable properties."""
    result = validate(PROGRAM, MANIFEST, {}, policy=None)
    assert result.accepted, _codes(result)


def test_builtin_quantities_property_accepted() -> None:
    result = validate(
        PROGRAM,
        MANIFEST,
        _env(
            {
                "name": "slow_near_people",
                "severity": "critical",
                "dialect": "stl",
                "expression": "always (person_distance < 2.0 implies speed <= 0.3)",
            }
        ),
        policy=None,
    )
    assert result.accepted, _codes(result)


def test_event_and_sensor_signals_accepted() -> None:
    result = validate(
        PROGRAM,
        MANIFEST,
        _env(
            {
                "name": "bounded_stop",
                "dialect": "stl",
                "expression": "always (stop_requested implies eventually[0, 0.5] (speed == 0))",
            },
            {"name": "keep_clear", "dialect": "stl", "expression": "always (range > 0.2)"},
        ),
        policy=None,
    )
    assert result.accepted, _codes(result)


def test_undeclared_signal_rejected() -> None:
    result = validate(
        PROGRAM,
        MANIFEST,
        _env({"name": "overheat", "dialect": "stl", "expression": "always (battery_temp < 80)"}),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.ENVELOPE_MONITORABLE_UNDECLARED_SIGNAL.value in _codes(result)


def test_malformed_expression_rejected() -> None:
    result = validate(
        PROGRAM,
        MANIFEST,
        _env({"name": "broken", "dialect": "stl", "expression": "always ("}),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.ENVELOPE_MONITORABLE_PARSE_ERROR.value in _codes(result)


def test_custom_dialect_resolves_signals() -> None:
    """A `custom` expression is not parsed, but its signals are still resolved."""
    result = validate(
        PROGRAM,
        MANIFEST,
        _env({"name": "c", "dialect": "custom", "expression": "G(battery_temp < 80)"}),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.ENVELOPE_MONITORABLE_UNDECLARED_SIGNAL.value in _codes(result)


def test_explicit_signals_must_also_be_declared() -> None:
    result = validate(
        PROGRAM,
        MANIFEST,
        _env(
            {
                "name": "p",
                "dialect": "stl",
                "expression": "always (speed <= 0.3)",
                "signals": ["made_up_signal"],
            }
        ),
        policy=None,
    )
    assert not result.accepted
    assert ErrorCode.ENVELOPE_MONITORABLE_UNDECLARED_SIGNAL.value in _codes(result)
