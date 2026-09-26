"""A fraction speed reaches the adapter in m/s, never as a raw fraction.

Layer 2 lets `move_to` and `drive` state speed as a fraction of the manifest
maximum (`{value: 0.9, units: fraction}`). Every `ROSAdapter` speed argument is
in m/s. The runtime used to forward `.value` whatever the units, so 0.9 of
cobot_cell's 0.25 m/s reached the adapter as 0.9 m/s, 3.6x the declared
maximum. These tests pin the lowering: the adapter receives value x
`manifest.mobility.max_velocity`, the substrate default (None) when the maximum
is unknown, and nothing at all when the fraction is outside 0..1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml
from urml_validator.schemas.common import Speed
from urml_validator.schemas.composition import Step
from urml_validator.schemas.primitives import DriveArgs, MoveToArgs

from urml_ros2_runtime import FleetRuntime, MockROSAdapter, URMLRuntime
from urml_ros2_runtime.primitives import (
    exec_drive,
    exec_move_to,
    execute_step,
    manifest_max_velocity,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFESTS = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures" / "manifests"


def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    assert isinstance(data, dict)
    return data


def _move_program(location: str, speed: Any) -> dict[str, Any]:
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"move_to": {"location": location, "speed": speed}}],
        },
    }


def _nav_speeds(adapter: MockROSAdapter) -> list[Any]:
    return [e["speed"] for e in adapter.call_log if e["method"] == "send_navigation_goal"]


_BUGGY: dict[str, Any] = {
    "manifest_version": "0.1",
    "robot_id": "buggy",
    "frames": [{"name": "floor", "parent": None}],
    "mobility": {
        "drive_type": "differential",
        "max_velocity": 0.3,
        "supports_relative_motion": True,
        "max_relative_distance": 2.0,
    },
}


# ---------------------------------------------------------------------------
# Through the runtime (the shipped path)
# ---------------------------------------------------------------------------


def test_cobot_fraction_reaches_the_adapter_in_mps() -> None:
    """The verified hole: 0.9 of cobot_cell's 0.25 m/s must arrive as 0.225 m/s."""
    manifest = _load(MANIFESTS / "cobot_cell.yaml")
    program = _move_program("pick_bin", {"value": 0.9, "units": "fraction"})
    program["profile"] = "industrial"
    adapter = MockROSAdapter()
    result = URMLRuntime(adapter).execute(program, manifest, None, ("industrial",), policy=None)
    assert result.success is True, result.audit_log
    assert _nav_speeds(adapter) == [pytest.approx(0.9 * 0.25)]
    assert _nav_speeds(adapter)[0] <= manifest["mobility"]["max_velocity"]


def test_home_fraction_is_value_times_manifest_max() -> None:
    manifest = _load(MANIFESTS / "turtlebot4_home.yaml")
    max_v = manifest["mobility"]["max_velocity"]
    adapter = MockROSAdapter()
    URMLRuntime(adapter).execute(
        _move_program("kitchen", {"value": 0.5, "units": "fraction"}),
        manifest,
        None,
        ("home",),
        policy=None,
    )
    assert _nav_speeds(adapter) == [pytest.approx(0.5 * max_v)]


def test_absolute_speeds_pass_through_unchanged() -> None:
    manifest = _load(MANIFESTS / "turtlebot4_home.yaml")
    adapter = MockROSAdapter()
    runtime = URMLRuntime(adapter)
    runtime.execute(
        _move_program("kitchen", {"value": 0.2, "units": "m_per_s"}), manifest, None, ("home",), policy=None
    )
    runtime.execute(_move_program("kitchen", 0.2), manifest, None, ("home",), policy=None)
    runtime.execute(_move_program("kitchen", None), manifest, None, ("home",), policy=None)
    assert _nav_speeds(adapter) == [0.2, 0.2, None]


