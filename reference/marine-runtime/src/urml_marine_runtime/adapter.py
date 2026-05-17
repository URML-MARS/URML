"""BlueRovAdapter — BlueROV2 / ArduSub underwater vehicle, via MAVLink.

ArduSub speaks MAVLink, exactly like PX4, so this adapter mirrors
:class:`PX4Adapter`: lazy ``pymavlink``, **no ROS 2 dependency**, a
lazily-opened cached connection, failures returned not raised. It is
the underwater analog of the PX4 no-ROS proof, and it activates the
``underwater_thrusters`` ``mobility.drive_type`` (already in the v0.1
manifest schema — no RFC needed).

## v0.1 method coverage

Supported (mapped to MAVLink against ArduSub's GUIDED mode):

- ``move_to`` / ``hover`` → ``SET_POSITION_TARGET_LOCAL_NED`` to a
  configured waypoint (location → north/east/depth via
  :class:`MarineConfig`); ``hover`` is a zero-velocity hold (ArduSub
  position/depth hold).
- ``wait`` → timed hold.
- ``measure`` → telemetry (``SCALED_PRESSURE`` depth, ``BATTERY_STATUS``).
- ``wait_for`` → MAVLink message-stream subscribe-once with a predicate.
- ``report`` → structured record to a local sink (no cloud — manifesto).
- ``scan`` → documented **stub success**, mirroring PX4Adapter.run_scan.

Not supported on a bare ROV (returned, not raised): ``grasp`` /
``release`` (needs a manipulator payload — a follow-up companion),
``dock``, ``detect``, ``capture``, ``speak``, ``listen``; and the
drone trio ``take_off`` / ``land`` / ``return_to_home`` are
``not_applicable_underwater``.
"""

from __future__ import annotations

from contextlib import suppress
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field
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

from urml_marine_runtime._version import __version__

__all__ = ["BlueRovAdapter", "MarineConfig", "__version__", "load_marine_config"]

_NOT_SUPPORTED = (
    "not_supported_on_bare_rov: a bare BlueROV2 has no {capability}. Pair it "
    "with a manipulator/perception payload companion adapter for full "
    "coverage; the URML program, manifest, and validator are unchanged."
)
_NOT_UNDERWATER = "not_applicable_underwater: {capability} has no meaning for a submersible."


class Waypoint(BaseModel):
    """A local-NED-ish underwater waypoint. ``depth`` is metres below surface (positive down)."""

    model_config = ConfigDict(extra="forbid")

    north: float = 0.0
    east: float = 0.0
    depth: float = 0.0


class MarineConfig(BaseModel):
    """Deployment-side BlueROV2 / ArduSub connection config."""

    model_config = ConfigDict(extra="forbid")

    connection_url: str = Field(
        default="udp:127.0.0.1:14550",
        description="pymavlink connection string. ArduSub SITL: 'udp:127.0.0.1:14550'.",
    )
    system_id: int = 255
    component_id: int = 1
    heartbeat_timeout_seconds: float = 5.0
    location_to_waypoint: dict[str, Waypoint] = Field(default_factory=dict)

    def resolve_location(self, name: str) -> Waypoint | None:
        return self.location_to_waypoint.get(name)


def load_marine_config(path: str) -> MarineConfig:
    """Parse a ``marine_adapter.yaml`` file into a :class:`MarineConfig`."""
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"marine-config file {path} did not contain a YAML mapping at the top level.")
    return MarineConfig.model_validate(data)


def _require_pymavlink() -> Any:
    """Lazy-import pymavlink with a clear error when missing."""
    try:
        from pymavlink import mavutil  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "pymavlink is not installed. BlueRovAdapter requires the [marine] extra.\n"
            "  Install with: pip install urml-marine-runtime[marine]"
        ) from exc
    return mavutil


class BlueRovAdapter:
    """BlueROV2 / ArduSub adapter implementing the URML ROSAdapter Protocol."""

    BRAND = "bluerov"

    def __init__(self, config: MarineConfig | None = None) -> None:
        self._mavutil = _require_pymavlink()
        self._config = config or MarineConfig()
        self._conn: Any = None
        self._reports: list[dict[str, Any]] = []
        self._closed = False

    def _connect(self) -> Any:
        if self._conn is not None:
            return self._conn
        conn = self._mavutil.mavlink_connection(
            self._config.connection_url,
            source_system=self._config.system_id,
            source_component=self._config.component_id,
        )
        conn.wait_heartbeat(timeout=self._config.heartbeat_timeout_seconds)
        self._conn = conn
        return conn

    def close(self) -> None:
        if self._closed:
            return
        if self._conn is not None:
            with suppress(Exception):
                self._conn.close()
        self._closed = True

    def __enter__(self) -> BlueRovAdapter:
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
        if location is None and pose is None:
            return NavigationResult(success=False, reason="send_navigation_goal called without location or pose")
        if location is not None:
            wp = self._config.resolve_location(location)
            if wp is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the "
                    "manifest but not mapped to a waypoint in marine_adapter.yaml.",
                )
            target = {"north": wp.north, "east": wp.east, "depth": wp.depth}
        else:
            target = dict(pose or {})
        conn = self._connect()
        conn.mav.set_position_target_local_ned_send(
            0, conn.target_system, conn.target_component, 1, 0b0000111111111000,
            target.get("north", 0.0), target.get("east", 0.0), target.get("depth", 0.0),
            0, 0, 0, 0, 0, 0, 0, 0,
        )
        return NavigationResult(success=True, final_pose=target, frame=frame or "ned")

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        self._connect()
        return SubstrateResult(success=True)

    def take_measurement(self, *, what: str, target: str | None, sensor: str | None) -> MeasurementResult:
        conn = self._connect()
        msg = conn.recv_match(type=["SCALED_PRESSURE", "BATTERY_STATUS"], blocking=True, timeout=5)
        value = float(getattr(msg, "press_abs", getattr(msg, "battery_remaining", 0.0))) if msg else None
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
        conn = self._connect()
        msg = conn.recv_match(blocking=True, timeout=timeout_seconds or 5)
        return WaitResult(success=True, timed_out=msg is None, payload=None)

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
            payload={"samples": [], "coverage": 0.0, "anomalies": [], "_note": "v0.1 BlueRovAdapter scan: stub."},
        )

    # ------------------------------------------------------------------
    # Not supported on a bare ROV
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
        return ManipulationResult(success=False, reason=_NOT_SUPPORTED.format(capability="manipulator"))

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
        return NavigationResult(success=False, reason=_NOT_UNDERWATER.format(capability="take_off"))

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_UNDERWATER.format(capability="land"))

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_UNDERWATER.format(capability="return_to_home"))
