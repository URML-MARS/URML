"""Unit tests for the home-profile speak/listen primitives.

Authorized by RFC-0002 §Profile-extensibility (home: speak, listen).
Specified by spec/profiles/home/README.md §Layer-2 primitives this profile adds.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from urml_validator import ErrorCode, validate

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = Path(__file__).parent / "fixtures"


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture
def turtlebot_manifest() -> dict:
    """Home fixture manifest — declares `speech` output endpoint AND
    a `speech` sensor, so both speak and listen pass capability checks."""
    return _load_yaml(FIXTURE_ROOT / "manifests" / "turtlebot4_home.yaml")


@pytest.fixture
def home_envelope() -> dict:
    return _load_yaml(FIXTURE_ROOT / "envelopes" / "home_default.yaml")


def _program_with_step(step: dict[str, Any]) -> dict[str, Any]:
    """A minimal program wrapping a single step."""
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [step],
        },
    }


# ---------------------------------------------------------------------------
# speak
# ---------------------------------------------------------------------------


class TestSpeak:
    def test_speak_accepted_with_speech_endpoint(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        program = _program_with_step({"speak": {"utterance": "Hello."}})
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert result.accepted, result.codes()

    def test_speak_rejected_without_speech_endpoint(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        manifest = dict(turtlebot_manifest)
        manifest["outputs"] = {"named_endpoints": []}
        program = _program_with_step({"speak": {"utterance": "Hello."}})
        result = validate(program, manifest, home_envelope, profiles=("home",))
        assert not result.accepted
        assert ErrorCode.CAPABILITY_MISSING_SPEECH_OUTPUT.value in result.codes()

    def test_speak_requires_non_empty_utterance(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        program = _program_with_step({"speak": {"utterance": ""}})
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert not result.accepted
        # Empty utterance fails Pass 1 (argument typing).
        assert any(c.startswith("argument.") for c in result.codes())

    def test_speak_style_options(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        for style in ("notice", "warning", "conversational"):
            program = _program_with_step({"speak": {"utterance": "test", "style": style}})
            result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
            assert result.accepted, f"style={style}: {result.codes()}"

    def test_speak_interrupt_flag(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        program = _program_with_step({"speak": {"utterance": "Stop.", "interrupt": True}})
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert result.accepted, result.codes()


# ---------------------------------------------------------------------------
# listen
# ---------------------------------------------------------------------------


class TestListen:
    def test_listen_accepted_with_speech_sensor(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        program = _program_with_step({"listen": {"prompt": "Yes or no?"}})
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert result.accepted, result.codes()

    def test_listen_rejected_without_speech_sensor(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        manifest = {
            **turtlebot_manifest,
            "perception": {**turtlebot_manifest["perception"], "sensors": []},
        }
        program = _program_with_step({"listen": {"prompt": "Yes?"}})
        result = validate(program, manifest, home_envelope, profiles=("home",))
        assert not result.accepted
        assert ErrorCode.CAPABILITY_MISSING_SPEECH_INPUT.value in result.codes()

    def test_listen_choice_requires_choices(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        program = _program_with_step({"listen": {"expected": "choice"}})
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert not result.accepted
        # Missing `choices` for expected=choice fails Pass 1.
        assert any(c.startswith("argument.") for c in result.codes())

    def test_listen_choices_only_with_choice_mode(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        program = _program_with_step(
            {"listen": {"expected": "free_form", "choices": ["yes", "no"]}}
        )
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert not result.accepted
        assert any(c.startswith("argument.") for c in result.codes())

    def test_listen_with_choice_and_choices(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        program = _program_with_step(
            {"listen": {"expected": "choice", "choices": ["mug", "cup"], "store_as": "pick"}}
        )
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert result.accepted, result.codes()

    def test_listen_store_as_creates_binding(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        """A subsequent step can reference $pick after listen(store_as: pick)."""
        program = {
            "profile": "home",
            "behavior": {
                "type": "sequence",
                "on_error": "abort_and_report",
                "steps": [
                    {"listen": {"expected": "free_form", "store_as": "user_text"}},
                    {
                        "report": {
                            "to": "log",
                            "facts": {"got": "see binding via path string $user_text"},
                            "attachments": ["$user_text"],
                        }
                    },
                ],
            },
        }
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert result.accepted, result.codes()


# ---------------------------------------------------------------------------
# Conversation flow: speak + listen + branch
# ---------------------------------------------------------------------------


class TestConversation:
    def test_speak_then_listen_then_report(
        self, turtlebot_manifest: dict, home_envelope: dict
    ) -> None:
        program = {
            "profile": "home",
            "behavior": {
                "type": "sequence",
                "on_error": "abort_and_report",
                "steps": [
                    {"speak": {"utterance": "What can I do for you?"}},
                    {"listen": {"expected": "free_form", "store_as": "request"}},
                    {
                        "report": {
                            "to": "log",
                            "facts": {"user_request": "stored"},
                            "attachments": ["$request"],
                        }
                    },
                ],
            },
        }
        result = validate(program, turtlebot_manifest, home_envelope, profiles=("home",))
        assert result.accepted, result.codes()
