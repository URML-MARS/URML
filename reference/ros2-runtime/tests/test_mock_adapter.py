"""MockROSAdapter unit tests.

Confirms that:
- Every method records into call_log.
- Sensible defaults cover the happy path with no setup.
- set_* overrides take precedence over defaults and are honored.
"""

from __future__ import annotations

from urml_ros2_runtime.substrate import (
    DetectionResult,
    MockROSAdapter,
    NavigationResult,
    SubstrateResult,
)


def test_navigation_records_call_and_defaults_success() -> None:
    adapter = MockROSAdapter()
    result = adapter.send_navigation_goal(location="kitchen")
    assert result.success is True
    assert len(adapter.call_log) == 1
    entry = adapter.call_log[0]
    assert entry["method"] == "send_navigation_goal"
    assert entry["location"] == "kitchen"


def test_detection_default_returns_a_payload() -> None:
    adapter = MockROSAdapter()
    out = adapter.query_detection(object_class="mug", attributes={"color": "red"})
    assert out.success is True
    assert out.payload is not None
    assert out.payload["class"] == "mug"
    assert out.payload["attributes"] == {"color": "red"}


def test_navigation_override_takes_precedence() -> None:
    adapter = MockROSAdapter()
    adapter.set_navigation_result(NavigationResult(success=False, reason="path_blocked"))
    result = adapter.send_navigation_goal(location="kitchen")
    assert result.success is False
    assert result.reason == "path_blocked"


def test_detection_override_can_signal_not_found() -> None:
    adapter = MockROSAdapter()
    adapter.set_detection_result(DetectionResult(success=False, reason="not_found", payload=None))
    out = adapter.query_detection(object_class="mug")
    assert out.success is False
    assert out.payload is None


def test_report_records_with_attachments() -> None:
    adapter = MockROSAdapter()
    res = adapter.emit_report(
        to="user",
        facts={"message": "done"},
        attachments=["$photo1"],
        status="success",
        severity="info",
    )
    assert res.success is True
    assert adapter.call_log[-1]["attachments"] == ["$photo1"]


def test_wait_passively_records_duration() -> None:
    adapter = MockROSAdapter()
    out = adapter.wait_passively(duration_seconds=2.5)
    assert isinstance(out, SubstrateResult)
    assert out.success is True
    assert adapter.call_log[-1]["duration_seconds"] == 2.5


# ---------------------------------------------------------------------------
# Drone-profile methods
# ---------------------------------------------------------------------------


def test_takeoff_records_call_and_returns_altitude() -> None:
    adapter = MockROSAdapter()
    result = adapter.send_takeoff_goal(altitude=30.0)
    assert result.success is True
    assert result.final_pose == {"x": 0.0, "y": 0.0, "z": 30.0}
    assert result.frame == "agl"
    assert adapter.call_log[-1] == {
        "method": "send_takeoff_goal",
        "altitude": 30.0,
        "climb_rate": None,
    }


def test_land_records_call() -> None:
    adapter = MockROSAdapter()
    result = adapter.send_land_goal(at="home", precision="precise")
    assert result.success is True
    entry = adapter.call_log[-1]
    assert entry["method"] == "send_land_goal"
    assert entry["at"] == "home"
    assert entry["precision"] == "precise"


def test_return_to_home_records_call() -> None:
    adapter = MockROSAdapter()
    result = adapter.send_return_to_home_goal(speed=5.0, altitude=40.0)
    assert result.success is True
    entry = adapter.call_log[-1]
    assert entry["method"] == "send_return_to_home_goal"
    assert entry["speed"] == 5.0
    assert entry["altitude"] == 40.0


def test_takeoff_override_takes_precedence() -> None:
    adapter = MockROSAdapter()
    adapter.set_takeoff_result(NavigationResult(success=False, reason="weather_violation"))
    result = adapter.send_takeoff_goal(altitude=30.0)
    assert result.success is False
    assert result.reason == "weather_violation"
