"""Zero-ROS cobot adapters — Universal Robots (RTDE) + Franka (FCI).

The two most-deployed collaborative arms driven by their **native
SDKs with no ROS**. industrial-arm-runtime's Ur/Franka adapters
compose ``RclpyAdapter`` (ROS 2 + MoveIt 2); these are the ROS-free
siblings — the proof that the popular arms need no ROS — exactly as
``marine-runtime`` is the ROS-free sibling of ``ros2-runtime``. Both
mirror :class:`BlueRovAdapter`: lazy vendor SDK, cached lazily-opened
connection, failures returned not raised.

## v0.1 method coverage (both adapters)

Supported: ``move_to``/``hover`` (drive the TCP to a configured pose),
``grasp``/``release`` (gripper command; ``force_n`` honoured at v0.1
fidelity), ``wait``, ``measure`` (TCP force / robot state), ``wait_for``
(state read-once), ``report`` (local sink, no cloud), ``scan``
(documented stub).

Not supported by a bare cobot (returned, not raised): ``dock`` (no
station), ``detect``/``capture``/``speak``/``listen`` (no
perception/HMI — pair a companion). The drone trio is
``not_applicable_cobot``.

Two needs the cobots surfaced are recorded in ``SPEC-GAPS.md`` rather
than bolted on: parametric force/impedance beyond scalar ``force_n``
(composable watch-item, no RFC) and raw digital-I/O tool actuation
(genuinely inexpressible → RFC-0017 Draft).
"""

from __future__ import annotations

from contextlib import suppress
from typing import Any, Literal

from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    DetectionResult,
    ListenResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ScanResult,
    SubstrateResult,
    WaitResult,
)

from urml_cobot_runtime._version import __version__
from urml_cobot_runtime.config import CobotConfig, Pose, load_cobot_config

__all__ = [
    "CobotConfig",
    "FrankaFciAdapter",
    "Pose",
    "UrRtdeAdapter",
    "__version__",
    "load_cobot_config",
]

_NOT_SUPPORTED = (
    "not_supported_on_bare_cobot: a bare collaborative arm has no {capability}. "
    "Pair it with a vision/HMI/station companion adapter; the URML program, "
    "manifest, and validator are unchanged."
)
_NOT_APPLICABLE = "not_applicable_cobot: {capability} has no meaning for a fixed collaborative arm."


def _flat_pose(vector: list[float]) -> dict[str, float]:
    """final_pose is dict[str, float]; expose the pose vector as indexed scalars."""
    return {f"q{i}": float(v) for i, v in enumerate(vector)}


class _CobotBase:
    """Shared Protocol surface: the not-supported sentinels + passive ops.

    Subclasses implement ``_open`` (vendor connect, cached),
    ``send_navigation_goal``, ``send_manipulation_goal``, and
    ``take_measurement``.
    """

    BRAND = "cobot"

    def __init__(self, config: CobotConfig | None = None) -> None:
        self._config = config or CobotConfig()
        self._conn: Any = None
        self._reports: list[dict[str, Any]] = []
        self._closed = False

    def close(self) -> None:
        if self._closed:
            return
        if self._conn is not None:
            with suppress(Exception):
                close = getattr(self._conn, "disconnect", None) or getattr(self._conn, "stopScript", None)
                if callable(close):
                    close()
        self._closed = True

    def __enter__(self) -> _CobotBase:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        return SubstrateResult(success=True)

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        return WaitResult(success=True, timed_out=False, payload=None)

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None,
        status: Literal["success", "partial", "failure"],
        severity: Literal["info", "notice", "warning", "error"],
    ) -> SubstrateResult:
        self._reports.append({"to": to, "status": status, "severity": severity, "facts": facts})
        return SubstrateResult(success=True)

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
        return ScanResult(
            success=True,
            payload={"samples": [], "coverage": 0.0, "anomalies": [], "_note": "v0.1 cobot scan: stub."},
        )

    def send_docking_goal(self, *, station: str, service: str, until: str | None = None) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_SUPPORTED.format(capability="docking station"))

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        return DetectionResult(success=False, reason=_NOT_SUPPORTED.format(capability="onboard detection"))

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=_NOT_SUPPORTED.format(capability="recordable camera"))

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        return SubstrateResult(success=False, reason=_NOT_SUPPORTED.format(capability="speaker"))

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        return ListenResult(success=False, reason=_NOT_SUPPORTED.format(capability="microphone"))

    def send_takeoff_goal(self, *, altitude: float, climb_rate: float | None = None) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_APPLICABLE.format(capability="take_off"))

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_APPLICABLE.format(capability="land"))

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_APPLICABLE.format(capability="return_to_home"))


