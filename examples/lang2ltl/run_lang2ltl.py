#!/usr/bin/env python3
"""A capability gate below an LTL task spec, and why a declared capability is not trusted on faith.

From a conversation with Prof. Stefanie Tellex about Lang2LTL. A pipeline like
Lang2LTL turns a natural-language command into a formal (LTL) task specification:
what to achieve, and in what order. That spec dispatches concrete actions to a
robot. URML sits one step below the spec: it validates each dispatched action
against the robot's declared capability manifest and safety envelope before the
action runs. It does not author the task and it does not compete with the LTL
spec; it is the admissibility check under it.

Two honest limits, and how URML handles each:

1. Necessary, not sufficient. URML validates against a DECLARATION. A declaration
   can be optimistic, so an in-envelope action is not guaranteed to succeed in a
   new scene. What URML does buy cheaply is rejecting the definitely-inadmissible
   before a risky attempt: a grasp force above the gripper's rated range is
   refused statically, no robot required.

2. A declared capability is not an actual one. RFC-0631 lets a capability record
   HOW its claim was established (inferred / declared / derived / verified), and a
   deployment policy can require a minimum. Under a policy that requires verified
   gripper evidence, a self-declared force range is refused
   (policy.evidence_insufficient), so a bare claim does not pass on trust.

The task here: "go to the table, pick up the mug, place it on the counter." Read
as an LTL-shaped goal it is roughly

    F(at_table & F(holding_mug & F(at_counter & placed)))

and the actions it dispatches are the URML sequence below. This example validates
that sequence three ways. Hermetic and deterministic (validator only, no robot),
so the committed ``lang2ltl-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "mobile-manipulator.manifest.yaml"
POLICY = _HERE / "verified-evidence.policy.yaml"
_PROFILES = ("industrial",)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _task_program(force_n: float) -> dict[str, Any]:
    """The action sequence an LTL spec for the pick-and-place task dispatches."""
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"move_to": {"location": "table"}},
                {"detect": {"object": "mug", "store_as": "mug"}},
                {"grasp": {"target": "$mug", "force": {"newtons": force_n}}},
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
    policy = _load(POLICY)
    program = _task_program(60.0)

    lines = [
        "URML as the capability gate below an LTL task spec (with Prof. Tellex, Lang2LTL).",
        "An LTL spec says what to achieve; URML validates each action it dispatches",
        "against the robot's declared capabilities and safety envelope before dispatch.",
        "",
        'Task: "go to the table, pick up the mug, place it on the counter."',
        "Dispatched actions: move_to table -> detect mug -> grasp -> move_to counter -> release.",
        "Policy: gripper capability claims must be VERIFIED, not self-declared (RFC-0631).",
        "",
        "# 1. Admissible: force within the verified gripper envelope",
        "",
    ]

    ok = validate(program, manifest, profiles=_PROFILES, policy=policy)
    lines.append(f"[{_verdict(ok)}] grasp the mug at 60 N (gripper rated 20 to 100 N, evidence verified)")
    if ok.accepted:
        lines.append("   Every dispatched action is within the declaration, and the gripper's force")
        lines.append("   claim is verified, so the policy admits it. Necessary check passed.")
    else:
        lines.append("   -> " + ", ".join(_codes(ok)))
    lines.append("")

    # 2. The same task, but the grasp force is above the gripper's rated range.
    lines += ["# 2. Necessary-not-sufficient: an out-of-envelope action is refused before dispatch", ""]
    over = validate(_task_program(250.0), manifest, profiles=_PROFILES, policy=policy)
    lines.append(f"[{_verdict(over)}] grasp the mug at 250 N (above the 100 N rating)")
    lines.append("   -> " + ", ".join(_codes(over)))
    lines.append("   A 250 N grasp on a 100 N gripper will not work; URML rejects it statically,")
    lines.append("   with no robot and no attempt. This is the cheap, definite half of the check.")
    lines.append("")

    # 3. The same admissible task, but the gripper claim is only self-declared.
    lines += ["# 3. Declared is not actual: a self-declared capability is refused under the policy", ""]
    declared = copy.deepcopy(manifest)
    declared["manipulation"]["grippers"][0]["evidence"]["source"] = "declared"
    declared["manipulation"]["grippers"][0]["evidence"].pop("ref", None)
    under = validate(program, declared, profiles=_PROFILES, policy=policy)
    lines.append(f"[{_verdict(under)}] the same 60 N grasp, but the gripper's force range is only self-declared")
    lines.append("   -> " + ", ".join(_codes(under)))
    lines.append("   The action is within the declared range, yet the policy refuses it: the claim")
    lines.append("   is self-declared, not verified. URML does not take a capability on faith.")
    lines.append("")

    lines += [
        "# The point",
        "",
        "URML is the necessary-not-sufficient admissibility gate below the task spec, not",
        "a competing way to write the task. It cheaply rejects the definitely-inadmissible",
        "(case 2), and it can refuse to trust an unverified capability claim (case 3, via",
        "RFC-0631 evidence). It does not, and cannot, promise that an admissible action",
        "succeeds in a novel scene. That honesty is the point.",
    ]

    # Assert the three verdicts so a behavior drift fails CI.
    assert ok.accepted, "the verified, in-envelope task should be admissible"
    assert not over.accepted and "envelope.force_exceeded" in _codes(over), "250 N must be refused"
    assert not under.accepted and "policy.evidence_insufficient" in _codes(under), (
        "a self-declared gripper must be refused under the verified-evidence policy"
    )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "lang2ltl-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
