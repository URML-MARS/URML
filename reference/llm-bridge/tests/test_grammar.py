"""Schema-to-GBNF derivation tests.

Hermetic: no llama.cpp, no model, no network. The tests exercise the
compiler on hand-rolled schemas (so the assertions name the exact
features), plus one round-trip against the real URML program schema
(so the regression net catches schema-evolution drift).
"""

from __future__ import annotations

import pytest
from urml_validator import export_schema

from urml_llm_bridge.grammar import GrammarDerivationError, schema_to_gbnf


def test_string_type_emits_string_rule() -> None:
    gbnf = schema_to_gbnf({"type": "string"})
    assert "root ::= string" in gbnf
    # Prelude rules are always appended.
    assert "string ::=" in gbnf


def test_integer_and_number_and_boolean_and_null() -> None:
    for typ in ("integer", "number", "boolean", "null"):
        gbnf = schema_to_gbnf({"type": typ})
        assert f"root ::= {typ}" in gbnf, gbnf


def test_enum_becomes_literal_alternation() -> None:
    gbnf = schema_to_gbnf({"enum": ["abort_and_report", "continue", "retry"]})
    # The three string literals must appear as quoted GBNF strings.
    assert '"\\"abort_and_report\\""' in gbnf
    assert '"\\"continue\\""' in gbnf
    assert '"\\"retry\\""' in gbnf
    # Joined by " | ".
    assert " | " in gbnf.splitlines()[0]


def test_const_becomes_single_literal() -> None:
    gbnf = schema_to_gbnf({"const": "sequence"})
    assert '"\\"sequence\\""' in gbnf
    assert " | " not in gbnf.splitlines()[0]


def test_one_of_renders_as_alternation() -> None:
    gbnf = schema_to_gbnf(
        {"oneOf": [{"type": "string"}, {"type": "integer"}, {"type": "boolean"}]}
    )
    root = gbnf.splitlines()[0]
    assert root.startswith("root ::= ")
    # Three alternatives.
    assert root.count("|") == 2


def test_any_of_renders_as_alternation() -> None:
    gbnf = schema_to_gbnf({"anyOf": [{"type": "string"}, {"type": "null"}]})
    root = gbnf.splitlines()[0]
    assert root.count("|") == 1


def test_closed_object_with_one_required_property() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {"location": {"type": "string"}},
        "required": ["location"],
    }
    gbnf = schema_to_gbnf(schema)
    # The key string literal appears verbatim.
    assert '"\\"location\\""' in gbnf
    # The closed object emits explicit braces, not the generic ``object`` rule.
    assert '"{" ws' in gbnf
    assert 'ws "}"' in gbnf


def test_open_object_widens_to_generic_object() -> None:
    """``additionalProperties: True`` (or omitted) means any-shape object."""
    gbnf = schema_to_gbnf({"type": "object"})
    assert "root ::= object" in gbnf


def test_required_and_optional_properties_emit_optional_groups() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "must": {"type": "string"},
            "may": {"type": "string"},
        },
        "required": ["must"],
    }
    gbnf = schema_to_gbnf(schema)
    # Optional property "may" is wrapped in a (...)? group.
    root = gbnf.splitlines()[0]
    assert "(ws \",\" ws " in root and ")?" in root


def test_array_with_homogeneous_items() -> None:
    schema = {"type": "array", "items": {"type": "integer"}}
    gbnf = schema_to_gbnf(schema)
    assert '"[" ws' in gbnf
    assert 'ws "]"' in gbnf


def test_ref_resolves_against_defs() -> None:
    schema = {
        "$defs": {"Thing": {"type": "string"}},
        "$ref": "#/$defs/Thing",
    }
    gbnf = schema_to_gbnf(schema)
    # The named rule for Thing appears.
    assert "thing ::= string" in gbnf
    # Root references it.
    assert "root ::= thing" in gbnf


def test_recursive_ref_does_not_explode() -> None:
    """The canonical Branch -> if_true -> Branch cycle must terminate.

    The recursion routes through the anonymous per-property rule
    (``v-if-true-N``), so the assertion is on the full grammar text rather
    than the bare branch rule line: the `branch` name appears at the root,
    in its own LHS, and as the body of the anonymous if_true value rule.
    """
    schema = {
        "$defs": {
            "Branch": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "type": {"const": "branch"},
                    "if_true": {"$ref": "#/$defs/Branch"},
                },
                "required": ["type", "if_true"],
            }
        },
        "$ref": "#/$defs/Branch",
    }
    gbnf = schema_to_gbnf(schema)
    # Branch rule defined exactly once.
    branch_rule_lines = [line for line in gbnf.splitlines() if line.startswith("branch ::=")]
    assert len(branch_rule_lines) == 1
    # ...and referenced from at least the root and the anonymous if_true rule.
    references = [
        line for line in gbnf.splitlines()
        if "branch" in line and not line.startswith("branch ::=")
    ]
    assert len(references) >= 2, gbnf


def test_unsupported_ref_target_raises() -> None:
    schema = {"$ref": "https://example.com/external#"}
    with pytest.raises(GrammarDerivationError):
        schema_to_gbnf(schema)


def test_missing_ref_target_raises() -> None:
    schema = {"$defs": {}, "$ref": "#/$defs/Nope"}
    with pytest.raises(GrammarDerivationError):
        schema_to_gbnf(schema)


def test_caching_returns_identical_text() -> None:
    schema = {"type": "object", "additionalProperties": False, "properties": {}}
    a = schema_to_gbnf(schema)
    b = schema_to_gbnf(schema)
    assert a == b


def test_real_urml_program_schema_compiles() -> None:
    """End-to-end: the URML program schema derives a non-trivial grammar.

    This is the regression net. If a future validator release adds a
    primitive or composition node that breaks derivation, this test fails
    before the bridge ships against it.
    """
    schema = export_schema("program")
    gbnf = schema_to_gbnf(schema)

    # Root is defined.
    assert gbnf.startswith("root ::= ")

    # Several known $defs from URMLProgram appear as named rules.
    for expected in ("branch ::=", "sequence ::=", "parallel ::="):
        assert expected in gbnf, f"missing rule {expected!r} in derived grammar"

    # Prelude is present.
    assert "value ::= " in gbnf
    assert "object ::= " in gbnf
    assert "array ::= " in gbnf

    # Grammar is non-trivial (the real program schema is hundreds of rules).
    assert gbnf.count("::=") > 20
