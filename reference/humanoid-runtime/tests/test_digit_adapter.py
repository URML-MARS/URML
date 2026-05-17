"""Hermetic unit tests for DigitAdapter — no ROS 2 install required.

DigitAdapter composes RclpyAdapter; rclpy only imports when RclpyAdapter
is constructed. These tests inject a recording fake inner adapter via
the ``inner_factory`` hook (the same technique the industrial-arm and
ANYmal suites use), so the delegation and v0.1 not-supported paths are
exercised against a controllable double.
"""

from __future__ import annotations

from typing import Any

from urml_ros2_runtime.substrate.base import (
    ManipulationResult,
    NavigationResult,
    ROSAdapter,
    SubstrateResult,
)

from urml_humanoid_runtime import DigitAdapter, HUMANOID_ADAPTERS


class _RecordingInner:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.closed = False

    def send_navigation_goal(self, **kw: Any) -> NavigationResult:
        self.calls.append("send_navigation_goal")
        return NavigationResult(success=True, frame="map")

    def take_measurement(self, **kw: Any) -> SubstrateResult:
        self.calls.append("take_measurement")
        return SubstrateResult(success=True)

    def wait_for_condition(self, **kw: Any) -> SubstrateResult:
        self.calls.append("wait_for_condition")
        return SubstrateResult(success=True)

    def wait_passively(self, **kw: Any) -> SubstrateResult:
        self.calls.append("wait_passively")
        return SubstrateResult(success=True)

    def emit_report(self, **kw: Any) -> SubstrateResult:
        self.calls.append("emit_report")
        return SubstrateResult(success=True)

    def close(self) -> None:
        self.closed = True


def test_registry_exposes_digit() -> None:
    assert HUMANOID_ADAPTERS == {"digit": DigitAdapter}
    assert DigitAdapter.BRAND == "digit"


def test_locomotion_subset_delegates() -> None:
    inner = _RecordingInner()
    with DigitAdapter(inner_factory=lambda: inner) as digit:
        assert isinstance(digit, ROSAdapter)
        assert digit.send_navigation_goal(location="staging_a").success
        assert digit.wait_passively(duration_seconds=0.1).success
        assert digit.take_measurement(what="imu", target=None, sensor=None).success
        assert digit.wait_for_condition(
            kind="signal", name="line_ready", input_mode=None, threshold=None, timeout_seconds=1.0
        ).success
        assert digit.emit_report(
            to="wms", facts={"tote": 7}, attachments=None, status="success", severity="info"
        ).success
    assert inner.calls == [
        "send_navigation_goal",
        "wait_passively",
        "take_measurement",
        "wait_for_condition",
        "emit_report",
    ]
    assert inner.closed is True


def test_non_locomotion_returns_v01_sentinel() -> None:
    inner = _RecordingInner()
    digit = DigitAdapter(inner_factory=lambda: inner)
    tag = "not_supported_on_humanoid[digit]"
    grip: ManipulationResult = digit.send_manipulation_goal(action="grasp")
    results = [
        grip,
        digit.send_docking_goal(station="d", service="park"),
        digit.query_detection(object_class="tote"),
        digit.run_scan(area={}, pattern="grid", overlap=0.1, altitude=None, media="photo", sensor=None),
        digit.capture_media(media="photo", target=None, duration_seconds=None, attributes=None),
        digit.emit_speech(utterance="hi", locale=None, style="notice", interrupt=False),
        digit.acquire_speech(prompt=None, locale=None, timeout_seconds=None, expected="free_form", choices=None),
        digit.send_takeoff_goal(altitude=1.0),
        digit.send_land_goal(),
        digit.send_return_to_home_goal(),
    ]
    for r in results:
        assert r.success is False
        assert r.reason is not None and r.reason.startswith(tag)
    assert inner.calls == []  # rejected paths never reach the composed adapter


def test_conformance_runner_accepts_digit_factory() -> None:
    from urml_conformance import ConformanceRunner

    runner = ConformanceRunner(
        adapter_factory=lambda: DigitAdapter(inner_factory=lambda: _RecordingInner())
    )
    assert runner is not None
