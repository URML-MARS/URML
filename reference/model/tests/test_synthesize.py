"""End-to-end synthesis: mined gold -> oracle filter -> deduped dataset."""

from __future__ import annotations

from urml_model.mining import GoldExample, mine_few_shot_pairs, mine_fixture_programs, resolve_manifest_ref
from urml_model.synthesize import synthesize


def test_synthesize_fixture_gold_all_accepted() -> None:
    gold = mine_fixture_programs(profiles=("drone",))
    dataset, report = synthesize(gold)
    assert report.kept > 0
    assert not report.dropped_rejected
    assert all(r.validator_verdict.accepted for r in dataset)
    assert all(r.provenance == "fixture_backtranslation" for r in dataset)


def test_synthesize_few_shots_keep_their_utterance() -> None:
    gold = mine_few_shot_pairs(profiles=("home",))
    dataset, report = synthesize(gold)
    assert report.kept == len(gold)
    assert {r.nl for r in dataset} == {g.nl for g in gold}
    assert all(r.provenance == "few_shot" for r in dataset)


def test_synthesize_drops_rejected_program_with_reason() -> None:
    manifest = resolve_manifest_ref("turtlebot4_home")
    bad = GoldExample(
        program={
            "profile": "home",
            "behavior": {"type": "sequence", "steps": [{"take_off": {"altitude": 30.0}}]},
        },
        manifest=manifest,
        manifest_ref="turtlebot4_home",
        profile="home",
        source="synthetic:ground-robot-take-off",
    )
    dataset, report = synthesize([bad])
    assert len(dataset) == 0
    assert len(report.dropped_rejected) == 1
    source, codes = report.dropped_rejected[0]
    assert source == "synthetic:ground-robot-take-off"
    assert codes, "the oracle names why it rejected"
    assert "rejected" in report.summary()


def test_synthesize_dedups_identical_pairs() -> None:
    gold = mine_few_shot_pairs(profiles=("drone",))
    dataset, report = synthesize(gold + gold)
    assert report.deduplicated == len(gold)
    assert len(dataset) == len(gold)
