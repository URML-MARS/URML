"""CLI tests for the `urml conformance` subcommand.

These tests require `urml-conformance` to be installed (e.g. via
`pip install -e ../../conformance` from this directory). When the package
isn't present they are skipped, since the conformance suite is an optional
dep of the validator.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("urml_conformance")

from urml_validator.cli import main


def test_conformance_run_passes_with_bundled_fixtures(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The bundled fixture set passes against the default hermetic adapter."""
    output = tmp_path / "report.json"
    rc = main(["conformance", "run", "--output", str(output)])
    captured = capsys.readouterr()
    assert rc == 0, f"stderr={captured.err}"
    assert output.is_file()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert "results" in payload
    assert payload["results"], "expected at least one case in the report"
    assert all(case["passed"] for case in payload["results"]), (
        f"expected all cases to pass; failures: "
        f"{[c['name'] for c in payload['results'] if not c['passed']]}"
    )


def test_conformance_run_without_output_still_succeeds(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No --output: the summary still prints, exit code reflects all_passed."""
    rc = main(["conformance", "run"])
    captured = capsys.readouterr()
    assert rc == 0, f"stderr={captured.err}"
    assert "Conformance:" in captured.err


def test_conformance_run_creates_parent_directories(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A nested --output path is created if its parent directories don't exist."""
    output = tmp_path / "deep" / "nested" / "report.json"
    rc = main(["conformance", "run", "--output", str(output)])
    captured = capsys.readouterr()
    assert rc == 0, f"stderr={captured.err}"
    assert output.is_file()
