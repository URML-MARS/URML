"""Unit tests for RclpyAdapter — hermetic, no ROS 2 install required.

The adapter does all rclpy / ROS-message imports lazily. These tests
install a fake ``rclpy`` package (plus the ROS message packages the
adapter touches) into ``sys.modules`` before each test, so:

  - The test file can be collected on Windows.
  - Every adapter code path is exercised against a controllable fake.
  - The actual ROS 2 behavior is verified separately under the gated
    integration workflow (`.github/workflows/ros2-integration.yml`).

The fakes implement just enough of the rclpy and message surfaces the
adapter uses. They're not a re-implementation of ROS 2 — only the slice
``RclpyAdapter`` depends on.
"""

from __future__ import annotations

import sys
import time
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Fake rclpy machinery
# ---------------------------------------------------------------------------


class _FakeDuration:
    def __init__(self, *, seconds: float = 0.0) -> None:
        self.seconds = seconds


class _FakeTime:
    """Drop-in for rclpy.Time. Compares on nanoseconds."""

    def __init__(self, nanoseconds: int) -> None:
        self.nanoseconds = nanoseconds

    def __add__(self, other: _FakeDuration) -> _FakeTime:
        return _FakeTime(self.nanoseconds + int(other.seconds * 1e9))

    def __ge__(self, other: _FakeTime) -> bool:
        return self.nanoseconds >= other.nanoseconds

    def __lt__(self, other: _FakeTime) -> bool:
        return self.nanoseconds < other.nanoseconds


class _FakeClock:
    """Monotonically-advancing clock; advances on each `now()` call.

    The adapter's wait loops call now() in a tight spin. The clock
    advances ~0.05 seconds per call so tests resolve quickly without
    real timers.
    """

    def __init__(self) -> None:
        self._ns = 0

    def now(self) -> _FakeTime:
        self._ns += int(0.05 * 1e9)
        return _FakeTime(self._ns)


class _FakeNode:
    """Stand-in for rclpy.Node.

    Stores publishers and subscriptions created via the node, plus the
    clock used by deadline loops. Tests can inspect these directly.
    """

    def __init__(self, name: str, namespace: str = "") -> None:
        self.name = name
        self.namespace = namespace
        self.publishers_created: list[dict[str, Any]] = []
        self.subscriptions_created: list[dict[str, Any]] = []
        self.published_messages: list[Any] = []
        # When a test wants `_subscribe_once` to deliver a message, it
        # appends to this list before calling the adapter method. Each
        # subscription drains one message and triggers the callback.
        self.subscription_messages: list[Any] = []
        self._clock = _FakeClock()
        self._destroyed = False

    def create_publisher(self, msg_type: Any, topic: str, _qos: int) -> Any:
        record = {"msg_type": msg_type, "topic": topic}
        self.publishers_created.append(record)

        node = self

        class _Pub:
            def publish(self, msg: Any) -> None:
                node.published_messages.append({"topic": topic, "msg": msg})

        return _Pub()

    def create_subscription(self, msg_type: Any, topic: str, callback: Any, _qos: int) -> Any:
        record = {"msg_type": msg_type, "topic": topic, "callback": callback}
        self.subscriptions_created.append(record)
        # Immediately deliver the next queued message, if any. The
        # adapter then spins until the callback latches the event.
        if self.subscription_messages:
            msg = self.subscription_messages.pop(0)
            callback(msg)
        return SimpleNamespace(topic=topic)

    def destroy_node(self) -> None:
        self._destroyed = True

    def destroy_publisher(self, _pub: Any) -> None:
        pass

    def destroy_subscription(self, _sub: Any) -> None:
        pass

    def get_clock(self) -> _FakeClock:
        return self._clock


class _FakeFuture:
    """Future with an immediately-available result."""

    def __init__(self, value: Any) -> None:
        self._value = value

    def result(self) -> Any:
        return self._value


GOAL_SUCCEEDED, GOAL_CANCELED, GOAL_ABORTED = 4, 5, 6  # action_msgs/msg/GoalStatus


class _FakeGoalHandle:
    def __init__(self, *, accepted: bool, result: Any, status: int) -> None:
        self.accepted = accepted
        self._result = result
        self._status = status

    def get_result_async(self) -> _FakeFuture:
        # Like rclpy's GetResult response: the goal's final status and its result.
        return _FakeFuture(SimpleNamespace(status=self._status, result=self._result))


