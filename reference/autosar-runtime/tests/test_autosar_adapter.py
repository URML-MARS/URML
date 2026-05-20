"""Hermetic unit tests for AutosarAdaptiveAdapter — no ara install needed.

A fake ``ara.sync`` module is injected into ``sys.modules`` so
``_require_ara`` resolves and ``_connect`` runs against a
controllable double (the same technique px4/marine/mujoco use).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import DetectionResult, ROSAdapter


class _FakeAraInstance:
    def __init__(self, store: dict[str, Any]) -> None:
        self._store = store

    def call_method(self, method: str, *args: Any) -> str:
        self._store.setdefault("calls", []).append((method, args))
        return "ok"

    def read_value(self) -> float:
        return 7.0


class _FakeAraSession:
    def __init__(self, url: str, timeout: float = 5.0) -> None:
        self.url = url
        self.connected = False
        self.disconnected = False
        self.store: dict[str, Any] = {}

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.disconnected = True

    def get_node(self, nodeid: str) -> _FakeAraInstance:
        return _FakeAraInstance(self.store)


@pytest.fixture
def fake_ara() -> Iterator[type[_FakeAraSession]]:
    sync_mod = ModuleType("ara.sync")
    sync_mod.Client = _FakeAraSession  # type: ignore[attr-defined]
    pkg = ModuleType("ara")
    pkg.sync = sync_mod  # type: ignore[attr-defined]
    saved = {k: sys.modules.get(k) for k in ("ara", "ara.sync")}
    sys.modules["ara"] = pkg
    sys.modules["ara.sync"] = sync_mod
    try:
        yield _FakeAraSession
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def test_nav_dock_grasp_measure_lifecycle(fake_ara: type[_FakeAraSession]) -> None:
    from urml_autosar_runtime import AutosarAdaptiveAdapter, AutosarConfig
    from urml_autosar_runtime.adapter import MethodTarget

    cfg = AutosarConfig(
        location_to_method={"pick_bin": MethodTarget(method="sid=MoveTo", args=["pick_bin"])},
        service_to_method={"swap_tool": MethodTarget(method="sid=SwapTool", args=["wide"])},
        manipulation_methods={"grasp": MethodTarget(method="sid=Grip")},
        measurement_node="sid=Force",
    )
    with AutosarAdaptiveAdapter(cfg) as cell:
        assert isinstance(cell, ROSAdapter)
        assert cell.send_navigation_goal(location="pick_bin").success
        miss = cell.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        # RFC-0013 swap_tool rides send_docking_goal — preserved.
        assert cell.send_docking_goal(station="tool_change_station", service="swap_tool", until="wide").success
        assert cell.send_manipulation_goal(action="grasp").success
        meas = cell.take_measurement(what="force", target=None, sensor="tcp_force")
        assert meas.success and meas.payload is not None and meas.payload["value"] == 7.0
        assert cell.wait_passively(duration_seconds=0.1).success
        assert cell.run_scan(
            area={}, pattern="grid", overlap=0.1, altitude=None, media="sensor_only", sensor=None
        ).success  # documented stub


def test_unconfigured_and_unsupported_sentinels(fake_ara: type[_FakeAraSession]) -> None:
    from urml_autosar_runtime import AutosarAdaptiveAdapter, AutosarConfig

    cell = AutosarAdaptiveAdapter(AutosarConfig())
    nores = cell.send_manipulation_goal(action="grasp")
    assert nores.success is False
    assert nores.reason is not None and nores.reason.startswith("manipulation_method_not_configured")
    det: DetectionResult = cell.query_detection(object_class="widget")
    assert det.success is False and det.reason is not None
    assert det.reason.startswith("not_supported_on_autosar_ecu_cell")
    for r in (cell.send_takeoff_goal(altitude=1.0), cell.send_land_goal(), cell.send_return_to_home_goal()):
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_applicable_autosar")


def test_missing_ara_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Construction without the [autosar] extra raises a clear error.

    Setting the sys.modules entries to None forces ``import ara.sync``
    to raise ImportError deterministically, whether or not ara is
    actually installed in the test environment.
    """
    from urml_autosar_runtime import AutosarAdaptiveAdapter

    monkeypatch.setitem(sys.modules, "ara", None)
    monkeypatch.setitem(sys.modules, "ara.sync", None)
    with pytest.raises(RuntimeError, match=r"\[autosar\] extra"):
        AutosarAdaptiveAdapter()


def test_conformance_runner_accepts_factory(fake_ara: type[_FakeAraSession]) -> None:
    from urml_conformance import ConformanceRunner

    from urml_autosar_runtime import AutosarAdaptiveAdapter

    assert ConformanceRunner(adapter_factory=lambda: AutosarAdaptiveAdapter()) is not None
