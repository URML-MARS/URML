"""Unit tests for PX4Adapter — hermetic, no pymavlink install required.

The adapter imports pymavlink lazily. These tests install a fake
``pymavlink`` package into ``sys.modules`` before each test so:

  - The test file collects on every host (Linux, Windows, CI runners).
  - Every adapter code path is exercised against a controllable fake.
  - Real MAVLink behavior is verified separately under live integration
    tests (PX4 SITL: ``tests/integration/test_px4_sitl_e2e.py``).

The fake is a small scripted PX4 multicopter, not an ACK echo. It keeps
the state a flight primitive has to confirm (the armed bit, altitude
above home, position, landed state), moves when the adapter's commands
would move a real vehicle, and streams HEARTBEAT, GLOBAL_POSITION_INT,
EXTENDED_SYS_STATE and HOME_POSITION on a simulated clock. Class-level
knobs make it refuse, stall or never arrive, so every failure path is a
test: an ACK alone never produces a success. Like PX4 v1.17, it sends
STATUSTEXT only once it has seen a ground-station heartbeat, in
50-character chunks.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Callable, Iterator
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Fake pymavlink machinery
# ---------------------------------------------------------------------------

HOME_LAT = 47.397742
HOME_LON = 8.545594
HOME_ALT = 488.0  # metres AMSL
EARTH_RADIUS_M = 6_371_000.0

PX4_SYSID = 1
PX4_COMPID = 1

DT = 0.05  # simulated seconds per blocking read

ON_GROUND, IN_AIR, TAKEOFF, LANDING = 1, 2, 3, 4


class _Msg(SimpleNamespace):
    """A MAVLink message stand-in with ``get_type()`` and a source."""

    def __init__(self, mtype: str, *, src: tuple[int, int] = (PX4_SYSID, PX4_COMPID), **fields: Any) -> None:
        super().__init__(**fields)
        self._mtype = mtype
        self._src = src

    def get_type(self) -> str:
        return self._mtype

    def get_srcSystem(self) -> int:  # noqa: N802 (pymavlink API name)
        return self._src[0]

    def get_srcComponent(self) -> int:  # noqa: N802 (pymavlink API name)
        return self._src[1]


class _SimClock:
    """Stands in for the adapter module's ``time``; reads advance it."""

    def __init__(self) -> None:
        self.now = 1000.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += max(0.0, seconds)


_CLOCK = _SimClock()


def _north_east(lat: float, lon: float) -> tuple[float, float]:
    north = math.radians(lat - HOME_LAT) * EARTH_RADIUS_M
    east = math.radians(lon - HOME_LON) * EARTH_RADIUS_M * math.cos(math.radians(HOME_LAT))
    return north, east


def _lat_lon(north: float, east: float) -> tuple[float, float]:
    lat = HOME_LAT + math.degrees(north / EARTH_RADIUS_M)
    lon = HOME_LON + math.degrees(east / (EARTH_RADIUS_M * math.cos(math.radians(HOME_LAT))))
    return lat, lon


class _FakeMavLink:
    """Stand-in for the `mav` attribute of a pymavlink connection.

    Records every command so tests can assert on ids and parameters, and
    hands commands to the simulated vehicle. ``sent`` is the order of all
    sends; ``lock_states`` records, per send, what ``_FakePX4.lock_probe``
    said (whether the adapter's send lock was held).
    """

    def __init__(self, px4: _FakePX4) -> None:
        self._px4 = px4
        self.command_long_calls: list[dict[str, Any]] = []
        self.command_int_calls: list[dict[str, Any]] = []
        self.set_position_target_calls: list[dict[str, Any]] = []
        self.statustext_calls: list[dict[str, Any]] = []
        self.heartbeat_calls: list[dict[str, Any]] = []
        self.sent: list[str] = []
        self.lock_states: list[bool] = []

    def _record(self, kind: str) -> None:
        self.sent.append(kind)
        probe = _FakePX4.lock_probe
        if probe is not None:
            self.lock_states.append(probe())

    def heartbeat_send(
        self,
        type: int,  # pymavlink's keyword
        autopilot: int,
        base_mode: int,
        custom_mode: int,
        system_status: int,
        mavlink_version: int = 3,
    ) -> None:
        self._record("HEARTBEAT")
        self.heartbeat_calls.append(
            {
                "type": type,
                "autopilot": autopilot,
                "base_mode": base_mode,
                "custom_mode": custom_mode,
                "system_status": system_status,
            }
        )
        self._px4.on_heartbeat(type)

    def command_long_send(
        self,
        target_system: int,
        target_component: int,
        command: int,
        confirmation: int,
        *params: float,
    ) -> None:
        self._record("COMMAND_LONG")
        self.command_long_calls.append(
            {"target": (target_system, target_component), "command": command, "params": tuple(params)}
        )
        self._px4.on_command(command, tuple(params))

    def command_int_send(
        self,
        target_system: int,
        target_component: int,
        frame: int,
        command: int,
        current: int,
        autocontinue: int,
        p1: float,
        p2: float,
        p3: float,
        p4: float,
        x: int,
        y: int,
        z: float,
    ) -> None:
        self._record("COMMAND_INT")
        self.command_int_calls.append(
            {
                "target": (target_system, target_component),
                "frame": frame,
                "command": command,
                "params": (p1, p2, p3, p4),
                "x": x,
                "y": y,
                "z": z,
            }
        )
        self._px4.on_command_int(command, (p1, p2, p3, p4), x, y, z)

    def set_position_target_local_ned_send(self, *args: Any) -> None:
        self.set_position_target_calls.append({"args": args})

    def statustext_send(self, severity: int, text: bytes) -> None:
        self._record("STATUSTEXT")
        self.statustext_calls.append({"severity": severity, "text": text})


