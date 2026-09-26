"""`urml execute` behavior tests.

Exercise `urml_validator.cli:main execute ...` end-to-end against the
canonical fixtures, in-process (no subprocess). The default `mock` adapter
is hermetic and zero-dependency, so the happy path runs anywhere the
bootstrap venv runs. The ros2/px4 adapter paths are tested only for their
clean "optional dep missing" behavior; their live execution is covered by
the gated integration suites.
"""

from __future__ import annotations

import importlib.util
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

from urml_validator.cli import _emit_execute_pretty, build_parser, main

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_ROOT = Path(__file__).parent / "fixtures"
EXAMPLES_ROOT = REPO_ROOT / "examples"

RED_MUG = EXAMPLES_ROOT / "home" / "red-mug.urml.yaml"
MANIFEST = FIXTURE_ROOT / "manifests" / "turtlebot4_home.yaml"
ENVELOPE = FIXTURE_ROOT / "envelopes" / "home_default.yaml"
CN_CRITICAL = FIXTURE_ROOT / "manifests" / "turtlebot4_home_cn_critical.yaml"
DRONE_MANIFEST = FIXTURE_ROOT / "manifests" / "drone_civilian.yaml"

_RCLPY_AVAILABLE = importlib.util.find_spec("rclpy") is not None


# ---------------------------------------------------------------------------
# Parser wiring
# ---------------------------------------------------------------------------


def test_execute_subcommand_is_registered() -> None:
    """`execute` is a real subcommand with the documented options."""
    parser = build_parser()
    ns = parser.parse_args([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--adapter",
        "mock",
        "--no-policy",
    ])
    assert ns.command == "execute"
    assert ns.adapter == "mock"
    assert ns.no_policy is True


# ---------------------------------------------------------------------------
# Happy path (hermetic mock)
# ---------------------------------------------------------------------------


def test_execute_mock_red_mug_succeeds(capsys: pytest.CaptureFixture[str]) -> None:
    """The canonical red-mug program runs to completion on the mock adapter."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--envelope",
        str(ENVELOPE),
        "--profile",
        "home",
        "--no-policy",
    ])
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "RESULT: SUCCESS" in out
    assert "5 step(s) executed" in out
    # The audit trace proves each primitive actually dispatched.
    assert "send_navigation_goal" in out
    assert "query_detection" in out
    assert "send_manipulation_goal" in out


def test_execute_mock_labels_substrate_honestly(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Plan criterion 2: the mock substrate is labeled as a mock, bluntly."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--no-policy",
    ])
    out = capsys.readouterr().out
    assert rc == 0
    assert "HERMETIC MOCK" in out
    assert "no actuator moved" in out.lower()


def test_execute_json_output_is_machine_readable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--json` emits a parseable envelope with the mock flag set true."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--no-policy",
        "--json",
    ])
    out = capsys.readouterr().out
    assert rc == 0
    payload = json.loads(out)
    assert payload["adapter"] == "mock"
    assert payload["substrate_is_mock"] is True
    assert payload["revalidated"] is True
    assert payload["result"]["success"] is True
    assert payload["result"]["steps_executed"] == 5


# ---------------------------------------------------------------------------
# The validator is not bypassed (CLAUDE.md safety boundary)
# ---------------------------------------------------------------------------


def test_execute_default_policy_refuses_noncompliant(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Without --no-policy, a CN-critical manifest is refused before any step."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(CN_CRITICAL),
        "--profile",
        "home",
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert "execution refused" in captured.err.lower()
    assert "policy.country_denied" in captured.err
    # Nothing executed: no audit trace printed.
    assert "RESULT: SUCCESS" not in captured.out


def test_execute_no_policy_lets_compliance_be_skipped(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--no-policy` is honored end to end: the CN-critical manifest runs.

    This proves the CLI validates with the *caller's* policy choice rather
    than letting the runtime's own default-policy re-validation override it.
    """
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(CN_CRITICAL),
        "--profile",
        "home",
        "--no-policy",
    ])
    out = capsys.readouterr().out
    assert rc == 0, out
    assert "RESULT: SUCCESS" in out


