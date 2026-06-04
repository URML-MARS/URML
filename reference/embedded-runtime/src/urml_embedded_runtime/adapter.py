"""EmbeddedAdapter — micro:bit / Arduino-class MCU over serial.

URML scales DOWN to a microcontroller: a buggy whose firmware reads
short ASCII commands off a serial line. **No ROS 2 dependency** — the
educational-flywheel analog of the PX4/marine no-ROS proof, serving
RFC-0011 educational. Mirrors :class:`BlueRovAdapter`: lazy
``pyserial``, cached lazily-opened port, failures returned not raised.

## v0.1 method coverage

Supported: ``move_to``/``hover`` (write the configured command),
``grasp``/``release`` (write the configured gripper-servo command),
``wait``, ``measure`` (query + read one line), ``wait_for``
(read-once), ``report`` (local sink, no cloud), ``scan`` (documented
stub).

Not supported on a tiny MCU (returned, not raised): ``dock``,
``detect``, ``capture``, ``speak``, ``listen``. The drone trio is
``not_applicable_mcu``.

The minimal-MCU manifest gap (a non-mobile sensor/LED node cannot
honestly fill the manifest's mobility/perception blocks; raw LED/GPIO
actuation has no verb) is recorded in ``SPEC-GAPS.md`` → RFC-0018
(manifest subset) cross-referencing RFC-0017 (the actuation verb), not
silently invented here.
"""

from __future__ import annotations

from contextlib import suppress
from typing import Any, Literal

from urml_ros2_runtime.substrate.base import (
    ProgramCallResult,
    unsupported_program_call,
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

from urml_embedded_runtime._version import __version__
from urml_embedded_runtime.config import EmbeddedConfig, load_embedded_config

__all__ = [
    "EmbeddedAdapter",
    "EmbeddedConfig",
    "__version__",
    "load_embedded_config",
]

_NOT_SUPPORTED = (
    "not_supported_on_mcu: a micro:bit/Arduino-class board has no {capability}. "
    "The URML program, manifest, and validator are unchanged; pair a richer "
    "board or a companion."
)
_NOT_APPLICABLE = "not_applicable_mcu: {capability} has no meaning for a tabletop educational buggy."


def _require_pyserial() -> Any:
    """Lazy-import pyserial with a clear error when missing."""
    try:
        import serial  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "pyserial is not installed. EmbeddedAdapter requires the [serial] extra.\n"
            "  Install with: pip install urml-embedded-runtime[serial]"
        ) from exc
    return serial


class EmbeddedAdapter:
    """Educational-MCU adapter implementing the URML ROSAdapter Protocol."""

    BRAND = "embedded"

    def __init__(self, config: EmbeddedConfig | None = None) -> None:
        self._serial = _require_pyserial()
        self._config = config or EmbeddedConfig()
        self._port: Any = None
        self._reports: list[dict[str, Any]] = []
        self._closed = False

    def _open(self) -> Any:
        if self._port is not None:
            return self._port
        self._port = self._serial.serial_for_url(
            self._config.port,
            baudrate=self._config.baudrate,
            timeout=self._config.read_timeout_seconds,
        )
        return self._port

    def _send(self, command: str) -> None:
        port = self._open()
        port.write((command + "\n").encode("ascii"))

    def close(self) -> None:
        if self._closed:
            return
        if self._port is not None:
            with suppress(Exception):
                self._port.close()
        self._closed = True

    def __enter__(self) -> EmbeddedAdapter:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Supported
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
        if location is None:
            return NavigationResult(
                success=False,
                reason="mcu_requires_named_location: a buggy drives to firmware-named "
                "commands; raw pose goals are not meaningful on an MCU.",
            )
        cmd = self._config.resolve_location(location)
        if cmd is None:
            return NavigationResult(
                success=False,
                reason=f"location_not_configured: {location!r} is declared in the "
                "manifest but not mapped to a command in embedded_adapter.yaml.",
            )
        self._send(cmd)
        return NavigationResult(success=True, final_pose=None, frame=frame or "buggy")

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
        cmd = self._config.manipulation_commands.get(action)
        if cmd is None:
            return ManipulationResult(
                success=False,
                reason=f"manipulation_command_not_configured: {action!r} is not mapped "
                "to a command in embedded_adapter.yaml.",
            )
        self._send(cmd)
        return ManipulationResult(success=True, grip_force_n=force_n)

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        self._open()
        return SubstrateResult(success=True)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        port = self._open()
        port.write(b"MEASURE\n")
        line = port.readline()
        try:
            value: float | None = float(line.decode("ascii", "ignore").strip())
        except (ValueError, AttributeError):
            value = None
        return MeasurementResult(success=True, payload={"value": value, "what": what})

    def wait_for_condition(
        self,
        *,
        kind: Literal["event", "signal", "input", "sensor_threshold"],
        name: str | None,
        input_mode: str | None,
        threshold: dict[str, Any] | None,
        timeout_seconds: float | None,
    ) -> WaitResult:
        port = self._open()
        line = port.readline()
        return WaitResult(success=True, timed_out=not line, payload=None)

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
            payload={"samples": [], "coverage": 0.0, "anomalies": [], "_note": "v0.1 EmbeddedAdapter scan: stub."},
        )

    # ------------------------------------------------------------------
    # Not supported on a tiny MCU
    # ------------------------------------------------------------------

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

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('embedded')
