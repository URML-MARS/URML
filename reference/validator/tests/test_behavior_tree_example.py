"""The AutoAPMS behavior-tree lowering example must be deterministic and true.

Mirrors the other example guards: deterministic generator, committed
``bt-report.txt`` matches, and the validate-then-lower flow decides correctly (an
admissible program lowers to a BehaviorTree.CPP tree; an undeclared-location
program is refused before lowering). From the AutoAPMS engagement (#22).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "behavior-tree"
GEN_PATH = EX / "lower_to_bt.py"
COMMITTED = EX / "bt-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("lower_to_bt", GEN_PATH)
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
        "examples/behavior-tree/bt-report.txt is stale; "
        "run `python examples/behavior-tree/lower_to_bt.py` and commit."
    )


def test_valid_lowers_invalid_refused() -> None:
    gen = _load_gen()
    report = gen.render_report()
    assert report.count("[LOWERED]") == 1
    assert "<Sequence>" in report and '<Action ID="move_to" location="shelf"/>' in report
    assert "BTCPP_format" in report
    assert report.count("[REFUSED]") == 1
    assert "capability.missing_location" in report and "not lowered." in report
