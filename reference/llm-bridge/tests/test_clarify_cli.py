"""`urml translate --clarify` end-to-end CLI tests (RFC-0700), hermetic."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
import yaml
from urml_validator.cli import main

from .test_clarify import CLARIFY_EMISSION, RED_MUG_PROGRAM

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST = (
    REPO_ROOT / "reference" / "validator" / "tests" / "fixtures" / "manifests" / "turtlebot4_home.yaml"
)


@pytest.fixture
def scripted_file(tmp_path: Path) -> Path:
    p = tmp_path / "responses.json"
    p.write_text(json.dumps([CLARIFY_EMISSION, RED_MUG_PROGRAM]), encoding="utf-8")
    return p


def _argv(scripted_file: Path, *extra: str) -> list[str]:
    return [
        "translate",
        "Bring me the mug.",
        "--manifest",
        str(MANIFEST),
        "--profile",
        "home",
        "--no-policy",
        "--provider",
        "echo",
        "--echo-response-file",
        str(scripted_file),
        *extra,
    ]


def test_clarify_cli_answers_and_translates(
    scripted_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO("the red one\n"))
    rc = main(_argv(scripted_file, "--clarify"))
    assert rc == 0
    captured = capsys.readouterr()
    assert "the model asks: Which mug do you mean?" in captured.err
    assert "options: the red one, the blue one" in captured.err
    assert 'continuing with answer: "the red one"' in captured.err
    program = yaml.safe_load(captured.out.split("answer> ", 1)[-1])
    assert program["profile"] == "home"


def test_clarify_cli_eof_exits_1(
    scripted_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr("sys.stdin", io.StringIO(""))
    rc = main(_argv(scripted_file, "--clarify"))
    assert rc == 1
    err = capsys.readouterr().err
    assert "the model asks: Which mug do you mean?" in err
    assert "stdin is closed" in err


def test_without_clarify_flag_a_question_is_just_invalid(
    scripted_file: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Default off: the clarify emission fails validation; no stdin is read."""
    rc = main(_argv(scripted_file, "--max-revisions", "0"))
    assert rc == 1
    err = capsys.readouterr().err
    assert "translation failed" in err
    assert "the model asks" not in err
