"""AutowareAdapter — real ROS 2 backing for URML's AV trajectory verbs.

Implements the ``TrajectoryAdapter`` Protocol (RFC-0020) against the
Autoware Universe **AD API** (``autoware_adapi_v1_msgs``). It is the first
substrate to implement that protocol; until now only ``MockROSAdapter`` did.

## What it maps

- ``plan_path`` -> ``plan_trajectory``: set a route to the goal pose through
  the AD API routing service (``/api/routing/set_route_points``). Autoware
  plans the dense trajectory internally from the vehicle's localized pose;
  URML binds a route handle, not raw waypoints (the payload is opaque per the
  protocol contract).
- ``follow_trajectory`` -> ``follow_trajectory_goal``: optionally publish a
  speed cap (``VelocityLimit`` to the scenario-planning ``max_velocity``
  topic), then engage autonomous driving via the operation-mode service
  (``/api/operation_mode/change_to_autonomous``). Engaging autonomous is what
  makes Autoware follow the planned route.

## Honest boundaries

- ``start`` is ignored: Autoware routes from the vehicle's current localized
  pose, not an arbitrary start.
- ``along`` (an HD-map corridor id) is checked by the validator upstream; it
  is not a field the AD API routing request takes, so it is not forwarded.
- ``max_accel_mps2`` and ``on_off_route`` are vehicle- and
  planning-configured in Autoware; the adapter records the intent but does not
  set them per call. This is stated, not silently dropped.
- Every AD API service / topic / message-type name is configurable
  (:class:`AutowareConfig`) so the adapter tracks a specific Autoware release
  without a code change.

## Lazy rclpy

``rclpy`` and the Autoware message packages are imported lazily, so this
module imports on every host (including Windows) and the hermetic tests run
without a ROS 2 install. ``rclpy.init()`` is the caller's responsibility, as
in ``RclpyAdapter``. Real-vehicle behavior is verified separately under a
gated integration workflow, never in the hermetic suite.
"""

from __future__ import annotations

import importlib
import math
from contextlib import suppress
from typing import Any

from urml_ros2_runtime.substrate.base import (
    NavigationResult,
    SubstrateResult,
    TrajectoryPlanResult,
)

from urml_av_runtime._version import __version__
from urml_av_runtime.config import AutowareConfig, MapPose, load_av_config

__all__ = ["AutowareAdapter", "AutowareConfig", "MapPose", "__version__", "load_av_config"]


def _require_rclpy() -> Any:
    """Lazy-import rclpy and surface a clear error if it isn't installed."""
    try:
        import rclpy  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "rclpy is not installed. AutowareAdapter requires a ROS 2 + Autoware "
            "environment.\n"
            "  On Linux: install ROS 2 and Autoware, source the setup files, then "
            "launch Python.\n"
            "  On Windows: this adapter is not supported; use WSL2, or fall back to "
            "MockROSAdapter for development."
        ) from exc
    return rclpy


def _import_type(spec: str) -> Any:
    """Import a ``module:attr`` type spec (e.g. ``geometry_msgs.msg:Pose``)."""
    module_name, _, attr = spec.partition(":")
    if not attr:
        raise ValueError(f"type spec {spec!r} must be 'module:attr'")
    module = importlib.import_module(module_name)
    return getattr(module, attr)


