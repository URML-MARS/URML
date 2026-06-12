"""LLM-bridge scorer tests (RFC-0021).

Exercises the backend-neutral scoring harness over the hermetic ``EchoProvider``
— no network, no GGUF, no running server. Skipped if the optional
``urml-conformance[llm-bridge]`` extra (i.e. ``urml_llm_bridge``) is not present.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

pytest.importorskip("urml_llm_bridge", reason="install urml-conformance[llm-bridge] to run the scorer")

from urml_conformance.llm_bridge import ResultRow, load_results_for_date, load_utterances, score
from urml_llm_bridge import EchoProvider

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LLM_BRIDGE_ROOT = REPO_ROOT / "conformance" / "llm-bridge"
MANIFESTS = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures" / "manifests"

# A validator-accepted home program the echo double returns for any positive
# utterance (echo is a dumb double; semantic fidelity to the text is not the
# point — exercising the harness is).
_POSITIVE = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"move_to": {"location": "kitchen"}},
            {"detect": {"object": "mug", "attributes": {"color": "red"}, "store_as": "m"}},
            {"grasp": {"target": "$m", "force": "gentle"}},
            {"move_to": {"location": "user", "carrying": "$m"}},
            {"release": {"mode": "hand_to_user"}},
        ],
    },
}

# An honest decline: a report(status: failure) naming the gap, not invented capability.
_REPORT_FAILURE = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [
            {"report": {"to": "user", "facts": {"reason": "capability_not_in_manifest"}, "status": "failure"}}
        ],
    },
}

# Substring -> canned emission. Every home utterance text contains exactly one key.
_ECHO_RESPONSES = {
    "red mug": json.dumps(_POSITIVE),
    "blue mug": json.dumps(_POSITIVE),
    "hello": json.dumps(_POSITIVE),
    "Come to me": json.dumps(_POSITIVE),
    "sandwich": json.dumps(_REPORT_FAILURE),
    "attic": json.dumps(_REPORT_FAILURE),
}


def _manifest() -> dict:
    return yaml.safe_load((MANIFESTS / "turtlebot4_home.yaml").read_text(encoding="utf-8"))


def test_echo_backend_scores_clean() -> None:
    utterances = load_utterances(LLM_BRIDGE_ROOT / "fixtures", profile="home", language="en")
    provider = EchoProvider(responses=_ECHO_RESPONSES, match_substrings=True)
    row = score(
        provider=provider,
        utterances=utterances,
        manifest=_manifest(),
        backend="echo",
        model_id="echo-double",
        recorded_at="2026-06-07T00:00:00Z",
        policy=None,
    )
    assert isinstance(row, ResultRow)
    assert row.backend == "echo"
    assert row.profile == "home"
    assert row.n_utterances == len(utterances.utterances)
    # Canned-correct echo: every emission is structurally valid and the outcome
    # matches expected_kind (positives accepted, report_failures decline cleanly),
    # accepted first try.
    assert row.structural_pass_rate == 1.0
    assert row.semantic_pass_rate == 1.0
    assert row.revision_attempts_mean == 0.0


def test_committed_echo_row_loads_and_matches() -> None:
    rows = load_results_for_date(LLM_BRIDGE_ROOT / "results", date="2026-06-07")
    echo_rows = [r for r in rows if r.backend == "echo"]
    assert echo_rows, "expected at least one committed echo-backend row under results/2026-06-07/"
    r = echo_rows[0]
    assert r.profile == "home"
    assert r.structural_pass_rate == 1.0
    assert r.semantic_pass_rate == 1.0
    assert r.revision_attempts_mean == 0.0
