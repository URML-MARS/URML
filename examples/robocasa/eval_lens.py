#!/usr/bin/env python3
"""URML as an eval lens over RoboCasa instructions.

The use sepnasiriany pointed at on robocasa/robocasa#200: a sim benchmark learns
policies end to end and has no actuation gate to refuse a request, but an
explicit capability + safety envelope is a useful eval lens for flagging
out-of-distribution or out-of-capability instructions.

That is exactly what URML's validator does, with no new machinery. Each benchmark
instruction is lowered to URML intent and validated against the RoboCasa manifest
(robocasa-kitchen.manifest.yaml, built from the spec the maintainer gave: a Franka
Panda on an Omron base, parallel-jaw gripper, kitchen reachability, the graspable
object vocabulary). An in-capability instruction passes; one that names an object
or place outside the scene, or exceeds a declared capability, is flagged before
any policy runs.

Nothing is actuated. The lens is static and offline. It is deterministic, so the
committed ``eval-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "robocasa-kitchen.manifest.yaml"

# Which capability error means which of the maintainer's two categories.
_OOD_CODES = {"capability.missing_object_class", "capability.missing_location"}
_OOC_CODES = {
    "capability.missing_gripper",
    "capability.drive_type_not_aerial",
    "capability.missing_service_ceiling",
}


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _program(steps: list[dict[str, Any]]) -> dict[str, Any]:
    return {"profile": "home", "behavior": {"type": "sequence", "steps": steps}}


# (instruction, expectation, steps). The expectation labels what the lens should
# do; the verdict below is computed, not assumed.
_CASES: list[tuple[str, str, list[dict[str, Any]]]] = [
    (
        "Pick up the mug from the counter and put it in the sink",
        "in-capability",
        [
            {"pick_from": {"source": "counter", "object": "mug", "store_as": "m"}},
            {"place_at": {"target": "sink", "held": "$m", "mode": "place"}},
        ],
    ),
    ("Drive to the stove", "in-capability", [{"move_to": {"location": "stove"}}]),
    (
        "Pick up the bowl from the cabinet",
        "in-capability",
        [{"pick_from": {"source": "cabinet", "object": "bowl", "store_as": "b"}}],
    ),
    (
        "Grasp the anvil on the counter",
        "out-of-distribution",
        [{"pick_from": {"source": "counter", "object": "anvil", "store_as": "a"}}],
    ),
    (
        "Go to the rooftop",
        "out-of-distribution",
        [{"move_to": {"location": "rooftop"}}],
    ),
    (
        "Pick up the mug, squeezing it with 200 N",
        "out-of-capability",
        [{"pick_from": {"source": "counter", "object": "mug", "force": {"newtons": 200}, "store_as": "m"}}],
    ),
    (
        "Fly up to the top shelf",
        "out-of-capability",
        [{"take_off": {"altitude": 2.0}}],
    ),
]


def _category(codes: list[str]) -> str:
    """Label a rejection by the maintainer's two buckets."""
    if any(c in _OOD_CODES for c in codes):
        return "out-of-distribution"
    if any(c in _OOC_CODES for c in codes):
        return "out-of-capability"
    return "rejected"


def render_report() -> str:
    manifest = _load(MANIFEST)
    gripper = manifest["manipulation"]["grippers"][0]
    vocab = manifest["perception"]["object_vocabulary"]
    places = [loc["name"] for loc in manifest["declared_locations"]]

    lines: list[str] = [
        "URML as an eval lens over RoboCasa instructions.",
        "No actuation: a static, offline capability + safety envelope, checked",
        "BEFORE a policy runs, to flag out-of-distribution / out-of-capability asks.",
        f"robot: {manifest['robot_id']} (Franka Panda on an Omron base)",
        f"gripper force <= {gripper['force_max_n']:.0f} N   reach <= "
        f"{manifest['manipulation']['reachable_workspace_m']:.2f} m   "
        f"payload <= {manifest['mobility']['max_payload']:.0f} kg",
        f"scene objects ({len(vocab)}): {', '.join(vocab)}",
        f"scene places ({len(places)}): {', '.join(places)}",
        "",
        "# Each instruction is lowered to URML intent and validated against the manifest",
        "",
    ]

    width = max(len(instr) for instr, _, _ in _CASES)
    accepted = 0
    flagged_ood = 0
    flagged_ooc = 0
    detail_lines: list[str] = []
    for instr, _expect, steps in _CASES:
        result = validate(_program(steps), manifest, profiles=["home"], policy=None)
        if result.accepted:
            accepted += 1
            lines.append(f"  [PASS]  {instr.ljust(width)}")
        else:
            codes = [e.code_str for e in result.errors]
            cat = _category(codes)
            if cat == "out-of-distribution":
                flagged_ood += 1
            elif cat == "out-of-capability":
                flagged_ooc += 1
            lines.append(f"  [FLAG]  {instr.ljust(width)}  [{cat}]")
            # the precise validator reason, for the per-instruction detail block
            detail_lines.append(f"  {instr}")
            detail_lines.append(f"      -> {cat}: {codes[0]}")
            detail_lines.append(f"         {result.errors[0].message}")

    lines.append("")
    lines.append(
        f"{accepted} in-capability and passed; "
        f"{flagged_ood + flagged_ooc} flagged "
        f"({flagged_ood} out-of-distribution, {flagged_ooc} out-of-capability)."
    )
    lines.append("")
    lines.append("# Why each flagged instruction was caught")
    lines.append("")
    lines += detail_lines
    lines.append("")
    lines.append(
        "The lens never executes anything; it only tells the benchmark which"
    )
    lines.append(
        "instructions are inside the robot's declared capability before the policy sees them."
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    report = render_report()
    (_HERE / "eval-report.txt").write_text(report, encoding="utf-8")
    print(report, end="")
