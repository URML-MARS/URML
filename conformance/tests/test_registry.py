"""The registry of validated robots: the committed entries check clean, the
generated files are fresh, and every rule of the checker bites.

The committed-file guards mirror the README hero guard: registry/registry.json
and registry/entry.schema.json must equal fresh output, so a stale file fails
CI. The negative cases run against a small registry built in a temporary
directory, so each rule is shown to refuse on its own.
"""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import pytest
import yaml
from urml_validator import __version__ as validator_version
from urml_validator import validate
from urml_validator.evidence import append_record, build_record, canonical_json, read_records

from urml_conformance import __version__ as conformance_version
from urml_conformance import run_suite
from urml_conformance.registry import (
    EXPORT_PATH,
    SCHEMA_PATH,
    RegistryCheckError,
    check_registry,
    main,
    profile_fixtures,
    render_export,
    render_schema,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
GOPIGO_MANIFEST = REPO_ROOT / "examples" / "gopigo3" / "gopigo3.manifest.yaml"
AS_OF = date(2026, 9, 27)

MANIFEST_REL = "examples/bot/bot.manifest.yaml"
RECORDS_REL = "registry/evidence/bot/validation-records.jsonl"
REPORT_REL = "registry/evidence/bot/conformance-report.json"
# Every fixture that lists the educational profile: a claim covers all of them.
EDUCATIONAL = sorted(profile_fixtures(REPO_ROOT)["educational"])


def _program(*steps: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile": ["educational"],
        "behavior": {"type": "sequence", "on_error": "abort_and_report", "steps": list(steps)},
    }


DRIVE_1M = _program({"drive": {"distance": 1.0}})
DRIVE_3M = _program({"drive": {"distance": 3.0}})


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# The committed registry
# ---------------------------------------------------------------------------


def test_committed_entries_pass_the_check() -> None:
    result = check_registry(REPO_ROOT)
    assert result.ok, "\n".join(result.problems)
    ids = {checked.entry.id for checked in result.entries if checked.entry is not None}
    assert ids == {"ardupilot-arducopter-pixhawk", "gopigo3-example-adapter", "px4-sitl-sih-quadrotor"}
    for checked in result.entries:
        assert checked.records is not None and checked.records.replayed


def test_registry_json_is_fresh() -> None:
    committed = (REPO_ROOT / EXPORT_PATH).read_text(encoding="utf-8")
    assert committed == render_export(REPO_ROOT), (
        "registry/registry.json is stale; run `python -m urml_conformance.registry export` and commit."
    )


def test_entry_schema_is_fresh() -> None:
    committed = (REPO_ROOT / SCHEMA_PATH).read_text(encoding="utf-8")
    assert committed == render_schema(), (
        "registry/entry.schema.json is stale; run `python -m urml_conformance.registry schema` and commit."
    )


def test_export_is_deterministic() -> None:
    first = render_export(REPO_ROOT)
    assert first == render_export(REPO_ROOT)
    document = json.loads(first)
    assert document["format"] == "urml.registry/1"
    ids = [entry["id"] for entry in document["entries"]]
    assert ids == sorted(ids)
    for entry in document["entries"]:
        records = entry["validation_records"]
        assert records["reverified_with"] == f"urml-validator {validator_version}"
        assert records["count"] == records["accepted"] + records["refused"]
        assert entry["entry_url"].endswith(f"registry/entries/{entry['id']}.yaml")


# ---------------------------------------------------------------------------
# A small registry to break, one rule at a time
# ---------------------------------------------------------------------------


@dataclass
class Mini:
    root: Path
    entry: dict[str, Any]

    @property
    def entry_path(self) -> Path:
        return self.root / "registry" / "entries" / f"{self.entry['id']}.yaml"

    def write(self) -> None:
        self.entry_path.parent.mkdir(parents=True, exist_ok=True)
        text = yaml.safe_dump(self.entry, sort_keys=False, allow_unicode=True)
        self.entry_path.write_text(text, encoding="utf-8", newline="\n")

    def problems(self) -> list[str]:
        self.write()
        return check_registry(self.root).problems

    def repin_records(self) -> None:
        self.entry["validation_records"]["sha256"] = _sha256(self.root / RECORDS_REL)

    def add_report(self, report: dict[str, Any], profiles: list[str] | None = None) -> None:
        path = self.root / REPORT_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
        self.entry["compatibility"] = {
            "tier": "self_reported",
            "profiles": profiles or ["educational"],
            "report": {"path": REPORT_REL, "sha256": _sha256(path)},
        }


def _record(program: dict[str, Any], manifest: dict[str, Any], base_dir: Path) -> Any:
    result = validate(
        program, manifest, None, profiles=("educational",), policy=None, manifest_base_dir=base_dir, as_of=AS_OF
    )
    return build_record(
        surface="api",
        stage="validation",
        result=result,
        program=program,
        manifest=manifest,
        policy=None,
        as_of=AS_OF,
        profiles=("educational",),
        recorded_at="2026-09-27T00:00:00Z",
    )


@pytest.fixture
def mini(tmp_path: Path) -> Mini:
    root = tmp_path / "repo"
    manifest_path = root / MANIFEST_REL
    manifest_path.parent.mkdir(parents=True)
    shutil.copyfile(GOPIGO_MANIFEST, manifest_path)
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    for program in (DRIVE_1M, DRIVE_3M):
        append_record(root / RECORDS_REL, _record(program, manifest, manifest_path.parent))
    (root / "docs").mkdir()
    (root / "docs" / "run.md").write_text("A run.\n", encoding="utf-8", newline="\n")
    entry: dict[str, Any] = {
        "registry_version": "1",
        "id": "bot",
        "title": "A test robot",
        "status": "listed",
        "listed": "2026-09-01",
        "last_verified": "2026-09-27",
        "submitted_by": "Test project",
        "robot": {"name": "Bot", "class": "two-wheel test robot", "manifest": MANIFEST_REL},
        "runtime": {
            "package": "bot-runtime",
            "version": "1.0.0",
            "adapter": "bot_runtime:BotAdapter",
            "substrate": "a test substrate",
        },
        "profiles": ["educational"],
        "field_evidence": [
            {
                "kind": "hardware_run",
                "date": "2026-09-01",
                "by": "Test project",
                "summary": "Drove one metre.",
                "sources": ["docs/run.md", "https://example.org/run"],
            }
        ],
        "validation_records": {
            "path": RECORDS_REL,
            "sha256": _sha256(root / RECORDS_REL),
            "summary": "One accepted drive and one refused drive.",
            "inputs": {"manifest": MANIFEST_REL, "policy": "none"},
        },
        "limits": ["A test entry, run by nobody."],
    }
    return Mini(root=root, entry=entry)


def _one(problems: list[str], fragment: str) -> None:
    assert any(fragment in problem for problem in problems), "\n".join(problems) or "(no problems)"


def test_the_mini_registry_is_clean(mini: Mini) -> None:
    assert mini.problems() == []
    document = json.loads(render_export(mini.root))
    (entry,) = document["entries"]
    assert entry["validation_records"]["accepted"] == 1
    assert entry["validation_records"]["refused"] == 1
    assert entry["validation_records"]["codes"] == {"capability.relative_distance_exceeded": 1}
    assert entry["field_evidence"][0]["sources"] == [
        "https://github.com/URML-MARS/URML/blob/main/docs/run.md",
        "https://example.org/run",
    ]
    assert entry["robot"]["manifest_url"].endswith(f"/blob/main/{MANIFEST_REL}")


def test_a_wrong_sha256_is_refused(mini: Mini) -> None:
    mini.entry["validation_records"]["sha256"] = "0" * 64
    _one(mini.problems(), "sha256 is")


def test_an_unknown_field_is_refused(mini: Mini) -> None:
    mini.entry["robot"]["colour"] = "red"
    _one(mini.problems(), "robot.colour: Extra inputs are not permitted")


def test_a_score_field_is_refused(mini: Mini) -> None:
    mini.entry["rating"] = 5
    _one(mini.problems(), "rating: Extra inputs are not permitted")


def test_a_missing_manifest_is_refused(mini: Mini) -> None:
    (mini.root / MANIFEST_REL).unlink()
    _one(mini.problems(), f"robot.manifest {MANIFEST_REL!r} does not exist")


def test_a_manifest_that_does_not_parse_is_refused(mini: Mini) -> None:
    (mini.root / MANIFEST_REL).write_text("manifest_version: '0.1'\nrobot_id: bot\nwheels: 2\n", encoding="utf-8")
    _one(mini.problems(), "does not parse as a URML capability manifest")


def test_a_manifest_that_is_not_yaml_is_a_problem_not_a_crash(mini: Mini) -> None:
    (mini.root / MANIFEST_REL).write_text("robot_id: [unclosed\n", encoding="utf-8")
    _one(mini.problems(), "is not readable YAML")


def test_an_input_that_is_a_folder_is_refused(mini: Mini) -> None:
    mini.entry["validation_records"]["inputs"]["envelope"] = "docs"
    _one(mini.problems(), "validation_records.inputs.envelope 'docs' is not a file")


def test_a_record_that_no_longer_reproduces_is_refused(mini: Mini) -> None:
    records = read_records(mini.root / RECORDS_REL)
    tampered = records[1].model_copy(update={"codes": ["capability.missing_location"]})
    lines = [canonical_json(r.model_dump(mode="json")) for r in (records[0], tampered)]
    (mini.root / RECORDS_REL).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    mini.repin_records()
    _one(mini.problems(), "record 2 does not reproduce: codes: recorded")


def test_a_changed_manifest_breaks_the_replay(mini: Mini) -> None:
    path = mini.root / MANIFEST_REL
    path.write_text(
        path.read_text(encoding="utf-8").replace("max_relative_distance: 2.0", "max_relative_distance: 5.0"),
        encoding="utf-8",
        newline="\n",
    )
    _one(mini.problems(), "the manifest supplied does not match the recorded manifest digest")


def test_records_judged_with_other_rulebook_settings_are_refused(mini: Mini) -> None:
    mini.entry["validation_records"]["inputs"]["default_rulebooks"] = False
    _one(mini.problems(), "default_rulebooks is True, the inputs say False")


@pytest.mark.parametrize(
    ("where", "text", "word"),
    [
        ("title", "A URML-Certified robot", "Certified"),
        ("limits", "Approved for classrooms.", "Approved"),
        ("summary", "Endorsed by the maker.", "Endorsed"),
        ("limits", "Audited by nobody.", "Audited"),
        ("title", "Guaranteed safe", "Guaranteed"),
    ],
)
def test_banned_words_are_refused(mini: Mini, where: str, text: str, word: str) -> None:
    if where == "title":
        mini.entry["title"] = text
    elif where == "limits":
        mini.entry["limits"] = [text]
    else:
        mini.entry["field_evidence"][0]["summary"] = text
    _one(mini.problems(), f"{word!r} is not used in a listing")


def test_an_email_address_is_refused(mini: Mini) -> None:
    mini.entry["submitted_by"] = "someone@example.org"
    _one(mini.problems(), "no email addresses")


def test_an_http_source_is_refused(mini: Mini) -> None:
    mini.entry["field_evidence"][0]["sources"] = ["http://example.org/run"]
    _one(mini.problems(), "a source is a repository path or an https:// URL")


def test_an_unquoted_date_is_refused(mini: Mini) -> None:
    mini.entry["listed"] = date(2026, 9, 1)
    _one(mini.problems(), "write the date as a quoted string")


def test_the_id_must_be_the_file_name(mini: Mini) -> None:
    mini.write()
    mini.entry_path.rename(mini.entry_path.with_name("other.yaml"))
    problems = check_registry(mini.root).problems
    _one(problems, "does not match the file name 'other.yaml'")


def test_an_entry_states_its_limits(mini: Mini) -> None:
    mini.entry["limits"] = []
    _one(mini.problems(), "limits: List should have at least 1 item")


def test_a_listed_entry_carries_evidence(mini: Mini) -> None:
    mini.entry["field_evidence"] = []
    del mini.entry["validation_records"]
    _one(mini.problems(), "a listed entry carries evidence")


def test_a_non_yaml_file_in_entries_is_refused(mini: Mini) -> None:
    mini.write()
    (mini.entry_path.parent / "notes.txt").write_text("hello\n", encoding="utf-8")
    _one(check_registry(mini.root).problems, "an entry is a .yaml file")


def test_a_path_outside_the_repository_is_refused(mini: Mini) -> None:
    mini.entry["field_evidence"][0]["sources"] = ["../outside.md"]
    _one(mini.problems(), "is not a repository path")


# ---------------------------------------------------------------------------
# Compatibility: the self-reported tier
# ---------------------------------------------------------------------------


def _report(**overrides: Any) -> dict[str, Any]:
    report: dict[str, Any] = {
        "format": "urml.conformance-report/1",
        "adapter": "bot_runtime:BotAdapter",
        "urml_conformance_version": conformance_version,
        "urml_validator_version": validator_version,
        "fixture_count": len(EDUCATIONAL),
        "fixtures_sha256": "a" * 64,
        "profiles": ["educational"],
        "results": [{"name": name, "passed": True, "diagnostics": []} for name in EDUCATIONAL],
    }
    report.update(overrides)
    return report


def test_a_self_report_from_the_runtimes_own_adapter_is_accepted(mini: Mini) -> None:
    mini.add_report(_report())
    assert mini.problems() == []
    (entry,) = json.loads(render_export(mini.root))["entries"]
    assert entry["compatibility"] == {
        "tier": "self_reported",
        "profiles": ["educational"],
        "fixtures_run": len(EDUCATIONAL),
        "filter": None,
        "report_url": f"https://github.com/URML-MARS/URML/blob/main/{REPORT_REL}",
    }


def test_a_report_with_a_failed_fixture_is_refused(mini: Mini) -> None:
    failing = [{"name": name, "passed": name != EDUCATIONAL[0], "diagnostics": [] if name != EDUCATIONAL[0] else ["x"]} for name in EDUCATIONAL]
    mini.add_report(_report(results=failing))
    _one(mini.problems(), "all_passed is false")


def test_a_report_whose_all_passed_lies_is_refused(mini: Mini) -> None:
    lying = _report(results=[{"name": name, "passed": name != EDUCATIONAL[0], "diagnostics": []} for name in EDUCATIONAL])
    lying["all_passed"] = True
    mini.add_report(lying)
    _one(mini.problems(), "is not a urml.conformance-report/1 report")


def test_a_report_from_the_mock_adapter_is_refused(mini: Mini) -> None:
    mini.add_report(_report(adapter="urml_ros2_runtime:MockROSAdapter"))
    _one(mini.problems(), "was run against the mock adapter")


def test_a_real_mock_run_is_refused(mini: Mini) -> None:
    report = json.loads(run_suite(filter="educational").model_dump_json())
    mini.add_report(report)
    _one(mini.problems(), "was run against the mock adapter")


def test_a_report_from_another_adapter_is_refused(mini: Mini) -> None:
    mini.add_report(_report(adapter="other_runtime:OtherAdapter"))
    _one(mini.problems(), "not the entry's runtime.adapter")


def test_a_report_from_another_suite_version_is_refused(mini: Mini) -> None:
    mini.add_report(_report(urml_conformance_version="0.0.1"))
    _one(mini.problems(), "re-run it with")


def test_a_claimed_profile_the_report_does_not_run_is_refused(mini: Mini) -> None:
    mini.entry["profiles"] = ["educational", "home"]
    mini.add_report(_report(), profiles=["educational", "home"])
    _one(mini.problems(), "does not run every 'home' fixture")


def test_a_claim_needs_every_fixture_of_the_profile(mini: Mini) -> None:
    short = [{"name": name, "passed": True, "diagnostics": []} for name in EDUCATIONAL[1:]]
    mini.add_report(_report(results=short, fixture_count=len(short)))
    _one(mini.problems(), f"does not run every 'educational' fixture: 1 of {len(EDUCATIONAL)} are missing")


def test_the_profile_selector_runs_the_whole_profile() -> None:
    report = run_suite(profiles=["educational"])
    assert sorted(result.name for result in report.results) == EDUCATIONAL
    assert report.profiles == ["educational"]


def test_a_profile_lives_across_suite_folders() -> None:
    drone = profile_fixtures(REPO_ROOT)["drone"]
    assert {name.split("/", 1)[0] for name in drone} >= {"drone", "fleet", "rulebook"}


def test_a_compatibility_claim_needs_the_runtime_adapter(mini: Mini) -> None:
    mini.add_report(_report())
    del mini.entry["runtime"]["adapter"]
    _one(mini.problems(), "a compatibility claim needs runtime.adapter")


# ---------------------------------------------------------------------------
# Withdrawal, export and the command line
# ---------------------------------------------------------------------------


def test_a_withdrawn_entry_stays_in_the_export_without_a_replay(mini: Mini) -> None:
    path = mini.root / MANIFEST_REL
    path.write_text(
        path.read_text(encoding="utf-8").replace("max_relative_distance: 2.0", "max_relative_distance: 5.0"),
        encoding="utf-8",
        newline="\n",
    )
    mini.entry["status"] = "withdrawn"
    assert mini.problems() == []
    (entry,) = json.loads(render_export(mini.root))["entries"]
    assert entry["status"] == "withdrawn"
    assert entry["validation_records"]["reverified_with"] is None


def test_export_refuses_a_registry_with_problems(mini: Mini) -> None:
    mini.entry["validation_records"]["sha256"] = "0" * 64
    mini.write()
    with pytest.raises(RegistryCheckError):
        render_export(mini.root)
    assert main(["--root", str(mini.root), "export"]) == 1
    assert not (mini.root / EXPORT_PATH).exists()


def test_the_command_line_checks_exports_and_writes_the_schema(
    mini: Mini, capsys: pytest.CaptureFixture[str]
) -> None:
    mini.write()
    assert main(["--root", str(mini.root), "check"]) == 0
    assert "1 entry, no problems" in capsys.readouterr().out
    assert main(["--root", str(mini.root), "export"]) == 0
    raw = (mini.root / EXPORT_PATH).read_bytes()
    assert b"\r\n" not in raw
    assert raw.decode("utf-8") == render_export(mini.root)
    assert main(["--root", str(mini.root), "schema"]) == 0
    assert (mini.root / SCHEMA_PATH).read_text(encoding="utf-8") == render_schema()


def test_the_check_command_reports_problems(mini: Mini, capsys: pytest.CaptureFixture[str]) -> None:
    mini.entry["title"] = "A URML-Certified robot"
    mini.write()
    assert main(["--root", str(mini.root), "check"]) == 1
    assert "problem(s) found" in capsys.readouterr().err
