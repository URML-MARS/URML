"""Clearpath wheeled-AMR adapters — Husky and Jackal, via ROS 2 + Nav2.

Husky and Jackal are differential-drive ROS 2 research/field AMRs (the
canonical ROS 2 mobile bases), so this adapter composes the ROS 2
runtime's :class:`RclpyAdapter` — the same single-sourced-substrate
pattern the industrial-arm, ANYmal, and Digit adapters use. The
per-brand surface is real (distinct class, brand-scoped not-supported
tag); the ROS 2 / Nav2 plumbing is not duplicated.

A bare AMR is a mobile base: it navigates (``move_to``), dwells
(``wait``), takes readings (``measure``), waits on site signals
(``wait_for``), and reports. It has no arm and no flight; those return
``not_supported_on_amr[<brand>]`` rather than raising — the same
returned-not-raised pattern the other families use. A Clearpath base
carrying a UR/Franka arm + Robotiq gripper (a common mobile-manipulator
config) pairs with an industrial-arm companion adapter; the URML
program, manifest, and validator are unchanged.

``rclpy`` is imported lazily inside :class:`RclpyAdapter`, so importing
this module works on every host; constructing the adapter needs a
sourced ROS 2 environment. Hermetic tests inject a fake inner adapter
via ``inner_factory`` and never touch rclpy.
"""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import Any, Literal

from urml_ros2_runtime.substrate.adapter_config import AdapterConfig
from urml_ros2_runtime.substrate.base import (
    ProgramCallResult,
    unsupported_program_call,
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

__all__ = ["ClearpathAdapter", "HuskyAdapter", "JackalAdapter", "MOBILE_ADAPTERS"]

_NOT_SUPPORTED = (
    "not_supported_on_amr[{brand}]: a bare {brand} mobile base has no "
    "{capability}. Pair it with an industrial-arm / payload companion adapter "
    "for full coverage; the URML program, manifest, and validator are unchanged."
)

InnerFactory = Callable[[], ROSAdapter]


class ClearpathAdapter:
    """Shared core for Clearpath wheeled AMRs, composing RclpyAdapter."""

    BRAND: str = "clearpath"

    def __init__(
        self,
        config: AdapterConfig | None = None,
        *,
        node_name: str | None = None,
        inner_factory: InnerFactory | None = None,
    ) -> None:
        self._config = config or AdapterConfig()
        node = node_name or f"urml_{self.BRAND}_amr"
        factory: InnerFactory = inner_factory or (lambda: RclpyAdapter(self._config, node_name=node))
        self._inner: ROSAdapter = factory()
        self._closed = False

    def close(self) -> None:
        if self._closed:
            return
        inner_close = getattr(self._inner, "close", None)
        if callable(inner_close):
            with suppress(Exception):
                inner_close()
        self._closed = True

    def __enter__(self) -> ClearpathAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _reason(self, capability: str) -> str:
        return _NOT_SUPPORTED.format(brand=self.BRAND, capability=capability)

    # ------------------------------------------------------------------
    # Supported — delegate to the composed RclpyAdapter
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
        return self._inner.send_navigation_goal(
            location=location, pose=pose, frame=frame, carrying=carrying, speed=speed
        )

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
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
        return self._inner.wait_for_condition(
            kind=kind, name=name, input_mode=input_mode, threshold=threshold, timeout_seconds=timeout_seconds
        )

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
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
        return self._inner.emit_report(
            to=to, facts=facts, attachments=attachments, status=status, severity=severity
        )

    # ------------------------------------------------------------------
    # Not supported on a bare mobile base
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
    ) -> ManipulationResult:
        return ManipulationResult(success=False, reason=self._reason("arm"))

    def send_docking_goal(self, *, station: str, service: str, until: str | None = None) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("docking station"))

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        return DetectionResult(success=False, reason=self._reason("onboard object detection"))

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
        return ScanResult(success=False, reason=self._reason("area-scan payload"))

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=self._reason("capture payload"))

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

    def send_takeoff_goal(self, *, altitude: float, climb_rate: float | None = None) -> NavigationResult:
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

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('mobile')


class HuskyAdapter(ClearpathAdapter):
    """Clearpath Husky (UGV) via ROS 2 + Nav2. US/Canada-made, compliant."""

    BRAND = "husky"


class JackalAdapter(ClearpathAdapter):
    """Clearpath Jackal (small UGV) via ROS 2 + Nav2. US/Canada-made, compliant."""

    BRAND = "jackal"


MOBILE_ADAPTERS: dict[str, type[ClearpathAdapter]] = {
    "husky": HuskyAdapter,
    "jackal": JackalAdapter,
}
