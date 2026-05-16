"""CompositeAdapter unit tests — hermetic, two MockROSAdapter backends.

No pymavlink, no rclpy. Each test invokes a Protocol method on the
composite and asserts the call landed in the expected backend's
``call_log`` (and not the other). This proves the routing table without
needing either real substrate.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest
from urml_ros2_runtime.substrate import MockROSAdapter
from urml_ros2_runtime.substrate.base import ROSAdapter

from urml_px4_runtime import COMPANION, FLIGHT, CompositeAdapter


@pytest.fixture
def backends() -> tuple[MockROSAdapter, MockROSAdapter]:
    return MockROSAdapter(), MockROSAdapter()


@pytest.fixture
def composite(backends: tuple[MockROSAdapter, MockROSAdapter]) -> CompositeAdapter:
    flight, companion = backends
    return CompositeAdapter(flight=flight, companion=companion)


# (method_name, invoke fn) — invoke fn calls the method on the composite
# with minimal valid args. The expected backend is the default-routing one.
_INVOCATIONS: dict[str, Callable[[CompositeAdapter], Any]] = {
    "send_navigation_goal": lambda c: c.send_navigation_goal(location="kitchen"),
    "send_docking_goal": lambda c: c.send_docking_goal(station="dock", service="park"),
    "send_takeoff_goal": lambda c: c.send_takeoff_goal(altitude=30.0),
    "send_land_goal": lambda c: c.send_land_goal(),
    "send_return_to_home_goal": lambda c: c.send_return_to_home_goal(),
    "wait_passively": lambda c: c.wait_passively(duration_seconds=1.0),
    "send_manipulation_goal": lambda c: c.send_manipulation_goal(action="grasp"),
    "query_detection": lambda c: c.query_detection(object_class="mug"),
    "run_scan": lambda c: c.run_scan(
        area={"named_region": "yard"},
        pattern="serpentine",
        overlap=0.3,
        altitude=None,
        media="photo",
        sensor=None,
    ),
    "take_measurement": lambda c: c.take_measurement(
        what="distance", target=None, sensor=None
    ),
    "capture_media": lambda c: c.capture_media(
        media="photo", target=None, duration_seconds=None, attributes=None
    ),
    "wait_for_condition": lambda c: c.wait_for_condition(
        kind="event", name="x", input_mode=None, threshold=None, timeout_seconds=None
    ),
    "emit_report": lambda c: c.emit_report(
        to="user", facts={}, attachments=None, status="success", severity="info"
    ),
    "emit_speech": lambda c: c.emit_speech(
        utterance="hi", locale=None, style="notice", interrupt=False
    ),
    "acquire_speech": lambda c: c.acquire_speech(
        prompt=None, locale=None, timeout_seconds=None, expected="free_form", choices=None
    ),
}

_EXPECTED_DEFAULT = {
    "send_navigation_goal": FLIGHT,
    "send_docking_goal": FLIGHT,
    "send_takeoff_goal": FLIGHT,
    "send_land_goal": FLIGHT,
    "send_return_to_home_goal": FLIGHT,
    "wait_passively": FLIGHT,
    "send_manipulation_goal": COMPANION,
    "query_detection": COMPANION,
    "run_scan": COMPANION,
    "take_measurement": COMPANION,
    "capture_media": COMPANION,
    "wait_for_condition": COMPANION,
    "emit_report": COMPANION,
    "emit_speech": COMPANION,
    "acquire_speech": COMPANION,
}


def test_all_fifteen_protocol_methods_are_covered() -> None:
    """Guard: the test matrix matches the routing table 1:1 (no method drifts uncovered)."""
    assert set(_INVOCATIONS) == set(_EXPECTED_DEFAULT)
    assert len(_INVOCATIONS) == 15


@pytest.mark.parametrize("method", sorted(_INVOCATIONS))
def test_default_routing_dispatches_to_correct_backend(
    method: str,
    backends: tuple[MockROSAdapter, MockROSAdapter],
    composite: CompositeAdapter,
) -> None:
    flight, companion = backends
    _INVOCATIONS[method](composite)

    expected = _EXPECTED_DEFAULT[method]
    chosen, other = (flight, companion) if expected == FLIGHT else (companion, flight)

    assert chosen.call_log, f"{method} did not reach the {expected} backend"
    assert chosen.call_log[-1]["method"] == method
    assert not other.call_log, f"{method} leaked to the wrong backend"
    assert composite.routing_for(method) == expected


def test_routing_override_remaps_a_method(
    backends: tuple[MockROSAdapter, MockROSAdapter],
) -> None:
    """A drone reading its rangefinder over MAVLink wants measure on flight."""
    flight, companion = backends
    composite = CompositeAdapter(
        flight=flight,
        companion=companion,
        routing={"take_measurement": FLIGHT},
    )
    composite.take_measurement(what="distance", target=None, sensor=None)
    assert flight.call_log[-1]["method"] == "take_measurement"
    assert not companion.call_log
    assert composite.routing_for("take_measurement") == FLIGHT
    # Unrelated methods keep the default.
    assert composite.routing_for("query_detection") == COMPANION


def test_override_unknown_method_rejected(
    backends: tuple[MockROSAdapter, MockROSAdapter],
) -> None:
    flight, companion = backends
    with pytest.raises(ValueError, match="unknown ROSAdapter method"):
        CompositeAdapter(
            flight=flight, companion=companion, routing={"send_warp_drive": FLIGHT}
        )


def test_override_bad_backend_value_rejected(
    backends: tuple[MockROSAdapter, MockROSAdapter],
) -> None:
    flight, companion = backends
    with pytest.raises(ValueError, match="must be 'flight' or 'companion'"):
        CompositeAdapter(
            flight=flight, companion=companion, routing={"query_detection": "satellite"}
        )


def test_routing_for_rejects_non_protocol_name(composite: CompositeAdapter) -> None:
    with pytest.raises(KeyError):
        composite.routing_for("not_a_method")


def test_satisfies_ros_adapter_protocol(composite: CompositeAdapter) -> None:
    """ROSAdapter is @runtime_checkable; the composite must structurally satisfy it."""
    assert isinstance(composite, ROSAdapter)


def test_close_closes_both_backends_exactly_once_even_if_called_twice() -> None:
    closed: list[str] = []

    class _Closable(MockROSAdapter):
        def __init__(self, tag: str) -> None:
            super().__init__()
            self._tag = tag

        def close(self) -> None:
            closed.append(self._tag)

    composite = CompositeAdapter(flight=_Closable("f"), companion=_Closable("c"))
    composite.close()
    composite.close()  # idempotent — second call is a no-op
    assert closed == ["f", "c"]  # each backend closed once, in order


def test_context_manager_closes(backends: tuple[MockROSAdapter, MockROSAdapter]) -> None:
    flight, companion = backends
    with CompositeAdapter(flight=flight, companion=companion) as c:
        c.send_takeoff_goal(altitude=10.0)
    assert flight.call_log[-1]["method"] == "send_takeoff_goal"


def test_backend_without_close_does_not_break_close(
    composite: CompositeAdapter,
) -> None:
    """MockROSAdapter has no close(); CompositeAdapter.close() must not raise."""
    composite.close()  # no exception