class _FakePX4:
    """Scripted PX4 multicopter behind a fake pymavlink connection.

    The vehicle streams one telemetry message per ``DT`` of simulated
    time and moves by ``DT`` of flight per message. Like a UDP socket, the
    link holds everything streamed while nobody read it: a non-blocking
    read replays that backlog (the flight included) up to the current
    clock, a blocking read that has caught up waits ``DT`` for the next
    message.

    Class-level knobs (reset per test by the fixture):
      - ``ack``: {command_id: MAV_RESULT}; missing -> accepted (0);
        ``-1`` -> never acked.
      - ``stray_ack``: every command is preceded on the link by an
        ACCEPTED ack for a different command.
      - ``arm_sticks``: an accepted arm sets the armed bit.
      - ``climb_rate`` / ``cruise_speed`` / ``descent_rate``: m/s; 0 means
        the vehicle never climbs / never moves / never descends.
      - ``rtl_lands``: PX4's RTL descends and lands after reaching home.
      - ``home_known``: HOME_POSITION is streamed.
      - ``home_shift_on_arm``: metres PX4's home altitude moves when it
        arms (PX4 re-sets home to the vehicle's estimate at arming).
      - ``autopilot``: MAV_AUTOPILOT of the vehicle heartbeat.
      - ``gcs_heartbeat_first``: a ground station's heartbeat arrives
        before the autopilot's, and ground-station heartbeats keep
        arriving in the stream.
      - ``start_armed_in_air``: the vehicle starts armed at 30 m, 15 m north.
      - ``queued``: messages delivered first for a matching type
        (measurement / wait tests).
      - ``statustext``: {command_id: [(severity, text), ...]}: what PX4
        says after its ack of that command (sent only once a
        ground-station heartbeat has arrived, as PX4 does).
      - ``emergency_at`` / ``emergency_state``: from this simulated time
        on, the vehicle HEARTBEAT reports ``system_status`` =
        ``emergency_state`` (8 = MAV_STATE_FLIGHT_TERMINATION).
      - ``lock_probe``: called on every send; its answers land in
        ``mav.lock_states``.
    """

    ack: dict[int, int] = {}  # noqa: RUF012
    stray_ack: bool = False
    arm_sticks: bool = True
    climb_rate: float = 3.0
    cruise_speed: float = 5.0
    descent_rate: float = 1.5
    rtl_lands: bool = True
    home_known: bool = True
    home_shift_on_arm: float = 0.0
    autopilot: int = 12
    heartbeat_answers: bool = True
    gcs_heartbeat_first: bool = False
    start_armed_in_air: bool = False
    queued: list[Any] = []  # noqa: RUF012
    statustext: dict[int, list[tuple[int, str]]] = {}  # noqa: RUF012
    emergency_at: float | None = None
    emergency_state: int = 8
    lock_probe: Callable[[], bool] | None = None

    def __init__(self, url: str, *_: Any, **kwargs: Any) -> None:
        self.url = url
        self.kwargs = kwargs
        self.target_system = PX4_SYSID
        self.target_component = PX4_COMPID
        self.mav = _FakeMavLink(self)
        self.heartbeat_waits = 0
        self._closed = False
        self.armed = False
        self.north = 0.0
        self.east = 0.0
        self.up = 0.0
        self.home_alt = HOME_ALT
        self.mode = "hold"
        self.goal: tuple[float, float, float] | None = None
        self.touchdown_at: float | None = None
        self.max_up = 0.0
        self.pending: list[_Msg] = []
        self.t_emit = _CLOCK.now  # simulated time the link has streamed up to
        self._cycle = 0
        self._gcs_sent = False
        self.gcs_heartbeats = 0  # MAV_TYPE_GCS heartbeats received from the adapter
        self._text_id = 0
        if _FakePX4.start_armed_in_air:
            self.armed = True
            self.up = 30.0
            self.north = 15.0
            self.goal = (15.0, 0.0, 30.0)
            self.max_up = 30.0

    # -- pymavlink surface ------------------------------------------------

    def wait_heartbeat(self, *, timeout: float = 5.0) -> Any:
        self.heartbeat_waits += 1
        if not _FakePX4.heartbeat_answers:
            _CLOCK.sleep(timeout)
            return None
        if _FakePX4.gcs_heartbeat_first and not self._gcs_sent:
            self._gcs_sent = True
            return self._gcs_heartbeat()
        return self._telemetry("HEARTBEAT")

    def recv_match(
        self,
        *,
        type: Any = None,  # pymavlink's keyword
        blocking: bool = False,
        timeout: float | None = None,
    ) -> Any:
        wanted = None if type is None else ({type} if isinstance(type, str) else set(type))
        # Queued test messages behave like data already on the socket.
        while _FakePX4.queued:
            msg = _FakePX4.queued.pop(0)
            if msg is None:
                _CLOCK.sleep(timeout or 0.0)
                return None
            if isinstance(msg, dict):
                if wanted is None or msg["type"] in wanted:
                    return msg["msg"]
                continue
            if wanted is None or msg.get_type() in wanted:
                return msg
        # Like a socket, a read consumes what it skips.
        while self.pending:
            msg = self.pending.pop(0)
            if wanted is None or msg.get_type() in wanted:
                return msg
        kinds = self._streamed(wanted)
        if not kinds:  # nothing this vehicle streams matches: the read times out
            if blocking:
                _CLOCK.sleep(timeout or 0.0)
            return None
        if self.t_emit + DT > _CLOCK.now + 1e-9:  # caught up with the clock
            if not blocking:
                return None
            _CLOCK.sleep(DT)
        self.t_emit += DT
        self._step(DT)
        kind = kinds[self._cycle % len(kinds)]
        self._cycle += 1
        if kind == "GCS_HEARTBEAT":
            return self._gcs_heartbeat()
        return self._telemetry(kind)

    def close(self) -> None:
        self._closed = True

    # -- vehicle ----------------------------------------------------------

    def _streamed(self, wanted: set[str] | None) -> list[str]:
        kinds = ["GLOBAL_POSITION_INT", "EXTENDED_SYS_STATE", "HEARTBEAT"]
        if _FakePX4.home_known:
            kinds.append("HOME_POSITION")
        if _FakePX4.gcs_heartbeat_first:
            kinds.append("GCS_HEARTBEAT")
        return [k for k in kinds if wanted is None or (k if k != "GCS_HEARTBEAT" else "HEARTBEAT") in wanted]

    def on_heartbeat(self, mav_type: int) -> None:
        if mav_type == 6:  # MAV_TYPE_GCS
            self.gcs_heartbeats += 1

    def _say(self, severity: int, text: str) -> None:
        """STATUSTEXT as PX4 v1.17 sends it: only to a link with a ground-station
        heartbeat, split into 50-character chunks that share an id."""
        if not self.gcs_heartbeats:
            return
        self._text_id += 1
        chunks = [text[i : i + 50] for i in range(0, len(text), 50)]
        for seq, chunk in enumerate(chunks):
            self.pending.append(_Msg("STATUSTEXT", severity=severity, text=chunk, id=self._text_id, chunk_seq=seq))

    def _ack(self, command: int, result: int) -> None:
        if result >= 0:
            self.pending.append(_Msg("COMMAND_ACK", command=command, result=result))
        # PX4 publishes its explanation on its own 20 Hz stream, so on the
        # wire it can trail the ack.
        for severity, text in _FakePX4.statustext.get(command, []):
            self._say(severity, text)

    def on_command(self, command: int, params: tuple[float, ...]) -> None:
        if _FakePX4.stray_ack:
            self.pending.append(_Msg("COMMAND_ACK", command=command + 1, result=0))
        result = _FakePX4.ack.get(command, 0)
        if command == 512:  # REQUEST_MESSAGE
            self._ack(command, result)
            if int(params[0]) == 242 and _FakePX4.home_known:
                self.pending.append(self._telemetry("HOME_POSITION"))
            return
        if result == 0:
            if command == 400:  # ARM_DISARM
                if params[0] == 1.0 and _FakePX4.arm_sticks:
                    self.armed = True
                    self.home_alt += _FakePX4.home_shift_on_arm
                elif params[0] == 0.0 and self.up <= 0.05:
                    self.armed = False
            elif command == 22:  # NAV_TAKEOFF, param7 AMSL
                self.mode = "takeoff"
                self.goal = (self.north, self.east, params[6] - self.home_alt)
            elif command == 20:  # RTL
                self.mode = "rtl"
                self.goal = (0.0, 0.0, self.up)
            elif command == 21:  # LAND
                self.mode = "land"
                self.goal = (self.north, self.east, 0.0)
        self._ack(command, result)

    def on_command_int(self, command: int, params: tuple[float, ...], x: int, y: int, z: float) -> None:
        result = _FakePX4.ack.get(command, 0)
        if command == 192 and result == 0 and int(params[1]) != 1:
            result = 3  # PX4 v1.17: UNSUPPORTED without the change-mode flag
        if command == 192 and result == 0 and self.armed:
            north, east = _north_east(x / 1e7, y / 1e7)
            up = self.up if math.isnan(z) else z - self.home_alt
            self.mode = "hold"
            self.goal = (north, east, up)
        self._ack(command, result)

    def _step(self, dt: float) -> None:
        if self.touchdown_at is not None and self.armed and self.t_emit - self.touchdown_at >= 2.0:
            self.armed = False  # PX4 disarms after landing (COM_DISARM_LAND)
        if not self.armed or self.goal is None:
            return
        goal_n, goal_e, goal_up = self.goal
        if self.mode == "takeoff":
            if self.climb_rate > 0:
                self.up = min(goal_up, self.up + self.climb_rate * dt)
            if self.up >= goal_up:
                self.mode = "hold"  # PX4 switches to Hold when the take-off completes
        elif self.mode in ("hold", "rtl"):
            dn, de = goal_n - self.north, goal_e - self.east
            dist = math.hypot(dn, de)
            step = self.cruise_speed * dt
            if dist <= step:
                self.north, self.east = goal_n, goal_e
                if self.mode == "rtl" and self.rtl_lands:
                    self.mode = "land"
                    self.goal = (goal_n, goal_e, 0.0)
            elif step > 0:
                self.north += dn / dist * step
                self.east += de / dist * step
            if self.mode == "hold":
                rate = self.climb_rate if goal_up > self.up else self.descent_rate
                delta = goal_up - self.up
                self.up += max(-rate * dt, min(rate * dt, delta))
        elif self.mode == "land" and self.descent_rate > 0:
            self.up = max(0.0, self.up - self.descent_rate * dt)
            if self.up == 0.0 and self.touchdown_at is None:
                self.touchdown_at = self.t_emit
        self.max_up = max(self.max_up, self.up)

    def landed_state(self) -> int:
        if self.up <= 0.05:
            return ON_GROUND
        if self.mode == "land":
            return LANDING
        if self.mode == "takeoff":
            return TAKEOFF
        return IN_AIR

    def _gcs_heartbeat(self) -> _Msg:
        return _Msg("HEARTBEAT", src=(255, 190), type=6, autopilot=8, base_mode=0, custom_mode=0)

    def _telemetry(self, kind: str) -> _Msg:
        if kind == "HEARTBEAT":
            emergency = _FakePX4.emergency_at is not None and self.t_emit >= _FakePX4.emergency_at
            return _Msg(
                "HEARTBEAT",
                type=2,
                autopilot=_FakePX4.autopilot,
                base_mode=(128 if self.armed else 0) | 29,
                custom_mode=0,
                system_status=_FakePX4.emergency_state if emergency else (4 if self.armed else 3),
            )
        if kind == "GLOBAL_POSITION_INT":
            lat, lon = _lat_lon(self.north, self.east)
            return _Msg(
                "GLOBAL_POSITION_INT",
                lat=round(lat * 1e7),
                lon=round(lon * 1e7),
                alt=round((self.home_alt + self.up) * 1000),
                relative_alt=round(self.up * 1000),
            )
        if kind == "EXTENDED_SYS_STATE":
            return _Msg("EXTENDED_SYS_STATE", vtol_state=0, landed_state=self.landed_state())
        if kind == "HOME_POSITION":
            return _Msg(
                "HOME_POSITION",
                latitude=round(HOME_LAT * 1e7),
                longitude=round(HOME_LON * 1e7),
                altitude=round(self.home_alt * 1000),
            )
        raise AssertionError(kind)


