"""DigitAdapter — Agility Robotics Digit, a ROS 2 bipedal humanoid.

Digit exposes ROS 2 interfaces (plus a JSON/WebSocket low-level API and
a MuJoCo/Gazebo sim), so this adapter composes the ROS 2 runtime's
:class:`RclpyAdapter` — the same single-sourced-substrate pattern the
industrial-arm and ANYmal adapters use. The per-brand surface is real
(distinct class, brand-scoped not-supported tag); ROS 2 plumbing is not
duplicated.

## v0.1 scope: locomotion + whole-body manipulation

Digit is a logistics humanoid: a biped (locomotion) with two arms.
Both classes are in scope as of RFC-0010 (whole-body / bimanual
manipulation). This adapter supports the locomotion path —
`move_to`/`hover`, `wait`, `measure`, `wait_for`, `report` — and
manipulation — `grasp`/`release` (with the optional `arm` selector)
and `bimanual` (decomposed by the runtime into two arm-addressed
manipulation goals, per RFC-0010). All of these delegate to the
composed ROS 2 adapter.

It still returns ``not_supported_on_humanoid[digit]`` for `dock`,
`detect`, `scan`, `capture`, `speak`, `listen`, and the drone trio:
onboard perception and speech pair via a companion adapter (a
manipulation `$target` is supplied by that companion's `detect`). This
is the same returned-not-raised pattern PX4Adapter and the other
families use.

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

from urml_humanoid_runtime._version import __version__

__all__ = ["DigitAdapter", "__version__"]

_NOT_SUPPORTED = (
    "not_supported_on_humanoid[digit]: v0.1 covers locomotion and whole-body "
    "manipulation (RFC-0010). {capability} is not on Digit's own surface. "
    "Pair Digit with a companion adapter for full coverage; the URML program, "
    "manifest, and validator are unchanged."
)

InnerFactory = Callable[[], ROSAdapter]


class DigitAdapter:
    """Agility Digit adapter (ROS 2), composing RclpyAdapter. v0.1: locomotion."""

    BRAND = "digit"

    def __init__(
        self,
        config: AdapterConfig | None = None,
        *,
        node_name: str = "urml_digit_humanoid",
        inner_factory: InnerFactory | None = None,
    ) -> None:
        self._config = config or AdapterConfig()
        factory: InnerFactory = inner_factory or (lambda: RclpyAdapter(self._config, node_name=node_name))
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

    def __enter__(self) -> DigitAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _reason(self, capability: str) -> str:
        return _NOT_SUPPORTED.format(capability=capability)

    # ------------------------------------------------------------------
    # Supported (locomotion subset) — delegate to the composed adapter
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
    ) -> ManipulationResult:
        """Manipulation, including the `arm` selector (RFC-0010).

        `bimanual` reaches the adapter as two arm-addressed calls (the
        runtime decomposes it), so a single delegating method covers both
        the single-arm and whole-body paths.
        """
        return self._inner.send_manipulation_goal(
            action=action,
            target=target,
            force_n=force_n,
            approach=approach,
            release_mode=release_mode,
            release_at=release_at,
            arm=arm,
        )

    # ------------------------------------------------------------------
    # Not supported in v0.1 (companion-paired: perception, speech)
    # ------------------------------------------------------------------

    def send_docking_goal(self, *, station: str, service: str, until: str | None = None) -> NavigationResult:
        return NavigationResult(success=False, reason=self._reason("docking"))

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        return DetectionResult(success=False, reason=self._reason("onboard detection"))

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
        return ScanResult(success=False, reason=self._reason("area scan"))

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=self._reason("capture"))

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        return SubstrateResult(success=False, reason=self._reason("speech"))

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        return ListenResult(success=False, reason=self._reason("listening"))

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
        return unsupported_program_call('humanoid')
