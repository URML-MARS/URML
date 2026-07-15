"""Mining pulls real gold out of the repo and every example re-validates."""

from __future__ import annotations

from urml_validator import validate

from urml_model.mining import mine_few_shot_pairs, mine_fixture_programs, resolve_manifest_ref


def test_fixture_mining_finds_gold() -> None:
    gold = mine_fixture_programs()
    assert len(gold) > 50, "the conformance suite holds well over 50 accepted single-robot cases"
    assert all(g.nl is None for g in gold)
    assert all(g.manifest_ref for g in gold)


def test_every_mined_fixture_program_revalidates() -> None:
    for example in mine_fixture_programs():
        result = validate(
            example.program,
            example.manifest,
            example.envelope,
            profiles=(example.profile,),
            policy=example.policy,
        )
        assert result.accepted, f"{example.source} no longer validates: {result.codes()}"


def test_few_shot_mining_covers_all_profiles() -> None:
    pairs = mine_few_shot_pairs()
    profiles = {p.profile for p in pairs}
    assert profiles == {"home", "industrial", "drone", "educational"}
    assert all(p.nl for p in pairs)


def test_every_few_shot_pair_revalidates() -> None:
    for example in mine_few_shot_pairs():
        result = validate(
            example.program,
            example.manifest,
            example.envelope,
            profiles=(example.profile,),
            policy=example.policy,
        )
        assert result.accepted, f"{example.source} ({example.nl!r}) no longer validates: {result.codes()}"


def test_profile_filter() -> None:
    drone_only = mine_fixture_programs(profiles=("drone",))
    assert drone_only
    assert {g.profile for g in drone_only} == {"drone"}


def test_resolve_manifest_ref_falls_back_to_validator_fixtures() -> None:
    manifest = resolve_manifest_ref("educational_buggy")
    assert isinstance(manifest, dict)
