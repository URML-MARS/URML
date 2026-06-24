"""The RoboCasa eval-lens worked example must be deterministic and true.

Mirrors the OPC UA / Isaac / evidence example guards: the generator is
deterministic, the committed ``eval-report.txt`` matches it, and the report
demonstrates the use sepnasiriany pointed at on robocasa/robocasa#200 (a
capability + safety envelope as an eval lens that flags out-of-distribution and
out-of-capability instructions). Validator-only, hermetic.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "robocasa"
GEN_PATH = EX / "eval_lens.py"
COMMITTED = EX / "eval-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("eval_lens", GEN_PATH)
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
        "examples/robocasa/eval-report.txt is stale; "
        "run `python examples/robocasa/eval_lens.py` and commit."
    )


def test_lens_passes_in_capability_and_flags_the_rest() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # In-capability instructions pass.
    assert "[PASS]  Pick up the mug from the counter and put it in the sink" in report
    # Both of the maintainer's categories are exercised and labelled.
    assert "[FLAG]  Grasp the anvil on the counter" in report
    assert "[out-of-distribution]" in report
    assert "[out-of-capability]" in report
    assert "3 in-capability and passed; 4 flagged (2 out-of-distribution, 2 out-of-capability)." in report
    # The flags carry the precise validator reason.
    assert "capability.missing_object_class" in report
    assert "capability.drive_type_not_aerial" in report
