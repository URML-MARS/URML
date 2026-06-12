#!/usr/bin/env python3
"""URML as the validating dispatcher for a PDDL planner (ROSPlan), with replan feedback.

The worked example from the ROSPlan engagement (KCL-Planning/ROSPlan#330), where
@gerardcanal asked the right questions: how does URML's capability layer relate to
a PDDL domain, is URML a dispatcher that checks an action is still valid, and what
happens when validation fails -- because feeding it back to the planner is what
stops it from returning the same plan.

The answer this example demonstrates:

- A PDDL domain encodes what the robot can do *symbolically*, for plan search.
  URML's capability manifest plus the safety envelope is a *different* layer: the
  physical robot's declared limits and the deployment-time safety contract. A
  symbolically valid plan can still be inadmissible on the real robot.

- URML is the validating dispatcher. It checks each grounded action against the
  manifest and envelope before dispatch (a precondition check at the physical,
  not just symbolic, level), and halts on the first inadmissible action.

- On failure it returns *structured* feedback: the rejected action, the failing
  validation pass, the error codes, and a directive the planner can apply
  (forbid this action and replan). Without that, as @gerardcanal noted, the
  planner would just hand back the same plan.

The script dispatches plan v1 (a symbolically valid PDDL plan whose route passes
through a people-occupancy zone the domain never modeled), shows URML halting
with replan feedback, then dispatches plan v2 (the re-plan with the feedback
applied) cleanly. It is hermetic (the validator only, no planner, no robot) and
deterministic, so the committed ``replan-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "delivery.manifest.yaml"
ENVELOPE = _HERE / "safety-envelope.yaml"
PLAN_V1 = _HERE / "plan-v1.yaml"
PLAN_V2 = _HERE / "plan-v2.yaml"

# Which validation pass a code namespace belongs to (the dispatcher reports it so
# the planner knows whether the action was symbolically- or physically-rejected).
_PASS = {
    "argument": "Pass 1 (argument typing)",
    "capability": "Pass 2 (capability)",
    "envelope": "Pass 3 (safety envelope)",
    "binding": "Pass 4 (variable bindings)",
    "policy": "Pass 5 (compliance policy)",
}


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _failing_pass(codes: list[str]) -> str:
    for c in codes:
        ns = c.split(".", 1)[0]
        if ns in _PASS:
            return _PASS[ns]
    return "validation"


def dispatch_plan(
    plan: dict[str, Any], manifest: dict[str, Any], envelope: dict[str, Any]
) -> tuple[list[str], dict[str, Any] | None]:
    """Validate-and-dispatch each action in order; halt on the first rejection.

    Returns the per-action report lines and, if an action was rejected, the
    structured replan-feedback the planner consumes.
    """
    lines: list[str] = []
    actions = plan["actions"]
    feedback: dict[str, Any] | None = None
    for i, step in enumerate(actions):
        result = validate(step["program"], manifest, envelope, policy=None)
        if result.accepted:
            lines.append(f"[DISPATCH] {step['action']}")
            continue
        codes = [e.code_str for e in result.errors]
        lines.append(f"[HALT]     {step['action']}")
        lines.append(f"   rejected at {_failing_pass(codes)} [{', '.join(codes)}]")
        lines.append(f"   {result.errors[0].message}")
        not_reached = len(actions) - (i + 1)
        lines.append(f"   -> dispatch halted; {not_reached} action(s) not reached.")
        feedback = {
            "rejected_action": step["action"],
            "failing_pass": _failing_pass(codes),
            "codes": codes,
            "directive": (
                f"forbid {step['action']} and replan; without this constraint the "
                "planner returns the same plan."
            ),
        }
        break
    return lines, feedback


def render_report() -> str:
    manifest = _load(MANIFEST)
    envelope = _load(ENVELOPE)
    plan_v1 = _load(PLAN_V1)
    plan_v2 = _load(PLAN_V2)

    lines = [
        "URML as the validating dispatcher for a PDDL planner: each grounded action",
        "is validated against the manifest + envelope before dispatch; an inadmissible",
        "action halts dispatch and returns structured feedback the planner replans on.",
        f"robot: {manifest['robot_id']}  |  envelope: {envelope['deployment_id']}",
        "",
        f"# Plan v1 (planner output) - goal: {plan_v1['goal']}",
        "",
    ]
    v1_lines, feedback = dispatch_plan(plan_v1, manifest, envelope)
    lines += v1_lines
    lines.append("")

    assert feedback is not None, "plan v1 is expected to be rejected by the envelope"
    lines += [
        "# Replan-feedback (returned to the planner)",
        "",
        f"rejected_action: {feedback['rejected_action']}",
        f"failing_pass:    {feedback['failing_pass']}",
        f"codes:           {', '.join(feedback['codes'])}",
        f"directive:       {feedback['directive']}",
        "",
        f"# Plan v2 (planner re-plan, feedback applied) - goal: {plan_v2['goal']}",
        "",
    ]
    v2_lines, v2_feedback = dispatch_plan(plan_v2, manifest, envelope)
    lines += v2_lines
    if v2_feedback is None:
        lines.append("-> all actions admissible; full plan dispatched.")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "replan-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
