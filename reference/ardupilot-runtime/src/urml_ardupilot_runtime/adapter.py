"""ArduCopterAdapter — ArduPilot (ArduCopter) MAVLink substrate adapter.

Subclasses ``PX4Adapter`` from the PX4 reference runtime. The two autopilots
share the MAVLink command set, so the wire format is the same; what differs
is *firmware behaviour* around those commands, and that is what this class
owns:

- **Mode entry.** ArduCopter accepts ``MAV_CMD_NAV_TAKEOFF`` and
  position setpoints only in GUIDED. PX4 auto-enters its equivalent.
- **Arming.** ArduCopter never arms itself for a GCS-commanded take-off.
  This adapter sends ``MAV_CMD_COMPONENT_ARM_DISARM`` and waits for the
  armed flag on a heartbeat. A refused arm surfaces the autopilot's own
  ``PreArm:`` STATUSTEXT as the reason. Nothing here disables pre-arm
  checks.
- **Ack filtering.** ArduPilot links are chatty; ``COMMAND_ACK`` is
  matched on its ``command`` field rather than taken first-come.
- **Arrival.** A GUIDED setpoint is one-shot, so ``move_to`` waits until
  the aircraft reports itself within ``arrival_radius_m`` (or times out).
  That is what makes a ``sequence`` of waypoints mean what it says.
- **Global setpoints.** A location bound to WGS84 in the config flies as
  ``SET_POSITION_TARGET_GLOBAL_INT`` (relative-altitude frame).
- **Camera and output lines.** ``capture`` triggers the on-board camera;
  ``set_output`` drives an ArduPilot gripper, winch, or servo.

Failures are returned, never raised, matching every other URML adapter.
Only a broken connection that cannot be opened raises.

## Bench versus field

On a bench with no GPS fix, GUIDED entry or arming is refused by the
autopilot. This adapter reports that refusal verbatim and stops. That is
the intended bench proof: the link works, the vehicle said no, nothing
moved.
"""

from __future__ import annotations

import math
import time
from collections import deque
from contextlib import suppress
from typing import Any, Literal

from urml_px4_runtime.adapter import PX4Adapter
from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    NavigationResult,
    SubstrateResult,
)

from urml_ardupilot_runtime.config import (
    ArduPilotAdapterConfig,
    GlobalPosition,
    OutputLineBinding,
    load_ardupilot_config,
)

__all__ = ["ArduCopterAdapter", "probe"]

# MAVLink constants (common.xml / ardupilotmega.xml). Spelled out so the
# module needs no pymavlink import to load, and so tests can assert on ids.
MAV_AUTOPILOT_ARDUPILOTMEGA = 3
MAV_TYPE_COPTER = frozenset({2, 13, 14, 15, 29})  # quad, hexa, octo, tri, dodeca

MAV_CMD_NAV_TAKEOFF = 22
MAV_CMD_DO_SET_MODE = 176
MAV_CMD_DO_SET_SERVO = 183
MAV_CMD_DO_SET_ROI_LOCATION = 195
MAV_CMD_DO_SET_ROI_NONE = 197
MAV_CMD_DO_DIGICAM_CONTROL = 203
MAV_CMD_DO_GRIPPER = 211
MAV_CMD_COMPONENT_ARM_DISARM = 400
MAV_CMD_SET_MESSAGE_INTERVAL = 511
MAV_CMD_REQUEST_MESSAGE = 512
MAV_CMD_DO_WINCH = 42600

MAV_MODE_FLAG_CUSTOM_MODE_ENABLED = 1
MAV_MODE_FLAG_SAFETY_ARMED = 128
MAV_FRAME_LOCAL_NED = 1
MAV_FRAME_GLOBAL_RELATIVE_ALT_INT = 6

GRIPPER_ACTION_RELEASE = 0
GRIPPER_ACTION_GRAB = 1
WINCH_DELIVER = 4
WINCH_RETRACT = 6

