"""RFC-0668 rehearsal gate: kinematic backend end-to-end, pass and fail."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from urml_ros2_runtime import (
    KinematicProfile,
    KinematicRehearsalAdapter,
    MockROSAdapter,
    TraceRecorder,
    rehearse,
)


def _manifest(name: str) -> dict:
    fixture = (
        Path(__file__).resolve().parents[2]
        / "validator" / "tests" / "fixtures" / "manifests" / f"{name}.yaml"
    )
    with fixture.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _patrol_program() -> dict:
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"move_to": {"location": "kitchen"}},
                {"move_to": {"location": "user"}},
            ],
        },
    }


def test_rehearsal_passes_within_envelope() -> None:
    adapter = KinematicRehearsalAdapter(KinematicProfile(cruise_speed=0.4))
    report = rehearse(
        _patrol_program(),
        _manifest("turtlebot4_home"),
        {"max_velocity": 1.0},
        adapter=adapter,
        profiles=("home",),
    )
    assert report.passed
    assert report.sim_success
    assert report.steps_executed == 2
    assert report.trace_len > 0
    assert report.properties_checked == 1
    assert report.violations == ()


def test_rehearsal_fails_when_profile_breaks_the_cap() -> None:
    # The declared kinematic assumption (2.0 m/s) exceeds the envelope cap.
    adapter = KinematicRehearsalAdapter(KinematicProfile(cruise_speed=2.0))
    report = rehearse(
        _patrol_program(),
        _manifest("turtlebot4_home"),
        {"max_velocity": 1.0},
        adapter=adapter,
        profiles=("home",),
    )
    assert not report.passed
    assert report.sim_success, "the sim run itself succeeds; the envelope is what fails"
    critical = report.critical_violations()
    assert [v.name for v in critical] == ["envelope.max_velocity"]
    payload = report.to_payload()
    assert payload["passed"] is False
    assert payload["violations"][0]["property"] == "envelope.max_velocity"


def test_rehearsal_checks_declared_monitorable_properties() -> None:
    envelope = {
        "monitorable_properties": [
            {
                "name": "no_sustained_motion",
                "severity": "critical",
                "dialect": "stl",
                "expression": "eventually (speed <= 0.05)",
            }
        ]
    }
    adapter = KinematicRehearsalAdapter()
    report = rehearse(
        _patrol_program(), _manifest("turtlebot4_home"), envelope, adapter=adapter, profiles=("home",)
    )
    # The kinematic profile returns to rest at each command boundary.
    assert report.passed
    assert report.properties_checked == 1


def test_warning_violations_reported_but_gate_passes() -> None:
    envelope = {
        "monitorable_properties": [
            {
                "name": "prefer_crawl",
                "severity": "warning",
                "dialect": "stl",
                "expression": "always (speed <= 0.1)",
            }
        ]
    }
    adapter = KinematicRehearsalAdapter(KinematicProfile(cruise_speed=0.5))
    report = rehearse(
        _patrol_program(), _manifest("turtlebot4_home"), envelope, adapter=adapter, profiles=("home",)
    )
    assert report.passed, "warning severity reports but does not fail the gate (RFC-0667 mapping)"
    assert [v.severity for v in report.violations] == ["warning"]


def test_empty_envelope_gates_on_execution_only() -> None:
    adapter = KinematicRehearsalAdapter()
    report = rehearse(_patrol_program(), _manifest("turtlebot4_home"), None, adapter=adapter, profiles=("home",))
    assert report.passed
    assert report.properties_checked == 0
    assert any("checked execution only" in note for note in report.notes)


def test_adapter_without_recorder_rejected() -> None:
    with pytest.raises(TypeError, match="TraceRecorder"):
        rehearse(
            _patrol_program(),
            _manifest("turtlebot4_home"),
            {"max_velocity": 1.0},
            adapter=MockROSAdapter(),
            profiles=("home",),
        )


def test_kinematic_adapter_is_a_trace_recorder() -> None:
    adapter = KinematicRehearsalAdapter()
    assert isinstance(adapter, TraceRecorder)
    assert adapter.samples() == ()


def test_altitude_profile_for_drone_program() -> None:
    program = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"take_off": {"altitude": 30.0}},
                {"move_to": {"location": "roof_north"}},
                {"return_to_home": {}},
                {"land": {}},
            ],
        },
    }
    ok = rehearse(
        program,
        _manifest("drone_civilian"),
        {"max_altitude": 50.0},
        adapter=KinematicRehearsalAdapter(),
        profiles=("drone",),
    )
    assert ok.passed

    too_low_ceiling = rehearse(
        program,
        _manifest("drone_civilian"),
        {"max_altitude": 50.0, "monitorable_properties": [
            {"name": "stay_low", "severity": "critical", "dialect": "stl",
             "expression": "always (altitude <= 20.0)"},
        ]},
        adapter=KinematicRehearsalAdapter(),
        profiles=("drone",),
    )
    assert not too_low_ceiling.passed
    assert [v.name for v in too_low_ceiling.critical_violations()] == ["stay_low"]
