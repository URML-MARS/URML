"""CLI behavior tests.

Exercise `urml_validator.cli:main` end-to-end against the canonical fixtures.
The tests run the CLI in-process (no subprocess) so coverage stays clean and
errors surface as Python tracebacks during dev.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from urml_validator.cli import build_parser, main

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = Path(__file__).parent / "fixtures"
EXAMPLES_ROOT = REPO_ROOT / "examples"

RED_MUG = EXAMPLES_ROOT / "home" / "red-mug.urml.yaml"
MANIFEST = FIXTURE_ROOT / "manifests" / "turtlebot4_home.yaml"
ENVELOPE = FIXTURE_ROOT / "envelopes" / "home_default.yaml"


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


def test_validate_red_mug_passes(capsys: pytest.CaptureFixture[str]) -> None:
    """Canonical red-mug example exits 0 with a pass message."""
    rc = main([
        "validate",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--envelope",
        str(ENVELOPE),
        "--profile",
        "home",
    ])
    captured = capsys.readouterr()
    assert rc == 0, f"stderr={captured.err}"
    assert "Validation passed" in captured.out


def test_validate_no_envelope_passes(capsys: pytest.CaptureFixture[str]) -> None:
    """`--envelope` is optional."""
    rc = main([
        "validate",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
    ])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Validation passed" in captured.out


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


def test_missing_program_file_exits_2(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "validate",
        str(tmp_path / "nope.yaml"),
        "--manifest",
        str(MANIFEST),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "program file not found" in captured.err.lower()


def test_missing_manifest_file_exits_2(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "validate",
        str(RED_MUG),
        "--manifest",
        str(tmp_path / "missing.yaml"),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "manifest file not found" in captured.err.lower()


def test_invalid_yaml_exits_2(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("this: is: not: valid: yaml: :\n", encoding="utf-8")
    rc = main([
        "validate",
        str(bad),
        "--manifest",
        str(MANIFEST),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "yaml parse error" in captured.err.lower()


def test_top_level_must_be_mapping(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bad = tmp_path / "list.yaml"
    bad.write_text("- one\n- two\n", encoding="utf-8")
    rc = main([
        "validate",
        str(bad),
        "--manifest",
        str(MANIFEST),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "yaml mapping" in captured.err.lower()


def test_validate_failure_exits_1(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A program with a known capability error exits 1 with structured output."""
    bad_program = tmp_path / "bad.yaml"
    bad_program.write_text(
        "profile: home\nbehavior:\n  type: sequence\n  steps:\n    - move_to: {location: the_moon}\n",
        encoding="utf-8",
    )
    rc = main([
        "validate",
        str(bad_program),
        "--manifest",
        str(MANIFEST),
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert "Validation failed" in captured.err
    assert "capability.missing_location" in captured.err
    assert "the_moon" in captured.err


# ---------------------------------------------------------------------------
# --json output
# ---------------------------------------------------------------------------


def test_json_output_passes(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main([
        "validate",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--envelope",
        str(ENVELOPE),
        "--json",
    ])
    captured = capsys.readouterr()
    assert rc == 0
    payload = json.loads(captured.out)
    assert payload["accepted"] is True
    assert payload["errors"] == []


def test_json_output_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bad_program = tmp_path / "bad.yaml"
    bad_program.write_text(
        "profile: home\nbehavior:\n  type: sequence\n  steps:\n    - move_to: {location: the_moon}\n",
        encoding="utf-8",
    )
    rc = main([
        "validate",
        str(bad_program),
        "--manifest",
        str(MANIFEST),
        "--json",
    ])
    captured = capsys.readouterr()
    assert rc == 1
    payload = json.loads(captured.out)
    assert payload["accepted"] is False
    codes = [e["code"] for e in payload["errors"]]
    assert "capability.missing_location" in codes


# ---------------------------------------------------------------------------
# Argparse behaviour
# ---------------------------------------------------------------------------


def test_help_includes_validate_subcommand() -> None:
    parser = build_parser()
    help_text = parser.format_help()
    assert "validate" in help_text
    assert "urml" in help_text


def test_version_short_circuits(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`urml --version` exits 0 via SystemExit (argparse's built-in behaviour)."""
    monkeypatch.setattr(sys, "argv", ["urml", "--version"])
    with pytest.raises(SystemExit) as excinfo:
        main(["--version"])
    assert excinfo.value.code == 0
    captured = capsys.readouterr()
    assert "urml-validator" in captured.out


def test_missing_subcommand_is_usage_error() -> None:
    """`urml` with no subcommand exits 2 (argparse's built-in)."""
    with pytest.raises(SystemExit) as excinfo:
        main([])
    assert excinfo.value.code == 2


def test_unknown_subcommand_is_usage_error() -> None:
    with pytest.raises(SystemExit) as excinfo:
        main(["nonsense"])
    assert excinfo.value.code == 2
