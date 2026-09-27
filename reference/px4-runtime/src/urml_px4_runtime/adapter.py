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

## Flight: success means the vehicle did it

A ``COMMAND_ACK`` only says PX4 accepted a command, not that the vehicle
flew. Each flight primitive therefore sends its command and then reads
telemetry until the action is complete, or returns a failure:

- ``take_off``: arms if disarmed (``MAV_CMD_COMPONENT_ARM_DISARM``, then
  the armed bit on ``HEARTBEAT``), sends ``MAV_CMD_NAV_TAKEOFF`` with an
  AMSL altitude (home altitude from ``HOME_POSITION`` plus the requested
  height; PX4 reads param 7 as AMSL), and waits until
  ``GLOBAL_POSITION_INT.relative_alt`` reaches the target.
- ``move_to`` / ``hover`` over a place: converts the NED offset from home
  to WGS84 and sends ``MAV_CMD_DO_REPOSITION`` as ``COMMAND_INT``
  (degE7 integers, so no float precision loss), then waits until the
  vehicle is inside the acceptance radius and altitude band.
- ``return_to_home``: ``MAV_CMD_NAV_RETURN_TO_LAUNCH``, then waits until
  the vehicle is within the acceptance radius of home, in the air or
  landed (PX4 RTL lands on its own).
- ``land``: reports an already-grounded vehicle as such; otherwise
  ``MAV_CMD_NAV_LAND`` and a wait for ``EXTENDED_SYS_STATE`` ON_GROUND.

A rejected command, a refused arm, or a timeout returns a failure whose
reason names PX4's ``MAV_RESULT`` or what telemetry last showed (the
altitude reached, the distance left). PX4 sends its ``STATUSTEXT``
explanations only on links where it sees a ground-station heartbeat;
this adapter sends none, so the explanation is on the autopilot console
or the ground station, not in the reason. Failures are *returned*, not
raised, the same contract as RclpyAdapter and MockROSAdapter. A
connection that cannot be opened is reported as ``connection_failed``.

The adapter reads a PX4 autopilot only: the first autopilot heartbeat
must say ``MAV_AUTOPILOT_PX4``. PX4 and ArduPilot read the same
MAVLink commands differently (take-off altitude is AMSL on PX4 and
relative on ArduPilot), so pointing this adapter at another autopilot is
refused rather than guessed at. ``ArduCopterAdapter`` covers ArduPilot.

## What's not supported on a bare autopilot

