"""Hermetic unit tests for OpcUaAdapter — no asyncua install needed.

A fake ``asyncua.sync`` module is injected into ``sys.modules`` so
``_require_asyncua`` resolves and ``_connect`` runs against a
controllable double (the same technique px4/marine/mujoco use).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import DetectionResult, ROSAdapter


class _FakeNode:
    def __init__(self, store: dict[str, Any]) -> None:
        self._store = store

    def call_method(self, method: str, *args: Any) -> str:
        self._store.setdefault("calls", []).append((method, args))
        return "ok"

    def read_value(self) -> float:
        return 7.0


class _FakeClient:
    def __init__(self, url: str, timeout: float = 5.0) -> None:
        self.url = url
        self.connected = False
        self.disconnected = False
        self.store: dict[str, Any] = {}

    def connect(self) -> None:
        self.connected = True

    def disconnect(self) -> None:
        self.disconnected = True

    def get_node(self, nodeid: str) -> _FakeNode:
        return _FakeNode(self.store)


@pytest.fixture
def fake_asyncua() -> Iterator[type[_FakeClient]]:
    sync_mod = ModuleType("asyncua.sync")
    sync_mod.Client = _FakeClient  # type: ignore[attr-defined]
    pkg = ModuleType("asyncua")
    pkg.sync = sync_mod  # type: ignore[attr-defined]
    saved = {k: sys.modules.get(k) for k in ("asyncua", "asyncua.sync")}
    sys.modules["asyncua"] = pkg
    sys.modules["asyncua.sync"] = sync_mod
    try:
        yield _FakeClient
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def test_nav_dock_grasp_measure_lifecycle(fake_asyncua: type[_FakeClient]) -> None:
    from urml_opcua_runtime import OpcUaAdapter, OpcUaConfig
    from urml_opcua_runtime.adapter import MethodTarget

    cfg = OpcUaConfig(
        location_to_method={"pick_bin": MethodTarget(method="ns=2;s=MoveTo", args=["pick_bin"])},
        service_to_method={"swap_tool": MethodTarget(method="ns=2;s=SwapTool", args=["wide"])},
        manipulation_methods={"grasp": MethodTarget(method="ns=2;s=Grip")},
        measurement_node="ns=2;s=Force",
        program_to_method={"pick_place_cycle": MethodTarget(method="ns=2;s=PickPlaceCycle")},
    )
    with OpcUaAdapter(cfg) as cell:
        assert isinstance(cell, ROSAdapter)
        assert cell.send_navigation_goal(location="pick_bin").success
        miss = cell.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        # RFC-0013 swap_tool rides send_docking_goal — preserved.
        assert cell.send_docking_goal(station="tool_change_station", service="swap_tool", until="wide").success
        assert cell.send_manipulation_goal(action="grasp").success
        # RFC-0015 call_program -> OPC UA method node (the motivating case).
        prog = cell.call_named_program(name="pick_place_cycle")
        assert prog.success and prog.payload == {"value": "ok"}
        meas = cell.take_measurement(what="force", target=None, sensor="tcp_force")
        assert meas.success and meas.payload is not None and meas.payload["value"] == 7.0
        assert cell.wait_passively(duration_seconds=0.1).success
        assert cell.run_scan(
            area={}, pattern="grid", overlap=0.1, altitude=None, media="sensor_only", sensor=None
        ).success  # documented stub


def test_unconfigured_and_unsupported_sentinels(fake_asyncua: type[_FakeClient]) -> None:
    from urml_opcua_runtime import OpcUaAdapter, OpcUaConfig

    cell = OpcUaAdapter(OpcUaConfig())
    nores = cell.send_manipulation_goal(action="grasp")
    assert nores.success is False
    assert nores.reason is not None and nores.reason.startswith("manipulation_method_not_configured")
    det: DetectionResult = cell.query_detection(object_class="widget")
    assert det.success is False and det.reason is not None
    assert det.reason.startswith("not_supported_on_opcua_cell")
    prog = cell.call_named_program(name="unmapped_program")
    assert prog.success is False and prog.reason is not None
    assert prog.reason.startswith("program_not_configured")
    for r in (cell.send_takeoff_goal(altitude=1.0), cell.send_land_goal(), cell.send_return_to_home_goal()):
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_applicable_opcua")


def test_missing_asyncua_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Construction without the [opcua] extra raises a clear error.

    Setting the sys.modules entries to None forces ``import asyncua.sync``
    to raise ImportError deterministically, whether or not asyncua is
    actually installed in the test environment.
    """
    from urml_opcua_runtime import OpcUaAdapter

    monkeypatch.setitem(sys.modules, "asyncua", None)
    monkeypatch.setitem(sys.modules, "asyncua.sync", None)
    with pytest.raises(RuntimeError, match=r"\[opcua\] extra"):
        OpcUaAdapter()


def test_conformance_runner_accepts_factory(fake_asyncua: type[_FakeClient]) -> None:
    from urml_conformance import ConformanceRunner

    from urml_opcua_runtime import OpcUaAdapter

    assert ConformanceRunner(adapter_factory=lambda: OpcUaAdapter()) is not None
