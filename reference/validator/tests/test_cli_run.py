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
    written = yaml.safe_load(out.read_text(encoding="utf-8"))
    # The request rides along as `description` (Discussion #597); the rest is verbatim.
    assert written.pop("description") == "Patrol the kitchen and come back to me."
    assert written == _PROGRAM


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


def _spy_on_runtime(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, dict]]:
    """Record how `urml run` builds and calls URMLRuntime (the real one still runs)."""
    import urml_ros2_runtime

    seen: list[tuple[str, dict]] = []
    real = urml_ros2_runtime.URMLRuntime

    class _Spy(real):  # type: ignore[misc,valid-type]
        def __init__(self, adapter, **kwargs) -> None:
            seen.append(("init", kwargs))
            super().__init__(adapter, **kwargs)

        def execute(self, *args, **kwargs):
            seen.append(("execute", kwargs))
            return super().execute(*args, **kwargs)

    monkeypatch.setattr(urml_ros2_runtime, "URMLRuntime", _Spy)
    return seen


def test_run_runtime_revalidates_with_the_chosen_policy(
    echo_response: Path, monkeypatch: pytest.MonkeyPatch, capsys
) -> None:
    seen = _spy_on_runtime(monkeypatch)
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
    assert code == 0, capsys.readouterr().err
    calls = dict(seen)
    assert calls["init"].get("revalidate", True) is True
    assert calls["execute"]["policy"] is None
    assert calls["execute"]["manifest_base_dir"] == MANIFEST.parent


def test_run_refuses_when_the_runtime_check_rejects(tmp_path: Path, capsys) -> None:
    """The bridge validates without the manifest's directory, so an HBOM-content
    rule can only warn there. The runtime re-validates with the directory, reads
    the HBOM, and refuses before any adapter call."""
    echo = tmp_path / "echo.json"
    echo.write_text(
        json.dumps(
            {
                "profile": "home",
                "behavior": {
                    "type": "sequence",
                    "on_error": "abort_and_report",
                    "steps": [{"move_to": {"location": "kitchen"}}],
                },
            }
        ),
        encoding="utf-8",
    )
    code = main(
        [
            "run", "Go to the kitchen.",
            "--manifest", str(FIXTURES / "manifests" / "provenance_hbom_cn_chip.yaml"),
            "--policy", str(FIXTURES / "policies" / "hbom_no_cn_components.yaml"),
            "--profile", "home",
            "--provider", "echo",
            "--echo-response-file", str(echo),
            "--adapter", "mock",
        ]
    )
    captured = capsys.readouterr()
    assert code == 1
    assert "execution refused" in captured.err
    assert "policy.hbom_component_country_denied" in captured.err
    assert "URML execute:" not in captured.out


def test_run_real_adapter_without_envelope_warns_first(
    tmp_path: Path, echo_response: Path, capsys
) -> None:
    code = main(
        [
            "run", "Patrol the kitchen and come back to me.",
            "--manifest", str(MANIFEST),
            "--profile", "home",
            "--provider", "echo",
            "--echo-response-file", str(echo_response),
            "--no-policy",
            "--adapter", "px4",
            "--adapter-config", str(tmp_path / "no_such.yaml"),
        ]
    )
    lines = capsys.readouterr().err.splitlines()
    assert code == 2  # the adapter build fails after the warning
    warning = [line for line in lines if line.startswith("urml: warning: --adapter px4 runs with no --envelope")]
    assert len(warning) == 1
    build_error = next(i for i, line in enumerate(lines) if "adapter-config file not found" in line)
    assert lines.index(warning[0]) < build_error


def test_run_ollama_requires_model(capsys) -> None:
    """The `run` parser carries the shared provider flags: --provider ollama
    without --model exits 2 before any adapter is constructed."""
    code = main(
        [
            "run", "Patrol the kitchen.",
            "--manifest", str(MANIFEST),
            "--provider", "ollama",
            "--no-policy",
        ]
    )
    captured = capsys.readouterr()
    assert code == 2
    assert "--model" in captured.err
    assert "ollama list" in captured.err


def test_run_audio_flags_present(tmp_path, capsys) -> None:
    """The `run` parser carries the shared speech flags (RFC-0670): --audio
    with a missing file exits 2 before any adapter is constructed."""
    code = main(
        [
            "run",
            "--manifest", str(MANIFEST),
            "--audio", str(tmp_path / "missing.wav"),
            "--no-policy",
        ]
    )
    captured = capsys.readouterr()
    assert code == 2
    assert "audio file not found" in captured.err
