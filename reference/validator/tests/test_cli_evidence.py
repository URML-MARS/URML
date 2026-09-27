"""`--evidence-log` on `urml validate`, `execute`, `run` and `translate`.

Every verdict a command makes lands in the log as one validation record, and
turning the log on changes nothing the command prints or returns. Hermetic:
the echo provider stands in for the model and the mock adapter for the robot.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from urml_validator.cli import main
from urml_validator.errors import ValidationResult
from urml_validator.evidence import ValidationRecord, content_digest, read_records, reverify

REPO_ROOT = Path(__file__).resolve().parents[3]
HOME = REPO_ROOT / "examples" / "home"
PROGRAM = HOME / "red-mug.urml.yaml"
GRASP_4N = HOME / "red-mug.grasp-4n.urml.yaml"
MANIFEST = HOME / "red-mug.manifest.yaml"
CN_MANIFEST = HOME / "red-mug.cn-critical.manifest.yaml"
ENVELOPE = HOME / "red-mug.envelope.yaml"
DOC = REPO_ROOT / "docs" / "evidence" / "validation-records.md"

REQUEST = "Pick up the mug and squeeze it hard."


def _load(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _run(argv: list[str], capsys: pytest.CaptureFixture[str]) -> tuple[int, str, str]:
    code = main(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def _same_with_and_without_the_log(
    argv: list[str], log: Path, capsys: pytest.CaptureFixture[str]
) -> int:
    """Run ``argv`` without, then with, ``--evidence-log``: exit code and output match."""
    plain = _run(argv, capsys)
    assert not log.exists()
    logged = _run([*argv, "--evidence-log", str(log)], capsys)
    assert logged == plain
    return logged[0]


def _echo(tmp_path: Path, *programs: dict[str, Any]) -> Path:
    """An echo-response file: one scripted emission per bridge attempt."""
    path = tmp_path / "echo.json"
    path.write_text(json.dumps(list(programs)), encoding="utf-8")
    return path


def _bridge_argv(command: str, echo: Path, *extra: str) -> list[str]:
    return [
        command, REQUEST,
        "--manifest", str(MANIFEST),
        "--envelope", str(ENVELOPE),
        "--profile", "home",
        "--no-policy",
        "--provider", "echo",
        "--echo-response-file", str(echo),
        *extra,
    ]


# ---------------------------------------------------------------------------
# urml validate
# ---------------------------------------------------------------------------


def test_validate_records_a_refusal(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    log = tmp_path / "evidence.jsonl"
    argv = [
        "validate", str(GRASP_4N), "-m", str(MANIFEST), "-e", str(ENVELOPE),
        "--profile", "home", "--no-policy",
    ]
    assert _same_with_and_without_the_log(argv, log, capsys) == 1
    (record,) = read_records(log)
    assert (record.surface, record.stage, record.verdict) == ("validate", "validation", "refused")
    assert record.codes == ["envelope.force_exceeded"]
    assert record.program == _load(GRASP_4N)
    assert record.program_digest == content_digest(_load(GRASP_4N))
    assert record.manifest_digest == content_digest(_load(MANIFEST))
    assert record.envelope_digest == content_digest(_load(ENVELOPE))
    assert record.robot_id == "turtlebot4_red_mug"
    assert record.policy == "none"
    assert record.profiles == ["home"]
    assert record.default_rulebooks is True and record.rulebooks == []
    assert record.as_of is None  # validate lets the validator pick today's date
    assert (record.request, record.attempts, record.attempt_codes) == (None, None, None)
    check = reverify(record, manifest=_load(MANIFEST), envelope=_load(ENVELOPE), policy=None)
    assert check.reproduced, check.problems


def test_validate_records_an_acceptance(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    log = tmp_path / "evidence.jsonl"
    argv = ["validate", str(PROGRAM), "-m", str(MANIFEST), "-e", str(ENVELOPE), "--profile", "home", "--json"]
    assert _same_with_and_without_the_log(argv, log, capsys) == 0
    (record,) = read_records(log)
    assert record.verdict == "accepted" and record.codes == []
    assert record.policy == "default"
    assert record.result == json.loads(_run(argv, capsys)[1])


def test_validate_appends_one_line_per_verdict(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    log = tmp_path / "nested" / "evidence.jsonl"
    common = ["-m", str(MANIFEST), "-e", str(ENVELOPE), "--profile", "home", "--evidence-log", str(log)]
    assert _run(["validate", str(PROGRAM), *common], capsys)[0] == 0
    assert _run(["validate", str(GRASP_4N), *common], capsys)[0] == 1
    assert [r.verdict for r in read_records(log)] == ["accepted", "refused"]
    assert len(log.read_text(encoding="utf-8").splitlines()) == 2


def test_no_flag_writes_no_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    assert _run(["validate", str(GRASP_4N), "-m", str(MANIFEST), "-e", str(ENVELOPE)], capsys)[0] == 1
    assert list(tmp_path.iterdir()) == []


def test_a_log_that_cannot_be_written_is_a_usage_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code, out, err = _run(
        ["validate", str(PROGRAM), "-m", str(MANIFEST), "--evidence-log", str(tmp_path)], capsys
    )
    assert code == 2
    assert out == ""
    assert "cannot write the evidence log" in err


# ---------------------------------------------------------------------------
# urml execute
# ---------------------------------------------------------------------------


def test_execute_records_the_pre_check_refusal(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    log = tmp_path / "evidence.jsonl"
    argv = [
        "execute", str(GRASP_4N), "-m", str(MANIFEST), "-e", str(ENVELOPE),
        "--profile", "home", "--no-policy", "--adapter", "mock",
    ]
    assert _same_with_and_without_the_log(argv, log, capsys) == 1
    (record,) = read_records(log)
    assert (record.surface, record.stage, record.verdict) == ("execute", "validation", "refused")
    assert record.codes == ["envelope.force_exceeded"]
    assert record.as_of is not None  # execute validates twice on one date


def test_execute_records_one_verdict_when_it_runs(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import urml_ros2_runtime

    seen: list[dict[str, Any]] = []
    real = urml_ros2_runtime.URMLRuntime

    class _Spy(real):  # type: ignore[misc,valid-type]
        def __init__(self, adapter: Any, **kwargs: Any) -> None:
            seen.append(kwargs)
            super().__init__(adapter, **kwargs)

    monkeypatch.setattr(urml_ros2_runtime, "URMLRuntime", _Spy)
    log = tmp_path / "evidence.jsonl"
    argv = [
        "execute", str(PROGRAM), "-m", str(MANIFEST), "-e", str(ENVELOPE),
        "--profile", "home", "--no-policy", "--adapter", "mock",
    ]
    assert _same_with_and_without_the_log(argv, log, capsys) == 0
    (record,) = read_records(log)
    assert (record.surface, record.verdict) == ("execute", "accepted")
    # The runtime gets the log, so its own refusals would land there too.
    assert seen == [{"evidence_log": None}, {"evidence_log": log}]


def test_execute_runtime_refusal_is_recorded_by_the_runtime(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A pre-check that lets the program through leaves the runtime's own check to refuse it."""
    import urml_validator.cli as cli

    monkeypatch.setattr(cli, "validate", lambda *args, **kwargs: ValidationResult(accepted=True))
    log = tmp_path / "evidence.jsonl"
    code, out, err = _run(
        [
            "execute", str(GRASP_4N), "-m", str(MANIFEST), "-e", str(ENVELOPE),
            "--profile", "home", "--no-policy", "--adapter", "mock", "--evidence-log", str(log),
        ],
        capsys,
    )
    assert code == 64 and "runtime rejected a pre-validated program" in err
    assert "URML execute:" not in out
    pre_check, runtime = read_records(log)
    assert (pre_check.surface, pre_check.verdict) == ("execute", "accepted")
    assert (runtime.surface, runtime.stage, runtime.verdict) == ("runtime", "revalidation", "refused")
    assert runtime.codes == ["envelope.force_exceeded"]
    assert runtime.as_of == pre_check.as_of


