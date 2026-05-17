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
from pathlib import Path

import pytest

from urml_validator.cli import build_parser, main

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
