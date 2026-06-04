"""RFC-0382: the temporal-logic core parser, signal extraction, STL compile."""

from __future__ import annotations

import pytest

from urml_validator.monitorable import (
    Binary,
    BoolOp,
    Compare,
    MonitorableParseError,
    Temporal,
    compile_to_stl,
    parse_property,
    referenced_signals,
    referenced_signals_custom,
)


def test_simple_comparison() -> None:
    node = parse_property("speed <= 0.3", dialect="stl")
    assert isinstance(node, Compare)
    assert node.left == "speed" and node.op == "<=" and node.right == 0.3
    assert referenced_signals(node) == {"speed"}


def test_always_implies_bounded_eventually() -> None:
    node = parse_property(
        "always (stop_requested implies eventually[0, 0.5] (speed == 0))", dialect="stl"
    )
    assert isinstance(node, Temporal) and node.op == "always"
    inner = node.operand
    assert isinstance(inner, BoolOp) and inner.op == "implies"
    assert referenced_signals(node) == {"stop_requested", "speed"}


def test_slow_near_people_signals() -> None:
    node = parse_property("always (person_distance < 2.0 implies speed <= 0.3)", dialect="stl")
    assert referenced_signals(node) == {"person_distance", "speed"}


def test_until_parses() -> None:
    node = parse_property("charging until (battery > 80)", dialect="stl")
    assert isinstance(node, Binary) and node.op == "until"
    assert referenced_signals(node) == {"charging", "battery"}


def test_compile_to_stl_shapes() -> None:
    assert compile_to_stl(parse_property("speed <= 0.3", dialect="stl")) == "(speed <= 0.3)"
    assert compile_to_stl(parse_property("always speed <= 0.3", dialect="stl")) == "G (speed <= 0.3)"
    assert (
        compile_to_stl(parse_property("eventually[0, 0.5] (speed == 0)", dialect="stl"))
        == "F[0, 0.5] (speed == 0)"
    )
    out = compile_to_stl(parse_property("a implies b", dialect="stl"))
    assert out == "(a -> b)"


@pytest.mark.parametrize(
    "expr",
    [
        "always (",            # unterminated paren
        "speed <=",            # dangling comparison
        "speed <= 0.3 0.4",    # trailing token
        "eventually[2, 1] x",  # inverted bound
        "5",                   # bare number is not a boolean atom
        "",                    # empty
        "always and speed",    # keyword where a signal/number is expected
    ],
)
def test_malformed_rejected(expr: str) -> None:
    with pytest.raises(MonitorableParseError):
        parse_property(expr, dialect="stl")


def test_spatial_rejected_under_stl_but_ok_under_strel() -> None:
    with pytest.raises(MonitorableParseError):
        parse_property("somewhere (person_distance < 1.0)", dialect="stl")
    node = parse_property("somewhere (person_distance < 1.0)", dialect="stl_strel")
    assert referenced_signals(node) == {"person_distance"}


def test_spatial_has_no_stl_compile() -> None:
    node = parse_property("somewhere (x < 1.0)", dialect="stl_strel")
    with pytest.raises(NotImplementedError):
        compile_to_stl(node)


def test_custom_signal_extraction_skips_keywords() -> None:
    sigs = referenced_signals_custom("always (foo < 3 and bar) implies baz")
    assert sigs == {"foo", "bar", "baz"}
