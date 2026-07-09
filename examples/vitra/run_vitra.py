#!/usr/bin/env python3
"""The same policy-emitted action, admissible on one robot and refused on another.

For microsoft/VITRA#41. VITRA is a vision-language-action model pretrained on
human-activity video; like any VLA it emits a manipulation action for a target
robot. What a human demonstrated, or a policy produced, is not automatically
admissible on the specific robot that will execute it: the arm may not be rated
for the commanded grip force, the object may be out of reach, the workspace may
be smaller.

URML is the static, substrate-neutral admissibility check for exactly that. It
declares each robot's capabilities and safety envelope in a manifest, and
validates a commanded action against them before dispatch, with no planner, no
controller, and no ROS in the loop. This example makes the point concretely: one
grasp action, validated against two robot manifests that differ only in the
gripper's declared force range, is admissible on the higher-force arm (Robot A)
and refused on the gentler one (Robot B).

The refusal is not a runtime failure. It is a static verdict the same policy
output earns differently per robot, which is the portability MoveIt or a
Pinocchio-based controller cannot give: those are ROS-bound and tied to one
robot model, and they run at execution time. URML runs before, off to the side,
and against a declaration.

Hermetic and deterministic (validator only, no robot, no ROS), so the committed
``vitra-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST_A = _HERE / "robot-a.manifest.yaml"
MANIFEST_B = _HERE / "robot-b.manifest.yaml"
_PROFILES = ("industrial",)

# The grip force the policy emits: inside Robot A's 50 to 250 N range, outside
# Robot B's 10 to 100 N range.
_GRASP_FORCE_N = 150.0


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _grasp_program(force_n: float) -> dict[str, Any]:
    """A VLA-shaped manipulation: detect a workpiece, grasp it, place it.

    This is the action a policy such as VITRA emits for the target robot. The
    force is the one number that decides admissibility here.
    """
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"detect": {"object": "workpiece", "store_as": "part"}},
                {"grasp": {"target": "$part", "force": {"newtons": force_n}}},
                {"release": {"mode": "place", "at": "assembly_fixture"}},
            ],
        },
    }


def render_report() -> str:
    manifest_a = _load(MANIFEST_A)
    manifest_b = _load(MANIFEST_B)
    program = _grasp_program(_GRASP_FORCE_N)

    lines = [
        "URML: one policy-emitted action, checked against two robots (microsoft/VITRA#41).",
        "A VLA such as VITRA emits a manipulation action; URML validates it against each",
        "target robot's declared envelope before dispatch, with no planner and no ROS.",
        "",
        f"The action: grasp a workpiece at {_GRASP_FORCE_N} N, then place it.",
        "Robot A: gripper rated 50 to 250 N.   Robot B: gripper rated 10 to 100 N.",
        "The two manifests differ only in that force range.",
        "",
        "# 1. The action on Robot A (grip force within the declared range)",
        "",
    ]

    result_a = validate(program, manifest_a, profiles=_PROFILES, policy=None)
    verdict_a = "VALID" if result_a.accepted else "REJECTED"
    lines.append(f"[{verdict_a}] grasp workpiece at {_GRASP_FORCE_N} N on Robot A (50 to 250 N gripper)")
    if result_a.accepted:
        lines.append(f"   {_GRASP_FORCE_N} N is within the declared 50 to 250 N envelope; the action is admissible.")
    else:
        lines.append("   -> " + ", ".join(sorted({e.code_str for e in result_a.errors})))
    lines.append("")

    lines += ["# 2. The same action on Robot B (grip force above the declared range)", ""]

    result_b = validate(program, manifest_b, profiles=_PROFILES, policy=None)
    verdict_b = "VALID" if result_b.accepted else "REJECTED"
    codes_b = sorted({e.code_str for e in result_b.errors})
    lines.append(f"[{verdict_b}] grasp workpiece at {_GRASP_FORCE_N} N on Robot B (10 to 100 N gripper)")
    lines.append("   -> " + ", ".join(codes_b))
    msgs_b = {e.code_str: e.message for e in result_b.errors}
    if "capability.missing_gripper" in msgs_b:
        lines.append(f"   capability.missing_gripper: {msgs_b['capability.missing_gripper']}")
    if "envelope.force_exceeded" in msgs_b:
        lines.append(f"   envelope.force_exceeded:    {msgs_b['envelope.force_exceeded']}")
    lines.append("")

    lines += [
        "# The point",
        "",
        "The same policy output is admissible on one robot and refused on another,",
        "decided statically from each robot's declaration, before anything is sent to",
        "a controller or a motion planner. URML does not plan the motion, check",
        "collisions against a live scene, or run on the robot; it is the portable,",
        "declarative admissibility gate above whatever executes the action. For a VLA",
        "that may deploy across several robots, that check is one manifest per robot,",
        "not a per-framework re-implementation.",
    ]

    # Assert the claims the report makes, so a drift in behavior fails CI.
    assert result_a.accepted, "the 150 N grasp should be admissible on Robot A"
    assert not result_b.accepted, "the 150 N grasp should be refused on Robot B"
    assert "capability.missing_gripper" in codes_b, "Robot B refusal should include capability.missing_gripper"
    assert "envelope.force_exceeded" in codes_b, "Robot B refusal should include envelope.force_exceeded"

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "vitra-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
