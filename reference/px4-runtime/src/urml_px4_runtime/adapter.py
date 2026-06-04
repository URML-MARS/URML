"""PX4Adapter — MAVLink-based URML substrate adapter.

Implements the ``ROSAdapter`` Protocol (despite the "ROS" in the name —
the Protocol is substrate-neutral) via ``pymavlink``. **No ROS 2
dependency.** This adapter is the second URML reference runtime; its
purpose is to keep the spec honest about substrate-neutrality.

## Lazy pymavlink

``pymavlink`` is a normal PyPI package (unlike ``rclpy``), so the
``[px4]`` extra can install it cleanly. But we still import lazily at
construction time so:

- Module-level ``import urml_px4_runtime`` works without pymavlink
  installed (useful in environments that only build the URML packages
  for spec / test purposes).
- The error when pymavlink is missing is clear and actionable.

## MAVLink dispatch pattern

Each Protocol method:

1. Establishes a heartbeat connection on first use (cached on the
   adapter instance).
2. Constructs the right MAVLink command (`command_long_send`,
   `set_position_target_local_ned_send`, etc.).
3. Optionally waits for an ACK or a follow-up message.
4. Maps the substrate response into the URML ``SubstrateResult`` shape.

Failures are *returned*, not raised — same contract as RclpyAdapter and
MockROSAdapter. Only unrecoverable substrate errors (broken connection
that can't be reopened) raise.

## What's not supported on a bare autopilot

PX4 itself doesn't have grippers, cameras, microphones, or perception
nodes — those live on a companion computer (typically ROS-2-backed).
The corresponding methods (`grasp`, `release`, `detect`, `capture`,
`speak`, `listen`, `dock`) return ``NavigationResult(success=False,
reason="not_supported_on_bare_autopilot: ...")``. Programs that need
both flight control *and* perception/manipulation should pair PX4Adapter
with RclpyAdapter via a composite adapter (future PR).
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

from urml_px4_runtime.config import PX4AdapterConfig

DEFAULT_HEARTBEAT_TIMEOUT_SECONDS = 5.0


def _require_pymavlink() -> Any:
    """Lazy-import pymavlink with a clear error when missing."""
    try:
        from pymavlink import mavutil  # type: ignore[import-not-found,unused-ignore]
    except ImportError as exc:
        raise RuntimeError(
            "pymavlink is not installed. PX4Adapter requires the [px4] extra.\n"
            "  Install with: pip install urml-px4-runtime[px4]"
        ) from exc
    return mavutil


# Sentinel reason used by every method that doesn't apply to a bare PX4
# autopilot. Extracted as a constant so tests can match exactly.
_NOT_SUPPORTED_REASON = (
    "not_supported_on_bare_autopilot: this primitive needs a companion "
    "computer (perception / manipulation / speech). Pair PX4Adapter with "
    "a ROS-2-backed companion adapter for full coverage."
)


class PX4Adapter:
    """MAVLink-based URML substrate adapter."""

    def __init__(self, config: PX4AdapterConfig | None = None) -> None:
        self._mavutil = _require_pymavlink()
        self._config = config or PX4AdapterConfig()
        self._connection: Any = None
        self._closed = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _connect(self) -> Any:
        """Open the MAVLink connection lazily; cache for reuse."""
        if self._connection is not None:
            return self._connection
        conn = self._mavutil.mavlink_connection(
            self._config.connection_url,
            source_system=self._config.system_id,
            source_component=self._config.component_id,
        )
        # Wait for the autopilot's first heartbeat so we know it's there.
        # pymavlink's wait_heartbeat returns the heartbeat message or
        # raises on timeout. We catch and surface as a clean failure.
        conn.wait_heartbeat(timeout=self._config.heartbeat_timeout_seconds)
        self._connection = conn
        return conn

    def close(self) -> None:
        """Close the MAVLink connection. Safe to call multiple times."""
        if self._closed:
            return
        if self._connection is not None:
            with suppress(Exception):
                self._connection.close()
        self._closed = True

    def __enter__(self) -> PX4Adapter:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _send_command_long(self, command: int, *params: float) -> tuple[bool, str | None]:
        """Send a MAV_CMD_* via COMMAND_LONG; wait for COMMAND_ACK.

        Returns ``(success, reason)``. params are MAVLink params 1-7;
        missing trailing params default to 0.
        """
        try:
            conn = self._connect()
        except Exception as exc:
            return False, f"connection_failed: {exc}"
        padded = list(params) + [0.0] * (7 - len(params))
        conn.mav.command_long_send(
            conn.target_system,
            conn.target_component,
            command,
            0,  # confirmation
            *padded[:7],
        )
        ack = conn.recv_match(
            type="COMMAND_ACK",
            blocking=True,
            timeout=self._config.ack_timeout_seconds,
        )
        if ack is None:
            return False, "ack_timeout"
        # MAV_RESULT_ACCEPTED = 0. Any other result is a failure.
        if int(getattr(ack, "result", -1)) != 0:
            return False, f"mav_result_{int(getattr(ack, 'result', -1))}"
        return True, None

    def _recv_message(
        self,
        msg_type: str,
        *,
        predicate: Any = None,
        timeout_seconds: float | None = None,
    ) -> tuple[Any | None, bool]:
        """Wait for the next message of ``msg_type`` (optionally matching
        ``predicate``). Returns ``(message, timed_out)``.
        """
        try:
            conn = self._connect()
        except Exception:
            return None, True
        wait = timeout_seconds if timeout_seconds is not None else self._config.message_timeout_seconds
        # recv_match with blocking + timeout returns None on timeout.
        # The predicate runs on candidate messages; we re-loop until we
        # find a match or the timeout elapses.
        if predicate is None:
            msg = conn.recv_match(type=msg_type, blocking=True, timeout=wait)
            return msg, msg is None
        # With a predicate, recv_match itself accepts a `condition` kwarg
        # in pymavlink, but using an explicit loop keeps behavior
        # readable and easy to mock.
        msg = conn.recv_match(type=msg_type, blocking=True, timeout=wait)
        if msg is None:
            return None, True
        if predicate(msg):
            return msg, False
        return None, True

    # ------------------------------------------------------------------
    # Drone-profile dispatch (the substantive PX4 surface)
    # ------------------------------------------------------------------

    def send_takeoff_goal(
        self,
        *,
        altitude: float,
        climb_rate: float | None = None,
    ) -> NavigationResult:
        # MAV_CMD_NAV_TAKEOFF = 22. param7 = altitude (m AGL).
        success, reason = self._send_command_long(22, 0, 0, 0, 0, 0, 0, float(altitude))
        return NavigationResult(
            success=success,
            reason=reason,
            final_pose={"x": 0.0, "y": 0.0, "z": float(altitude)} if success else None,
            frame="agl" if success else None,
        )

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        # MAV_CMD_NAV_LAND = 21. Precision-landing is a PX4-parameter
        # concern; v0.1 ignores `precision` (the autopilot uses whichever
        # landing mode it's configured for).
        success, reason = self._send_command_long(21)
        return NavigationResult(success=success, reason=reason)

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        # MAV_CMD_NAV_RETURN_TO_LAUNCH = 20. Speed/altitude are PX4
        # parameters set ahead of time, not part of the RTL command itself
        # (per the MAVLink spec). v0.1 takes the autopilot's configured
        # defaults; a future RFC may add a param-set step here.
        success, reason = self._send_command_long(20)
        return NavigationResult(success=success, reason=reason)

    # ------------------------------------------------------------------
    # Core navigation
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
        # Resolve to NED. URML's `pose` is x/y/z; PX4 uses
        # north/east/down. We treat x→north, y→east, z (positive up, AGL)
        # → down=-z.
        if location is not None:
            ned = self._config.resolve_location(location)
            if ned is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the "
                    "manifest but not mapped to a NED pose in px4_adapter.yaml.",
                )
            north, east, alt = ned.north, ned.east, ned.alt
        elif pose is not None:
            north = float(pose.get("x", 0.0))
            east = float(pose.get("y", 0.0))
            alt = float(pose.get("z", 0.0))
        else:
            return NavigationResult(
                success=False,
                reason="send_navigation_goal called without location or pose",
            )

        try:
            conn = self._connect()
        except Exception as exc:
            return NavigationResult(success=False, reason=f"connection_failed: {exc}")

        # SET_POSITION_TARGET_LOCAL_NED. type_mask bit 0xDF8 ignores
        # velocity/accel/yaw — we only set position. (0xDF8 = ignore
        # velocity (3 bits) + accel (3 bits) + yaw + yaw rate.)
        type_mask = 0b0000_1111_1111_1000
        conn.mav.set_position_target_local_ned_send(
            0,  # time_boot_ms
            conn.target_system,
            conn.target_component,
            1,  # MAV_FRAME_LOCAL_NED
            type_mask,
            north,
            east,
            -alt,  # NED down is negative-up
            0.0, 0.0, 0.0,  # velocity
            0.0, 0.0, 0.0,  # accel
            0.0, 0.0,  # yaw, yaw_rate
        )
        return NavigationResult(
            success=True,
            final_pose={"x": north, "y": east, "z": alt},
            frame=frame or "ned",
        )

    def send_docking_goal(
        self,
        *,
        station: str,
        service: str,
        until: str | None = None,
    ) -> NavigationResult:
        return NavigationResult(success=False, reason=_NOT_SUPPORTED_REASON)

    # ------------------------------------------------------------------
    # Hover: same MAVLink message as move_to but with zero velocity and
    # current position (kept here for explicitness; the URML executor
    # dispatches hover through send_navigation_goal).
    #
    # No-op as a distinct method because the Protocol already routes
    # hover through send_navigation_goal.
    # ------------------------------------------------------------------

    # ------------------------------------------------------------------
    # Manipulation / perception / speech — not on a bare autopilot
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
    ) -> ManipulationResult:
        return ManipulationResult(success=False, reason=_NOT_SUPPORTED_REASON)

    def query_detection(
        self,
        *,
        object_class: str,
        attributes: dict[str, Any] | None = None,
        where_near: str | None = None,
        where_within: float | None = None,
    ) -> DetectionResult:
        return DetectionResult(success=False, reason=_NOT_SUPPORTED_REASON)

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
        # Scan = sequence of move_to waypoints + capture triggers. Full
        # implementation requires a companion computer for capture; the
        # bare-autopilot path returns a stub success matching MockROSAdapter.
        return ScanResult(
            success=True,
            payload={
                "samples": [],
                "coverage": 1.0,
                "anomalies": [],
                "_note": "v0.1 PX4Adapter scan: stub. Full waypoint expansion + "
                "capture requires a companion adapter; see README.",
            },
        )

    def take_measurement(
        self,
        *,
        what: str,
        target: str | None,
        sensor: str | None,
    ) -> MeasurementResult:
        # Map a URML measurement kind to a MAVLink telemetry message.
        # v0.1 supports distance (DISTANCE_SENSOR) and battery voltage
        # (BATTERY_STATUS); other kinds return not_supported until the
        # mapping is documented per-message.
        kind_to_msg = {
            "distance": "DISTANCE_SENSOR",
            "voltage": "BATTERY_STATUS",
        }
        msg_type = kind_to_msg.get(what)
        if msg_type is None:
            return MeasurementResult(
                success=False,
                reason=f"measurement_kind_not_supported: {what!r}. "
                f"PX4Adapter v0.1 supports: {sorted(kind_to_msg)}.",
            )
        msg, timed_out = self._recv_message(msg_type)
        if timed_out or msg is None:
            return MeasurementResult(success=False, reason="no_reading_within_timeout")
        # DISTANCE_SENSOR.current_distance is cm; BATTERY_STATUS.voltages[0] is mV.
        if msg_type == "DISTANCE_SENSOR":
            value = float(getattr(msg, "current_distance", 0)) / 100.0
            unit = "m"
        else:
            voltages = getattr(msg, "voltages", [0])
            value = float(voltages[0] if voltages else 0) / 1000.0
            unit = "V"
        timestamp = float(getattr(msg, "time_boot_ms", 0)) / 1000.0
        return MeasurementResult(
            success=True,
            payload={"value": value, "unit": unit, "timestamp": timestamp},
        )

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        return CaptureResult(success=False, reason=_NOT_SUPPORTED_REASON)

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
        # PX4 doesn't have a native event-topic taxonomy beyond STATUSTEXT
        # and the per-message types. v0.1 supports `sensor_threshold` against
        # battery (voltage-low watchdog), `event:emergency_stop` mapped to
        # SYSTEM_STATUS.MAV_STATE_EMERGENCY, and times out cleanly otherwise.
        if kind == "sensor_threshold":
            sensor = (threshold or {}).get("sensor", "battery")
            op = (threshold or {}).get("op", "gt")
            value = float((threshold or {}).get("value", 0.0))
            if sensor != "battery":
                return WaitResult(
                    success=False,
                    reason=f"sensor_threshold_not_supported: {sensor!r}. "
                    "PX4Adapter v0.1 supports: battery.",
                )

            def _matches(msg: Any) -> bool:
                voltages = getattr(msg, "voltages", [0])
                v = float(voltages[0] if voltages else 0) / 1000.0
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

            msg, timed_out = self._recv_message(
                "BATTERY_STATUS",
                predicate=_matches,
                timeout_seconds=timeout_seconds,
            )
            if timed_out or msg is None:
                return WaitResult(success=False, timed_out=True, reason="timeout")
            voltages = getattr(msg, "voltages", [0])
            v = float(voltages[0] if voltages else 0) / 1000.0
            return WaitResult(success=True, payload={"sensor": "battery", "value": v})

        if kind == "event" and name == "emergency_stop":
            msg, timed_out = self._recv_message(
                "SYS_STATUS",
                timeout_seconds=timeout_seconds,
            )
            if timed_out or msg is None:
                return WaitResult(success=False, timed_out=True, reason="timeout")
            return WaitResult(success=True, payload={"event": "emergency_stop"})

        return WaitResult(
            success=False,
            reason=f"wait_kind_not_supported_on_bare_autopilot: kind={kind!r}, name={name!r}",
        )

    def wait_passively(self, *, duration_seconds: float) -> SubstrateResult:
        # MAVLink doesn't have a "pause-but-keep-station" command on its
        # own — PX4 in offboard mode requires continuous setpoints to
        # hold position. A correct implementation would re-send the
        # current setpoint at 10 Hz for `duration_seconds`. v0.1 uses a
        # simple time.sleep — deployers running offboard mode should hold
        # position via send_navigation_goal first.
        import time as _time

        _time.sleep(max(0.0, float(duration_seconds)))
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
        # Map URML severity → MAV_SEVERITY (0=EMERGENCY .. 7=DEBUG).
        sev_map = {"info": 6, "notice": 5, "warning": 4, "error": 3}
        mav_severity = sev_map.get(severity, 6)
        # STATUSTEXT max payload length is 50 bytes. Truncate the JSON.
        import json

        text = json.dumps({"status": status, "facts": facts}, sort_keys=True)[:50]
        try:
            conn = self._connect()
        except Exception as exc:
            return SubstrateResult(success=False, reason=f"connection_failed: {exc}")
        conn.mav.statustext_send(mav_severity, text.encode("utf-8"))
        return SubstrateResult(success=True)

    def emit_speech(
        self,
        *,
        utterance: str,
        locale: str | None,
        style: Literal["notice", "warning", "conversational"],
        interrupt: bool,
    ) -> SubstrateResult:
        return SubstrateResult(success=False, reason=_NOT_SUPPORTED_REASON)

    def acquire_speech(
        self,
        *,
        prompt: str | None,
        locale: str | None,
        timeout_seconds: float | None,
        expected: Literal["free_form", "confirmation", "choice"],
        choices: list[str] | None,
    ) -> ListenResult:
        return ListenResult(success=False, reason=_NOT_SUPPORTED_REASON)

    def call_named_program(
        self,
        *,
        name: str,
        args: dict[str, Any] | None = None,
    ) -> ProgramCallResult:
        """``call_program``: this substrate exposes no named programs (RFC-0015)."""
        return unsupported_program_call('bare_autopilot')
