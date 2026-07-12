"""RFC-0667 monitor semantics: the executable form of the spec's evaluation rules.

Each test names the rule it pins. If a change here is not accompanied by a
spec-text change, one of the two is wrong.
"""

from __future__ import annotations

import pytest

from urml_validator.monitor import (
    Entity,
    MonitorError,
    MonitorSemanticsError,
    MonitorSignalError,
    OnlineMonitor,
    Sample,
    compile_envelope_monitors,
    evaluate_trace,
)
from urml_validator.monitorable import parse_property


def _trace(*values: float, signal: str = "speed", dt: float = 1.0) -> list[Sample]:
    return [Sample(t=i * dt, signals={signal: v}) for i, v in enumerate(values)]


def _prop(expression: str, dialect: str = "stl"):
    return parse_property(expression, dialect=dialect)


# ---------------------------------------------------------------------------
# Atoms and boolean connectives
# ---------------------------------------------------------------------------


def test_compare_at_first_sample() -> None:
    assert evaluate_trace(_prop("speed <= 1.0"), _trace(0.5, 9.9))
    assert not evaluate_trace(_prop("speed <= 1.0"), _trace(1.5))


def test_bare_signal_is_truthiness() -> None:
    trace = [Sample(t=0.0, signals={"estop": 0.0}), Sample(t=1.0, signals={"estop": 1.0})]
    assert not evaluate_trace(_prop("estop"), trace)
    assert evaluate_trace(_prop("eventually estop"), trace)


def test_boolean_connectives() -> None:
    trace = _trace(0.5)
    assert evaluate_trace(_prop("speed <= 1.0 and speed >= 0.1"), trace)
    assert evaluate_trace(_prop("speed > 1.0 or speed <= 1.0"), trace)
    assert evaluate_trace(_prop("speed > 1.0 implies false"), trace)
    assert not evaluate_trace(_prop("not (speed <= 1.0)"), trace)
    assert evaluate_trace(_prop("true"), trace)
    assert not evaluate_trace(_prop("false"), trace)


def test_missing_signal_is_an_error_not_false() -> None:
    with pytest.raises(MonitorSignalError, match="person_distance"):
        evaluate_trace(_prop("person_distance > 2.0"), _trace(0.5))


# ---------------------------------------------------------------------------
# Temporal operators, completed-trace semantics
# ---------------------------------------------------------------------------


def test_always_unbounded_over_completed_trace() -> None:
    assert evaluate_trace(_prop("always (speed <= 1.0)"), _trace(0.5, 0.9, 1.0))
    assert not evaluate_trace(_prop("always (speed <= 1.0)"), _trace(0.5, 1.1, 0.5))


def test_eventually_unbounded_requires_a_witness() -> None:
    assert evaluate_trace(_prop("eventually (speed > 1.0)"), _trace(0.5, 1.5))
    assert not evaluate_trace(_prop("eventually (speed > 1.0)"), _trace(0.5, 0.9))


def test_bounded_always_only_constrains_the_window() -> None:
    # Window [0, 1.5]: samples at t=0 and t=1. The violation at t=2 is outside.
    assert evaluate_trace(_prop("always[0, 1.5] (speed <= 1.0)"), _trace(0.5, 0.9, 5.0))
    assert not evaluate_trace(_prop("always[0, 1.5] (speed <= 1.0)"), _trace(0.5, 1.2, 0.1))


def test_bounded_eventually_strong_at_truncation() -> None:
    # Window [0, 10] extends past the trace end; no witness observed -> violated.
    assert not evaluate_trace(_prop("eventually[0, 10] (speed > 1.0)"), _trace(0.5, 0.9))


def test_bounded_window_offset() -> None:
    # Window [2, 3]: only t=2 and t=3 count.
    assert evaluate_trace(_prop("eventually[2, 3] (speed > 1.0)"), _trace(0.1, 0.1, 2.0, 0.1))
    assert not evaluate_trace(_prop("eventually[2, 3] (speed > 1.0)"), _trace(2.0, 0.1, 0.1, 0.1))


def test_until_witness_with_left_hold() -> None:
    # speed stays under 1.0 until docked becomes true.
    trace = [
        Sample(t=0.0, signals={"speed": 0.5, "docked": 0.0}),
        Sample(t=1.0, signals={"speed": 0.8, "docked": 0.0}),
        Sample(t=2.0, signals={"speed": 2.0, "docked": 1.0}),
    ]
    assert evaluate_trace(_prop("speed <= 1.0 until docked"), trace)


def test_until_fails_when_left_breaks_before_witness() -> None:
    trace = [
        Sample(t=0.0, signals={"speed": 0.5, "docked": 0.0}),
        Sample(t=1.0, signals={"speed": 2.0, "docked": 0.0}),
        Sample(t=2.0, signals={"speed": 0.5, "docked": 1.0}),
    ]
    assert not evaluate_trace(_prop("speed <= 1.0 until docked"), trace)