def _make_fake_module(name: str, **attrs: Any) -> ModuleType:
    mod = ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


def _install_fake_pymavlink(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Install fake pymavlink into sys.modules; return shared state."""
    _FakePX4.ack = {}
    _FakePX4.stray_ack = False
    _FakePX4.arm_sticks = True
    _FakePX4.climb_rate = 3.0
    _FakePX4.cruise_speed = 5.0
    _FakePX4.descent_rate = 1.5
    _FakePX4.rtl_lands = True
    _FakePX4.home_known = True
    _FakePX4.home_shift_on_arm = 0.0
    _FakePX4.autopilot = 12
    _FakePX4.heartbeat_answers = True
    _FakePX4.gcs_heartbeat_first = False
    _FakePX4.start_armed_in_air = False
    _FakePX4.queued = []
    _FakePX4.statustext = {}
    _FakePX4.emergency_at = None
    _FakePX4.emergency_state = 8
    _FakePX4.lock_probe = None
    _CLOCK.now = 1000.0

    captured: dict[str, Any] = {"connections": []}

    def _mavlink_connection(url: str, *args: Any, **kwargs: Any) -> _FakePX4:
        conn = _FakePX4(url, *args, **kwargs)
        captured["connections"].append(conn)
        return conn

    mavutil = _make_fake_module(
        "pymavlink.mavutil",
        mavlink_connection=_mavlink_connection,
    )
    pymavlink = _make_fake_module("pymavlink", mavutil=mavutil)

    monkeypatch.setitem(sys.modules, "pymavlink", pymavlink)
    monkeypatch.setitem(sys.modules, "pymavlink.mavutil", mavutil)
    # The adapter's deadlines read the simulated clock, not the wall clock.
    monkeypatch.setattr("urml_px4_runtime.adapter.time", _CLOCK)
    return captured


@pytest.fixture
def fake_pymavlink(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    yield _install_fake_pymavlink(monkeypatch)


def _vehicle(fake: dict[str, Any]) -> _FakePX4:
    conn: _FakePX4 = fake["connections"][0]
    return conn


def _long_commands(fake: dict[str, Any]) -> list[int]:
    return [c["command"] for c in _vehicle(fake).mav.command_long_calls if c["command"] != 512]


def _cfg(**kwargs: Any) -> Any:
    from urml_px4_runtime import PX4AdapterConfig
    from urml_px4_runtime.config import NEDPosition

    base: dict[str, Any] = {
        "location_to_pose": {
            "roof_north": NEDPosition(north=15.0, east=0.0, alt=30.0),
            "pad_east": NEDPosition(north=0.0, east=12.0, alt=10.0),
        }
    }
    base.update(kwargs)
    return PX4AdapterConfig(**base)


def _airborne(fake: dict[str, Any], **cfg: Any) -> Any:
    """An adapter whose vehicle has already taken off to 30 m."""
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter(_cfg(**cfg))
    assert adapter.send_takeoff_goal(altitude=30.0).success
    return adapter


# ---------------------------------------------------------------------------
# Module-import tests
# ---------------------------------------------------------------------------


def test_module_imports_without_pymavlink() -> None:
    """The adapter module must be importable on every host."""
    from urml_px4_runtime import adapter

    assert adapter.PX4Adapter is not None


def test_constructor_raises_clear_error_when_pymavlink_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without pymavlink installed, the constructor surfaces an install hint."""
    for name in list(sys.modules):
        if name == "pymavlink" or name.startswith("pymavlink."):
            monkeypatch.delitem(sys.modules, name, raising=False)
    monkeypatch.setitem(sys.modules, "pymavlink", None)  # type: ignore[arg-type]

    from urml_px4_runtime import PX4Adapter

    with pytest.raises(RuntimeError) as excinfo:
        PX4Adapter()
    assert "pymavlink is not installed" in str(excinfo.value)
    assert "[px4]" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Construction + lifecycle
# ---------------------------------------------------------------------------


def test_constructor_does_not_connect_eagerly(fake_pymavlink: dict[str, Any]) -> None:
    """Construction must NOT open the MAVLink connection — that happens lazily."""
    from urml_px4_runtime import PX4Adapter

    PX4Adapter()
    assert fake_pymavlink["connections"] == []


def test_close_without_connect_is_a_noop(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    adapter.close()  # no error even though connect was never called


def test_context_manager_closes(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    with PX4Adapter() as adapter:
        adapter.send_takeoff_goal(altitude=30.0)
    assert fake_pymavlink["connections"][0]._closed is True


def test_no_heartbeat_is_a_connection_failure(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.heartbeat_answers = False
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert (result.reason or "").startswith("connection_failed: heartbeat_timeout")
    assert _vehicle(fake_pymavlink).mav.command_long_calls == []


def test_non_px4_autopilot_is_refused(fake_pymavlink: dict[str, Any]) -> None:
    """ArduPilot reads NAV_TAKEOFF param7 as relative; never send it PX4's AMSL."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.autopilot = 3  # MAV_AUTOPILOT_ARDUPILOTMEGA
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert "not_a_px4_autopilot" in (result.reason or "")
    assert _vehicle(fake_pymavlink).mav.command_long_calls == []
    assert _vehicle(fake_pymavlink).mav.heartbeat_calls == []  # no ground-station heartbeat either


def test_ground_station_heartbeat_is_not_the_vehicle(fake_pymavlink: dict[str, Any]) -> None:
    """A GCS heartbeat (disarmed, autopilot INVALID) must not stand in for PX4's."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.gcs_heartbeat_first = True
    adapter = PX4Adapter()
    result = adapter.send_takeoff_goal(altitude=10.0)
    assert result.success is True, result.reason
    assert _long_commands(fake_pymavlink) == [400, 22]
    assert {c["target"] for c in _vehicle(fake_pymavlink).mav.command_long_calls} == {(PX4_SYSID, PX4_COMPID)}
    # Ground-station heartbeats kept arriving; the vehicle is still seen as armed.
    assert adapter._is_armed() is True


# ---------------------------------------------------------------------------
# Ground-station heartbeat
# ---------------------------------------------------------------------------


def _real_wait_until(predicate: Callable[[], bool], timeout_s: float = 5.0) -> bool:
    """Poll in real time (the heartbeat thread runs on the wall clock, not the simulated one)."""
    import time as real_time

    deadline = real_time.monotonic() + timeout_s
    while real_time.monotonic() < deadline:
        if predicate():
            return True
        real_time.sleep(0.01)
    return predicate()


def test_gcs_heartbeat_goes_out_before_the_first_command(fake_pymavlink: dict[str, Any]) -> None:
    """PX4 sends STATUSTEXT only to a link with a ground-station heartbeat, so announce one first."""
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    assert adapter.send_takeoff_goal(altitude=10.0).success is True
    mav = _vehicle(fake_pymavlink).mav
    assert mav.sent[0] == "HEARTBEAT"
    assert mav.heartbeat_calls[0] == {
        "type": 6,  # MAV_TYPE_GCS
        "autopilot": 8,  # MAV_AUTOPILOT_INVALID
        "base_mode": 0,
        "custom_mode": 0,
        "system_status": 4,  # MAV_STATE_ACTIVE
    }
    adapter.close()


def test_gcs_heartbeat_period_is_one_second(fake_pymavlink: dict[str, Any]) -> None:
    import time as real_time

    import urml_px4_runtime.adapter as adapter_module
    from urml_px4_runtime import PX4Adapter

    assert adapter_module.GCS_HEARTBEAT_PERIOD_SECONDS == 1.0
    adapter = PX4Adapter()
    adapter._connect()
    real_time.sleep(0.3)  # well inside the first 1 s period: only the heartbeat sent on connect
    assert len(_vehicle(fake_pymavlink).mav.heartbeat_calls) == 1
    adapter.close()


def test_gcs_heartbeat_repeats_from_a_daemon_thread_and_stops_on_close(
    fake_pymavlink: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    import time as real_time

    import urml_px4_runtime.adapter as adapter_module
    from urml_px4_runtime import PX4Adapter

    monkeypatch.setattr(adapter_module, "GCS_HEARTBEAT_PERIOD_SECONDS", 0.01)
    adapter = PX4Adapter()
    adapter._connect()
    thread = adapter._gcs_thread
    assert thread is not None and thread.daemon and thread.is_alive()
    mav = _vehicle(fake_pymavlink).mav
    assert _real_wait_until(lambda: len(mav.heartbeat_calls) >= 5)
    assert {c["type"] for c in mav.heartbeat_calls} == {6}

    adapter.close()
    assert not thread.is_alive()
    assert adapter._gcs_thread is None
    sent = len(mav.heartbeat_calls)
    real_time.sleep(0.1)  # ten periods
    assert len(mav.heartbeat_calls) == sent
    assert _vehicle(fake_pymavlink)._closed is True


def test_a_closed_adapter_does_not_reconnect(fake_pymavlink: dict[str, Any]) -> None:
    """After close() nothing may restart the heartbeat, or PX4 would still see a ground station."""
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    adapter._connect()
    adapter.close()
    result = adapter.send_takeoff_goal(altitude=10.0)
    assert result.success is False
    assert (result.reason or "").startswith("connection_failed: adapter_closed")
    assert len(fake_pymavlink["connections"]) == 1
    assert adapter._gcs_thread is None


def test_every_send_holds_the_send_lock(
    fake_pymavlink: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    """The heartbeat thread and the caller both send; pymavlink sends are not thread-safe."""
    import urml_px4_runtime.adapter as adapter_module
    from urml_px4_runtime import PX4Adapter

    monkeypatch.setattr(adapter_module, "GCS_HEARTBEAT_PERIOD_SECONDS", 0.001)
    adapter = PX4Adapter(_cfg())
    _FakePX4.lock_probe = adapter._send_lock.locked
    assert adapter.send_takeoff_goal(altitude=10.0).success is True
    assert adapter.send_navigation_goal(location="pad_east").success is True
    assert adapter.emit_report(to="user", facts={}, attachments=None, status="success", severity="info").success
    adapter.close()
    mav = _vehicle(fake_pymavlink).mav
    assert {"HEARTBEAT", "COMMAND_LONG", "COMMAND_INT", "STATUSTEXT"} <= set(mav.sent)
    assert len(mav.lock_states) == len(mav.sent)
    assert all(mav.lock_states)


# ---------------------------------------------------------------------------
# take_off
# ---------------------------------------------------------------------------


def test_takeoff_arms_climbs_and_confirms_altitude(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.send_takeoff_goal(altitude=30.0)
    assert result.success is True, result.reason
    assert result.frame == "agl"
    assert result.final_pose is not None and result.final_pose["z"] >= 29.0
    vehicle = _vehicle(fake_pymavlink)
    assert vehicle.armed is True
    assert vehicle.up >= 29.0
    assert _long_commands(fake_pymavlink) == [400, 22]  # arm, then take off
    arm = next(c for c in vehicle.mav.command_long_calls if c["command"] == 400)
    assert arm["params"][0] == 1.0
    assert arm["params"][1] == 0.0  # never the force-arm magic number


def test_takeoff_altitude_is_amsl_from_home(fake_pymavlink: dict[str, Any]) -> None:
    """PX4 reads NAV_TAKEOFF param7 as AMSL; lat / lon / yaw are NaN (keep current)."""
    from urml_px4_runtime import PX4Adapter

    PX4Adapter().send_takeoff_goal(altitude=30.0)
    takeoff = next(c for c in _vehicle(fake_pymavlink).mav.command_long_calls if c["command"] == 22)
    params = takeoff["params"]
    assert params[6] == pytest.approx(HOME_ALT + 30.0)
    assert math.isnan(params[3]) and math.isnan(params[4]) and math.isnan(params[5])


def test_takeoff_aims_from_the_home_px4_sets_at_arming(fake_pymavlink: dict[str, Any]) -> None:
    """PX4 re-sets home when it arms; a pre-arm home would aim 1.4 m low and never arrive."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.home_shift_on_arm = 1.4
    result = PX4Adapter(_cfg(takeoff_timeout_seconds=60.0)).send_takeoff_goal(altitude=30.0)
    assert result.success is True, result.reason
    takeoff = next(c for c in _vehicle(fake_pymavlink).mav.command_long_calls if c["command"] == 22)
    assert takeoff["params"][6] == pytest.approx(HOME_ALT + 1.4 + 30.0)


def test_takeoff_requests_home_when_not_streamed(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.home_known = False
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert (result.reason or "").startswith("home_unknown")
    calls = _vehicle(fake_pymavlink).mav.command_long_calls
    assert [c["command"] for c in calls] == [512]  # asked for HOME_POSITION, never armed
    assert calls[0]["params"][0] == 242.0


def test_takeoff_skips_arming_when_already_armed(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.start_armed_in_air = True
    result = PX4Adapter().send_takeoff_goal(altitude=40.0)
    assert result.success is True
    assert _long_commands(fake_pymavlink) == [22]


def test_takeoff_arm_rejected(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.ack = {400: 1}  # TEMPORARILY_REJECTED
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == "arm_rejected: mav_result_temporarily_rejected"
    assert 22 not in _long_commands(fake_pymavlink)  # no take-off after a refused arm
    assert _vehicle(fake_pymavlink).up == 0.0


def test_arm_refusal_reason_quotes_px4_statustext(fake_pymavlink: dict[str, Any]) -> None:
    """PX4 v1.17 explains a refused arm in STATUSTEXT, and only to a link with a ground station.

    Both are PX4 v1.17's own texts for an arm refused by COM_ARMABLE = 0.
    The first is exactly 50 characters (one chunk, no terminator); the
    second is 52, so PX4 splits it in two. Here both arrive after the ack;
    in SITL PX4 sent the first when the parameter changed, before the arm,
    and the reason then carried only the second.
    """
    from urml_px4_runtime import PX4Adapter

    _FakePX4.ack = {400: 1}  # TEMPORARILY_REJECTED
    _FakePX4.statustext = {
        400: [
            (2, "Preflight Fail: Vehicle is in safety configuration"),
            (2, "Arming denied: Resolve system health failures first\t"),
        ]
    }
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == (
        "arm_rejected: mav_result_temporarily_rejected; PX4 said: "
        '"Preflight Fail: Vehicle is in safety configuration"; '
        '"Arming denied: Resolve system health failures first"'
    )
    assert 22 not in _long_commands(fake_pymavlink)


def test_reason_leaves_out_warnings_from_before_the_command(fake_pymavlink: dict[str, Any]) -> None:
    """A warning already on the link may no longer hold, so only what PX4 says from the command on counts.

    This is what PX4 v1.17 SITL did with COM_ARMABLE = 0: it sent the
    50-character "Preflight Fail" text (one chunk, no terminator, so the
    adapter holds it open until the next text) when the parameter changed,
    and only "Arming denied" in reply to the arm. The held-open text keeps
    its place in the read order from before the command.
    """
    from urml_px4_runtime import PX4Adapter

    _FakePX4.queued = [
        _Msg("STATUSTEXT", severity=2, text="an older warning", id=8, chunk_seq=0),
        _Msg("STATUSTEXT", severity=2, text="Preflight Fail: Vehicle is in safety configuration", id=9, chunk_seq=0),
    ]
    _FakePX4.ack = {400: 1}
    _FakePX4.statustext = {400: [(2, "Arming denied: Resolve system health failures first\t")]}
    adapter = PX4Adapter()
    result = adapter.send_takeoff_goal(altitude=30.0)
    assert result.reason == (
        'arm_rejected: mav_result_temporarily_rejected; PX4 said: "Arming denied: Resolve system health failures first"'
    )
    kept = [entry.text for entry in adapter._statustext_log]
    assert kept[:2] == ["an older warning", "Preflight Fail: Vehicle is in safety configuration"]  # read, not quoted


def test_ack_timeout_reason_quotes_px4_statustext(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.ack = {22: -1}  # never acked
    _FakePX4.statustext = {22: [(3, "an error PX4 reported instead of an ack")]}
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == 'takeoff_rejected: ack_timeout; PX4 said: "an error PX4 reported instead of an ack"'


def test_timeout_reason_quotes_px4_warnings_not_its_narration(fake_pymavlink: dict[str, Any]) -> None:
    """Only STATUSTEXT of severity WARNING or worse goes into a reason; PX4's INFO lines narrate."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.climb_rate = 0.0
    _FakePX4.statustext = {22: [(6, "an info line PX4 narrates"), (4, "a warning PX4 sent")]}
    result = PX4Adapter(_cfg(takeoff_timeout_seconds=5.0)).send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == (
        'takeoff_timeout: relative altitude 0.0 m after 5s, target 30.0 m; PX4 said: "a warning PX4 sent"'
    )


def test_takeoff_arm_accepted_but_never_armed(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.arm_sticks = False
    result = PX4Adapter(_cfg(arm_timeout_seconds=3.0)).send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert "armed flag not seen on HEARTBEAT" in (result.reason or "")
    assert 22 not in _long_commands(fake_pymavlink)


def test_takeoff_rejected_disarms_the_vehicle_it_armed(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.ack = {22: 4}  # FAILED
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == "takeoff_rejected: mav_result_failed"
    assert _long_commands(fake_pymavlink) == [400, 22, 400]
    assert _vehicle(fake_pymavlink).armed is False


def test_takeoff_timeout_when_the_vehicle_never_climbs(fake_pymavlink: dict[str, Any]) -> None:
    """Accepted and armed is not airborne: no climb, no success."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.climb_rate = 0.0
    result = PX4Adapter(_cfg(takeoff_timeout_seconds=20.0)).send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert (result.reason or "").startswith("takeoff_timeout: relative altitude 0.0 m after 20s")


def test_takeoff_ack_timeout(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.ack = {22: -1}  # no ack at all
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert (result.reason or "").startswith("takeoff_rejected: ack_timeout")


def test_ack_for_another_command_is_not_ours(fake_pymavlink: dict[str, Any]) -> None:
    """A stray ACCEPTED ack for a different command must not satisfy the arm wait."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.ack = {400: -1}
    _FakePX4.stray_ack = True
    result = PX4Adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert (result.reason or "").startswith("arm_rejected: ack_timeout")
    assert 22 not in _long_commands(fake_pymavlink)


def test_low_takeoff_still_has_to_leave_the_ground(fake_pymavlink: dict[str, Any]) -> None:
    """The tolerance is capped at half the target, so 1 m never passes on the ground."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.climb_rate = 0.0
    result = PX4Adapter(_cfg(arrival_alt_tolerance_m=5.0, takeoff_timeout_seconds=5.0)).send_takeoff_goal(
        altitude=1.0
    )
    assert result.success is False


def test_takeoff_rejects_non_positive_altitude(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    result = PX4Adapter().send_takeoff_goal(altitude=0.0)
    assert result.success is False
    assert (result.reason or "").startswith("invalid_altitude")
    assert fake_pymavlink["connections"] == []


# ---------------------------------------------------------------------------
# move_to
# ---------------------------------------------------------------------------


def test_move_to_location_repositions_and_confirms_arrival(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    result = adapter.send_navigation_goal(location="roof_north")
    assert result.success is True, result.reason
    assert result.final_pose == {"x": 15.0, "y": 0.0, "z": 30.0}
    vehicle = _vehicle(fake_pymavlink)
    assert vehicle.north == pytest.approx(15.0, abs=1.5)
    assert vehicle.up == pytest.approx(30.0, abs=1.0)
    # The fire-and-forget offboard setpoint is gone.
    assert vehicle.mav.set_position_target_calls == []


def test_move_to_sends_do_reposition_as_command_int(fake_pymavlink: dict[str, Any]) -> None:
    """COMMAND_INT carries lat / lon as degE7 integers; z is AMSL; PX4 needs the mode flag."""
    from urml_px4_runtime.adapter import _offset_to_global

    adapter = _airborne(fake_pymavlink)
    adapter.send_navigation_goal(location="pad_east", speed=3.0)
    (call,) = _vehicle(fake_pymavlink).mav.command_int_calls
    assert call["command"] == 192
    assert call["frame"] == 0  # MAV_FRAME_GLOBAL: altitude AMSL
    assert call["target"] == (PX4_SYSID, PX4_COMPID)
    lat, lon = _offset_to_global(HOME_LAT, HOME_LON, 0.0, 12.0)
    assert isinstance(call["x"], int) and isinstance(call["y"], int)
    assert call["x"] == round(lat * 1e7)
    assert call["y"] == round(lon * 1e7)
    assert call["z"] == pytest.approx(HOME_ALT + 10.0)
    speed, flags, _, yaw = call["params"]
    assert speed == 3.0
    assert flags == 1.0  # MAV_DO_REPOSITION_FLAGS_CHANGE_MODE
    assert math.isnan(yaw)


def test_move_to_pose_uses_the_pose(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    result = adapter.send_navigation_goal(pose={"x": 5.0, "y": 3.0, "z": 20.0}, frame="agl")
    assert result.success is True, result.reason
    assert result.final_pose == {"x": 5.0, "y": 3.0, "z": 20.0}
    assert result.frame == "agl"
    vehicle = _vehicle(fake_pymavlink)
    assert (vehicle.north, vehicle.east) == (pytest.approx(5.0, abs=1.5), pytest.approx(3.0, abs=1.5))
    assert vehicle.up == pytest.approx(20.0, abs=1.0)


def test_move_to_pose_without_z_keeps_the_current_altitude(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    result = adapter.send_navigation_goal(pose={"x": 8.0, "y": 0.0})
    assert result.success is True, result.reason
    (call,) = _vehicle(fake_pymavlink).mav.command_int_calls
    assert math.isnan(call["z"])
    assert result.final_pose is not None and result.final_pose["z"] == pytest.approx(30.0, abs=1.0)


def test_move_to_that_never_arrives_is_a_failure(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink, arrival_timeout_seconds=15.0)
    _FakePX4.cruise_speed = 0.0
    result = adapter.send_navigation_goal(location="roof_north")
    assert result.success is False
    assert (result.reason or "").startswith("arrival_timeout: 15.0 m from the target at 30.0 m altitude after 15s")


def test_move_to_rejected_reposition(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    _FakePX4.ack = {192: 1}
    result = adapter.send_navigation_goal(location="roof_north")
    assert result.success is False
    assert result.reason == "reposition_rejected: mav_result_temporarily_rejected"


def test_move_to_while_disarmed_fails_without_commanding(fake_pymavlink: dict[str, Any]) -> None:
    """PX4 ignores DO_REPOSITION while disarmed; the adapter says so up front."""
    from urml_px4_runtime import PX4Adapter

    result = PX4Adapter(_cfg()).send_navigation_goal(location="roof_north")
    assert result.success is False
    assert (result.reason or "").startswith("not_airborne")
    assert _vehicle(fake_pymavlink).mav.command_int_calls == []


def test_send_navigation_goal_unmapped_location_returns_failure(
    fake_pymavlink: dict[str, Any],
) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.send_navigation_goal(location="unknown")
    assert result.success is False
    assert "location_not_configured" in (result.reason or "")


def test_send_navigation_goal_without_args_returns_failure(
    fake_pymavlink: dict[str, Any],
) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.send_navigation_goal()
    assert result.success is False
    assert "without location or pose" in (result.reason or "")


def test_offset_to_global_round_trips_with_haversine() -> None:
    from urml_px4_runtime.adapter import _haversine_m, _offset_to_global

    lat, lon = _offset_to_global(HOME_LAT, HOME_LON, 15.0, 0.0)
    assert lon == pytest.approx(HOME_LON)
    assert lat > HOME_LAT
    assert _haversine_m(HOME_LAT, HOME_LON, lat, lon) == pytest.approx(15.0, abs=1e-6)
    lat2, lon2 = _offset_to_global(HOME_LAT, HOME_LON, -30.0, 40.0)
    assert _haversine_m(HOME_LAT, HOME_LON, lat2, lon2) == pytest.approx(50.0, abs=1e-3)


# ---------------------------------------------------------------------------
# return_to_home
# ---------------------------------------------------------------------------


def test_return_to_home_waits_until_home(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    assert adapter.send_navigation_goal(location="roof_north").success
    vehicle = _vehicle(fake_pymavlink)
    assert vehicle.north == pytest.approx(15.0, abs=1.5)  # away from home before the RTL
    result = adapter.send_return_to_home_goal()
    assert result.success is True, result.reason
    assert math.hypot(vehicle.north, vehicle.east) <= 1.5
    assert vehicle.up > 20.0  # home reached in the air; PX4 lands on its own afterwards
    assert 20 in _long_commands(fake_pymavlink)


def test_return_to_home_that_never_arrives_is_a_failure(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink, arrival_timeout_seconds=10.0)
    assert adapter.send_navigation_goal(location="roof_north").success
    _FakePX4.cruise_speed = 0.0
    result = adapter.send_return_to_home_goal()
    assert result.success is False
    reason = result.reason or ""
    assert reason.startswith("rtl_timeout: 1")  # 13.5 to 15 m, wherever move_to called it arrived
    assert "m from home after 10s" in reason


def test_return_to_home_rejected(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    _FakePX4.ack = {20: 2}
    result = adapter.send_return_to_home_goal()
    assert result.success is False
    assert result.reason == "rtl_rejected: mav_result_denied"


def test_return_to_home_on_the_ground_at_home_says_so(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    result = PX4Adapter().send_return_to_home_goal()
    assert result.success is True
    assert (result.reason or "").startswith("already_at_home")
    assert _long_commands(fake_pymavlink) == []


def test_return_to_home_disarmed_away_from_home_fails(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    adapter._connect()
    _vehicle(fake_pymavlink).north = 20.0  # on the ground, disarmed, 20 m from home
    result = adapter.send_return_to_home_goal()
    assert result.success is False
    assert (result.reason or "").startswith("not_airborne")
    assert _long_commands(fake_pymavlink) == []


# ---------------------------------------------------------------------------
# land
# ---------------------------------------------------------------------------


def test_land_waits_for_on_ground(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    result = adapter.send_land_goal()
    assert result.success is True, result.reason
    vehicle = _vehicle(fake_pymavlink)
    assert vehicle.up == 0.0
    assert vehicle.landed_state() == ON_GROUND
    land = next(c for c in vehicle.mav.command_long_calls if c["command"] == 21)
    assert all(math.isnan(p) for p in land["params"][3:])  # land where it is


def test_land_on_the_ground_reports_it_without_commanding(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    result = PX4Adapter().send_land_goal()
    assert result.success is True
    assert (result.reason or "").startswith("already_on_ground")
    assert 21 not in _long_commands(fake_pymavlink)


def test_landing_timeout(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink, land_timeout_seconds=12.0)
    _FakePX4.descent_rate = 0.0
    result = adapter.send_land_goal()
    assert result.success is False
    assert (result.reason or "").startswith("landing_timeout: landed_state landing after 12s")


def test_land_rejected(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    _FakePX4.ack = {21: 1}
    result = adapter.send_land_goal()
    assert result.success is False
    assert (result.reason or "").startswith("land_rejected: mav_result_temporarily_rejected")


def test_land_at_flies_there_first(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    result = adapter.send_land_goal(at="pad_east")
    assert result.success is True, result.reason
    vehicle = _vehicle(fake_pymavlink)
    assert vehicle.east == pytest.approx(12.0, abs=1.5)
    assert vehicle.landed_state() == ON_GROUND


def test_land_at_unmapped_location(fake_pymavlink: dict[str, Any]) -> None:
    adapter = _airborne(fake_pymavlink)
    result = adapter.send_land_goal(at="nowhere")
    assert result.success is False
    assert "location_not_configured" in (result.reason or "")


def test_rtl_that_lands_by_itself_then_land_reports_on_ground(fake_pymavlink: dict[str, Any]) -> None:
    """PX4 RTL lands on its own; `land` afterwards sees ON_GROUND and sends nothing."""
    import urml_px4_runtime.adapter as adapter_module

    adapter = _airborne(fake_pymavlink)
    assert adapter.send_navigation_goal(location="roof_north").success
    assert adapter.send_return_to_home_goal().success
    adapter_module.time.sleep(60.0)  # PX4 finishes its RTL descent while nothing reads
    result = adapter.send_land_goal()
    assert result.success is True
    assert (result.reason or "").startswith("already_on_ground")
    assert 21 not in _long_commands(fake_pymavlink)


# ---------------------------------------------------------------------------
# The flight-only conformance program, end to end against the fake
# ---------------------------------------------------------------------------


def test_flight_only_program_flies_the_fake_vehicle(fake_pymavlink: dict[str, Any]) -> None:
    """take_off, move_to, return_to_home, land: every step confirmed by telemetry."""
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter(_cfg())
    steps = [
        adapter.send_takeoff_goal(altitude=30.0),
        adapter.send_navigation_goal(location="roof_north"),
        adapter.send_return_to_home_goal(),
        adapter.send_land_goal(),
    ]
    assert [s.success for s in steps] == [True, True, True, True], [s.reason for s in steps]
    vehicle = _vehicle(fake_pymavlink)
    assert vehicle.max_up >= 29.0
    assert vehicle.landed_state() == ON_GROUND


# ---------------------------------------------------------------------------
# Not-supported-on-bare-autopilot surface
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "call",
    [
        lambda a: a.send_docking_goal(station="dock", service="park"),
        lambda a: a.send_manipulation_goal(action="grasp"),
        lambda a: a.query_detection(object_class="mug"),
        lambda a: a.capture_media(media="photo", target=None, duration_seconds=None, attributes=None),
        lambda a: a.emit_speech(utterance="Hi", locale=None, style="conversational", interrupt=False),
        lambda a: a.acquire_speech(
            prompt=None, locale=None, timeout_seconds=1.0, expected="free_form", choices=None
        ),
    ],
)
def test_bare_autopilot_unsupported_primitives_return_clean_failure(
    fake_pymavlink: dict[str, Any], call: Any
) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = call(adapter)
    assert result.success is False
    assert "not_supported_on_bare_autopilot" in (result.reason or "")


# ---------------------------------------------------------------------------
# Measure
# ---------------------------------------------------------------------------


def test_measure_distance_reads_distance_sensor(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    # DISTANCE_SENSOR.current_distance is cm; 1500 cm = 15 m.
    _FakePX4.queued = [
        {"type": "DISTANCE_SENSOR", "msg": _Msg("DISTANCE_SENSOR", current_distance=1500, time_boot_ms=12000)}
    ]
    adapter = PX4Adapter()
    result = adapter.take_measurement(what="distance", target=None, sensor=None)
    assert result.success is True
    assert result.payload == {"value": 15.0, "unit": "m", "timestamp": 12.0}


def test_measure_voltage_reads_battery_status(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    # voltages[0] is mV; 12400 mV = 12.4 V.
    _FakePX4.queued = [
        {"type": "BATTERY_STATUS", "msg": _Msg("BATTERY_STATUS", voltages=[12400], time_boot_ms=5000)}
    ]
    adapter = PX4Adapter()
    result = adapter.take_measurement(what="voltage", target=None, sensor=None)
    assert result.success is True
    assert result.payload is not None
    assert result.payload["value"] == 12.4
    assert result.payload["unit"] == "V"


def test_measure_unsupported_kind_returns_failure(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.take_measurement(what="humidity", target=None, sensor=None)
    assert result.success is False
    assert "measurement_kind_not_supported" in (result.reason or "")


def test_measure_timeout(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.take_measurement(what="distance", target=None, sensor=None)
    assert result.success is False
    assert result.reason == "no_reading_within_timeout"


# ---------------------------------------------------------------------------
# Wait / report
# ---------------------------------------------------------------------------


def _battery(millivolts: int) -> dict[str, Any]:
    return {"type": "BATTERY_STATUS", "msg": _Msg("BATTERY_STATUS", voltages=[millivolts])}


def _wait_for_battery_below(adapter: Any, volts: float, timeout_seconds: float) -> Any:
    return adapter.wait_for_condition(
        kind="sensor_threshold",
        name=None,
        input_mode=None,
        threshold={"sensor": "battery", "op": "lt", "value": volts},
        timeout_seconds=timeout_seconds,
    )


def _wait_for_emergency_stop(adapter: Any, timeout_seconds: float) -> Any:
    return adapter.wait_for_condition(
        kind="event",
        name="emergency_stop",
        input_mode=None,
        threshold=None,
        timeout_seconds=timeout_seconds,
    )


def test_wait_for_battery_threshold(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.queued = [_battery(10000)]
    result = _wait_for_battery_below(PX4Adapter(), 11.0, timeout_seconds=1.0)
    assert result.success is True
    assert result.payload == {"sensor": "battery", "value": 10.0}


def test_wait_for_battery_threshold_reads_past_samples_that_do_not_match(fake_pymavlink: dict[str, Any]) -> None:
    """Regression: the wait gave up at the first BATTERY_STATUS that did not meet the threshold."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.queued = [_battery(12600), _battery(11600), _battery(10900)]
    result = _wait_for_battery_below(PX4Adapter(), 11.0, timeout_seconds=5.0)
    assert result.success is True, result.reason
    assert result.payload == {"sensor": "battery", "value": 10.9}


def test_wait_for_battery_threshold_times_out_when_no_sample_matches(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.queued = [_battery(12600)]
    result = _wait_for_battery_below(PX4Adapter(), 11.0, timeout_seconds=2.0)
    assert result.success is False
    assert result.timed_out is True
    assert _CLOCK.now >= 1002.0  # it kept reading until the timeout


def test_wait_for_emergency_stop_is_not_any_sys_status(fake_pymavlink: dict[str, Any]) -> None:
    """Regression: any SYS_STATUS counted as an emergency stop, and PX4 streams SYS_STATUS all the time."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.queued = [{"type": "SYS_STATUS", "msg": _Msg("SYS_STATUS", onboard_control_sensors_health=0)}]
    result = _wait_for_emergency_stop(PX4Adapter(), timeout_seconds=3.0)
    assert result.success is False
    assert result.timed_out is True
    assert result.reason == "timeout"


@pytest.mark.parametrize(("state", "name"), [(8, "flight_termination"), (6, "emergency")])
def test_wait_for_emergency_stop_fires_on_the_autopilot_heartbeat(
    fake_pymavlink: dict[str, Any], state: int, name: str
) -> None:
    """MAV_STATE_FLIGHT_TERMINATION (PX4: termination, kill switch) or MAV_STATE_EMERGENCY."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.emergency_at = _CLOCK.now + 2.0
    _FakePX4.emergency_state = state
    result = _wait_for_emergency_stop(PX4Adapter(), timeout_seconds=10.0)
    assert result.success is True, result.reason
    assert result.payload == {"event": "emergency_stop", "system_status": name}
    assert _CLOCK.now >= 1002.0  # it waited for the state; the normal heartbeats before it did not count


def test_wait_for_emergency_stop_fires_at_once_when_the_state_already_holds(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakePX4.emergency_at = _CLOCK.now
    result = _wait_for_emergency_stop(PX4Adapter(), timeout_seconds=10.0)
    assert result.success is True
    assert result.payload == {"event": "emergency_stop", "system_status": "flight_termination"}
    assert _CLOCK.now < 1000.5


def test_wait_for_emergency_stop_ignores_other_senders(fake_pymavlink: dict[str, Any]) -> None:
    """A ground station's heartbeat, or another vehicle's, is not this autopilot's emergency."""
    from urml_px4_runtime import PX4Adapter

    _FakePX4.queued = [
        _Msg("HEARTBEAT", src=(255, 190), type=6, autopilot=8, base_mode=0, custom_mode=0, system_status=8),
        _Msg("HEARTBEAT", src=(2, 1), type=2, autopilot=12, base_mode=0, custom_mode=0, system_status=8),
    ]
    result = _wait_for_emergency_stop(PX4Adapter(), timeout_seconds=3.0)
    assert result.success is False
    assert result.timed_out is True


def test_wait_passively_sleeps(fake_pymavlink: dict[str, Any]) -> None:
    import time as _time

    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    start = _time.monotonic()
    result = adapter.wait_passively(duration_seconds=0.05)
    assert result.success is True
    assert (_time.monotonic() - start) >= 0.04  # allow a little slop


def test_emit_report_sends_statustext(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.emit_report(
        to="user",
        facts={"battery": "low"},
        attachments=None,
        status="success",
        severity="info",
    )
    assert result.success is True
    statustexts = fake_pymavlink["connections"][0].mav.statustext_calls
    assert len(statustexts) == 1
    assert statustexts[0]["severity"] == 6  # info → MAV_SEVERITY_INFO
    # Payload is 50-byte capped, encoded as bytes
    assert isinstance(statustexts[0]["text"], bytes)


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------


def test_scan_is_not_supported_on_a_bare_autopilot(fake_pymavlink: dict[str, Any]) -> None:
    """Regression: scan reported success with coverage 1.0 while nothing flew and nothing was captured."""
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.run_scan(
        area={"bounding_box": {"min_x": 0, "max_x": 10, "min_y": 0, "max_y": 10}},
        pattern="serpentine",
        overlap=0.3,
        altitude=30.0,
        media="photo",
        sensor=None,
    )
    assert result.success is False
    assert (result.reason or "").startswith("not_supported_on_bare_autopilot")
    assert result.payload is None
    assert fake_pymavlink["connections"] == []  # nothing was sent to the vehicle


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------


def test_config_loader(tmp_path: Path) -> None:
    from urml_px4_runtime import load_px4_config

    p = tmp_path / "px4_adapter.yaml"
    p.write_text(
        """
connection_url: "udp:127.0.0.1:14540"
system_id: 255
component_id: 1
takeoff_timeout_seconds: 90
arrival_radius_m: 2.0
location_to_pose:
  roof_north: { north: 10.0, east: 5.0, alt: 30.0 }
""",
        encoding="utf-8",
    )
    cfg = load_px4_config(p)
    assert cfg.connection_url == "udp:127.0.0.1:14540"
    assert cfg.location_to_pose["roof_north"].north == 10.0
    assert cfg.location_to_pose["roof_north"].alt == 30.0
    assert cfg.takeoff_timeout_seconds == 90.0
    assert cfg.arrival_radius_m == 2.0


def test_config_flight_defaults() -> None:
    from urml_px4_runtime import PX4AdapterConfig

    cfg = PX4AdapterConfig()
    assert cfg.arm_timeout_seconds == 10.0
    assert cfg.takeoff_timeout_seconds == 120.0
    assert cfg.arrival_radius_m == 1.5
    assert cfg.arrival_alt_tolerance_m == 1.0
    assert cfg.arrival_timeout_seconds == 120.0
    assert cfg.land_timeout_seconds == 180.0


def test_config_rejects_non_positive_flight_limits() -> None:
    from pydantic import ValidationError

    from urml_px4_runtime import PX4AdapterConfig

    with pytest.raises(ValidationError):
        PX4AdapterConfig(arrival_radius_m=0.0)
    with pytest.raises(ValidationError):
        PX4AdapterConfig(land_timeout_seconds=-1.0)