def _spy_on_runtime(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, dict[str, Any]]]:
    """Record how the CLI builds and calls URMLRuntime (the real one still runs)."""
    import urml_ros2_runtime

    seen: list[tuple[str, dict[str, Any]]] = []
    real = urml_ros2_runtime.URMLRuntime

    class _Spy(real):  # type: ignore[misc,valid-type]
        def __init__(self, adapter: Any, **kwargs: Any) -> None:
            seen.append(("init", kwargs))
            super().__init__(adapter, **kwargs)

        def execute(self, *args: Any, **kwargs: Any) -> Any:
            seen.append(("execute", kwargs))
            return super().execute(*args, **kwargs)

    monkeypatch.setattr(urml_ros2_runtime, "URMLRuntime", _Spy)
    return seen


def test_execute_runtime_revalidates_with_the_chosen_policy(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The runtime's own check runs, under the caller's policy and manifest dir."""
    seen = _spy_on_runtime(monkeypatch)
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(CN_CRITICAL),
        "--profile",
        "home",
        "--no-policy",
    ])
    assert rc == 0, capsys.readouterr().err
    (init_kind, init_kwargs), (exec_kind, exec_kwargs) = seen
    assert (init_kind, exec_kind) == ("init", "execute")
    assert init_kwargs.get("revalidate", True) is True
    assert exec_kwargs["policy"] is None
    assert exec_kwargs["manifest_base_dir"] == CN_CRITICAL.parent


def test_execute_runtime_gets_a_custom_policy_file(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    seen = _spy_on_runtime(monkeypatch)
    policy_path = FIXTURE_ROOT / "policies" / "permissive.yaml"
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--profile",
        "home",
        "--policy",
        str(policy_path),
    ])
    assert rc == 0, capsys.readouterr().err
    exec_kwargs = dict(seen)["execute"]
    assert isinstance(exec_kwargs["policy"], dict)
    assert exec_kwargs["policy"]["policy_id"] == _load_yaml_mapping(policy_path)["policy_id"]


def _load_yaml_mapping(path: Path) -> dict[str, Any]:
    import yaml

    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


_NO_ENVELOPE_WARNING = "urml: warning: --adapter px4 runs with no --envelope"


def test_execute_real_adapter_without_envelope_warns_first(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """One stderr line, printed before the real adapter is built."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--no-policy",
        "--adapter",
        "px4",
        "--adapter-config",
        str(tmp_path / "no_such.yaml"),
    ])
    err = capsys.readouterr().err
    assert rc == 2  # the adapter build fails after the warning
    lines = err.splitlines()
    warning = [line for line in lines if line.startswith(_NO_ENVELOPE_WARNING)]
    assert len(warning) == 1
    assert "only the manifest's limits apply" in warning[0]
    build_error = next(i for i, line in enumerate(lines) if "adapter-config file not found" in line)
    assert lines.index(warning[0]) < build_error


def test_execute_real_adapter_with_envelope_does_not_warn(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--envelope",
        str(ENVELOPE),
        "--no-policy",
        "--adapter",
        "px4",
        "--adapter-config",
        str(tmp_path / "no_such.yaml"),
    ])
    err = capsys.readouterr().err
    assert rc == 2
    assert "--envelope" not in err


def test_execute_mock_adapter_does_not_warn(capsys: pytest.CaptureFixture[str]) -> None:
    rc = main(["execute", str(RED_MUG), "--manifest", str(MANIFEST), "--no-policy"])
    assert rc == 0
    assert "warning" not in capsys.readouterr().err


def test_execute_capability_mismatch_refused(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A program the manifest cannot satisfy is refused, not executed."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(DRONE_MANIFEST),
        "--no-policy",
    ])
    captured = capsys.readouterr()
    assert rc == 1
    assert "execution refused" in captured.err.lower()
    assert "RESULT: SUCCESS" not in captured.out


# ---------------------------------------------------------------------------
# Usage errors exit 2 with a hint, never a traceback
# ---------------------------------------------------------------------------


