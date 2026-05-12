r"""Variable-binding resolution for primitive arguments.

The runtime walks a URML program's bindings as it executes (each
`store_as` adds an entry). Primitive arguments can reference those
bindings via `$name`, `$name.field`, `$name.field.subfield`. This module
turns those reference strings into concrete values just before the
adapter is called, so the adapter only ever sees resolved data — no
URML syntax leaks across the substrate boundary.

## Resolution rules

- A string that doesn't start with `$` is a literal; returned as-is.
- A string of the form `$name` resolves to ``bindings[name]``.
- A dotted form `$name.field.subfield` walks the bound value via dict
  key access or attribute lookup. Missing intermediates raise
  ``UnresolvedReferenceError`` — at runtime, missing fields are bugs;
  the validator's static binding pass should have caught them.
- ``resolve_all`` recurses through lists and dicts so refs nested in
  structured args (e.g., ``report.attachments: [\$photo1, \$photo2]`` or
  ``report.facts: {target: \$mug}``) are resolved transparently. Recursion
  does NOT cross the boundary into bound values themselves — once a
  value is resolved, it's treated as opaque data.
"""

from __future__ import annotations

from typing import Any

from urml_ros2_runtime.errors import UnresolvedReferenceError

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def resolve(value: Any, bindings: dict[str, Any]) -> Any:
    """Resolve `$ref` strings in `value` against `bindings`.

    Strings starting with ``$`` are interpreted as reference expressions.
    All other types (numbers, bools, None) pass through unchanged. To
    recurse into lists and dicts, use :func:`resolve_all`.
    """
    if not isinstance(value, str):
        return value
    if not value.startswith("$"):
        return value
    return _resolve_ref(value, bindings)


def resolve_all(value: Any, bindings: dict[str, Any]) -> Any:
    """Like :func:`resolve` but recurses into lists and dicts.

    Useful for primitive arg fields whose schema accepts structured
    values (lists of refs, dicts whose values may be refs).
    """
    if isinstance(value, list):
        return [resolve_all(item, bindings) for item in value]
    if isinstance(value, dict):
        return {key: resolve_all(item, bindings) for key, item in value.items()}
    return resolve(value, bindings)


# ---------------------------------------------------------------------------
# Internals
# ---------------------------------------------------------------------------


def _resolve_ref(ref: str, bindings: dict[str, Any]) -> Any:
    if len(ref) < 2:
        raise UnresolvedReferenceError(
            f"empty reference {ref!r}",
            reference=ref,
            bound_names=sorted(bindings.keys()),
        )
    parts = ref[1:].split(".")
    name = parts[0]
    if name not in bindings:
        raise UnresolvedReferenceError(
            f"unbound reference {ref!r}; known bindings: {sorted(bindings.keys())!r}",
            reference=ref,
            bound_names=sorted(bindings.keys()),
        )
    current: Any = bindings[name]
    consumed = "$" + name
    for attr in parts[1:]:
        next_value = _step(current, attr)
        if next_value is _MISSING:
            raise UnresolvedReferenceError(
                f"reference {ref!r} could not be resolved beyond {consumed!r}: "
                f"no field {attr!r} on the bound value",
                reference=ref,
                bound_names=sorted(bindings.keys()),
            )
        current = next_value
        consumed = f"{consumed}.{attr}"
    return current


_MISSING = object()


def _step(value: Any, attr: str) -> Any:
    """One field access. Returns _MISSING if the field doesn't exist; supports
    dict-key access and (defensively) attribute access on pydantic models.
    """
    if isinstance(value, dict):
        if attr in value:
            return value[attr]
        return _MISSING
    # Defensive: pydantic models expose fields as attributes.
    sentinel = object()
    got = getattr(value, attr, sentinel)
    if got is sentinel:
        return _MISSING
    return got
