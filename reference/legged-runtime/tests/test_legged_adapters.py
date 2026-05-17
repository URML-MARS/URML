"""Hermetic unit tests for the legged adapters — no bosdyn / ROS 2 install.

SpotAdapter: a fake ``bosdyn`` package is injected into ``sys.modules``
so ``_require_bosdyn`` resolves and ``_connect`` runs against a
controllable double (the same technique px4-runtime uses for pymavlink).

AnymalAdapter: a recording fake inner adapter is injected via the
``inner_factory`` hook (the industrial-arm technique) so the delegation
and not-supported paths are exercised without rclpy.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import (
    ManipulationResult,
    NavigationResult,
    ROSAdapter,
    SubstrateResult,
)

# ---------------------------------------------------------------------------
# Fake bosdyn
# ---------------------------------------------------------------------------


class _FakeGraphNav:
    def __init__(self) -> None:
        self.calls: list[Any] = []

    def navigate_to(self, waypoint: Any) -> None:
        self.calls.append(("navigate_to", waypoint))

    def navigate_to_anchor(self, pose: Any) -> None:
        self.calls.append(("navigate_to_anchor", pose))


class _FakeRobot:
    def __init__(self) -> None:
        self.powered_off = False
        self.authed: tuple[str, str] | None = None
        self.time_sync = SimpleNamespace(wait_for_sync=lambda: None)
        self._clients: dict[str, Any] = {
            "graph-nav": _FakeGraphNav(),
            "docking": SimpleNamespace(dock=lambda station: None),
            "robot-command": SimpleNamespace(stand=lambda duration_seconds=0.0: None),
            "robot-state": SimpleNamespace(
                get_robot_state=lambda: SimpleNamespace(battery_percentage=87.0)
            ),
        }

    def authenticate(self, username: str, password: str) -> None:
        self.authed = (username, password)

    def ensure_client(self, name: str) -> Any:
        return self._clients[name]

    def power_off(self, cut_immediately: bool = False) -> None:
        self.powered_off = True


class _FakeSdk:
    def __init__(self) -> None:
        self.robot = _FakeRobot()

    def create_robot(self, hostname: str) -> _FakeRobot:
        return self.robot


@pytest.fixture
def fake_bosdyn() -> Iterator[_FakeSdk]:
    sdk = _FakeSdk()
    client_mod = ModuleType("bosdyn.client")
    client_mod.create_standard_sdk = lambda name: sdk  # type: ignore[attr-defined]
    pkg = ModuleType("bosdyn")
    pkg.client = client_mod  # type: ignore[attr-defined]
    saved = {k: sys.modules.get(k) for k in ("bosdyn", "bosdyn.client")}
    sys.modules["bosdyn"] = pkg
    sys.modules["bosdyn.client"] = client_mod
    try:
        yield sdk
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


# ---------------------------------------------------------------------------
# SpotAdapter
# ---------------------------------------------------------------------------


def test_spot_navigation_and_lifecycle(fake_bosdyn: _FakeSdk) -> None:
    from urml_legged_runtime import SpotAdapter, SpotConfig

    cfg = SpotConfig(location_to_waypoint={"dock_a": "wp-12"})
    with SpotAdapter(cfg) as spot:
        assert isinstance(spot, ROSAdapter)
        ok = spot.send_navigation_goal(location="dock_a")
        assert ok.success
        miss = spot.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        assert spot.send_docking_goal(station="dock_a", service="park").success
        assert spot.wait_passively(duration_seconds=0.1).success
        meas = spot.take_measurement(what="battery", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 87.0
        assert spot.run_scan(
            area={}, pattern="grid", overlap=0.1, altitude=None, media="photo", sensor=None
        ).success  # documented stub success
    assert fake_bosdyn.robot.powered_off is True


def test_spot_unsupported_returns_sentinel(fake_bosdyn: _FakeSdk) -> None:
    from urml_legged_runtime import SpotAdapter

    spot = SpotAdapter()
    results = [
        spot.send_manipulation_goal(action="grasp"),
        spot.query_detection(object_class="x"),
        spot.capture_media(media="photo", target=None, duration_seconds=None, attributes=None),
        spot.emit_speech(utterance="hi", locale=None, style="notice", interrupt=False),
        spot.acquire_speech(prompt=None, locale=None, timeout_seconds=None, expected="free_form", choices=None),
        spot.send_takeoff_goal(altitude=2.0),
        spot.send_land_goal(),
        spot.send_return_to_home_goal(),
    ]
    for r in results:
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_supported_on_spot")


def test_spot_missing_bosdyn_is_actionable() -> None:
    """Without the [spot] extra, construction raises a clear error."""
    from urml_legged_runtime import SpotAdapter

    sys.modules.pop("bosdyn", None)
    sys.modules.pop("bosdyn.client", None)
    with pytest.raises(RuntimeError, match=r"\[spot\] extra"):
        SpotAdapter()


# ---------------------------------------------------------------------------
# AnymalAdapter
# ---------------------------------------------------------------------------


class _RecordingInner:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.closed = False

    def send_navigation_goal(self, **kw: Any) -> NavigationResult:
        self.calls.append("send_navigation_goal")
        return NavigationResult(success=True, frame="odom")

    def take_measurement(self, **kw: Any) -> SubstrateResult:
        self.calls.append("take_measurement")
        return SubstrateResult(success=True)

    def wait_for_condition(self, **kw: Any) -> SubstrateResult:
        self.calls.append("wait_for_condition")
        return SubstrateResult(success=True)

    def wait_passively(self, **kw: Any) -> SubstrateResult:
        self.calls.append("wait_passively")
        return SubstrateResult(success=True)

    def emit_report(self, **kw: Any) -> SubstrateResult:
        self.calls.append("emit_report")
        return SubstrateResult(success=True)

    def close(self) -> None:
        self.closed = True


def test_anymal_delegates_and_rejects() -> None:
    from urml_legged_runtime import AnymalAdapter

    inner = _RecordingInner()
    with AnymalAdapter(inner_factory=lambda: inner) as anymal:
        assert isinstance(anymal, ROSAdapter)
        assert anymal.send_navigation_goal(location="valve_07").success
        assert anymal.wait_passively(duration_seconds=0.1).success
        assert anymal.emit_report(
            to="site_log", facts={}, attachments=None, status="success", severity="info"
        ).success
        bad: ManipulationResult = anymal.send_manipulation_goal(action="grasp")
        assert bad.success is False
        assert bad.reason is not None and bad.reason.startswith("not_supported_on_quadruped[anymal]")
        assert anymal.send_takeoff_goal(altitude=1.0).success is False
    assert inner.calls == ["send_navigation_goal", "wait_passively", "emit_report"]
    assert inner.closed is True


def test_conformance_runner_accepts_legged_factories(fake_bosdyn: _FakeSdk) -> None:
    from urml_conformance import ConformanceRunner

    from urml_legged_runtime import AnymalAdapter, SpotAdapter

    assert ConformanceRunner(adapter_factory=lambda: SpotAdapter()) is not None
    assert ConformanceRunner(
        adapter_factory=lambda: AnymalAdapter(inner_factory=lambda: _RecordingInner())
    ) is not None
