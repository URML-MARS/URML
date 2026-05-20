"""ROS-Industrial / MoveIt 2 arm adapters — one first-class class per vendor.

An industrial manipulator is a fixed-base arm. Its load-bearing URML
primitives are ``grasp`` / ``release`` (a gripper action) and ``move_to``
(an end-effector / named-pose move via MoveIt 2). That dispatch shape is
*identical* to the one the ROS 2 runtime's :class:`RclpyAdapter` already
implements (``control_msgs/GripperCommand`` for the gripper,
``nav2_msgs/NavigateToPose``-style action send-and-wait for moves). So the
substrate plumbing is single-sourced: each brand adapter **composes** a
:class:`RclpyAdapter` rather than re-implementing MoveIt 2.

The per-brand surface is still real and first-class: :class:`AbbAdapter`,
:class:`FanucAdapter`, :class:`KukaAdapter`, :class:`YaskawaAdapter` are
distinct classes with distinct default configs (the vendor's
ROS-Industrial action-server conventions) and a brand-scoped
not-supported tag. "One adapter per brand", no duplicated substrate code.

A bare arm has no mobile base, no flight, and no onboard
perception/speech. Those primitives return a documented
``not_supported_on_industrial_arm[<brand>]`` result rather than raising —
the same pattern :class:`PX4Adapter` uses for
``not_supported_on_bare_autopilot``. A work-cell that pairs an arm with a
vision system dispatches detection through a companion adapter, exactly
as the drone stack pairs flight with a ROS 2 companion. The URML program,
manifest, and validator are unchanged and unaware.

## rclpy is lazy

Importing this module works on every host (Windows included): the
``rclpy`` import lives inside :class:`RclpyAdapter` and only fires when an
adapter is *constructed*. Constructing a brand adapter therefore needs a
sourced ROS 2 environment (the ROS-Industrial driver + MoveIt 2 for that
arm), just like :class:`RclpyAdapter`. Hermetic tests inject a fake inner
adapter via the ``inner_factory`` hook and never touch rclpy.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import Any, Literal

from urml_ros2_runtime.substrate.adapter_config import ActionServerConfig, AdapterConfig
from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    DetectionResult,
    ListenResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ROSAdapter,
    ScanResult,
    SubstrateResult,
    WaitResult,
)
from urml_ros2_runtime.substrate.rclpy_adapter import RclpyAdapter

from urml_industrial_arm_runtime._version import __version__

__all__ = [
    "AbbAdapter",
    "ComauAdapter",
    "DensoAdapter",
    "EpsonAdapter",
    "FanucAdapter",
    "FrankaAdapter",
    "HanwhaAdapter",
    "HyundaiAdapter",
    "IndustrialArmAdapter",
    "KawasakiAdapter",
    "KukaAdapter",
    "MitsubishiAdapter",
    "NachiAdapter",
    "OmronAdapter",
    "StaubliAdapter",
    "UrAdapter",
    "YaskawaAdapter",
    "__version__",
]

# The not-supported sentinel for every primitive a bare fixed-base arm
# cannot serve. Extracted so tests can match exactly, mirroring
# PX4Adapter._NOT_SUPPORTED_REASON.
_NOT_SUPPORTED_TEMPLATE = (
    "not_supported_on_industrial_arm[{brand}]: a fixed-base manipulator has no "
    "{capability}. Pair the arm with a companion adapter (vision / mobile base) "
    "for full coverage; the URML program, manifest, and validator are unchanged."
)

# v0.1 ROS-Industrial action-server conventions per vendor. These are the
# vanilla-install defaults a deployer typically keeps; sites that
# namespace their cells override them in an adapter.yaml, exactly as
# RclpyAdapter documents for its own AdapterConfig.
_BRAND_GRIPPER_SERVER = {
    "abb": "/abb/gripper/gripper_cmd",
    "fanuc": "/fanuc/gripper/gripper_cmd",
    "kuka": "/kuka/gripper/gripper_cmd",
    "yaskawa": "/motoman/gripper/gripper_cmd",  # YASKAWA's ROS-Industrial driver is `motoman`.
    "ur": "/ur/robotiq_gripper/gripper_cmd",  # UR cobots most commonly carry a Robotiq gripper.
    "franka": "/franka/franka_gripper/gripper_cmd",  # Franka's ROS package is `franka_gripper`.
    "kawasaki": "/kawasaki/gripper/gripper_cmd",  # Kawasaki's ROS package is `kawasaki_robot`.
    "staubli": "/staubli/gripper/gripper_cmd",  # Stäubli VAL3 driver — `staubli_val3_driver`.
    "comau": "/comau/gripper/gripper_cmd",  # Comau ROS 2 driver — `comau_ros2_driver`.
    "mitsubishi": "/melfa/gripper/gripper_cmd",  # Mitsubishi Electric MELFA — `melfa_ros2`.
    "denso": "/denso/gripper/gripper_cmd",  # Denso — `denso_robot_ros2`.
    "hyundai": "/hyundai/gripper/gripper_cmd",  # Hyundai Robotics — `hyundai_robot_ros2`.
    "nachi": "/nachi/gripper/gripper_cmd",  # Nachi-Fujikoshi — `nachi_robot_ros2`.
    "epson": "/epson/gripper/gripper_cmd",  # Seiko Epson — `epson_robot_ros2`.
    "omron": "/omron/gripper/gripper_cmd",  # Omron (Adept legacy) — `omron_industrial_robot`.
    "hanwha": "/hanwha/gripper/gripper_cmd",  # Hanwha HCR cobot via ROS — `hanwha_hcr_ros2`.
}

InnerFactory = Callable[[], ROSAdapter]


class IndustrialArmAdapter:
    """Shared core: a brand arm adapter over a composed RclpyAdapter.

    Subclasses set :pyattr:`BRAND` and may override :pymeth:`default_config`.
    Construct with no arguments to use the brand default config, or pass an
    :class:`AdapterConfig` to point at a specific cell's action servers.
    """

    #: Vendor tag — overridden by each brand subclass. Surfaces in the
    #: not-supported reason and the default node name.
    BRAND: str = "generic"

    def __init__(
        self,
        config: AdapterConfig | None = None,
        *,
        node_name: str | None = None,
        inner_factory: InnerFactory | None = None,
    ) -> None:
        self._config = config or self.default_config()
        node = node_name or f"urml_{self.BRAND}_arm"
        factory: InnerFactory = inner_factory or (lambda: RclpyAdapter(self._config, node_name=node))
        self._inner: ROSAdapter = factory()
        self._closed = False

    @classmethod
    def default_config(cls) -> AdapterConfig:
        """Brand-default deployment config (ROS-Industrial conventions).

        ``move_group`` is MoveIt 2's vanilla ``/move_action``. The gripper
        action server follows the vendor's ROS-Industrial driver naming.
        A real cell overrides these in an adapter.yaml.
        """
        gripper_server = _BRAND_GRIPPER_SERVER.get(cls.BRAND, "/gripper/gripper_cmd")
        return AdapterConfig(
            action_servers=ActionServerConfig(
                move_group="/move_action",
                gripper={f"{cls.BRAND}_gripper": gripper_server},
            ),
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Tear down the composed adapter. Safe to call multiple times."""
        if self._closed:
            return
        inner_close = getattr(self._inner, "close", None)
        if callable(inner_close):
            with suppress(Exception):
                inner_close()
        self._closed = True

    def __enter__(self) -> IndustrialArmAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Supported on a fixed-base arm — delegate to the composed adapter
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
        """``move_to`` / ``hover``: a MoveIt 2 move to a named pose."""
        return self._inner.send_navigation_goal(
            location=location, pose=pose, frame=frame, carrying=carrying, speed=speed
        )

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
        """``grasp`` / ``release``: a ``control_msgs/GripperCommand`` action."""
        return self._inner.send_manipulation_goal(
            action=action,
            target=target,
            force_n=force_n,
            approach=approach,
            release_mode=release_mode,
            release_at=release_at,
        )

    def take_measurement(
        self,
        *,
        what: str,
        target: str | None,
        sensor: str | None,
    ) -> MeasurementResult:
        """``measure``: a single reading (e.g. joint state / wrench)."""
        return self._inner.take_measurement(what=what, target=target, sensor=sensor)

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        """``wait_for``: block on a cell signal / threshold."""
        return self._inner.wait_for_condition(
            kind=kind,
            name=name,
            input_mode=input_mode,
            threshold=threshold,
            timeout_seconds=timeout_seconds,
        )

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        """``wait``: dwell in place for a duration."""
        return self._inner.wait_passively(duration_seconds=duration_seconds)

    def emit_report(
        self,
        *,
        to: str,
        facts: dict[str, Any],
        attachments: list[str] | None,
        status: Literal["success", "partial", "failure"],
        severity: Literal["info", "notice", "warning", "error"],
    ) -> SubstrateResult:
        """``report``: structured status upstream."""
        return self._inner.emit_report(
            to=to, facts=facts, attachments=attachments, status=status, severity=severity
        )

    # ------------------------------------------------------------------
    # Not supported on a bare fixed-base arm
    # ------------------------------------------------------------------

    def _reason(self, capability: str) -> str:
        return _NOT_SUPPORTED_TEMPLATE.format(brand=self.BRAND, capability=capability)

    def send_docking_goal(
        self,
        *,
        station: str,
        service: str,
        until: str | None = None,
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("docking station (it is fixed-base)"))

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        return DetectionResult(success=False, reason=self._reason("onboard perception"))

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
        return ScanResult(success=False, reason=self._reason("area-scan capability"))

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=self._reason("onboard camera"))

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        return SubstrateResult(success=False, reason=self._reason("speaker"))

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        return ListenResult(success=False, reason=self._reason("microphone"))

    def send_takeoff_goal(
        self,
        *,
        altitude: float,
        climb_rate: float | None = None,
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("flight capability"))

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("flight capability"))

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("flight capability"))


