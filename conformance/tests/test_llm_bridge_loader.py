"""LLM-bridge conformance loader tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from urml_conformance.llm_bridge.loader import (
    ConformanceLoaderError,
    load_results_for_date,
    load_utterances,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LLM_BRIDGE_ROOT = REPO_ROOT / "conformance" / "llm-bridge"
FIXTURES = LLM_BRIDGE_ROOT / "fixtures"
RESULTS = LLM_BRIDGE_ROOT / "results"


def test_home_english_utterances_load() -> None:
    s = load_utterances(FIXTURES, profile="home", language="en")
    assert s.profile == "home"
    assert s.language == "en"
    assert s.manifest == "turtlebot4_home"
    assert len(s.utterances) >= 4
    ids = {u.id for u in s.utterances}
    assert "red_mug" in ids
    # Both expected_kind values are exercised by the shipped fixture.
    kinds = {u.expected_kind for u in s.utterances}
    assert kinds == {"positive", "report_failure"}


def test_missing_profile_raises() -> None:
    with pytest.raises(ConformanceLoaderError, match="no utterance fixture"):
        load_utterances(FIXTURES, profile="nonexistent", language="en")


def test_missing_results_date_returns_empty_list() -> None:
    rows = load_results_for_date(RESULTS, date="2026-01-01")
    assert rows == []


def test_malformed_utterance_yaml_raises(tmp_path: Path) -> None:
    bad_fixture = tmp_path / "home" / "utterances-en.yaml"
    bad_fixture.parent.mkdir(parents=True)
    bad_fixture.write_text(
        "profile: home\nlanguage: en\nmanifest: x\nutterances:\n  - id: a\n    text: hi\n    expected_kind: maybe\n",
        encoding="utf-8",
    )
    with pytest.raises(ConformanceLoaderError, match="expected_kind"):
        load_utterances(tmp_path, profile="home", language="en")
