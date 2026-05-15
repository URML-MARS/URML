"""Unit tests for PX4Adapter — hermetic, no pymavlink install required.

The adapter imports pymavlink lazily. These tests install a fake
``pymavlink`` package into ``sys.modules`` before each test so:

  - The test file collects on every host (Linux, Windows, CI runners).
  - Every adapter code path is exercised against a controllable fake.
  - Real MAVLink behavior is verified separately under live integration
    tests (PX4 SITL; documented follow-up in the README).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from pathlib import Path
from types import ModuleType, SimpleNamespace
from typing import Any

import pytest


# ---------------------------------------------------------------------------
# Fake pymavlink machinery
# ---------------------------------------------------------------------------


class _FakeMavLink:
    """Stand-in for the `mav` attribute of a pymavlink connection.

    Records every command_long_send / set_position_target_local_ned_send /
    statustext_send call so tests can assert on them.
    """

    def __init__(self) -> None:
        self.command_long_calls: list[dict[str, Any]] = []
        self.set_position_target_calls: list[dict[str, Any]] = []
        self.statustext_calls: list[dict[str, Any]] = []

    def command_long_send(
        self,
        target_system: int,
        target_component: int,
        command: int,
        confirmation: int,
        p1: float,
        p2: float,
        p3: float,
        p4: float,
        p5: float,
        p6: float,
        p7: float,
    ) -> None:
        self.command_long_calls.append(
            {
                "target_system": target_system,
                "target_component": target_component,
                "command": command,
                "confirmation": confirmation,
                "params": (p1, p2, p3, p4, p5, p6, p7),
            }
        )

    def set_position_target_local_ned_send(
        self,
        time_boot_ms: int,
        target_system: int,
        target_component: int,
        coordinate_frame: int,
        type_mask: int,
        x: float,
        y: float,
        z: float,
        vx: float,
        vy: float,
        vz: float,
        afx: float,
        afy: float,
        afz: float,
        yaw: float,
        yaw_rate: float,
    ) -> None:
        self.set_position_target_calls.append(
            {
                "frame": coordinate_frame,
                "type_mask": type_mask,
                "position": (x, y, z),
                "velocity": (vx, vy, vz),
                "yaw": yaw,
            }
        )

    def statustext_send(self, severity: int, text: bytes) -> None:
        self.statustext_calls.append({"severity": severity, "text": text})


class _FakeConnection:
    """Configurable fake pymavlink connection.

    Tests set:
      - ``ack_result`` (int): MAV_RESULT value to return from
        command_long → COMMAND_ACK. 0 = ACCEPTED. -1 = no ACK (timeout).
      - ``recv_match_responses``: queue of messages to deliver for
        recv_match calls. Each entry is a dict {"type": ..., "msg": ...}
        or ``None`` to simulate a timeout.
    """

    ack_result: int = 0
    recv_match_responses: list[Any] = []  # noqa: RUF012  — shared, reset per test

    def __init__(self, *_: Any, **__: Any) -> None:
        self.target_system = 1
        self.target_component = 1
        self.mav = _FakeMavLink()
        self.heartbeat_waits: int = 0
        self._closed = False

    def wait_heartbeat(self, *, timeout: float = 5.0) -> None:
        self.heartbeat_waits += 1

    def recv_match(
        self,
        *,
        type: str | None = None,  # noqa: A002 — pymavlink uses `type`
        blocking: bool = False,
        timeout: float = 0.0,
    ) -> Any:
        # Always-on responder for COMMAND_ACK: return the configured ack
        # result. (Tests set ack_result before sending the command.)
        if type == "COMMAND_ACK":
            if _FakeConnection.ack_result < 0:
                return None
            return SimpleNamespace(result=_FakeConnection.ack_result)
        # For other types, drain from the queued responses.
        if _FakeConnection.recv_match_responses:
            response = _FakeConnection.recv_match_responses.pop(0)
            if response is None:
                return None
            if isinstance(response, dict):
                return response.get("msg") if response.get("type") == type else None
            return response
        return None

    def close(self) -> None:
        self._closed = True


def _make_fake_module(name: str, **attrs: Any) -> ModuleType:
    mod = ModuleType(name)
    for k, v in attrs.items():
        setattr(mod, k, v)
    return mod


def _install_fake_pymavlink(monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    """Install fake pymavlink into sys.modules; return shared state."""
    _FakeConnection.ack_result = 0
    _FakeConnection.recv_match_responses = []

    captured: dict[str, Any] = {"connections": []}

    def _mavlink_connection(*args: Any, **kwargs: Any) -> _FakeConnection:
        conn = _FakeConnection(*args, **kwargs)
        captured["connections"].append(conn)
        return conn

    mavutil = _make_fake_module(
        "pymavlink.mavutil",
        mavlink_connection=_mavlink_connection,
    )
    pymavlink = _make_fake_module("pymavlink", mavutil=mavutil)

    monkeypatch.setitem(sys.modules, "pymavlink", pymavlink)
    monkeypatch.setitem(sys.modules, "pymavlink.mavutil", mavutil)
    return captured


@pytest.fixture
def fake_pymavlink(monkeypatch: pytest.MonkeyPatch) -> Iterator[dict[str, Any]]:
    yield _install_fake_pymavlink(monkeypatch)


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


# ---------------------------------------------------------------------------
# Drone-profile dispatch
# ---------------------------------------------------------------------------


def test_takeoff_sends_mav_cmd_nav_takeoff(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.send_takeoff_goal(altitude=30.0)
    assert result.success is True
    assert result.final_pose == {"x": 0.0, "y": 0.0, "z": 30.0}
    cmd = fake_pymavlink["connections"][0].mav.command_long_calls[0]
    assert cmd["command"] == 22  # MAV_CMD_NAV_TAKEOFF
    assert cmd["params"][6] == 30.0  # param7 = altitude


def test_takeoff_failure_on_ack_reject(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakeConnection.ack_result = 3  # MAV_RESULT_DENIED
    adapter = PX4Adapter()
    result = adapter.send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == "mav_result_3"


def test_takeoff_failure_on_ack_timeout(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakeConnection.ack_result = -1  # simulate no ACK
    adapter = PX4Adapter()
    result = adapter.send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == "ack_timeout"


def test_land_sends_mav_cmd_nav_land(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.send_land_goal()
    assert result.success is True
    assert fake_pymavlink["connections"][0].mav.command_long_calls[0]["command"] == 21


def test_return_to_home_sends_mav_cmd_nav_rtl(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.send_return_to_home_goal()
    assert result.success is True
    assert fake_pymavlink["connections"][0].mav.command_long_calls[0]["command"] == 20


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------


def test_send_navigation_goal_uses_location_from_config(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter, PX4AdapterConfig
    from urml_px4_runtime.config import NEDPosition

    cfg = PX4AdapterConfig(
        location_to_pose={"roof_north": NEDPosition(north=10.0, east=5.0, alt=30.0)}
    )
    adapter = PX4Adapter(cfg)
    result = adapter.send_navigation_goal(location="roof_north")
    assert result.success is True
    assert result.final_pose == {"x": 10.0, "y": 5.0, "z": 30.0}
    target = fake_pymavlink["connections"][0].mav.set_position_target_calls[0]
    # NED down = -alt (we store alt positive-up, send NED down).
    assert target["position"] == (10.0, 5.0, -30.0)


def test_send_navigation_goal_uses_pose_directly(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    adapter = PX4Adapter()
    result = adapter.send_navigation_goal(pose={"x": 5.0, "y": 3.0, "z": 20.0}, frame="ned")
    assert result.success is True
    target = fake_pymavlink["connections"][0].mav.set_position_target_calls[0]
    assert target["position"] == (5.0, 3.0, -20.0)


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
    _FakeConnection.recv_match_responses = [
        {"type": "DISTANCE_SENSOR", "msg": SimpleNamespace(current_distance=1500, time_boot_ms=12000)}
    ]
    adapter = PX4Adapter()
    result = adapter.take_measurement(what="distance", target=None, sensor=None)
    assert result.success is True
    assert result.payload == {"value": 15.0, "unit": "m", "timestamp": 12.0}


def test_measure_voltage_reads_battery_status(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    # voltages[0] is mV; 12400 mV = 12.4 V.
    _FakeConnection.recv_match_responses = [
        {"type": "BATTERY_STATUS", "msg": SimpleNamespace(voltages=[12400], time_boot_ms=5000)}
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


def test_wait_for_battery_threshold(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakeConnection.recv_match_responses = [
        {"type": "BATTERY_STATUS", "msg": SimpleNamespace(voltages=[10000])}
    ]
    adapter = PX4Adapter()
    result = adapter.wait_for_condition(
        kind="sensor_threshold",
        name=None,
        input_mode=None,
        threshold={"sensor": "battery", "op": "lt", "value": 11.0},
        timeout_seconds=1.0,
    )
    assert result.success is True
    assert result.payload == {"sensor": "battery", "value": 10.0}


def test_wait_for_emergency_stop_event(fake_pymavlink: dict[str, Any]) -> None:
    from urml_px4_runtime import PX4Adapter

    _FakeConnection.recv_match_responses = [
        {"type": "SYS_STATUS", "msg": SimpleNamespace()}
    ]
    adapter = PX4Adapter()
    result = adapter.wait_for_condition(
        kind="event",
        name="emergency_stop",
        input_mode=None,
        threshold=None,
        timeout_seconds=1.0,
    )
    assert result.success is True


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
# Scan stub
# ---------------------------------------------------------------------------


def test_scan_returns_stub_success(fake_pymavlink: dict[str, Any]) -> None:
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
    assert result.success is True
    assert result.payload is not None
    assert result.payload["coverage"] == 1.0


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
location_to_pose:
  roof_north: { north: 10.0, east: 5.0, alt: 30.0 }
""",
        encoding="utf-8",
    )
    cfg = load_px4_config(p)
    assert cfg.connection_url == "udp:127.0.0.1:14540"
    assert cfg.location_to_pose["roof_north"].north == 10.0
    assert cfg.location_to_pose["roof_north"].alt == 30.0
