"""`urml init` CLI subcommand tests.

The init subcommand lives in the validator package and has no runtime
dependency on the bridge — tests live alongside the other validator CLI
tests.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from urml_validator.cli import main

# ---------------------------------------------------------------------------
# Happy paths: home profile
# ---------------------------------------------------------------------------


def test_init_home_writes_full_starter(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project = tmp_path / "demo-home"
    rc = main(["init", str(project), "--profile", "home"])
    captured = capsys.readouterr()
    assert rc == 0, captured.err

    # Expected file set for home.
    for name in (
        "manifest.yaml",
        "envelope.yaml",
        "program.urml.yaml",
        "prompt.en.txt",
        "README.md",
        "Makefile",
    ):
        assert (project / name).is_file(), f"missing: {name}"

    # The manifest is valid YAML and identifies as a manifest.
    manifest = yaml.safe_load((project / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == "0.1"
    assert "kitchen" in [loc["name"] for loc in manifest["declared_locations"]]

    # The prompt is the canonical English red-mug request.
    assert "red mug" in (project / "prompt.en.txt").read_text(encoding="utf-8").lower()

    # The status banner went to stderr.
    assert "Initialized home project" in captured.err
    assert "Next steps" in captured.err


def test_init_home_emits_validation_friendly_program(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The starter program must validate against its sibling manifest+envelope."""
    project = tmp_path / "demo-home"
    main(["init", str(project), "--profile", "home"])
    capsys.readouterr()  # discard init's output

    # Run `urml validate` on the freshly scaffolded project. This is the
    # whole point of `init` -- the user can validate immediately.
    rc = main([
        "validate",
        str(project / "program.urml.yaml"),
        "--manifest", str(project / "manifest.yaml"),
        "--envelope", str(project / "envelope.yaml"),
        "--profile", "home",
    ])
    captured = capsys.readouterr()
    assert rc == 0, f"starter program did not validate. stderr={captured.err}"
    assert "Validation passed" in captured.out


# ---------------------------------------------------------------------------
# Happy paths: industrial profile
# ---------------------------------------------------------------------------


def test_init_industrial_writes_full_starter(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project = tmp_path / "demo-industrial"
    rc = main(["init", str(project), "--profile", "industrial"])
    captured = capsys.readouterr()
    assert rc == 0, captured.err

    # Industrial set: no envelope.
    for name in (
        "manifest.yaml",
        "program.urml.yaml",
        "prompt.en.txt",
        "README.md",
        "Makefile",
    ):
        assert (project / name).is_file(), f"missing: {name}"
    assert not (project / "envelope.yaml").exists()

    # Manifest identifies as an industrial cell.
    manifest = yaml.safe_load((project / "manifest.yaml").read_text(encoding="utf-8"))
    assert manifest["robot_id"] == "cell_a1"
    assert "widget_red" in manifest["perception"]["object_vocabulary"]


def test_init_industrial_program_validates(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project = tmp_path / "demo-industrial"
    main(["init", str(project), "--profile", "industrial"])
    capsys.readouterr()

    rc = main([
        "validate",
        str(project / "program.urml.yaml"),
        "--manifest", str(project / "manifest.yaml"),
        "--profile", "industrial",
    ])
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "Validation passed" in captured.out


# ---------------------------------------------------------------------------
# Defaults + edge cases
# ---------------------------------------------------------------------------


def test_init_defaults_to_home(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """No --profile -> home."""
    project = tmp_path / "default"
    rc = main(["init", str(project)])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Initialized home project" in captured.err
    assert (project / "envelope.yaml").is_file()


def test_init_creates_parent_dirs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project = tmp_path / "nested" / "deeper" / "demo"
    rc = main(["init", str(project)])
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert (project / "manifest.yaml").is_file()


# ---------------------------------------------------------------------------
# Refusal modes
# ---------------------------------------------------------------------------


def test_init_refuses_non_empty_directory_without_force(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project = tmp_path / "non-empty"
    project.mkdir()
    (project / "existing.txt").write_text("hello", encoding="utf-8")

    rc = main(["init", str(project)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "is not empty" in captured.err
    # Pre-existing file untouched.
    assert (project / "existing.txt").read_text(encoding="utf-8") == "hello"


def test_init_force_overwrites_existing_files(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    project = tmp_path / "existing"
    project.mkdir()
    (project / "README.md").write_text("old content", encoding="utf-8")

    rc = main(["init", str(project), "--force"])
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "old content" not in (project / "README.md").read_text(encoding="utf-8")


def test_init_refuses_when_target_is_a_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = tmp_path / "not-a-dir"
    target.write_text("this is a file", encoding="utf-8")

    rc = main(["init", str(target)])
    captured = capsys.readouterr()
    assert rc == 2
    assert "not a directory" in captured.err


# ---------------------------------------------------------------------------
# CLI surface
# ---------------------------------------------------------------------------


def test_init_listed_in_help(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--help"])
    out = capsys.readouterr().out
    assert "init" in out


def test_init_rejects_unknown_profile(capsys: pytest.CaptureFixture[str]) -> None:
    """Argparse's choice= validation enforces the profile set."""
    with pytest.raises(SystemExit) as excinfo:
        main(["init", "x", "--profile", "fictional"])
    assert excinfo.value.code == 2
    err = capsys.readouterr().err
    assert "invalid choice" in err.lower() or "fictional" in err
