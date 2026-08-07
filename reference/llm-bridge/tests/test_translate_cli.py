"""`urml translate` CLI subcommand tests.

The subcommand lives in `urml_validator.cli`; this test module is in the
bridge package because exercising it end-to-end requires both
`urml-validator` and `urml-llm-bridge` to be installed. The bridge's venv
has both.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
import yaml
from urml_validator.cli import main

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"

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


@pytest.fixture
def manifest_path() -> Path:
    return VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home.yaml"


@pytest.fixture
def envelope_path() -> Path:
    return VALIDATOR_FIXTURES / "envelopes" / "home_default.yaml"


@pytest.fixture
def echo_response_file(tmp_path: Path) -> Path:
    """A JSON file containing the canned EchoProvider response."""
    path = tmp_path / "echo-response.json"
    path.write_text(json.dumps(RED_MUG_PROGRAM), encoding="utf-8")
    return path


@pytest.fixture
def echo_response_yaml_file(tmp_path: Path) -> Path:
    """A YAML file containing the canned response."""
    path = tmp_path / "echo-response.yaml"
    path.write_text(yaml.safe_dump(RED_MUG_PROGRAM), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_translate_echo_accepts(
    manifest_path: Path,
    envelope_path: Path,
    echo_response_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "Bring me the red mug from the kitchen.",
        "--manifest", str(manifest_path),
        "--envelope", str(envelope_path),
        "--profile", "home",
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
    ])
    captured = capsys.readouterr()
    assert rc == 0, f"stderr={captured.err}"
    # Default output is YAML on stdout.
    assert "profile: home" in captured.out
    assert "move_to" in captured.out
    # Status banner goes to stderr.
    assert "Translation accepted" in captured.err


def test_translate_echo_accepts_yaml_response_file(
    manifest_path: Path,
    envelope_path: Path,
    echo_response_yaml_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--echo-response-file accepts YAML, not just JSON."""
    rc = main([
        "translate",
        "Bring me the red mug.",
        "--manifest", str(manifest_path),
        "--envelope", str(envelope_path),
        "--profile", "home",
        "--provider", "echo",
        "--echo-response-file", str(echo_response_yaml_file),
    ])
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "profile: home" in captured.out


def test_translate_json_output(
    manifest_path: Path,
    envelope_path: Path,
    echo_response_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "Bring me the red mug.",
        "--manifest", str(manifest_path),
        "--envelope", str(envelope_path),
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
        "--json",
    ])
    captured = capsys.readouterr()
    assert rc == 0
    payload = json.loads(captured.out)
    assert payload["profile"] == "home"
    assert payload["behavior"]["type"] == "sequence"


