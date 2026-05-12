"""Condition expression evaluator unit tests."""

from __future__ import annotations

import pytest

from urml_ros2_runtime import ConditionEvalError, evaluate_condition

# ---------------------------------------------------------------------------
# Literals and keywords
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("true", True),
        ("false", False),
        ("always", True),
        ("never", False),
        ("1", True),
        ("0", False),
        ("1.5", True),
        ('"x"', True),
        ('""', False),
    ],
)
def test_literal_and_keyword_evaluation(expr: str, expected: bool) -> None:
    assert evaluate_condition(expr, {}) is expected


# ---------------------------------------------------------------------------
# Variable references
# ---------------------------------------------------------------------------


def test_unresolved_variable_is_falsy() -> None:
    assert evaluate_condition("$nope", {}) is False


def test_bound_dict_is_truthy_when_nonempty() -> None:
    assert evaluate_condition("$obj", {"obj": {"x": 1}}) is True


def test_dotted_access_resolves_dict_fields() -> None:
    bindings = {"mug": {"attributes": {"color": "red"}, "confidence": 0.92}}
    assert evaluate_condition("$mug.confidence", bindings) is True
    assert evaluate_condition("$mug.attributes.color == \"red\"", bindings) is True
    assert evaluate_condition("$mug.attributes.color == \"blue\"", bindings) is False


def test_dotted_access_on_missing_field_is_none_falsy() -> None:
    assert evaluate_condition("$mug.nope", {"mug": {"x": 1}}) is False


def test_dotted_access_on_missing_root_is_falsy() -> None:
    assert evaluate_condition("$missing.field.deeper", {}) is False


# ---------------------------------------------------------------------------
# Comparisons
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("$mug.confidence > 0.5", True),
        ("$mug.confidence > 0.95", False),
        ("$mug.confidence >= 0.92", True),
        ("$mug.confidence < 0.95", True),
        ("$mug.confidence <= 0.91", False),
        ("$mug.confidence == 0.92", True),
        ("$mug.confidence != 0.92", False),
    ],
)
def test_numeric_comparisons(expr: str, expected: bool) -> None:
    bindings = {"mug": {"confidence": 0.92}}
    assert evaluate_condition(expr, bindings) is expected


def test_chained_comparison() -> None:
    bindings = {"x": 5}
    assert evaluate_condition("0 < $x < 10", bindings) is True
    assert evaluate_condition("0 < $x < 3", bindings) is False


def test_string_comparison() -> None:
    bindings = {"mug": {"attributes": {"color": "red"}}}
    assert evaluate_condition("$mug.attributes.color == 'red'", bindings) is True
    assert evaluate_condition('$mug.attributes.color != "blue"', bindings) is True


# ---------------------------------------------------------------------------
# Boolean operators
# ---------------------------------------------------------------------------


def test_and_or_not() -> None:
    bindings = {"a": 1, "b": 0}
    assert evaluate_condition("$a and $a", bindings) is True
    assert evaluate_condition("$a and $b", bindings) is False
    assert evaluate_condition("$a or $b", bindings) is True
    assert evaluate_condition("not $b", bindings) is True
    assert evaluate_condition("not (not $a)", bindings) is True
    assert evaluate_condition("$a and not $b", bindings) is True


# ---------------------------------------------------------------------------
# Error paths
# ---------------------------------------------------------------------------


def test_arithmetic_is_disallowed() -> None:
    with pytest.raises(ConditionEvalError, match="arithmetic"):
        evaluate_condition("$x + 1 == 2", {"x": 1})


def test_unknown_bare_name_raises() -> None:
    with pytest.raises(ConditionEvalError, match="unknown name"):
        evaluate_condition("nonsense_name", {})


def test_syntax_error_raises() -> None:
    with pytest.raises(ConditionEvalError, match="not a valid expression"):
        evaluate_condition("$bad ===", {})


def test_function_call_is_unsupported() -> None:
    with pytest.raises(ConditionEvalError, match="unsupported"):
        evaluate_condition('len("foo") > 0', {})


def test_subscription_is_unsupported() -> None:
    with pytest.raises(ConditionEvalError, match="unsupported"):
        evaluate_condition('$bindings["key"]', {"bindings": {"key": 1}})
