"""Back-translation: deterministic templates + provider-driven paraphrases."""

from __future__ import annotations

import json
from typing import Any

from urml_model.backtranslate import LLMBackTranslator, TemplateBackTranslator

_DRONE_PROGRAM = {
    "profile": "drone",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"take_off": {"altitude": 30.0}},
            {"move_to": {"location": "roof_north"}},
            {"capture": {"media": "photo", "store_as": "photo"}},
            {"return_to_home": {}},
            {"land": {}},
        ],
    },
}

_EDU_ORBIT = {
    "profile": "educational",
    "behavior": {
        "type": "sequence",
        "steps": [{"drive": {"radius": 0.05, "arc": 180}}],
    },
}


def test_template_is_deterministic_and_ordered() -> None:
    translator = TemplateBackTranslator()
    first = translator.to_utterances(_DRONE_PROGRAM, {})
    second = translator.to_utterances(_DRONE_PROGRAM, {})
    assert first == second
    assert len(first) == 1
    utterance = first[0]
    assert utterance == "Take off to 30.0 meters, go to roof north, take a photo, return home, then land."


def test_template_renders_radius_orbit_form() -> None:
    (utterance,) = TemplateBackTranslator().to_utterances(_EDU_ORBIT, {})
    assert utterance == "Orbit 180 degrees with a 0.05 meter radius."


def test_template_skips_unknown_primitives() -> None:
    program = {"behavior": {"type": "sequence", "steps": [{"frobnicate": {"x": 1}}]}}
    assert TemplateBackTranslator().to_utterances(program, {}) == []


def test_template_english_only() -> None:
    assert TemplateBackTranslator().to_utterances(_DRONE_PROGRAM, {}, language="he") == []


class _FakeProvider:
    """LLMProvider double returning a canned JSON array."""

    def __init__(self, payload: str) -> None:
        self._payload = payload
        self.calls: list[dict[str, Any]] = []

    def complete(self, *, system: str, user: str, schema: dict[str, Any], max_tokens: int = 4096) -> str:
        self.calls.append({"system": system, "user": user})
        return self._payload


def test_llm_backtranslator_parses_paraphrases() -> None:
    provider = _FakeProvider(json.dumps(["Inspect the roof.", "Fly up and photograph the north roof.", "  "]))
    translator = LLMBackTranslator(provider)
    utterances = translator.to_utterances(_DRONE_PROGRAM, {}, n=3)
    assert utterances == ["Inspect the roof.", "Fly up and photograph the north roof."]
    assert json.loads(provider.calls[0]["user"]) == _DRONE_PROGRAM


def test_llm_backtranslator_tolerates_garbage() -> None:
    assert LLMBackTranslator(_FakeProvider("not json")).to_utterances(_DRONE_PROGRAM, {}) == []
    assert LLMBackTranslator(_FakeProvider('{"an": "object"}')).to_utterances(_DRONE_PROGRAM, {}) == []