def test_translate_out_file(
    tmp_path: Path,
    manifest_path: Path,
    envelope_path: Path,
    echo_response_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    out_path = tmp_path / "subdir" / "result.yaml"  # also tests parent-dir creation
    rc = main([
        "translate",
        "Bring me the red mug.",
        "--manifest", str(manifest_path),
        "--envelope", str(envelope_path),
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
        "--out", str(out_path),
    ])
    captured = capsys.readouterr()
    assert rc == 0
    assert out_path.is_file()
    assert "wrote" in captured.err
    parsed = yaml.safe_load(out_path.read_text(encoding="utf-8"))
    assert parsed == RED_MUG_PROGRAM


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


def test_translate_revision_exhausted(
    tmp_path: Path,
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Echo provider returns a known-bad program; validator rejects; only one
    scripted response means the revision loop exhausts immediately."""
    bad_program = json.loads(json.dumps(RED_MUG_PROGRAM))
    bad_program["behavior"]["steps"][0]["move_to"]["location"] = "the_moon"
    response_file = tmp_path / "bad.json"
    response_file.write_text(json.dumps(bad_program), encoding="utf-8")
    rc = main([
        "translate",
        "Bring me the red mug.",
        "--manifest", str(manifest_path),
        "--provider", "echo",
        "--echo-response-file", str(response_file),
        "--max-revisions", "0",  # no revisions; first failure is fatal
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert "translation failed" in captured.err.lower()
    assert "capability.missing_location" in captured.err


def test_translate_save_rejected_writes_emission(
    tmp_path: Path,
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """On failure, --save-rejected writes the model's final rejected emission
    with a DO-NOT-EXECUTE banner."""
    bad_program = json.loads(json.dumps(RED_MUG_PROGRAM))
    bad_program["behavior"]["steps"][0]["move_to"]["location"] = "the_moon"
    response_file = tmp_path / "bad.json"
    response_file.write_text(json.dumps(bad_program), encoding="utf-8")
    rejected_path = tmp_path / "rejected.txt"
    rc = main([
        "translate",
        "Bring me the red mug.",
        "--manifest", str(manifest_path),
        "--provider", "echo",
        "--echo-response-file", str(response_file),
        "--max-revisions", "0",
        "--save-rejected", str(rejected_path),
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert rejected_path.is_file()
    text = rejected_path.read_text(encoding="utf-8")
    assert "DO NOT EXECUTE" in text
    # The actual rejected emission is preserved verbatim after the banner.
    assert "the_moon" in text
    assert "wrote rejected emission" in captured.err


def test_translate_save_rejected_absent_on_success(
    tmp_path: Path,
    manifest_path: Path,
    envelope_path: Path,
    echo_response_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--save-rejected writes nothing when the translation succeeds."""
    rejected_path = tmp_path / "rejected.txt"
    rc = main([
        "translate",
        "Bring me the red mug from the kitchen.",
        "--manifest", str(manifest_path),
        "--envelope", str(envelope_path),
        "--profile", "home",
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
        "--save-rejected", str(rejected_path),
    ])
    assert rc == 0
    assert not rejected_path.exists()


def test_translate_echo_requires_response_file(
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "request",
        "--manifest", str(manifest_path),
        "--provider", "echo",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "--echo-response-file" in captured.err


def test_translate_missing_manifest(
    tmp_path: Path,
    echo_response_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "request",
        "--manifest", str(tmp_path / "missing.yaml"),
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "manifest file not found" in captured.err.lower()


def test_translate_missing_echo_response_file(
    manifest_path: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "request",
        "--manifest", str(manifest_path),
        "--provider", "echo",
        "--echo-response-file", str(tmp_path / "nope.json"),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "echo-response file not found" in captured.err.lower()


def test_translate_anthropic_needs_api_key(
    manifest_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    rc = main([
        "translate",
        "request",
        "--manifest", str(manifest_path),
        "--provider", "anthropic",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "ANTHROPIC_API_KEY" in captured.err


def test_translate_openai_needs_api_key(
    manifest_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    # A base URL (flag or env) relaxes the key requirement; make sure the
    # developer's real environment can't flip this test onto that path.
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    rc = main([
        "translate",
        "request",
        "--manifest", str(manifest_path),
        "--provider", "openai",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "OPENAI_API_KEY" in captured.err


# ---------------------------------------------------------------------------
# Local providers (ollama, llama_cpp, OpenAI-compatible servers)
# ---------------------------------------------------------------------------


def _make_recorder() -> tuple[type, list[dict[str, Any]]]:
    """A stand-in provider class: records constructor kwargs, emits the
    canned red-mug program so the translation succeeds end-to-end."""
    calls: list[dict[str, Any]] = []

    class _Recorder:
        def __init__(self, **kwargs: Any) -> None:
            calls.append(kwargs)

        def complete(
            self, *, system: str, user: str, schema: dict[str, Any], max_tokens: int = 4096
        ) -> str:
            return json.dumps(RED_MUG_PROGRAM)

    return _Recorder, calls


def _translate_args(manifest_path: Path, envelope_path: Path, *extra: str) -> list[str]:
    return [
        "translate",
        "Bring me the red mug from the kitchen.",
        "--manifest", str(manifest_path),
        "--envelope", str(envelope_path),
        "--profile", "home",
        *extra,
    ]


def test_translate_ollama_end_to_end_with_stub(
    manifest_path: Path,
    envelope_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    recorder, calls = _make_recorder()
    monkeypatch.setattr("urml_llm_bridge.providers.ollama.OllamaProvider", recorder)
    rc = main(_translate_args(
        manifest_path, envelope_path,
        "--provider", "ollama", "--model", "llama3.2:1b",
    ))
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "profile: home" in captured.out
    assert calls == [{"model": "llama3.2:1b"}]  # no base_url: provider default applies


def test_translate_ollama_base_url_plumbed(
    manifest_path: Path,
    envelope_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, calls = _make_recorder()
    monkeypatch.setattr("urml_llm_bridge.providers.ollama.OllamaProvider", recorder)
    rc = main(_translate_args(
        manifest_path, envelope_path,
        "--provider", "ollama", "--model", "m", "--base-url", "http://127.0.0.1:9999",
    ))
    assert rc == 0
    assert calls == [{"model": "m", "base_url": "http://127.0.0.1:9999"}]


def test_translate_ollama_requires_model(
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "request",
        "--manifest", str(manifest_path),
        "--provider", "ollama",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "--model" in captured.err
    assert "ollama list" in captured.err


def test_translate_llama_cpp_end_to_end_with_stub(
    manifest_path: Path,
    envelope_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    recorder, calls = _make_recorder()
    monkeypatch.setattr("urml_llm_bridge.providers.llama_cpp.LlamaCppProvider", recorder)
    # No --model needed: llama-server's loaded GGUF is fixed at launch.
    rc = main(_translate_args(manifest_path, envelope_path, "--provider", "llama_cpp"))
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert calls == [{}]

    calls.clear()
    rc = main(_translate_args(
        manifest_path, envelope_path,
        "--provider", "llama_cpp", "--model", "smollm-360m",
    ))
    assert rc == 0
    assert calls == [{"model_label": "smollm-360m"}]


def test_translate_llama_cpp_base_url_plumbed(
    manifest_path: Path,
    envelope_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, calls = _make_recorder()
    monkeypatch.setattr("urml_llm_bridge.providers.llama_cpp.LlamaCppProvider", recorder)
    rc = main(_translate_args(
        manifest_path, envelope_path,
        "--provider", "llama_cpp", "--base-url", "http://gpu-box:8081",
    ))
    assert rc == 0
    assert calls == [{"base_url": "http://gpu-box:8081"}]


@pytest.mark.parametrize("provider", ["anthropic", "echo"])
def test_translate_base_url_rejected_for_remote_and_echo(
    provider: str,
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "request",
        "--manifest", str(manifest_path),
        "--provider", provider,
        "--base-url", "http://127.0.0.1:9999",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "--base-url is only meaningful" in captured.err
    assert "ollama" in captured.err


def test_translate_ollama_httpx_missing_hint(
    manifest_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """When httpx is absent, provider construction raises ImportError; the CLI
    maps it to exit 2 with the pip-extra hint."""

    class _Unconstructable:
        def __init__(self, **kwargs: Any) -> None:
            raise ImportError("No module named 'httpx'")

    monkeypatch.setattr("urml_llm_bridge.providers.ollama.OllamaProvider", _Unconstructable)
    rc = main([
        "translate",
        "request",
        "--manifest", str(manifest_path),
        "--provider", "ollama", "--model", "m",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "urml-llm-bridge[ollama]" in captured.err


def test_translate_openai_no_key_with_base_url_env(
    manifest_path: Path,
    envelope_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """OPENAI_BASE_URL alone unlocks the openai provider (LM Studio, vLLM)."""
    recorder, calls = _make_recorder()
    monkeypatch.setattr("urml_llm_bridge.providers.openai.OpenAIProvider", recorder)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_BASE_URL", "http://127.0.0.1:1234/v1")
    rc = main(_translate_args(
        manifest_path, envelope_path,
        "--provider", "openai", "--model", "qwen3.5:9b",
    ))
    assert rc == 0
    # The SDK reads OPENAI_BASE_URL itself, so no base_url kwarg is passed;
    # the placeholder key satisfies the SDK's non-None requirement.
    assert calls == [{"model": "qwen3.5:9b", "api_key": "urml-local-no-key"}]


def test_translate_openai_no_key_with_base_url_flag(
    manifest_path: Path,
    envelope_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, calls = _make_recorder()
    monkeypatch.setattr("urml_llm_bridge.providers.openai.OpenAIProvider", recorder)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    rc = main(_translate_args(
        manifest_path, envelope_path,
        "--provider", "openai", "--base-url", "http://127.0.0.1:1234/v1",
    ))
    assert rc == 0
    assert calls == [{"base_url": "http://127.0.0.1:1234/v1", "api_key": "urml-local-no-key"}]


# ---------------------------------------------------------------------------
# Speech input (RFC-0670)
# ---------------------------------------------------------------------------


def _make_speech_recorder(transcript: str) -> tuple[type, dict[str, Any]]:
    """A stand-in speech provider class: records constructor and transcribe
    kwargs, returns a fixed transcript."""
    seen: dict[str, Any] = {}

    class _Recorder:
        def __init__(self, **kwargs: Any) -> None:
            seen["ctor"] = kwargs

        def transcribe(
            self, *, audio: bytes, filename: str = "audio.wav", language: str | None = None
        ) -> str:
            seen["transcribe"] = {"audio": audio, "filename": filename, "language": language}
            return transcript

    return _Recorder, seen


@pytest.fixture
def audio_file(tmp_path: Path) -> Path:
    path = tmp_path / "request.wav"
    path.write_bytes(b"RIFF-fake-wav-bytes")
    return path


def _audio_translate_args(manifest_path: Path, envelope_path: Path, *extra: str) -> list[str]:
    """Like `_translate_args` but with no positional REQUEST (--audio replaces it)."""
    return [
        "translate",
        "--manifest", str(manifest_path),
        "--envelope", str(envelope_path),
        "--profile", "home",
        *extra,
    ]


def test_translate_audio_end_to_end_with_stub(
    manifest_path: Path,
    envelope_path: Path,
    echo_response_file: Path,
    audio_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--audio: transcribe with the (stubbed) default whisper_cpp provider,
    then translate the transcript with the echo LLM provider."""
    recorder, seen = _make_speech_recorder("Bring me the red mug from the kitchen.")
    monkeypatch.setattr("urml_llm_bridge.speech.whisper_cpp.WhisperCppProvider", recorder)
    rc = main(_audio_translate_args(
        manifest_path, envelope_path,
        "--audio", str(audio_file),
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
    ))
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "profile: home" in captured.out
    assert 'transcribed request.wav: "Bring me the red mug from the kitchen."' in captured.err
    assert seen["ctor"] == {}  # no base_url: provider default applies
    assert seen["transcribe"] == {
        "audio": b"RIFF-fake-wav-bytes",
        "filename": "request.wav",
        "language": None,
    }


def test_translate_audio_echo_speech_provider_is_hermetic(
    manifest_path: Path,
    envelope_path: Path,
    echo_response_file: Path,
    audio_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The echo speech provider needs no speech model or server on the host."""
    rc = main(_audio_translate_args(
        manifest_path, envelope_path,
        "--audio", str(audio_file),
        "--speech-provider", "echo",
        "--echo-transcript", "Bring me the red mug from the kitchen.",
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
    ))
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "profile: home" in captured.out


def test_translate_speech_base_url_and_language_plumbed(
    manifest_path: Path,
    envelope_path: Path,
    echo_response_file: Path,
    audio_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, seen = _make_speech_recorder("Bring me the red mug from the kitchen.")
    monkeypatch.setattr("urml_llm_bridge.speech.whisper_cpp.WhisperCppProvider", recorder)
    rc = main(_audio_translate_args(
        manifest_path, envelope_path,
        "--audio", str(audio_file),
        "--speech-base-url", "http://gpu-box:9000",
        "--speech-language", "he",
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
    ))
    assert rc == 0
    assert seen["ctor"] == {"base_url": "http://gpu-box:9000"}
    assert seen["transcribe"]["language"] == "he"


def test_translate_audio_and_request_conflict(
    manifest_path: Path,
    audio_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "typed request",
        "--manifest", str(manifest_path),
        "--audio", str(audio_file),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "not both" in captured.err


def test_translate_requires_request_or_audio(
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "--manifest", str(manifest_path),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "REQUEST or --audio" in captured.err


def test_translate_audio_file_not_found(
    manifest_path: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "--manifest", str(manifest_path),
        "--audio", str(tmp_path / "missing.wav"),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "audio file not found" in captured.err


def test_translate_speech_echo_requires_transcript(
    manifest_path: Path,
    audio_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "translate",
        "--manifest", str(manifest_path),
        "--audio", str(audio_file),
        "--speech-provider", "echo",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "--echo-transcript" in captured.err


def test_translate_empty_transcript_rejected(
    manifest_path: Path,
    audio_file: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Silence in, error out: an empty transcript never reaches the LLM."""
    rc = main([
        "translate",
        "--manifest", str(manifest_path),
        "--audio", str(audio_file),
        "--speech-provider", "echo",
        "--echo-transcript", "   ",
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "empty transcript" in captured.err


def test_translate_speech_dead_server_exits_1(
    manifest_path: Path,
    audio_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class _Dead:
        def __init__(self, **kwargs: Any) -> None:
            pass

        def transcribe(
            self, *, audio: bytes, filename: str = "audio.wav", language: str | None = None
        ) -> str:
            raise ConnectionError(
                "could not reach whisper-server at http://127.0.0.1:8080: refused. "
                "Is whisper-server running?"
            )

    monkeypatch.setattr("urml_llm_bridge.speech.whisper_cpp.WhisperCppProvider", _Dead)
    rc = main([
        "translate",
        "--manifest", str(manifest_path),
        "--audio", str(audio_file),
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert "speech provider error" in captured.err
    assert "whisper-server" in captured.err


def test_translate_openai_speech_no_key_with_base_url(
    manifest_path: Path,
    envelope_path: Path,
    echo_response_file: Path,
    audio_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder, seen = _make_speech_recorder("Bring me the red mug from the kitchen.")
    monkeypatch.setattr("urml_llm_bridge.speech.openai.OpenAISpeechProvider", recorder)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    rc = main(_audio_translate_args(
        manifest_path, envelope_path,
        "--audio", str(audio_file),
        "--speech-provider", "openai",
        "--speech-base-url", "http://127.0.0.1:1234/v1",
        "--speech-model", "faster-whisper-large-v3",
        "--provider", "echo",
        "--echo-response-file", str(echo_response_file),
    ))
    assert rc == 0
    assert seen["ctor"] == {
        "model": "faster-whisper-large-v3",
        "base_url": "http://127.0.0.1:1234/v1",
        "api_key": "urml-local-no-key",
    }


# ---------------------------------------------------------------------------
# Help / argparse
# ---------------------------------------------------------------------------


def test_translate_help_in_parser_output(capsys: pytest.CaptureFixture[str]) -> None:
    """`urml --help` should list the translate subcommand."""
    with pytest.raises(SystemExit):
        main(["--help"])
    out = capsys.readouterr().out
    assert "translate" in out
