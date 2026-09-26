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

import pytest
import yaml
from urml_llm_bridge import EchoProvider

from urml_ros2_runtime import MockROSAdapter
from urml_ros2_runtime.action_server import (
    ExecuteRequest,
    PinnedConstraints,
    execute_request,
    load_pinned,
    request_from_goal,
    require_pinned_for_adapter,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FLEXBE = REPO_ROOT / "examples" / "flexbe"
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"


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


# ---------------------------------------------------------------------------
# The runtime re-validates with the goal's policy (no revalidate=False)
# ---------------------------------------------------------------------------


def test_runtime_revalidates_with_the_chosen_policy(monkeypatch: pytest.MonkeyPatch) -> None:
    import urml_ros2_runtime.action_server as action_server

    seen: list[tuple[str, dict[str, Any]]] = []
    real = action_server.URMLRuntime

    class _Spy(real):  # type: ignore[misc,valid-type]
        def __init__(self, adapter: Any, **kwargs: Any) -> None:
            seen.append(("init", kwargs))
            super().__init__(adapter, **kwargs)

        def execute(self, *args: Any, **kwargs: Any) -> Any:
            seen.append(("execute", kwargs))
            return super().execute(*args, **kwargs)

    monkeypatch.setattr(action_server, "URMLRuntime", _Spy)
    req = ExecuteRequest(manifest=_manifest(), program=_program(), profiles=("home",), no_policy=True)
    out = execute_request(req, adapter=MockROSAdapter())
    assert out["success"] is True
    calls = dict(seen)
    assert calls["init"].get("revalidate", True) is True
    assert calls["execute"]["policy"] is None


# ---------------------------------------------------------------------------
# Pinned deployment constraints: the goal cannot choose its own limits
# ---------------------------------------------------------------------------


def _pinned(**overrides: Any) -> PinnedConstraints:
    fields: dict[str, Any] = {
        "manifest": _manifest(),
        "envelope": {"envelope_version": "0.1", "deployment_id": "test", "max_velocity": 0.8},
        "policy": None,
    }
    fields.update(overrides)
    return PinnedConstraints(**fields)


@pytest.mark.parametrize(
    ("goal_fields", "named"),
    [
        ({"manifest": {"robot_id": "anything"}}, "manifest_yaml"),
        ({"envelope": {"max_velocity": 99.0}}, "envelope_yaml"),
        ({"no_policy": True}, "no_policy"),
    ],
)
def test_pinned_server_refuses_a_goal_that_sets_constraints(
    goal_fields: dict[str, Any], named: str
) -> None:
    adapter = MockROSAdapter()
    req = ExecuteRequest(program=_program(), profiles=("home",), **goal_fields)
    out = execute_request(req, adapter=adapter, pinned=_pinned())
    assert out["refused"] is True
    assert named in out["reason"]
    assert adapter.call_log == []


def test_pinned_refusal_comes_before_translation() -> None:
    """A pinned server refuses the goal before any provider or adapter call."""
    adapter = MockROSAdapter()
    sentence = "Patrol the two waypoints, then come home."
    emission = (FLEXBE / "turtle-patrol.echo-response.json").read_text(encoding="utf-8")
    provider = EchoProvider(responses={sentence: emission})
    req = ExecuteRequest(manifest=_manifest(), sentence=sentence, profiles=("home",))
    out = execute_request(req, adapter=adapter, provider=provider, pinned=_pinned())
    assert out["refused"] is True
    assert provider.call_log == []
    assert adapter.call_log == []


def test_pinned_goal_runs_under_the_pinned_constraints() -> None:
    adapter = MockROSAdapter()
    req = ExecuteRequest(program=_program(), profiles=("home",))
    out = execute_request(req, adapter=adapter, pinned=_pinned())
    assert out["success"] is True, out["reason"]
    assert out["steps_executed"] == 3


def test_pinned_natural_language_goal_runs_under_the_pinned_constraints() -> None:
    adapter = MockROSAdapter()
    sentence = "Patrol the two waypoints, then come home."
    emission = (FLEXBE / "turtle-patrol.echo-response.json").read_text(encoding="utf-8")
    provider = EchoProvider(responses={sentence: emission})
    req = ExecuteRequest(sentence=sentence, profiles=("home",))
    out = execute_request(req, adapter=adapter, provider=provider, pinned=_pinned())
    assert out["success"] is True, out["reason"]
    assert len(provider.call_log) == 1


def test_pinned_envelope_is_enforced() -> None:
    adapter = MockROSAdapter()
    fast = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "steps": [{"move_to": {"location": "waypoint_a", "speed": 0.5}}],
        },
    }
    pinned = _pinned(envelope={"envelope_version": "0.1", "deployment_id": "t", "max_velocity": 0.1})
    out = execute_request(ExecuteRequest(program=fast, profiles=("home",)), adapter=adapter, pinned=pinned)
    assert out["refused"] is True
    assert "envelope.velocity_exceeded" in out["reason"]
    assert adapter.call_log == []


def test_pinned_policy_and_manifest_dir_are_enforced() -> None:
    """The pinned HBOM policy reads the HBOM next to the pinned manifest."""
    manifests = VALIDATOR_FIXTURES / "manifests"
    pinned = PinnedConstraints(
        manifest=_load(manifests / "provenance_hbom_cn_chip.yaml"),
        envelope=None,
        policy=_load(VALIDATOR_FIXTURES / "policies" / "hbom_no_cn_components.yaml"),
        manifest_base_dir=manifests,
    )
    program = {
        "profile": "home",
        "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "kitchen"}}]},
    }
    adapter = MockROSAdapter()
    out = execute_request(ExecuteRequest(program=program, profiles=("home",)), adapter=adapter, pinned=pinned)
    assert out["refused"] is True
    assert "policy.hbom_component_country_denied" in out["reason"]
    assert adapter.call_log == []