PX4 itself doesn't have grippers, cameras, microphones, or perception
nodes — those live on a companion computer (typically ROS-2-backed).
The corresponding methods (`grasp`, `release`, `detect`, `capture`,
`speak`, `listen`, `dock`) return ``NavigationResult(success=False,
reason="not_supported_on_bare_autopilot: ...")``. Programs that need
both flight control *and* perception/manipulation should pair PX4Adapter
with RclpyAdapter via ``CompositeAdapter``.
"""

from __future__ import annotations

import math
import time
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, Literal

from urml_ros2_runtime.substrate.base import (
    CaptureResult,
    DetectionResult,
    ListenResult,
    ManipulationResult,
    MeasurementResult,
    NavigationResult,
    ProgramCallResult,
    ScanResult,
    SubstrateResult,
    WaitResult,
    unsupported_program_call,
)

from urml_px4_runtime.config import PX4AdapterConfig

DEFAULT_HEARTBEAT_TIMEOUT_SECONDS = 5.0

# MAVLink constants (common.xml). Spelled out so the module needs no
# pymavlink import to load, and so tests can assert on ids.
MAV_AUTOPILOT_PX4 = 12
MAV_AUTOPILOT_INVALID = 8

MAV_CMD_NAV_RETURN_TO_LAUNCH = 20
MAV_CMD_NAV_LAND = 21
MAV_CMD_NAV_TAKEOFF = 22
MAV_CMD_DO_REPOSITION = 192
MAV_CMD_COMPONENT_ARM_DISARM = 400
MAV_CMD_REQUEST_MESSAGE = 512

MAV_DO_REPOSITION_FLAGS_CHANGE_MODE = 1
MAV_FRAME_GLOBAL = 0
MAV_MODE_FLAG_SAFETY_ARMED = 128
MAV_RESULT_ACCEPTED = 0
MAV_RESULT_IN_PROGRESS = 5

MAV_LANDED_STATE_UNDEFINED = 0
MAV_LANDED_STATE_ON_GROUND = 1

MSG_ID_HOME_POSITION = 242

_MAV_RESULT_NAMES = {
    0: "accepted",
    1: "temporarily_rejected",
    2: "denied",
    3: "unsupported",
    4: "failed",
    5: "in_progress",
    6: "cancelled",
}
_LANDED_STATE_NAMES = {0: "undefined", 1: "on_ground", 2: "in_air", 3: "takeoff", 4: "landing"}

# The telemetry every flight wait keeps current while it reads.
_STATE_TYPES = ("HEARTBEAT", "GLOBAL_POSITION_INT", "EXTENDED_SYS_STATE", "HOME_POSITION")

# Upper bound on messages read when catching up with the link. PX4 streams
# a few hundred messages a second on the onboard link; this is minutes of
# backlog, and it keeps a flooded link from pinning the adapter.
_DRAIN_MAX_MESSAGES = 50_000

# PX4's CONSTANTS_RADIUS_OF_EARTH; the projection below matches PX4's own.
_EARTH_RADIUS_M = 6_371_000.0


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


@dataclass(frozen=True)
class _Home:
    """PX4's home position, from ``HOME_POSITION``."""

    lat: float  # degrees
    lon: float  # degrees
    alt_amsl: float  # metres above mean sea level


def _offset_to_global(lat0: float, lon0: float, north: float, east: float) -> tuple[float, float]:
    """WGS84 point ``north`` / ``east`` metres from ``(lat0, lon0)``.

    Azimuthal equidistant reprojection, the same projection PX4 uses
    between its local frame and WGS84 (``MapProjection::reproject``), so
    an offset in the adapter config lands where PX4's local frame says.
    """
    x = north / _EARTH_RADIUS_M
    y = east / _EARTH_RADIUS_M
    c = math.hypot(x, y)
    if c == 0.0:
        return lat0, lon0
    lat0_r = math.radians(lat0)
    sin_c, cos_c = math.sin(c), math.cos(c)
    lat = math.asin(cos_c * math.sin(lat0_r) + x * sin_c * math.cos(lat0_r) / c)
    lon = math.radians(lon0) + math.atan2(
        y * sin_c, c * math.cos(lat0_r) * cos_c - x * math.sin(lat0_r) * sin_c
    )
    return math.degrees(lat), math.degrees(lon)


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in metres between two WGS84 points."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = p2 - p1
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * _EARTH_RADIUS_M * math.asin(math.sqrt(min(1.0, a)))


def _deg_e7(degrees: float) -> int:
    return round(degrees * 1e7)


def _relative_alt_m(msg: Any) -> float:
    """``GLOBAL_POSITION_INT.relative_alt`` (mm above home) in metres."""
    return float(getattr(msg, "relative_alt", 0)) / 1000.0


def _distance_to(msg: Any, lat: float, lon: float) -> float:
    """Horizontal distance from a ``GLOBAL_POSITION_INT`` fix to a point."""
    return _haversine_m(float(getattr(msg, "lat", 0)) / 1e7, float(getattr(msg, "lon", 0)) / 1e7, lat, lon)


def _is_armed_heartbeat(msg: Any) -> bool:
    return bool(int(getattr(msg, "base_mode", 0)) & MAV_MODE_FLAG_SAFETY_ARMED)