def test_until_fails_without_witness() -> None:
    trace = [
        Sample(t=0.0, signals={"speed": 0.5, "docked": 0.0}),
        Sample(t=1.0, signals={"speed": 0.5, "docked": 0.0}),
    ]
    assert not evaluate_trace(_prop("speed <= 1.0 until docked"), trace)


def test_nested_temporal() -> None:
    # "every sample starts a window in which speed eventually drops under 0.2"
    assert evaluate_trace(
        _prop("always (eventually[0, 2] (speed < 0.2))"),
        _trace(0.5, 0.1, 0.5, 0.1, 0.1),
    )
    assert not evaluate_trace(
        _prop("always (eventually[0, 2] (speed < 0.2))"),
        _trace(0.5, 0.1, 0.5, 0.5, 0.5),
    )


def test_implication_guard_pattern() -> None:
    # The RFC-0382 headline example: slow down whenever a person is near.
    prop = _prop("always ((person_distance < 2.0) implies (speed <= 0.3))")
    near_and_slow = [
        Sample(t=0.0, signals={"speed": 1.0, "person_distance": 5.0}),
        Sample(t=1.0, signals={"speed": 0.2, "person_distance": 1.0}),
    ]
    near_and_fast = [
        Sample(t=0.0, signals={"speed": 1.0, "person_distance": 5.0}),
        Sample(t=1.0, signals={"speed": 1.0, "person_distance": 1.0}),
    ]
    assert evaluate_trace(prop, near_and_slow)
    assert not evaluate_trace(prop, near_and_fast)


# ---------------------------------------------------------------------------
# Spatial operators (stl_strel)
# ---------------------------------------------------------------------------


def _spatial_sample(*entities: Entity) -> Sample:
    return Sample(t=0.0, signals={"speed": 0.5}, entities=entities)


def test_somewhere_quantifies_entities_in_band() -> None:
    prop = _prop("somewhere[0, 2] (person > 0.5)", dialect="stl_strel")
    near_person = _spatial_sample(Entity("p1", 1.0, {"person": 1.0}))
    far_person = _spatial_sample(Entity("p1", 5.0, {"person": 1.0}))
    assert evaluate_trace(prop, [near_person])
    assert not evaluate_trace(prop, [far_person])


def test_everywhere_vacuous_with_empty_band() -> None:
    prop = _prop("everywhere[0, 2] (person > 0.5)", dialect="stl_strel")
    assert evaluate_trace(prop, [_spatial_sample()])
    mixed = _spatial_sample(Entity("p1", 1.0, {"person": 1.0}), Entity("p2", 1.5, {"person": 0.0}))
    assert not evaluate_trace(prop, [mixed])


def test_entity_signals_shadow_ego_then_fall_back() -> None:
    prop = _prop("somewhere[0, 2] (speed > 0.4)", dialect="stl_strel")
    # The entity has no `speed`; the lookup falls back to ego's 0.5.
    assert evaluate_trace(prop, [_spatial_sample(Entity("p1", 1.0))])
    # An entity-scoped `speed` shadows ego's.
    shadowing = _spatial_sample(Entity("p1", 1.0, {"speed": 0.1}))
    assert not evaluate_trace(prop, [shadowing])


def test_surround_annulus_form() -> None:
    prop = _prop("(speed <= 1.0) surround[1, 3] (person > 0.5)", dialect="stl_strel")
    ok = _spatial_sample(Entity("p1", 2.0, {"person": 1.0}))
    bad_entity = _spatial_sample(Entity("p1", 2.0, {"person": 0.0}))
    outside_band = _spatial_sample(Entity("p1", 0.5, {"person": 0.0}))
    assert evaluate_trace(prop, [ok])
    assert not evaluate_trace(prop, [bad_entity])
    assert evaluate_trace(prop, [outside_band]), "entities outside the annulus do not count"


def test_temporal_inside_spatial_rejected() -> None:
    prop = _prop("somewhere[0, 2] (eventually (person > 0.5))", dialect="stl_strel")
    with pytest.raises(MonitorSemanticsError, match="entity identity"):
        evaluate_trace(prop, [_spatial_sample(Entity("p1", 1.0, {"person": 1.0}))])


# ---------------------------------------------------------------------------
# Trace discipline
# ---------------------------------------------------------------------------


def test_empty_trace_rejected() -> None:
    with pytest.raises(MonitorError, match="empty"):
        evaluate_trace(_prop("true"), [])


def test_non_increasing_timestamps_rejected() -> None:
    with pytest.raises(MonitorError, match="strictly increase"):
        evaluate_trace(_prop("true"), [Sample(t=1.0), Sample(t=1.0)])


# ---------------------------------------------------------------------------
# Envelope compilation
# ---------------------------------------------------------------------------


def test_static_caps_derive_always_properties() -> None:
    envelope = {"max_velocity": 1.5, "max_altitude": 50.0}
    compiled = compile_envelope_monitors(envelope)
    names = {c.name for c in compiled}
    assert names == {"envelope.max_velocity", "envelope.max_altitude"}
    assert all(c.severity == "critical" and c.source == "derived" for c in compiled)
    velocity = next(c for c in compiled if c.name == "envelope.max_velocity")
    assert evaluate_trace(velocity.node, _trace(1.0, 1.5))
    assert not evaluate_trace(velocity.node, _trace(1.0, 1.6))