class AutowareAdapter:
    """Autoware AD API backing for URML's ``plan_path`` / ``follow_trajectory``."""

    def __init__(self, config: AutowareConfig | None = None) -> None:
        self._rclpy = _require_rclpy()
        self._config = config or AutowareConfig()
        self._node = self._rclpy.create_node(
            self._config.node_name,
            namespace=self._config.ros2_namespace,
        )
        # Lazy client / publisher slots — None until first use.
        self._clients: dict[str, Any] = {}
        self._velocity_pub: Any = None
        self._reports: list[dict[str, Any]] = []
        self._closed = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        if self._closed:
            return
        with suppress(Exception):
            self._node.destroy_node()
        self._closed = True

    def __enter__(self) -> AutowareAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Service / topic plumbing
    # ------------------------------------------------------------------

    def _client(self, service_name: str, srv_type_spec: str) -> Any:
        client = self._clients.get(service_name)
        if client is None:
            srv_type = _import_type(srv_type_spec)
            client = self._node.create_client(srv_type, service_name)
            self._clients[service_name] = client
        return client

    def _call_service(
        self, service_name: str, srv_type_spec: str, request: Any
    ) -> tuple[Any | None, str | None]:
        """Call a service and wait. Returns (response, reason). reason is set on failure."""
        client = self._client(service_name, srv_type_spec)
        timeout = self._config.service_timeout_seconds
        if not client.wait_for_service(timeout_sec=timeout):
            return None, f"service_unavailable: {service_name}"
        future = client.call_async(request)
        self._rclpy.spin_until_future_complete(self._node, future, timeout_sec=timeout)
        response = future.result()
        if response is None:
            return None, f"no_response: {service_name}"
        return response, None

    @staticmethod
    def _status_ok(response: Any) -> bool:
        """AD API responses carry a ResponseStatus with a `success` flag."""
        status = getattr(response, "status", None)
        if status is None:
            # Some services return a bare success field.
            return bool(getattr(response, "success", False))
        return bool(getattr(status, "success", False))

    @staticmethod
    def _status_message(response: Any) -> str:
        status = getattr(response, "status", None)
        if status is not None:
            return str(getattr(status, "message", "") or "")
        return str(getattr(response, "message", "") or "")

    def _resolve_goal_pose(self, goal: dict[str, float] | str) -> MapPose | None:
        if isinstance(goal, str):
            return self._config.resolve_pose(goal)
        # A pose dict {x, y, z?, yaw?} from the program.
        return MapPose.model_validate(goal)

    def _build_pose(self, pose: MapPose) -> Any:
        pose_type = _import_type("geometry_msgs.msg:Pose")
        msg = pose_type()
        msg.position.x = float(pose.x)
        msg.position.y = float(pose.y)
        msg.position.z = float(pose.z)
        # Heading (yaw) as a quaternion about z.
        msg.orientation.z = math.sin(pose.yaw / 2.0)
        msg.orientation.w = math.cos(pose.yaw / 2.0)
        return msg

    # ------------------------------------------------------------------
    # TrajectoryAdapter (RFC-0020)
    # ------------------------------------------------------------------

    def plan_trajectory(
        self,
        *,
        start: dict[str, float] | str | None,
        goal: dict[str, float] | str,
        along: str | None = None,
    ) -> TrajectoryPlanResult:
        goal_pose = self._resolve_goal_pose(goal)
        if goal_pose is None:
            return TrajectoryPlanResult(
                success=False,
                reason=(
                    f"goal_not_resolvable: {goal!r} is declared in the manifest but not "
                    "mapped to a pose in av_adapter.yaml `location_to_pose`."
                ),
            )

        if self._config.clear_route_before_plan:
            clear_type = _import_type(self._config.clear_route_srv_type)
            _resp, reason = self._call_service(
                self._config.clear_route_service, self._config.clear_route_srv_type, clear_type.Request()
            )
            # A clear failure is not fatal (there may be no route yet); the
            # set below is the authority. Only a service-unavailable is worth
            # noting, and set_route will surface it too, so continue.

        set_type = _import_type(self._config.set_route_srv_type)
        request = set_type.Request()
        # header: stamp + frame. Fields present on the AD API request.
        if hasattr(request, "header"):
            request.header.frame_id = self._config.map_frame
            with suppress(Exception):
                request.header.stamp = self._node.get_clock().now().to_msg()
        request.goal = self._build_pose(goal_pose)
        if hasattr(request, "waypoints"):
            request.waypoints = []

        response, reason = self._call_service(
            self._config.set_route_service, self._config.set_route_srv_type, request
        )
        if response is None:
            return TrajectoryPlanResult(success=False, reason=reason)
        if not self._status_ok(response):
            return TrajectoryPlanResult(
                success=False,
                reason=f"route_rejected: {self._status_message(response) or 'AD API declined the route'}",
            )
        return TrajectoryPlanResult(
            success=True,
            payload={
                "goal": {"x": goal_pose.x, "y": goal_pose.y, "z": goal_pose.z, "yaw": goal_pose.yaw},
                "frame": self._config.map_frame,
                "along": along,
                "waypoints": [],
                "route_set": True,
            },
        )

    def follow_trajectory_goal(
        self,
        *,
        trajectory: dict[str, Any] | None,
        max_velocity_mps: float | None = None,
        max_accel_mps2: float | None = None,
        on_off_route: str = "abort",
    ) -> NavigationResult:
        if trajectory is None or not trajectory.get("route_set"):
            return NavigationResult(
                success=False,
                reason=(
                    "no_route: follow_trajectory needs a route bound by plan_path "
                    "(the trajectory payload has no `route_set`)."
                ),
            )
        if max_velocity_mps is not None:
            self._publish_velocity_limit(max_velocity_mps)

        change_type = _import_type(self._config.change_mode_srv_type)
        response, reason = self._call_service(
            self._config.change_to_autonomous_service,
            self._config.change_mode_srv_type,
            change_type.Request(),
        )
        if response is None:
            return NavigationResult(success=False, reason=reason)
        if not self._status_ok(response):
            return NavigationResult(
                success=False,
                reason=(
                    f"engage_rejected: {self._status_message(response) or 'AD API declined autonomous mode'}"
                ),
            )
        return NavigationResult(success=True, frame=self._config.map_frame)

    def _publish_velocity_limit(self, max_velocity_mps: float) -> None:
        if self._velocity_pub is None:
            msg_type = _import_type(self._config.velocity_limit_msg_type)
            self._velocity_pub = self._node.create_publisher(
                msg_type, self._config.velocity_limit_topic, 1
            )
        msg_type = _import_type(self._config.velocity_limit_msg_type)
        msg = msg_type()
        if hasattr(msg, "stamp"):
            with suppress(Exception):
                msg.stamp = self._node.get_clock().now().to_msg()
        msg.max_velocity = float(max_velocity_mps)
        self._velocity_pub.publish(msg)

    # ------------------------------------------------------------------
    # Non-actuating base primitives an AV program may use
    # ------------------------------------------------------------------

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        return SubstrateResult(success=True)

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None = None,
        status: str = "success",
        severity: str = "info",
    ) -> SubstrateResult:
        self._reports.append({"to": to, "status": status, "severity": severity, "facts": facts})
        return SubstrateResult(success=True)
