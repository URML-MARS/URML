"""RFC-0667 shield: gate, step-boundary telemetry, ShieldedAdapter interposition."""

from __future__ import annotations

import pytest
from urml_validator.monitor import Sample

from urml_ros2_runtime import (
    MockROSAdapter,
    ROSAdapter,
    Shield,
    ShieldedAdapter,
    ShieldViolationError,
    TelemetryAdapter,
    URMLRuntime,
)

_ENVELOPE = {"max_velocity": 1.0}

_CRITICAL_PERSON_RULE = {
    "monitorable_properties": [
        {
            "name": "person_slowdown",
            "severity": "critical",
            "dialect": "stl",
            "expression": "always ((person_distance < 2.0) implies (speed <= 0.3))",
        }
    ]
}

_WARNING_RULE = {
    "monitorable_properties": [
        {
            "name": "prefer_slow",
            "severity": "warning",
            "dialect": "stl",
            "expression": "always (speed <= 0.5)",
        }
    ]
}


def _sample(t: float, speed: float, person_distance: float = 100.0) -> Sample:
    return Sample(
        t=t,
        signals={
            "speed": speed,
            "altitude": 0.0,
            "payload": 0.0,
            "grip_force": 0.0,
            "person_distance": person_distance,
        },
    )


def _three_move_program() -> dict:
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"move_to": {"location": "kitchen"}},
                {"move_to": {"location": "user"}},
                {"move_to": {"location": "charging_dock"}},
            ],
        },
    }


# ---------------------------------------------------------------------------
# Shield core
# ---------------------------------------------------------------------------


def test_gate_passes_with_no_violations() -> None:
    shield = Shield(_ENVELOPE)
    shield.gate("move_to")  # no telemetry yet: nothing stands violated


def test_observe_then_gate_vetoes_on_critical() -> None:
    shield = Shield(_ENVELOPE)  # max_velocity derives a critical always-property
    violations = shield.observe(_sample(0.0, speed=2.0))
    assert [v.name for v in violations] == ["envelope.max_velocity"]
    with pytest.raises(ShieldViolationError, match=r"envelope\.max_velocity"):
        shield.gate("move_to")


def test_warning_violation_never_blocks() -> None:
    shield = Shield(_WARNING_RULE)
    violations = shield.observe(_sample(0.0, speed=0.9))
    assert [v.severity for v in violations] == ["warning"]
    shield.gate("move_to")  # warnings record, they do not veto
    assert shield.audit_entries()[0]["property"] == "prefer_slow"


def test_shield_never_reads_a_clock() -> None:
    shield = Shield(_ENVELOPE)
    shield.observe(_sample(1000.0, speed=0.1))
    shield.observe(_sample(1001.0, speed=0.1))
    assert shield.violations() == []


# ---------------------------------------------------------------------------
# URMLRuntime integration
# ---------------------------------------------------------------------------


def _home_manifest() -> dict:
    from pathlib import Path

    import yaml

    fixture = (
        Path(__file__).resolve().parents[2]
        / "validator" / "tests" / "fixtures" / "manifests" / "turtlebot4_home.yaml"
    )
    with fixture.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def test_runtime_halts_mid_program_on_critical_violation() -> None:
    adapter = MockROSAdapter()
    # Second move overspeeds: the shield must halt before the third dispatch.
    adapter.set_telemetry([_sample(0.0, speed=0.5), _sample(1.0, speed=2.0)])
    shield = Shield(_ENVELOPE)
    runtime = URMLRuntime(adapter, shield=shield)

    result = runtime.execute(_three_move_program(), _home_manifest(), profiles=("home",))

    assert not result.success
    assert result.last_outcome is not None
    assert "shield.critical_violation" in (result.last_outcome.reason or "")
    navigations = [e for e in result.audit_log if e.get("method") == "send_navigation_goal"]
    assert len(navigations) == 2, "the third move must never dispatch"
    shield_entries = [e for e in result.audit_log if e.get("method") == "shield.violation"]
    assert shield_entries and shield_entries[0]["property"] == "envelope.max_velocity"
    assert shield_entries[0]["severity"] == "critical"