def test_declared_properties_compile_and_custom_skipped() -> None:
    envelope = {
        "monitorable_properties": [
            {"name": "person_slowdown", "severity": "critical", "dialect": "stl",
             "expression": "always ((person_distance < 2.0) implies (speed <= 0.3))"},
            {"name": "vendor_thing", "dialect": "custom", "expression": "OPAQUE(x)"},
        ]
    }
    compiled = compile_envelope_monitors(envelope)
    assert [c.name for c in compiled] == ["person_slowdown"]
    assert compiled[0].source == "declared"


def test_none_envelope_compiles_to_nothing() -> None:
    assert compile_envelope_monitors(None) == []


# ---------------------------------------------------------------------------
# Online monitor: three-valued verdicts + online/offline agreement
# ---------------------------------------------------------------------------


def _online(expression: str) -> OnlineMonitor:
    envelope = {"monitorable_properties": [{"name": "p", "severity": "critical", "expression": expression}]}
    return OnlineMonitor(compile_envelope_monitors(envelope))


def test_unbounded_always_stays_pending_until_violated() -> None:
    monitor = _online("always (speed <= 1.0)")
    (v,) = monitor.observe(Sample(t=0.0, signals={"speed": 0.5}))
    assert v.state == "pending"
    (v,) = monitor.observe(Sample(t=1.0, signals={"speed": 2.0}))
    assert v.state == "violated"
    assert monitor.violations()[0].name == "p"
    # The verdict is final: a recovery does not un-violate.
    (v,) = monitor.observe(Sample(t=2.0, signals={"speed": 0.1}))
    assert v.state == "violated"


def test_bounded_eventually_pending_then_satisfied() -> None:
    monitor = _online("eventually[0, 5] (speed > 1.0)")
    (v,) = monitor.observe(Sample(t=0.0, signals={"speed": 0.5}))
    assert v.state == "pending"
    (v,) = monitor.observe(Sample(t=2.0, signals={"speed": 2.0}))
    assert v.state == "satisfied"


def test_bounded_eventually_violated_once_window_elapses() -> None:
    monitor = _online("eventually[0, 5] (speed > 1.0)")
    monitor.observe(Sample(t=0.0, signals={"speed": 0.5}))
    (v,) = monitor.observe(Sample(t=6.0, signals={"speed": 0.5}))
    assert v.state == "violated"


def test_finalize_collapses_pending_with_completed_semantics() -> None:
    always = _online("always (speed <= 1.0)")
    always.observe(Sample(t=0.0, signals={"speed": 0.5}))
    (v,) = always.finalize()
    assert v.state == "satisfied"

    eventually = _online("eventually (speed > 1.0)")
    eventually.observe(Sample(t=0.0, signals={"speed": 0.5}))
    (v,) = eventually.finalize()
    assert v.state == "violated"


@pytest.mark.parametrize(
    "expression",
    [
        "always (speed <= 1.0)",
        "eventually (speed > 1.0)",
        "eventually[0, 2] (speed > 1.0)",
        "always[0, 2] (speed <= 1.0)",
        "speed <= 1.0 until (speed > 1.5)",
        "always ((speed > 1.0) implies (eventually[0, 2] (speed <= 0.5)))",
    ],
)
@pytest.mark.parametrize(
    "values",
    [
        (0.5, 0.9, 1.2, 0.3, 2.0),
        (0.5, 0.5, 0.5),
        (2.0, 0.1, 1.6, 0.2),
    ],
)
def test_online_offline_agreement(expression: str, values: tuple[float, ...]) -> None:
    """A finalized online run equals the offline verdict, and any non-pending
    verdict reached mid-run already equals it."""
    node = parse_property(expression, dialect="stl")
    trace = _trace(*values)
    offline = evaluate_trace(node, trace)

    monitor = _online(expression)
    mid_verdicts = []
    for sample in trace:
        (v,) = monitor.observe(sample)
        mid_verdicts.append(v.state)
    (final,) = monitor.finalize()

    assert (final.state == "satisfied") == offline
    for state in mid_verdicts:
        if state != "pending":
            assert (state == "satisfied") == offline


def test_observe_after_finalize_rejected() -> None:
    monitor = _online("always (speed <= 1.0)")
    monitor.observe(Sample(t=0.0, signals={"speed": 0.5}))
    monitor.finalize()
    with pytest.raises(MonitorError, match="finalize"):
        monitor.observe(Sample(t=1.0, signals={"speed": 0.5}))


def test_online_rejects_non_increasing_time() -> None:
    monitor = _online("always (speed <= 1.0)")
    monitor.observe(Sample(t=1.0, signals={"speed": 0.5}))
    with pytest.raises(MonitorError, match="strictly increase"):
        monitor.observe(Sample(t=1.0, signals={"speed": 0.5}))
