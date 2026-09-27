"""The conformance report says what ran: adapter, versions, fixture set, filter.

A registry entry links a report as the evidence for a self-reported
URML-compatible claim (spec/conformance/v0.1.0.md section 3), so the report
must name the adapter it ran against and pin the fixtures, and its summary
(all_passed, passed, failed) must be written out and agree with its results.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from types import ModuleType

import pytest
from pydantic import ValidationError
from urml_ros2_runtime import MockROSAdapter
from urml_validator import __version__ as validator_version

from urml_conformance import (
    DEFAULT_ADAPTER,
    REPORT_FORMAT,
    AdapterSpecError,
    ConformanceReport,
    ConformanceRunner,
    __version__,
    discover_fixtures,
    fixture_paths,
    fixtures_root,
    fixtures_sha256,
    load_fixture,
    run_suite,
)


def _quadruped_paths() -> list[Path]:
    return [p for p in fixture_paths() if "quadruped" in load_fixture(p).name]


def test_run_suite_report_says_what_ran() -> None:
    report = run_suite(filter="quadruped")
    assert report.format == REPORT_FORMAT
    assert report.adapter == DEFAULT_ADAPTER
    assert report.urml_conformance_version == __version__
    assert report.urml_validator_version == validator_version
    assert report.filter == "quadruped"
    assert report.results and all(r.name.startswith("quadruped/") for r in report.results)
    assert report.fixture_count == len(report.results) == len(_quadruped_paths())
    assert report.fixtures_sha256 == fixtures_sha256(_quadruped_paths())
    assert report.all_passed and report.passed == len(report.results) and report.failed == 0


def test_unfiltered_run_pins_the_whole_suite() -> None:
    report = run_suite()
    assert report.filter is None
    assert report.fixture_count == len(fixture_paths())
    assert report.fixtures_sha256 == fixtures_sha256(fixture_paths())
    assert report.all_passed, report.render()


def test_serialized_report_carries_the_summary_first() -> None:
    payload = json.loads(run_suite(filter="quadruped").model_dump_json())
    assert payload["format"] == "urml.conformance-report/1"
    assert payload["all_passed"] is True
    assert payload["passed"] == len(payload["results"])
    assert payload["failed"] == 0
    assert list(payload)[-1] == "results"
    assert re.fullmatch(r"[0-9a-f]{64}", payload["fixtures_sha256"])


def test_report_round_trips() -> None:
    report = run_suite(filter="quadruped")
    text = report.model_dump_json(indent=2)
    again = ConformanceReport.model_validate_json(text)
    assert again == report
    assert again.model_dump_json(indent=2) == text


@pytest.mark.parametrize(
    ("key", "value"),
    [("all_passed", False), ("passed", 0), ("failed", 1)],
)
def test_a_summary_the_results_contradict_is_rejected(key: str, value: object) -> None:
    payload = json.loads(run_suite(filter="quadruped").model_dump_json())
    payload[key] = value
    with pytest.raises(ValidationError, match=key):
        ConformanceReport.model_validate(payload)


def test_a_failing_result_makes_all_passed_false() -> None:
    report = ConformanceReport.model_validate(
        {"results": [{"name": "a/one", "passed": True}, {"name": "a/two", "passed": False}]}
    )
    payload = json.loads(report.model_dump_json())
    assert (payload["all_passed"], payload["passed"], payload["failed"]) == (False, 1, 1)


def test_a_report_from_before_the_format_still_parses() -> None:
    report = ConformanceReport.model_validate({"results": [{"name": "home/x", "passed": True}]})
    assert report.adapter is None and report.fixtures_sha256 is None
    assert report.all_passed


def test_unknown_fields_are_still_rejected() -> None:
    with pytest.raises(ValidationError):
        ConformanceReport.model_validate({"results": [], "score": 5})


def test_named_adapter_is_recorded_as_given() -> None:
    spec = "urml_ros2_runtime:MockROSAdapter"
    assert run_suite(spec, filter="quadruped").adapter == spec


def test_a_programmatic_factory_is_named_by_its_module_and_name() -> None:
    cases = [c for c in discover_fixtures() if "quadruped" in c.name]
    report = ConformanceRunner(cases=cases, adapter_factory=MockROSAdapter).run()
    assert report.adapter is not None and report.adapter.endswith(":MockROSAdapter")
    assert report.fixtures_sha256 is None  # handed parsed cases, not files


def test_bad_adapter_spec_raises() -> None:
    with pytest.raises(AdapterSpecError, match="module:attribute"):
        run_suite("no-colon-here")


def test_filter_with_no_match_gives_an_empty_report() -> None:
    report = run_suite(filter="no-such-fixture-zzz")
    assert report.results == [] and report.fixture_count == 0


def test_a_factory_that_raises_fails_cases_not_the_run(monkeypatch: pytest.MonkeyPatch) -> None:
    module = ModuleType("report_test_broken_adapter")

    def make() -> object:
        raise RuntimeError("the SDK is not installed")

    module.make = make  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "report_test_broken_adapter", module)
    report = run_suite("report_test_broken_adapter:make", filter="quadruped")
    assert report.adapter == "report_test_broken_adapter:make"
    assert not report.all_passed
    failed = report.failed_cases()
    assert failed
    assert all(
        any("adapter factory raised: RuntimeError: the SDK is not installed" in d for d in case.diagnostics)
        for case in failed
    )


def test_fixture_digest_pins_names_and_content(tmp_path: Path) -> None:
    (tmp_path / "a").mkdir()
    first = tmp_path / "a" / "01_one.yaml"
    second = tmp_path / "b.yaml"
    first.write_bytes(b"name: a/one\n")
    second.write_bytes(b"name: b\n")
    digest = fixtures_sha256([first, second], tmp_path)
    assert digest == fixtures_sha256([second, first], tmp_path)
    second.write_bytes(b"name: b changed\n")
    changed = fixtures_sha256([first, second], tmp_path)
    assert changed != digest
    moved = tmp_path / "c.yaml"
    second.rename(moved)
    assert fixtures_sha256([first, moved], tmp_path) != changed


def test_fixture_digest_is_the_documented_listing(tmp_path: Path) -> None:
    import hashlib

    one = tmp_path / "one.yaml"
    one.write_bytes(b"x: 1\n")
    file_digest = hashlib.sha256(b"x: 1\n").hexdigest()
    listing = f"{file_digest}  one.yaml\n".encode()
    assert fixtures_sha256([one], tmp_path) == hashlib.sha256(listing).hexdigest()


def test_fixtures_root_default_is_used() -> None:
    assert fixtures_sha256(fixture_paths()) == fixtures_sha256(fixture_paths(), fixtures_root())