class PX4Adapter:
    """MAVLink-based URML substrate adapter."""

    def __init__(self, config: PX4AdapterConfig | None = None) -> None:
        self._mavutil = _require_pymavlink()
        self._config = config or PX4AdapterConfig()
        self._connection: Any = None
        self._closed = False
        # The autopilot this adapter talks to, locked from its heartbeat.
        self._target: tuple[int, int] | None = None
        # Latest telemetry, refreshed by every read (see _observe).
        self._heartbeat: Any = None
        self._global_position: Any = None
        self._extended_state: Any = None
        self._home: _Home | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def _connect(self) -> Any:
        """Open the MAVLink connection lazily; cache for reuse.

        Waits for the autopilot's heartbeat (other components on the link,
        such as a ground station, are skipped), checks it is PX4, and locks
        the command target to that autopilot. Raises ``RuntimeError`` when
        no PX4 heartbeat arrives; callers turn that into a failure result.
        """
        if self._connection is not None:
            return self._connection
        url = self._config.connection_url
        conn = self._mavutil.mavlink_connection(
            url,
            source_system=self._config.system_id,
            source_component=self._config.component_id,
        )
        wait = self._config.heartbeat_timeout_seconds
        deadline = time.monotonic() + wait
        heartbeat: Any = None
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            msg = conn.wait_heartbeat(timeout=remaining)
            if msg is None:
                break
            if int(getattr(msg, "autopilot", MAV_AUTOPILOT_INVALID)) != MAV_AUTOPILOT_INVALID:
                heartbeat = msg
                break
        if heartbeat is None:
            with suppress(Exception):
                conn.close()
            raise RuntimeError(f"heartbeat_timeout: no autopilot heartbeat on {url!r} within {wait:.0f}s")
        autopilot = int(getattr(heartbeat, "autopilot", -1))
        if autopilot != MAV_AUTOPILOT_PX4:
            with suppress(Exception):
                conn.close()
            raise RuntimeError(
                f"not_a_px4_autopilot: heartbeat autopilot={autopilot} (expected {MAV_AUTOPILOT_PX4} = "
                "MAV_AUTOPILOT_PX4). PX4Adapter sends PX4 command semantics; use ArduCopterAdapter for ArduPilot."
            )
        get_system = getattr(heartbeat, "get_srcSystem", None)
        get_component = getattr(heartbeat, "get_srcComponent", None)
        if callable(get_system) and callable(get_component):
            self._target = (int(get_system()), int(get_component()))
        else:
            self._target = (int(conn.target_system), int(conn.target_component))
        self._heartbeat = heartbeat
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

    def _target_ids(self) -> tuple[int, int]:
        if self._target is not None:
            return self._target
        conn = self._connection
        return int(conn.target_system), int(conn.target_component)

    def _from_target(self, msg: Any) -> bool:
        """True when ``msg`` came from the locked autopilot.

        Heartbeats must match system and component (a ground station's
        heartbeat says "disarmed" and must not stand in for the vehicle's);
        other messages must match the system.
        """
        if self._target is None:
            return True
        get_system = getattr(msg, "get_srcSystem", None)
        if callable(get_system) and int(get_system()) != self._target[0]:
            return False
        if msg.get_type() == "HEARTBEAT":
            get_component = getattr(msg, "get_srcComponent", None)
            if callable(get_component) and int(get_component()) != self._target[1]:
                return False
        return True

    def _observe(self, msg: Any) -> None:
        """Keep the latest vehicle state from any message read."""
        kind = msg.get_type() if hasattr(msg, "get_type") else None
        if kind is None or not self._from_target(msg):
            return
        if kind == "HEARTBEAT":
            self._heartbeat = msg
        elif kind == "GLOBAL_POSITION_INT":
            self._global_position = msg
        elif kind == "EXTENDED_SYS_STATE":
            self._extended_state = msg
        elif kind == "HOME_POSITION":
            self._home = _Home(
                lat=float(getattr(msg, "latitude", 0)) / 1e7,
                lon=float(getattr(msg, "longitude", 0)) / 1e7,
                alt_amsl=float(getattr(msg, "altitude", 0)) / 1000.0,
            )

    def _drain(self) -> None:
        """Read everything already queued on the link.

        UDP backlog builds up whenever the adapter is not reading (between
        primitives, during ``wait``). Draining before a decision keeps the
        cached state current instead of seconds old.
        """
        conn = self._connection
        if conn is None:
            return
        for _ in range(_DRAIN_MAX_MESSAGES):
            msg = conn.recv_match(blocking=False)
            if msg is None:
                return
            self._observe(msg)

    def _begin(self) -> str | None:
        """Start a flight primitive: connect and catch up with the link."""
        try:
            self._connect()
        except Exception as exc:
            return f"connection_failed: {exc}"
        self._drain()
        return None

    def _await(self, msg_type: str, predicate: Callable[[Any], bool], timeout_seconds: float) -> Any | None:
        """Read until a ``msg_type`` message from the vehicle satisfies ``predicate``.

        Returns that message, or None on timeout. Every state message read
        on the way is observed, so the caches stay current.
        """
        conn = self._connection
        if conn is None:
            return None
        types = [msg_type, *(t for t in _STATE_TYPES if t != msg_type)]
        deadline = time.monotonic() + timeout_seconds
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            msg = conn.recv_match(type=types, blocking=True, timeout=remaining)
            if msg is None:
                return None
            self._observe(msg)
            if msg.get_type() == msg_type and self._from_target(msg) and predicate(msg):
                return msg

    def _wait_ack(self, command: int) -> tuple[bool, str | None]:
        """Wait for the COMMAND_ACK of ``command`` (matched on its id)."""
        ack = self._await(
            "COMMAND_ACK",
            lambda m: int(getattr(m, "command", -1)) == command
            and int(getattr(m, "result", -1)) != MAV_RESULT_IN_PROGRESS,
            self._config.ack_timeout_seconds,
        )
        if ack is None:
            return False, "ack_timeout"
        result = int(getattr(ack, "result", -1))
        if result == MAV_RESULT_ACCEPTED:
            return True, None
        return False, f"mav_result_{_MAV_RESULT_NAMES.get(result, result)}"

    def _send_command_long(self, command: int, *params: float) -> tuple[bool, str | None]:
        """Send a MAV_CMD_* via COMMAND_LONG; wait for its COMMAND_ACK.

        Returns ``(success, reason)``. params are MAVLink params 1-7;
        missing trailing params default to 0. An ack only says PX4 took
        the command; the flight primitives confirm the outcome separately.
        """
        try:
            conn = self._connect()
        except Exception as exc:
            return False, f"connection_failed: {exc}"
        padded = [float(p) for p in params] + [0.0] * (7 - len(params))
        target_system, target_component = self._target_ids()
        conn.mav.command_long_send(target_system, target_component, command, 0, *padded[:7])
        return self._wait_ack(command)

    def _send_command_int(
        self,
        command: int,
        frame: int,
        params: tuple[float, float, float, float],
        x: int,
        y: int,
        z: float,
    ) -> tuple[bool, str | None]:
        """Send a MAV_CMD_* via COMMAND_INT (integer lat / lon); wait for its ack."""
        try:
            conn = self._connect()
        except Exception as exc:
            return False, f"connection_failed: {exc}"
        target_system, target_component = self._target_ids()
        conn.mav.command_int_send(
            target_system, target_component, frame, command, 0, 0, *params, x, y, float(z)
        )
        return self._wait_ack(command)

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
    # Vehicle state
    # ------------------------------------------------------------------

    def _is_armed(self) -> bool:
        return self._heartbeat is not None and _is_armed_heartbeat(self._heartbeat)

    def _ensure_home(self) -> _Home | None:
        """PX4's home position: the latest one streamed, else requested."""
        if self._home is not None:
            return self._home
        return self._request_home()

    def _request_home(self) -> _Home | None:
        """Ask PX4 for its current home position (MAV_CMD_REQUEST_MESSAGE) and wait for it.

        PX4 moves home to the vehicle's position when it arms, so a take-off
        re-reads home after arming instead of trusting the pre-arm value.
        """
        conn = self._connection
        target_system, target_component = self._target_ids()
        conn.mav.command_long_send(
            target_system,
            target_component,
            MAV_CMD_REQUEST_MESSAGE,
            0,
            float(MSG_ID_HOME_POSITION),
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
        )
        self._await("HOME_POSITION", lambda _m: True, self._config.message_timeout_seconds)
        return self._home

    def _home_unknown(self) -> NavigationResult:
        return NavigationResult(
            success=False,
            reason=f"home_unknown: no HOME_POSITION from PX4 within {self._config.message_timeout_seconds:.0f}s. "
            "PX4 sets home once it has a global position estimate.",
        )

    def _current_position(self) -> Any | None:
        """The latest GLOBAL_POSITION_INT, waiting briefly if none has arrived."""
        if self._global_position is None:
            self._await("GLOBAL_POSITION_INT", lambda _m: True, self._config.message_timeout_seconds)
        return self._global_position

    def _landed_state(self) -> int:
        """EXTENDED_SYS_STATE.landed_state, waiting briefly if none has arrived."""
        if self._extended_state is None:
            self._await("EXTENDED_SYS_STATE", lambda _m: True, self._config.message_timeout_seconds)
        if self._extended_state is None:
            return MAV_LANDED_STATE_UNDEFINED
        return int(getattr(self._extended_state, "landed_state", MAV_LANDED_STATE_UNDEFINED))

    def _arm(self) -> tuple[bool, str | None]:
        """Arm and confirm the armed bit on a heartbeat. Never forces past PX4's checks."""
        ok, reason = self._send_command_long(MAV_CMD_COMPONENT_ARM_DISARM, 1.0)
        if not ok:
            return False, f"arm_rejected: {reason}"
        armed = self._await("HEARTBEAT", _is_armed_heartbeat, self._config.arm_timeout_seconds)
        if armed is None:
            return False, (
                f"arm_rejected: armed flag not seen on HEARTBEAT within {self._config.arm_timeout_seconds:.0f}s"
            )
        return True, None

    def _disarm_on_ground(self) -> None:
        """Best effort: disarm a vehicle this adapter armed and could not fly."""
        with suppress(Exception):
            self._send_command_long(MAV_CMD_COMPONENT_ARM_DISARM, 0.0)

    # ------------------------------------------------------------------
    # Drone-profile dispatch (the substantive PX4 surface)
    # ------------------------------------------------------------------

    def send_takeoff_goal(
        self,
        *,
        altitude: float,
        climb_rate: float | None = None,
    ) -> NavigationResult:
        # climb_rate has no MAVLink take-off parameter; PX4 climbs at its
        # MPC_TKO_SPEED. The target altitude is what the program states.
        target = float(altitude)
        if not (math.isfinite(target) and target > 0.0):
            return NavigationResult(success=False, reason=f"invalid_altitude: {altitude!r}")
        failure = self._begin()
        if failure is not None:
            return NavigationResult(success=False, reason=failure)
        home = self._ensure_home()
        if home is None:
            return self._home_unknown()

        armed_here = False
        if not self._is_armed():
            ok, reason = self._arm()
            if not ok:
                return NavigationResult(success=False, reason=reason)
            armed_here = True
            # Arming moved home to where the vehicle stands; aim from there.
            home = self._request_home() or home

        # MAV_CMD_NAV_TAKEOFF: param4 yaw, param5/6 lat/lon (NaN = keep
        # current heading and position), param7 altitude AMSL on PX4.
        ok, reason = self._send_command_long(
            MAV_CMD_NAV_TAKEOFF, 0.0, 0.0, 0.0, math.nan, math.nan, math.nan, home.alt_amsl + target
        )
        if not ok:
            if armed_here:
                self._disarm_on_ground()
            return NavigationResult(success=False, reason=f"takeoff_rejected: {reason}")

        # Airborne once within the altitude tolerance of the target (never
        # more than half the target, so a low take-off still has to leave
        # the ground).
        threshold = target - min(self._config.arrival_alt_tolerance_m, 0.5 * target)
        reached = self._await(
            "GLOBAL_POSITION_INT",
            lambda m: _relative_alt_m(m) >= threshold,
            self._config.takeoff_timeout_seconds,
        )
        if reached is None:
            last = self._global_position
            now = f"{_relative_alt_m(last):.1f} m" if last is not None else "unknown"
            return NavigationResult(
                success=False,
                reason=f"takeoff_timeout: relative altitude {now} after "
                f"{self._config.takeoff_timeout_seconds:.0f}s, target {target:.1f} m",
            )
        return NavigationResult(
            success=True,
            final_pose={"x": 0.0, "y": 0.0, "z": round(_relative_alt_m(reached), 2)},
            frame="agl",
        )

    def send_land_goal(
        self,
        *,
        at: str | None = None,
        precision: Literal["standard", "precise"] = "standard",
    ) -> NavigationResult:
        # Precision landing is a PX4 mode and parameter concern (a landing
        # target is needed); `precision` is not mapped and PX4 lands the
        # way it is configured to.
        failure = self._begin()
        if failure is not None:
            return NavigationResult(success=False, reason=failure)
        if at is not None:
            ned = self._config.resolve_location(at)
            if ned is None:
                return NavigationResult(
                    success=False,
                    reason=f"location_not_configured: land at {at!r} is not mapped to a NED pose in px4_adapter.yaml.",
                )
            moved = self._fly_to(ned.north, ned.east, None, speed=None, frame=None)
            if not moved.success:
                return NavigationResult(success=False, reason=f"land_at_failed: {moved.reason}")

        if self._landed_state() == MAV_LANDED_STATE_ON_GROUND:
            return NavigationResult(
                success=True,
                reason="already_on_ground: PX4 reports landed_state ON_GROUND; no LAND command sent.",
            )

        ok, reason = self._send_command_long(
            MAV_CMD_NAV_LAND, 0.0, 0.0, 0.0, math.nan, math.nan, math.nan, math.nan
        )
        if not ok:
            return NavigationResult(success=False, reason=f"land_rejected: {reason}")
        down = self._await(
            "EXTENDED_SYS_STATE",
            lambda m: int(getattr(m, "landed_state", -1)) == MAV_LANDED_STATE_ON_GROUND,
            self._config.land_timeout_seconds,
        )
        if down is None:
            state = _LANDED_STATE_NAMES.get(self._landed_state(), "unknown")
            return NavigationResult(
                success=False,
                reason=f"landing_timeout: landed_state {state} after {self._config.land_timeout_seconds:.0f}s",
            )
        return NavigationResult(success=True)

    def send_return_to_home_goal(
        self,
        *,
        speed: float | None = None,
        altitude: float | None = None,
    ) -> NavigationResult:
        # MAV_CMD_NAV_RETURN_TO_LAUNCH has no parameters. Return speed and
        # altitude are PX4 parameters (MPC_XY_CRUISE, RTL_RETURN_ALT) set
        # on the autopilot ahead of time.
        failure = self._begin()
        if failure is not None:
            return NavigationResult(success=False, reason=failure)
        home = self._ensure_home()
        if home is None:
            return self._home_unknown()
        radius = self._config.arrival_radius_m

        if not self._is_armed():
            here = self._current_position()
            if here is not None and _distance_to(here, home.lat, home.lon) <= radius:
                return NavigationResult(
                    success=True,
                    reason=f"already_at_home: disarmed within {radius:.1f} m of home; no RTL command sent.",
                    final_pose={"x": 0.0, "y": 0.0, "z": round(_relative_alt_m(here), 2)},
                    frame="agl",
                )
            return NavigationResult(
                success=False,
                reason=f"not_airborne: PX4 reports the vehicle disarmed and not within {radius:.1f} m of home; "
                "return_to_home needs an airborne vehicle.",
            )

        ok, reason = self._send_command_long(MAV_CMD_NAV_RETURN_TO_LAUNCH)
        if not ok:
            return NavigationResult(success=False, reason=f"rtl_rejected: {reason}")
        home_reached = self._await(
            "GLOBAL_POSITION_INT",
            lambda m: _distance_to(m, home.lat, home.lon) <= radius,
            self._config.arrival_timeout_seconds,
        )
        if home_reached is None:
            last = self._global_position
            away = f"{_distance_to(last, home.lat, home.lon):.1f} m" if last is not None else "an unknown distance"
            return NavigationResult(
                success=False,
                reason=f"rtl_timeout: {away} from home after {self._config.arrival_timeout_seconds:.0f}s",
            )
        return NavigationResult(
            success=True,
            final_pose={"x": 0.0, "y": 0.0, "z": round(_relative_alt_m(home_reached), 2)},
            frame="agl",
        )

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
        # Resolve to an offset from home. URML's `pose` is x/y/z; we treat
        # x -> north, y -> east, z -> metres above home (positive up). A
        # pose without z keeps the current altitude.
        alt: float | None
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
            alt = float(pose["z"]) if pose.get("z") is not None else None
        else:
            return NavigationResult(
                success=False,
                reason="send_navigation_goal called without location or pose",
            )
        return self._fly_to(north, east, alt, speed=speed, frame=frame)

    def _fly_to(
        self,
        north: float,
        east: float,
        alt: float | None,
        *,
        speed: float | None,
        frame: str | None,
    ) -> NavigationResult:
        """Reposition to an offset from home and wait for arrival."""
        failure = self._begin()
        if failure is not None:
            return NavigationResult(success=False, reason=failure)
        home = self._ensure_home()
        if home is None:
            return self._home_unknown()
        if not self._is_armed():
            return NavigationResult(
                success=False,
                reason="not_airborne: PX4 reports the vehicle disarmed. PX4 only executes a reposition "
                "while armed; take off first.",
            )

        lat, lon = _offset_to_global(home.lat, home.lon, north, east)
        if alt is None:
            here = self._current_position()
            if here is None:
                return NavigationResult(
                    success=False,
                    reason=f"no_position: no GLOBAL_POSITION_INT within {self._config.message_timeout_seconds:.0f}s",
                )
            target_alt = _relative_alt_m(here)
            z = math.nan  # PX4 keeps the current altitude
        else:
            target_alt = float(alt)
            z = home.alt_amsl + target_alt

        # DO_REPOSITION: param1 ground speed (-1 = PX4 default), param2
        # MAV_DO_REPOSITION_FLAGS_CHANGE_MODE (PX4 answers UNSUPPORTED
        # without it), param4 yaw (NaN = keep heading).
        ground_speed = float(speed) if speed is not None and speed > 0 else -1.0
        ok, reason = self._send_command_int(
            MAV_CMD_DO_REPOSITION,
            MAV_FRAME_GLOBAL,
            (ground_speed, float(MAV_DO_REPOSITION_FLAGS_CHANGE_MODE), 0.0, math.nan),
            _deg_e7(lat),
            _deg_e7(lon),
            z,
        )
        if not ok:
            return NavigationResult(success=False, reason=f"reposition_rejected: {reason}")

        radius = self._config.arrival_radius_m
        alt_tolerance = self._config.arrival_alt_tolerance_m
        arrived = self._await(
            "GLOBAL_POSITION_INT",
            lambda m: _distance_to(m, lat, lon) <= radius and abs(_relative_alt_m(m) - target_alt) <= alt_tolerance,
            self._config.arrival_timeout_seconds,
        )
        if arrived is None:
            last = self._global_position
            where = (
                f"{_distance_to(last, lat, lon):.1f} m from the target at {_relative_alt_m(last):.1f} m altitude"
                if last is not None
                else "position unknown"
            )
            return NavigationResult(
                success=False,
                reason=f"arrival_timeout: {where} after {self._config.arrival_timeout_seconds:.0f}s",
            )
        return NavigationResult(
            success=True,
            final_pose={"x": north, "y": east, "z": target_alt},
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
    # Hover: the executor dispatches hover through send_navigation_goal
    # (speed 0). Hover over a place flies there like move_to; PX4 then
    # holds position in Hold mode. Hover with no place is not mapped and
    # fails cleanly.
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
        camera: str | None = None,
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
        # PX4 holds position on its own in Hold mode, which is where
        # take_off and move_to leave the vehicle, so waiting is a plain
        # sleep. The next flight primitive drains the telemetry that
        # queued up meanwhile before it decides anything.
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
