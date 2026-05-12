"""Bridge behavior tests using EchoProvider — fully hermetic, no network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from urml_validator import ErrorCode, export_schema

from urml_llm_bridge import (
    Bridge,
    BridgeRevisionExhausted,
    EchoProvider,
    ProviderError,
    TranslateResult,
    build_system_prompt,
    default_few_shots,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"


@pytest.fixture
def turtlebot_manifest() -> dict:
    with (VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def home_envelope() -> dict:
    with (VALIDATOR_FIXTURES / "envelopes" / "home_default.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# A correct URML program the EchoProvider can return.
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


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_translate_happy_path(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    """First emission is correct; bridge accepts immediately."""
    provider = EchoProvider(scripted=[json.dumps(RED_MUG_PROGRAM)])
    bridge = Bridge(
        provider=provider,
        manifest=turtlebot_manifest,
        envelope=home_envelope,
        profiles=("home",),
        max_revisions=2,
    )
    result = bridge.translate("Bring me the red mug from the kitchen.")
    assert isinstance(result, TranslateResult)
    assert result.accepted is True
    assert result.revision_count == 0
    assert result.program == RED_MUG_PROGRAM
    assert len(result.raw_completions) == 1


# ---------------------------------------------------------------------------
# Revision loop
# ---------------------------------------------------------------------------


def test_revision_loop_accepts_after_one_fix(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    """First emission references an undeclared location; second emission corrects it."""
    bad_program = dict(RED_MUG_PROGRAM)
    bad_program = json.loads(json.dumps(RED_MUG_PROGRAM))  # deep copy via JSON
    bad_program["behavior"]["steps"][0]["move_to"]["location"] = "the_moon"

    provider = EchoProvider(
        scripted=[
            json.dumps(bad_program),
            json.dumps(RED_MUG_PROGRAM),
        ]
    )
    bridge = Bridge(
        provider=provider,
        manifest=turtlebot_manifest,
        envelope=home_envelope,
        profiles=("home",),
        max_revisions=3,
    )
    result = bridge.translate("Bring me the red mug from the kitchen.")
    assert result.accepted is True
    assert result.revision_count == 1
    assert len(result.raw_completions) == 2
    # The revision context must have been injected into the second call's system prompt.
    second_call_system = provider.call_log[1]["system"]
    assert "Revision required" in second_call_system
    assert "capability.missing_location" in second_call_system
    assert "the_moon" in second_call_system


def test_revision_exhausted(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    """Every emission is bad; bridge raises BridgeRevisionExhausted after the budget."""
    bad_program = json.loads(json.dumps(RED_MUG_PROGRAM))
    bad_program["behavior"]["steps"][0]["move_to"]["location"] = "the_moon"

    provider = EchoProvider(scripted=[json.dumps(bad_program)] * 5)
    bridge = Bridge(
        provider=provider,
        manifest=turtlebot_manifest,
        envelope=home_envelope,
        profiles=("home",),
        max_revisions=2,
    )
    with pytest.raises(BridgeRevisionExhausted) as excinfo:
        bridge.translate("Bring me the red mug from the kitchen.")
    assert excinfo.value.attempts == 3  # max_revisions=2 -> 1 initial + 2 retries
    last = excinfo.value.last_result
    assert last is not None
    # last_result should expose the structured error code.
    assert any(e.code == ErrorCode.CAPABILITY_MISSING_LOCATION for e in last.errors)  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Provider misbehaviour
# ---------------------------------------------------------------------------


def test_provider_returns_non_json(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(scripted=["I am not JSON."])
    bridge = Bridge(provider=provider, manifest=turtlebot_manifest, max_revisions=0)
    with pytest.raises(ProviderError):
        bridge.translate("test")


def test_provider_returns_empty(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(scripted=[""])
    bridge = Bridge(provider=provider, manifest=turtlebot_manifest, max_revisions=0)
    with pytest.raises(ProviderError):
        bridge.translate("test")


def test_provider_returns_list_not_object(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(scripted=["[1, 2, 3]"])
    bridge = Bridge(provider=provider, manifest=turtlebot_manifest, max_revisions=0)
    with pytest.raises(ProviderError):
        bridge.translate("test")


def test_provider_raises_is_wrapped(turtlebot_manifest: dict) -> None:
    """Exceptions from the provider surface as ProviderError, not whatever the SDK raised."""

    class BoomProvider:
        def complete(self, **_kwargs: object) -> str:
            raise RuntimeError("network broke")

    bridge = Bridge(provider=BoomProvider(), manifest=turtlebot_manifest, max_revisions=0)
    with pytest.raises(ProviderError, match="provider raised: RuntimeError"):
        bridge.translate("test")


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def test_system_prompt_contains_schema_and_manifest(turtlebot_manifest: dict) -> None:
    prompt = build_system_prompt(
        schema=export_schema("program"),
        manifest=turtlebot_manifest,
        envelope=None,
        profiles=("home",),
        few_shots=default_few_shots(),
    )
    # Schema is inlined.
    assert "URML program JSON Schema" in prompt
    # Manifest summary is present.
    assert "turtlebot4_demo" in prompt
    assert "kitchen" in prompt  # declared location
    assert "mug" in prompt  # object vocabulary
    # Few-shot example is present.
    assert "Bring me the red mug" in prompt
    # Profile declared.
    assert "Active profile(s): home" in prompt


def test_system_prompt_with_envelope(turtlebot_manifest: dict, home_envelope: dict) -> None:
    prompt = build_system_prompt(
        schema=export_schema("program"),
        manifest=turtlebot_manifest,
        envelope=home_envelope,
        profiles=("home",),
    )
    assert "Active safety envelope" in prompt
    assert "home_demo" in prompt
    assert "max_velocity=0.4" in prompt


def test_default_few_shots_returns_red_mug() -> None:
    shots = default_few_shots()
    assert len(shots) >= 1
    assert shots[0].user == "Bring me the red mug from the kitchen."
    assert shots[0].program["profile"] == "home"


# ---------------------------------------------------------------------------
# EchoProvider behaviours
# ---------------------------------------------------------------------------


def test_echo_provider_substring_matching() -> None:
    provider = EchoProvider(
        responses={"red mug": "{}"},
        match_substrings=True,
    )
    out = provider.complete(system="...", user="please bring me the red mug now", schema={})
    assert out == "{}"


def test_echo_provider_no_match_raises() -> None:
    provider = EchoProvider(responses={"foo": "{}"})
    with pytest.raises(KeyError):
        provider.complete(system="...", user="bar", schema={})


def test_echo_provider_scripted_exhausted() -> None:
    provider = EchoProvider(scripted=["{}"])
    provider.complete(system="...", user="first", schema={})
    with pytest.raises(KeyError, match="scripted responses exhausted"):
        provider.complete(system="...", user="second", schema={})


def test_echo_provider_rejects_both_modes() -> None:
    with pytest.raises(ValueError, match="exactly one"):
        EchoProvider(responses={"a": "b"}, scripted=["c"])


def test_echo_provider_requires_at_least_one_mode() -> None:
    with pytest.raises(ValueError, match="either"):
        EchoProvider()
