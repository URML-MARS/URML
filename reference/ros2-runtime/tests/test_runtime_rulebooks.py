"""The runtimes and the action server under rulebooks (RFC-0702, Draft).

URMLRuntime and FleetRuntime re-validate with the same rulebooks, default
switch and validation date the caller used, so a runtime re-check never drops
a rulebook. The action server takes rulebooks from its operator only: a goal
has no field for them.
"""

from __future__ import annotations

import copy
import datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from urml_ros2_runtime import FleetRuntime, MockROSAdapter, URMLRuntime, ValidationRejectedError
from urml_ros2_runtime.action_server import (
    ExecuteRequest,
    PinnedConstraints,
    execute_request,
    load_pinned,
    request_from_goal,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"
EXAMPLE_RULEBOOKS = REPO_ROOT / "examples" / "rulebooks"
DRONE_PATH = FIXTURES / "manifests" / "drone_high_ceiling.yaml"
WAIVER_PATH = EXAMPLE_RULEBOOKS / "example-deployment.yaml"


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _flight(altitude: float) -> dict[str, Any]:
    return {
        "profile": "drone",
        "behavior": {"type": "sequence", "steps": [{"take_off": {"altitude": altitude}}, {"land": {}}]},
    }


def test_the_runtime_refuses_a_450_foot_take_off_before_any_adapter_call() -> None:
    adapter = MockROSAdapter()
    with pytest.raises(ValidationRejectedError) as exc:
        URMLRuntime(adapter).execute(_flight(137.16), _load(DRONE_PATH), policy=None)
    assert exc.value.validation_result.has("rule.cap_exceeded")
    assert adapter.call_log == []


def test_the_runtime_applies_the_callers_rulebooks_and_date() -> None:
    adapter = MockROSAdapter()
    result = URMLRuntime(adapter).execute(
        _flight(137.16), _load(DRONE_PATH), policy=None,
        rulebooks=[_load(WAIVER_PATH)], as_of=datetime.date(2026, 9, 26),
    )
    assert result.success and [c["method"] for c in adapter.call_log] == ["send_takeoff_goal", "send_land_goal"]
    with pytest.raises(ValidationRejectedError):
        URMLRuntime(MockROSAdapter()).execute(
            _flight(137.16), _load(DRONE_PATH), policy=None,
            rulebooks=[_load(WAIVER_PATH)], as_of=datetime.date(2027, 4, 1),
        )


def test_the_runtime_honors_the_default_switch() -> None:
    result = URMLRuntime(MockROSAdapter()).execute(
        _flight(137.16), _load(DRONE_PATH), policy=None, default_rulebooks=False
    )
    assert result.success


def test_the_fleet_runtime_judges_concurrency_and_takes_the_same_keywords() -> None:
    drone = _load(FIXTURES / "manifests" / "utm_drone.yaml")
    roster = {"members": [{"name": "a", "manifest": "utm_drone"}, {"name": "b", "manifest": "utm_drone"}]}
    members = {"a": copy.deepcopy(drone), "b": copy.deepcopy(drone)}
    program = {
        "profile": "drone",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"type": "on", "member": "a", "body": {"take_off": {"altitude": 10.0}}},
                {"type": "on", "member": "b", "body": {"take_off": {"altitude": 20.0}}},
            ],
        },
    }
    adapters = {"a": MockROSAdapter(), "b": MockROSAdapter()}
    with pytest.raises(ValidationRejectedError) as exc:
        FleetRuntime(adapters, sequential=True).execute(roster, members, program, policy=None)
    assert exc.value.validation_result.has("rule.concurrency_exceeded")
    assert all(adapter.call_log == [] for adapter in adapters.values())
    result = FleetRuntime(adapters, sequential=True).execute(
        roster, members, program, policy=None, default_rulebooks=False
    )
    assert result.success


# ---------------------------------------------------------------------------
# The action server: rulebooks are operator configuration only
# ---------------------------------------------------------------------------