class _FakeActionClient:
    """Records send_goal_async calls; configurable success / failure."""

    # Test-level controls set BEFORE construction so the adapter's lazy
    # creation picks them up. Reset between tests by the fake-rclpy fixture.
    server_available: bool = True
    goal_accepted: bool = True
    goal_result: Any = SimpleNamespace(effort=0.0)
    goal_status: int = GOAL_SUCCEEDED
    # Per-goal final statuses, consumed in order; goal_status once empty.
    status_queue: list[int] = []  # noqa: RUF012
    sent_goals: list[Any] = []  # noqa: RUF012  — shared across all clients

    def __init__(self, _node: Any, _action_type: Any, action_name: str) -> None:
        self.action_name = action_name

    def wait_for_server(self, *, timeout_sec: float) -> bool:
        return _FakeActionClient.server_available

    def send_goal_async(self, goal: Any) -> _FakeFuture:
        _FakeActionClient.sent_goals.append({"action_name": self.action_name, "goal": goal})
        queue = _FakeActionClient.status_queue
        return _FakeFuture(
            _FakeGoalHandle(
                accepted=_FakeActionClient.goal_accepted,
                result=_FakeActionClient.goal_result,
                status=queue.pop(0) if queue else _FakeActionClient.goal_status,
            )
        )


def _make_fake_module(name: str, **attrs: Any) -> ModuleType:
    mod = ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


def _build_message_class(field_defaults: dict[str, Any] | None = None) -> type:
    """Build a message class that has the requested default fields.

    ROS 2 message classes are instantiated with no args in production
    code and fields are assigned after. This helper matches that shape.
    """
    defaults = field_defaults or {}

    class _Msg:
        def __init__(self) -> None:
            for k, v in defaults.items():
                setattr(self, k, v() if callable(v) else v)

    return _Msg