class AbbAdapter(IndustrialArmAdapter):
    """ABB arm via the ``abb_ros2`` ROS-Industrial driver + MoveIt 2."""

    BRAND = "abb"


class FanucAdapter(IndustrialArmAdapter):
    """FANUC arm via the ROS-Industrial FANUC driver + MoveIt 2."""

    BRAND = "fanuc"


class KukaAdapter(IndustrialArmAdapter):
    """KUKA arm via the KUKA ROS 2 driver (EKI/RSI ros2_control) + MoveIt 2."""

    BRAND = "kuka"


class YaskawaAdapter(IndustrialArmAdapter):
    """YASKAWA (Motoman) arm via the ``motoman`` ROS-Industrial driver + MoveIt 2."""

    BRAND = "yaskawa"


class UrAdapter(IndustrialArmAdapter):
    """Universal Robots cobot via the ``ur_robot_driver`` (ROS 2) + MoveIt 2.

    UR is the dominant collaborative arm; it uses the same MoveIt 2 /
    ``control_msgs`` dispatch as the other industrial brands, so it is a
    pure brand specialization of the shared core. Denmark-made,
    Teradyne (US) owned — passes the default US-federal policy.
    """

    BRAND = "ur"


class FrankaAdapter(IndustrialArmAdapter):
    """Franka Emika arm via ``franka_ros2`` + MoveIt 2.

    The dominant research/teaching arm; first-class here because the
    educational community is a core adoption flywheel. Germany-made —
    passes the default US-federal policy.
    """

    BRAND = "franka"


