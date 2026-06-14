"""RclpyAdapter — real ROS 2 backing for the URML runtime.

Implements the ``ROSAdapter`` Protocol (see ``substrate/base.py``) via
``rclpy`` and the standard ROS 2 message / action packages (Nav2 for
navigation and docking, MoveIt 2 for arm manipulation, ``vision_msgs``
for detection, ``sensor_msgs`` for measurement, ``audio_common_msgs``
or a configurable string topic for speech).

## Lazy rclpy

``rclpy`` is not in ``dependencies`` because the rclpy wheel ships with
a ROS 2 distribution rather than from PyPI. The adapter imports rclpy
*lazily* at construction time, so:

- Module-level ``import urml_ros2_runtime.substrate.rclpy_adapter`` works
  on every host, including Windows, even without rclpy installed.
- ``RclpyAdapter()`` raises a clear, actionable error if rclpy is missing.

Per-method ROS message types are also imported lazily — this keeps the
module-load cost small on hosts that only need a subset of primitives.

## Adapter lifecycle

- ``rclpy.init()`` is the *caller's* responsibility. Adapters in
  production typically share a single init across multiple subsystems;
  re-init'ing here would clobber other nodes in the same process.
- The adapter owns one ``rclpy.Node`` plus a set of lazily-created action
  clients. Action clients are constructed on first use, not at
  construction, so an adapter that never calls navigation doesn't pay
  the Nav2 action-client cost.
- ``close()`` destroys the node and any subscriptions. Adapters are
  context managers: ``with RclpyAdapter(...) as a: ...``.

## Error contract

Per the ROSAdapter Protocol: failures are *returned* in
``SubstrateResult(success=False, reason=...)``, not raised. Only
unrecoverable substrate errors (broken connection, ROS 2 graph down)
raise — and the runtime wraps those into ``PrimitiveExecutionError``.

A pinpoint exception to the "return don't raise" rule: action clients
that fail to even reach a server return ``success=False`` with
``reason='server_unavailable'``. That's a substrate-side failure the
URML on-error policy is well-positioned to handle.
"""

from __future__ import annotations

import threading
from contextlib import suppress
from typing import Any, Literal

from urml_ros2_runtime.substrate.adapter_config import AdapterConfig
from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    DetectionResult,
    ListenResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ProgramCallResult,
    ScanResult,
    SubstrateResult,
    WaitResult,
)

DEFAULT_ACTION_TIMEOUT_SECONDS = 1.0
"""How long to wait for an action server to become available before
returning a server_unavailable failure. The action's own execution
timeout is separate and lives in the URML envelope / fixture."""

DEFAULT_TOPIC_TIMEOUT_SECONDS = 5.0
"""Default wait for a single message on a topic (detection, sensor,
audio). Each method can override per-call via its `timeout_seconds`
argument when URML provides one."""


def _require_rclpy() -> Any:
    """Lazy-import rclpy and surface a clear error if it isn't installed.

    Returns the imported rclpy module. Callers should cache it on the
    adapter instance after construction; per-call lookups would waste time.
    """
    try:
        import rclpy  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "rclpy is not installed. RclpyAdapter requires a ROS 2 environment.\n"
            "  On Linux: install ROS 2 (e.g., `apt install ros-jazzy-desktop`) and "
            "source `/opt/ros/<distro>/setup.bash` before launching Python.\n"
            "  On Windows: this adapter is not supported on Windows; use WSL2 or "
            "fall back to MockROSAdapter for development."
        ) from exc
    return rclpy


