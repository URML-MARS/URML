"""Hermetic unit tests for MicroduckAdapter — no robot, no socket.

The adapter's ``_dial`` hook is monkeypatched to return a scripted NDJSON
transport, so every wire behaviour (handshake, request/response id
matching, notifications for continuous intents, error surfacing) is
exercised against the `duck-ipc-proto` contract shapes without opening a
socket.
"""

from __future__ import annotations

import json
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import ROSAdapter

from urml_edu_runtime import EduConfig, EduSkillCall
from urml_edu_runtime.microduck import MicroduckAdapter


class _FakeTransport:
    """Scripted duplex: records written lines, answers requests by method."""

    def __init__(self) -> None:
        self.written: list[dict[str, Any]] = []
        self.results: dict[str, Any] = {"hello": {"api_version": 16}}
        self.errors: dict[str, dict[str, Any]] = {}
        self.interleave_noise = False
        self._pending: list[str] = []
        self.closed = False

    def write_line(self, line: str) -> None:
        message = json.loads(line)
        self.written.append(message)
        if "id" not in message:
            return  # notification: no reply
        method = message["method"]
        if self.interleave_noise:
            self._pending.append(
                json.dumps({"jsonrpc": "2.0", "method": "update.progress", "params": {"pct": 50}})
            )
        if method in self.errors:
            self._pending.append(
                json.dumps({"jsonrpc": "2.0", "id": message["id"], "error": self.errors[method]})
            )
        else:
            self._pending.append(
                json.dumps({"jsonrpc": "2.0", "id": message["id"], "result": self.results.get(method, {})})
            )

    def read_line(self) -> str:
        if not self._pending:
            raise RuntimeError("fake transport: nothing to read")
        return self._pending.pop(0)

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def duck(monkeypatch: pytest.MonkeyPatch) -> tuple[MicroduckAdapter, _FakeTransport]:
    transport = _FakeTransport()
    monkeypatch.setattr(MicroduckAdapter, "_dial", lambda self: transport)
    cfg = EduConfig(
        device="tcp://duck.local:7007",
        location_to_command={
            "sit_spot": EduSkillCall(method="robot.do", kwargs={"skill": "sit_toggle"}),
            "step_ahead": EduSkillCall(method="robot.move", kwargs={"vx": 0.1, "vy": 0.0, "vyaw": 0.0}),
            "stand_up": "robot.init",
        },
        manipulation_commands={
            "grasp": EduSkillCall(method="robot.do", kwargs={"skill": "ground_pick"}),
            "release": "robot.relax",
        },
    )
    return MicroduckAdapter(cfg), transport


def _methods(transport: _FakeTransport) -> list[str]:
    return [m["method"] for m in transport.written]


def test_satisfies_protocol(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, _ = duck
    assert isinstance(adapter, ROSAdapter)


def test_hello_handshake_first(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    assert adapter.send_navigation_goal(location="stand_up").success
    assert _methods(transport)[0] == "hello"
    assert transport.written[0]["params"] == {"api_version": 16}
    # Second call reuses the connection: no second handshake.
    assert adapter.send_navigation_goal(location="stand_up").success
    assert _methods(transport).count("hello") == 1


def test_skill_request_is_answered(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    assert adapter.send_navigation_goal(location="sit_spot").success
    do = next(m for m in transport.written if m["method"] == "robot.do")
    assert do["params"] == {"skill": "sit_toggle"}
    assert "id" in do  # discrete intent: a request, not a notification


def test_continuous_intent_is_a_notification(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    assert adapter.send_navigation_goal(location="step_ahead").success
    move = next(m for m in transport.written if m["method"] == "robot.move")
    assert move["params"] == {"vx": 0.1, "vy": 0.0, "vyaw": 0.0}
    assert "id" not in move  # continuous intent: notification, no reply expected


def test_unknown_location_is_typed_failure(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, _ = duck
    result = adapter.send_navigation_goal(location="nowhere")
    assert result.success is False
    assert (result.reason or "").startswith("location_not_configured")


def test_manipulation_maps_to_ground_pick(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    assert adapter.send_manipulation_goal(action="grasp").success
    assert adapter.send_manipulation_goal(action="release").success
    methods = _methods(transport)
    assert "robot.do" in methods and "robot.relax" in methods


def test_rpc_error_surfaces_as_typed_runtime_error(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    transport.errors["robot.do"] = {"code": -32601, "message": "another skill holds the robot"}
    with pytest.raises(RuntimeError, match=r"microduck_rpc_error: robot.do"):
        adapter.send_navigation_goal(location="sit_spot")


def test_interleaved_notifications_are_skipped(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    transport.interleave_noise = True
    assert adapter.send_navigation_goal(location="sit_spot").success


def test_measure_health_passes_result_through(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    transport.results["robot.health"] = {"ok": True, "release": "0.4.1"}
    reading = adapter.take_measurement(what="health", target=None, sensor=None)
    assert reading.success
    assert reading.payload is not None
    assert reading.payload["value"] == {"ok": True, "release": "0.4.1"}


def test_measure_rejects_non_readback_method(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, _ = duck
    bad = adapter.take_measurement(what="x", target=None, sensor="drop table")
    assert bad.success is False
    assert (bad.reason or "").startswith("microduck_sensor_not_found")


def test_measure_error_returns_failure_not_raise(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    transport.errors["robot.mode"] = {"code": 1, "message": "no mode"}
    result = adapter.take_measurement(what="mode", target=None, sensor="robot.mode")
    assert result.success is False
    assert "microduck_rpc_error" in (result.reason or "")


def test_positional_args_rejected(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, _ = duck
    adapter._config.location_to_command["bad"] = EduSkillCall(method="robot.do", args=["sit_toggle"])
    with pytest.raises(RuntimeError, match="microduck_positional_args_not_supported"):
        adapter.send_navigation_goal(location="bad")


def test_device_shapes() -> None:
    from urml_edu_runtime.microduck import MicroduckAdapter as A

    bad = A(EduConfig(device="serial:///dev/ttyUSB0"))
    with pytest.raises(RuntimeError, match="microduck_device_invalid"):
        bad._dial()
    no_port = A(EduConfig(device="tcp://duck.local"))
    with pytest.raises(RuntimeError, match="microduck_device_invalid"):
        no_port._dial()


def test_close_closes_transport(duck: tuple[MicroduckAdapter, _FakeTransport]) -> None:
    adapter, transport = duck
    adapter.send_navigation_goal(location="stand_up")
    adapter.close()
    assert transport.closed is True
