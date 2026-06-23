#!/usr/bin/env python3
"""URML pick-and-place on a Dobot Magician, validated before the arm moves.

The worked example from the magician_ros2 engagement
(jkaniuka/magician_ros2#11): an English front door for the Dobot Magician.

A spoken request like "pick up the block and put it on the dropoff spot"
becomes a typed URML program. The validator checks it against the Dobot's
declared manifest (its locations, its gripper, what it can see) before anything
moves. This script validates the happy path, then shows the validator refusing
three programs the Magician cannot do: an object it cannot recognize, a location
it does not know, and a grasp force past the gripper's range.

Hermetic (the validator only, no arm) and deterministic, so the committed
``pick-place-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "dobot-magician.manifest.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _program(steps: list[dict[str, Any]]) -> dict[str, Any]:
    return {"profile": "industrial", "behavior": {"type": "sequence", "on_error": "abort_and_report", "steps": steps}}


_PICK_PLACE = [
    {"pick_from": {"source": "pickup", "object": "block", "force": "firm", "store_as": "held"}},
    {"place_at": {"target": "dropoff", "held": "$held", "mode": "place"}},
    {"move_to": {"location": "home"}},
]


def _emit(lines: list[str], label: str, steps: list[dict[str, Any]]) -> None:
    manifest = _load(MANIFEST)
    result = validate(_program(steps), manifest, profiles=("industrial",), policy=None)
    verdict = "VALID" if result.accepted else "REJECTED"
    lines.append(f"[{verdict}] {label}")
    if not result.accepted:
        codes = ", ".join(sorted({e.code_str for e in result.errors}))
        lines.append(f"   -> {codes}")
    lines.append("")


def render_report() -> str:
    manifest = _load(MANIFEST)
    lines = [
        "URML pick-and-place on a Dobot Magician (magician_ros2).",
        "The validator checks every program against the arm's manifest before it moves.",
        f"robot: {manifest['robot_id']}   substrate: magician_ros2 (ROS 2 driver)",
        "",
    ]

    _emit(lines, "pick the block from pickup, place it at dropoff, return home", _PICK_PLACE)

    # 1. An object the Dobot cannot recognize (not in its vocabulary).
    _emit(
        lines,
        "pick a 'mug', which is not in the arm's object vocabulary",
        [{"pick_from": {"source": "pickup", "object": "mug", "force": "firm", "store_as": "held"}},
         {"place_at": {"target": "dropoff", "held": "$held", "mode": "place"}}],
    )

    # 2. A location the Dobot does not know.
    _emit(
        lines,
        "move to 'shelf', an undeclared location",
        [{"move_to": {"location": "shelf"}}],
    )

    # 3. A grasp force past the gripper's declared range (max 8 N).
    _emit(
        lines,
        "pick with 50 N of force, past the gripper's 8 N maximum",
        [{"pick_from": {"source": "pickup", "object": "block", "force": 50.0, "store_as": "held"}},
         {"place_at": {"target": "dropoff", "held": "$held", "mode": "place"}}],
    )

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "pick-place-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
