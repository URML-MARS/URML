"""Schema-to-GBNF derivation for grammar-constrained LLM backends.

`schema_to_gbnf(schema)` walks a JSON Schema Draft 2020-12 document (the
shape `urml_validator.export_schema("program")` produces) and emits a GBNF
grammar that accepts the same JSON value space *structurally*. The grammar
is what `llama-server` (and any future backend with native grammar support)
loads to make malformed URML unrepresentable at the token level.

The schema remains the single source of structural truth. The grammar is a
derivation, not a parallel specification. A grammar-valid emission is still
subject to the full validator: GBNF enforces JSON shape, the validator
enforces semantics.

Supported JSON Schema features
------------------------------
- ``type``: ``object``, ``array``, ``string``, ``number``, ``integer``,
  ``boolean``, ``null``.
- ``properties`` + ``required`` + ``additionalProperties: false`` (closed
  objects; ``additionalProperties: true`` or absent widens to generic JSON).
- ``items`` (homogeneous arrays).
- ``enum`` and ``const`` (literal alternation; the cheapest place to
  exclude invalid emissions).
- ``oneOf`` / ``anyOf`` (alternation, cycle-safe).
- ``$ref`` against ``#/$defs/...`` and ``#/definitions/...`` (recursive
  rules; the program schema's ``Branch -> if_true -> Branch`` cycle is the
  canonical reason this matters).

NOT enforced at the grammar level — these surface via the validator's
revision loop, which is the spec-defined place for them:

- ``pattern``, ``minLength``, ``maxLength``.
- ``minimum``, ``maximum``, ``exclusiveMinimum``, ``exclusiveMaximum``,
  ``multipleOf``.
- Cross-field constraints (``store_as`` uniqueness within scope, ``$ref``
  bindings resolving to a typed producer, etc.).
- Manifest-aware constraints (locations declared, capability present,
  docking services registered, etc.).

This is RFC-0021's design choice, not an oversight: the validator already
owns semantics and is the spec-normative gate; replicating it in GBNF
would double the surface and invite drift.

Determinism + caching
---------------------
``schema_to_gbnf`` is a pure function of its inputs and is cached by a
canonical JSON serialization of the schema. Two calls with the same schema
produce identical grammar text and re-use the cached derivation. The cache
is keyed by content so a validator upgrade that ships a new schema
invalidates automatically.
"""

from __future__ import annotations

import functools
import json
import re
from typing import Any

__all__ = ["GrammarDerivationError", "schema_to_gbnf"]


class GrammarDerivationError(ValueError):
    """Raised when a schema feature is encountered that `schema_to_gbnf` does
    not know how to compile. Listed-but-unsupported features (e.g. ``$ref``
    targets outside ``$defs``/``definitions``) raise this; unlisted features
    (e.g. ``allOf`` with no concrete branch) fall back silently to a generic
    JSON value, since the validator catches the residue."""


# Generic JSON value rules every grammar inherits. Anything the typed walk
# cannot specialize falls back to these.
_PRELUDE = (
    'ws ::= [ \\t\\n]*\n'
    'string ::= "\\"" '
    '( [^"\\\\] | "\\\\" (["\\\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]) )* '
    '"\\""\n'
    'number ::= "-"? ("0" | [1-9] [0-9]*) ("." [0-9]+)? ([eE] [-+]? [0-9]+)?\n'
    'integer ::= "-"? ("0" | [1-9] [0-9]*)\n'
    'boolean ::= "true" | "false"\n'
    'null ::= "null"\n'
    'value ::= object | array | string | number | boolean | null\n'
    'object ::= "{" ws (string ws ":" ws value (ws "," ws string ws ":" ws value)*)? ws "}"\n'
    'array ::= "[" ws (value (ws "," ws value)*)? ws "]"\n'
)

# GBNF rule names accept letters, digits, and "-". Other chars become "-".
_INVALID_RULE_CHAR = re.compile(r"[^a-zA-Z0-9-]")


def schema_to_gbnf(schema: dict[str, Any], *, root: str = "root") -> str:
    """Return a GBNF grammar accepting the JSON value-space of ``schema``.

    The grammar is keyed by content; identical schemas produce identical
    grammar text. The result is safe to feed to llama-server's ``grammar``
    parameter.
    """
    return _build(_canonicalize(schema), root)


def _canonicalize(schema: dict[str, Any]) -> str:
    """Stable JSON form of a schema, used as the cache key."""
    return json.dumps(schema, sort_keys=True, separators=(",", ":"))


@functools.lru_cache(maxsize=128)
def _build(canonical_schema: str, root: str) -> str:
    schema = json.loads(canonical_schema)
    builder = _Builder(schema)
    builder.add_named(root, schema)
    return builder.render()