# ---------------------------------------------------------------------------
# Node support: node parameters -> PinnedConstraints, startup rule, goal parsing
# (the rclpy node calls these; they are tested here without ROS 2)
# ---------------------------------------------------------------------------


def test_load_pinned_is_none_when_nothing_is_pinned() -> None:
    assert load_pinned("", "", "") is None


def test_load_pinned_reads_the_example_files() -> None:
    manifest_path = FLEXBE / "turtle.manifest.yaml"
    pinned = load_pinned(str(manifest_path), str(FLEXBE / "turtle.envelope.yaml"), "")
    assert pinned is not None
    assert pinned.manifest == _manifest()
    assert pinned.envelope is not None and pinned.envelope["max_velocity"] > 0
    assert pinned.policy == "DEFAULT"
    assert pinned.manifest_base_dir == manifest_path.parent


def test_load_pinned_policy_path_forms() -> None:
    manifest = str(FLEXBE / "turtle.manifest.yaml")
    no_policy = load_pinned(manifest, "", "none")
    assert no_policy is not None and no_policy.policy is None
    policy_file = VALIDATOR_FIXTURES / "policies" / "permissive.yaml"
    custom = load_pinned(manifest, "", str(policy_file))
    assert custom is not None and custom.policy == _load(policy_file)


def test_load_pinned_needs_the_manifest_for_any_pin() -> None:
    with pytest.raises(ValueError, match="manifest_path"):
        load_pinned("", str(FLEXBE / "turtle.envelope.yaml"), "")
    with pytest.raises(ValueError, match="manifest_path"):
        load_pinned("", "", "none")


def test_load_pinned_rejects_missing_or_malformed_files(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not found"):
        load_pinned(str(tmp_path / "missing.yaml"), "", "")
    not_a_mapping = tmp_path / "list.yaml"
    not_a_mapping.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(ValueError, match="mapping"):
        load_pinned(str(not_a_mapping), "", "")


def test_real_adapter_needs_a_pinned_manifest_and_envelope() -> None:
    with pytest.raises(RuntimeError, match="manifest_path"):
        require_pinned_for_adapter("ros2", None)
    with pytest.raises(RuntimeError, match="envelope_path"):
        require_pinned_for_adapter("ros2", PinnedConstraints(manifest=_manifest()))
    require_pinned_for_adapter("ros2", _pinned())  # manifest + envelope: starts
    require_pinned_for_adapter("mock", None)  # the mock moves nothing: starts


class _Goal:
    """Stand-in for the generated ExecuteURML.Goal (same field names)."""

    def __init__(self, **fields: Any) -> None:
        self.program_yaml = ""
        self.sentence = ""
        self.manifest_yaml = ""
        self.envelope_yaml = ""
        self.profiles = ["home"]
        self.no_policy = False
        for key, value in fields.items():
            setattr(self, key, value)


def test_request_from_goal_blank_fields_are_unset() -> None:
    program_yaml = (FLEXBE / "turtle-patrol.urml.yaml").read_text(encoding="utf-8")
    req = request_from_goal(_Goal(program_yaml=program_yaml, manifest_yaml="  \n"))
    assert req.manifest is None and req.envelope is None and req.no_policy is False
    assert req.program == _program()
    assert req.profiles == ("home",)


def test_request_from_goal_counts_a_non_mapping_field_as_set() -> None:
    """A pinned server refuses a goal that sets manifest_yaml, even to garbage."""
    req = request_from_goal(_Goal(program_yaml="{}", manifest_yaml="- not\n- a mapping\n"))
    assert req.manifest == {}
    adapter = MockROSAdapter()
    out = execute_request(req, adapter=adapter, pinned=_pinned())
    assert out["refused"] is True and "manifest_yaml" in out["reason"]
    assert adapter.call_log == []


def test_pinned_example_goal_runs_end_to_end() -> None:
    """The FlexBE worked example, minus ROS 2: files pinned, goal sends the program only."""
    pinned = load_pinned(
        str(FLEXBE / "turtle.manifest.yaml"), str(FLEXBE / "turtle.envelope.yaml"), ""
    )
    program_yaml = (FLEXBE / "turtle-patrol.urml.yaml").read_text(encoding="utf-8")
    adapter = MockROSAdapter()
    out = execute_request(
        request_from_goal(_Goal(program_yaml=program_yaml)), adapter=adapter, pinned=pinned
    )
    assert out["success"] is True, out["reason"]
    assert len(adapter.call_log) == 3


def test_pinned_ur3e_example_goal_runs_end_to_end() -> None:
    pinned = load_pinned(
        str(FLEXBE / "ur3e.manifest.yaml"), str(FLEXBE / "ur3e.envelope.yaml"), ""
    )
    program_yaml = (FLEXBE / "ur3e-pick-place.urml.yaml").read_text(encoding="utf-8")
    out = execute_request(
        request_from_goal(_Goal(program_yaml=program_yaml, profiles=["industrial"])),
        adapter=MockROSAdapter(),
        pinned=pinned,
    )
    assert out["success"] is True, out["reason"]
