"""Binding-resolver unit tests."""

from __future__ import annotations

import pytest

from urml_ros2_runtime import (
    UnresolvedReferenceError,
    resolve_reference,
    resolve_references,
)

# ---------------------------------------------------------------------------
# Literals pass through
# ---------------------------------------------------------------------------


def test_non_ref_string_returned_as_is() -> None:
    assert resolve_reference("kitchen", {}) == "kitchen"


def test_non_string_returned_as_is() -> None:
    assert resolve_reference(42, {}) == 42
    assert resolve_reference(None, {}) is None
    assert resolve_reference(True, {}) is True


def test_string_with_dollar_not_in_first_position_is_a_literal() -> None:
    """Only a leading `$` triggers reference resolution."""
    assert resolve_reference("price_$5", {}) == "price_$5"


# ---------------------------------------------------------------------------
# Simple $name resolution
# ---------------------------------------------------------------------------


def test_simple_ref_returns_bound_value() -> None:
    bindings = {"mug": {"class": "mug", "pose": {"x": 1.0}}}
    out = resolve_reference("$mug", bindings)
    assert out == {"class": "mug", "pose": {"x": 1.0}}


def test_unbound_ref_raises() -> None:
    with pytest.raises(UnresolvedReferenceError) as excinfo:
        resolve_reference("$missing", {"other": 1})
    assert excinfo.value.reference == "$missing"
    assert excinfo.value.bound_names == ["other"]


# ---------------------------------------------------------------------------
# Dotted access
# ---------------------------------------------------------------------------


def test_dotted_access_on_dict() -> None:
    bindings = {"mug": {"attributes": {"color": "red"}, "confidence": 0.9}}
    assert resolve_reference("$mug.attributes", bindings) == {"color": "red"}
    assert resolve_reference("$mug.attributes.color", bindings) == "red"
    assert resolve_reference("$mug.confidence", bindings) == 0.9


def test_dotted_access_missing_intermediate_raises() -> None:
    bindings = {"mug": {"attributes": {"color": "red"}}}
    with pytest.raises(UnresolvedReferenceError, match="no field 'size'"):
        resolve_reference("$mug.attributes.size", bindings)


def test_dotted_access_missing_root_field_raises() -> None:
    bindings = {"mug": {"pose": {"x": 1.0}}}
    with pytest.raises(UnresolvedReferenceError, match="no field 'attributes'"):
        resolve_reference("$mug.attributes.color", bindings)


# ---------------------------------------------------------------------------
# Pydantic-style attribute access
# ---------------------------------------------------------------------------


def test_dotted_access_falls_back_to_attribute() -> None:
    """If the bound value isn't a dict, we use attribute access."""

    class _Stub:
        def __init__(self) -> None:
            self.value = 7

    bindings = {"obj": _Stub()}
    assert resolve_reference("$obj.value", bindings) == 7


# ---------------------------------------------------------------------------
# resolve_references (recursive)
# ---------------------------------------------------------------------------


def test_resolve_all_walks_list() -> None:
    bindings = {"a": "alpha", "b": "beta"}
    out = resolve_references(["$a", "$b", "literal"], bindings)
    assert out == ["alpha", "beta", "literal"]


def test_resolve_all_walks_dict_values() -> None:
    bindings = {"mug": {"class": "mug"}}
    out = resolve_references(
        {"target": "$mug", "label": "fixed", "nested": {"obj": "$mug"}},
        bindings,
    )
    assert out == {
        "target": {"class": "mug"},
        "label": "fixed",
        "nested": {"obj": {"class": "mug"}},
    }


def test_resolve_all_does_not_recurse_into_resolved_values() -> None:
    """If a binding contains $refs as data, we don't re-resolve them.

    The validator vets the program's surface; bound values are opaque data.
    """
    bindings = {"obj": {"sub": "$something_inside"}}
    out = resolve_references({"target": "$obj"}, bindings)
    # The sub-string `$something_inside` is preserved verbatim — not treated
    # as a new ref.
    assert out == {"target": {"sub": "$something_inside"}}


def test_resolve_all_propagates_unresolved_error() -> None:
    with pytest.raises(UnresolvedReferenceError):
        resolve_references({"attachments": ["$missing"]}, {"other": 1})


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_lone_dollar_sign_raises() -> None:
    with pytest.raises(UnresolvedReferenceError):
        resolve_reference("$", {})


def test_ref_with_empty_field_segment_raises() -> None:
    """`$mug.` (trailing dot) is ill-formed; the validator catches this
    statically, but the runtime fails loudly if it slips through."""
    with pytest.raises(UnresolvedReferenceError):
        resolve_reference("$mug.", {"mug": {"x": 1}})