class _Builder:
    """Accumulates named GBNF rules while walking a JSON Schema."""

    def __init__(self, root_schema: dict[str, Any]) -> None:
        self.rules: dict[str, str] = {}
        self._defs: dict[str, dict[str, Any]] = dict(
            root_schema.get("$defs") or root_schema.get("definitions") or {}
        )
        self._anon_counter = 0

    # -- public ---------------------------------------------------------

    def add_named(self, name: str, schema: dict[str, Any]) -> None:
        """Compile ``schema`` as the right-hand side of a named rule."""
        if name in self.rules:
            return
        # Reserve the name before recursing so self-referential schemas
        # (Branch -> if_true -> Branch) resolve to a back-reference.
        self.rules[name] = ""
        self.rules[name] = self._compile(schema)

    def render(self) -> str:
        """Render the full grammar text. Root first, then alphabetical."""
        lines: list[str] = []
        if "root" in self.rules:
            lines.append(f"root ::= {self.rules['root']}")
        for name in sorted(n for n in self.rules if n != "root"):
            lines.append(f"{name} ::= {self.rules[name]}")
        lines.append(_PRELUDE.rstrip())
        return "\n".join(lines) + "\n"

    # -- compile dispatch -----------------------------------------------

    def _compile(self, schema: dict[str, Any]) -> str:
        if not isinstance(schema, dict):
            return "value"
        if "$ref" in schema:
            return self._ref(schema["$ref"])
        if "const" in schema:
            return _literal(schema["const"])
        if "enum" in schema:
            return " | ".join(_literal(v) for v in schema["enum"])
        if "oneOf" in schema:
            return self._alternation(schema["oneOf"])
        if "anyOf" in schema:
            return self._alternation(schema["anyOf"])
        if "allOf" in schema:
            for branch in schema["allOf"]:
                if isinstance(branch, dict) and (
                    "$ref" in branch or "type" in branch or "properties" in branch
                ):
                    return self._compile(branch)
            return "value"
        t = schema.get("type")
        if isinstance(t, list):
            # Type unions: ["string", "null"] etc. → alternation over typed branches.
            return self._alternation([{"type": typ} for typ in t])
        if t == "object":
            return self._object(schema)
        if t == "array":
            return self._array(schema)
        if t == "string":
            return "string"
        if t == "number":
            return "number"
        if t == "integer":
            return "integer"
        if t == "boolean":
            return "boolean"
        if t == "null":
            return "null"
        return "value"

    # -- compilers ------------------------------------------------------

    def _alternation(self, branches: list[Any]) -> str:
        if not branches:
            return "value"
        rendered = [f"({self._compile(b)})" for b in branches]
        return " | ".join(rendered)

    def _ref(self, ref: str) -> str:
        if ref.startswith("#/$defs/"):
            name = ref[len("#/$defs/") :]
        elif ref.startswith("#/definitions/"):
            name = ref[len("#/definitions/") :]
        else:
            raise GrammarDerivationError(f"unsupported $ref target: {ref!r}")
        target = self._defs.get(name)
        if target is None:
            raise GrammarDerivationError(f"$ref target not found in $defs: {ref!r}")
        rule = _safe_rule_name(name)
        self.add_named(rule, target)
        return rule

    def _object(self, schema: dict[str, Any]) -> str:
        props = schema.get("properties") or {}
        additional = schema.get("additionalProperties", True)
        # Open-ended objects widen to the generic prelude rule.
        if additional is True or (isinstance(additional, dict) and additional):
            return "object"
        if not props:
            return '"{" ws "}"'
        required = set(schema.get("required") or [])
        # Canonical ordering: alphabetical. The LLM emits keys in this order;
        # the validator does not care about key order, so this is a
        # restriction on emission, not on acceptance.
        sorted_keys = sorted(props.keys())
        req_kvs: list[str] = []
        opt_kvs: list[str] = []
        for key in sorted_keys:
            sub_rule = _safe_rule_name(self._anon(f"v-{key}"))
            self.add_named(sub_rule, props[key])
            kv = f'"\\"{key}\\"" ws ":" ws {sub_rule}'
            (req_kvs if key in required else opt_kvs).append(kv)
        return self._object_body(req_kvs, opt_kvs)

    def _array(self, schema: dict[str, Any]) -> str:
        items = schema.get("items")
        if items is None or items is True:
            return "array"
        if items is False:
            return '"[" ws "]"'
        item_rule = _safe_rule_name(self._anon("item"))
        self.add_named(item_rule, items)
        return f'"[" ws ({item_rule} (ws "," ws {item_rule})*)? ws "]"'

    # -- helpers --------------------------------------------------------

    def _object_body(self, req_kvs: list[str], opt_kvs: list[str]) -> str:
        """Render an object body. Required keys appear first in canonical
        order; optional keys each independently elidable, appearing after
        the required keys. This is a deliberate restriction (any-order
        emission is hard to express cleanly in GBNF) and is documented in
        the module docstring."""
        parts: list[str] = ['"{" ws']
        if req_kvs:
            parts.append(req_kvs[0])
            for kv in req_kvs[1:]:
                parts.append('ws "," ws')
                parts.append(kv)
            for kv in opt_kvs:
                parts.append(f'(ws "," ws {kv})?')
        elif opt_kvs:
            # No required keys: optionals are zero-or-more, in the canonical
            # head-then-tail pattern.
            head = opt_kvs[0]
            tail = "".join(f' (ws "," ws {kv})?' for kv in opt_kvs[1:])
            parts.append(f"({head}{tail})?")
        parts.append('ws "}"')
        return " ".join(parts)

    def _anon(self, prefix: str) -> str:
        self._anon_counter += 1
        return f"{prefix}-{self._anon_counter}"


def _safe_rule_name(name: str) -> str:
    """Coerce a JSON-Schema name into a GBNF-safe rule identifier."""
    cleaned = _INVALID_RULE_CHAR.sub("-", name)
    if not cleaned:
        return "anon"
    if not cleaned[0].isalpha():
        cleaned = "r-" + cleaned
    return cleaned[0].lower() + cleaned[1:]


def _literal(value: Any) -> str:
    """Encode a JSON literal as a GBNF string literal.

    Two-level encoding: the inner ``json.dumps`` produces the JSON form
    (``"sequence"``, ``true``, ``42``), and the outer ``json.dumps`` wraps
    that form as a quoted GBNF string with escapes (``"\"sequence\""``,
    ``"true"``, ``"42"``).
    """
    inner: str = json.dumps(value, sort_keys=True)
    outer: str = json.dumps(inner)
    return outer
