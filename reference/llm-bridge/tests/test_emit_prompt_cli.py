"""`urml emit-prompt` CLI subcommand tests.

Subcommand lives in `urml_validator.cli`; tested here because exercising
it requires `urml-llm-bridge` to be installed in the active venv.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from urml_validator.cli import main

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATOR_FIXTURES = REPO_ROOT / "reference" / "validator" / "tests" / "fixtures"


@pytest.fixture
def manifest_path() -> Path:
    return VALIDATOR_FIXTURES / "manifests" / "turtlebot4_home.yaml"


@pytest.fixture
def envelope_path() -> Path:
    return VALIDATOR_FIXTURES / "envelopes" / "home_default.yaml"


@pytest.fixture
def industrial_manifest_path() -> Path:
    return VALIDATOR_FIXTURES / "manifests" / "industrial_cell.yaml"


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------


def test_emit_prompt_manifest_only(
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["emit-prompt", "--manifest", str(manifest_path)])
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    # The prompt always contains: instruction header, manifest summary, schema.
    assert "URML program JSON Schema" in captured.out
    assert "turtlebot4_demo" in captured.out
    assert "Robot ID" in captured.out


def test_emit_prompt_with_envelope_and_profile(
    manifest_path: Path,
    envelope_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "emit-prompt",
        "--manifest", str(manifest_path),
        "--envelope", str(envelope_path),
        "--profile", "home",
    ])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Active safety envelope" in captured.out
    assert "Active profile(s): home" in captured.out
    # The default home few-shot (red mug) appears.
    assert "Bring me the red mug from the kitchen." in captured.out


def test_emit_prompt_industrial_profile_picks_industrial_few_shots(
    industrial_manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "emit-prompt",
        "--manifest", str(industrial_manifest_path),
        "--profile", "industrial",
    ])
    captured = capsys.readouterr()
    assert rc == 0
    # The industrial few-shot appears.
    assert "Pick a red widget from the bin" in captured.out
    # The home red-mug example does NOT appear in an industrial-profile prompt.
    assert "Bring me the red mug from the kitchen." not in captured.out


def test_emit_prompt_no_few_shots_flag(
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "emit-prompt",
        "--manifest", str(manifest_path),
        "--profile", "home",
        "--no-few-shots",
    ])
    captured = capsys.readouterr()
    assert rc == 0
    # Few-shot block header should be absent.
    assert "=== Examples ===" not in captured.out
    assert "Bring me the red mug" not in captured.out


def test_emit_prompt_out_file(
    tmp_path: Path,
    manifest_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    out_path = tmp_path / "subdir" / "prompt.txt"
    rc = main([
        "emit-prompt",
        "--manifest", str(manifest_path),
        "--out", str(out_path),
    ])
    captured = capsys.readouterr()
    assert rc == 0
    assert out_path.is_file()
    assert "wrote" in captured.err
    text = out_path.read_text(encoding="utf-8")
    assert "URML program JSON Schema" in text
    assert "turtlebot4_demo" in text
    # Stdout should be empty when --out is used.
    assert captured.out == ""


# ---------------------------------------------------------------------------
# Failure modes
# ---------------------------------------------------------------------------


def test_emit_prompt_missing_manifest(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "emit-prompt",
        "--manifest", str(tmp_path / "missing.yaml"),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "manifest file not found" in captured.err.lower()


def test_emit_prompt_missing_envelope(
    manifest_path: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "emit-prompt",
        "--manifest", str(manifest_path),
        "--envelope", str(tmp_path / "missing.yaml"),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "envelope file not found" in captured.err.lower()


def test_emit_prompt_invalid_yaml(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("this: is: not: valid:\n  : :\n", encoding="utf-8")
    rc = main([
        "emit-prompt",
        "--manifest", str(bad),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "yaml parse error" in captured.err.lower()


# ---------------------------------------------------------------------------
# Help integration
# ---------------------------------------------------------------------------


def test_emit_prompt_listed_in_help(capsys: pytest.CaptureFixture[str]) -> None:
    """`urml --help` should list emit-prompt."""
    with pytest.raises(SystemExit):
        main(["--help"])
    out = capsys.readouterr().out
    assert "emit-prompt" in out
