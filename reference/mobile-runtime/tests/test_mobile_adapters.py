"""Hermetic unit tests for the Clearpath AMR adapters — no ROS 2 needed.

A recording fake inner adapter is injected via ``inner_factory`` (the
same technique the industrial-arm / ANYmal / Digit suites use), so the
delegation and not-supported paths are exercised without rclpy.
"""

from __future__ import annotations

from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import (
    ManipulationResult,
    NavigationResult,
    ROSAdapter,
    SubstrateResult,
)

from urml_mobile_runtime import ClearpathAdapter, HuskyAdapter, JackalAdapter, MOBILE_ADAPTERS

BRAND_CLASSES = [HuskyAdapter, JackalAdapter]
BRAND_IDS = [c.BRAND for c in BRAND_CLASSES]


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


def test_registry() -> None:
    assert MOBILE_ADAPTERS == {"husky": HuskyAdapter, "jackal": JackalAdapter}
    assert issubclass(HuskyAdapter, ClearpathAdapter)


@pytest.mark.parametrize("cls", BRAND_CLASSES, ids=BRAND_IDS)
def test_delegates_and_rejects(cls: type[ClearpathAdapter]) -> None:
    inner = _RecordingInner()
    with cls(inner_factory=lambda: inner) as amr:
        assert isinstance(amr, ROSAdapter)
        assert amr.BRAND == cls.BRAND
        assert amr.send_navigation_goal(location="dock_a").success
        assert amr.wait_passively(duration_seconds=0.1).success
        assert amr.take_measurement(what="odom", target=None, sensor=None).success
        assert amr.emit_report(
            to="fleet", facts={}, attachments=None, status="success", severity="info"
        ).success
        bad: ManipulationResult = amr.send_manipulation_goal(action="grasp")
        assert bad.success is False
        assert bad.reason is not None and bad.reason.startswith(f"not_supported_on_amr[{cls.BRAND}]")
        assert amr.send_takeoff_goal(altitude=1.0).success is False
        assert amr.send_docking_goal(station="d", service="charge").success is False
    assert inner.calls == ["send_navigation_goal", "wait_passively", "take_measurement", "emit_report"]
    assert inner.closed is True


def test_conformance_runner_accepts_factory() -> None:
    from urml_conformance import ConformanceRunner

    runner = ConformanceRunner(
        adapter_factory=lambda: HuskyAdapter(inner_factory=lambda: _RecordingInner())
    )
    assert runner is not None