def test_drive_fraction_is_lowered() -> None:
    program = {
        "profile": ["educational"],
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"drive": {"distance": 0.5, "speed": {"value": 0.5, "units": "fraction"}}}],
        },
    }
    adapter = MockROSAdapter()
    result = URMLRuntime(adapter).execute(program, _BUGGY, None, ("educational",), policy=None)
    assert result.success is True, result.audit_log
    drive = next(e for e in adapter.call_log if e["method"] == "drive_by")
    assert drive["speed"] == pytest.approx(0.5 * 0.3)


def test_fleet_fraction_uses_the_member_manifest() -> None:
    """Each fleet member's fraction is lowered against that member's own maximum."""
    fast = {
        "robot_id": "fast",
        "frames": [{"name": "map"}],
        "declared_locations": [{"name": "dock", "pose": {"x": 1.0, "y": 0.0}, "frame": "map"}],
        "mobility": {"drive_type": "differential", "max_velocity": 1.5},
    }
    slow = {**fast, "robot_id": "slow", "mobility": {"drive_type": "differential", "max_velocity": 0.4}}
    roster = {
        "roster_version": "0.1",
        "members": [{"name": "fast", "manifest": "fast"}, {"name": "slow", "manifest": "slow"}],
    }
    half = {"value": 0.5, "units": "fraction"}
    program = {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "steps": [
                {"type": "on", "member": "fast", "body": {"move_to": {"location": "dock", "speed": half}}},
                {"type": "on", "member": "slow", "body": {"move_to": {"location": "dock", "speed": half}}},
            ],
        },
    }
    adapters = {"fast": MockROSAdapter(), "slow": MockROSAdapter()}
    result = FleetRuntime(adapters, sequential=True).execute(
        roster, {"fast": fast, "slow": slow}, program, policy=None
    )
    assert result.success is True, result.per_member_audit
    assert _nav_speeds(adapters["fast"]) == [pytest.approx(0.75)]
    assert _nav_speeds(adapters["slow"]) == [pytest.approx(0.2)]


# ---------------------------------------------------------------------------
# At dispatch (execute_step and the executors themselves)
# ---------------------------------------------------------------------------


def _move_step(speed: Any) -> Step:
    return Step.model_validate({"move_to": {"location": "kitchen", "speed": speed}})


def test_unknown_maximum_sends_the_substrate_default() -> None:
    """No declared maximum: the adapter gets None, never the fraction itself."""
    adapter = MockROSAdapter()
    outcome = execute_step(_move_step({"value": 0.9, "units": "fraction"}), adapter, {})
    assert outcome.success is True
    assert _nav_speeds(adapter) == [None]


@pytest.mark.parametrize("value", [1.5, -0.2])
def test_fraction_outside_zero_to_one_is_refused_before_the_adapter(value: float) -> None:
    adapter = MockROSAdapter()
    outcome = execute_step(
        _move_step({"value": value, "units": "fraction"}), adapter, {}, max_velocity=0.25
    )
    assert outcome.success is False
    assert outcome.reason is not None and "fraction" in outcome.reason
    assert adapter.call_log == []


def test_executors_never_forward_a_raw_fraction() -> None:
    """A direct executor call with an un-lowered fraction sends None, not the value."""
    adapter = MockROSAdapter()
    exec_move_to(
        MoveToArgs(location="kitchen", speed=Speed(value=0.9, units="fraction")), adapter, {}
    )
    exec_drive(DriveArgs(distance=0.5, speed=Speed(value=0.9, units="fraction")), adapter, {})
    assert [e["speed"] for e in adapter.call_log] == [None, None]


def test_manifest_max_velocity_reads_dicts_and_models() -> None:
    from urml_validator.schemas.manifest import CapabilityManifest

    raw = _load(MANIFESTS / "cobot_cell.yaml")
    assert manifest_max_velocity(raw) == 0.25
    assert manifest_max_velocity(CapabilityManifest.model_validate(raw)) == 0.25
    assert manifest_max_velocity({"robot_id": "no_mobility"}) is None
    assert manifest_max_velocity({"mobility": {"max_velocity": "fast"}}) is None