# ---------------------------------------------------------------------------
# urml translate and urml run
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("command", ["translate", "run"])
def test_a_bridge_refusal_is_recorded(
    command: str, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    grasp = _load(GRASP_4N)
    log = tmp_path / "evidence.jsonl"
    argv = _bridge_argv(command, _echo(tmp_path, grasp, grasp), "--max-revisions", "1")
    if command == "run":
        argv += ["--adapter", "mock"]
    assert _same_with_and_without_the_log(argv, log, capsys) == 1
    (record,) = read_records(log)
    assert (record.surface, record.stage, record.verdict) == (command, "bridge", "refused")
    assert record.request == REQUEST
    assert record.attempts == 2
    assert record.attempt_codes == [["envelope.force_exceeded"], ["envelope.force_exceeded"]]
    assert record.codes == ["envelope.force_exceeded"]
    assert record.program == grasp  # the parsed emission the final verdict judged
    assert (record.as_of is not None) is (command == "run")
    check = reverify(record, manifest=_load(MANIFEST), envelope=_load(ENVELOPE), policy=None)
    assert check.reproduced, check.problems


@pytest.mark.parametrize("command", ["translate", "run"])
def test_a_bridge_acceptance_is_recorded(
    command: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    import urml_ros2_runtime

    seen: list[dict[str, Any]] = []
    real = urml_ros2_runtime.URMLRuntime

    class _Spy(real):  # type: ignore[misc,valid-type]
        def __init__(self, adapter: Any, **kwargs: Any) -> None:
            seen.append(kwargs)
            super().__init__(adapter, **kwargs)

    monkeypatch.setattr(urml_ros2_runtime, "URMLRuntime", _Spy)
    program = _load(PROGRAM)
    log = tmp_path / "evidence.jsonl"
    argv = _bridge_argv(command, _echo(tmp_path, program))
    if command == "run":
        argv += ["--adapter", "mock"]
    assert _same_with_and_without_the_log(argv, log, capsys) == 0
    (record,) = read_records(log)  # the runtime records only its own refusals
    assert (record.surface, record.stage, record.verdict) == (command, "bridge", "accepted")
    assert record.program == program  # as judged, before the request is copied into it
    assert (record.request, record.attempts, record.attempt_codes) == (REQUEST, 1, [[]])
    if command == "run":
        assert seen == [{"evidence_log": None}, {"evidence_log": log}]


def test_a_policy_refusal_through_the_bridge_is_recorded(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    log = tmp_path / "evidence.jsonl"
    argv = [
        "translate", REQUEST, "--manifest", str(CN_MANIFEST), "--profile", "home",
        "--provider", "echo", "--echo-response-file", str(_echo(tmp_path, _load(PROGRAM))),
    ]
    assert _same_with_and_without_the_log(argv, log, capsys) == 1
    (record,) = read_records(log)
    assert record.verdict == "refused" and record.policy == "default"
    assert record.codes and all(code.startswith("policy.") for code in record.codes)
    assert record.attempts == 1


def test_a_provider_error_writes_no_record(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """The bridge ended without a verdict (the model stopped answering), so nothing is recorded."""
    log = tmp_path / "evidence.jsonl"
    argv = _bridge_argv(
        "translate", _echo(tmp_path, _load(GRASP_4N)), "--max-revisions", "1", "--evidence-log", str(log)
    )
    code, _, err = _run(argv, capsys)
    assert code == 1 and "provider error" in err
    assert not log.exists()


# ---------------------------------------------------------------------------
# The documented example is a real, replayable record
# ---------------------------------------------------------------------------


def _documented_record() -> ValidationRecord:
    text = DOC.read_text(encoding="utf-8")
    lines = re.findall(r"^\{\"as_of\".*\}$", text, flags=re.MULTILINE)
    assert len(lines) == 1, "the page shows exactly one record line"
    return ValidationRecord.model_validate(json.loads(lines[0]))


def test_the_documented_record_replays() -> None:
    record = _documented_record()
    assert (record.surface, record.verdict, record.codes) == ("validate", "refused", ["envelope.force_exceeded"])
    assert record.program == _load(GRASP_4N)
    check = reverify(record, manifest=_load(MANIFEST), envelope=_load(ENVELOPE), policy=None)
    assert check.reproduced, check.problems
