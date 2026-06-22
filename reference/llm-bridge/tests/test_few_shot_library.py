"""Few-shot library tests.

The load-bearing check: every shipped example must validate end-to-end
against its target profile's canonical manifest fixture. If any of these
fixtures stop validating, the system prompt would be teaching the LLM
to emit programs the validator rejects — exactly the wrong direction
for the revision loop's hit rate.

Also covers the profile selector (`few_shots_for(profiles)`) and the
Bridge's profile-aware defaulting.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from urml_validator import validate

from urml_llm_bridge import (
    Bridge,
    EchoProvider,
    FewShot,
    default_few_shots,
    drone_few_shots,
    educational_few_shots,
    few_shots_for,
    home_few_shots,
    industrial_few_shots,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"

HOME_MANIFEST_PATH = VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home.yaml"
INDUSTRIAL_MANIFEST_PATH = VALIDATOR_FIXTURES / "manifests" / "industrial_cell.yaml"
DRONE_MANIFEST_PATH = VALIDATOR_FIXTURES / "manifests" / "drone_civilian.yaml"
EDUCATIONAL_MANIFEST_PATH = VALIDATOR_FIXTURES / "manifests" / "educational_buggy.yaml"
HOME_ENVELOPE_PATH = VALIDATOR_FIXTURES / "envelopes" / "home_default.yaml"
DRONE_ENVELOPE_PATH = VALIDATOR_FIXTURES / "envelopes" / "drone_default.yaml"


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def home_manifest() -> dict:
    return _load(HOME_MANIFEST_PATH)


@pytest.fixture
def industrial_manifest() -> dict:
    return _load(INDUSTRIAL_MANIFEST_PATH)


@pytest.fixture
def drone_manifest() -> dict:
    return _load(DRONE_MANIFEST_PATH)


@pytest.fixture
def educational_manifest() -> dict:
    return _load(EDUCATIONAL_MANIFEST_PATH)


@pytest.fixture
def home_envelope() -> dict:
    return _load(HOME_ENVELOPE_PATH)


@pytest.fixture
def drone_envelope() -> dict:
    return _load(DRONE_ENVELOPE_PATH)


# ---------------------------------------------------------------------------
# Each shipped example validates end-to-end.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("example", home_few_shots(), ids=lambda ex: ex.user[:40])
def test_every_home_example_validates(example: FewShot, home_manifest: dict, home_envelope: dict) -> None:
    """Every home-profile few-shot must validate against the home manifest + envelope."""
    result = validate(example.program, home_manifest, home_envelope, profiles=("home",))
    assert result.accepted, (
        f"home few-shot {example.user!r} failed validation: "
        f"{[e.render() for e in result.errors]}"
    )


@pytest.mark.parametrize("example", educational_few_shots(), ids=lambda ex: ex.user[:40])
def test_every_educational_example_validates(example: FewShot, educational_manifest: dict) -> None:
    """Every educational-profile few-shot (RFC-0630 drive/turn) must validate against the buggy manifest."""
    result = validate(example.program, educational_manifest, profiles=("educational",))
    assert result.accepted, (
        f"educational few-shot {example.user!r} failed validation: "
        f"{[e.render() for e in result.errors]}"
    )


@pytest.mark.parametrize("example", industrial_few_shots(), ids=lambda ex: ex.user[:40])
def test_every_industrial_example_validates(example: FewShot, industrial_manifest: dict) -> None:
    """Every industrial-profile few-shot must validate against the industrial manifest."""
    result = validate(example.program, industrial_manifest, profiles=("industrial",))
    assert result.accepted, (
        f"industrial few-shot {example.user!r} failed validation: "
        f"{[e.render() for e in result.errors]}"
    )


@pytest.mark.parametrize("example", drone_few_shots(), ids=lambda ex: ex.user[:40])
def test_every_drone_example_validates(
    example: FewShot, drone_manifest: dict, drone_envelope: dict
) -> None:
    """Every drone-profile few-shot must validate against the drone manifest + envelope."""
    result = validate(example.program, drone_manifest, drone_envelope, profiles=("drone",))
    assert result.accepted, (
        f"drone few-shot {example.user!r} failed validation: "
        f"{[e.render() for e in result.errors]}"
    )


# ---------------------------------------------------------------------------
# Library shape / structural guarantees
# ---------------------------------------------------------------------------


def test_home_few_shots_nonempty_with_unique_user_strings() -> None:
    shots = home_few_shots()
    assert len(shots) >= 4
    users = [s.user for s in shots]
    assert len(set(users)) == len(users), "duplicate user requests in home_few_shots()"


def test_industrial_few_shots_nonempty_with_unique_user_strings() -> None:
    shots = industrial_few_shots()
    assert len(shots) >= 2
    users = [s.user for s in shots]
    assert len(set(users)) == len(users), "duplicate user requests in industrial_few_shots()"


def test_drone_few_shots_nonempty_with_unique_user_strings() -> None:
    shots = drone_few_shots()
    assert len(shots) >= 3
    users = [s.user for s in shots]
    assert len(set(users)) == len(users), "duplicate user requests in drone_few_shots()"


def test_every_example_declares_a_profile() -> None:
    """Each example program must declare a `profile` field at the top level."""
    for shots in (home_few_shots(), industrial_few_shots(), drone_few_shots()):
        for s in shots:
            assert "profile" in s.program, f"example missing profile: {s.user!r}"


# ---------------------------------------------------------------------------
# few_shots_for(profiles)
# ---------------------------------------------------------------------------


def test_few_shots_for_home() -> None:
    assert few_shots_for(("home",)) == home_few_shots()


def test_few_shots_for_industrial() -> None:
    assert few_shots_for(("industrial",)) == industrial_few_shots()


def test_few_shots_for_drone() -> None:
    assert few_shots_for(("drone",)) == drone_few_shots()


def test_few_shots_for_empty_falls_back_to_home() -> None:
    assert few_shots_for(()) == home_few_shots()


def test_few_shots_for_unknown_profile_falls_back_to_home() -> None:
    assert few_shots_for(("definitely_not_a_real_profile",)) == home_few_shots()


def test_few_shots_for_concatenates_known_profiles_in_order() -> None:
    """Multiple profiles -> concatenated, declaration order preserved."""
    out = few_shots_for(("industrial", "home"))
    expected = industrial_few_shots() + home_few_shots()
    assert out == expected


def test_few_shots_for_mixed_known_and_unknown_skips_unknown() -> None:
    out = few_shots_for(("home", "definitely_not_a_real_profile"))
    assert out == home_few_shots()


def test_default_few_shots_is_home_alias() -> None:
    assert default_few_shots() == home_few_shots()


# ---------------------------------------------------------------------------
# Bridge integration: profile-aware defaults
# ---------------------------------------------------------------------------


_TINY_HOME_RESPONSE = (
    '{"profile": "home", "behavior": {"type": "sequence",'
    ' "steps": [{"wait": {"duration": "1s"}}]}}'
)
_TINY_INDUSTRIAL_RESPONSE = (
    '{"profile": "industrial", "behavior": {"type": "sequence",'
    ' "steps": [{"wait": {"duration": "1s"}}]}}'
)
_TINY_DRONE_RESPONSE = (
    '{"profile": "drone", "behavior": {"type": "sequence",'
    ' "steps": [{"wait": {"duration": "1s"}}]}}'
)


def test_bridge_picks_home_few_shots_by_default(home_manifest: dict) -> None:
    provider = EchoProvider(scripted=[_TINY_HOME_RESPONSE])
    bridge = Bridge(provider=provider, manifest=home_manifest, profiles=("home",))
    bridge.translate("test")
    system_prompt = provider.call_log[0]["system"]
    # The red-mug example is in home_few_shots; its NL line should appear.
    assert "Bring me the red mug from the kitchen." in system_prompt


def test_bridge_picks_industrial_few_shots_when_profile_is_industrial(
    industrial_manifest: dict,
) -> None:
    provider = EchoProvider(scripted=[_TINY_INDUSTRIAL_RESPONSE])
    bridge = Bridge(provider=provider, manifest=industrial_manifest, profiles=("industrial",))
    bridge.translate("test")
    system_prompt = provider.call_log[0]["system"]
    # The pick-red example is in industrial_few_shots; its NL line should appear.
    assert "Pick a red widget from the bin" in system_prompt
    # The home red-mug example should NOT be in an industrial-profile prompt.
    assert "Bring me the red mug from the kitchen." not in system_prompt


def test_bridge_picks_drone_few_shots_when_profile_is_drone(
    drone_manifest: dict, drone_envelope: dict
) -> None:
    provider = EchoProvider(scripted=[_TINY_DRONE_RESPONSE])
    bridge = Bridge(
        provider=provider,
        manifest=drone_manifest,
        envelope=drone_envelope,
        profiles=("drone",),
    )
    bridge.translate("test")
    system_prompt = provider.call_log[0]["system"]
    # The roof-inspection example is in drone_few_shots; its NL line should appear.
    assert "Inspect the north roof for damage and bring me photos." in system_prompt
    # The home red-mug example should NOT appear in a drone-profile prompt.
    assert "Bring me the red mug from the kitchen." not in system_prompt
    # Neither should the industrial pick-red example.
    assert "Pick a red widget from the bin" not in system_prompt


def test_bridge_explicit_few_shots_overrides_auto_selection(home_manifest: dict) -> None:
    """When `few_shots=` is passed, the bridge uses those exactly, ignoring profile."""
    custom_program = {
        "profile": "home",
        "behavior": {"type": "sequence", "steps": [{"wait": {"duration": "1s"}}]},
    }
    custom = [FewShot(user="custom example NL", program=custom_program)]
    provider = EchoProvider(scripted=[_TINY_HOME_RESPONSE])
    bridge = Bridge(
        provider=provider,
        manifest=home_manifest,
        profiles=("industrial",),  # would normally select industrial examples
        few_shots=custom,
    )
    bridge.translate("test")
    system_prompt = provider.call_log[0]["system"]
    assert "custom example NL" in system_prompt
    assert "Pick a red widget" not in system_prompt


# ---------------------------------------------------------------------------
# Validator's industrial fixture itself parses
# ---------------------------------------------------------------------------


def test_industrial_manifest_fixture_parses(industrial_manifest: dict) -> None:
    """Smoke check on the new manifest fixture."""
    from urml_validator.schemas.manifest import CapabilityManifest

    parsed = CapabilityManifest.model_validate(industrial_manifest)
    assert parsed.robot_id == "cell_a1"
    assert parsed.manipulation is not None
    assert any(g.name == "pneumatic_2_finger" for g in parsed.manipulation.grippers)
    assert parsed.perception is not None
    assert "widget_red" in parsed.perception.object_vocabulary
