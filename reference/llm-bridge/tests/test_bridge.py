"""Bridge behavior tests using EchoProvider — fully hermetic, no network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from urml_validator import ErrorCode, export_schema

from urml_llm_bridge import (
    Bridge,
    BridgePolicyViolation,
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


@pytest.fixture
def drone_manifest() -> dict:
    with (VALIDATOR_FIXTURES / "manifests" / "drone_civilian.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def drone_envelope() -> dict:
    with (VALIDATOR_FIXTURES / "envelopes" / "drone_default.yaml").open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def industrial_manifest() -> dict:
    with (VALIDATOR_FIXTURES / "manifests" / "industrial_cell.yaml").open(encoding="utf-8") as fh:
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


# A correct drone-profile URML program the EchoProvider can return.
ROOF_INSPECTION_PROGRAM = {
    "profile": "drone",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"take_off": {"altitude": 30.0}},
            {"move_to": {"location": "roof_north"}},
            {"capture": {"media": "photo", "store_as": "north_photo"}},
            {"return_to_home": {}},
            {"land": {}},
        ],
    },
}


def test_translate_happy_path_drone(
    drone_manifest: dict,
    drone_envelope: dict,
) -> None:
    """End-to-end drone translate: provider returns a valid program, bridge accepts."""
    provider = EchoProvider(scripted=[json.dumps(ROOF_INSPECTION_PROGRAM)])
    bridge = Bridge(
        provider=provider,
        manifest=drone_manifest,
        envelope=drone_envelope,
        profiles=("drone",),
        max_revisions=2,
    )
    result = bridge.translate("Inspect the north roof for damage and bring me photos.")
    assert result.accepted is True
    assert result.revision_count == 0
    assert result.program == ROOF_INSPECTION_PROGRAM


# A correct industrial-profile URML program the EchoProvider can return.
PICK_RED_PROGRAM = {
    "profile": "industrial",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"move_to": {"location": "pick_bin"}},
            {
                "detect": {
                    "object": "widget_red",
                    "where": {"near": "pick_bin"},
                    "store_as": "red_widget",
                }
            },
            {"grasp": {"target": "$red_widget", "force": "firm"}},
            {"move_to": {"location": "kitting_tray_red", "carrying": "$red_widget"}},
            {"release": {"mode": "place", "at": "kitting_tray_red"}},
            {"move_to": {"location": "home_pose"}},
            {
                "report": {
                    "to": "line_controller",
                    "facts": {"cycle": "pick_red_to_tray", "result": "ok"},
                    "status": "success",
                }
            },
        ],
    },
}


def test_translate_happy_path_industrial(
    industrial_manifest: dict,
) -> None:
    """End-to-end industrial translate: provider returns a valid program, bridge accepts."""
    provider = EchoProvider(scripted=[json.dumps(PICK_RED_PROGRAM)])
    bridge = Bridge(
        provider=provider,
        manifest=industrial_manifest,
        profiles=("industrial",),
        max_revisions=2,
    )
    result = bridge.translate(
        "Pick a red widget from the bin and place it in the red kitting tray."
    )
    assert result.accepted is True
    assert result.revision_count == 0
    assert result.program == PICK_RED_PROGRAM


# ---------------------------------------------------------------------------
# Multilingual round-trips: Japanese
#
# Per the manifesto's multilingual commitment (CLAUDE.md §Strategic Posture),
# the natural-language layer must accept non-English requests. The Bridge is
# language-agnostic by design — it forwards the user's string to the LLM
# verbatim — but these tests pin that contract: a Japanese request must flow
# through bridge → validator → accepted URML without truncation, encoding
# loss, or schema-side rejection. Companion `.ja.txt` files live alongside
# the canonical English prompts under examples/{drone,industrial}/.
# ---------------------------------------------------------------------------


_JA_DRONE_REQUEST = "北側の屋根を点検して、損傷の写真を持ってきてください。"
_JA_INDUSTRIAL_REQUEST = "ビンから赤いウィジェットを取って、赤いトレイに置いてください。"


def test_translate_happy_path_drone_japanese(
    drone_manifest: dict,
    drone_envelope: dict,
) -> None:
    """A Japanese drone request flows through the bridge without encoding loss."""
    provider = EchoProvider(scripted=[json.dumps(ROOF_INSPECTION_PROGRAM)])
    bridge = Bridge(
        provider=provider,
        manifest=drone_manifest,
        envelope=drone_envelope,
        profiles=("drone",),
        max_revisions=2,
    )
    result = bridge.translate(_JA_DRONE_REQUEST)
    assert result.accepted is True
    assert result.program == ROOF_INSPECTION_PROGRAM
    # The Japanese characters reach the provider intact (no mojibake, no
    # silent ASCII-only coercion in the prompt assembly path).
    assert _JA_DRONE_REQUEST in provider.call_log[0]["user"]


def test_translate_happy_path_industrial_japanese(
    industrial_manifest: dict,
) -> None:
    """A Japanese industrial request flows through the bridge without encoding loss."""
    provider = EchoProvider(scripted=[json.dumps(PICK_RED_PROGRAM)])
    bridge = Bridge(
        provider=provider,
        manifest=industrial_manifest,
        profiles=("industrial",),
        max_revisions=2,
    )
    result = bridge.translate(_JA_INDUSTRIAL_REQUEST)
    assert result.accepted is True
    assert result.program == PICK_RED_PROGRAM
    assert _JA_INDUSTRIAL_REQUEST in provider.call_log[0]["user"]


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


# ---------------------------------------------------------------------------
# Policy short-circuit (RFC-0004)
# ---------------------------------------------------------------------------


def _manifest_with_provenance(country: str = "US", attestation: str = "third_party_audited") -> dict:
    """Minimal manifest that triggers Pass 5."""
    return {
        "manifest_version": "0.1",
        "robot_id": "test_bot",
        "provenance": {
            "manifest_attestation": attestation,
            "components": [
                {
                    "id": "drive_controller",
                    "role": "critical",
                    "vendor": "example_vendor",
                    "country_of_origin": country,
                    "country_of_final_assembly": country,
                    "hbom_ref": {
                        "format": "cyclonedx-1.7",
                        "uri": "./hbom/x.json",
                        "sha256": "abc",
                    },
                }
            ],
        },
    }


# A trivial program that doesn't depend on the manifest's mobility/etc.
_WAIT_PROGRAM = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [{"wait": {"duration": "1s"}}],
    },
}


def test_policy_only_errors_raise_violation_without_revision() -> None:
    """When only policy.* errors fire, the bridge does NOT retry — it raises."""
    provider = EchoProvider(scripted=[json.dumps(_WAIT_PROGRAM)])
    bridge = Bridge(
        provider=provider,
        manifest=_manifest_with_provenance(country="CN"),  # tripwires default policy
        profiles=("home",),
        max_revisions=3,
    )
    with pytest.raises(BridgePolicyViolation) as excinfo:
        bridge.translate("ignored request")
    # The bridge gave up after one attempt — provider only had one scripted
    # response, but the assertion that matters is that we did NOT exhaust
    # the scripted list (no revision was attempted).
    assert excinfo.value.attempts == 1


def test_policy_none_disables_pass_5() -> None:
    """Passing policy=None to the Bridge constructor skips Pass 5 entirely."""
    provider = EchoProvider(scripted=[json.dumps(_WAIT_PROGRAM)])
    bridge = Bridge(
        provider=provider,
        manifest=_manifest_with_provenance(country="CN"),
        profiles=("home",),
        max_revisions=1,
        policy=None,
    )
    result = bridge.translate("ignored request")
    assert result.accepted


def test_us_compliant_manifest_translates_under_default_policy() -> None:
    """A US-compliant provenance manifest passes the bundled default policy."""
    provider = EchoProvider(scripted=[json.dumps(_WAIT_PROGRAM)])
    bridge = Bridge(
        provider=provider,
        manifest=_manifest_with_provenance(country="US"),
        profiles=("home",),
        max_revisions=1,
    )
    result = bridge.translate("ignored request")
    assert result.accepted


# ---------------------------------------------------------------------------
# JSON repair for small/local models (conservative, validator still gates)
# ---------------------------------------------------------------------------


def test_translate_repairs_fenced_emission(
    turtlebot_manifest: dict,
    home_envelope: dict,
) -> None:
    """A small model that wraps valid JSON in a Markdown fence is recovered."""
    fenced = "```json\n" + json.dumps(RED_MUG_PROGRAM) + "\n```"
    provider = EchoProvider(scripted=[fenced])
    bridge = Bridge(
        provider=provider,
        manifest=turtlebot_manifest,
        envelope=home_envelope,
        profiles=("home",),
        max_revisions=0,
    )
    result = bridge.translate("Bring me the red mug from the kitchen.")
    assert result.accepted is True
    assert result.program == RED_MUG_PROGRAM
    # The original (fenced) emission is preserved for --save-rejected style review.
    assert result.raw_completions[0] == fenced


def test_parse_emission_recovers_common_malformations() -> None:
    from urml_llm_bridge.bridge import _parse_emission

    obj = {"profile": "home", "behavior": {"type": "sequence", "steps": []}}
    clean = json.dumps(obj)
    # Markdown fence.
    assert _parse_emission("```json\n" + clean + "\n```") == obj
    # Surrounding prose.
    assert _parse_emission("Here is the program:\n" + clean + "\nHope that helps!") == obj
    # Trailing comma before a closing brace.
    assert _parse_emission('{"profile": "home", "behavior": {"type": "sequence", "steps": [],},}') == obj
    # Already-clean JSON is unchanged.
    assert _parse_emission(clean) == obj


def test_parse_emission_does_not_fabricate_broken_json() -> None:
    """Genuinely broken JSON (not a safe wrapper issue) still fails, not guessed."""
    from urml_llm_bridge.bridge import _parse_emission

    with pytest.raises(ProviderError, match="non-JSON output"):
        _parse_emission('{"profile": "home" "behavior": {}}')  # missing comma, ambiguous
    with pytest.raises(ProviderError, match="non-JSON output"):
        _parse_emission("this is not json at all")
    with pytest.raises(ProviderError, match="expected an object"):
        _parse_emission("[1, 2, 3]")
