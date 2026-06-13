"""RFC-0304 — language.translation_alternatives + the open_llm engine class.

Turns RFC-0268's commercial-use-gate hard failure into a fork: a commercial
deployment with a CC-BY-NC translation substrate (NLLB) validates if it also
declares a commercial-eligible permissive alternative (Qwen / Gemma open LLM).
The path the NLLB-200 maintainer recommended on RFC-0167.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import validate
from urml_validator.errors import ErrorCode
from urml_validator.schemas.manifest import CapabilityManifest

_BASE = {
    "manifest_version": "0.1",
    "robot_id": "ta_test",
    "mobility": {"drive_type": "differential", "max_velocity": 0.5},
    "frames": [{"name": "map", "parent": None}],
    "declared_locations": [{"name": "kitchen", "pose": {"x": 1.0, "y": 1.0}, "frame": "map"}],
}
_PROG = {
    "profile": "home",
    "behavior": {"type": "sequence", "on_error": "abort_and_report",
                 "steps": [{"move_to": {"location": "kitchen"}}]},
}
_NLLB_GATED = {"components": [{"name": "nllb_200", "license": "cc_by_nc_4_0",
                              "boundary": "cross_citation", "commercial_use_gate": True}]}
_OPEN_LLM_ALT = {"engine_class": "open_llm", "engine_class_note": "Qwen3.5-Instruct, Apache-2.0",
                 "commercial_eligible": True, "target_languages": ["en"]}


def _codes(issues) -> list[str]:
    return [i.code.value for i in issues]


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_open_llm_primary_requires_note():
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate({**_BASE, "language": {"translation_engine_class": "open_llm"}})


def test_open_llm_primary_with_note_parses():
    CapabilityManifest.model_validate(
        {**_BASE, "language": {"translation_engine_class": "open_llm",
                               "translation_engine_class_note": "Gemma 4, permissive"}}
    )


def test_alternative_open_llm_requires_note():
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(
            {**_BASE, "language": {"translation_alternatives": [
                {"engine_class": "open_llm", "commercial_eligible": True}]}}
        )


def test_alternative_commercial_eligible_required():
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(
            {**_BASE, "language": {"translation_alternatives": [
                {"engine_class": "opus_mt"}]}}  # missing commercial_eligible
        )


def test_full_alternative_parses():
    CapabilityManifest.model_validate(
        {**_BASE, "language": {"translation_engine_class": "nllb",
                               "translation_alternatives": [_OPEN_LLM_ALT]}}
    )


# ---------------------------------------------------------------------------
# The commercial-use-gate fork (the payoff)
# ---------------------------------------------------------------------------


def _commercial(language: dict, licensing: dict) -> dict:
    return {**_BASE, "deployment": {"commercial_use": True}, "language": language, "licensing": licensing}


def test_nllb_no_alternative_rejected_under_policy():
    # Status quo from RFC-0268: commercial + gated NLLB, no fork -> hard fail.
    m = _commercial({"translation_engine_class": "nllb"}, _NLLB_GATED)
    r = validate(_PROG, m, profiles=("home",), policy="DEFAULT")
    assert not r.accepted
    assert ErrorCode.POLICY_COMMERCIAL_USE_GATE_VIOLATED.value in _codes(r.errors)


def test_nllb_with_permissive_alternative_accepted_under_policy():
    # The fork: a declared commercial-eligible alternative satisfies the gate.
    m = _commercial({"translation_engine_class": "nllb", "translation_alternatives": [_OPEN_LLM_ALT]},
                    _NLLB_GATED)
    r = validate(_PROG, m, profiles=("home",), policy="DEFAULT")
    assert r.accepted
    assert ErrorCode.CAPABILITY_COMMERCIAL_GATE_SATISFIED_BY_ALTERNATIVE.value in _codes(r.warnings)
    assert ErrorCode.POLICY_COMMERCIAL_USE_GATE_VIOLATED.value not in _codes(r.errors)


def test_open_llm_primary_permissive_accepted_under_policy():
    # open_llm as the primary with a permissive (non-gated) licensing component.
    lang = {"translation_engine_class": "open_llm", "translation_engine_class_note": "Qwen3.5, Apache-2.0"}
    lic = {"components": [{"name": "qwen", "license": "apache_2_0", "boundary": "cross_citation",
                           "commercial_use_gate": False}]}
    m = _commercial(lang, lic)
    r = validate(_PROG, m, profiles=("home",), policy="DEFAULT")
    assert r.accepted


def test_non_translation_gated_component_not_excused():
    # A permissive translation alternative does not excuse an unrelated gated component.
    lang = {"translation_engine_class": "nllb", "translation_alternatives": [_OPEN_LLM_ALT]}
    lic = {"components": [{"name": "some_gpl_tool", "license": "gpl_3_0", "boundary": "subprocess",
                           "commercial_use_gate": True}]}
    m = _commercial(lang, lic)
    r = validate(_PROG, m, profiles=("home",), policy="DEFAULT")
    assert not r.accepted
    assert ErrorCode.POLICY_COMMERCIAL_USE_GATE_VIOLATED.value in _codes(r.errors)


def test_noncommercial_nllb_no_alternative_accepted():
    # RFC-0268: a non-commercial deployment needs no alternative.
    m = {**_BASE, "deployment": {"commercial_use": False},
         "language": {"translation_engine_class": "nllb"}, "licensing": _NLLB_GATED}
    r = validate(_PROG, m, profiles=("home",), policy="DEFAULT")
    assert r.accepted


def test_alternative_without_commercial_eligible_does_not_satisfy():
    # An alternative that is not commercial_eligible does not open the fork.
    alt = {"engine_class": "argos_translate", "commercial_eligible": False, "target_languages": ["en"]}
    m = _commercial({"translation_engine_class": "nllb", "translation_alternatives": [alt]}, _NLLB_GATED)
    r = validate(_PROG, m, profiles=("home",), policy="DEFAULT")
    assert not r.accepted
    assert ErrorCode.POLICY_COMMERCIAL_USE_GATE_VIOLATED.value in _codes(r.errors)
