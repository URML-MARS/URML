"""LLM-bridge conformance sub-suite (RFC-0021).

Per-model scoring of ``(model, backend, profile)`` triples. The runner
calls a real ``LLMProvider`` through ``urml_llm_bridge.Bridge`` and tallies
structural and semantic pass rates per profile. See
[`conformance/llm-bridge/README.md`](../../../llm-bridge/README.md) for the
on-disk layout, row schema, and the published-results convention.

This package ships the fixture-loader and the dataclass schema in v0.1.
The real-model scoring runner lands in a follow-up commit so this RFC
PR does not require GGUF artifacts in CI.
"""

from urml_conformance.llm_bridge.loader import (
    ConformanceLoaderError,
    ExpectedKind,
    ResultRow,
    Utterance,
    UtteranceSet,
    load_results_for_date,
    load_utterances,
)

__all__ = [
    "ConformanceLoaderError",
    "ExpectedKind",
    "ResultRow",
    "Utterance",
    "UtteranceSet",
    "load_results_for_date",
    "load_utterances",
]
