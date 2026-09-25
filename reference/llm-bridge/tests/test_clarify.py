"""RFC-0700 clarify mode: hermetic tests (EchoProvider + fake Anthropic client).

Default-off is the load-bearing property: with `clarify=False` (the default)
the bridge's provider calls, prompt bytes, and outcomes are identical to
v0.2.0, and every pre-existing test in this suite passes untouched.
"""

from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any

import pytest
import yaml
from pathlib import Path

from urml_validator import export_schema

from urml_llm_bridge import (
    Bridge,
    BridgeClarificationNeeded,
    BridgeRevisionExhausted,
    EchoProvider,
    ProviderError,
)
from urml_llm_bridge.grammar import schema_to_gbnf
from urml_llm_bridge.providers.anthropic import (
    CLARIFY_TOOL_NAME,
    EMIT_TOOL_NAME,
    AnthropicProvider,
)
from urml_llm_bridge.providers.base import (
    CLARIFY_SCHEMA,
    build_clarify_union_schema,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"


@pytest.fixture
def turtlebot_manifest() -> dict:
    with (VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


RED_MUG_PROGRAM = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"move_to": {"location": "kitchen"}},
            {
                "detect": {
                    "object": "mug",
                    "attributes": {"color": "red"},
                    "store_as": "target_mug",
                }
            },
            {"grasp": {"target": "$target_mug", "force": "gentle"}},
            {"move_to": {"location": "user", "carrying": "$target_mug"}},
            {"release": {"mode": "hand_to_user"}},
        ],
    },
}

CLARIFY_EMISSION = {
    "clarify": {
        "question": "Which mug do you mean?",
        "options": ["the red one", "the blue one"],
    }
}

INVALID_PROGRAM = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [{"move_to": {"location": "attic"}}],
    },
}


def _clarify_bridge(provider: EchoProvider, manifest: dict, **kw: Any) -> Bridge:
    kw.setdefault("clarify", True)
    return Bridge(
        provider=provider,
        manifest=manifest,
        profiles=("home",),
        max_revisions=1,
        policy=None,
        **kw,
    )


# ---------------------------------------------------------------------------
# The happy path: ask, answer, translate
# ---------------------------------------------------------------------------


