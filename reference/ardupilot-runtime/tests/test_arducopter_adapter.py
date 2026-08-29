"""Unit tests for ArduCopterAdapter — hermetic, no pymavlink install required.

A fake ``pymavlink`` is installed into ``sys.modules`` before each test,
following the PX4 runtime's pattern. The fake connection is scripted: it
answers ``COMMAND_ACK`` per command id, emits heartbeats whose mode and
armed flag follow the commands the adapter sent, and drains queued
position / STATUSTEXT messages so arrival and refusal paths can be
exercised without an autopilot.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest

# ---------------------------------------------------------------------------
# Fake pymavlink machinery
# ---------------------------------------------------------------------------


class _Msg(SimpleNamespace):
    """A MAVLink message stand-in with ``get_type()``."""

    def __init__(self, mtype: str, **fields: Any) -> None:
        super().__init__(**fields)
        self._mtype = mtype

    def get_type(self) -> str:
        return self._mtype

    def get_srcSystem(self) -> int:  # noqa: N802 — pymavlink API name
        return 10

    def get_srcComponent(self) -> int:  # noqa: N802 — pymavlink API name
        return 1


class _FakeMavLink:
    def __init__(self, conn: _FakeConnection) -> None:
        self._conn = conn
        self.command_long_calls: list[dict[str, Any]] = []
        self.local_target_calls: list[dict[str, Any]] = []
        self.global_target_calls: list[dict[str, Any]] = []
        self.statustext_calls: list[dict[str, Any]] = []

    def command_long_send(
        self, target_system: int, target_component: int, command: int, confirmation: int, *params: float
    ) -> None:
        self.command_long_calls.append({"command": command, "params": tuple(params)})
        self._conn.on_command(command, params)

    def set_position_target_local_ned_send(self, *args: Any) -> None:
        self.local_target_calls.append(
            {"frame": args[3], "type_mask": args[4], "position": (args[5], args[6], args[7])}
        )

    def set_position_target_global_int_send(self, *args: Any) -> None:
        self.global_target_calls.append(
            {"frame": args[3], "type_mask": args[4], "lat_int": args[5], "lon_int": args[6], "alt": args[7]}
        )

    def statustext_send(self, severity: int, text: bytes) -> None:
        self.statustext_calls.append({"severity": severity, "text": text})


class _FakeConnection:
    """Scripted ArduCopter.

    Class-level knobs (reset per test):
      - ``heartbeat``: autopilot / type on the first heartbeat.
      - ``ack_results``: {command_id: MAV_RESULT}; missing -> accepted (0);
        ``-1`` -> never ack.
      - ``mode_accepts`` / ``arm_accepts``: whether the heartbeat *follows*
        an accepted mode / arm command (a rejected-by-behaviour case).
      - ``prearm_text``: STATUSTEXT emitted on an arm command.
      - ``queued``: messages delivered for other ``recv_match`` types, in order.
    """

    heartbeat: dict[str, int] = {"autopilot": 3, "type": 2}  # noqa: RUF012
    ack_results: dict[int, int] = {}  # noqa: RUF012
    mode_accepts: bool = True
    arm_accepts: bool = True
    prearm_text: str | None = None
    queued: list[Any] = []  # noqa: RUF012
    wait_heartbeat_returns_none: bool = False
    stray_ack: bool = False

    def __init__(self, url: str, *_: Any, **__: Any) -> None:
        self.url = url
        self.target_system = 10
        self.target_component = 1
        self.mav = _FakeMavLink(self)
        self._mode = 0
        self._armed = False
        self._closed = False
        self._pending: list[Any] = []

    def close(self) -> None:
        self._closed = True

    def mode_mapping(self) -> dict[str, int]:
        return {"STABILIZE": 0, "GUIDED": 4, "LOITER": 5, "RTL": 6, "LAND": 9}

    def _hb(self) -> _Msg:
        return _Msg(
            "HEARTBEAT",
            autopilot=_FakeConnection.heartbeat["autopilot"],
            type=_FakeConnection.heartbeat["type"],
            custom_mode=self._mode,
            base_mode=(128 if self._armed else 0) | 1,
        )

    def wait_heartbeat(self, *, timeout: float = 5.0) -> Any:
        if _FakeConnection.wait_heartbeat_returns_none:
            return None
        return self._hb()

    def on_command(self, command: int, params: tuple[float, ...]) -> None:
        result = _FakeConnection.ack_results.get(command, 0)
        if command == 176 and result == 0 and _FakeConnection.mode_accepts:
            self._mode = int(params[1])
        if command == 400 and result == 0 and _FakeConnection.arm_accepts:
            self._armed = bool(params[0])
        if command == 400 and _FakeConnection.prearm_text:
            self._pending.append(_Msg("STATUSTEXT", severity=2, text=_FakeConnection.prearm_text))
        if command == 511:
            return  # stream requests are never acked in the fake
        if _FakeConnection.stray_ack:
            self._pending.append(_Msg("COMMAND_ACK", command=999, result=4))
        if result >= 0:
            self._pending.append(_Msg("COMMAND_ACK", command=command, result=result))

    def recv_match(self, *, type: Any = None, blocking: bool = False, timeout: float = 0.0) -> Any:
        wanted = {type} if isinstance(type, str) else (set(type) if type else None)
        # Pending acks / statustext first.
        for i, msg in enumerate(self._pending):
            if wanted is None or msg.get_type() in wanted:
                return self._pending.pop(i)
        if wanted is None or "HEARTBEAT" in wanted:
            if wanted is None and _FakeConnection.queued:
                return _FakeConnection.queued.pop(0)
            return self._hb()
        while _FakeConnection.queued:
            msg = _FakeConnection.queued.pop(0)
            if msg is None:
                return None
            if msg.get_type() in wanted:
                return msg
        return None


def _install_fake_pymavlink(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    _FakeConnection.heartbeat = {"autopilot": 3, "type": 2}
    _FakeConnection.ack_results = {}
    _FakeConnection.mode_accepts = True
    _FakeConnection.arm_accepts = True
    _FakeConnection.prearm_text = None
    _FakeConnection.queued = []
    _FakeConnection.wait_heartbeat_returns_none = False
    _FakeConnection.stray_ack = False

    captured: dict[str, Any] = {"connections": []}

    def _mavlink_connection(url: str, *args: Any, **kwargs: Any) -> _FakeConnection:
        conn = _FakeConnection(url, *args, **kwargs)
        captured["connections"].append(conn)
        return conn

    mavutil = ModuleType("pymavlink.mavutil")
    mavutil.mavlink_connection = _mavlink_connection  # type: ignore[attr-defined]
    pymavlink = ModuleType("pymavlink")
    pymavlink.mavutil = mavutil  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "pymavlink", pymavlink)
    monkeypatch.setitem(sys.modules, "pymavlink.mavutil", mavutil)
    return captured


@pytest.fixture
def fake(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    monkeypatch.setattr("urml_ardupilot_runtime.adapter.time.sleep", lambda *_: None)
    yield _install_fake_pymavlink(monkeypatch)


def _adapter(**cfg: Any) -> Any:
    from urml_ardupilot_runtime import ArduCopterAdapter, ArduPilotAdapterConfig

    return ArduCopterAdapter(ArduPilotAdapterConfig(**cfg))


def _commands(fake: dict[str, Any]) -> list[int]:
    return [c["command"] for c in fake["connections"][0].mav.command_long_calls if c["command"] != 511]


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def test_serial_url_gets_baud_suffix() -> None:
    from urml_ardupilot_runtime import ArduPilotAdapterConfig

    assert ArduPilotAdapterConfig(connection_url="COM5").effective_connection_url() == "COM5,115200"
    assert ArduPilotAdapterConfig(connection_url="/dev/ttyACM0", baud=57600).effective_connection_url() == (
        "/dev/ttyACM0,57600"
    )


def test_udp_url_untouched() -> None:
    from urml_ardupilot_runtime import ArduPilotAdapterConfig

    cfg = ArduPilotAdapterConfig()
    assert cfg.effective_connection_url() == "udp:127.0.0.1:14550"
    assert cfg.component_id == 190


def test_config_loads_from_yaml(tmp_path: Any) -> None:
    from urml_ardupilot_runtime import load_ardupilot_config

    p = tmp_path / "ap.yaml"
    p.write_text(
        "connection_url: COM7\nlocation_to_global:\n  site: {lat: 32.1, lon: 34.8, alt_agl: 100}\n"
        "output_lines:\n  latch: {kind: gripper}\ncamera: {kind: digicam}\n",
        encoding="utf-8",
    )
    cfg = load_ardupilot_config(p)
    assert cfg.resolve_global("site") is not None
    assert cfg.output_lines["latch"].kind == "gripper"
    assert cfg.camera is not None


# ---------------------------------------------------------------------------
# Import / construction
# ---------------------------------------------------------------------------


def test_module_imports_without_pymavlink() -> None:
    from urml_ardupilot_runtime import adapter

    assert adapter.ArduCopterAdapter is not None


def test_constructor_does_not_connect(fake: dict[str, Any]) -> None:
    _adapter()
    assert fake["connections"] == []


def test_satisfies_adapter_protocols(fake: dict[str, Any]) -> None:
    from urml_ros2_runtime.substrate.base import OutputAdapter, ROSAdapter

    a = _adapter()
    assert isinstance(a, ROSAdapter)
    assert isinstance(a, OutputAdapter)


# ---------------------------------------------------------------------------
# Connection identity checks
# ---------------------------------------------------------------------------


def test_non_ardupilot_heartbeat_is_a_clean_failure(fake: dict[str, Any]) -> None:
    _FakeConnection.heartbeat = {"autopilot": 12, "type": 2}  # PX4
    result = _adapter().send_takeoff_goal(altitude=5.0)
    assert result.success is False
    assert result.reason is not None
    assert result.reason.startswith("connection_failed: not_an_ardupilot_autopilot")
    assert fake["connections"][0]._closed is True


def test_non_copter_type_is_a_clean_failure(fake: dict[str, Any]) -> None:
    _FakeConnection.heartbeat = {"autopilot": 3, "type": 1}  # fixed wing
    result = _adapter().send_takeoff_goal(altitude=5.0)
    assert result.success is False
    assert "not_a_copter" in (result.reason or "")


def test_missing_heartbeat_is_a_clean_failure(fake: dict[str, Any]) -> None:
    _FakeConnection.wait_heartbeat_returns_none = True
    result = _adapter(connection_url="COM9").send_takeoff_goal(altitude=5.0)
    assert result.success is False
    assert "heartbeat_timeout" in (result.reason or "")
    assert fake["connections"][0].url == "COM9,115200"


def test_connect_requests_telemetry_streams(fake: dict[str, Any]) -> None:
    _adapter().send_takeoff_goal(altitude=5.0)
    stream_reqs = [c for c in fake["connections"][0].mav.command_long_calls if c["command"] == 511]
    assert {int(c["params"][0]) for c in stream_reqs} >= {33, 32, 147}


# ---------------------------------------------------------------------------
# Take-off preamble
# ---------------------------------------------------------------------------


def test_takeoff_happy_path_orders_guided_arm_takeoff(fake: dict[str, Any]) -> None:
    _FakeConnection.queued = [_Msg("GLOBAL_POSITION_INT", lat=0, lon=0, relative_alt=29_800)]
    result = _adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is True, result.reason
    assert _commands(fake) == [176, 400, 22]
    takeoff = next(c for c in fake["connections"][0].mav.command_long_calls if c["command"] == 22)
    assert takeoff["params"][6] == 30.0
    assert result.final_pose == {"x": 0.0, "y": 0.0, "z": 29.8}


def test_takeoff_stops_at_mode_rejection(fake: dict[str, Any]) -> None:
    _FakeConnection.ack_results = {176: 4}  # MAV_RESULT_FAILED
    result = _adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert (result.reason or "").startswith("mode_rejected: GUIDED mav_result_failed")
    assert 400 not in _commands(fake)
    assert 22 not in _commands(fake)


def test_takeoff_stops_when_mode_not_confirmed(fake: dict[str, Any]) -> None:
    _FakeConnection.mode_accepts = False
    result = _adapter(mode_timeout_seconds=0.01).send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert "mode_rejected: GUIDED not confirmed" in (result.reason or "")


def test_arm_rejection_surfaces_prearm_text(fake: dict[str, Any]) -> None:
    _FakeConnection.ack_results = {400: 4}
    _FakeConnection.prearm_text = "PreArm: Need 3D Fix"
    result = _adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == "arm_rejected: mav_result_failed; PreArm: Need 3D Fix"
    assert 22 not in _commands(fake)


def test_arm_not_confirmed_on_heartbeat(fake: dict[str, Any]) -> None:
    _FakeConnection.arm_accepts = False
    result = _adapter(arm_timeout_seconds=0.01).send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert "arm_rejected: armed flag not seen" in (result.reason or "")


def test_takeoff_timeout_when_altitude_not_reached(fake: dict[str, Any]) -> None:
    _FakeConnection.queued = [_Msg("GLOBAL_POSITION_INT", lat=0, lon=0, relative_alt=1_000), None]
    result = _adapter(takeoff_timeout_seconds=0.05).send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == "takeoff_timeout: target altitude not reached"


def test_ack_for_a_different_command_is_ignored(fake: dict[str, Any]) -> None:
    """A stray, failed COMMAND_ACK for another command must not be taken as ours."""
    _FakeConnection.stray_ack = True
    _FakeConnection.queued = [_Msg("GLOBAL_POSITION_INT", lat=0, lon=0, relative_alt=30_000)]
    result = _adapter().send_takeoff_goal(altitude=30.0)
    assert result.success is True, result.reason
    assert _commands(fake) == [176, 400, 22]


# ---------------------------------------------------------------------------
# Land / RTL
# ---------------------------------------------------------------------------


def test_land_enters_land_mode(fake: dict[str, Any]) -> None:
    result = _adapter(arrival_timeout_seconds=0.01).send_land_goal()
    assert result.success is True
    mode_cmd = next(c for c in fake["connections"][0].mav.command_long_calls if c["command"] == 176)
    assert mode_cmd["params"][1] == 9.0


def test_rtl_enters_rtl_mode(fake: dict[str, Any]) -> None:
    result = _adapter().send_return_to_home_goal()
    assert result.success is True
    mode_cmd = next(c for c in fake["connections"][0].mav.command_long_calls if c["command"] == 176)
    assert mode_cmd["params"][1] == 6.0


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


def test_local_move_waits_for_arrival(fake: dict[str, Any]) -> None:
    from urml_px4_runtime.config import NEDPosition

    _FakeConnection.queued = [
        _Msg("LOCAL_POSITION_NED", x=2.0, y=0.0, z=-30.0),
        _Msg("LOCAL_POSITION_NED", x=15.2, y=0.1, z=-29.7),
    ]
    a = _adapter(location_to_pose={"roof": NEDPosition(north=15.0, east=0.0, alt=30.0)})
    result = a.send_navigation_goal(location="roof")
    assert result.success is True, result.reason
    target = fake["connections"][0].mav.local_target_calls[0]
    assert target["position"] == (15.0, 0.0, -30.0)
    assert target["frame"] == 1


def test_local_move_arrival_timeout(fake: dict[str, Any]) -> None:
    _FakeConnection.queued = [_Msg("LOCAL_POSITION_NED", x=0.0, y=0.0, z=0.0), None]
    result = _adapter(arrival_timeout_seconds=0.05).send_navigation_goal(pose={"x": 10.0, "y": 0.0, "z": 20.0})
    assert result.success is False
    assert result.reason == "arrival_timeout: setpoint not reached"


def test_global_move_sends_global_int_and_roi(fake: dict[str, Any]) -> None:
    _FakeConnection.queued = [
        _Msg("GLOBAL_POSITION_INT", lat=320853000, lon=347818000, relative_alt=100_200),
    ]
    a = _adapter(
        location_to_global={
            "site_p1": {"lat": 32.0853, "lon": 34.7818, "alt_agl": 100.0, "look_at": {"lat": 32.085, "lon": 34.7815}}
        }
    )
    result = a.send_navigation_goal(location="site_p1")
    assert result.success is True, result.reason
    g = fake["connections"][0].mav.global_target_calls[0]
    assert g["frame"] == 6
    assert g["lat_int"] == 320853000
    assert g["lon_int"] == 347818000
    assert g["alt"] == 100.0
    assert fake["connections"][0].mav.local_target_calls == []
    roi = [c for c in fake["connections"][0].mav.command_long_calls if c["command"] == 195]
    assert roi and roi[0]["params"][4:6] == (32.085, 34.7815)
    assert result.frame == "wgs84"


def test_global_binding_wins_over_local(fake: dict[str, Any]) -> None:
    from urml_px4_runtime.config import NEDPosition

    _FakeConnection.queued = [_Msg("GLOBAL_POSITION_INT", lat=100000000, lon=200000000, relative_alt=10_000)]
    a = _adapter(
        location_to_pose={"x": NEDPosition(north=1.0, east=1.0, alt=1.0)},
        location_to_global={"x": {"lat": 10.0, "lon": 20.0, "alt_agl": 10.0}},
    )
    assert a.send_navigation_goal(location="x").success is True
    assert fake["connections"][0].mav.global_target_calls
    assert not fake["connections"][0].mav.local_target_calls


def test_rtl_clears_roi_after_global_move(fake: dict[str, Any]) -> None:
    _FakeConnection.queued = [_Msg("GLOBAL_POSITION_INT", lat=100000000, lon=200000000, relative_alt=10_000)]
    a = _adapter(
        location_to_global={"x": {"lat": 10.0, "lon": 20.0, "alt_agl": 10.0, "look_at": {"lat": 10, "lon": 20}}}
    )
    a.send_navigation_goal(location="x")
    a.send_return_to_home_goal()
    assert 197 in _commands(fake)


def test_unbound_location_is_a_clean_failure(fake: dict[str, Any]) -> None:
    result = _adapter().send_navigation_goal(location="nowhere")
    assert result.success is False
    assert (result.reason or "").startswith("location_not_configured")


def test_hover_without_target_is_confirmed_noop(fake: dict[str, Any]) -> None:
    result = _adapter().send_navigation_goal(speed=0.0)
    assert result.success is True
    assert _commands(fake) == [176]  # GUIDED only, no setpoint


# ---------------------------------------------------------------------------
# Camera
# ---------------------------------------------------------------------------


def test_capture_without_camera_config_is_not_supported(fake: dict[str, Any]) -> None:
    result = _adapter().capture_media(media="photo", target=None, duration_seconds=None, attributes=None)
    assert result.success is False
    assert "camera_not_configured" in (result.reason or "")


def test_capture_digicam_geotags_from_last_position(fake: dict[str, Any]) -> None:
    _FakeConnection.queued = [_Msg("GLOBAL_POSITION_INT", lat=320853000, lon=347818000, relative_alt=100_000)]
    a = _adapter(camera={"kind": "digicam"}, location_to_global={"p": {"lat": 32.0853, "lon": 34.7818, "alt_agl": 100}})
    assert a.send_navigation_goal(location="p").success is True
    result = a.capture_media(media="photo", target=None, duration_seconds=None, attributes=None)
    assert result.success is True, result.reason
    assert 203 in _commands(fake)
    assert result.payload["uri"] == "camera://shot/1"
    assert result.payload["pose"] == {"lat": 32.0853, "lon": 34.7818, "alt_agl": 100.0}
    assert result.payload["frame"] == "wgs84"


def test_capture_servo_pulses_channel(fake: dict[str, Any]) -> None:
    a = _adapter(camera={"kind": "servo", "channel": 9, "pwm_on": 1900, "pwm_off": 1100})
    result = a.capture_media(media="photo", target=None, duration_seconds=None, attributes=None)
    assert result.success is True, result.reason
    servo = [c["params"][:2] for c in fake["connections"][0].mav.command_long_calls if c["command"] == 183]
    assert servo == [(9.0, 1900.0), (9.0, 1100.0)]


def test_capture_video_not_supported(fake: dict[str, Any]) -> None:
    a = _adapter(camera={"kind": "digicam"})
    result = a.capture_media(media="video", target=None, duration_seconds=5.0, attributes=None)
    assert result.success is False
    assert "video_not_supported" in (result.reason or "")


def test_capture_rejected_ack(fake: dict[str, Any]) -> None:
    _FakeConnection.ack_results = {203: 3}
    a = _adapter(camera={"kind": "digicam"})
    result = a.capture_media(media="photo", target=None, duration_seconds=None, attributes=None)
    assert result.success is False
    assert result.reason == "capture_rejected: mav_result_unsupported"


# ---------------------------------------------------------------------------
# Output lines
# ---------------------------------------------------------------------------


def test_unknown_output_line_is_clean_failure(fake: dict[str, Any]) -> None:
    result = _adapter().set_output_line(output="latch", value=True)
    assert result.success is False
    assert "output_line_not_configured" in (result.reason or "")
    assert fake["connections"] == []  # never even connected


def test_gripper_line_release_and_grab(fake: dict[str, Any]) -> None:
    a = _adapter(output_lines={"latch": {"kind": "gripper", "instance": 2}})
    assert a.set_output_line(output="latch", value=True).success is True
    assert a.set_output_line(output="latch", value=False).success is True
    calls = [c["params"][:2] for c in fake["connections"][0].mav.command_long_calls if c["command"] == 211]
    assert calls == [(2.0, 0.0), (2.0, 1.0)]  # RELEASE then GRAB


def test_winch_line_deliver_and_retract(fake: dict[str, Any]) -> None:
    a = _adapter(output_lines={"winch": {"kind": "winch", "deliver_length_m": 15.0, "rate_m_s": 0.5}})
    assert a.set_output_line(output="winch", value=True).success is True
    assert a.set_output_line(output="winch", value=False).success is True
    calls = [c["params"][:4] for c in fake["connections"][0].mav.command_long_calls if c["command"] == 42600]
    assert calls == [(1.0, 1.0, 15.0, 0.5), (1.0, 1.0, -15.0, 0.5)]  # relative length +/-


def test_servo_line_pulse_reverts(fake: dict[str, Any]) -> None:
    a = _adapter(output_lines={"aux": {"kind": "servo", "channel": 10, "on_pwm": 2000, "off_pwm": 1000}})
    assert a.set_output_line(output="aux", value=True, pulse_ms=200).success is True
    calls = [c["params"][:2] for c in fake["connections"][0].mav.command_long_calls if c["command"] == 183]
    assert calls == [(10.0, 2000.0), (10.0, 1000.0)]


def test_output_rejected_ack(fake: dict[str, Any]) -> None:
    _FakeConnection.ack_results = {211: 2}
    a = _adapter(output_lines={"latch": {"kind": "gripper"}})
    result = a.set_output_line(output="latch", value=True)
    assert result.success is False
    assert result.reason == "output_rejected: latch mav_result_denied"


# ---------------------------------------------------------------------------
# Probe
# ---------------------------------------------------------------------------


def test_probe_is_read_only(fake: dict[str, Any]) -> None:
    _FakeConnection.queued = [
        _Msg("AUTOPILOT_VERSION", flight_sw_version=(4 << 24) | (6 << 16) | (3 << 8)),
        _Msg("BATTERY_STATUS", voltages=[12_600]),
        _Msg("GPS_RAW_INT", fix_type=3, satellites_visible=11),
        None,
    ]
    info = _adapter().probe(listen_seconds=0.05)
    assert info["autopilot"] == "ArduPilot"
    assert info["mav_type"] == 2
    assert info["system_id"] == 10
    assert info["armed"] is False
    assert info["mode"] == "STABILIZE"
    assert info["firmware"] == "4.6.3"
    assert info["battery_v"] == 12.6
    assert info["gps_fix"] == 3
    sent = _commands(fake)
    assert 512 in sent  # version request
    assert not ({176, 400, 22, 211, 42600, 183, 203} & set(sent))


# ---------------------------------------------------------------------------
# Inherited surface unchanged
# ---------------------------------------------------------------------------


def test_manipulation_still_not_supported(fake: dict[str, Any]) -> None:
    result = _adapter().send_manipulation_goal(action="grasp")
    assert result.success is False
    assert "not_supported_on_bare_autopilot" in (result.reason or "")