def test_a_goal_has_no_field_for_rulebooks() -> None:
    class _Goal:
        manifest_yaml = ""
        envelope_yaml = ""
        program_yaml = "profile: drone\nbehavior: {take_off: {altitude: 10.0}}\n"
        sentence = ""
        profiles: list[str] = []
        no_policy = False
        rulebooks = "a deployment rulebook an agent wrote"  # ignored: not a goal field

    request = request_from_goal(_Goal())
    assert not hasattr(request, "rulebooks") and not hasattr(request, "default_rulebooks")
    with pytest.raises(TypeError):
        ExecuteRequest(program={}, rulebooks=[{}])  # type: ignore[call-arg]


def test_an_unpinned_server_applies_the_bundled_rulebooks() -> None:
    adapter = MockROSAdapter()
    request = ExecuteRequest(manifest=_load(DRONE_PATH), program=_flight(137.16), profiles=("drone",), no_policy=True)
    out = execute_request(request, adapter=adapter)
    assert out["refused"] is True and "rule.cap_exceeded" in out["reason"]
    assert adapter.call_log == []


def test_pinned_rulebooks_apply_to_the_check_and_the_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    import urml_ros2_runtime.action_server as action_server

    seen: list[dict[str, Any]] = []
    real = action_server.URMLRuntime

    class _Spy(real):  # type: ignore[misc,valid-type]
        def execute(self, *args: Any, **kwargs: Any) -> Any:
            seen.append(kwargs)
            return super().execute(*args, **kwargs)

    monkeypatch.setattr(action_server, "URMLRuntime", _Spy)
    pinned = PinnedConstraints(manifest=_load(DRONE_PATH), policy=None, default_rulebooks=False)
    out = execute_request(ExecuteRequest(program=_flight(137.16), profiles=("drone",)), adapter=MockROSAdapter(), pinned=pinned)
    assert out["success"] is True
    (kwargs,) = seen
    assert kwargs["default_rulebooks"] is False and kwargs["rulebooks"] == () and kwargs["as_of"] is not None

    warehouse_rules = _load(EXAMPLE_RULEBOOKS / "example-warehouse.yaml")
    pinned = PinnedConstraints(manifest=_load(FIXTURES / "manifests" / "warehouse_areas.yaml"), policy=None, rulebooks=(warehouse_rules,))
    program = {"profile": "warehouse", "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "server_room"}}]}}
    adapter = MockROSAdapter()
    out = execute_request(ExecuteRequest(program=program, profiles=("warehouse",)), adapter=adapter, pinned=pinned)
    assert out["refused"] is True and "rule.zone_forbidden" in out["reason"]
    assert adapter.call_log == []


def test_load_pinned_reads_and_checks_rulebook_files(tmp_path: Path) -> None:
    pinned = load_pinned(str(DRONE_PATH), "", "none", [str(WAIVER_PATH), ""], False)
    assert pinned is not None
    assert [book["rulebook_id"] for book in pinned.rulebooks] == ["example_aerial_survey_north_tower"]
    assert pinned.default_rulebooks is False
    assert load_pinned(str(DRONE_PATH), "", "").rulebooks == ()  # type: ignore[union-attr]
    with pytest.raises(ValueError, match="does not follow the rulebook format"):
        load_pinned(str(DRONE_PATH), "", "", [str(EXAMPLE_RULEBOOKS / "industrial-template.yaml")])
    with pytest.raises(ValueError, match="not found"):
        load_pinned(str(DRONE_PATH), "", "", [str(tmp_path / "missing.yaml")])


@pytest.mark.parametrize(
    ("paths", "defaults"),
    [([str(WAIVER_PATH)], True), ([], False)],
    ids=["rulebooks", "default_switch"],
)
def test_rulebook_settings_need_a_pinned_manifest(paths: list[str], defaults: bool) -> None:
    with pytest.raises(ValueError, match="pinned together with manifest_path"):
        load_pinned("", "", "", paths, defaults)
