#!/usr/bin/env python3
"""URML in the mind of an autonomous robot (Discussion #526).

@slowrunner described a patrol: during activity hours, if the battery is over
50%, wander the allowed area, stop when an unclassified quadrilateral or circular
shape is seen, photograph it from several angles, and store the photos tagged
with time and pose.

The question that thread raised is where URML sits in that. The answer is the
boundary this example draws concretely:

  - The MASTERMIND (autonomy: a planner, a behavior tree, a policy, your own
    Python) owns the decisions. When to patrol (hours + battery), where to
    wander, whether a shape is novel and unclassified, and storing the tagged
    photos are all autonomy. URML expresses none of them.

  - Each concrete PHYSICAL ACTION the mastermind decides on becomes a URML step,
    validated against the robot's manifest before it runs: drive, turn, capture.

This script plays a `Mastermind` (plain Python, no URML) through one patrol, and
shows every physical action it issues being validated as a URML step. Then it
shows the boundary the other way: when the mastermind tries to push its
perception judgment *down* into URML as a `detect`, the validator refuses it,
because novelty detection is not a declared capability. It is deterministic, so
the committed ``autonomy-boundary-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate
from urml_ros2_runtime.runtime import URMLRuntime
from urml_ros2_runtime.substrate.mock import MockROSAdapter

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "patrol.manifest.yaml"
_PROFILES = ("educational",)


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class Mastermind:
    """The autonomy layer. Plain Python. URML expresses none of this.

    It owns the guards, the wander policy, the open-set perception ("is this an
    unclassified shape?"), and the tagged storage. It emits URML steps for the
    physical actions it decides to take, and nothing else.
    """

    def __init__(self) -> None:
        self.activity_hours = True
        self.battery_pct = 72
        self.classified = {"charging_dock", "table_leg", "doorway"}

    # --- decisions that stay in autonomy (NOT URML) ---

    def may_patrol(self) -> bool:
        return self.activity_hours and self.battery_pct > 50

    def wander_legs(self) -> list[tuple[float, float]]:
        """Where to go next. Autonomy's policy; URML never sees the reasoning."""
        return [(30.0, 0.5), (-20.0, 0.5)]

    def is_unclassified_shape(self, view: str) -> bool:
        """Open-set novelty detection. Autonomy. Not a URML capability."""
        return view not in self.classified

    def photo_angles(self) -> list[tuple[float, float]]:
        """How to reposition for each angle. Autonomy decides; URML moves."""
        return [(0.0, 0.0), (45.0, 0.3), (45.0, 0.3)]

    def store_tagged(self, handle: str, pose: str) -> None:
        """Write the photo to a tagged folder. Autonomy filesystem IO. Not URML."""
        # (no-op in the example)


def _step_label(step: dict[str, Any]) -> str:
    verb, args = next(iter(step.items()))
    if verb == "turn":
        return f"turn {args['angle']:+.0f} deg"
    if verb == "drive":
        return f"drive {args['distance']:.2f} m"
    if verb == "capture":
        return "capture photo (current view)"
    if verb == "measure":
        return f"measure {args['what']}"
    return verb


def _validate_step(manifest: dict[str, Any], step: dict[str, Any]) -> bool:
    prog = {"profile": list(_PROFILES), "behavior": {"type": "sequence", "steps": [step]}}
    return validate(prog, manifest, profiles=_PROFILES, policy=None).accepted


def render_report() -> str:
    manifest = _load(MANIFEST)
    mind = Mastermind()

    lines = [
        "URML in the mind of an autonomous robot (Discussion #526).",
        "The mastermind (autonomy) decides; URML validates and executes each physical action.",
        f"robot: {manifest['robot_id']}",
        "",
        "# Decisions that stay in the mastermind (autonomy, NOT URML)",
        "",
        f"  activity hours + battery > 50%   -> may_patrol() = {mind.may_patrol()}",
        "  where to wander next              -> autonomy policy",
        "  'is this an unclassified shape?'  -> autonomy (open-set perception)",
        "  store photos tagged to a folder   -> autonomy (filesystem IO)",
        "",
        "# Each physical action the mastermind issues becomes a validated URML step",
        "",
    ]

    # The mastermind plays out one patrol, emitting URML steps for physical actions.
    steps: list[dict[str, Any]] = []
    for angle, dist in mind.wander_legs():
        steps.append({"turn": {"angle": angle}})
        steps.append({"drive": {"distance": dist}})

    # The mastermind's camera sees something; it judges (in autonomy) that the
    # shape is not one it has classified. That judgment is NOT a URML step.
    saw_novel = mind.is_unclassified_shape("unknown_blob")
    lines.append(f"  [autonomy] saw a shape, is_unclassified_shape() = {saw_novel}: stop and photograph it")
    lines.append("")

    # Photograph from several angles: reposition (URML), then snap (URML).
    for i, (angle, dist) in enumerate(mind.photo_angles(), start=1):
        if angle:
            steps.append({"turn": {"angle": angle}})
        if dist:
            steps.append({"drive": {"distance": dist}})
        steps.append({"capture": {"media": "photo", "store_as": f"shot_{i}"}})
    steps.append({"measure": {"what": "distance", "sensor": "distance", "store_as": "clearance"}})

    for step in steps:
        ok = _validate_step(manifest, step)
        lines.append(f"  [{'VALID' if ok else 'REJECTED'}]  {_step_label(step)}")
    lines.append("")

    # Execute the whole validated patrol through the mock substrate, to show the
    # steps actually dispatch (no robot).
    program = {"profile": list(_PROFILES), "behavior": {"type": "sequence", "on_error": "abort_and_report", "steps": steps}}
    result = validate(program, manifest, profiles=_PROFILES, policy=None)
    run = URMLRuntime(MockROSAdapter()).execute(program, manifest, profiles=_PROFILES)
    lines.append(f"# Executed through the mock substrate: {run.steps_executed} steps, success={run.success}")
    lines.append("")

    # The boundary the other way: the mastermind cannot push its perception
    # judgment down into URML. Expressed as a `detect`, the validator refuses it.
    lines += [
        "# The boundary, shown by what URML REFUSES",
        "",
        "  the mastermind's perception judgment is not a URML step. Expressed as one:",
    ]
    detect_step = {"detect": {"object": "unclassified_shape", "store_as": "novel"}}
    detect_prog = {"profile": list(_PROFILES), "behavior": {"type": "sequence", "steps": [detect_step]}}
    dres = validate(detect_prog, manifest, profiles=_PROFILES, policy=None)
    code = next((e.code_str for e in dres.errors), "")
    lines.append(f"    detect(object: unclassified_shape)  ->  [REJECTED] {code}")
    lines.append("    novelty detection is not a declared capability; it stays in autonomy.")
    lines.append("")
    lines.append(
        f"Summary: {len(steps)} physical actions validated and executed; "
        "1 non-URML decision correctly refused."
    )
    lines.append(
        "The mastermind is free to be as clever as it likes; the robot still only does"
    )
    lines.append("what the manifest declares and the envelope allows.")
    assert result.accepted and run.success and not dres.accepted
    return "\n".join(lines) + "\n"


def main() -> None:
    out = _HERE / "autonomy-boundary-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