MSG_ID_HEARTBEAT = 0
MSG_ID_GPS_RAW_INT = 24
MSG_ID_LOCAL_POSITION_NED = 32
MSG_ID_GLOBAL_POSITION_INT = 33
MSG_ID_BATTERY_STATUS = 147
MSG_ID_AUTOPILOT_VERSION = 148

# ArduCopter flight-mode numbers. pymavlink's ``mode_mapping()`` is
# preferred at runtime; this table is the fallback so the adapter also
# works against a minimal connection object.
COPTER_MODES: dict[str, int] = {
    "STABILIZE": 0,
    "ALT_HOLD": 2,
    "AUTO": 3,
    "GUIDED": 4,
    "LOITER": 5,
    "RTL": 6,
    "LAND": 9,
    "POSHOLD": 16,
    "BRAKE": 17,
}
_MODE_NAMES = {v: k for k, v in COPTER_MODES.items()}

_MAV_RESULT_NAMES = {
    0: "accepted",
    1: "temporarily_rejected",
    2: "denied",
    3: "unsupported",
    4: "failed",
    5: "in_progress",
    6: "cancelled",
}

# Position-only type_mask: ignore velocity, acceleration, yaw, yaw rate.
_POSITION_ONLY_MASK = 0b0000_1111_1111_1000

_EARTH_RADIUS_M = 6_371_000.0


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres between two WGS84 points."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(a))