class KawasakiAdapter(IndustrialArmAdapter):
    """Kawasaki arm via the ``kawasaki_robot`` ROS-Industrial driver + MoveIt 2.

    Japan-made — passes the default US-federal policy (JP allied origin).
    """

    BRAND = "kawasaki"


class StaubliAdapter(IndustrialArmAdapter):
    """Stäubli arm via ``staubli_val3_driver`` (VAL 3 protocol bridge) + MoveIt 2.

    Switzerland-made — passes the default US-federal policy (CH allied).
    """

    BRAND = "staubli"


class ComauAdapter(IndustrialArmAdapter):
    """Comau arm via ``comau_ros2_driver`` + MoveIt 2.

    Italy-made (Stellantis subsidiary) — passes the default US-federal
    policy (IT allied origin).
    """

    BRAND = "comau"


class MitsubishiAdapter(IndustrialArmAdapter):
    """Mitsubishi Electric MELFA arm via ``melfa_ros2`` + MoveIt 2.

    Japan-made — passes the default US-federal policy. Vendor token is
    ``mitsubishi_electric`` in provenance to disambiguate from any other
    Mitsubishi-prefixed entity.
    """

    BRAND = "mitsubishi"


class DensoAdapter(IndustrialArmAdapter):
    """Denso arm via ``denso_robot_ros2`` + MoveIt 2.

    Japan-made — passes the default US-federal policy.
    """

    BRAND = "denso"


class HyundaiAdapter(IndustrialArmAdapter):
    """Hyundai Robotics arm via ``hyundai_robot_ros2`` + MoveIt 2.

    South Korea-made — passes the default US-federal policy (KR allied
    origin; not on the denylist).
    """

    BRAND = "hyundai"


class NachiAdapter(IndustrialArmAdapter):
    """Nachi-Fujikoshi arm via ``nachi_robot_ros2`` + MoveIt 2.

    Japan-made — passes the default US-federal policy.
    """

    BRAND = "nachi"


class EpsonAdapter(IndustrialArmAdapter):
    """Seiko Epson SCARA / 6-axis arm via ``epson_robot_ros2`` + MoveIt 2.

    Japan-made — passes the default US-federal policy.
    """

    BRAND = "epson"


class OmronAdapter(IndustrialArmAdapter):
    """Omron industrial arm (the former Adept line) via ``omron_industrial_robot``
    ROS-Industrial driver + MoveIt 2.

    Japan-made (Adept Technology was acquired by Omron in 2015) — passes
    the default US-federal policy.
    """

    BRAND = "omron"


class HanwhaAdapter(IndustrialArmAdapter):
    """Hanwha HCR collaborative arm via ``hanwha_hcr_ros2`` + MoveIt 2.

    Unlike Doosan/Techman/Kinova (zero-ROS vendor SDKs handled by
    ``cobot-runtime``), Hanwha publishes a ROS 2 driver shaped exactly
    like the other ROS-Industrial brands, so it belongs in this runtime.
    South Korea-made — passes the default US-federal policy.
    """

    BRAND = "hanwha"
