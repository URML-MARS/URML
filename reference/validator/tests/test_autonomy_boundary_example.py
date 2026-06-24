"""The autonomy-boundary worked example must be deterministic and true.

Mirrors the other example guards: the generator is deterministic, the committed
``autonomy-boundary-report.txt`` matches it, and the report demonstrates the
boundary Discussion #526 asked about (the mastermind decides; URML validates and
executes each physical action; a perception judgment expressed as a URML step is
refused). Hermetic: validator + mock substrate, no robot.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "autonomy-boundary"
GEN_PATH = EX / "autonomy_patrol.py"
COMMITTED = EX / "autonomy-boundary-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("autonomy_patrol", GEN_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generator_is_deterministic() -> None:
    gen = _load_gen()
    assert gen.render_report() == gen.render_report()


def test_committed_report_matches_generator() -> None:
    gen = _load_gen()
    assert COMMITTED.exists(), f"missing {COMMITTED}"
    assert COMMITTED.read_text(encoding="utf-8") == gen.render_report(), (
        "examples/autonomy-boundary/autonomy-boundary-report.txt is stale; "
        "run `python examples/autonomy-boundary/autonomy_patrol.py` and commit."
    )


def test_physical_actions_validate_and_perception_is_refused() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # Physical actions the mastermind issues validate and execute.
    assert "[VALID]  drive 0.50 m" in report
    assert "[VALID]  capture photo (current view)" in report
    assert "success=True" in report
    assert "[REJECTED]" not in report.split("# The boundary")[0]
    # The perception judgment, pushed down as a URML detect, is refused.
    assert "detect(object: unclassified_shape)  ->  [REJECTED] capability.missing_object_class" in report