class ArduCopterAdapter(PX4Adapter):
    """MAVLink adapter for ArduCopter over pymavlink."""

    def __init__(self, config: ArduPilotAdapterConfig | None = None) -> None:
        cfg = config or ArduPilotAdapterConfig()
        super().__init__(cfg)
        self._ap_config: ArduPilotAdapterConfig = cfg
        self._statustext: deque[str] = deque(maxlen=20)
        self._last_heartbeat: Any = None
        self._last_global: Any = None
        self._last_local: Any = None
        self._capture_count = 0
        self._roi_active = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def __enter__(self) -> ArduCopterAdapter:
        return self

    def _connect(self) -> Any:
        """Open the link, verify it is an ArduCopter, request telemetry."""
        if self._connection is not None:
            return self._connection
        url = self._ap_config.effective_connection_url()
        conn = self._mavutil.mavlink_connection(
            url,
            source_system=self._ap_config.system_id,
            source_component=self._ap_config.component_id,
        )
        hb = conn.wait_heartbeat(timeout=self._ap_config.heartbeat_timeout_seconds)
        if hb is None:
            with suppress(Exception):
                conn.close()
            raise RuntimeError(
                f"heartbeat_timeout: no MAVLink heartbeat on {url!r} within "
                f"{self._ap_config.heartbeat_timeout_seconds:.0f}s"
            )
        autopilot = getattr(hb, "autopilot", None)
        vehicle_type = getattr(hb, "type", None)
        if autopilot != MAV_AUTOPILOT_ARDUPILOTMEGA:
            with suppress(Exception):
                conn.close()
            raise RuntimeError(
                f"not_an_ardupilot_autopilot: heartbeat autopilot={autopilot!r} "
                f"(expected {MAV_AUTOPILOT_ARDUPILOTMEGA} = MAV_AUTOPILOT_ARDUPILOTMEGA)"
            )
        if vehicle_type not in MAV_TYPE_COPTER:
            with suppress(Exception):
                conn.close()
            raise RuntimeError(
                f"not_a_copter: heartbeat MAV_TYPE={vehicle_type!r}; ArduCopterAdapter v0.1 "
                "supports multirotor types only (ArduPlane / ArduRover are RFC-0041 follow-ups)"
            )
        self._last_heartbeat = hb
        self._connection = conn
        self._request_streams(conn)
        return conn

    def _request_streams(self, conn: Any) -> None:
        """Ask for position and battery at ``stream_rate_hz`` (fire and forget).

        ArduPilot honours ``SET_MESSAGE_INTERVAL`` regardless of the
        ``SR*_`` stream parameters, so the measurement and arrival paths do
        not depend on how the board happens to be configured.
        """
        interval_us = int(1_000_000 / self._ap_config.stream_rate_hz)
        for msg_id in (
            MSG_ID_GLOBAL_POSITION_INT,
            MSG_ID_LOCAL_POSITION_NED,
            MSG_ID_BATTERY_STATUS,
            MSG_ID_GPS_RAW_INT,
        ):
            conn.mav.command_long_send(
                conn.target_system,
                conn.target_component,
                MAV_CMD_SET_MESSAGE_INTERVAL,
                0,
                float(msg_id),
                float(interval_us),
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            )

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _note(self, msg: Any) -> None:
        """Cache the messages the adapter reads state from."""
        kind = msg.get_type() if hasattr(msg, "get_type") else None
        if kind == "HEARTBEAT":
            self._last_heartbeat = msg
        elif kind == "GLOBAL_POSITION_INT":
            self._last_global = msg
        elif kind == "LOCAL_POSITION_NED":
            self._last_local = msg
        elif kind == "STATUSTEXT":
            text = getattr(msg, "text", "")
            if isinstance(text, bytes):
                text = text.decode("utf-8", "replace")
            text = str(text).rstrip("\x00").strip()
            if text:
                self._statustext.append(text)

    def _recent_prearm_text(self, *, listen_seconds: float = 1.5) -> str:
        """The autopilot's own explanation for a refusal, if it gave one.

        ArduPilot sends the ``PreArm:`` / ``Arm:`` STATUSTEXT lines shortly
        *after* the failed COMMAND_ACK, so listen briefly before composing
        the reason.
        """
        conn = self._connection
        if conn is not None and listen_seconds > 0:
            deadline = time.monotonic() + listen_seconds
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                msg = conn.recv_match(type=["STATUSTEXT"], blocking=True, timeout=remaining)
                if msg is None:
                    break
                self._note(msg)
        hits = [t for t in self._statustext if t.startswith(("PreArm", "Arm:", "Mode change", "Flight mode"))]
        if not hits:
            hits = list(self._statustext)[-2:]
        return "; ".join(hits)

    def _send_command_long(self, command: int, *params: float) -> tuple[bool, str | None]:
        """Send a MAV_CMD via COMMAND_LONG and wait for *its* COMMAND_ACK.

        Unlike the PX4 base class, the ack is matched on ``ack.command`` so a
        stray ack for an earlier command (stream requests, a GCS on the same
        link) cannot be mistaken for ours. STATUSTEXT seen while waiting is
        kept so a rejection can carry the autopilot's reason.
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
            0,
            *padded[:7],
        )
        deadline = time.monotonic() + self._ap_config.ack_timeout_seconds
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False, "ack_timeout"
            msg = conn.recv_match(type=["COMMAND_ACK", "STATUSTEXT"], blocking=True, timeout=remaining)
            if msg is None:
                return False, "ack_timeout"
            self._note(msg)
            if msg.get_type() != "COMMAND_ACK":
                continue
            if int(getattr(msg, "command", -1)) != command:
                continue
            result = int(getattr(msg, "result", -1))
            if result == 0:
                return True, None
            return False, f"mav_result_{_MAV_RESULT_NAMES.get(result, result)}"

    def _wait_for(self, msg_type: str, predicate: Any, timeout_seconds: float) -> Any | None:
        """Read ``msg_type`` messages until ``predicate`` holds or time runs out."""
        try:
            conn = self._connect()
        except Exception:
            return None
        deadline = time.monotonic() + timeout_seconds
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            msg = conn.recv_match(type=[msg_type, "STATUSTEXT"], blocking=True, timeout=remaining)
            if msg is None:
                return None
            self._note(msg)
            if msg.get_type() == msg_type and predicate(msg):
                return msg

    def _mode_id(self, name: str) -> int | None:
        try:
            conn = self._connect()
        except Exception:
            return None
        mapping = None
        getter = getattr(conn, "mode_mapping", None)
        if callable(getter):
            with suppress(Exception):
                mapping = getter()
        if not mapping or name not in mapping:
            mapping = COPTER_MODES
        value = mapping.get(name)
        return int(value) if value is not None else None

    def _current_mode(self) -> int | None:
        hb = self._last_heartbeat
        if hb is None:
            return None
        return int(getattr(hb, "custom_mode", -1))

    def _mode_name(self) -> str:
        mode = self._current_mode()
        if mode is None:
            return "unknown"
        return _MODE_NAMES.get(mode, str(mode))

    def _is_armed(self) -> bool:
        hb = self._last_heartbeat
        if hb is None:
            return False
        return bool(int(getattr(hb, "base_mode", 0)) & MAV_MODE_FLAG_SAFETY_ARMED)

    def _set_mode(self, name: str) -> tuple[bool, str | None]:
        """Enter a flight mode and confirm it on a heartbeat."""
        try:
            self._connect()
        except Exception as exc:
            return False, f"connection_failed: {exc}"
        mode_id = self._mode_id(name)
        if mode_id is None:
            return False, f"mode_unknown: {name!r}"
        if self._current_mode() == mode_id:
            return True, None
        ok, reason = self._send_command_long(
            MAV_CMD_DO_SET_MODE, float(MAV_MODE_FLAG_CUSTOM_MODE_ENABLED), float(mode_id)
        )
        if not ok:
            detail = self._recent_prearm_text()
            return False, f"mode_rejected: {name} {reason}" + (f"; {detail}" if detail else "")
        hb = self._wait_for(
            "HEARTBEAT",
            lambda m: int(getattr(m, "custom_mode", -1)) == mode_id,
            self._ap_config.mode_timeout_seconds,
        )
        if hb is None:
            detail = self._recent_prearm_text()
            return False, f"mode_rejected: {name} not confirmed on heartbeat" + (f"; {detail}" if detail else "")
        return True, None

    def _arm(self) -> tuple[bool, str | None]:
        """Arm and confirm the armed flag on a heartbeat. Never bypasses pre-arm."""
        if self._is_armed():
            return True, None
        ok, reason = self._send_command_long(MAV_CMD_COMPONENT_ARM_DISARM, 1.0)
        if not ok:
            detail = self._recent_prearm_text()
            return False, f"arm_rejected: {reason}" + (f"; {detail}" if detail else "")
        hb = self._wait_for(
            "HEARTBEAT",
            lambda m: bool(int(getattr(m, "base_mode", 0)) & MAV_MODE_FLAG_SAFETY_ARMED),
            self._ap_config.arm_timeout_seconds,
        )
        if hb is None:
            detail = self._recent_prearm_text()
            return False, "arm_rejected: armed flag not seen on heartbeat" + (f"; {detail}" if detail else "")
        return True, None

    def _relative_alt_m(self, msg: Any) -> float:
        return float(getattr(msg, "relative_alt", 0)) / 1000.0

    # ------------------------------------------------------------------
    # Drone-profile dispatch
    # ------------------------------------------------------------------

    def send_takeoff_goal(
        self,
        *,
        altitude: float,
        climb_rate: float | None = None,
    ) -> NavigationResult:
        target = float(altitude)
        ok, reason = self._set_mode("GUIDED")
        if not ok:
            return NavigationResult(success=False, reason=reason)
        ok, reason = self._arm()
        if not ok:
            return NavigationResult(success=False, reason=reason)
        ok, reason = self._send_command_long(MAV_CMD_NAV_TAKEOFF, 0, 0, 0, 0, 0, 0, target)
        if not ok:
            detail = self._recent_prearm_text()
            return NavigationResult(
                success=False,
                reason=f"takeoff_rejected: {reason}" + (f"; {detail}" if detail else ""),
            )
        reached = self._wait_for(
            "GLOBAL_POSITION_INT",
            lambda m: self._relative_alt_m(m) >= 0.95 * target,
            self._ap_config.takeoff_timeout_seconds,
        )
        if reached is None:
            return NavigationResult(success=False, reason="takeoff_timeout: target altitude not reached")
        return NavigationResult(
            success=True,
            final_pose={"x": 0.0, "y": 0.0, "z": self._relative_alt_m(reached)},
            frame="agl",
        )

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        self._clear_roi()
        ok, reason = self._set_mode("LAND")
        if not ok:
            return NavigationResult(success=False, reason=reason)
        # Landing ends with an automatic disarm. Wait for it, bounded; a
        # confirmed mode change is still a success if the wait runs out.
        self._wait_for(
            "HEARTBEAT",
            lambda m: not (int(getattr(m, "base_mode", 0)) & MAV_MODE_FLAG_SAFETY_ARMED),
            self._ap_config.arrival_timeout_seconds,
        )
        return NavigationResult(success=True)

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        self._clear_roi()
        ok, reason = self._set_mode("RTL")
        if not ok:
            return NavigationResult(success=False, reason=reason)
        return NavigationResult(success=True)

    # ------------------------------------------------------------------
    # Navigation
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
        # hover with no `over` reaches here as speed == 0 and no target:
        # in GUIDED an ArduCopter holds position on its own, so this is a
        # confirmed no-op rather than a failure.
        if location is None and pose is None:
            if speed == 0.0:
                ok, reason = self._set_mode("GUIDED")
                return NavigationResult(success=ok, reason=reason)
            return NavigationResult(
                success=False,
                reason="send_navigation_goal called without location or pose",
            )

        if location is not None:
            gp = self._ap_config.resolve_global(location)
            if gp is not None:
                return self._fly_global(gp)
            ned = self._ap_config.resolve_location(location)
            if ned is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: {location!r} is declared in the manifest "
                    "but not bound in the adapter config (location_to_global or location_to_pose).",
                )
            north, east, alt = ned.north, ned.east, ned.alt
        else:
            assert pose is not None
            north = float(pose.get("x", 0.0))
            east = float(pose.get("y", 0.0))
            alt = float(pose.get("z", 0.0))
        return self._fly_local(north, east, alt, frame)

    def _fly_local(self, north: float, east: float, alt: float, frame: str | None) -> NavigationResult:
        ok, reason = self._set_mode("GUIDED")
        if not ok:
            return NavigationResult(success=False, reason=reason)
        conn = self._connection
        conn.mav.set_position_target_local_ned_send(
            0,
            conn.target_system,
            conn.target_component,
            MAV_FRAME_LOCAL_NED,
            _POSITION_ONLY_MASK,
            north,
            east,
            -alt,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        radius = self._ap_config.arrival_radius_m
        alt_tol = self._ap_config.arrival_alt_tolerance_m

        def _arrived(m: Any) -> bool:
            dx = float(getattr(m, "x", 0.0)) - north
            dy = float(getattr(m, "y", 0.0)) - east
            dz = -float(getattr(m, "z", 0.0)) - alt
            return math.hypot(dx, dy) <= radius and abs(dz) <= alt_tol

        got = self._wait_for("LOCAL_POSITION_NED", _arrived, self._ap_config.arrival_timeout_seconds)
        if got is None:
            return NavigationResult(success=False, reason="arrival_timeout: setpoint not reached")
        return NavigationResult(
            success=True,
            final_pose={"x": north, "y": east, "z": alt},
            frame=frame or "ned",
        )

    def _fly_global(self, gp: GlobalPosition) -> NavigationResult:
        ok, reason = self._set_mode("GUIDED")
        if not ok:
            return NavigationResult(success=False, reason=reason)
        conn = self._connection
        conn.mav.set_position_target_global_int_send(
            0,
            conn.target_system,
            conn.target_component,
            MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            _POSITION_ONLY_MASK,
            round(gp.lat * 1e7),
            round(gp.lon * 1e7),
            float(gp.alt_agl),
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        radius = self._ap_config.arrival_radius_m
        alt_tol = self._ap_config.arrival_alt_tolerance_m

        def _arrived(m: Any) -> bool:
            lat = float(getattr(m, "lat", 0)) / 1e7
            lon = float(getattr(m, "lon", 0)) / 1e7
            d = _haversine_m(lat, lon, gp.lat, gp.lon)
            return d <= radius and abs(self._relative_alt_m(m) - gp.alt_agl) <= alt_tol

        got = self._wait_for("GLOBAL_POSITION_INT", _arrived, self._ap_config.arrival_timeout_seconds)
        if got is None:
            return NavigationResult(success=False, reason="arrival_timeout: global setpoint not reached")
        if gp.look_at is not None:
            ok, reason = self._send_command_long(
                MAV_CMD_DO_SET_ROI_LOCATION, 0, 0, 0, 0, gp.look_at.lat, gp.look_at.lon, 0.0
            )
            if not ok:
                return NavigationResult(success=False, reason=f"roi_rejected: {reason}")
            self._roi_active = True
        return NavigationResult(
            success=True,
            final_pose={"x": gp.lon, "y": gp.lat, "z": gp.alt_agl},
            frame="wgs84",
        )

    def _clear_roi(self) -> None:
        if not self._roi_active:
            return
        self._roi_active = False
        with suppress(Exception):
            self._send_command_long(MAV_CMD_DO_SET_ROI_NONE)

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------

    def capture_media(
        self,
        *,
        media: Literal["photo", "video"],
        target: str | None,
        duration_seconds: float | None,
        attributes: dict[str, Any] | None,
    ) -> CaptureResult:
        cam = self._ap_config.camera
        if cam is None:
            return CaptureResult(
                success=False,
                reason="camera_not_configured: set `camera:` in the adapter config "
                "(kind: digicam | servo) to trigger an autopilot-wired camera.",
            )
        if media != "photo":
            return CaptureResult(
                success=False, reason="video_not_supported: ArduCopterAdapter v0.1 triggers stills only"
            )
        if cam.kind == "servo":
            if cam.channel is None:
                return CaptureResult(success=False, reason="camera_not_configured: servo trigger needs `channel`")
            ok, reason = self._send_command_long(MAV_CMD_DO_SET_SERVO, float(cam.channel), float(cam.pwm_on))
            if ok:
                time.sleep(cam.pulse_ms / 1000.0)
                ok, reason = self._send_command_long(MAV_CMD_DO_SET_SERVO, float(cam.channel), float(cam.pwm_off))
        else:
            # DO_DIGICAM_CONTROL: p5 = shoot command (1 = trigger).
            ok, reason = self._send_command_long(MAV_CMD_DO_DIGICAM_CONTROL, 0, 0, 0, 0, 1, 0, 0)
        if not ok:
            return CaptureResult(success=False, reason=f"capture_rejected: {reason}")
        if cam.settle_seconds > 0:
            time.sleep(cam.settle_seconds)
        self._capture_count += 1
        g = self._last_global
        pose = (
            {
                "lat": float(getattr(g, "lat", 0)) / 1e7,
                "lon": float(getattr(g, "lon", 0)) / 1e7,
                "alt_agl": self._relative_alt_m(g),
            }
            if g is not None
            else None
        )
        return CaptureResult(
            success=True,
            payload={
                "type": "photo",
                "format": "on-camera",
                "uri": f"camera://shot/{self._capture_count}",
                "pose": pose,
                "frame": "wgs84" if pose else None,
                "timestamp": time.time(),
                "_note": "Image is stored on the camera, not transferred over MAVLink. "
                "The pose is the autopilot position at trigger time.",
            },
        )

    # ------------------------------------------------------------------
    # Output lines (RFC-0017): gripper, winch, servo
    # ------------------------------------------------------------------

    def set_output_line(
        self,
        *,
        output: str,
        value: bool | float,
        pulse_ms: float | None = None,
    ) -> SubstrateResult:
        binding = self._ap_config.output_lines.get(output)
        if binding is None:
            return SubstrateResult(
                success=False,
                reason=f"output_line_not_configured: {output!r} has no entry in the adapter config `output_lines`.",
            )
        on = bool(value)
        ok, reason = self._drive_line(binding, on)
        if not ok:
            return SubstrateResult(success=False, reason=f"output_rejected: {output} {reason}")
        if pulse_ms is not None:
            time.sleep(float(pulse_ms) / 1000.0)
            ok, reason = self._drive_line(binding, not on)
            if not ok:
                return SubstrateResult(success=False, reason=f"output_rejected: {output} revert {reason}")
        return SubstrateResult(success=True)

    def _drive_line(self, binding: OutputLineBinding, on: bool) -> tuple[bool, str | None]:
        if binding.kind == "gripper":
            action = GRIPPER_ACTION_RELEASE if on else GRIPPER_ACTION_GRAB
            return self._send_command_long(MAV_CMD_DO_GRIPPER, float(binding.instance), float(action))
        if binding.kind == "winch":
            action = WINCH_DELIVER if on else WINCH_RETRACT
            length = binding.deliver_length_m if on else 0.0
            return self._send_command_long(
                MAV_CMD_DO_WINCH, float(binding.instance), float(action), length, binding.rate_m_s
            )
        if binding.channel is None:
            return False, "servo binding needs `channel`"
        pwm = binding.on_pwm if on else binding.off_pwm
        return self._send_command_long(MAV_CMD_DO_SET_SERVO, float(binding.channel), float(pwm))

    # ------------------------------------------------------------------
    # Read-only identity probe
    # ------------------------------------------------------------------

    def probe(self, *, listen_seconds: float = 3.0) -> dict[str, Any]:
        """Identity snapshot. Sends only a version request; changes no state."""
        conn = self._connect()
        hb = self._last_heartbeat
        out: dict[str, Any] = {
            "connection_url": self._ap_config.effective_connection_url(),
            "autopilot": "ArduPilot" if getattr(hb, "autopilot", None) == MAV_AUTOPILOT_ARDUPILOTMEGA else "unknown",
            "mav_type": int(getattr(hb, "type", -1)),
            "system_id": int(hb.get_srcSystem()) if hasattr(hb, "get_srcSystem") else int(conn.target_system),
            "component_id": (
                int(hb.get_srcComponent()) if hasattr(hb, "get_srcComponent") else int(conn.target_component)
            ),
            "armed": self._is_armed(),
            "mode": self._mode_name(),
            "firmware": None,
            "battery_v": None,
            "gps_fix": None,
            "satellites": None,
        }
        conn.mav.command_long_send(
            conn.target_system,
            conn.target_component,
            MAV_CMD_REQUEST_MESSAGE,
            0,
            float(MSG_ID_AUTOPILOT_VERSION),
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        deadline = time.monotonic() + listen_seconds
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            msg = conn.recv_match(blocking=True, timeout=remaining)
            if msg is None:
                break
            self._note(msg)
            kind = msg.get_type()
            if kind == "AUTOPILOT_VERSION":
                fv = int(getattr(msg, "flight_sw_version", 0))
                out["firmware"] = f"{(fv >> 24) & 0xFF}.{(fv >> 16) & 0xFF}.{(fv >> 8) & 0xFF}"
            elif kind == "BATTERY_STATUS":
                volts = getattr(msg, "voltages", None) or [0]
                if volts and int(volts[0]) != 0xFFFF:
                    out["battery_v"] = round(float(volts[0]) / 1000.0, 2)
            elif kind == "SYS_STATUS" and out["battery_v"] is None:
                mv = int(getattr(msg, "voltage_battery", 0))
                if mv and mv != 0xFFFF:
                    out["battery_v"] = round(mv / 1000.0, 2)
            elif kind == "GPS_RAW_INT":
                out["gps_fix"] = int(getattr(msg, "fix_type", 0))
                out["satellites"] = int(getattr(msg, "satellites_visible", 0))
            elif kind == "HEARTBEAT":
                out["armed"] = self._is_armed()
                out["mode"] = self._mode_name()
        out["statustext"] = list(self._statustext)
        return out


def probe(config: ArduPilotAdapterConfig | str | None = None, *, listen_seconds: float = 3.0) -> dict[str, Any]:
    """Convenience: open, probe, close. ``config`` may be a path or a config."""
    if isinstance(config, str):
        cfg = load_ardupilot_config(config)
    else:
        cfg = config or ArduPilotAdapterConfig()
    with ArduCopterAdapter(cfg) as adapter:
        return adapter.probe(listen_seconds=listen_seconds)
