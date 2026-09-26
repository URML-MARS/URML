"""Tests for the ``python -m urml_conformance`` BYO-adapter entrypoint."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest
from urml_ros2_runtime import URMLRuntime

from urml_conformance.__main__ import _load_adapter_factory, _load_runtime_factory, main


def test_default_run_is_hermetic_and_green() -> None:
    """No --adapter: the MockROSAdapter self-test passes (exit 0)."""
    assert main([]) == 0


def test_filter_selects_a_subset() -> None:
    assert main(["--filter", "quadruped"]) == 0


def test_filter_with_no_match_returns_2() -> None:
    assert main(["--filter", "no-such-fixture-zzz"]) == 2


def test_bad_adapter_spec_is_actionable() -> None:
    with pytest.raises(SystemExit, match="module:attribute"):
        _load_adapter_factory("notacolonspec")


def test_unimportable_adapter_module_is_actionable() -> None:
    with pytest.raises(SystemExit, match="could not import"):
        _load_adapter_factory("urml_conformance._definitely_missing:Thing")


def test_non_callable_attribute_is_rejected() -> None:
    with pytest.raises(SystemExit, match="not callable"):
        _load_adapter_factory("urml_conformance:__doc__")


# ---------------------------------------------------------------------------
# --goal-line and --runtime
# ---------------------------------------------------------------------------


def test_goal_line_self_test_is_green(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--goal-line"]) == 0
    out = capsys.readouterr().out
    assert "URML goal line" in out
    assert "zero adapter calls" in out


def test_goal_line_honors_filter(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["--goal-line", "--filter", "compliance"]) == 0
    assert "3/3 rejected fixtures" in capsys.readouterr().out


def test_goal_line_filter_without_rejected_fixtures_returns_2() -> None:
    assert main(["--goal-line", "--filter", "no-such-fixture-zzz"]) == 2


def test_goal_line_fails_a_leaking_runtime(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    module = ModuleType("goal_line_leaky_runtime")
    module.make = lambda adapter: URMLRuntime(adapter, revalidate=False)  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "goal_line_leaky_runtime", module)
    assert main(["--goal-line", "--runtime", "goal_line_leaky_runtime:make"]) == 1
    out = capsys.readouterr().out
    assert "goal_line_leaky_runtime:make" in out
    assert "[FAIL]" in out


def test_runtime_flag_needs_goal_line() -> None:
    with pytest.raises(SystemExit):
        main(["--runtime", "urml_ros2_runtime:URMLRuntime"])


def test_bad_runtime_spec_is_actionable() -> None:
    with pytest.raises(SystemExit, match="--runtime must be 'module:attribute'"):
        _load_runtime_factory("notacolonspec")
