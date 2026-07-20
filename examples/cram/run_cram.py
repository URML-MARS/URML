#!/usr/bin/env python3
"""A validate-before-actuate gate below CRAM's action decomposition.

From a conversation with the CRAM group (U. Bremen, Institute for Artificial
Intelligence) about where a declared-capability check sits relative to a cognitive
architecture. CRAM takes an underspecified request and decomposes it into a plan
of grounded sub-actions, resolving the open parameters at runtime from its
knowledge base (KnowRob). URML sits one step below that decomposition: it validates
each grounded sub-action against the robot's declared capability manifest and safety
envelope before the sub-action is dispatched. It does not plan, and it does not
compete with the decomposition; it is the admissibility check under it.

The request here is a CRAM "transporting" designator, roughly

    (an action (type transporting) (object (an object (type mug)))
              (target (a location (on counter))))

which CRAM decomposes into the grounded sub-action sequence below:

    move_to table -> detect mug -> grasp mug -> move_to counter -> place.

This example validates that decomposition three ways. Hermetic and deterministic
(validator only, no robot), so the committed ``cram-report.txt`` is byte-asserted
in CI.

Two things the gate catches before CRAM dispatches a single sub-action:

1. An out-of-envelope grounded parameter. CRAM may ground a firm grasp whose force
   is above the gripper's rated range. URML rejects it statically
   (envelope.force_exceeded), no robot and no attempt required.

2. A grounded object the robot cannot perceive. CRAM's knowledge base may resolve a
   request to an object class the robot's perception vocabulary does not declare.
   URML rejects the grounded detect (capability.missing_object_class) before the
   plan runs, rather than discovering it mid-execution.

URML is necessary, not sufficient: it validates a declaration, so an in-envelope
sub-action is not guaranteed to succeed in a novel scene. What it buys cheaply is
rejecting the definitely-inadmissible before the robot commits to a plan.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "mobile-manipulator.manifest.yaml"
_PROFILES = ("industrial",)
# This example is about the capability and safety-envelope gate, not federal
# compliance, so it runs policy-free (policy=None skips Pass 5). Compliance is a
# separate, orthogonal concern that stays one flag away.


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _transport_program(obj: str, force_n: float) -> dict[str, Any]:
    """The grounded sub-action sequence CRAM's `transporting` designator expands to."""
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"move_to": {"location": "table"}},
                {"detect": {"object": obj, "store_as": "item"}},
                {"grasp": {"target": "$item", "force": {"newtons": force_n}}},
                {"move_to": {"location": "counter"}},
                {"release": {"mode": "place", "at": "counter"}},
            ],
        },
    }


def _verdict(result: Any) -> str:
    return "VALID" if result.accepted else "REJECTED"


def _codes(result: Any) -> list[str]:
    return sorted({e.code_str for e in result.errors})


def render_report() -> str:
    manifest = _load(MANIFEST)

    lines = [
        "URML as the validate-before-actuate gate below CRAM's decomposition (U. Bremen IAI).",
        "CRAM decomposes an underspecified request into grounded sub-actions and resolves",
        "the open parameters from its knowledge base. URML validates each grounded",
        "sub-action against the robot's declared capabilities and safety envelope before",
        "the sub-action is dispatched.",
        "",
        'Request: transporting(object: mug, target: on counter).',
        "Grounded plan: move_to table -> detect mug -> grasp mug -> move_to counter -> place.",
        "",
        "# 1. Admissible: every grounded sub-action is within the declaration",
        "",
    ]

    ok = validate(_transport_program("mug", 60.0), manifest, profiles=_PROFILES, policy=None)
    lines.append(f"[{_verdict(ok)}] transport the mug, grasp at 60 N (gripper rated 20 to 100 N)")
    if ok.accepted:
        lines.append("   Each grounded sub-action resolves against the manifest: the object is in the")
        lines.append("   perception vocabulary and the grasp force is within the gripper's range.")
        lines.append("   URML admits the plan. Necessary check passed.")
    else:
        lines.append("   -> " + ", ".join(_codes(ok)))
    lines.append("")

    # 2. CRAM grounds a firm grasp whose force is above the gripper's rated range.
    lines += ["# 2. Out-of-envelope parameter: a grounded grasp above the gripper rating is refused", ""]
    over = validate(_transport_program("mug", 250.0), manifest, profiles=_PROFILES, policy=None)
    lines.append(f"[{_verdict(over)}] the same transport, but the grasp is grounded at 250 N (above the 100 N rating)")
    lines.append("   -> " + ", ".join(_codes(over)))
    lines.append("   A 250 N grasp on a 100 N gripper will not work; URML rejects the grounded")
    lines.append("   sub-action statically, before CRAM dispatches the plan. No robot, no attempt.")
    lines.append("")

    # 3. CRAM's KB grounds the request to an object the robot cannot perceive.
    lines += ["# 3. Ungrounded perception: a grounded object outside the robot's vocabulary is refused", ""]
    unknown = validate(_transport_program("tray", 60.0), manifest, profiles=_PROFILES, policy=None)
    lines.append(f"[{_verdict(unknown)}] transport a tray (the vocabulary declares only: mug)")
    lines.append("   -> " + ", ".join(_codes(unknown)))
    lines.append("   CRAM's knowledge base can ground a request to an object the robot's perception")
    lines.append("   does not declare. URML rejects the grounded detect before the plan runs, rather")
    lines.append("   than discovering the gap mid-execution.")
    lines.append("")

    lines += [
        "# The point",
        "",
        "URML is the necessary-not-sufficient admissibility gate below CRAM's decomposition,",
        "not a competing planner. It cheaply rejects the definitely-inadmissible grounded",
        "sub-action (case 2, an out-of-envelope force; case 3, an object outside the declared",
        "vocabulary) before the robot commits to the plan. It does not, and cannot, promise",
        "that an admissible sub-action succeeds in a novel scene. That honesty is the point.",
    ]

    # Assert the three verdicts so a behavior drift fails CI.
    assert ok.accepted, "the in-envelope, in-vocabulary transport should be admissible"
    assert not over.accepted and "envelope.force_exceeded" in _codes(over), "250 N must be refused"
    assert not unknown.accepted and "capability.missing_object_class" in _codes(unknown), (
        "an object outside the perception vocabulary must be refused"
    )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "cram-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
