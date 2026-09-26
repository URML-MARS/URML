"""CLI surface of the rulebook pass (RFC-0702, Draft).

`--rulebook PATH` (repeatable) and `--no-default-rulebooks` on validate,
execute, run, translate and bench; `--no-policy` leaves rulebooks alone; the
pretty output lists the applied rulebooks with their obligations; `urml
schema --name rulebook` prints the format.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path
from typing import Any

import pytest
import yaml

from urml_validator.cli import build_parser, main

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).parent / "fixtures"
DRONE = FIXTURES / "manifests" / "drone_high_ceiling.yaml"
WAREHOUSE = FIXTURES / "manifests" / "warehouse_areas.yaml"
HOME = FIXTURES / "manifests" / "turtlebot4_home.yaml"
RED_MUG = REPO_ROOT / "examples" / "home" / "red-mug.urml.yaml"
WAIVER = REPO_ROOT / "examples" / "rulebooks" / "example-deployment.yaml"
WAREHOUSE_RULES = REPO_ROOT / "examples" / "rulebooks" / "example-warehouse.yaml"
TEMPLATE = REPO_ROOT / "examples" / "rulebooks" / "industrial-template.yaml"
NO_REMOTE_ID = FIXTURES / "rulebooks" / "deployment_no_remote_id.yaml"

HEADLINE = (
    "14 CFR 107.51(b): maximum altitude 400 feet (121.92 m) above ground level. "
    "take_off.altitude is 137.16 m; the limit is 121.92 m."
)

FLIGHT_450 = {
    "profile": "drone",
    "behavior": {
        "type": "sequence",
        "on_error": "abort_and_report",
        "steps": [{"take_off": {"altitude": 137.16}}, {"land": {}}],
    },
}


@pytest.fixture()
def flight_450(tmp_path: Path) -> Path:
    path = tmp_path / "flight-450ft.urml.yaml"
    path.write_text(yaml.safe_dump(FLIGHT_450, sort_keys=False), encoding="utf-8")
    return path


def _write(tmp_path: Path, name: str, data: dict[str, Any]) -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("command", ["validate", "execute", "run", "translate", "bench"])
def test_every_validating_command_takes_the_rulebook_flags(command: str) -> None:
    argv = {
        "validate": ["validate", "p.yaml", "-m", "m.yaml"],
        "execute": ["execute", "p.yaml", "-m", "m.yaml"],
        "run": ["run", "go", "-m", "m.yaml"],
        "translate": ["translate", "go", "-m", "m.yaml"],
        "bench": ["bench", "--corpus", "c.yaml", "-m", "m.yaml"],
    }[command]
    args = build_parser().parse_args(
        [*argv, "--rulebook", "a.yaml", "--rulebook", "b.yaml", "--no-default-rulebooks", "--no-policy"]
    )
    assert args.rulebook_paths == [Path("a.yaml"), Path("b.yaml")]
    assert args.no_default_rulebooks is True and args.no_policy is True


def test_validate_refuses_a_450_foot_take_off_with_no_policy(flight_450: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["validate", str(flight_450), "-m", str(DRONE), "--no-policy"])
    err = capsys.readouterr().err
    assert rc == 1
    assert "ERROR [rule.cap_exceeded] behavior/steps/0" in err
    assert HEADLINE in err
    assert "rule: us_faa_part107/altitude_400ft_agl (Federal Aviation Administration, US)" in err
    assert "source: https://www.ecfr.gov/" in err
    assert "rulebooks (a program that passes is not a legal compliance determination):" in err
    assert "- 14 CFR 107.31: Visual line of sight for the whole flight" in err


def test_the_example_waiver_accepts_it_with_a_warning(flight_450: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # The CLI validates as of today; the fictional waiver expires on 2027-03-31.
    expired = datetime.datetime.now(datetime.UTC).date() > datetime.date(2027, 3, 31)
    rc = main(["validate", str(flight_450), "-m", str(DRONE), "--no-policy", "--rulebook", str(WAIVER)])
    out = capsys.readouterr().out
    assert rc == (1 if expired else 0)
    if not expired:
        assert "WARN  [rule.cap_exceeded]" in out
        assert "allowed by exception: Certificate of waiver 107W-EXAMPLE-0001" in out
        assert "exception: applies (deployment rulebook example_aerial_survey_north_tower)" in out
        assert "example_aerial_survey_north_tower (deployment)" in out
        assert "declares remote_id: broadcast_module" in out


def test_no_default_rulebooks_warns_and_accepts(flight_450: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["validate", str(flight_450), "-m", str(DRONE), "--no-policy", "--no-default-rulebooks"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "urml: warning: --no-default-rulebooks switches off the bundled rulebooks (us_faa_part107)" in captured.err
    assert "WARN  [rule.defaults_disabled] <rulebook>/us_faa_part107" in captured.out


def test_json_carries_the_rulebooks_only_when_one_applied(flight_450: Path, capsys: pytest.CaptureFixture[str]) -> None:
    main(["validate", str(flight_450), "-m", str(DRONE), "--no-policy", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["rulebooks"][0]["rulebook_id"] == "us_faa_part107"
    assert payload["errors"][0]["detail"]["cite"]["text"] == "14 CFR 107.51(b)"
    main(["validate", str(RED_MUG), "-m", str(HOME), "--json"])
    assert "rulebooks" not in json.loads(capsys.readouterr().out)


def test_the_home_output_is_unchanged(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["validate", str(RED_MUG), "-m", str(HOME)])
    out = capsys.readouterr().out
    assert rc == 0 and out == f"Validation passed: {RED_MUG}\n"


def test_an_organization_rulebook_file(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    program = _write(
        tmp_path,
        "p.yaml",
        {"profile": "warehouse", "behavior": {"type": "sequence", "steps": [{"move_to": {"location": "server_room"}}]}},
    )
    rc = main(["validate", str(program), "-m", str(WAREHOUSE), "--no-policy", "--rulebook", str(WAREHOUSE_RULES)])
    err = capsys.readouterr().err
    assert rc == 1 and "ERROR [rule.zone_forbidden]" in err
    assert "example_logistics_operations: Example Logistics robot operating rules (fictional)" in err
    assert "- Example Logistics Robot Operating Policy, section 2.1 (fictional): Only trained staff start robot programs" in err


def test_a_rulebook_that_breaks_the_format_refuses_the_program(flight_450: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["validate", str(flight_450), "-m", str(DRONE), "--no-policy", "--rulebook", str(TEMPLATE)])
    err = capsys.readouterr().err
    assert rc == 1
    assert "ERROR [rule.rulebook_invalid] <rulebook>/FILL_IN" in err
    assert "problem: rulebook_id: String should match pattern" in err


def test_a_missing_or_unparseable_rulebook_file_is_a_usage_error(
    tmp_path: Path, flight_450: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    rc = main(["validate", str(flight_450), "-m", str(DRONE), "--rulebook", str(tmp_path / "missing.yaml")])
    assert rc == 2 and "rulebook file not found" in capsys.readouterr().err
    listed = tmp_path / "list.yaml"
    listed.write_text("- a\n- b\n", encoding="utf-8")
    rc = main(["validate", str(flight_450), "-m", str(DRONE), "--rulebook", str(listed)])
    assert rc == 2 and "did not contain a YAML mapping" in capsys.readouterr().err


def test_schema_name_rulebook(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["schema", "--name", "rulebook"]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert schema["$id"].endswith("urml-rulebook.schema.json")
    assert "rulebook_id" in schema["properties"]


def test_execute_refuses_before_any_adapter_call(flight_450: Path, capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["execute", str(flight_450), "-m", str(DRONE), "--no-policy", "--adapter", "mock"])
    captured = capsys.readouterr()
    assert rc == 1
    assert "execution refused" in captured.err and HEADLINE in captured.err
    assert "URML execute:" not in captured.out


def test_execute_hands_the_rulebooks_to_the_runtime(
    flight_450: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import urml_ros2_runtime

    seen: list[dict[str, Any]] = []
    real = urml_ros2_runtime.URMLRuntime

    class _Spy(real):  # type: ignore[misc,valid-type]
        def execute(self, *args: Any, **kwargs: Any) -> Any:
            seen.append(kwargs)
            return super().execute(*args, **kwargs)

    monkeypatch.setattr(urml_ros2_runtime, "URMLRuntime", _Spy)
    rc = main([
        "execute", str(flight_450), "-m", str(DRONE), "--no-policy", "--adapter", "mock",
        "--no-default-rulebooks", "--rulebook", str(WAIVER),
    ])
    assert rc == 0, capsys.readouterr().err
    (kwargs,) = seen
    assert kwargs["default_rulebooks"] is False
    assert [book["rulebook_id"] for book in kwargs["rulebooks"]] == ["example_aerial_survey_north_tower"]
    assert kwargs["as_of"] is not None


def test_translate_revises_toward_the_rule(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    lower = {**FLIGHT_450, "behavior": {**FLIGHT_450["behavior"], "steps": [{"take_off": {"altitude": 100.0}}, {"land": {}}]}}
    echo = tmp_path / "echo.json"
    echo.write_text(json.dumps([FLIGHT_450, lower]), encoding="utf-8")
    rc = main([
        "translate", "Take off to 450 feet.", "-m", str(DRONE), "--profile", "drone", "--no-policy",
        "--provider", "echo", "--echo-response-file", str(echo),
    ])
    captured = capsys.readouterr()
    assert rc == 0, captured.err
    assert "Translation accepted after 1 revision(s)" in captured.err
    assert "altitude: 100.0" in captured.out


def test_translate_stops_on_a_deployment_problem(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    low = {**FLIGHT_450, "behavior": {**FLIGHT_450["behavior"], "steps": [{"take_off": {"altitude": 30.0}}]}}
    echo = tmp_path / "echo.json"
    echo.write_text(json.dumps([low, low]), encoding="utf-8")
    rc = main([
        "translate", "Take off.", "-m", str(DRONE), "--profile", "drone", "--no-policy",
        "--provider", "echo", "--echo-response-file", str(echo), "--rulebook", str(NO_REMOTE_ID),
    ])
    err = capsys.readouterr().err
    assert rc == 1
    assert "translation stopped after 1 attempt(s): a rulebook needs a deployment change" in err
    assert "ERROR [rule.declaration_missing]" in err


def test_run_stops_on_a_deployment_problem_before_any_adapter(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    low = {**FLIGHT_450, "behavior": {**FLIGHT_450["behavior"], "steps": [{"take_off": {"altitude": 30.0}}]}}
    echo = tmp_path / "echo.json"
    echo.write_text(json.dumps(low), encoding="utf-8")
    rc = main([
        "run", "Take off.", "-m", str(DRONE), "--profile", "drone", "--no-policy",
        "--provider", "echo", "--echo-response-file", str(echo), "--rulebook", str(NO_REMOTE_ID),
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert "run aborted after 1 attempt(s): a rulebook needs a deployment change" in captured.err
    assert "URML execute:" not in captured.out
