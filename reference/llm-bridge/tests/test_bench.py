"""`urml_llm_bridge.bench`: hermetic benchmark-harness tests (EchoProvider only)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from urml_llm_bridge import Bridge, EchoProvider
from urml_llm_bridge.bench import (
    BenchCorpus,
    BenchCorpusError,
    BenchUtterance,
    classify,
    load_corpus,
    load_rows,
    render_row,
    render_table,
    run_bench,
    write_row,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"
CONFORMANCE_UTTERANCES = (
    REPO_ROOT / "conformance" / "llm-bridge" / "fixtures" / "home" / "utterances-en.yaml"
)
BENCH_CORPORA = REPO_ROOT / "bench" / "corpora"


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

REFUSAL_PROGRAM = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {
                "report": {
                    "to": "user",
                    "facts": {"reason": "No sandwich-making capability is declared."},
                    "status": "failure",
                }
            }
        ],
    },
}

# Does real work, then reports failure: NOT an honest refusal (root is mixed).
WORK_THEN_FAIL_PROGRAM = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"move_to": {"location": "kitchen"}},
            {
                "report": {
                    "to": "user",
                    "facts": {"reason": "Could not finish."},
                    "status": "failure",
                }
            },
        ],
    },
}

INVALID_PROGRAM = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [{"move_to": {"location": "attic"}}],
    },
}


def _bridge(provider: EchoProvider, manifest: dict, max_revisions: int = 1) -> Bridge:
    return Bridge(
        provider=provider,
        manifest=manifest,
        profiles=("home",),
        max_revisions=max_revisions,
        policy=None,
    )


def _utt(text: str, expected: str = "accept") -> BenchUtterance:
    return BenchUtterance(id="u", text=text, expected=expected)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# classify: the five outcomes
# ---------------------------------------------------------------------------


def test_classify_accepted(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(responses={"mug": json.dumps(RED_MUG_PROGRAM)}, match_substrings=True)
    r = classify(_bridge(provider, turtlebot_manifest), _utt("Bring me the red mug."))
    assert r.outcome == "accepted"
    assert r.expected_match is True
    assert r.revision_count == 0


def test_classify_honest_refusal_matches_refuse(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(responses={"sandwich": json.dumps(REFUSAL_PROGRAM)}, match_substrings=True)
    r = classify(_bridge(provider, turtlebot_manifest), _utt("Make me a sandwich.", "refuse"))
    assert r.outcome == "honest_refusal"
    assert r.expected_match is True


def test_classify_honest_refusal_misses_accept(turtlebot_manifest: dict) -> None:
    """A model that refuses a doable request is an honest refusal that missed."""
    provider = EchoProvider(responses={"mug": json.dumps(REFUSAL_PROGRAM)}, match_substrings=True)
    r = classify(_bridge(provider, turtlebot_manifest), _utt("Bring me the red mug."))
    assert r.outcome == "honest_refusal"
    assert r.expected_match is False


def test_work_then_fail_is_not_a_refusal(turtlebot_manifest: dict) -> None:
    """Root-only rule: real work followed by a failure report counts as accepted."""
    provider = EchoProvider(
        responses={"kitchen": json.dumps(WORK_THEN_FAIL_PROGRAM)}, match_substrings=True
    )
    r = classify(_bridge(provider, turtlebot_manifest), _utt("Check the kitchen."))
    assert r.outcome == "accepted"


def test_classify_invalid_emission(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(scripted=[json.dumps(INVALID_PROGRAM)] * 2)
    r = classify(_bridge(provider, turtlebot_manifest, max_revisions=1), _utt("Go to the attic.", "refuse"))
    assert r.outcome == "invalid_emission"
    assert r.expected_match is False
    assert "2 attempt(s)" in r.detail


def test_classify_provider_error(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(responses={"nothing-matches": "{}"}, match_substrings=True)
    r = classify(_bridge(provider, turtlebot_manifest), _utt("Bring me the red mug."))
    assert r.outcome == "provider_error"


def test_classify_policy_block() -> None:
    manifest = {
        "manifest_version": "0.1",
        "robot_id": "test_bot",
        "provenance": {
            "manifest_attestation": "third_party_audited",
            "components": [
                {
                    "id": "drive_controller",
                    "role": "critical",
                    "vendor": "example_vendor",
                    "country_of_origin": "CN",
                    "country_of_final_assembly": "CN",
                    "hbom_ref": {"format": "cyclonedx-1.7", "uri": "./hbom/x.json", "sha256": "abc"},
                }
            ],
        },
    }
    wait_program = {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"wait": {"duration": "1s"}}],
        },
    }
    provider = EchoProvider(scripted=[json.dumps(wait_program)])
    bridge = Bridge(provider=provider, manifest=manifest, profiles=("home",), max_revisions=3)
    r = classify(bridge, _utt("wait a second"))
    assert r.outcome == "policy_block"


# ---------------------------------------------------------------------------
# run_bench: aggregation, and one bad row never aborts the run
# ---------------------------------------------------------------------------


def _mixed_corpus() -> BenchCorpus:
    return BenchCorpus(
        corpus_id="mixed",
        profile="home",
        language="en",
        utterances=(
            BenchUtterance(id="ok", text="Bring me the red mug.", expected="accept"),
            BenchUtterance(id="refused", text="Make me a sandwich.", expected="refuse"),
            BenchUtterance(id="broken", text="This request matches nothing.", expected="accept"),
        ),
    )


def test_run_bench_mixed_row(turtlebot_manifest: dict) -> None:
    provider = EchoProvider(
        responses={
            "mug": json.dumps(RED_MUG_PROGRAM),
            "sandwich": json.dumps(REFUSAL_PROGRAM),
        },
        match_substrings=True,
    )
    row = run_bench(
        bridge=_bridge(provider, turtlebot_manifest),
        corpus=_mixed_corpus(),
        backend="echo",
        model_id="echo-model",
        recorded_at="2026-09-25",
        notes="unit test",
    )
    assert row.n == 3
    assert row.counts["accepted"] == 1
    assert row.counts["honest_refusal"] == 1
    assert row.counts["provider_error"] == 1  # the bad row cost itself, not the run
    assert row.expected_match_rate == pytest.approx(2 / 3)
    assert row.revision_attempts_mean == pytest.approx(0.0)  # over the two returned rows
    assert row.row_id == "2026-09-25-echo-echo-model-mixed"


# ---------------------------------------------------------------------------
# Corpus loading
# ---------------------------------------------------------------------------


def test_load_corpus_legacy_conformance_fixture() -> None:
    corpus = load_corpus(CONFORMANCE_UTTERANCES)
    assert corpus.profile == "home"
    assert len(corpus.utterances) == 6
    kinds = {u.id: u.expected for u in corpus.utterances}
    assert kinds["red_mug"] == "accept"
    assert kinds["missing_capability"] == "refuse"


def test_load_repo_corpora() -> None:
    for name in ("home-en.yaml", "industrial-en.yaml"):
        corpus = load_corpus(BENCH_CORPORA / name)
        assert corpus.utterances
        assert {u.expected for u in corpus.utterances} == {"accept", "refuse"}


def test_load_corpus_rejects_bad_rows(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("utterances:\n  - id: a\n    text: hi\n", encoding="utf-8")
    with pytest.raises(BenchCorpusError, match="expected"):
        load_corpus(p)
    p.write_text(
        "utterances:\n"
        "  - {id: a, text: hi, expected: accept}\n"
        "  - {id: a, text: bye, expected: refuse}\n",
        encoding="utf-8",
    )
    with pytest.raises(BenchCorpusError, match="duplicate"):
        load_corpus(p)


# ---------------------------------------------------------------------------
# Row persistence + rendering
# ---------------------------------------------------------------------------


def test_row_roundtrip_and_table(tmp_path: Path, turtlebot_manifest: dict) -> None:
    provider = EchoProvider(
        responses={
            "mug": json.dumps(RED_MUG_PROGRAM),
            "sandwich": json.dumps(REFUSAL_PROGRAM),
        },
        match_substrings=True,
    )
    row = run_bench(
        bridge=_bridge(provider, turtlebot_manifest),
        corpus=_mixed_corpus(),
        backend="echo",
        model_id="echo-model",
        recorded_at="2026-09-25",
    )
    out = tmp_path / "rows" / f"{row.row_id}.yaml"
    write_row(row, out)
    assert out.is_file()

    rows = load_rows(out.parent)
    assert len(rows) == 1
    loaded = rows[0]
    assert loaded.counts == row.counts
    assert loaded.expected_match_rate == pytest.approx(row.expected_match_rate, abs=1e-4)

    table = render_table(rows)
    assert "| echo-model | echo | mixed | 3 |" in table
    assert "67%" in table

    report = render_row(row)
    assert "broken" in report and "provider_error" in report


def test_load_rows_missing_dir(tmp_path: Path) -> None:
    with pytest.raises(BenchCorpusError):
        load_rows(tmp_path / "nope")
