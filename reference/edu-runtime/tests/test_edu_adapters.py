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


class _FakeMarty:
    """Stand-in for ``martypy.Marty`` with the skill methods + sensor getters
    the URML adapter dispatches against.
    """

    def __init__(self, device: str) -> None:
        self.device = device
        self.calls: list[str] = []

    def walk(self) -> None:
        self.calls.append("walk")

    def sit(self) -> None:
        self.calls.append("sit")

    def kick(self) -> None:
        self.calls.append("kick")

    def open_claw(self) -> None:
        self.calls.append("open_claw")

    def close_claw(self) -> None:
        self.calls.append("close_claw")

    def get_battery_voltage(self) -> float:
        return 7.2

    def get_accelerometer(self) -> float:
        return 0.98

    def disconnect(self) -> None:
        pass


@pytest.fixture
def fake_edu_sdks() -> Iterator[None]:
    vex = ModuleType("pyvex")
    vex.Brain = _FakeVexBrain  # type: ignore[attr-defined]
    lego = ModuleType("pybricksdev")
    lego.connect = lambda dev: _FakeLegoHub(dev)  # type: ignore[attr-defined]
    thy = ModuleType("tdmclient")
    thy.Client = _FakeThymio  # type: ignore[attr-defined]
    mar = ModuleType("martypy")
    mar.Marty = _FakeMarty  # type: ignore[attr-defined]
    keys = ("pyvex", "pybricksdev", "tdmclient", "martypy")
    saved = {k: sys.modules.get(k) for k in keys}
    sys.modules["pyvex"] = vex
    sys.modules["pybricksdev"] = lego
    sys.modules["tdmclient"] = thy
    sys.modules["martypy"] = mar
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


def test_marty_adapter_lifecycle(fake_edu_sdks: None) -> None:
    """RoboticalMartyAdapter dispatches URML primitives to ``martypy`` skill methods.

    Location names map to martypy skill method names per the maintainer's
    response on robotical/martypy#52 (2026-05-25). v2 default transport is
    USB serial; v1 is socket; both pass through ``EduConfig.device``.
    """
    from urml_edu_runtime import EduConfig, RoboticalMartyAdapter

    cfg = EduConfig(
        device="usb",
        location_to_command={"start_mat": "walk", "rest_mat": "sit"},
        manipulation_commands={"grasp": "close_claw", "release": "open_claw"},
    )
    with RoboticalMartyAdapter(cfg) as marty:
        assert isinstance(marty, ROSAdapter)
        assert marty.send_navigation_goal(location="start_mat").success
        assert marty.send_navigation_goal(location="rest_mat").success
        miss = marty.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        assert marty.send_manipulation_goal(action="grasp").success
        assert marty.send_manipulation_goal(action="release").success
        # Sensor getter must exist on the martypy.Marty instance.
        meas = marty.take_measurement(what="battery", target=None, sensor="get_battery_voltage")
        assert meas.success and meas.payload is not None and meas.payload["value"] == 7.2
        # Unknown sensor returns a typed failure, not a crash.
        bad = marty.take_measurement(what="nope", target=None, sensor="get_no_such_thing")
        assert bad.success is False and bad.reason is not None
        assert bad.reason.startswith("marty_sensor_not_found")


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
    from urml_edu_runtime import (
        EduConfig,
        LegoSpikeAdapter,
        RoboticalMartyAdapter,
        ThymioAdapter,
        VexV5Adapter,
    )

    cfg = EduConfig(location_to_command={"x": "GO X"})
    for mod in ("pyvex", "pybricksdev", "tdmclient", "martypy"):
        monkeypatch.setitem(sys.modules, mod, None)
    with pytest.raises(RuntimeError, match=r"\[vex\] extra"):
        VexV5Adapter(cfg).send_navigation_goal(location="x")
    with pytest.raises(RuntimeError, match=r"\[lego\] extra"):
        LegoSpikeAdapter(cfg).send_navigation_goal(location="x")
    with pytest.raises(RuntimeError, match=r"\[thymio\] extra"):
        ThymioAdapter(cfg).send_navigation_goal(location="x")
    with pytest.raises(RuntimeError, match=r"\[marty\] extra"):
        RoboticalMartyAdapter(cfg).send_navigation_goal(location="x")


def test_conformance_runner_accepts_factories(fake_edu_sdks: None) -> None:
    from urml_conformance import ConformanceRunner

    from urml_edu_runtime import LegoSpikeAdapter, RoboticalMartyAdapter, ThymioAdapter, VexV5Adapter

    assert ConformanceRunner(adapter_factory=lambda: VexV5Adapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: LegoSpikeAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: ThymioAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: RoboticalMartyAdapter()) is not None
