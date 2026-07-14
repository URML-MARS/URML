"""RFC-0668 CLI: `urml run` end-to-end and the rehearsal gate on `execute`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from urml_validator.cli import main

FIXTURES = Path(__file__).parent / "fixtures"
MANIFEST = FIXTURES / "manifests" / "turtlebot4_home.yaml"

_PROGRAM = {
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


@pytest.fixture()
def echo_response(tmp_path: Path) -> Path:
    path = tmp_path / "echo.json"
    path.write_text(json.dumps(_PROGRAM), encoding="utf-8")
    return path


@pytest.fixture()
def program_file(tmp_path: Path) -> Path:
    path = tmp_path / "program.yaml"
    path.write_text(yaml.safe_dump(_PROGRAM), encoding="utf-8")
    return path


def _envelope_file(tmp_path: Path, max_velocity: float) -> Path:
    path = tmp_path / f"envelope-{max_velocity}.yaml"
    path.write_text(yaml.safe_dump({"max_velocity": max_velocity}), encoding="utf-8")
    return path


def test_run_with_passing_rehearsal_executes(tmp_path: Path, echo_response: Path, capsys) -> None:
    envelope = _envelope_file(tmp_path, 1.0)  # kinematic default cruise 0.5 stays under
    code = main(
        [
            "run", "Patrol the kitchen and come back to me.",
            "--manifest", str(MANIFEST),
            "--envelope", str(envelope),
            "--profile", "home",
            "--provider", "echo",
            "--echo-response-file", str(echo_response),
            "--no-policy",
            "--rehearse",
            "--adapter", "mock",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, captured.err
    assert "gate: PASSED" in captured.err
    assert "SYNTHETIC KINEMATIC PROFILE" in captured.err
    assert "URML execute:" in captured.out
    assert "send_navigation_goal" in captured.out


def test_run_rehearsal_failure_blocks_execution(tmp_path: Path, echo_response: Path, capsys) -> None:
    envelope = _envelope_file(tmp_path, 0.2)  # cap below the kinematic cruise assumption
    code = main(
        [
            "run", "Patrol the kitchen and come back to me.",
            "--manifest", str(MANIFEST),
            "--envelope", str(envelope),
            "--profile", "home",
            "--provider", "echo",
            "--echo-response-file", str(echo_response),
            "--no-policy",
            "--rehearse",
            "--adapter", "mock",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert "gate: FAILED" in captured.err
    assert "envelope.max_velocity" in captured.err
    assert "URML execute:" not in captured.out, "the real adapter must receive nothing"


def test_run_without_rehearse_still_works(echo_response: Path, capsys) -> None:
    code = main(
        [
            "run", "Patrol the kitchen and come back to me.",
            "--manifest", str(MANIFEST),
            "--profile", "home",
            "--provider", "echo",
            "--echo-response-file", str(echo_response),
            "--no-policy",
            "--adapter", "mock",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, captured.err
    assert "rehearsal" not in captured.err.lower()
    assert "URML execute:" in captured.out


def test_run_writes_program_out(tmp_path: Path, echo_response: Path) -> None:
    out = tmp_path / "accepted.yaml"
    code = main(
        [
            "run", "Patrol the kitchen and come back to me.",
            "--manifest", str(MANIFEST),
            "--profile", "home",
            "--provider", "echo",
            "--echo-response-file", str(echo_response),
            "--no-policy",
            "--out", str(out),
        ]
    )
    assert code == 0
    assert yaml.safe_load(out.read_text(encoding="utf-8")) == _PROGRAM


def test_run_echo_requires_response_file(capsys) -> None:
    code = main(
        [
            "run", "Patrol.",
            "--manifest", str(MANIFEST),
            "--provider", "echo",
            "--no-policy",
        ]
    )
    assert code == 2
    assert "echo-response-file" in capsys.readouterr().err


def test_execute_rehearse_gate(tmp_path: Path, program_file: Path, capsys) -> None:
    passing = _envelope_file(tmp_path, 1.0)
    code = main(
        [
            "execute", str(program_file),
            "--manifest", str(MANIFEST),
            "--envelope", str(passing),
            "--profile", "home",
            "--no-policy",
            "--rehearse",
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, captured.err
    assert "gate: PASSED" in captured.err

    failing = _envelope_file(tmp_path, 0.2)
    code = main(
        [
            "execute", str(program_file),
            "--manifest", str(MANIFEST),
            "--envelope", str(failing),
            "--profile", "home",
            "--no-policy",
            "--rehearse",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert "gate: FAILED" in captured.err
    assert "URML execute:" not in captured.out


def test_execute_rehearse_config_profile(tmp_path: Path, program_file: Path, capsys) -> None:
    # A slower declared profile passes the same tight cap.
    envelope = _envelope_file(tmp_path, 0.2)
    config = tmp_path / "kinematic.yaml"
    config.write_text(yaml.safe_dump({"cruise_speed": 0.1, "turn_speed": 0.05}), encoding="utf-8")
    code = main(
        [
            "execute", str(program_file),
            "--manifest", str(MANIFEST),
            "--envelope", str(envelope),
            "--profile", "home",
            "--no-policy",
            "--rehearse", "kinematic",
            "--rehearse-config", str(config),
        ]
    )
    captured = capsys.readouterr()
    assert code == 0, captured.err
    assert "gate: PASSED" in captured.err