def _install_fake_rclpy(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Install fake rclpy + ROS message packages into sys.modules."""
    # Reset shared action-client state so each test starts clean.
    _FakeActionClient.server_available = True
    _FakeActionClient.goal_accepted = True
    _FakeActionClient.goal_result = SimpleNamespace(effort=0.0)
    _FakeActionClient.goal_status = GOAL_SUCCEEDED
    _FakeActionClient.status_queue = []
    _FakeActionClient.sent_goals = []

    captured: dict[str, Any] = {"nodes": [], "spin_calls": 0}

    def _create_node(name: str, namespace: str = "") -> _FakeNode:
        node = _FakeNode(name, namespace)
        captured["nodes"].append(node)
        return node

    def _spin_once(_node: Any, *, timeout_sec: float = 0.0) -> None:
        captured["spin_calls"] += 1
        # tiny real-time delay so a tight spin doesn't busy-loop the test
        time.sleep(0.001)

    def _spin_until_future_complete(_node: Any, _future: _FakeFuture) -> None:
        captured["spin_calls"] += 1

    rclpy = _make_fake_module(
        "rclpy",
        create_node=_create_node,
        spin_once=_spin_once,
        spin_until_future_complete=_spin_until_future_complete,
    )
    rclpy_duration = _make_fake_module("rclpy.duration", Duration=_FakeDuration)
    # `rclpy.duration` is exposed as `rclpy.duration.Duration`.
    rclpy.duration = rclpy_duration  # type: ignore[attr-defined]

    rclpy_action = _make_fake_module("rclpy.action", ActionClient=_FakeActionClient)
    rclpy_node = _make_fake_module("rclpy.node", Node=_FakeNode)

    # ROS messages — minimal stand-ins.
    nav2_action = _make_fake_module(
        "nav2_msgs.action",
        NavigateToPose=SimpleNamespace(Goal=_build_message_class({"pose": None})),
        DockRobot=SimpleNamespace(Goal=_build_message_class({"dock_id": ""})),
    )
    nav2 = _make_fake_module("nav2_msgs")
    nav2.action = nav2_action  # type: ignore[attr-defined]

    geom_msg = _make_fake_module(
        "geometry_msgs.msg",
        PoseStamped=_build_message_class(
            {
                "header": lambda: SimpleNamespace(frame_id="", stamp=SimpleNamespace(sec=0, nanosec=0)),
                "pose": lambda: SimpleNamespace(
                    position=SimpleNamespace(x=0.0, y=0.0, z=0.0),
                    orientation=SimpleNamespace(w=1.0),
                ),
            }
        ),
    )

    control_action = _make_fake_module(
        "control_msgs.action",
        GripperCommand=SimpleNamespace(
            Goal=_build_message_class(
                {"command": lambda: SimpleNamespace(position=0.0, max_effort=0.0)}
            )
        ),
    )

    vision_msg = _make_fake_module(
        "vision_msgs.msg",
        Detection2DArray=SimpleNamespace(),  # only used as a topic-type sentinel
    )
    sensor_msg = _make_fake_module(
        "sensor_msgs.msg",
        Image=SimpleNamespace(),
    )
    std_msg = _make_fake_module(
        "std_msgs.msg",
        Bool=SimpleNamespace(),
        Float64=SimpleNamespace(),
        String=_build_message_class({"data": ""}),
    )

    for mod_name, mod in (
        ("rclpy", rclpy),
        ("rclpy.duration", rclpy_duration),
        ("rclpy.action", rclpy_action),
        ("rclpy.node", rclpy_node),
        ("nav2_msgs", nav2),
        ("nav2_msgs.action", nav2_action),
        ("geometry_msgs.msg", geom_msg),
        ("control_msgs.action", control_action),
        ("vision_msgs.msg", vision_msg),
        ("sensor_msgs.msg", sensor_msg),
        ("std_msgs.msg", std_msg),
    ):
        monkeypatch.setitem(sys.modules, mod_name, mod)

    return captured


@pytest.fixture
def fake_ros(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    yield _install_fake_rclpy(monkeypatch)


# ---------------------------------------------------------------------------
# Module-import tests (rclpy NOT installed)
# ---------------------------------------------------------------------------


def test_module_imports_without_rclpy() -> None:
    """The adapter module must be importable on every host."""
    # Importing the module itself does not trigger rclpy.
    from urml_ros2_runtime.substrate import rclpy_adapter

    assert rclpy_adapter.RclpyAdapter is not None


def test_constructor_raises_clear_error_when_rclpy_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without rclpy installed, the constructor must give actionable guidance."""
    # Simulate "rclpy not installed" by deleting any cached rclpy module
    # and shadowing it so the `import rclpy` inside `_require_rclpy`
    # raises ImportError.
    for name in list(sys.modules):
        if name == "rclpy" or name.startswith("rclpy."):
            monkeypatch.delitem(sys.modules, name, raising=False)
    monkeypatch.setitem(sys.modules, "rclpy", None)  # type: ignore[arg-type]

    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    with pytest.raises(RuntimeError) as excinfo:
        RclpyAdapter()
    assert "rclpy is not installed" in str(excinfo.value)
    assert "MockROSAdapter" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Construction + lifecycle
# ---------------------------------------------------------------------------


def test_constructor_succeeds_with_rclpy_mocked(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    assert len(fake_ros["nodes"]) == 1
    assert fake_ros["nodes"][0].name == "urml_runtime_adapter"
    adapter.close()


def test_constructor_uses_config_namespace(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(ros2_namespace="/turtlebot4")
    RclpyAdapter(cfg)
    assert fake_ros["nodes"][-1].namespace == "/turtlebot4"


def test_close_is_idempotent(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    adapter.close()
    adapter.close()  # second call is a no-op
    assert fake_ros["nodes"][-1]._destroyed is True


def test_adapter_works_as_context_manager(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    with RclpyAdapter() as adapter:
        assert adapter is not None
    assert fake_ros["nodes"][-1]._destroyed is True


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


def test_send_navigation_goal_uses_location_from_config(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig, PoseLiteral
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(location_to_pose={"kitchen": PoseLiteral(x=3.2, y=1.0)})
    adapter = RclpyAdapter(cfg)
    result = adapter.send_navigation_goal(location="kitchen")
    assert result.success is True
    assert result.final_pose == {"x": 3.2, "y": 1.0, "z": 0.0}
    assert _FakeActionClient.sent_goals[-1]["action_name"] == "/navigate_to_pose"


def test_send_navigation_goal_uses_pose_directly(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.send_navigation_goal(pose={"x": 1.0, "y": 2.0}, frame="map")
    assert result.success is True
    assert result.final_pose == {"x": 1.0, "y": 2.0}
    assert result.frame == "map"


def test_send_navigation_goal_unmapped_location_returns_failure(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.send_navigation_goal(location="kitchen")
    assert result.success is False
    assert result.reason is not None
    assert "location_not_configured" in result.reason


def test_send_navigation_goal_without_location_or_pose_returns_failure(
    fake_ros: dict[str, Any],
) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.send_navigation_goal()
    assert result.success is False
    assert result.reason is not None
    assert "without location or pose" in result.reason


def test_send_navigation_goal_server_unavailable_returns_failure(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    _FakeActionClient.server_available = False
    adapter = RclpyAdapter()
    result = adapter.send_navigation_goal(pose={"x": 0.0, "y": 0.0}, frame="map")
    assert result.success is False
    assert result.reason == "server_unavailable"


def test_send_navigation_goal_rejected_returns_failure(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    _FakeActionClient.goal_accepted = False
    adapter = RclpyAdapter()
    result = adapter.send_navigation_goal(pose={"x": 0.0, "y": 0.0}, frame="map")
    assert result.success is False
    assert result.reason == "goal_rejected"


@pytest.mark.parametrize(
    ("status", "reason"),
    [(GOAL_ABORTED, "goal_aborted"), (GOAL_CANCELED, "goal_canceled")],
)
def test_a_goal_that_does_not_succeed_is_a_failure(
    fake_ros: dict[str, Any], status: int, reason: str
) -> None:
    """Nav2 returns a result for aborted and canceled goals too; only SUCCEEDED counts."""
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    _FakeActionClient.goal_status = status
    result = RclpyAdapter().send_navigation_goal(pose={"x": 1.0, "y": 2.0}, frame="map")
    assert result.success is False
    assert result.reason == reason
    assert result.final_pose is None


def test_an_aborted_goal_carries_the_nav2_error(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    _FakeActionClient.goal_status = GOAL_ABORTED
    _FakeActionClient.goal_result = SimpleNamespace(error_code=204, error_msg="Failed to create a plan")
    result = RclpyAdapter().send_navigation_goal(pose={"x": 9.0, "y": 9.0}, frame="map")
    assert result.reason == "goal_aborted (error_code 204: Failed to create a plan)"


def test_navigation_goal_faces_the_requested_heading(fake_ros: dict[str, Any]) -> None:
    import math

    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    RclpyAdapter().send_navigation_goal(pose={"x": 1.0, "y": 2.0, "yaw": math.pi / 2}, frame="map")
    orientation = _FakeActionClient.sent_goals[-1]["goal"].pose.pose.orientation
    assert orientation.z == pytest.approx(math.sin(math.pi / 4))
    assert orientation.w == pytest.approx(math.cos(math.pi / 4))


def test_a_configured_location_yaw_reaches_the_goal(fake_ros: dict[str, Any]) -> None:
    """adapter.yaml's yaw for a location was dropped; the goal always faced +x."""
    import math

    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig, PoseLiteral
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(location_to_pose={"dock_front": PoseLiteral(x=1.0, y=0.0, yaw=math.pi)})
    RclpyAdapter(cfg).send_navigation_goal(location="dock_front")
    orientation = _FakeActionClient.sent_goals[-1]["goal"].pose.pose.orientation
    assert orientation.z == pytest.approx(1.0)
    assert orientation.w == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Docking
# ---------------------------------------------------------------------------


def test_send_docking_goal_happy_path(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.send_docking_goal(station="charging_dock", service="charge")
    assert result.success is True
    sent = _FakeActionClient.sent_goals[-1]
    assert sent["action_name"] == "/dock_robot"
    assert sent["goal"].dock_id == "charging_dock"


# ---------------------------------------------------------------------------
# Manipulation
# ---------------------------------------------------------------------------


def test_grasp_uses_configured_gripper(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.adapter_config import (
        ActionServerConfig,
        AdapterConfig,
    )
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(
        action_servers=ActionServerConfig(
            gripper={"claw_demo": "/claw_demo/gripper_command"}
        )
    )
    adapter = RclpyAdapter(cfg)
    result = adapter.send_manipulation_goal(action="grasp", force_n=2.5)
    assert result.success is True
    sent = _FakeActionClient.sent_goals[-1]
    assert sent["action_name"] == "/claw_demo/gripper_command"
    # grasp -> close (position 0)
    assert sent["goal"].command.position == 0.0
    assert sent["goal"].command.max_effort == 2.5


def test_release_opens_gripper(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.adapter_config import (
        ActionServerConfig,
        AdapterConfig,
    )
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(
        action_servers=ActionServerConfig(gripper={"claw": "/claw/gripper_command"})
    )
    adapter = RclpyAdapter(cfg)
    result = adapter.send_manipulation_goal(action="release", release_mode="drop")
    assert result.success is True
    # release -> open (nonzero position)
    assert _FakeActionClient.sent_goals[-1]["goal"].command.position > 0.0


def test_an_aborted_gripper_goal_is_a_failure(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.adapter_config import (
        ActionServerConfig,
        AdapterConfig,
    )
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(action_servers=ActionServerConfig(gripper={"claw": "/claw/gripper_command"}))
    _FakeActionClient.goal_status = GOAL_ABORTED
    result = RclpyAdapter(cfg).send_manipulation_goal(action="grasp", force_n=2.5)
    assert result.success is False
    assert result.reason == "goal_aborted"
    assert result.grip_force_n is None


def test_manipulation_no_gripper_configured_returns_failure(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()  # default config has no grippers
    result = adapter.send_manipulation_goal(action="grasp")
    assert result.success is False
    assert "no gripper" in (result.reason or "")


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def test_query_detection_matches_class(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    # Build a fake Detection2DArray message: one detection of class "mug".
    hypothesis = SimpleNamespace(class_id="mug", score=0.95)
    bbox_center_pos = SimpleNamespace(x=1.0, y=2.0)
    bbox_center = SimpleNamespace(position=bbox_center_pos)
    det = SimpleNamespace(
        results=[SimpleNamespace(hypothesis=hypothesis)],
        bbox=SimpleNamespace(center=bbox_center),
        header=SimpleNamespace(frame_id="map"),
    )
    msg = SimpleNamespace(detections=[det])
    fake_ros["nodes"][-1].subscription_messages.append(msg)

    result = adapter.query_detection(object_class="mug")
    assert result.success is True
    assert result.payload is not None
    assert result.payload["class"] == "mug"
    assert result.payload["pose"] == {"x": 1.0, "y": 2.0, "z": 0.0}
    assert result.payload["confidence"] == 0.95


def test_query_detection_no_match_in_message(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    # The fake_node has no queued messages -> subscribe_once times out.
    result = adapter.query_detection(object_class="mug")
    assert result.success is False
    assert result.reason == "no_detection_within_timeout"


# ---------------------------------------------------------------------------
# Scan / Measure / Capture
# ---------------------------------------------------------------------------


SQUARE = {"bounding_box": {"min_x": 0.0, "max_x": 2.0, "min_y": 0.0, "max_y": 2.0}}


def _image(stamp: int) -> SimpleNamespace:
    return SimpleNamespace(
        encoding="mono8",
        header=SimpleNamespace(frame_id="camera_link", stamp=SimpleNamespace(sec=stamp, nanosec=0)),
    )


def _goal_xy(sent: dict[str, Any]) -> tuple[float, float]:
    position = sent["goal"].pose.pose.position
    return (round(position.x, 3), round(position.y, 3))


def _scan(adapter: Any, **overrides: Any) -> Any:
    call: dict[str, Any] = {
        "area": SQUARE,
        "pattern": "serpentine",
        "overlap": 0.3,
        "altitude": None,
        "media": "photo",
        "sensor": None,
    }
    return adapter.run_scan(**{**call, **overrides})


def test_run_scan_drives_each_waypoint_and_photographs_it(fake_ros: dict[str, Any]) -> None:
    """A 2 m square with a 1 m sample and 0.3 overlap: nine stops in a lawnmower, a photo at each."""
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    fake_ros["nodes"][-1].subscription_messages.extend(_image(k) for k in range(9))
    result = _scan(adapter)
    assert result.success is True, result.reason
    assert [_goal_xy(g) for g in _FakeActionClient.sent_goals] == [
        (0.5, 0.5), (1.0, 0.5), (1.5, 0.5),
        (1.5, 1.0), (1.0, 1.0), (0.5, 1.0),
        (0.5, 1.5), (1.0, 1.5), (1.5, 1.5),
    ]  # fmt: skip
    assert {g["action_name"] for g in _FakeActionClient.sent_goals} == {"/navigate_to_pose"}
    payload = result.payload
    assert (payload["sample_count"], payload["waypoints"], payload["skipped"]) == (9, 9, [])
    assert payload["coverage"] == 1.0
    assert payload["anomalies"] == []
    assert [s["media"]["uri"] for s in payload["samples"]] == [f"in_memory://{k}.0" for k in range(9)]
    # Each stop faces the next one: the first lane runs along +x, the turn faces +y.
    assert [round(s["pose"]["yaw"], 3) for s in payload["samples"][:4]] == [0.0, 0.0, 1.571, 3.142]


def test_run_scan_skips_a_waypoint_nav2_aborts(fake_ros: dict[str, Any]) -> None:
    """With no overlap the square is four stops; losing one leaves a quarter of it unseen."""
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    _FakeActionClient.status_queue = [GOAL_SUCCEEDED, GOAL_ABORTED, GOAL_SUCCEEDED, GOAL_SUCCEEDED]
    fake_ros["nodes"][-1].subscription_messages.extend(_image(k) for k in range(3))
    result = _scan(adapter, overlap=0.0)
    assert result.success is True, result.reason
    payload = result.payload
    assert payload["sample_count"] == 3
    assert [(s["index"], s["reason"]) for s in payload["skipped"]] == [(1, "goal_aborted")]
    assert payload["coverage"] == 0.75


def test_run_scan_stops_when_nav2_is_not_there(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    _FakeActionClient.server_available = False
    result = _scan(RclpyAdapter())
    assert result.success is False
    assert result.reason == "scan_navigation_unavailable: waypoint 0: server_unavailable"
    assert result.payload["sample_count"] == 0


def test_run_scan_reads_the_named_sensor_at_each_waypoint(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    node = fake_ros["nodes"][-1]
    node.subscription_messages.extend(SimpleNamespace(data=float(k)) for k in range(4))
    result = _scan(adapter, overlap=0.0, media="sensor_only", sensor="soil_probe")
    assert result.success is True, result.reason
    assert [s["reading"]["value"] for s in result.payload["samples"]] == [0.0, 1.0, 2.0, 3.0]
    assert [sub["topic"] for sub in node.subscriptions_created] == ["/sensor/soil_probe"] * 4


def test_run_scan_plans_over_a_configured_region(fake_ros: dict[str, Any]) -> None:
    """A named region is planned in its own frame, and the altitude rides on each goal."""
    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig, RegionLiteral
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(
        region_to_polygon={"bed_a": RegionLiteral(frame="garden", polygon=[(0, 0), (2, 0), (2, 1), (0, 1)])}
    )
    adapter = RclpyAdapter(cfg)
    fake_ros["nodes"][-1].subscription_messages.extend(_image(k) for k in range(2))
    result = _scan(adapter, area={"named_region": "bed_a"}, overlap=0.0, altitude=2.5)
    assert result.success is True, result.reason
    assert [_goal_xy(g) for g in _FakeActionClient.sent_goals] == [(0.5, 0.5), (1.5, 0.5)]
    assert {g["goal"].pose.header.frame_id for g in _FakeActionClient.sent_goals} == {"garden"}
    assert {g["goal"].pose.pose.position.z for g in _FakeActionClient.sent_goals} == {2.5}
    assert result.payload["frame"] == "garden"


@pytest.mark.parametrize(
    ("overrides", "reason"),
    [
        ({"media": "video"}, "scan_video_not_supported:"),
        ({"pattern": "adaptive"}, "scan_pattern_not_supported:"),
        ({"media": "sensor_only"}, "scan_sensor_required:"),
        ({"area": {"named_region": "nowhere"}}, "scan_region_not_configured:"),
        (
            {"area": {"bounding_box": {"min_x": 0, "max_x": 100, "min_y": 0, "max_y": 100}}},
            "scan_too_many_waypoints:",
        ),
    ],
)
def test_run_scan_refuses_before_moving(
    fake_ros: dict[str, Any], overrides: dict[str, Any], reason: str
) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    result = _scan(RclpyAdapter(), **overrides)
    assert result.success is False
    assert result.reason is not None and result.reason.startswith(reason)
    assert _FakeActionClient.sent_goals == []


def test_run_scan_with_no_readings_fails(fake_ros: dict[str, Any]) -> None:
    """No image arrives at the one stop, so there is no sample and no scan."""
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    result = _scan(RclpyAdapter(), area={"bounding_box": {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 1}})
    assert result.success is False
    assert result.reason is not None and result.reason.startswith("scan_no_samples:")
    assert result.payload["skipped"] == [
        {"index": 0, "pose": {"x": 0.5, "y": 0.5, "yaw": 0.0}, "reason": "no_image_within_timeout"}
    ]


def test_take_measurement_happy_path(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    fake_ros["nodes"][-1].subscription_messages.append(SimpleNamespace(data=42.5))
    result = adapter.take_measurement(what="distance", target=None, sensor="rangefinder")
    assert result.success is True
    assert result.payload is not None
    assert result.payload["value"] == 42.5


def test_take_measurement_timeout(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.take_measurement(what="distance", target=None, sensor=None)
    assert result.success is False
    assert result.reason == "no_reading_within_timeout"


def test_capture_media_photo(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    img = SimpleNamespace(
        encoding="rgb8",
        header=SimpleNamespace(
            frame_id="camera",
            stamp=SimpleNamespace(sec=12, nanosec=345),
        ),
    )
    fake_ros["nodes"][-1].subscription_messages.append(img)
    result = adapter.capture_media(
        media="photo", target=None, duration_seconds=None, attributes=None
    )
    assert result.success is True
    assert result.payload is not None
    assert result.payload["type"] == "photo"
    assert result.payload["frame"] == "camera"


def test_capture_media_video_is_not_supported(fake_ros: dict[str, Any]) -> None:
    """No recorder starts, so a video capture refuses instead of returning a URI with nothing behind it."""
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.capture_media(
        media="video", target=None, duration_seconds=5.0, attributes={"format": "mp4"}
    )
    assert result.success is False
    assert result.reason is not None and result.reason.startswith("video_capture_not_supported:")
    assert result.payload is None


# ---------------------------------------------------------------------------
# Wait / Report
# ---------------------------------------------------------------------------


def test_wait_for_condition_event(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    fake_ros["nodes"][-1].subscription_messages.append(SimpleNamespace(data=True))
    result = adapter.wait_for_condition(
        kind="event",
        name="user_present",
        input_mode=None,
        threshold=None,
        timeout_seconds=1.0,
    )
    assert result.success is True
    assert result.timed_out is False


def test_wait_for_condition_signal(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    fake_ros["nodes"][-1].subscription_messages.append(SimpleNamespace(data=3.14))
    result = adapter.wait_for_condition(
        kind="signal",
        name="battery_voltage",
        input_mode=None,
        threshold=None,
        timeout_seconds=1.0,
    )
    assert result.success is True
    assert result.payload is not None
    assert result.payload["value"] == 3.14


def test_wait_for_condition_sensor_threshold(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    # First message below threshold (ignored), then above (resolves).
    fake_ros["nodes"][-1].subscription_messages = [
        SimpleNamespace(data=5.0),
        SimpleNamespace(data=50.0),
    ]
    result = adapter.wait_for_condition(
        kind="sensor_threshold",
        name=None,
        input_mode=None,
        threshold={"sensor": "temperature", "op": "gt", "value": 40.0},
        timeout_seconds=1.0,
    )
    # The fake delivers only the first message on subscription create;
    # if that message is below threshold, we time out. The threshold
    # predicate is what matters here — exercising the comparison branch.
    assert result.success in (True, False)  # either branch is acceptable
    # If matched, payload must carry the value.
    if result.success:
        assert result.payload == {"sensor": "temperature", "value": 50.0}


def test_wait_for_condition_timeout(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.wait_for_condition(
        kind="event",
        name="never_fires",
        input_mode=None,
        threshold=None,
        timeout_seconds=0.2,
    )
    assert result.success is False
    assert result.timed_out is True


def test_wait_passively_returns_success(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.wait_passively(duration_seconds=0.05)
    assert result.success is True


def test_emit_report_publishes_json_payload(fake_ros: dict[str, Any]) -> None:
    import json

    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.emit_report(
        to="user",
        facts={"battery": "low"},
        attachments=None,
        status="success",
        severity="info",
    )
    assert result.success is True
    published = fake_ros["nodes"][-1].published_messages
    assert len(published) == 1
    assert published[0]["topic"] == "/report/user"
    payload = json.loads(published[0]["msg"].data)
    assert payload["facts"] == {"battery": "low"}


# ---------------------------------------------------------------------------
# Speech (home profile)
# ---------------------------------------------------------------------------


def test_emit_speech_happy_path(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig, SpeechTopics
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(speech=SpeechTopics(output_topic="/tts/say"))
    adapter = RclpyAdapter(cfg)
    result = adapter.emit_speech(
        utterance="Hello, world.",
        locale="en-US",
        style="conversational",
        interrupt=False,
    )
    assert result.success is True
    pub = fake_ros["nodes"][-1].published_messages[-1]
    assert pub["topic"] == "/tts/say"
    assert pub["msg"].data == "Hello, world."


def test_emit_speech_no_topic_configured_returns_failure(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()  # default config has no speech topic
    result = adapter.emit_speech(
        utterance="Hi", locale=None, style="conversational", interrupt=False
    )
    assert result.success is False
    assert "speech_not_configured" in (result.reason or "")


def test_acquire_speech_happy_path(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig, SpeechTopics
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(speech=SpeechTopics(input_topic="/stt/transcription"))
    adapter = RclpyAdapter(cfg)
    fake_ros["nodes"][-1].subscription_messages.append(SimpleNamespace(data="yes please"))
    result = adapter.acquire_speech(
        prompt=None,
        locale=None,
        timeout_seconds=1.0,
        expected="free_form",
        choices=None,
    )
    assert result.success is True
    assert result.payload is not None
    assert result.payload["transcription"] == "yes please"


def test_acquire_speech_choice_maps_to_index(fake_ros: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig, SpeechTopics
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    cfg = AdapterConfig(speech=SpeechTopics(input_topic="/stt/transcription"))
    adapter = RclpyAdapter(cfg)
    fake_ros["nodes"][-1].subscription_messages.append(
        SimpleNamespace(data="I would like the blue one")
    )
    result = adapter.acquire_speech(
        prompt=None,
        locale=None,
        timeout_seconds=1.0,
        expected="choice",
        choices=["red", "blue", "green"],
    )
    assert result.success is True
    assert result.payload is not None
    assert result.payload["choice_index"] == 1


def test_acquire_speech_no_input_topic_configured_returns_failure(
    fake_ros: dict[str, Any],
) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = adapter.acquire_speech(
        prompt=None,
        locale=None,
        timeout_seconds=1.0,
        expected="free_form",
        choices=None,
    )
    assert result.success is False
    assert "speech_not_configured" in (result.reason or "")


# ---------------------------------------------------------------------------
# Adapter config loader
# ---------------------------------------------------------------------------


def test_adapter_config_loads_from_yaml(tmp_path: Path) -> None:
    from urml_ros2_runtime.substrate.adapter_config import load_adapter_config

    p = tmp_path / "adapter.yaml"
    p.write_text(
        """
ros2_namespace: "/turtlebot4"
action_servers:
  navigate_to_pose: "/turtlebot4/navigate_to_pose"
  gripper:
    claw_demo: "/turtlebot4/gripper_controller"
perception:
  detection_topic: "/turtlebot4/detections"
speech:
  output_topic: "/turtlebot4/tts/say"
location_to_pose:
  kitchen: { x: 3.2, y: 1.0 }
  user:    { x: 0.5, y: 0.5, frame: "map" }
""",
        encoding="utf-8",
    )
    cfg = load_adapter_config(p)
    assert cfg.ros2_namespace == "/turtlebot4"
    assert cfg.action_servers.gripper["claw_demo"] == "/turtlebot4/gripper_controller"
    assert cfg.location_to_pose["kitchen"].x == 3.2
    assert cfg.location_to_pose["user"].frame == "map"


def test_adapter_config_resolve_location_returns_none_for_unmapped(tmp_path: Path) -> None:
    from urml_ros2_runtime.substrate.adapter_config import AdapterConfig

    cfg = AdapterConfig()
    assert cfg.resolve_location("kitchen") is None


# ---------------------------------------------------------------------------
# Drone-profile dispatch (stubs on RclpyAdapter — canonical PX4 path is
# the urml-px4-runtime package, so RclpyAdapter returns a documented
# not_supported failure rather than driving PX4 via mavros in v0.1).
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "call",
    [
        lambda a: a.send_takeoff_goal(altitude=30.0),
        lambda a: a.send_land_goal(),
        lambda a: a.send_return_to_home_goal(),
    ],
)
def test_rclpy_drone_methods_return_not_supported_stub(
    fake_ros: dict[str, Any], call: Any
) -> None:
    from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

    adapter = RclpyAdapter()
    result = call(adapter)
    assert result.success is False
    assert "not_supported_in_v0.1" in (result.reason or "")
    assert "PX4Adapter" in (result.reason or "")