def test_execute_missing_program_exits_2(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    rc = main([
        "execute",
        str(tmp_path / "nope.yaml"),
        "--manifest",
        str(MANIFEST),
        "--no-policy",
    ])
    err = capsys.readouterr().err
    assert rc == 2
    assert "program file not found" in err.lower()


@pytest.mark.skipif(
    _RCLPY_AVAILABLE,
    reason="rclpy is importable here; the missing-dep path can't be exercised.",
)
def test_execute_ros2_without_ros_env_exits_2(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Plan criterion 2: --adapter ros2 with no ROS env exits 2 + a hint."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--no-policy",
        "--adapter",
        "ros2",
    ])
    err = capsys.readouterr().err
    assert rc == 2
    assert "ros 2 environment" in err.lower()
    assert "--adapter mock" in err
    # No traceback leaked.
    assert "Traceback" not in err


def test_execute_adapter_config_not_found_exits_2(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A missing --adapter-config for px4 is a clean usage error."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--no-policy",
        "--adapter",
        "px4",
        "--adapter-config",
        str(tmp_path / "no_such.yaml"),
    ])
    err = capsys.readouterr().err
    assert rc == 2
    assert "adapter-config file not found" in err.lower()
    assert "Traceback" not in err


# ---------------------------------------------------------------------------
# The trace renderer does not imply "nothing happened" when an adapter
# simply keeps no call log (the PX4Adapter case the flight demo relies on)
# ---------------------------------------------------------------------------


@dataclass
class _StubResult:
    """Minimal stand-in for RuntimeResult for the pretty-printer."""

    success: bool
    steps_executed: int
    audit_log: list[dict[str, Any]] = field(default_factory=list)
    bindings: dict[str, Any] = field(default_factory=dict)
    last_outcome: Any = None


def test_trace_render_no_call_log_does_not_claim_empty_tree(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Steps ran but the adapter logged nothing (px4): say so, honestly."""
    rr = _StubResult(success=True, steps_executed=4, audit_log=[])
    _emit_execute_pretty(rr, "px4", program_path=Path("flight.yaml"))
    out = capsys.readouterr().out
    assert "4 step(s) dispatched" in out
    assert "keeps\n    no call log" in out or "keeps no call log" in out
    # The misleading old wording must not appear when steps actually ran.
    assert "behavior tree was empty" not in out
    assert "RESULT: SUCCESS" in out


def test_trace_render_empty_tree_when_zero_steps(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Genuinely-empty behavior tree still reports as empty."""
    rr = _StubResult(success=True, steps_executed=0, audit_log=[])
    _emit_execute_pretty(rr, "mock", program_path=Path("empty.yaml"))
    out = capsys.readouterr().out
    assert "behavior tree was empty" in out


# ---------------------------------------------------------------------------
# --adapter ardupilot is wired the same way as px4
# ---------------------------------------------------------------------------


def test_execute_accepts_ardupilot_adapter_choice() -> None:
    parser = build_parser()
    args = parser.parse_args(["execute", "prog.yaml", "-m", "man.yaml", "--adapter", "ardupilot"])
    assert args.adapter == "ardupilot"


def test_execute_ardupilot_adapter_config_not_found_exits_2(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing --adapter-config for ardupilot is a clean usage error, no traceback."""
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--no-policy",
        "--adapter",
        "ardupilot",
        "--adapter-config",
        str(tmp_path / "no_such.yaml"),
    ])
    err = capsys.readouterr().err
    assert rc == 2
    assert "adapter-config file not found" in err.lower()
    assert "Traceback" not in err


def test_execute_ardupilot_missing_package_is_actionable(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Without urml-ardupilot-runtime installed, exit 2 with the install hint."""
    import sys

    monkeypatch.setitem(sys.modules, "urml_ardupilot_runtime", None)  # type: ignore[arg-type]
    rc = main([
        "execute",
        str(RED_MUG),
        "--manifest",
        str(MANIFEST),
        "--no-policy",
        "--adapter",
        "ardupilot",
    ])
    err = capsys.readouterr().err
    assert rc == 2
    assert "urml-ardupilot-runtime" in err
    assert "Traceback" not in err
