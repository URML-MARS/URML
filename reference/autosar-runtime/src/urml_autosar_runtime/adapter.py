"""AutosarAdaptiveAdapter — AUTOSAR Adaptive cell, via ara.

AUTOSAR Adaptive is the universal factory-floor companion spec; this is
the industrial-automation analog of the PX4/marine no-ROS proof and
mirrors :class:`BlueRovAdapter`: lazy ``ara``, **no ROS 2
dependency**, a lazily-opened cached client, failures returned not
raised. It hits the manufacturer / federal-procurement wedge
(RFC-0007) and complements the shipped industrial-arm family +
RFC-0013 primitives.

## v0.1 method coverage

Supported (mapped onto configured AUTOSAR Adaptive method/variable nodes):

- ``move_to`` / ``hover`` → call the configured per-location method
  node (location → method+args via :class:`AutosarConfig`).
- ``dock`` → call the configured station-service method; this is the
  path RFC-0013 ``swap_tool`` rides (service name keyed in config),
  preserved unchanged.
- ``grasp`` / ``release`` → call the configured manipulation method.
- ``wait`` → no-op success (a cell holds position).
- ``measure`` / ``wait_for`` → read the configured variable node once.
- ``report`` → structured record to a local sink (no cloud — manifesto).
- ``scan`` → documented **stub success**, mirroring PX4Adapter.run_scan.

Not supported by a bare cell (returned, not raised): ``detect``,
``capture``, ``speak``, ``listen`` — pair a vision/HMI companion. The
drone trio ``take_off`` / ``land`` / ``return_to_home`` are
``not_applicable_autosar``.

A general "invoke a named ara::com Method / PLC method with arguments"
is **not** expressible with the current primitives (it is not a
station service, unlike ``swap_tool``); that is a recorded spec gap
(see ``SPEC-GAPS.md`` → RFC-0015), not silently bolted on here.
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

from urml_autosar_runtime._version import __version__
from urml_autosar_runtime.config import MethodTarget, AutosarConfig, load_autosar_config

__all__ = [
    "MethodTarget",
    "AutosarAdaptiveAdapter",
    "AutosarConfig",
    "__version__",
    "load_autosar_config",
]

_NOT_SUPPORTED = (
    "not_supported_on_autosar_ecu_cell: a bare AUTOSAR Adaptive cell has no {capability}. "
    "Pair it with a vision/HMI companion adapter; the URML program, manifest, "
    "and validator are unchanged."
)
_NOT_APPLICABLE = "not_applicable_autosar: {capability} has no meaning for a fixed industrial cell."


def _require_ara() -> Any:
    """Lazy-import ara's sync client with a clear error when missing."""
    try:
        from ara.sync import Client  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "ara is not installed. AutosarAdaptiveAdapter requires the [autosar] extra.\n"
            "  Install with: pip install urml-autosar-runtime[autosar]"
        ) from exc
    return Client


class AutosarAdaptiveAdapter:
    """AUTOSAR Adaptive adapter implementing the URML ROSAdapter Protocol."""

    BRAND = "autosar"

    def __init__(self, config: AutosarConfig | None = None) -> None:
        self._client_cls = _require_ara()
        self._config = config or AutosarConfig()
        self._client: Any = None
        self._objects: Any = None
        self._reports: list[dict[str, Any]] = []
        self._closed = False

    def _connect(self) -> Any:
        if self._client is not None:
            return self._client
        client = self._client_cls(self._config.endpoint_url, timeout=self._config.connect_timeout_seconds)
        client.connect()
        self._client = client
        self._objects = client.get_node(self._config.objects_node)
        return client

    def _call(self, mt: MethodTarget) -> Any:
        self._connect()
        return self._objects.call_method(mt.method, *mt.args)

    def close(self) -> None:
        if self._closed:
            return
        if self._client is not None:
            with suppress(Exception):
                self._client.disconnect()
        self._closed = True

    def __enter__(self) -> AutosarAdaptiveAdapter:
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
                reason="autosar_requires_named_location: an AUTOSAR Adaptive cell drives to named "
                "method-mapped poses; raw pose goals are not exposed by the companion spec.",
            )
        mt = self._config.resolve_location(location)
        if mt is None:
            return NavigationResult(
                success=False,
                reason=f"location_not_configured: {location!r} is declared in the "
                "manifest but not mapped to a method in autosar_adapter.yaml.",
            )
        self._call(mt)
        return NavigationResult(success=True, final_pose=None, frame=frame or "cell")

    def send_docking_goal(self, *, station: str, service: str, until: str | None = None) -> NavigationResult:
        mt = self._config.resolve_service(service)
        if mt is None:
            return NavigationResult(
                success=False,
                reason=f"service_not_configured: station service {service!r} (station "
                f"{station!r}) is not mapped to a method in autosar_adapter.yaml.",
            )
        self._call(mt)
        return NavigationResult(success=True, final_pose=None, frame="cell")

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
        mt = self._config.manipulation_methods.get(action)
        if mt is None:
            return ManipulationResult(
                success=False,
                reason=f"manipulation_method_not_configured: {action!r} is not mapped "
                "to a method in autosar_adapter.yaml.",
            )
        self._call(mt)
        return ManipulationResult(success=True)

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        self._connect()
        return SubstrateResult(success=True)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        if self._config.measurement_node is None:
            return MeasurementResult(success=True, payload={"value": None, "what": what})
        self._connect()
        node = self._client.get_node(self._config.measurement_node)
        value = node.read_value()
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
        if self._config.measurement_node is None:
            self._connect()
            return WaitResult(success=True, timed_out=False, payload=None)
        node = self._client.get_node(self._config.measurement_node) if self._connect() else None
        value = node.read_value() if node is not None else None
        return WaitResult(success=True, timed_out=False, payload={"value": value})

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
            payload={"samples": [], "coverage": 0.0, "anomalies": [], "_note": "v0.1 AutosarAdaptiveAdapter scan: stub."},
        )

    # ------------------------------------------------------------------
    # Not supported by a bare cell
    # ------------------------------------------------------------------

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
        return unsupported_program_call('autosar_ecu')
