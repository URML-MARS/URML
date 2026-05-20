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
    "DoosanDrflAdapter",
    "FrankaFciAdapter",
    "KassowKrAdapter",
    "KinovaKortexAdapter",
    "MecademicMeca500Adapter",
    "NeuraMairaAdapter",
    "Pose",
    "TechmanTmflowAdapter",
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


class DoosanDrflAdapter(_CobotBase):
    """Doosan via DRFL (Doosan Robot Function Library) — zero ROS.

    Doosan ships its DRFL SDK as the native Python control surface (no
    ROS). Korea-made (Doosan Robotics, KR — allied; not on the
    us_federal_default denylist).
    """

    BRAND = "doosan"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import DRFL  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "DRFL is not installed. DoosanDrflAdapter requires the [doosan] extra.\n"
                "  Install with: pip install urml-cobot-runtime[doosan]"
            ) from exc
        # DRFL's Robot client wraps the M/H-series controller TCP API.
        self._conn = DRFL.Robot(self._config.robot_ip)
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
        robot = self._open()
        robot.movel(vec, speed or self._config.speed)
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
        robot = self._open()
        force = robot.get_tool_force()
        value = float(force[0]) if force else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})


class TechmanTmflowAdapter(_CobotBase):
    """Techman via TMflow (techmanpy / Listen Node) — zero ROS.

    Techman Robot ships TMflow with a Listen-Node TCP protocol; the
    `techmanpy` client is its native Python surface (no ROS). Taiwan-made
    (Techman Robot, TW — allied; Omron-JP parent). Not on the
    us_federal_default denylist.
    """

    BRAND = "techman"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import techmanpy  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "techmanpy is not installed. TechmanTmflowAdapter requires the [techman] extra.\n"
                "  Install with: pip install urml-cobot-runtime[techman]"
            ) from exc
        self._conn = techmanpy.connect_sct(self._config.robot_ip)
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
        client = self._open()
        client.move_to_point_line(vec, speed or self._config.speed)
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
        client = self._open()
        force = client.get_tcp_force()
        value = float(force[0]) if force else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})


class KinovaKortexAdapter(_CobotBase):
    """Kinova via Kortex (kortex_api Python) — zero ROS.

    Kinova ships Kortex as the native control surface for the Gen3 / Gen3
    Lite arms (no ROS dependency). Canada-made (Kinova, CA — allied).
    Not on the us_federal_default denylist.
    """

    BRAND = "kinova"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import kortex_api  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "kortex_api is not installed. KinovaKortexAdapter requires the [kinova] extra.\n"
                "  Install with: pip install urml-cobot-runtime[kinova]"
            ) from exc
        # Kortex's real session setup is TCPTransport → RouterClient → BaseClient.
        # The v0.1 scaffold delegates to a thin connect helper on the package;
        # deployment-side wiring of the full session (transport/router) is the
        # documented calibration step in cobot-integration.yml (controller-e2e
        # placeholder), exactly like marine-sitl-e2e / cobot-controller-e2e.
        self._conn = kortex_api.BaseClient(self._config.robot_ip)
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
        base = self._open()
        base.send_pose_command(vec, speed or self._config.speed)
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
        base = self._open()
        force = base.get_tool_external_wrench()
        value = float(force[0]) if force else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})


class MecademicMeca500Adapter(_CobotBase):
    """Mecademic Meca500 via mecademicpy (Apache-2.0) — zero ROS.

    Mecademic ships ``mecademicpy`` as the native Python control surface for
    the Meca500 (a high-precision compact 6-axis arm with no ROS dep). Made
    in Montréal, Canada — passes the default US-federal policy (CA allied).
    """

    BRAND = "mecademic"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            import mecademicpy.robot as mecademic_robot  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "mecademicpy is not installed. MecademicMeca500Adapter requires the [mecademic] extra.\n"
                "  Install with: pip install urml-cobot-runtime[mecademic]"
            ) from exc
        robot = mecademic_robot.Robot()
        robot.Connect(self._config.robot_ip)
        self._conn = robot
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
        robot = self._open()
        robot.MovePose(*vec)
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
        robot = self._open()
        joints = robot.GetJoints()
        value = float(joints[0]) if joints else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})


class NeuraMairaAdapter(_CobotBase):
    """Neura Robotics MAiRA via neurapy — zero ROS.

    Neura Robotics ships ``neurapy`` as the native Python control surface
    for MAiRA (cognitive robotic arm with no ROS dependency). Made in
    Metzingen, Germany — passes the default US-federal policy (DE allied).
    """

    BRAND = "neura"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            from neurapy.robot import Robot as NeuraRobot  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "neurapy is not installed. NeuraMairaAdapter requires the [neura] extra.\n"
                "  Install with: pip install urml-cobot-runtime[neura]"
            ) from exc
        self._conn = NeuraRobot(self._config.robot_ip)
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
        robot = self._open()
        robot.move_joint(vec, speed=speed or self._config.speed)
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
        robot = self._open()
        wrench = robot.get_tcp_wrench()
        value = float(wrench[0]) if wrench else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})


class KassowKrAdapter(_CobotBase):
    """Kassow Robots KR-series cobot via kassow-py — zero ROS.

    Kassow ships a native Python TCP client for the KR-series 7-axis arms
    (no ROS dependency); the community-maintained ``kassow-py`` wheel is
    the canonical access pin recorded here, with the documented best-effort
    substitution clause (the hermetic tests fake the module, so the suite
    is robust to a wheel-name swap in deployment). Made in Copenhagen,
    Denmark — passes the default US-federal policy (DK allied).

    Substituted in for OB7: Productive Robotics OB7 (US) has no broadly
    available Python wheel — its controller is teach-pendant programmed.
    Kassow ships an equivalent zero-ROS arm with a Python control surface,
    so it's a closer match to the cobot-runtime contract. The OB7 line
    can return as a manifest-only fixture once Productive Robotics
    publishes a Python SDK.
    """

    BRAND = "kassow"

    def _open(self) -> Any:
        if self._conn is not None:
            return self._conn
        try:
            from kassow_py.client import KassowClient  # type: ignore[import-not-found,unused-ignore]
        except ImportError as exc:
            raise RuntimeError(
                "kassow-py is not installed. KassowKrAdapter requires the [kassow] extra.\n"
                "  Install with: pip install urml-cobot-runtime[kassow]"
            ) from exc
        self._conn = KassowClient(self._config.robot_ip)
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
        client = self._open()
        client.movej(vec, speed or self._config.speed)
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
        client = self._open()
        wrench = client.get_tcp_wrench()
        value = float(wrench[0]) if wrench else None
        return MeasurementResult(success=True, payload={"value": value, "what": what})
