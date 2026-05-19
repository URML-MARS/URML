"""Hermetic unit tests for EmbeddedAdapter — no pyserial install needed.

A fake ``serial`` module is injected into ``sys.modules`` so
``_require_pyserial`` resolves and ``_open`` runs against a
controllable loopback double (the technique px4/marine/opcua use).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import DetectionResult, ROSAdapter


class _FakePort:
    def __init__(self) -> None:
        self.written: list[bytes] = []
        self.closed = False

    def write(self, data: bytes) -> int:
        self.written.append(data)
        return len(data)

    def readline(self) -> bytes:
        return b"21.5\n"

    def close(self) -> None:
        self.closed = True


class _FakeSerial(ModuleType):
    def __init__(self) -> None:
        super().__init__("serial")
        self.last_port: _FakePort | None = None

        def serial_for_url(url: str, baudrate: int = 115200, timeout: float = 2.0) -> _FakePort:
            p = _FakePort()
            self.last_port = p
            return p

        self.serial_for_url = serial_for_url  # type: ignore[attr-defined]


@pytest.fixture
def fake_serial() -> Iterator[_FakeSerial]:
    fake = _FakeSerial()
    saved = sys.modules.get("serial")
    sys.modules["serial"] = fake
    try:
        yield fake
    finally:
        if saved is None:
            sys.modules.pop("serial", None)
        else:
            sys.modules["serial"] = saved


def test_buggy_lifecycle(fake_serial: _FakeSerial) -> None:
    from urml_embedded_runtime import EmbeddedAdapter, EmbeddedConfig

    cfg = EmbeddedConfig(
        location_to_command={"waypoint_a": "GO A", "dock": "HOME"},
        manipulation_commands={"grasp": "CLAW C", "release": "CLAW O"},
    )
    with EmbeddedAdapter(cfg) as buggy:
        assert isinstance(buggy, ROSAdapter)
        ok = buggy.send_navigation_goal(location="waypoint_a")
        assert ok.success
        assert fake_serial.last_port is not None and fake_serial.last_port.written[0] == b"GO A\n"
        miss = buggy.send_navigation_goal(location="nowhere")
        assert miss.success is False and miss.reason is not None
        assert miss.reason.startswith("location_not_configured")
        assert buggy.send_manipulation_goal(action="grasp").success
        meas = buggy.take_measurement(what="light", target=None, sensor=None)
        assert meas.success and meas.payload is not None and meas.payload["value"] == 21.5
        assert buggy.wait_passively(duration_seconds=0.1).success
        assert buggy.run_scan(
            area={}, pattern="grid", overlap=0.1, altitude=None, media="sensor_only", sensor=None
        ).success


def test_unsupported_and_not_applicable_sentinels(fake_serial: _FakeSerial) -> None:
    from urml_embedded_runtime import EmbeddedAdapter

    buggy = EmbeddedAdapter()
    det: DetectionResult = buggy.query_detection(object_class="ball")
    assert det.success is False and det.reason is not None
    assert det.reason.startswith("not_supported_on_mcu")
    nores = buggy.send_manipulation_goal(action="grasp")
    assert nores.success is False and nores.reason is not None
    assert nores.reason.startswith("manipulation_command_not_configured")
    for r in (buggy.send_takeoff_goal(altitude=1.0), buggy.send_land_goal(), buggy.send_return_to_home_goal()):
        assert r.success is False
        assert r.reason is not None and r.reason.startswith("not_applicable_mcu")


def test_missing_pyserial_is_actionable(monkeypatch: pytest.MonkeyPatch) -> None:
    """Construction without the [serial] extra raises a clear error.

    Setting the sys.modules entry to None forces ``import serial`` to
    raise ImportError deterministically, whether or not pyserial is
    actually installed in the test environment.
    """
    from urml_embedded_runtime import EmbeddedAdapter

    monkeypatch.setitem(sys.modules, "serial", None)
    with pytest.raises(RuntimeError, match=r"\[serial\] extra"):
        EmbeddedAdapter()


def test_conformance_runner_accepts_factory(fake_serial: _FakeSerial) -> None:
    from urml_conformance import ConformanceRunner

    from urml_embedded_runtime import EmbeddedAdapter

    assert ConformanceRunner(adapter_factory=lambda: EmbeddedAdapter()) is not None
