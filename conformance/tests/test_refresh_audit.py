"""Offline unit tests for the claims-audit re-measurer.

`tools/scripts/refresh_audit.py` turns each suite's pytest output into the
number the maintainer transcribes into docs/launch/claims-audit.md. A suite
with failures must not produce a number: until 2026-09-28 the summary
"2 failed, 280 passed" was read as 280 passed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tools" / "scripts" / "refresh_audit.py"


def _load():
    spec = importlib.util.spec_from_file_location("refresh_audit", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_a_clean_run_reports_its_counts() -> None:
    out = "....  [100%]\n=========== 115 passed, 4 skipped in 1.21s ===========\n"
    assert _load().classify(out, 0)[:3] == ("ok", 115, 4)


def test_a_run_with_failures_has_no_number() -> None:
    out = "FAILED tests/test_x.py::test_y\n========== 2 failed, 280 passed in 19.45s ==========\n"
    kind, reason = _load().classify(out, 1)
    assert kind == "fail"
    assert "2 failed, 280 passed" in reason


def test_collection_errors_count_as_failures() -> None:
    assert _load().classify("========== 1 error, 40 passed in 1.10s ==========\n", 1)[0] == "fail"


def test_expected_failures_are_not_failures() -> None:
    out = "========== 280 passed, 2 xfailed in 19.45s ==========\n"
    assert _load().classify(out, 0)[:3] == ("ok", 280, 0)


def test_a_missing_optional_dependency_is_an_env_row() -> None:
    out = (
        "ImportError while importing test module 'tests/test_x.py'.\n"
        "E   ModuleNotFoundError: No module named 'openai'\n"
    )
    assert _load().classify(out, 2)[0] == "env"
