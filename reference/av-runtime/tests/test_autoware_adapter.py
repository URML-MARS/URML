"""Hermetic unit tests for AutowareAdapter — no ROS 2 / Autoware install.

Fake ``rclpy`` and the Autoware message packages (``geometry_msgs.msg``,
``autoware_adapi_v1_msgs.srv``, ``tier4_planning_msgs.msg``) are injected into
``sys.modules`` so the adapter's lazy imports resolve against controllable
doubles. The fakes implement only the slice the adapter touches; real Autoware
behavior is verified separately on a Linux + Autoware host.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Iterator
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import TrajectoryAdapter

# --------------------------------------------------------------------------
# Fakes
# --------------------------------------------------------------------------


class _FakeFuture:
    def __init__(self, value: Any) -> None:
        self._value = value

    def result(self) -> Any:
        return self._value


class _FakeClient:
    # Test-level controls, reset by the fixture.
    available: bool = True
    success_by_service: dict[str, bool] = {}  # noqa: RUF012
    calls: list[dict[str, Any]] = []  # noqa: RUF012

    def __init__(self, _srv_type: Any, service_name: str) -> None:
        self.service_name = service_name

    def wait_for_service(self, *, timeout_sec: float) -> bool:
        return _FakeClient.available

    def call_async(self, request: Any) -> _FakeFuture:
        _FakeClient.calls.append({"service": self.service_name, "request": request})
        ok = _FakeClient.success_by_service.get(self.service_name, True)
        response = SimpleNamespace(status=SimpleNamespace(success=ok, message="" if ok else "declined"))
        return _FakeFuture(response)


class _FakePublisher:
    published: list[dict[str, Any]] = []  # noqa: RUF012

    def __init__(self, topic: str) -> None:
        self.topic = topic

    def publish(self, msg: Any) -> None:
        _FakePublisher.published.append({"topic": self.topic, "msg": msg})


class _FakeClock:
    def now(self) -> Any:
        return SimpleNamespace(to_msg=lambda: SimpleNamespace())


class _FakeNode:
    def __init__(self, name: str, namespace: str = "") -> None:
        self.name = name
        self.namespace = namespace
        self.destroyed = False

    def create_client(self, srv_type: Any, service_name: str) -> _FakeClient:
        return _FakeClient(srv_type, service_name)

    def create_publisher(self, _msg_type: Any, topic: str, _qos: int) -> _FakePublisher:
        return _FakePublisher(topic)

    def get_clock(self) -> _FakeClock:
        return _FakeClock()

    def destroy_node(self) -> None:
        self.destroyed = True


# ROS message doubles ------------------------------------------------------


class _Pose:
    def __init__(self) -> None:
        self.position = SimpleNamespace(x=0.0, y=0.0, z=0.0)
        self.orientation = SimpleNamespace(x=0.0, y=0.0, z=0.0, w=1.0)


class _Header:
    def __init__(self) -> None:
        self.frame_id = ""
        self.stamp = None


class _SetRoutePointsRequest:
    def __init__(self) -> None:
        self.header = _Header()
        self.goal = None
        self.waypoints: list[Any] = []


class _SetRoutePoints:
    Request = _SetRoutePointsRequest


class _EmptyRequest:
    pass


class _ClearRoute:
    Request = _EmptyRequest


class _ChangeOperationMode:
    Request = _EmptyRequest


class _VelocityLimit:
    def __init__(self) -> None:
        self.stamp = None
        self.max_velocity = 0.0


def _make_module(name: str, **attrs: Any) -> ModuleType:
    mod = ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


@pytest.fixture
def fake_ros() -> Iterator[None]:
    _FakeClient.available = True
    _FakeClient.success_by_service = {}
    _FakeClient.calls = []
    _FakePublisher.published = []

    rclpy = _make_module(
        "rclpy",
        create_node=lambda name, namespace="": _FakeNode(name, namespace),
        spin_until_future_complete=lambda _node, _future, timeout_sec=None: None,
    )
    geometry = _make_module("geometry_msgs")
    geometry_msg = _make_module("geometry_msgs.msg", Pose=_Pose)
    adapi = _make_module("autoware_adapi_v1_msgs")
    adapi_srv = _make_module(
        "autoware_adapi_v1_msgs.srv",
        SetRoutePoints=_SetRoutePoints,
        ClearRoute=_ClearRoute,
        ChangeOperationMode=_ChangeOperationMode,
    )
    tier4 = _make_module("tier4_planning_msgs")
    tier4_msg = _make_module("tier4_planning_msgs.msg", VelocityLimit=_VelocityLimit)

    mods = {
        "rclpy": rclpy,
        "geometry_msgs": geometry,
        "geometry_msgs.msg": geometry_msg,
        "autoware_adapi_v1_msgs": adapi,
        "autoware_adapi_v1_msgs.srv": adapi_srv,
        "tier4_planning_msgs": tier4,
        "tier4_planning_msgs.msg": tier4_msg,
    }
    saved = {k: sys.modules.get(k) for k in mods}
    sys.modules.update(mods)
    try:
        yield
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v


def _config(**over: Any) -> Any:
    from urml_av_runtime import AutowareConfig

    base: dict[str, Any] = {
        "location_to_pose": {
            "depot": {"x": 0.0, "y": 0.0, "yaw": 0.0},
            "dropoff": {"x": 30.0, "y": 12.0, "yaw": math.pi / 2},
        }
    }
    base.update(over)
    return AutowareConfig.model_validate(base)


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


def test_is_a_trajectory_adapter(fake_ros: None) -> None:
    from urml_av_runtime import AutowareAdapter

    with AutowareAdapter(_config()) as a:
        assert isinstance(a, TrajectoryAdapter)


def test_plan_then_follow_happy_path(fake_ros: None) -> None:
    from urml_av_runtime import AutowareAdapter

    with AutowareAdapter(_config()) as a:
        plan = a.plan_trajectory(start=None, goal="dropoff", along="city_map")
        assert plan.success and plan.payload is not None
        assert plan.payload["route_set"] is True
        assert plan.payload["goal"]["x"] == 30.0
        assert plan.payload["along"] == "city_map"

        nav = a.follow_trajectory_goal(trajectory=plan.payload, max_velocity_mps=12.0)
        assert nav.success

    services = [c["service"] for c in _FakeClient.calls]
    assert "/api/routing/set_route_points" in services
    assert "/api/operation_mode/change_to_autonomous" in services
    assert "/api/routing/clear_route" in services  # cleared before planning

    # Goal pose built with yaw -> quaternion about z.
    set_call = next(c for c in _FakeClient.calls if c["service"] == "/api/routing/set_route_points")
    goal = set_call["request"].goal
    assert goal.position.x == 30.0 and goal.position.y == 12.0
    assert goal.orientation.z == pytest.approx(math.sin(math.pi / 4))
    assert goal.orientation.w == pytest.approx(math.cos(math.pi / 4))

    # Speed cap published to the velocity-limit topic.
    assert len(_FakePublisher.published) == 1
    pub = _FakePublisher.published[0]
    assert pub["topic"] == "/planning/scenario_planning/max_velocity"
    assert pub["msg"].max_velocity == 12.0


def test_plan_goal_as_pose_dict(fake_ros: None) -> None:
    from urml_av_runtime import AutowareAdapter

    with AutowareAdapter(_config()) as a:
        plan = a.plan_trajectory(start=None, goal={"x": 5.0, "y": -2.0})
        assert plan.success and plan.payload is not None
        assert plan.payload["goal"] == {"x": 5.0, "y": -2.0, "z": 0.0, "yaw": 0.0}


def test_plan_goal_unresolvable(fake_ros: None) -> None:
    from urml_av_runtime import AutowareAdapter

    with AutowareAdapter(_config()) as a:
        plan = a.plan_trajectory(start=None, goal="nowhere")
        assert plan.success is False
        assert plan.reason is not None and plan.reason.startswith("goal_not_resolvable")


def test_route_rejected_by_ad_api(fake_ros: None) -> None:
    from urml_av_runtime import AutowareAdapter

    _FakeClient.success_by_service = {"/api/routing/set_route_points": False}
    with AutowareAdapter(_config()) as a:
        plan = a.plan_trajectory(start=None, goal="dropoff")
        assert plan.success is False
        assert plan.reason is not None and plan.reason.startswith("route_rejected")


def test_engage_rejected_by_ad_api(fake_ros: None) -> None:
    from urml_av_runtime import AutowareAdapter

    _FakeClient.success_by_service = {"/api/operation_mode/change_to_autonomous": False}
    with AutowareAdapter(_config()) as a:
        plan = a.plan_trajectory(start=None, goal="dropoff")
        nav = a.follow_trajectory_goal(trajectory=plan.payload)
        assert nav.success is False
        assert nav.reason is not None and nav.reason.startswith("engage_rejected")


def test_follow_without_a_route(fake_ros: None) -> None:
    from urml_av_runtime import AutowareAdapter

    with AutowareAdapter(_config()) as a:
        nav = a.follow_trajectory_goal(trajectory=None)
        assert nav.success is False
        assert nav.reason is not None and nav.reason.startswith("no_route")


def test_service_unavailable(fake_ros: None) -> None:
    from urml_av_runtime import AutowareAdapter

    _FakeClient.available = False
    with AutowareAdapter(_config()) as a:
        plan = a.plan_trajectory(start=None, goal="dropoff")
        assert plan.success is False
        assert plan.reason is not None and "service_unavailable" in plan.reason
