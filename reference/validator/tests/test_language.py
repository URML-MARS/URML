"""RFC-0260 — Layer-4 NL-infrastructure `language` block.

Covers the schema (closed enums, custom-requires-note), the manifest-static
advisories/consistency warnings, the listen/speak engine-undeclared
suggestions, and the US-federal `vosk` origin gate (default-policy only).
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError as PydanticValidationError

from urml_validator import validate
from urml_validator.errors import ErrorCode
from urml_validator.schemas.manifest import CapabilityManifest

_BASE = {
    "manifest_version": "0.1",
    "robot_id": "lang_test",
    "mobility": {"drive_type": "differential", "max_velocity": 0.5},
    "frames": [{"name": "map", "parent": None}],
    "declared_locations": [{"name": "kitchen", "pose": {"x": 1.0, "y": 1.0}, "frame": "map"}],
}
_MOVE_PROG = {
    "profile": "home",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [{"move_to": {"location": "kitchen"}}],
    },
}


def _manifest(language: dict) -> dict:
    return {**_BASE, "language": language}


def _codes(issues) -> list[str]:
    return [i.code.value for i in issues]


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


def test_whisper_stt_parses():
    CapabilityManifest.model_validate(_manifest({"stt_engine_class": "whisper"}))


def test_full_engine_options_parse():
    CapabilityManifest.model_validate(
        _manifest(
            {
                "stt_engine_class": "whisper_cpp",
                "tts_engine_class": "espeak",
                "translation_engine_class": "opus_mt",
                "engine_options": {
                    "stt": {"inference_runtime": "embedded", "quantization_level": "int4",
                            "latency_class": "offline", "model_size": "tiny"},
                    "tts": {"voice_id": "en", "sample_rate_hz": 22050},
                    "translation": {"source_languages": ["en", "he"], "target_languages": ["en"],
                                    "offline_capable": True},
                },
            }
        )
    )


@pytest.mark.parametrize(
    "language",
    [
        {"stt_engine_class": "custom"},
        {"tts_engine_class": "custom"},
        {"translation_engine_class": "custom"},
    ],
)
def test_custom_requires_note(language):
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(_manifest(language))


def test_custom_with_note_ok():
    CapabilityManifest.model_validate(
        _manifest({"stt_engine_class": "custom", "stt_engine_class_note": "in-house STT"})
    )


def test_unknown_engine_class_rejected():
    with pytest.raises(PydanticValidationError):
        CapabilityManifest.model_validate(_manifest({"stt_engine_class": "deepspeech"}))


# ---------------------------------------------------------------------------
# vosk origin gate (default policy only)
# ---------------------------------------------------------------------------


def test_vosk_rejected_under_default_policy():
    r = validate(_MOVE_PROG, _manifest({"stt_engine_class": "vosk"}), profiles=("home",), policy="DEFAULT")
    assert not r.accepted
    assert ErrorCode.POLICY_STT_ENGINE_ORIGIN_DENIED.value in _codes(r.errors)


def test_vosk_accepted_without_policy():
    r = validate(_MOVE_PROG, _manifest({"stt_engine_class": "vosk"}), profiles=("home",), policy=None)
    assert r.accepted


def test_vosk_accepted_under_custom_policy():
    custom = {"policy_id": "custom_permissive", "rules": []}
    r = validate(_MOVE_PROG, _manifest({"stt_engine_class": "vosk"}), profiles=("home",), policy=custom)
    assert r.accepted  # the gate fires only under the bundled US-federal default


def test_whisper_accepted_under_default_policy():
    r = validate(_MOVE_PROG, _manifest({"stt_engine_class": "whisper"}), profiles=("home",), policy="DEFAULT")
    assert r.accepted


# ---------------------------------------------------------------------------
# License advisories + consistency (warnings)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "language",
    [
        {"tts_engine_class": "piper"},
        {"translation_engine_class": "nllb", "engine_options": {"translation": {"target_languages": ["en"]}}},
        {"translation_engine_class": "libretranslate", "engine_options": {"translation": {"target_languages": ["en"]}}},
    ],
)
def test_license_advisory_warns_but_accepts(language):
    r = validate(_MOVE_PROG, _manifest(language), profiles=("home",), policy=None)
    assert r.accepted
    assert ErrorCode.CAPABILITY_ENGINE_LICENSE_ADVISORY.value in _codes(r.warnings)


def test_translation_empty_target_languages_warns():
    lang = {"translation_engine_class": "opus_mt", "engine_options": {"translation": {"source_languages": ["en"]}}}
    r = validate(_MOVE_PROG, _manifest(lang), profiles=("home",), policy=None)
    assert r.accepted
    assert ErrorCode.CAPABILITY_TRANSLATION_LANGUAGES_INCONSISTENT.value in _codes(r.warnings)


def test_opus_mt_with_targets_no_advisory():
    lang = {"translation_engine_class": "opus_mt", "engine_options": {"translation": {"target_languages": ["en"]}}}
    r = validate(_MOVE_PROG, _manifest(lang), profiles=("home",), policy=None)
    assert r.accepted
    assert ErrorCode.CAPABILITY_ENGINE_LICENSE_ADVISORY.value not in _codes(r.warnings)


# ---------------------------------------------------------------------------
# listen / speak engine-undeclared suggestion
# ---------------------------------------------------------------------------


def test_listen_without_stt_engine_warns():
    prog = {
        "profile": "home",
        "behavior": {"type": "sequence", "on_error": "abort_and_report",
                     "steps": [{"listen": {"prompt": "say a command", "store_as": "cmd"}}]},
    }
    r = validate(prog, _BASE, profiles=("home",), policy=None)
    assert ErrorCode.CAPABILITY_STT_ENGINE_UNDECLARED.value in _codes(r.warnings)


def test_speak_without_tts_engine_warns():
    prog = {
        "profile": "home",
        "behavior": {"type": "sequence", "on_error": "abort_and_report",
                     "steps": [{"speak": {"utterance": "hello"}}]},
    }
    r = validate(prog, _BASE, profiles=("home",), policy=None)
    assert ErrorCode.CAPABILITY_TTS_ENGINE_UNDECLARED.value in _codes(r.warnings)


def test_speak_with_tts_engine_no_warning():
    prog = {
        "profile": "home",
        "behavior": {"type": "sequence", "on_error": "abort_and_report",
                     "steps": [{"speak": {"utterance": "hello"}}]},
    }
    r = validate(prog, _manifest({"tts_engine_class": "espeak"}), profiles=("home",), policy=None)
    assert ErrorCode.CAPABILITY_TTS_ENGINE_UNDECLARED.value not in _codes(r.warnings)


def test_move_program_no_language_no_language_warnings():
    r = validate(_MOVE_PROG, _BASE, profiles=("home",), policy=None)
    lang_codes = {
        ErrorCode.CAPABILITY_STT_ENGINE_UNDECLARED.value,
        ErrorCode.CAPABILITY_TTS_ENGINE_UNDECLARED.value,
        ErrorCode.CAPABILITY_ENGINE_LICENSE_ADVISORY.value,
    }
    assert not (lang_codes & set(_codes(r.warnings)))
