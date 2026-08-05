#!/usr/bin/env python3
"""URML as a per-subtask eval lens over RoboCasa composite tasks.

The follow-up sepnasiriany pointed at on robocasa/robocasa#200: RoboCasa's target
composite-task datasets now annotate every frame with a subtask index, an
atomic-skill name, a stage (pick / place / navigate), and a natural-language
instruction. Collapsed to segments, a composite task is an ordered list of
annotated subtasks.

That upgrades the eval lens (``eval_lens.py``) from whole-instruction to
per-subtask. Instead of passing or flagging "set the table" as one blob, the lens
walks the annotated subtasks and reports WHICH one is out-of-distribution or
out-of-capability. The composite is lowered to one URML sequence, one primitive
per subtask, validated once against the RoboCasa manifest; each validator error
carries the step index of the subtask that produced it, so the flag lands on the
exact subtask.

This models the documented annotation shape (subtask index / atomic skill / stage
/ instruction); it is hermetic and does not download the dataset. When run against
the real LeRobot parquet, the per-subtask fields align. Nothing is actuated. The
lens is static and offline, and the committed ``subtask-eval-report.txt`` is
byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "robocasa-kitchen.manifest.yaml"

_OOD_CODES = {"capability.missing_object_class", "capability.missing_location"}
_OOC_CODES = {
    "capability.missing_gripper",
    "capability.drive_type_not_aerial",
    "capability.missing_service_ceiling",
}


# One annotated RoboCasa subtask, as the composite datasets label it:
# (atomic-skill name, stage [navigate|pick|place], per-subtask instruction, the
# URML primitive it lowers to). A plain tuple, mirroring eval_lens.py, to avoid a
# dataclass-under-importlib pitfall in the byte-assert test.
Subtask = tuple[str, str, str, dict[str, Any]]

# Three RoboCasa-style composite tasks, each an ordered list of annotated
# subtasks (one atomic skill per subtask, mirroring the per-stage annotation).
_COMPOSITES: list[tuple[str, list[Subtask]]] = [
    (
        "put the mug in the sink",
        [
            ("NavigateKitchen", "navigate", "go to the counter",
             {"move_to": {"location": "counter"}}),
            ("PnP", "pick", "pick up the mug from the counter",
             {"pick_from": {"source": "counter", "object": "mug", "store_as": "m"}}),
            ("NavigateKitchen", "navigate", "go to the sink",
             {"move_to": {"location": "sink"}}),
            ("PnP", "place", "place the mug in the sink",
             {"place_at": {"target": "sink", "held": "$m", "mode": "place"}}),
        ],
    ),
    (
        "set the table",
        [
            ("NavigateKitchen", "navigate", "go to the cabinet",
             {"move_to": {"location": "cabinet"}}),
            ("PnP", "pick", "pick up the plate from the cabinet",
             {"pick_from": {"source": "cabinet", "object": "plate", "store_as": "p"}}),
            ("NavigateKitchen", "navigate", "go to the counter",
             {"move_to": {"location": "counter"}}),
            ("PnP", "place", "place the plate on the counter",
             {"place_at": {"target": "counter", "held": "$p", "mode": "place"}}),
            ("PnP", "pick", "pick up the anvil from the cabinet",
             {"pick_from": {"source": "cabinet", "object": "anvil", "store_as": "a"}}),
        ],
    ),
    (
        "wash the kettle",
        [
            ("NavigateKitchen", "navigate", "go to the sink",
             {"move_to": {"location": "sink"}}),
            ("PnP", "pick", "pick up the kettle from the sink",
             {"pick_from": {"source": "sink", "object": "kettle", "store_as": "k"}}),
            ("PnP", "pick", "scrub the kettle, gripping it at 200 N",
             {"pick_from": {"source": "sink", "object": "kettle",
                            "force": {"newtons": 200}, "store_as": "k2"}}),
        ],
    ),
]


def _program(subtasks: list[Subtask]) -> dict[str, Any]:
    return {"profile": "home", "behavior": {"type": "sequence", "steps": [s[3] for s in subtasks]}}


def _category(code: str) -> str:
    if code in _OOD_CODES:
        return "out-of-distribution"
    if code in _OOC_CODES:
        return "out-of-capability"
    return "flagged"


def _step_index(path: list[Any]) -> int | None:
    """Pull the subtask's step index out of a validator error path.

    Paths look like ['behavior', 'steps', '4']; the subtask is that step.
    """
    if len(path) >= 3 and path[0] == "behavior" and path[1] == "steps":
        try:
            return int(path[2])
        except (TypeError, ValueError):
            return None
    return None


def render_report() -> str:
    manifest = _load(MANIFEST)
    gripper = manifest["manipulation"]["grippers"][0]
    vocab = manifest["perception"]["object_vocabulary"]
    places = [loc["name"] for loc in manifest["declared_locations"]]

    lines: list[str] = [
        "URML as a PER-SUBTASK eval lens over RoboCasa composite tasks.",
        "RoboCasa annotates every composite frame with a subtask (index, atomic skill,",
        "stage, instruction). The lens walks those subtasks and flags WHICH one leaves",
        "the robot's declared capability, instead of a whole-instruction pass/flag.",
        f"robot: {manifest['robot_id']} (Franka Panda on an Omron base)",
        f"gripper force <= {gripper['force_max_n']:.0f} N   scene objects: {', '.join(vocab)}",
        f"scene places: {', '.join(places)}",
        "",
    ]

    for title, subtasks in _COMPOSITES:
        result = validate(_program(subtasks), manifest, profiles=["home"], policy=None)
        # Map each error to the subtask (step) it came from.
        by_step: dict[int, Any] = {}
        for e in result.errors:
            idx = _step_index(list(e.path))
            if idx is not None and idx not in by_step:
                by_step[idx] = e

        lines.append(f'Composite: "{title}"  ({len(subtasks)} annotated subtasks)')
        width = max(len(f"{skill}/{stage}") for skill, stage, _, _ in subtasks)
        flagged_at: list[int] = []
        for i, (skill, stage, instruction, _step) in enumerate(subtasks):
            tag = f"{skill}/{stage}"
            if i in by_step:
                e = by_step[i]
                cat = _category(e.code_str)
                flagged_at.append(i + 1)
                lines.append(f"  [FLAG]  {i + 1}. {tag:<{width}}  {instruction}")
                lines.append(f"             -> {cat}: {e.code_str}")
            else:
                lines.append(f"  [PASS]  {i + 1}. {tag:<{width}}  {instruction}")
        if flagged_at:
            where = ", ".join(str(n) for n in flagged_at)
            lines.append(
                f"  => subtask {where} is the flagged step; the rest are in-capability."
            )
        else:
            lines.append("  => every subtask is in-capability.")
        lines.append("")

    lines.append(
        "The lens never executes anything. With per-subtask annotations it points at"
    )
    lines.append(
        "the exact step that goes out-of-distribution or out-of-capability, a sharper"
    )
    lines.append("signal for the benchmark than a single verdict over the whole instruction.")
    return "\n".join(lines) + "\n"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


if __name__ == "__main__":
    report = render_report()
    (_HERE / "subtask-eval-report.txt").write_text(report, encoding="utf-8")
    print(report, end="")