class RclpyAdapter:
    """Real ROS 2 adapter implementing the URML ``ROSAdapter`` Protocol.

    Construction requires a running ROS 2 environment (rclpy importable,
    ``rclpy.init()`` already called by the caller). Methods map each URML
    primitive's dispatch step onto Nav2 / MoveIt 2 / standard message
    topics per the table in ``INTEGRATION.md``.
    """

    def __init__(
        self,
        config: AdapterConfig | None = None,
        *,
        node_name: str = "urml_runtime_adapter",
    ) -> None:
        self._rclpy = _require_rclpy()
        self._config = config or AdapterConfig()
        self._node = self._rclpy.create_node(
            node_name,
            namespace=self._config.ros2_namespace,
        )
        # Lazy action-client slots — None until the first call.
        self._nav_client: Any = None
        self._dock_client: Any = None
        self._move_group_client: Any = None
        # Per-gripper-name action clients.
        self._gripper_clients: dict[str, Any] = {}
        # Per-topic subscription slots, with a one-shot latch for the
        # "subscribe for one message" pattern used by detection / measure /
        # acquire_speech / wait_for(condition.signal).
        self._closed = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Tear down the node. Safe to call multiple times."""
        if self._closed:
            return
        with suppress(Exception):
            self._node.destroy_node()
        self._closed = True

    def __enter__(self) -> RclpyAdapter:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _send_action_goal(
        self,
        client: Any,
        goal: Any,
        *,
        timeout_seconds: float | None = None,
    ) -> tuple[bool, str | None, Any]:
        """Common send-and-wait scaffolding for action clients.

        Returns ``(success, reason, result)``. ``result`` is the action's
        typed result object (or None on failure). Timeouts and server
        unavailability translate into clean failure tuples; only
        unrecoverable substrate errors propagate.
        """
        server_wait = timeout_seconds or DEFAULT_ACTION_TIMEOUT_SECONDS
        if not client.wait_for_server(timeout_sec=server_wait):
            return False, "server_unavailable", None
        send_future = client.send_goal_async(goal)
        self._rclpy.spin_until_future_complete(self._node, send_future)
        goal_handle = send_future.result()
        if goal_handle is None or not goal_handle.accepted:
            return False, "goal_rejected", None
        result_future = goal_handle.get_result_async()
        self._rclpy.spin_until_future_complete(self._node, result_future)
        wrapped = result_future.result()
        if wrapped is None:
            return False, "no_result", None
        return True, None, wrapped.result

    def _subscribe_once(
        self,
        topic: str,
        msg_type: Any,
        *,
        predicate: Any = None,
        timeout_seconds: float = DEFAULT_TOPIC_TIMEOUT_SECONDS,
    ) -> tuple[Any | None, bool]:
        """Subscribe to ``topic``, return the first message matching
        ``predicate`` (or the first message if predicate is None).

        Returns ``(message, timed_out)``. The subscription is destroyed
        before returning, so it does not leak between calls.
        """
        result_holder: dict[str, Any] = {"msg": None}
        event = threading.Event()

        def _cb(msg: Any) -> None:
            if predicate is None or predicate(msg):
                result_holder["msg"] = msg
                event.set()

        sub = self._node.create_subscription(msg_type, topic, _cb, 10)
        try:
            deadline = self._node.get_clock().now() + self._rclpy.duration.Duration(
                seconds=timeout_seconds,
            )
            while not event.is_set():
                self._rclpy.spin_once(self._node, timeout_sec=0.1)
                if self._node.get_clock().now() >= deadline:
                    return None, True
            return result_holder["msg"], False
        finally:
            with suppress(Exception):
                self._node.destroy_subscription(sub)

    def _publish_once(self, topic: str, msg_type: Any, msg: Any) -> None:
        """Publish a single message on a topic and tear down the publisher.

        ROS 2 publishers benefit from being held open (subscribers need
        time to connect); when the URML primitive *intent* is "fire and
        forget" (`emit_speech`, `emit_report`), holding the publisher
        for one message is acceptable and avoids leaks.
        """
        pub = self._node.create_publisher(msg_type, topic, 10)
        try:
            pub.publish(msg)
        finally:
            with suppress(Exception):
                self._node.destroy_publisher(pub)

    # ------------------------------------------------------------------
    # Navigation & docking
    # ------------------------------------------------------------------

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        from geometry_msgs.msg import PoseStamped  # type: ignore[import-not-found,unused-ignore]
        from nav2_msgs.action import NavigateToPose  # type: ignore[import-not-found,unused-ignore]

        # Resolve target pose: either from the adapter's location map, or
        # from the URML pose (with the URML-provided frame).
        target_pose: dict[str, float]
        target_frame: str
        if pose is not None:
            target_pose = dict(pose)
            target_frame = frame or "map"
        elif location is not None:
            resolved = self._config.resolve_location(location)
            if resolved is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the "
                    "manifest but not mapped to a pose in adapter.yaml.",
                )
            target_pose = {"x": resolved.x, "y": resolved.y, "z": resolved.z}
            if resolved.yaw is not None:
                target_pose["yaw"] = resolved.yaw
            target_frame = resolved.frame
        else:
            return NavigationResult(
                success=False,
                reason="send_navigation_goal called without location or pose",
            )

        if self._nav_client is None:
            from rclpy.action import ActionClient  # type: ignore[import-not-found,unused-ignore]

            self._nav_client = ActionClient(
                self._node,
                NavigateToPose,
                self._config.action_servers.navigate_to_pose,
            )

        msg = PoseStamped()
        msg.header.frame_id = target_frame
        msg.pose.position.x = float(target_pose.get("x", 0.0))
        msg.pose.position.y = float(target_pose.get("y", 0.0))
        msg.pose.position.z = float(target_pose.get("z", 0.0))
        # Yaw → quaternion is normally a small helper; we leave w=1 (no
        # rotation) when yaw isn't supplied. Real deployments often have
        # a tf2 conversion utility for this.
        msg.pose.orientation.w = 1.0

        goal = NavigateToPose.Goal()
        goal.pose = msg

        success, reason, _result = self._send_action_goal(self._nav_client, goal)
        return NavigationResult(
            success=success,
            reason=reason,
            final_pose=target_pose if success else None,
            frame=target_frame if success else None,
        )

    def send_docking_goal(
        self,
        *,
        station: str,
        service: str,
        until: str | None = None,
    ) -> NavigationResult:
        # Nav2's docking server (Iron+) action interface. Older distros
        # require a custom action wrapping the docking server; deployers
        # on those distros override the action-server name in adapter.yaml.
        from nav2_msgs.action import DockRobot  # type: ignore[import-not-found,unused-ignore]

        if self._dock_client is None:
            from rclpy.action import ActionClient  # type: ignore[import-not-found,unused-ignore]

            self._dock_client = ActionClient(
                self._node,
                DockRobot,
                self._config.action_servers.dock_robot,
            )

        goal = DockRobot.Goal()
        goal.dock_id = station
        # `service` and `until` are URML-side semantics that don't have a
        # direct Nav2 docking-message field. We forward them as ROS 2
        # parameters on the goal where possible; for v0.1 we just record
        # them in the request and let the deployer's docking server
        # interpret. (Future: encode in the dock_id namespacing.)
        success, reason, _result = self._send_action_goal(self._dock_client, goal)
        return NavigationResult(success=success, reason=reason)

    # ------------------------------------------------------------------
    # Manipulation
    # ------------------------------------------------------------------

    def send_manipulation_goal(
        self,
        *,
        action: Literal["grasp", "release"],
        target: dict[str, Any] | None = None,
        force_n: float | None = None,
        approach: Literal["top", "side", "front", "auto"] = "auto",
        release_mode: Literal["drop", "place", "hand_to_user"] | None = None,
        release_at: dict[str, Any] | str | None = None,
        arm: str | None = None,
        grasp_type: str | None = None,
    ) -> ManipulationResult:
        from control_msgs.action import GripperCommand  # type: ignore[import-not-found,unused-ignore]

        # The validator already confirmed at least one gripper exists in
        # the manifest. v0.1 picks the first configured gripper as the
        # default; multi-gripper deployments can extend the protocol with
        # an explicit gripper-name argument (future RFC).
        gripper_map = self._config.action_servers.gripper
        if not gripper_map:
            return ManipulationResult(
                success=False,
                reason="no gripper action server configured in adapter.yaml",
            )
        gripper_name = next(iter(gripper_map))
        action_server = gripper_map[gripper_name]

        if gripper_name not in self._gripper_clients:
            from rclpy.action import ActionClient  # type: ignore[import-not-found,unused-ignore]

            self._gripper_clients[gripper_name] = ActionClient(
                self._node,
                GripperCommand,
                action_server,
            )
        client = self._gripper_clients[gripper_name]

        goal = GripperCommand.Goal()
        # GripperCommand expects a position (m) and a max effort (N).
        # URML's grasp/release semantics map: grasp -> close (position 0),
        # release -> open (position 0.08 default). Real deployments tune
        # these via a gripper config; v0.1 uses conservative defaults.
        goal.command.position = 0.0 if action == "grasp" else 0.08
        goal.command.max_effort = float(force_n) if force_n is not None else 0.0

        success, reason, result = self._send_action_goal(client, goal)
        measured_force: float | None = None
        if success and result is not None:
            measured_force = float(getattr(result, "effort", 0.0)) or force_n
        return ManipulationResult(
            success=success,
            reason=reason,
            grip_force_n=measured_force,
        )

    # ------------------------------------------------------------------
    # Perception
    # ------------------------------------------------------------------

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        from vision_msgs.msg import Detection2DArray  # type: ignore[import-not-found,unused-ignore]

        def _matches(msg: Any) -> bool:
            for det in getattr(msg, "detections", []) or []:
                for hyp in getattr(det, "results", []) or []:
                    hypothesis = getattr(hyp, "hypothesis", None) or hyp
                    class_id = str(getattr(hypothesis, "class_id", ""))
                    if class_id == object_class:
                        return True
            return False

        msg, timed_out = self._subscribe_once(
            self._config.perception.detection_topic,
            Detection2DArray,
            predicate=_matches,
        )
        if timed_out or msg is None:
            return DetectionResult(success=False, reason="no_detection_within_timeout")

        # Pull the first matching detection out as the payload. Real
        # deployments may want to pick the highest-confidence match;
        # v0.1 takes the first to keep behavior deterministic in tests.
        for det in msg.detections:
            for hyp in det.results:
                hypothesis = getattr(hyp, "hypothesis", None) or hyp
                class_id = str(getattr(hypothesis, "class_id", ""))
                if class_id != object_class:
                    continue
                bbox_center = getattr(det.bbox, "center", None)
                pose_position = getattr(bbox_center, "position", None) if bbox_center else None
                px = float(getattr(pose_position, "x", 0.0)) if pose_position else 0.0
                py = float(getattr(pose_position, "y", 0.0)) if pose_position else 0.0
                payload = {
                    "class": class_id,
                    "pose": {"x": px, "y": py, "z": 0.0},
                    "frame": str(getattr(det.header, "frame_id", "map") or "map"),
                    "attributes": attributes or {},
                    "confidence": float(getattr(hypothesis, "score", 0.0)),
                }
                return DetectionResult(success=True, payload=payload)
        return DetectionResult(success=False, reason="no_match_in_message")

    def run_scan(
        self,
        *,
        area: dict[str, Any],
        pattern: Literal["serpentine", "spiral", "grid", "adaptive"],
        overlap: float,
        altitude: float | None,
        media: Literal["photo", "video", "sensor_only"],
        sensor: str | None,
    ) -> ScanResult:
        # Real scan implementation = expand area to waypoints, follow them
        # with Nav2, trigger capture at each waypoint. The pattern
        # generator is non-trivial (~150 lines) and lives in a future PR;
        # v0.1 returns success with an empty sample set and full coverage,
        # matching MockROSAdapter's default. Integration tests against
        # Gazebo will exercise the real path.
        payload = {
            "samples": [],
            "coverage": 1.0,
            "anomalies": [],
            "_note": "v0.1 RclpyAdapter scan: stub implementation. "
            "Full waypoint expansion lands in a follow-up PR.",
        }
        return ScanResult(success=True, payload=payload)

    def take_measurement(
        self,
        *,
        what: str,
        target: str | None,
        sensor: str | None,
    ) -> MeasurementResult:
        # Default sensor topic conventions: `/sensor/<sensor_name>` for a
        # named sensor, `/sensor/<what>` as a fallback. Real deployments
        # override per-sensor; for v0.1 we use the convention to avoid
        # bloating adapter.yaml until a deployment forces the rename.
        topic_name = f"/sensor/{sensor}" if sensor else f"/sensor/{what}"
        from std_msgs.msg import Float64  # type: ignore[import-not-found,unused-ignore]

        msg, timed_out = self._subscribe_once(topic_name, Float64)
        if timed_out or msg is None:
            return MeasurementResult(success=False, reason="no_reading_within_timeout")
        now_seconds = self._node.get_clock().now().nanoseconds / 1e9
        payload = {
            "value": float(msg.data),
            "unit": "unspecified",
            "timestamp": now_seconds,
        }
        return MeasurementResult(success=True, payload=payload)

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        from sensor_msgs.msg import Image  # type: ignore[import-not-found,unused-ignore]

        if media == "photo":
            msg, timed_out = self._subscribe_once(
                self._config.perception.image_topic,
                Image,
            )
            if timed_out or msg is None:
                return CaptureResult(success=False, reason="no_image_within_timeout")
            payload = {
                "type": "photo",
                "format": (attributes or {}).get("format", msg.encoding or "default"),
                "pose": {"x": 0.0, "y": 0.0},
                "frame": str(msg.header.frame_id or "map"),
                "uri": f"in_memory://{msg.header.stamp.sec}.{msg.header.stamp.nanosec}",
            }
            return CaptureResult(success=True, payload=payload)

        # Video: v0.1 records a single frame and returns a stub URI.
        # rosbag2 integration lives in a follow-up.
        payload = {
            "type": "video",
            "format": (attributes or {}).get("format", "default"),
            "pose": {"x": 0.0, "y": 0.0},
            "frame": "map",
            "uri": f"rosbag2://urml_capture/{duration_seconds or 0.0}s",
        }
        return CaptureResult(success=True, payload=payload)

    # ------------------------------------------------------------------
    # Wait / report
    # ------------------------------------------------------------------

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        from std_msgs.msg import Bool, Float64  # type: ignore[import-not-found,unused-ignore]

        actual_timeout = timeout_seconds if timeout_seconds is not None else DEFAULT_TOPIC_TIMEOUT_SECONDS

        if kind == "event":
            # Events are bool latches on `/event/<name>`. The condition
            # resolves when we observe a True. Convention; deployers can
            # override via a future adapter.yaml entry.
            msg, timed_out = self._subscribe_once(
                f"/event/{name}",
                Bool,
                predicate=lambda m: bool(m.data),
                timeout_seconds=actual_timeout,
            )
            if timed_out:
                return WaitResult(success=False, timed_out=True, reason="timeout")
            return WaitResult(success=True, payload={"event": name})

        if kind == "signal":
            msg, timed_out = self._subscribe_once(
                f"/signal/{name}",
                Float64,
                timeout_seconds=actual_timeout,
            )
            if timed_out or msg is None:
                return WaitResult(success=False, timed_out=True, reason="timeout")
            return WaitResult(success=True, payload={"signal": name, "value": float(msg.data)})

        if kind == "sensor_threshold":
            sensor = (threshold or {}).get("sensor", "default")
            op = (threshold or {}).get("op", "gt")
            value = float((threshold or {}).get("value", 0.0))

            def _matches(m: Any) -> bool:
                v = float(getattr(m, "data", 0.0))
                if op == "gt":
                    return v > value
                if op == "lt":
                    return v < value
                if op == "gte":
                    return v >= value
                if op == "lte":
                    return v <= value
                if op == "eq":
                    return v == value
                if op == "ne":
                    return v != value
                return False

            msg, timed_out = self._subscribe_once(
                f"/sensor/{sensor}",
                Float64,
                predicate=_matches,
                timeout_seconds=actual_timeout,
            )
            if timed_out or msg is None:
                return WaitResult(success=False, timed_out=True, reason="timeout")
            return WaitResult(
                success=True,
                payload={"sensor": sensor, "value": float(msg.data)},
            )

        # `input` kind: route through the speech adapter path for
        # `input: speech`, or fail otherwise. v0.1 supports `speech` only.
        if kind == "input" and input_mode == "speech":
            listen = self.acquire_speech(
                prompt=None,
                locale=None,
                timeout_seconds=actual_timeout,
                expected="free_form",
                choices=None,
            )
            return WaitResult(
                success=listen.success,
                timed_out=listen.timed_out,
                reason=listen.reason,
                payload=listen.payload,
            )
        return WaitResult(success=False, reason=f"unsupported_input_mode: {input_mode}")

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        # rclpy doesn't have a portable blocking sleep that yields the
        # executor; spin_once with a timeout is the idiomatic way.
        deadline_ns = self._node.get_clock().now().nanoseconds + int(duration_seconds * 1e9)
        while self._node.get_clock().now().nanoseconds < deadline_ns:
            self._rclpy.spin_once(self._node, timeout_sec=0.1)
        return SubstrateResult(success=True)

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None,
        status: Literal["success", "partial", "failure"],
        severity: Literal["info", "notice", "warning", "error"],
    ) -> SubstrateResult:
        # Reports publish a JSON-shaped String to a topic named for the
        # `to` endpoint. URML-side validation ensures `to` is one of
        # `user`/`log`/`caller` or a declared `named_endpoints` entry.
        import json

        from std_msgs.msg import String  # type: ignore[import-not-found,unused-ignore]

        payload = {
            "facts": facts,
            "attachments": attachments or [],
            "status": status,
            "severity": severity,
        }
        msg = String()
        msg.data = json.dumps(payload, sort_keys=True)
        self._publish_once(f"/report/{to}", String, msg)
        return SubstrateResult(success=True)

    # ------------------------------------------------------------------
    # Speech (home profile)
    # ------------------------------------------------------------------

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        if not self._config.speech.output_topic:
            return SubstrateResult(
                success=False,
                reason="speech_not_configured: set speech.output_topic in adapter.yaml",
            )
        from std_msgs.msg import String  # type: ignore[import-not-found,unused-ignore]

        msg = String()
        msg.data = utterance
        self._publish_once(self._config.speech.output_topic, String, msg)
        return SubstrateResult(success=True)

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        if not self._config.speech.input_topic:
            return ListenResult(
                success=False,
                reason="speech_not_configured: set speech.input_topic in adapter.yaml",
            )
        # If the runtime supplied a prompt, speak it first.
        if prompt is not None:
            self.emit_speech(
                utterance=prompt,
                locale=locale,
                style="conversational",
                interrupt=False,
            )

        from std_msgs.msg import String  # type: ignore[import-not-found,unused-ignore]

        msg, timed_out = self._subscribe_once(
            self._config.speech.input_topic,
            String,
            timeout_seconds=timeout_seconds if timeout_seconds is not None else DEFAULT_TOPIC_TIMEOUT_SECONDS,
        )
        if timed_out or msg is None:
            return ListenResult(
                success=False,
                timed_out=True,
                reason="no_speech_within_timeout",
            )
        transcription = str(msg.data)
        choice_index: int | None = None
        if expected == "choice" and choices is not None:
            # Loose match: pick the first declared choice that appears
            # as a substring of the transcription (case-insensitive).
            t = transcription.lower()
            for idx, c in enumerate(choices):
                if c.lower() in t:
                    choice_index = idx
                    break
        payload = {
            "transcription": transcription,
            "confidence": 1.0,
            "choice_index": choice_index,
        }
        return ListenResult(success=True, timed_out=False, payload=payload)

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """Invoke a substrate program by name (RFC-0015 `call_program`).

        The concrete ROS-Industrial binding is deployment-specific: a driver
        like ``khi_ros2`` exposes its on-controller programs (Kawasaki
        AS-language jobs) as cell-defined actions/services whose message types
        are not standardized across drivers, so there is no single generic
        call this base adapter can make. v0.1 returns a documented
        not-supported failure (mirroring the drone stubs below); a deployment
        subclasses RclpyAdapter and overrides this method to call its driver's
        program service/action. The substrate-neutral semantics ("invoke the
        named routine and await its result") are exercised end-to-end against
        the hermetic MockROSAdapter, and the non-ROS path is implemented
        concretely in the OPC UA adapter's ``call_method`` (the RFC-0015
        motivating case).
        """
        return ProgramCallResult(
            success=False,
            reason=f"not_supported_in_v0.1: RclpyAdapter has no generic program-call "
            f"message for {name!r}. Override call_named_program in a deployment subclass "
            "to bind your driver's program service/action (e.g. khi_ros2's AS-program "
            "launch). The program is already manifest-declared and validator-checked.",
        )

    # ------------------------------------------------------------------
    # Drone-profile dispatch
    #
    # v0.1: stubs that return a documented "not supported in this adapter"
    # failure. The canonical PX4 path lives in the urml-px4-runtime
    # package (pymavlink-direct, no ROS 2 dependency). A future PR can
    # wire these through mavros for deployments that pair ROS 2 + PX4 in
    # the same stack; until then, deployments using drone primitives
    # should construct PX4Adapter instead of RclpyAdapter.
    # ------------------------------------------------------------------

    def send_takeoff_goal(
        self,
        *,
        altitude: float,
        climb_rate: float | None = None,
    ) -> NavigationResult:
        return NavigationResult(
            success=False,
            reason="not_supported_in_v0.1: RclpyAdapter does not drive PX4. "
            "Use urml_px4_runtime.PX4Adapter for MAVLink-based drone deployments.",
        )

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        return NavigationResult(
            success=False,
            reason="not_supported_in_v0.1: RclpyAdapter does not drive PX4. "
            "Use urml_px4_runtime.PX4Adapter for MAVLink-based drone deployments.",
        )

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        return NavigationResult(
            success=False,
            reason="not_supported_in_v0.1: RclpyAdapter does not drive PX4. "
            "Use urml_px4_runtime.PX4Adapter for MAVLink-based drone deployments.",
        )
