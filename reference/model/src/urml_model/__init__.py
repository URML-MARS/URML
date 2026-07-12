"""urml-model — dataset synthesis pipeline for a URML-native small model (RFC-0666).

The validator is the labeling oracle: every (natural language, program,
manifest) triple in a dataset produced here passed `urml_validator.validate`
at synthesis time, and every rejected bridge emission becomes a repair
example carrying the validator's machine-readable error codes.

This package never trains a model, never downloads weights, and never
calls a specific LLM vendor. It mines the repository's gold assets,
back-translates programs into utterances (deterministic templates in CI,
any `LLMProvider` at scale), filters through the oracle, and exports the
formats fine-tuning frameworks consume. The training itself is
operator-action, documented in ``docs/training-recipe.md``.
"""

from __future__ import annotations

from urml_model.backtranslate import BackTranslator, LLMBackTranslator, TemplateBackTranslator
from urml_model.dataset import Dataset, DatasetRecord, Provenance, ValidatorVerdict
from urml_model.export import export_dpo, export_sft
from urml_model.mining import (
    GoldExample,
    mine_few_shot_pairs,
    mine_fixture_programs,
    resolve_envelope_ref,
    resolve_manifest_ref,
)
from urml_model.rejections import RejectionSession, mine_rejections, session_from_result
from urml_model.synthesize import SynthesisReport, synthesize

__all__ = [
    "BackTranslator",
    "Dataset",
    "DatasetRecord",
    "GoldExample",
    "LLMBackTranslator",
    "Provenance",
    "RejectionSession",
    "SynthesisReport",
    "TemplateBackTranslator",
    "ValidatorVerdict",
    "export_dpo",
    "export_sft",
    "mine_few_shot_pairs",
    "mine_fixture_programs",
    "mine_rejections",
    "resolve_envelope_ref",
    "resolve_manifest_ref",
    "session_from_result",
    "synthesize",
]