def test_clarify_question_then_program(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(
        scripted=[json.dumps(CLARIFY_EMISSION), json.dumps(RED_MUG_PROGRAM)]
    )
    seen: list[tuple[str, list[str]]] = []

    def answer(question: str, options: list[str]) -> str:
        seen.append((question, options))
        return "the red one"

    result = _clarify_bridge(provider, turtlebot_manifest).translate(
        "Bring me the mug.", on_clarify=answer
    )
    assert result.accepted
    assert result.clarification_count == 1
    assert result.clarifications == [("Which mug do you mean?", "the red one")]
    assert result.revision_count == 0  # a question never consumes a revision
    assert seen == [("Which mug do you mean?", ["the red one", "the blue one"])]

    first, second = provider.call_log
    # While the budget is open the provider gets the clarify branch...
    assert first["clarify_schema"] == CLARIFY_SCHEMA
    assert "Clarify mode is enabled" in first["system"]
    # ...after the question is spent, the branch is withheld and the answer
    # is folded into the effective request.
    assert second["clarify_schema"] is None
    assert "clarification budget is spent" in second["system"]
    assert "Q: Which mug do you mean?" in second["user"]
    assert "A: the red one" in second["user"]
    assert second["user"].startswith("Bring me the mug.")


def test_clarify_without_callback_raises(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(scripted=[json.dumps(CLARIFY_EMISSION)])
    with pytest.raises(BridgeClarificationNeeded) as excinfo:
        _clarify_bridge(provider, turtlebot_manifest).translate("Bring me the mug.")
    assert excinfo.value.question == "Which mug do you mean?"
    assert excinfo.value.options == ["the red one", "the blue one"]


# ---------------------------------------------------------------------------
# The guardrails
# ---------------------------------------------------------------------------


def test_no_question_after_rejection(turtlebot_manifest: dict) -> None:
    """A rejection closes the clarify window: the clarify branch is withheld
    and a clarify emission after it fails validation like any bad program."""
    provider = EchoProvider(
        scripted=[json.dumps(INVALID_PROGRAM), json.dumps(CLARIFY_EMISSION)]
    )
    with pytest.raises(BridgeRevisionExhausted):
        _clarify_bridge(provider, turtlebot_manifest).translate(
            "Bring the mug to the attic.", on_clarify=lambda q, o: "?"
        )
    first, second = provider.call_log
    assert first["clarify_schema"] == CLARIFY_SCHEMA
    assert second["clarify_schema"] is None


def test_clarify_off_is_v020_behavior(turtlebot_manifest: dict) -> None:
    """Default off: no addendum, no clarify branch, and a clarify emission is
    just an invalid program for the ordinary revision loop."""
    provider = EchoProvider(scripted=[json.dumps(CLARIFY_EMISSION)] * 2)
    bridge = Bridge(
        provider=provider,
        manifest=turtlebot_manifest,
        profiles=("home",),
        max_revisions=1,
        policy=None,
    )
    with pytest.raises(BridgeRevisionExhausted):
        bridge.translate("Bring me the mug.")
    for call in provider.call_log:
        assert call["clarify_schema"] is None
        assert "Clarify mode" not in call["system"]
        assert "clarify" not in call["system"].split("=== URML program JSON Schema ===")[0]


def test_malformed_clarify_is_provider_error(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(scripted=[json.dumps({"clarify": {"options": ["a"]}})])
    with pytest.raises(ProviderError, match="question"):
        _clarify_bridge(provider, turtlebot_manifest).translate(
            "Bring me the mug.", on_clarify=lambda q, o: "?"
        )


def test_budget_zero_never_offers_clarify(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(scripted=[json.dumps(RED_MUG_PROGRAM)])
    result = _clarify_bridge(
        provider, turtlebot_manifest, max_clarifications=0
    ).translate("Bring me the red mug.", on_clarify=lambda q, o: "?")
    assert result.accepted
    assert provider.call_log[0]["clarify_schema"] is None
    assert "clarification budget is spent" in provider.call_log[0]["system"]


# ---------------------------------------------------------------------------
# The union schema and constrained decoding
# ---------------------------------------------------------------------------


def test_union_schema_derives_gbnf_with_both_branches() -> None:
    program_schema = export_schema("program")
    union = build_clarify_union_schema(program_schema, CLARIFY_SCHEMA)
    grammar = schema_to_gbnf(union)
    assert '\\"clarify\\"' in grammar
    assert '\\"question\\"' in grammar
    assert '\\"behavior\\"' in grammar  # the program branch survived the hoist


# ---------------------------------------------------------------------------
# Anthropic adapter: second tool, widened tool_choice, wire-shape mapping
# ---------------------------------------------------------------------------


class _FakeMessages:
    def __init__(self, response: Any) -> None:
        self.response = response
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        return self.response


class _FakeAnthropicClient:
    def __init__(self, response: Any) -> None:
        self.messages = _FakeMessages(response)


def test_anthropic_registers_clarify_tool_and_maps_wire_shape() -> None:
    inner = {"question": "Which mug?", "options": ["red"]}
    response = SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name=CLARIFY_TOOL_NAME, input=inner)]
    )
    client = _FakeAnthropicClient(response)
    out = AnthropicProvider(client=client).complete(
        system="S", user="U", schema={"type": "object"}, clarify_schema=CLARIFY_SCHEMA
    )
    assert json.loads(out) == {"clarify": inner}

    call = client.messages.calls[0]
    assert call["tool_choice"] == {"type": "any"}
    names = [tool["name"] for tool in call["tools"]]
    assert names == [EMIT_TOOL_NAME, CLARIFY_TOOL_NAME]
    assert call["tools"][1]["input_schema"] == CLARIFY_SCHEMA["properties"]["clarify"]


def test_anthropic_without_clarify_is_unchanged() -> None:
    payload = {"profile": "home"}
    response = SimpleNamespace(
        content=[SimpleNamespace(type="tool_use", name=EMIT_TOOL_NAME, input=payload)]
    )
    client = _FakeAnthropicClient(response)
    out = AnthropicProvider(client=client).complete(
        system="S", user="U", schema={"type": "object"}
    )
    assert json.loads(out) == payload
    call = client.messages.calls[0]
    assert call["tool_choice"] == {"type": "tool", "name": EMIT_TOOL_NAME}
    assert [tool["name"] for tool in call["tools"]] == [EMIT_TOOL_NAME]
