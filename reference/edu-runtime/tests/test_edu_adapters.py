"""Hermetic unit tests for the educational-platform adapters.

No vendor SDK install required. Fake pyvex / pybricksdev / tdmclient
modules are injected into ``sys.modules`` so the lazy imports resolve
and ``_open`` runs against controllable doubles.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import DetectionResult, ROSAdapter


class _FakeVexBrain:
    def __init__(self, device: str) -> None:
        self.device = device
        self.commands: list[str] = []

    def run_command(self, cmd: str) -> None:
        self.commands.append(cmd)

    def read_sensor(self, name: str) -> float:
        return 17.5

    def disconnect(self) -> None:
        pass


class _FakeLegoHub:
    def __init__(self, device: str) -> None:
        self.device = device
        self.commands: list[str] = []

    def send_command(self, cmd: str) -> None:
        self.commands.append(cmd)

    def read_sensor(self, name: str) -> float:
        return 33.0

    def disconnect(self) -> None:
        pass


class _FakeThymio:
    def __init__(self, device: str) -> None:
        self.device = device
        self.events: list[str] = []

    def send_event(self, cmd: str) -> None:
        self.events.append(cmd)

    def read_variable(self, name: str) -> float:
        return 7.0

    def close(self) -> None:
        pass


@pytest.fixture
def fake_edu_sdks() -> Iterator[None]:
    vex = ModuleType("pyvex")
    vex.Brain = _FakeVexBrain  # type: ignore[attr-defined]
    lego = ModuleType("pybricksdev")
    lego.connect = lambda dev: _FakeLegoHub(dev)  # type: ignore[attr-defined]
    thy = ModuleType("tdmclient")
    thy.Client = _FakeThymio  # type: ignore[attr-defined]
    keys = ("pyvex", "pybricksdev", "tdmclient")
    saved = {k: sys.modules.get(k) for k in keys}
    sys.modules["pyvex"] = vex
    sys.modules["pybricksdev"] = lego
    sys.modules["tdmclient"] = thy
    try:
        yield
    finally:
        for k in keys:
            if saved[k] is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = saved[k]


def test_vex_adapter_lifecycle(fake_edu_sdks: None) -> None:
    from urml_edu_runtime import EduConfig, VexV5Adapter

    cfg = EduConfig(
        location_to_command={"start_mat": "GO START", "waypoint_a": "GO A"},
        manipulation_commands={"grasp": "CLAW C", "release": "CLAW O"},
    )
    with VexV5Adapter(cfg) as vex:
        assert isinstance(vex, ROSAdapter)
        assert vex.send_navigation_goal(location="start_mat").success
        miss = vex.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        assert vex.send_manipulation_goal(action="grasp", force_n=2.0).success
        meas = vex.take_measurement(what="light", target=None, sensor="light_sensor")
        assert meas.success and meas.payload is not None and meas.payload["value"] == 17.5
        assert vex.run_scan(
            area={}, pattern="grid", overlap=0.1, altitude=None, media="sensor_only", sensor=None
        ).success


def test_lego_adapter_lifecycle(fake_edu_sdks: None) -> None:
    from urml_edu_runtime import EduConfig, LegoSpikeAdapter

    cfg = EduConfig(
        location_to_command={"start_mat": "drive_forward", "home_mat": "drive_home"},
        manipulation_commands={"grasp": "claw_close"},
    )
    with LegoSpikeAdapter(cfg) as hub:
        assert isinstance(hub, ROSAdapter)
        assert hub.send_navigation_goal(location="start_mat").success
        assert hub.send_manipulation_goal(action="grasp").success
        meas = hub.take_measurement(what="distance", target=None, sensor="ultrasonic")
        assert meas.success and meas.payload is not None and meas.payload["value"] == 33.0


def test_thymio_adapter_lifecycle(fake_edu_sdks: None) -> None:
    from urml_edu_runtime import EduConfig, ThymioAdapter

    cfg = EduConfig(
        location_to_command={"start_mat": "go_start"},
        manipulation_commands={"release": "open_claw"},
    )
    with ThymioAdapter(cfg) as thy:
        assert isinstance(thy, ROSAdapter)
        assert thy.send_navigation_goal(location="start_mat").success
        assert thy.send_manipulation_goal(action="release").success
        meas = thy.take_measurement(what="prox", target=None, sensor="prox.horizontal[0]")
        assert meas.success and meas.payload is not None and meas.payload["value"] == 7.0


def test_unsupported_and_not_applicable_sentinels(fake_edu_sdks: None) -> None:
    from urml_edu_runtime import VexV5Adapter

    vex = VexV5Adapter()
    det: DetectionResult = vex.query_detection(object_class="ball")
    assert det.success is False and det.reason is not None
    assert det.reason.startswith("not_supported_on_edu_platform")
    nores = vex.send_manipulation_goal(action="grasp")
    assert nores.success is False and nores.reason is not None
    assert nores.reason.startswith("manipulation_command_not_configured")
    for r in (vex.send_takeoff_goal(altitude=1.0), vex.send_land_goal(), vex.send_return_to_home_goal()):
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_applicable_edu")


def test_missing_extras_are_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each adapter raises an actionable error naming its [extra] when SDK missing.

    The lazy ``_open()`` only fires when a Protocol method *actually* needs
    the connection; an unmapped location short-circuits before the import
    attempt. So the test config maps the location so ``_send`` runs.
    """
    from urml_edu_runtime import EduConfig, LegoSpikeAdapter, ThymioAdapter, VexV5Adapter

    cfg = EduConfig(location_to_command={"x": "GO X"})
    for mod in ("pyvex", "pybricksdev", "tdmclient"):
        monkeypatch.setitem(sys.modules, mod, None)
    with pytest.raises(RuntimeError, match=r"\[vex\] extra"):
        VexV5Adapter(cfg).send_navigation_goal(location="x")
    with pytest.raises(RuntimeError, match=r"\[lego\] extra"):
        LegoSpikeAdapter(cfg).send_navigation_goal(location="x")
    with pytest.raises(RuntimeError, match=r"\[thymio\] extra"):
        ThymioAdapter(cfg).send_navigation_goal(location="x")


def test_conformance_runner_accepts_factories(fake_edu_sdks: None) -> None:
    from urml_conformance import ConformanceRunner

    from urml_edu_runtime import LegoSpikeAdapter, ThymioAdapter, VexV5Adapter

    assert ConformanceRunner(adapter_factory=lambda: VexV5Adapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: LegoSpikeAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: ThymioAdapter()) is not None
