"""Hermetic unit tests for the cobot adapters — no vendor SDK needed.

Fake ``rtde_control`` / ``rtde_receive`` / ``panda_py`` modules are
injected into ``sys.modules`` so the lazy imports resolve and
``_open`` runs against controllable doubles (the technique
px4/marine/opcua use).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import DetectionResult, ROSAdapter


class _FakeRtdeControl:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.moves: list[Any] = []

    def moveL(self, vec: Any, speed: float) -> bool:  # noqa: N802
        self.moves.append((vec, speed))
        return True

    def stopScript(self) -> None:  # noqa: N802
        pass


class _FakeRtdeReceive:
    def __init__(self, ip: str) -> None:
        self.ip = ip

    def getActualTCPForce(self) -> list[float]:  # noqa: N802
        return [12.5, 0.0, 0.0, 0.0, 0.0, 0.0]


class _FakePanda:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.moved: list[Any] = []

    def move_to_joint_position(self, vec: Any) -> None:
        self.moved.append(vec)

    def get_state(self) -> Any:
        return SimpleNamespace(O_F_ext_hat_K=[3.3, 0.0, 0.0])

    def disconnect(self) -> None:
        pass


class _FakeDoosanRobot:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.moves: list[Any] = []

    def movel(self, vec: Any, speed: float) -> None:
        self.moves.append((vec, speed))

    def get_tool_force(self) -> list[float]:
        return [9.1, 0.0, 0.0, 0.0, 0.0, 0.0]

    def disconnect(self) -> None:
        pass


class _FakeTechmanClient:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.moves: list[Any] = []

    def move_to_point_line(self, vec: Any, speed: float) -> None:
        self.moves.append((vec, speed))

    def get_tcp_force(self) -> list[float]:
        return [4.4, 0.0, 0.0, 0.0, 0.0, 0.0]

    def disconnect(self) -> None:
        pass


class _FakeKinovaBase:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.poses: list[Any] = []

    def send_pose_command(self, vec: Any, speed: float) -> None:
        self.poses.append((vec, speed))

    def get_tool_external_wrench(self) -> list[float]:
        return [6.6, 0.0, 0.0, 0.0, 0.0, 0.0]

    def disconnect(self) -> None:
        pass


class _FakeMecademicRobot:
    def __init__(self) -> None:
        self.ip: str | None = None
        self.poses: list[Any] = []
        self._joints = [0.5, 0.0, 0.0, 0.0, 0.0, 0.0]

    def Connect(self, ip: str) -> None:  # noqa: N802 — vendor SDK casing
        self.ip = ip

    def MovePose(self, *vec: float) -> None:  # noqa: N802
        self.poses.append(vec)

    def GetJoints(self) -> list[float]:  # noqa: N802
        return self._joints

    def disconnect(self) -> None:
        pass


class _FakeNeuraRobot:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.moves: list[Any] = []

    def move_joint(self, vec: Any, speed: float) -> None:
        self.moves.append((vec, speed))

    def get_tcp_wrench(self) -> list[float]:
        return [2.2, 0.0, 0.0, 0.0, 0.0, 0.0]

    def disconnect(self) -> None:
        pass


class _FakeKassowClient:
    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.moves: list[Any] = []

    def movej(self, vec: Any, speed: float) -> None:
        self.moves.append((vec, speed))

    def get_tcp_wrench(self) -> list[float]:
        return [7.7, 0.0, 0.0, 0.0, 0.0, 0.0]

    def disconnect(self) -> None:
        pass


@pytest.fixture
def fake_sdks() -> Iterator[None]:
    rc = ModuleType("rtde_control")
    rc.RTDEControlInterface = _FakeRtdeControl  # type: ignore[attr-defined]
    rr = ModuleType("rtde_receive")
    rr.RTDEReceiveInterface = _FakeRtdeReceive  # type: ignore[attr-defined]
    pp = ModuleType("panda_py")
    pp.Panda = _FakePanda  # type: ignore[attr-defined]
    drfl = ModuleType("DRFL")
    drfl.Robot = _FakeDoosanRobot  # type: ignore[attr-defined]
    tm = ModuleType("techmanpy")
    tm.connect_sct = lambda ip: _FakeTechmanClient(ip)  # type: ignore[attr-defined]
    kx = ModuleType("kortex_api")
    kx.BaseClient = _FakeKinovaBase  # type: ignore[attr-defined]
    # Mecademic ships as `mecademicpy.robot.Robot` — recreate the subpath.
    mec_pkg = ModuleType("mecademicpy")
    mec_robot = ModuleType("mecademicpy.robot")
    mec_robot.Robot = _FakeMecademicRobot  # type: ignore[attr-defined]
    mec_pkg.robot = mec_robot  # type: ignore[attr-defined]
    # Neura ships as `neurapy.robot.Robot` — recreate the subpath.
    neura_pkg = ModuleType("neurapy")
    neura_robot = ModuleType("neurapy.robot")
    neura_robot.Robot = _FakeNeuraRobot  # type: ignore[attr-defined]
    neura_pkg.robot = neura_robot  # type: ignore[attr-defined]
    # Kassow ships as `kassow_py.client.KassowClient` — recreate the subpath.
    kassow_pkg = ModuleType("kassow_py")
    kassow_client = ModuleType("kassow_py.client")
    kassow_client.KassowClient = _FakeKassowClient  # type: ignore[attr-defined]
    kassow_pkg.client = kassow_client  # type: ignore[attr-defined]
    keys = (
        "rtde_control",
        "rtde_receive",
        "panda_py",
        "DRFL",
        "techmanpy",
        "kortex_api",
        "mecademicpy",
        "mecademicpy.robot",
        "neurapy",
        "neurapy.robot",
        "kassow_py",
        "kassow_py.client",
    )
    saved = {k: sys.modules.get(k) for k in keys}
    sys.modules["rtde_control"] = rc
    sys.modules["rtde_receive"] = rr
    sys.modules["panda_py"] = pp
    sys.modules["DRFL"] = drfl
    sys.modules["techmanpy"] = tm
    sys.modules["kortex_api"] = kx
    sys.modules["mecademicpy"] = mec_pkg
    sys.modules["mecademicpy.robot"] = mec_robot
    sys.modules["neurapy"] = neura_pkg
    sys.modules["neurapy.robot"] = neura_robot
    sys.modules["kassow_py"] = kassow_pkg
    sys.modules["kassow_py.client"] = kassow_client
    try:
        yield
    finally:
        for k in keys:
            if saved[k] is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = saved[k]


def test_ur_adapter_lifecycle(fake_sdks: None) -> None:
    from urml_cobot_runtime import CobotConfig, UrRtdeAdapter
    from urml_cobot_runtime.adapter import Pose

    cfg = CobotConfig(location_to_pose={"pick": Pose(vector=[0.4, -0.3, 0.1, 0.0, 3.14, 0.0])})
    with UrRtdeAdapter(cfg) as ur:
        assert isinstance(ur, ROSAdapter)
        ok = ur.send_navigation_goal(location="pick")
        assert ok.success and ok.final_pose is not None and ok.final_pose["q0"] == 0.4
        miss = ur.send_navigation_goal(location="nope")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        assert ur.send_manipulation_goal(action="grasp", force_n=10.0).success
        meas = ur.take_measurement(what="tcp_force", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 12.5
        assert ur.run_scan(
            area={}, pattern="grid", overlap=0.1, altitude=None, media="sensor_only", sensor=None
        ).success


def test_franka_adapter_lifecycle(fake_sdks: None) -> None:
    from urml_cobot_runtime import CobotConfig, FrankaFciAdapter
    from urml_cobot_runtime.adapter import Pose

    cfg = CobotConfig(location_to_pose={"home": Pose(vector=[0.0, -0.78, 0.0, -2.35, 0.0, 1.57, 0.78])})
    with FrankaFciAdapter(cfg) as fr:
        assert isinstance(fr, ROSAdapter)
        assert fr.send_navigation_goal(location="home").success
        assert fr.send_manipulation_goal(action="release").success
        meas = fr.take_measurement(what="ext_force", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 3.3


def test_doosan_adapter_lifecycle(fake_sdks: None) -> None:
    from urml_cobot_runtime import CobotConfig, DoosanDrflAdapter
    from urml_cobot_runtime.adapter import Pose

    cfg = CobotConfig(location_to_pose={"pick": Pose(vector=[0.4, -0.3, 0.1, 0.0, 3.14, 0.0])})
    with DoosanDrflAdapter(cfg) as dr:
        assert isinstance(dr, ROSAdapter)
        assert dr.send_navigation_goal(location="pick").success
        assert dr.send_manipulation_goal(action="grasp", force_n=8.0).success
        meas = dr.take_measurement(what="tcp_force", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 9.1


def test_techman_adapter_lifecycle(fake_sdks: None) -> None:
    from urml_cobot_runtime import CobotConfig, TechmanTmflowAdapter
    from urml_cobot_runtime.adapter import Pose

    cfg = CobotConfig(location_to_pose={"pick": Pose(vector=[0.4, -0.3, 0.1, 0.0, 3.14, 0.0])})
    with TechmanTmflowAdapter(cfg) as tm:
        assert isinstance(tm, ROSAdapter)
        assert tm.send_navigation_goal(location="pick").success
        assert tm.send_manipulation_goal(action="release").success
        meas = tm.take_measurement(what="tcp_force", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 4.4


def test_kinova_adapter_lifecycle(fake_sdks: None) -> None:
    from urml_cobot_runtime import CobotConfig, KinovaKortexAdapter
    from urml_cobot_runtime.adapter import Pose

    cfg = CobotConfig(location_to_pose={"home": Pose(vector=[0.0, 0.0, 0.5, 0.0, 0.0, 0.0])})
    with KinovaKortexAdapter(cfg) as kx:
        assert isinstance(kx, ROSAdapter)
        assert kx.send_navigation_goal(location="home").success
        assert kx.send_manipulation_goal(action="grasp").success
        meas = kx.take_measurement(what="ext_wrench", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 6.6


def test_mecademic_adapter_lifecycle(fake_sdks: None) -> None:
    from urml_cobot_runtime import CobotConfig, MecademicMeca500Adapter
    from urml_cobot_runtime.adapter import Pose

    cfg = CobotConfig(location_to_pose={"pick": Pose(vector=[100.0, 0.0, 200.0, 0.0, 90.0, 0.0])})
    with MecademicMeca500Adapter(cfg) as mc:
        assert isinstance(mc, ROSAdapter)
        assert mc.send_navigation_goal(location="pick").success
        assert mc.send_manipulation_goal(action="release").success
        meas = mc.take_measurement(what="joint_state", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 0.5


def test_neura_adapter_lifecycle(fake_sdks: None) -> None:
    from urml_cobot_runtime import CobotConfig, NeuraMairaAdapter
    from urml_cobot_runtime.adapter import Pose

    cfg = CobotConfig(location_to_pose={"pick": Pose(vector=[0.4, -0.3, 0.1, 0.0, 3.14, 0.0])})
    with NeuraMairaAdapter(cfg) as nu:
        assert isinstance(nu, ROSAdapter)
        assert nu.send_navigation_goal(location="pick").success
        assert nu.send_manipulation_goal(action="grasp", force_n=5.0).success
        meas = nu.take_measurement(what="tcp_wrench", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 2.2


def test_kassow_adapter_lifecycle(fake_sdks: None) -> None:
    from urml_cobot_runtime import CobotConfig, KassowKrAdapter
    from urml_cobot_runtime.adapter import Pose

    cfg = CobotConfig(location_to_pose={"home": Pose(vector=[0.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0])})
    with KassowKrAdapter(cfg) as ks:
        assert isinstance(ks, ROSAdapter)
        assert ks.send_navigation_goal(location="home").success
        assert ks.send_manipulation_goal(action="release").success
        meas = ks.take_measurement(what="tcp_wrench", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 7.7


def test_unsupported_and_not_applicable_sentinels(fake_sdks: None) -> None:
    from urml_cobot_runtime import UrRtdeAdapter

    ur = UrRtdeAdapter()
    dock = ur.send_docking_goal(station="x", service="swap_tool")
    assert dock.success is False and dock.reason is not None
    assert dock.reason.startswith("not_supported_on_bare_cobot")
    det: DetectionResult = ur.query_detection(object_class="widget")
    assert det.success is False
    for r in (ur.send_takeoff_goal(altitude=1.0), ur.send_land_goal(), ur.send_return_to_home_goal()):
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_applicable_cobot")


def test_missing_extras_are_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Construction is cheap; the clear error fires on first use without the extra."""
    from urml_cobot_runtime import (
        DoosanDrflAdapter,
        FrankaFciAdapter,
        KassowKrAdapter,
        KinovaKortexAdapter,
        MecademicMeca500Adapter,
        NeuraMairaAdapter,
        TechmanTmflowAdapter,
        UrRtdeAdapter,
    )

    for mod in (
        "rtde_control",
        "rtde_receive",
        "panda_py",
        "DRFL",
        "techmanpy",
        "kortex_api",
        "mecademicpy",
        "mecademicpy.robot",
        "neurapy",
        "neurapy.robot",
        "kassow_py",
        "kassow_py.client",
    ):
        monkeypatch.setitem(sys.modules, mod, None)
    with pytest.raises(RuntimeError, match=r"\[ur\] extra"):
        UrRtdeAdapter().send_navigation_goal(pose={"x": 0.0})
    with pytest.raises(RuntimeError, match=r"\[franka\] extra"):
        FrankaFciAdapter().send_navigation_goal(pose={"x": 0.0})
    with pytest.raises(RuntimeError, match=r"\[doosan\] extra"):
        DoosanDrflAdapter().send_navigation_goal(pose={"x": 0.0})
    with pytest.raises(RuntimeError, match=r"\[techman\] extra"):
        TechmanTmflowAdapter().send_navigation_goal(pose={"x": 0.0})
    with pytest.raises(RuntimeError, match=r"\[kinova\] extra"):
        KinovaKortexAdapter().send_navigation_goal(pose={"x": 0.0})
    with pytest.raises(RuntimeError, match=r"\[mecademic\] extra"):
        MecademicMeca500Adapter().send_navigation_goal(pose={"x": 0.0})
    with pytest.raises(RuntimeError, match=r"\[neura\] extra"):
        NeuraMairaAdapter().send_navigation_goal(pose={"x": 0.0})
    with pytest.raises(RuntimeError, match=r"\[kassow\] extra"):
        KassowKrAdapter().send_navigation_goal(pose={"x": 0.0})


def test_conformance_runner_accepts_factories(fake_sdks: None) -> None:
    from urml_conformance import ConformanceRunner

    from urml_cobot_runtime import (
        DoosanDrflAdapter,
        FrankaFciAdapter,
        KassowKrAdapter,
        KinovaKortexAdapter,
        MecademicMeca500Adapter,
        NeuraMairaAdapter,
        TechmanTmflowAdapter,
        UrRtdeAdapter,
    )

    assert ConformanceRunner(adapter_factory=lambda: UrRtdeAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: FrankaFciAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: DoosanDrflAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: TechmanTmflowAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: KinovaKortexAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: MecademicMeca500Adapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: NeuraMairaAdapter()) is not None
    assert ConformanceRunner(adapter_factory=lambda: KassowKrAdapter()) is not None
