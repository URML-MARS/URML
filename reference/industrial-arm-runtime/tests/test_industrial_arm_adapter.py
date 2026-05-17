"""Hermetic unit tests for the industrial-arm brand adapters.

No ROS 2 install required. The brand adapters compose a RclpyAdapter,
but RclpyAdapter only imports rclpy when *it* is constructed. These
tests bypass that entirely via the ``inner_factory`` hook: a recording
fake stands in for the composed adapter, so every wrapper code path
(delegation + the not-supported sentinels) is exercised against a
controllable double. Real ROS 2 / MoveIt 2 behavior is covered
separately by the gated integration workflow.
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

from urml_industrial_arm_runtime import (
    AbbAdapter,
    FanucAdapter,
    IndustrialArmAdapter,
    KukaAdapter,
    YaskawaAdapter,
)

BRAND_CLASSES = [AbbAdapter, FanucAdapter, KukaAdapter, YaskawaAdapter]
BRAND_IDS = [c.BRAND for c in BRAND_CLASSES]


class _RecordingInner:
    """Records delegated calls; returns recognizable success results."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []
        self.closed = False

    def send_navigation_goal(self, **kw: Any) -> NavigationResult:
        self.calls.append(("send_navigation_goal", kw))
        return NavigationResult(success=True, final_pose={"x": 1.0}, frame="world")

    def send_manipulation_goal(self, **kw: Any) -> ManipulationResult:
        self.calls.append(("send_manipulation_goal", kw))
        return ManipulationResult(success=True, grip_force_n=12.5)

    def take_measurement(self, **kw: Any) -> SubstrateResult:
        self.calls.append(("take_measurement", kw))
        return SubstrateResult(success=True)

    def wait_for_condition(self, **kw: Any) -> SubstrateResult:
        self.calls.append(("wait_for_condition", kw))
        return SubstrateResult(success=True)

    def wait_passively(self, **kw: Any) -> SubstrateResult:
        self.calls.append(("wait_passively", kw))
        return SubstrateResult(success=True)

    def emit_report(self, **kw: Any) -> SubstrateResult:
        self.calls.append(("emit_report", kw))
        return SubstrateResult(success=True)

    def close(self) -> None:
        self.closed = True


def _make(cls: type[IndustrialArmAdapter]) -> tuple[IndustrialArmAdapter, _RecordingInner]:
    inner = _RecordingInner()
    adapter = cls(inner_factory=lambda: inner)
    return adapter, inner


@pytest.mark.parametrize("cls", BRAND_CLASSES, ids=BRAND_IDS)
def test_brand_tag_and_default_config(cls: type[IndustrialArmAdapter]) -> None:
    adapter, _ = _make(cls)
    assert adapter.BRAND == cls.BRAND
    cfg = cls.default_config()
    # MoveIt 2 vanilla move-group, and a brand-keyed gripper server.
    assert cfg.action_servers.move_group == "/move_action"
    assert f"{cls.BRAND}_gripper" in cfg.action_servers.gripper


@pytest.mark.parametrize("cls", BRAND_CLASSES, ids=BRAND_IDS)
def test_supported_primitives_delegate(cls: type[IndustrialArmAdapter]) -> None:
    adapter, inner = _make(cls)

    grip = adapter.send_manipulation_goal(action="grasp", force_n=10.0)
    assert grip.success and grip.grip_force_n == 12.5

    move = adapter.send_navigation_goal(location="fixture_a")
    assert move.success and move.frame == "world"

    assert adapter.wait_passively(duration_seconds=0.1).success
    assert adapter.take_measurement(what="joint_state", target=None, sensor=None).success
    assert adapter.emit_report(
        to="cell_log", facts={"ok": True}, attachments=None, status="success", severity="info"
    ).success

    delegated = [name for name, _ in inner.calls]
    assert delegated == [
        "send_manipulation_goal",
        "send_navigation_goal",
        "wait_passively",
        "take_measurement",
        "emit_report",
    ]


@pytest.mark.parametrize("cls", BRAND_CLASSES, ids=BRAND_IDS)
def test_unsupported_primitives_return_branded_sentinel(cls: type[IndustrialArmAdapter]) -> None:
    adapter, inner = _make(cls)
    tag = f"not_supported_on_industrial_arm[{cls.BRAND}]"

    results = [
        adapter.send_docking_goal(station="d1", service="park"),
        adapter.query_detection(object_class="widget"),
        adapter.run_scan(area={}, pattern="grid", overlap=0.1, altitude=None, media="photo", sensor=None),
        adapter.capture_media(media="photo", target=None, duration_seconds=None, attributes=None),
        adapter.emit_speech(utterance="hi", locale=None, style="notice", interrupt=False),
        adapter.acquire_speech(
            prompt=None, locale=None, timeout_seconds=None, expected="free_form", choices=None
        ),
        adapter.send_takeoff_goal(altitude=5.0),
        adapter.send_land_goal(),
        adapter.send_return_to_home_goal(),
    ]
    for r in results:
        assert r.success is False
        assert r.reason is not None and r.reason.startswith(tag)
    # Not-supported paths must never reach the composed adapter.
    assert inner.calls == []


@pytest.mark.parametrize("cls", BRAND_CLASSES, ids=BRAND_IDS)
def test_is_a_ros_adapter_and_closes(cls: type[IndustrialArmAdapter]) -> None:
    adapter, inner = _make(cls)
    # runtime_checkable Protocol conformance.
    assert isinstance(adapter, ROSAdapter)
    with adapter as a:
        assert a is adapter
    assert inner.closed is True


def test_conformance_runner_accepts_brand_factory() -> None:
    """The ConformanceRunner accepts an industrial-arm adapter factory."""
    from urml_conformance import ConformanceRunner

    runner = ConformanceRunner(
        adapter_factory=lambda: AbbAdapter(inner_factory=lambda: _RecordingInner())
    )
    assert runner is not None
