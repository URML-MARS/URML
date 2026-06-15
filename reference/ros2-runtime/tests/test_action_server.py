"""Hermetic tests for the URML ExecuteURML action-server core.

These exercise ``execute_request`` (the rclpy-free core) with ``MockROSAdapter``
and the hermetic ``EchoProvider``. No ROS 2, no network, no LLM. The rclpy
``URMLActionServerNode`` shell is a thin wrapper over this core and is exercised
only by the gated ``flexbe-integration`` workflow on a real ROS 2 host.

Coverage:
- program path executes successfully against the mock;
- natural-language path translates (echo) then executes;
- refusal path: a program with an undeclared location is rejected by the
  validator, ``refused=True``, and NOTHING actuates (adapter call log empty);
- a missing provider on an NL goal refuses cleanly;
- the feedback sink receives the phase events.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from urml_llm_bridge import EchoProvider

from urml_ros2_runtime import MockROSAdapter
from urml_ros2_runtime.action_server import ExecuteRequest, execute_request

REPO_ROOT = Path(__file__).resolve().parents[3]
FLEXBE = REPO_ROOT / "examples" / "flexbe"


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _manifest() -> dict[str, Any]:
    return _load(FLEXBE / "turtle.manifest.yaml")


def _program() -> dict[str, Any]:
    return _load(FLEXBE / "turtle-patrol.urml.yaml")


def test_program_path_executes_against_mock() -> None:
    adapter = MockROSAdapter()
    req = ExecuteRequest(
        manifest=_manifest(),
        program=_program(),
        profiles=("home",),
        no_policy=True,
    )
    out = execute_request(req, adapter=adapter)

    assert out["success"] is True
    assert out["refused"] is False
    assert out["steps_executed"] == 3
    assert len(adapter.call_log) == 3  # three move_to dispatches


def test_natural_language_path_translates_then_executes() -> None:
    adapter = MockROSAdapter()
    sentence = "Patrol the two waypoints, then come home."
    emission = (FLEXBE / "turtle-patrol.echo-response.json").read_text(encoding="utf-8")
    # The bridge feeds provider.complete(user=sentence); echo returns the program.
    provider = EchoProvider(responses={sentence: json.dumps(json.loads(emission))})

    req = ExecuteRequest(
        manifest=_manifest(),
        sentence=sentence,
        profiles=("home",),
        no_policy=True,
    )
    out = execute_request(req, adapter=adapter, provider=provider)

    assert out["success"] is True
    assert out["refused"] is False
    assert out["steps_executed"] == 3


def test_refusal_does_not_actuate() -> None:
    adapter = MockROSAdapter()
    bad = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"move_to": {"location": "nowhere_undeclared"}}],
        },
    }
    req = ExecuteRequest(manifest=_manifest(), program=bad, profiles=("home",), no_policy=True)
    out = execute_request(req, adapter=adapter)

    assert out["refused"] is True
    assert out["success"] is False
    assert "refused" in out["reason"]
    assert adapter.call_log == []  # the safety boundary held: no actuation


def test_nl_without_provider_refuses_cleanly() -> None:
    adapter = MockROSAdapter()
    req = ExecuteRequest(manifest=_manifest(), sentence="go somewhere", profiles=("home",))
    out = execute_request(req, adapter=adapter, provider=None)

    assert out["refused"] is True
    assert "provider" in out["reason"]
    assert adapter.call_log == []


def test_feedback_sink_receives_phases() -> None:
    adapter = MockROSAdapter()
    events: list[dict[str, Any]] = []
    req = ExecuteRequest(manifest=_manifest(), program=_program(), profiles=("home",), no_policy=True)
    execute_request(req, adapter=adapter, feedback=events.append)

    phases = [e["phase"] for e in events]
    assert "validating" in phases
    assert "executing" in phases
    assert phases[-1] == "done"
