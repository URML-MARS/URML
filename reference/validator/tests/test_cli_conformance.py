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
    # urml.conformance-report/1: the summary is written out with the results.
    assert payload["format"] == "urml.conformance-report/1"
    assert payload["all_passed"] is True
    assert payload["passed"] == len(payload["results"]) == payload["fixture_count"]
    assert payload["failed"] == 0
    assert payload["adapter"] == "urml_ros2_runtime:MockROSAdapter"
    assert payload["filter"] is None
    assert len(payload["fixtures_sha256"]) == 64


def test_conformance_run_records_the_adapter_and_filter(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--adapter and --filter reach the report, so it says what ran."""
    output = tmp_path / "report.json"
    spec = "urml_ros2_runtime:MockROSAdapter"
    rc = main(["conformance", "run", "--adapter", spec, "--filter", "quadruped", "--output", str(output)])
    captured = capsys.readouterr()
    assert rc == 0, f"stderr={captured.err}"
    raw = output.read_bytes()
    assert b"\r\n" not in raw, "the report is written with LF line endings"
    payload = json.loads(raw)
    assert payload["adapter"] == spec
    assert payload["filter"] == "quadruped"
    assert payload["results"] and all(c["name"].startswith("quadruped/") for c in payload["results"])


def test_conformance_run_selects_a_whole_profile(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """--profile runs every fixture that lists the profile, and the report says so."""
    output = tmp_path / "report.json"
    rc = main(["conformance", "run", "--profile", "drone", "--output", str(output)])
    captured = capsys.readouterr()
    assert rc == 0, f"stderr={captured.err}"
    payload = json.loads(output.read_bytes())
    assert payload["profiles"] == ["drone"]
    folders = {c["name"].split("/", 1)[0] for c in payload["results"]}
    assert {"drone", "fleet", "rulebook"} <= folders


def test_conformance_run_unknown_profile_is_a_usage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["conformance", "run", "--profile", "no-such-profile"])
    assert rc == 2
    assert "no fixtures list --profile" in capsys.readouterr().err


def test_conformance_run_bad_adapter_is_a_usage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["conformance", "run", "--adapter", "notacolonspec"])
    assert rc == 2
    assert "module:attribute" in capsys.readouterr().err


def test_conformance_run_filter_without_match_is_a_usage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main(["conformance", "run", "--filter", "no-such-fixture-zzz"])
    assert rc == 2
    assert "no fixtures match" in capsys.readouterr().err


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
