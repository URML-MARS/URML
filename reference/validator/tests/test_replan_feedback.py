"""The ROSPlan replan-feedback example must be deterministic and true.

Mirrors the VLA / fieldbus / esmini export guards: the generator is
deterministic, the committed ``replan-report.txt`` matches it, and the
dispatch-validate-replan loop decides correctly (plan v1 halts at the
occupancy-zone action with structured feedback; plan v2, the re-plan, dispatches
in full). The worked example for the ROSPlan engagement (KCL-Planning/ROSPlan
#330), where the maintainer asked what happens on validation failure and noted
that feeding it back to the planner is what avoids the same plan.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EX = REPO_ROOT / "examples" / "planning"
GEN_PATH = EX / "validate_and_replan.py"
COMMITTED = EX / "replan-report.txt"


def _load_gen():
    spec = importlib.util.spec_from_file_location("validate_and_replan", GEN_PATH)
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
        "examples/planning/replan-report.txt is stale; "
        "run `python examples/planning/validate_and_replan.py` and commit."
    )


def test_v1_halts_with_feedback_v2_dispatches() -> None:
    gen = _load_gen()
    report = gen.render_report()
    # Plan v1 halts at the occupancy-zone action; one action is not reached.
    assert "[HALT]     (goto shelf crowd_spot)" in report
    assert "envelope.occupancy_zone_intrusion" in report
    assert "1 action(s) not reached." in report
    # Structured replan-feedback is returned to the planner.
    assert "rejected_action: (goto shelf crowd_spot)" in report
    assert "directive:" in report
    # Plan v2 (the re-plan) dispatches in full, with no further halt.
    assert "-> all actions admissible; full plan dispatched." in report
    assert report.count("[HALT]") == 1  # only plan v1 halts


def test_dispatch_loop_helper_returns_feedback() -> None:
    """The dispatch helper yields structured feedback on rejection, None on success."""
    gen = _load_gen()
    manifest = gen._load(gen.MANIFEST)
    envelope = gen._load(gen.ENVELOPE)
    _, fb_v1 = gen.dispatch_plan(gen._load(gen.PLAN_V1), manifest, envelope)
    assert fb_v1 is not None
    assert fb_v1["rejected_action"] == "(goto shelf crowd_spot)"
    assert fb_v1["codes"] == ["envelope.occupancy_zone_intrusion"]
    _, fb_v2 = gen.dispatch_plan(gen._load(gen.PLAN_V2), manifest, envelope)
    assert fb_v2 is None  # the re-plan is fully admissible
