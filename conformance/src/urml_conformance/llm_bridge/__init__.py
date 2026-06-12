"""LLM-bridge conformance sub-suite (RFC-0021).

Per-model scoring of ``(model, backend, profile)`` triples. The runner
calls a real ``LLMProvider`` through ``urml_llm_bridge.Bridge`` and tallies
structural and semantic pass rates per profile. See
[`conformance/llm-bridge/README.md`](../../../llm-bridge/README.md) for the
on-disk layout, row schema, and the published-results convention.

This package ships the fixture-loader, the dataclass schema, and a
backend-neutral scoring harness (``score``) in v0.1, with one hermetic
echo-backend result row exercising the parametrization path. Populating the
published table with real-model rows (which require a GGUF artifact and a
running server) is a follow-up project, kept out of CI.

The ``loader`` is dependency-light (PyYAML + dataclasses) so docs tooling can
read the published table without the bridge. ``score`` lazy-imports
``urml_llm_bridge``; install the optional ``urml-conformance[llm-bridge]`` extra.
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
from urml_conformance.llm_bridge.scorer import Backend, score

__all__ = [
    "Backend",
    "ConformanceLoaderError",
    "ExpectedKind",
    "ResultRow",
    "Utterance",
    "UtteranceSet",
    "load_results_for_date",
    "load_utterances",
    "score",
]
