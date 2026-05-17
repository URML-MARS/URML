"""Hermetic unit tests for BlueRovAdapter — no pymavlink install needed.

A fake ``pymavlink`` package is injected into ``sys.modules`` so
``_require_pymavlink`` resolves and ``_connect`` runs against a
controllable double (the same technique px4-runtime uses).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import ManipulationResult, NavigationResult, ROSAdapter


class _FakeMav:
    def __init__(self) -> None:
        self.sent: list[tuple[Any, ...]] = []

    def set_position_target_local_ned_send(self, *args: Any) -> None:
        self.sent.append(args)


class _FakeConn:
    def __init__(self) -> None:
        self.target_system = 1
        self.target_component = 1
        self.mav = _FakeMav()
        self.closed = False

    def wait_heartbeat(self, timeout: float = 0.0) -> object:
        return object()

    def recv_match(self, **kw: Any) -> Any:
        return SimpleNamespace(press_abs=1013.0, battery_remaining=88.0)

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def fake_pymavlink() -> Iterator[_FakeConn]:
    conn = _FakeConn()
    mavutil = ModuleType("pymavlink.mavutil")
    mavutil.mavlink_connection = lambda url, source_system=255, source_component=1: conn  # type: ignore[attr-defined]
    pkg = ModuleType("pymavlink")
    pkg.mavutil = mavutil  # type: ignore[attr-defined]
    saved = {k: sys.modules.get(k) for k in ("pymavlink", "pymavlink.mavutil")}
    sys.modules["pymavlink"] = pkg
    sys.modules["pymavlink.mavutil"] = mavutil
    try:
        yield conn
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def test_navigation_measure_scan_lifecycle(fake_pymavlink: _FakeConn) -> None:
    from urml_marine_runtime import BlueRovAdapter, MarineConfig
    from urml_marine_runtime.adapter import Waypoint

    cfg = MarineConfig(location_to_waypoint={"reef_a": Waypoint(north=10.0, east=2.0, depth=5.0)})
    with BlueRovAdapter(cfg) as rov:
        assert isinstance(rov, ROSAdapter)
        ok = rov.send_navigation_goal(location="reef_a")
        assert ok.success and ok.final_pose == {"north": 10.0, "east": 2.0, "depth": 5.0}
        assert fake_pymavlink.mav.sent, "a position-target MAVLink message was sent"
        miss = rov.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        assert rov.wait_passively(duration_seconds=0.1).success
        meas = rov.take_measurement(what="depth", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 1013.0
        assert rov.run_scan(
            area={}, pattern="serpentine", overlap=0.1, altitude=None, media="sensor_only", sensor=None
        ).success  # documented stub success
    assert fake_pymavlink.closed is True


def test_unsupported_and_underwater_sentinels(fake_pymavlink: _FakeConn) -> None:
    from urml_marine_runtime import BlueRovAdapter

    rov = BlueRovAdapter()
    bare: ManipulationResult = rov.send_manipulation_goal(action="grasp")
    assert bare.success is False
    assert bare.reason is not None and bare.reason.startswith("not_supported_on_bare_rov")
    for r in (rov.send_takeoff_goal(altitude=1.0), rov.send_land_goal(), rov.send_return_to_home_goal()):
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_applicable_underwater")


def test_missing_pymavlink_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Construction without the [marine] extra raises a clear error.

    Setting the sys.modules entry to None forces ``import pymavlink`` to
    raise ImportError deterministically, whether or not pymavlink is
    actually installed in the test environment.
    """
    from urml_marine_runtime import BlueRovAdapter

    monkeypatch.setitem(sys.modules, "pymavlink", None)
    monkeypatch.setitem(sys.modules, "pymavlink.mavutil", None)
    with pytest.raises(RuntimeError, match=r"\[marine\] extra"):
        BlueRovAdapter()


def test_conformance_runner_accepts_factory(fake_pymavlink: _FakeConn) -> None:
    from urml_conformance import ConformanceRunner

    from urml_marine_runtime import BlueRovAdapter

    assert ConformanceRunner(adapter_factory=lambda: BlueRovAdapter()) is not None
