#!/usr/bin/env python3
"""A catch is a grasp whose target refuses to sit still, checked before dispatch.

RFC-0671. "Catch the ball" is one sentence of intent: a `grasp` with
`target_motion: ballistic`. The catching itself is a runtime skill. What URML
decides, on paper and before anything moves, is whether this hand on this robot
is allowed to attempt an interception at all: does the addressed gripper declare
an `interception` block, and does it cover the requested motion class?

That is the same shape as refusing a 250 N grasp on a 100 N gripper, applied to
motion instead of force. This example validates the same catch program against
three manifests, hermetically (validator only, no ROS, no robot):

  - a hand that declares ballistic interception  -> admissible
  - the same hand with no interception block      -> refused (not_supported)
  - a gripper that declares only tracked          -> refused (mode_not_declared)

Deterministic and byte-asserted: the committed ``dynamic-grasp-report.txt`` is
checked in CI.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "phantom-hand.manifest.yaml"
PROGRAM = _HERE / "catch-the-ball.urml.yaml"
_PROFILES = ("research",)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _validate(program: Any, manifest: Any) -> tuple[bool, list[str], dict[str, str]]:
    res = validate(program, manifest, profiles=_PROFILES, policy=None)
    codes = sorted({e.code_str for e in res.errors})
    msgs = {e.code_str: e.message for e in res.errors}
    return res.accepted, codes, msgs


def _without_interception(manifest: Any) -> Any:
    variant = copy.deepcopy(manifest)
    variant["manipulation"]["grippers"][0].pop("interception", None)
    return variant


def _tracked_only(manifest: Any) -> Any:
    variant = copy.deepcopy(manifest)
    variant["manipulation"]["grippers"][0]["interception"]["modes"] = ["tracked"]
    return variant


def render_report() -> str:
    manifest = _load(MANIFEST)
    program = _load(PROGRAM)

    lines = [
        "URML: a catch is a grasp whose target refuses to sit still, checked before dispatch.",
        "RFC-0671 adds an optional target_motion (static | tracked | ballistic) to `grasp`, and an",
        "`interception` block on a gripper declaring which motion classes it can catch. The validator",
        "admits an interception only on a hand that declared it. It never answers whether the catch",
        "will succeed, only whether the attempt is admissible on the declared hardware.",
        "",
        "Program: catch the ball -> grasp(target: $incoming_ball, target_motion: ballistic).",
        "",
        "# 1. A hand that declares ballistic interception",
        "",
    ]

    ok, ok_codes, _ = _validate(program, manifest)
    lines.append(f"[{'VALID' if ok else 'REJECTED'}] phantom_hand declares interception modes [tracked, ballistic]")
    if ok:
        lines.append("   Admissible: the addressed hand declares the ballistic mode. Dispatch may proceed;")
        lines.append("   the millisecond perception-prediction-closure loop is the runtime's job.")
    else:
        lines.append("   -> " + ", ".join(ok_codes))
    lines.append("")

    lines += ["# 2. The same hand with no interception block", ""]
    bad_ns, ns_codes, ns_msgs = _validate(program, _without_interception(manifest))
    lines.append(f"[{'VALID' if bad_ns else 'REJECTED'}] phantom_hand declares no interception")
    lines.append("   -> " + ", ".join(ns_codes))
    if "capability.target_motion_not_supported" in ns_msgs:
        lines.append("   " + ns_msgs["capability.target_motion_not_supported"])
    lines.append("   A hand that never declared it can intercept cannot be asked to catch.")
    lines.append("")

    lines += ["# 3. A gripper that declares only tracked interception", ""]
    bad_md, md_codes, md_msgs = _validate(program, _tracked_only(manifest))
    lines.append(f"[{'VALID' if bad_md else 'REJECTED'}] interception modes [tracked], ballistic requested")
    lines.append("   -> " + ", ".join(md_codes))
    if "capability.target_motion_mode_not_declared" in md_msgs:
        lines.append("   " + md_msgs["capability.target_motion_mode_not_declared"])
    lines.append("   A conveyor-tracking gripper is a real interceptor, but not for a thrown ball.")
    lines.append("")

    lines += [
        "# What the declaration buys",
        "",
        "Without target_motion and interception, \"catch the ball\" either validated on a parallel-jaw",
        "gripper that has no hope of executing it, or was refused everywhere, depending on how a bridge",
        "phrased it. Now the language distinguishes hardware that declares the capability from hardware",
        "that does not. No new primitive: a catch is a grasp. URML declares and statically checks the",
        "attempt; the runtime (an RFC-0383 learned policy) does the catch. The declaration is trusted,",
        "not verified, and the numbers make it falsifiable by inspection.",
    ]

    # Assert the claims so a behavior drift fails CI.
    assert ok, "a ballistic catch on a hand declaring ballistic should validate"
    assert not bad_ns and "capability.target_motion_not_supported" in ns_codes, "no interception should be refused"
    assert not bad_md and "capability.target_motion_mode_not_declared" in md_codes, "tracked-only should refuse ballistic"

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "dynamic-grasp-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