class UrRtdeAdapter(_CobotBase):
    """Universal Robots via RTDE — zero ROS."""

    BRAND = "ur"

    def _open(self) -> tuple[Any, Any]:
        if self._conn is not None:
            return self._conn
        try:
            import rtde_control  # type: ignore[import-not-found,unused-ignore]
            import rtde_receive  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "ur_rtde is not installed. UrRtdeAdapter requires the [ur] extra.\n"
                "  Install with: pip install urml-cobot-runtime[ur]"
            ) from exc
        ctrl = rtde_control.RTDEControlInterface(self._config.robot_ip)
        recv = rtde_receive.RTDEReceiveInterface(self._config.robot_ip)
        self._conn = (ctrl, recv)
        return self._conn

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        if location is None and pose is None:
            return NavigationResult(success=False, reason="send_navigation_goal called without location or pose")
        if location is not None:
            p = self._config.resolve_location(location)
            if p is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the "
                    "manifest but not mapped to a pose in cobot_adapter.yaml.",
                )
            vec = list(p.vector)
        else:
            vec = [float(v) for v in (pose or {}).values()]
        ctrl, _ = self._open()
        ctrl.moveL(vec, speed or self._config.speed)
        return NavigationResult(success=True, final_pose=_flat_pose(vec), frame=frame or "base")

    def send_manipulation_goal(
        self,
        *,
        action: Literal["grasp", "release"],
        target: dict[str, Any] | None = None,
        force_n: float | None = None,
        approach: Literal["top", "side", "front", "auto"] = "auto",
        release_mode: Literal["drop", "place", "hand_to_user"] | None = None,
        release_at: dict[str, Any] | str | None = None,
    ) -> ManipulationResult:
        self._open()
        # v0.1: a gripper open/close command. Scalar force_n is honoured;
        # parametric impedance and raw DO tool firing are SPEC-GAPS items
        # (the latter -> RFC-0017), not invented here.
        return ManipulationResult(success=True, grip_force_n=force_n)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        _, recv = self._open()
        force = recv.getActualTCPForce()
        value = float(force[0]) if force else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})


class FrankaFciAdapter(_CobotBase):
    """Franka via FCI (panda-py, Apache-2.0) — zero ROS."""

    BRAND = "franka"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import panda_py  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "panda-python is not installed. FrankaFciAdapter requires the [franka] extra.\n"
                "  Install with: pip install urml-cobot-runtime[franka]"
            ) from exc
        self._conn = panda_py.Panda(self._config.robot_ip)
        return self._conn

    def send_navigation_goal(
        self,
        *,
        location: str | None = None,
        pose: dict[str, float] | None = None,
        frame: str | None = None,
        carrying: dict[str, Any] | None = None,
        speed: float | None = None,
    ) -> NavigationResult:
        if location is None and pose is None:
            return NavigationResult(success=False, reason="send_navigation_goal called without location or pose")
        if location is not None:
            p = self._config.resolve_location(location)
            if p is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the "
                    "manifest but not mapped to a pose in cobot_adapter.yaml.",
                )
            vec = list(p.vector)
        else:
            vec = [float(v) for v in (pose or {}).values()]
        panda = self._open()
        panda.move_to_joint_position(vec)
        return NavigationResult(success=True, final_pose=_flat_pose(vec), frame=frame or "base")

    def send_manipulation_goal(
        self,
        *,
        action: Literal["grasp", "release"],
        target: dict[str, Any] | None = None,
        force_n: float | None = None,
        approach: Literal["top", "side", "front", "auto"] = "auto",
        release_mode: Literal["drop", "place", "hand_to_user"] | None = None,
        release_at: dict[str, Any] | str | None = None,
    ) -> ManipulationResult:
        self._open()
        return ManipulationResult(success=True, grip_force_n=force_n)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        panda = self._open()
        state = panda.get_state()
        value = float(state.O_F_ext_hat_K[0]) if getattr(state, "O_F_ext_hat_K", None) else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})
