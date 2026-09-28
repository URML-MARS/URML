"""Hermetic unit tests for ReachyMiniAdapter (RFC-0698 ExpressionAdapter).

A fake ``reachy_mini`` module is injected into ``sys.modules`` so the lazy
client factory resolves against a controllable double. No SDK / hardware
required.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Iterator
from types import ModuleType
from typing import Any

import pytest
from urml_ros2_runtime.substrate.base import ExpressionAdapter


class _FakeReachy:
    def __init__(self, host: str | None = None) -> None:
        self.host = host
        self.calls: list[tuple[str, Any, Any]] = []

    def goto_target(self, *, head: Any, body_yaw: float, duration: float, method: str) -> None:
        self.calls.append(("goto_target", head, {"body_yaw": body_yaw, "duration": duration, "method": method}))

    def wave(self, *args: Any, **kwargs: Any) -> None:
        self.calls.append(("wave", args, kwargs))

    def close(self) -> None:
        pass


@pytest.fixture
def fake_reachy() -> Iterator[None]:
    mod = ModuleType("reachy_mini")
    mod.ReachyMini = _FakeReachy  # type: ignore[attr-defined]
    saved = sys.modules.get("reachy_mini")
    sys.modules["reachy_mini"] = mod
    try:
        yield
    finally:
        if saved is None:
            sys.modules.pop("reachy_mini", None)
        else:
            sys.modules["reachy_mini"] = saved


def test_is_an_expression_adapter(fake_reachy: None) -> None:
    from urml_edu_runtime import ReachyConfig, ReachyMiniAdapter

    with ReachyMiniAdapter(ReachyConfig()) as a:
        assert isinstance(a, ExpressionAdapter)


def test_look_at_direction_orients_head_and_body(fake_reachy: None) -> None:
    from urml_edu_runtime import ReachyConfig, ReachyMiniAdapter

    with ReachyMiniAdapter(ReachyConfig()) as a:
        result = a.orient_gaze(target="direction", yaw=30.0, pitch=10.0, body_yaw=15.0, duration_seconds=0.5)
        assert result.success
        client = a._open()
        method, head, kw = client.calls[0]
        assert method == "goto_target"
        assert len(head) == 4 and len(head[0]) == 4  # 4x4 homogeneous matrix
        assert head[3] == [0.0, 0.0, 0.0, 1.0]
        assert kw["body_yaw"] == pytest.approx(math.radians(15.0))
        assert kw["duration"] == 0.5
        assert kw["method"] == "minjerk"


def test_look_at_non_direction_target_is_not_supported(fake_reachy: None) -> None:
    from urml_edu_runtime import ReachyConfig, ReachyMiniAdapter

    with ReachyMiniAdapter(ReachyConfig()) as a:
        result = a.orient_gaze(target="face")
        assert result.success is False
        assert result.reason is not None and result.reason.startswith("reachy_gaze_target_not_supported")


def test_gesture_dispatches_a_configured_move(fake_reachy: None) -> None:
    from urml_edu_runtime import EduSkillCall, ReachyConfig, ReachyMiniAdapter

    cfg = ReachyConfig(gesture_moves={"greet": EduSkillCall(method="wave", args=["right"])})
    with ReachyMiniAdapter(cfg) as a:
        assert a.perform_gesture(name="greet").success
        client = a._open()
        assert ("wave", ("right",), {}) in client.calls


def test_gesture_unconfigured_is_a_clean_failure(fake_reachy: None) -> None:
    from urml_edu_runtime import ReachyConfig, ReachyMiniAdapter

    with ReachyMiniAdapter(ReachyConfig()) as a:
        result = a.perform_gesture(name="nope")
        assert result.success is False
        assert result.reason is not None and result.reason.startswith("reachy_gesture_not_configured")


def test_gesture_missing_client_method_is_a_clean_failure(fake_reachy: None) -> None:
    from urml_edu_runtime import EduSkillCall, ReachyConfig, ReachyMiniAdapter

    cfg = ReachyConfig(gesture_moves={"greet": EduSkillCall(method="no_such_move")})
    with ReachyMiniAdapter(cfg) as a:
        result = a.perform_gesture(name="greet")
        assert result.success is False
        assert result.reason is not None and result.reason.startswith("reachy_client_missing_method")