def test_runtime_with_shield_and_clean_telemetry_succeeds() -> None:
    adapter = MockROSAdapter()
    shield = Shield(_ENVELOPE)
    runtime = URMLRuntime(adapter, shield=shield)
    result = runtime.execute(_three_move_program(), _home_manifest(), profiles=("home",))
    assert result.success
    assert result.steps_executed == 3
    assert shield.violations() == []


def test_runtime_without_shield_is_unchanged() -> None:
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    result = runtime.execute(_three_move_program(), _home_manifest(), profiles=("home",))
    assert result.success
    assert all(e.get("method") != "sample_signals" for e in result.audit_log)


def test_runtime_warning_violations_recorded_not_halting() -> None:
    adapter = MockROSAdapter()
    adapter.set_telemetry([_sample(0.0, speed=0.9)])
    shield = Shield(_WARNING_RULE)
    runtime = URMLRuntime(adapter, shield=shield)
    result = runtime.execute(_three_move_program(), _home_manifest(), profiles=("home",))
    assert result.success, "a warning-severity violation must not halt the program"
    shield_entries = [e for e in result.audit_log if e.get("method") == "shield.violation"]
    assert [e["severity"] for e in shield_entries] == ["warning"]


# ---------------------------------------------------------------------------
# ShieldedAdapter — the VLA-shield story: no URMLRuntime involved
# ---------------------------------------------------------------------------


def test_shielded_adapter_satisfies_the_protocols() -> None:
    shielded = ShieldedAdapter(MockROSAdapter(), Shield(_ENVELOPE))
    assert isinstance(shielded, ROSAdapter)
    assert isinstance(shielded, TelemetryAdapter)


def test_shielded_adapter_halts_a_raw_driver() -> None:
    inner = MockROSAdapter()
    inner.set_telemetry([_sample(0.0, speed=0.5), _sample(1.0, speed=2.0)])
    shielded = ShieldedAdapter(inner, Shield(_ENVELOPE))

    # An arbitrary policy (no URML program anywhere) drives the adapter.
    shielded.send_navigation_goal(location="kitchen")
    with pytest.raises(ShieldViolationError, match=r"envelope\.max_velocity"):
        shielded.send_navigation_goal(location="user")
    # The violation stands: the next action is vetoed at the gate.
    with pytest.raises(ShieldViolationError):
        shielded.send_manipulation_goal(action="grasp", target={"object": "mug"}, force="gentle")
    navigations = [e for e in inner.call_log if e["method"] == "send_navigation_goal"]
    assert len(navigations) == 2, "the vetoed third action never reached the robot"


def test_shielded_adapter_person_proximity_rule() -> None:
    inner = MockROSAdapter()
    inner.set_telemetry([_sample(0.0, speed=1.0, person_distance=5.0), _sample(1.0, speed=1.0, person_distance=1.0)])
    shielded = ShieldedAdapter(inner, Shield(_CRITICAL_PERSON_RULE))

    shielded.send_navigation_goal(location="kitchen")  # fast but nobody near: fine
    with pytest.raises(ShieldViolationError, match="person_slowdown"):
        shielded.send_navigation_goal(location="user")  # fast with a person at 1 m


def test_shielded_adapter_mirrors_inner_surface() -> None:
    class _Minimal:
        def send_navigation_goal(self, **kwargs: object) -> None:
            return None

    shielded = ShieldedAdapter(_Minimal(), Shield(_ENVELOPE))
    with pytest.raises(AttributeError):
        _ = shielded.drive_by  # inner has no relative-motion surface; neither does the wrapper


def test_shielded_adapter_non_guarded_attributes_pass_through() -> None:
    inner = MockROSAdapter()
    shielded = ShieldedAdapter(inner, Shield(_ENVELOPE))
    assert shielded.call_log is inner.call_log
