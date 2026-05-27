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


# ---------------------------------------------------------------------------
# Policy flag tests (RFC-0004)
# ---------------------------------------------------------------------------


def _write_manifest_with_provenance(
    tmp_path: Path,
    *,
    country: str = "US",
    vendor: str = "example_vendor",
) -> Path:
    """Write a minimal manifest with a single critical-provenance component."""
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        f"""manifest_version: "0.1"
robot_id: test_bot
provenance:
  manifest_attestation: self_declared
  components:
    - id: drive_controller
      role: critical
      vendor: {vendor}
      country_of_origin: {country}
      country_of_final_assembly: {country}
      hbom_ref:
        format: cyclonedx-1.7
        uri: ./hbom/x.json
        sha256: abc
""",
        encoding="utf-8",
    )
    return manifest


def _write_trivial_program(tmp_path: Path) -> Path:
    """Write a program that exercises Pass 5 without Pass 1-4 issues."""
    program = tmp_path / "program.yaml"
    program.write_text(
        """profile: home
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - wait: { duration: 1s }
""",
        encoding="utf-8",
    )
    return program


def test_default_policy_rejects_cn_critical_component(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without --policy, the bundled US-federal default loads and fires on CN provenance."""
    manifest = _write_manifest_with_provenance(tmp_path, country="CN")
    program = _write_trivial_program(tmp_path)
    rc = main(["validate", str(program), "--manifest", str(manifest)])
    captured = capsys.readouterr()
    assert rc == 1
    assert "policy.country_denied" in captured.err


def test_no_policy_flag_skips_pass_5(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--no-policy` bypasses Pass 5 entirely; a CN component validates."""
    manifest = _write_manifest_with_provenance(tmp_path, country="CN")
    program = _write_trivial_program(tmp_path)
    rc = main(["validate", str(program), "--manifest", str(manifest), "--no-policy"])
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "Validation passed" in captured.out


def test_explicit_policy_path_loads_and_evaluates(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--policy PATH` overrides the default with a custom rule set."""
    manifest = _write_manifest_with_provenance(tmp_path, country="US")
    program = _write_trivial_program(tmp_path)
    # Permissive policy: empty rules list, accepts everything.
    policy = tmp_path / "permissive.yaml"
    policy.write_text(
        """policy_version: "0.1"
policy_id: permissive
rules: []
""",
        encoding="utf-8",
    )
    rc = main([
        "validate",
        str(program),
        "--manifest",
        str(manifest),
        "--policy",
        str(policy),
    ])
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "Validation passed" in captured.out


def test_policy_and_no_policy_are_mutually_exclusive(
    tmp_path: Path,
) -> None:
    """argparse rejects --policy together with --no-policy."""
    manifest = _write_manifest_with_provenance(tmp_path)
    program = _write_trivial_program(tmp_path)
    policy = tmp_path / "p.yaml"
    policy.write_text("policy_version: \"0.1\"\npolicy_id: x\nrules: []\n", encoding="utf-8")
    with pytest.raises(SystemExit) as excinfo:
        main([
            "validate",
            str(program),
            "--manifest",
            str(manifest),
            "--policy",
            str(policy),
            "--no-policy",
        ])
    assert excinfo.value.code == 2


def test_missing_policy_file_exits_2(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    manifest = _write_manifest_with_provenance(tmp_path)
    program = _write_trivial_program(tmp_path)
    rc = main([
        "validate",
        str(program),
        "--manifest",
        str(manifest),
        "--policy",
        str(tmp_path / "nope.yaml"),
    ])
    captured = capsys.readouterr()
    assert rc == 2
    assert "policy file not found" in captured.err.lower()


def test_policy_error_detail_appears_in_pretty_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The `detail` dict on policy errors is rendered in the pretty output."""
    manifest = _write_manifest_with_provenance(tmp_path, country="CN")
    program = _write_trivial_program(tmp_path)
    rc = main(["validate", str(program), "--manifest", str(manifest)])
    captured = capsys.readouterr()
    assert rc == 1
    # detail fields rendered as `key: value` lines under the error.
    assert "rule_id:" in captured.err
    assert "component_id:" in captured.err
    assert "offending_value:" in captured.err


def test_policy_error_appears_in_json_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """JSON output carries the structured detail dict on policy errors."""
    manifest = _write_manifest_with_provenance(tmp_path, country="CN")
    program = _write_trivial_program(tmp_path)
    rc = main([
        "validate",
        str(program),
        "--manifest",
        str(manifest),
        "--json",
    ])
    captured = capsys.readouterr()
    assert rc == 1
    payload = json.loads(captured.out)
    codes = [e["code"] for e in payload["errors"]]
    assert "policy.country_denied" in codes
    policy_err = next(e for e in payload["errors"] if e["code"] == "policy.country_denied")
    assert policy_err["detail"] is not None
    assert policy_err["detail"]["component_id"] == "drive_controller"


def test_urml_schema_policy_emits_policy_schema(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`urml schema --name policy` returns the Policy JSON Schema."""
    rc = main(["schema", "--name", "policy"])
    captured = capsys.readouterr()
    assert rc == 0
    payload = json.loads(captured.out)
    # The Policy model declares these top-level fields.
    assert "policy_id" in payload["properties"]
    assert "rules" in payload["properties"]
