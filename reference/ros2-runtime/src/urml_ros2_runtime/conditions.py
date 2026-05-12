"""Condition expression evaluator for ``Branch`` and ``Retry``.

URML's Layer-3 grammar (RFC-0002) names ``Branch.condition`` and
``Retry.until`` as **condition expression strings**. RFC-0002's Unresolved
Questions defer the formal grammar to the eventual Layer-3 RFC. This
evaluator ships a deliberately small but useful subset *now* so the
runtime can execute branches and retry-until-condition programs end to
end. The Layer-3 RFC will likely formalise or extend what's here; if it
takes URML in a different direction, this evaluator is replaceable behind
the same `evaluate(expr, bindings)` signature.

## Supported grammar

  - Boolean literals:  ``true``, ``false``, ``always``, ``never``
  - Numbers:           ``1``, ``1.5``, ``-3``
  - Strings:           ``"red"``, ``'red'``
  - Variable refs:     ``$name``, ``$name.field``, ``$name.field.subfield``
  - Comparisons:       ``==``  ``!=``  ``<``  ``>``  ``<=``  ``>=``
  - Boolean ops:       ``and``, ``or``, ``not``
  - Parentheses:       ``(expr)``

## Examples

    true
    $target_mug
    $target_mug.confidence > 0.8
    $target_mug.attributes.color == "red"
    $found and $target_mug.confidence > 0.5

## Semantics

An unbound ``$name`` evaluates to ``None``, which is *falsy*. This lets
expressions like ``$target_mug`` work as "was a detection bound?" without
extra plumbing. Attribute access on ``None`` returns ``None`` (no
NoneType errors), so ``$missing.field`` is just *falsy*.
"""

from __future__ import annotations

import ast
import re
from typing import Any

from urml_ros2_runtime.errors import ConditionEvalError

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def evaluate(expr: str, bindings: dict[str, Any]) -> bool:
    """Evaluate `expr` to a Python bool against `bindings`.

    Raises:
        ConditionEvalError: The expression uses an unsupported construct
            or is syntactically invalid. The error message names the
            offending construct.
    """
    rewritten = _rewrite_var_refs(expr)
    try:
        tree = ast.parse(rewritten, mode="eval")
    except SyntaxError as exc:
        raise ConditionEvalError(
            f"condition is not a valid expression: {expr!r} -> {exc.msg}"
        ) from exc
    return bool(_safe_eval(tree.body, bindings))


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


# `$name` and `$name.field` are pre-translated to `_v_name` / `_v_name.field`
# so the rewritten expression is valid Python and parse-able with the stdlib.
_VAR_REF_RE = re.compile(r"\$([a-z_][a-z0-9_]*)")


def _rewrite_var_refs(expr: str) -> str:
    return _VAR_REF_RE.sub(r"_v_\1", expr)


# Mapping of bare-name keywords to their values.
_KEYWORDS: dict[str, bool] = {
    "true": True,
    "false": False,
    "always": True,
    "never": False,
    # `None` is reserved for unbound variables (see _resolve_name).
}


# Allowed AST node types. Anything not on this list raises ConditionEvalError.
_ALLOWED_NODES: tuple[type[ast.AST], ...] = (
    ast.BoolOp,
    ast.UnaryOp,
    ast.BinOp,
    ast.Compare,
    ast.Constant,
    ast.Name,
    ast.Attribute,
    ast.Load,
    ast.And,
    ast.Or,
    ast.Not,
    ast.Eq,
    ast.NotEq,
    ast.Lt,
    ast.Gt,
    ast.LtE,
    ast.GtE,
    ast.USub,
    ast.UAdd,
)


def _safe_eval(node: ast.AST, bindings: dict[str, Any]) -> Any:
    if not isinstance(node, _ALLOWED_NODES):
        raise ConditionEvalError(
            f"unsupported expression node: {type(node).__name__!r}"
        )

    if isinstance(node, ast.Constant):
        # Literal numbers, strings, booleans, None.
        return node.value

    if isinstance(node, ast.Name):
        return _resolve_name(node.id, bindings)

    if isinstance(node, ast.Attribute):
        target = _safe_eval(node.value, bindings)
        return _attr(target, node.attr)

    if isinstance(node, ast.UnaryOp):
        operand = _safe_eval(node.operand, bindings)
        if isinstance(node.op, ast.Not):
            return not operand
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.UAdd):
            return +operand
        raise ConditionEvalError(f"unsupported unary op: {type(node.op).__name__!r}")

    if isinstance(node, ast.BoolOp):
        values = [_safe_eval(v, bindings) for v in node.values]
        if isinstance(node.op, ast.And):
            return all(values)
        if isinstance(node.op, ast.Or):
            return any(values)
        raise ConditionEvalError(f"unsupported boolean op: {type(node.op).__name__!r}")

    if isinstance(node, ast.Compare):
        left = _safe_eval(node.left, bindings)
        for op_node, right_node in zip(node.ops, node.comparators, strict=True):
            right = _safe_eval(right_node, bindings)
            if not _apply_compare(op_node, left, right):
                return False
            left = right
        return True

    if isinstance(node, ast.BinOp):
        # Arithmetic is intentionally NOT supported in conditions to keep the
        # surface tight. Anyone needing it should compute in the program
        # and bind the result, then compare.
        raise ConditionEvalError(
            "arithmetic is not allowed in condition expressions; "
            "compute in the program and compare bindings instead"
        )

    raise ConditionEvalError(f"unsupported expression node: {type(node).__name__!r}")


def _apply_compare(op: ast.cmpop, left: Any, right: Any) -> bool:
    if isinstance(op, ast.Eq):
        return bool(left == right)
    if isinstance(op, ast.NotEq):
        return bool(left != right)
    if isinstance(op, ast.Lt):
        return _safe_lt(left, right)
    if isinstance(op, ast.Gt):
        return _safe_lt(right, left)
    if isinstance(op, ast.LtE):
        return _safe_lt(left, right) or left == right
    if isinstance(op, ast.GtE):
        return _safe_lt(right, left) or left == right
    raise ConditionEvalError(f"unsupported comparison op: {type(op).__name__!r}")


def _safe_lt(left: Any, right: Any) -> bool:
    """A '<' that handles None by treating it as falsy/least."""
    if left is None or right is None:
        return False
    try:
        return bool(left < right)
    except TypeError as exc:
        raise ConditionEvalError(
            f"cannot compare {type(left).__name__} and {type(right).__name__}"
        ) from exc


def _resolve_name(name: str, bindings: dict[str, Any]) -> Any:
    if name in _KEYWORDS:
        return _KEYWORDS[name]
    if name.startswith("_v_"):
        var_name = name[len("_v_") :]
        return bindings.get(var_name)
    raise ConditionEvalError(
        f"unknown name {name!r}; only `true`, `false`, `always`, `never`, "
        "and `$variable` references are recognized"
    )


def _attr(target: Any, name: str) -> Any:
    """Dotted access on a binding. Returns None for unresolved chains so a
    missing intermediate field doesn't break a whole expression."""
    if target is None:
        return None
    if isinstance(target, dict):
        return target.get(name)
    return getattr(target, name, None)
