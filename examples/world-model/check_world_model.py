#!/usr/bin/env python3
"""URML checks intent against a robot's declared world model: rooms and objects.

The worked example for RFC-0615, from the linorobot2 / Dallas Personal Robotics
Group feedback ("how to define objects, rooms... it doesn't define how objects
will be detected"). The manifest declares named rooms (declared_areas) and which
sensor detects which object class (perception.object_detection). URML does not
map the rooms or perform detection; it declares the finite set this robot is
configured for, so a request that names a room or object the robot was never
declared to know is refused before it actuates.

This script validates a few model-produced intents against
`home.manifest.yaml` and prints the decision per intent. It is hermetic (the
validator only) and deterministic, so the committed `world-model-report.txt` is
byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "home.manifest.yaml"
INTENTS = _HERE / "intents.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _summary(program: dict[str, Any]) -> str:
    parts = []
    for step in program["behavior"]["steps"]:
        verb, args = next(iter(step.items()))
        args = args or {}
        if verb == "move_to":
            parts.append(f"move_to({args.get('location')})")
        elif verb == "detect":
            parts.append(f"detect({args.get('object')})")
        elif verb == "grasp":
            parts.append("grasp")
        else:
            parts.append(verb)
    return " -> ".join(parts)


def render_report() -> str:
    manifest = _load(MANIFEST)
    intents = _load(INTENTS)["intents"]
    rooms = [a["name"] for a in manifest.get("declared_areas", [])]
    vocab = manifest["perception"]["object_vocabulary"]

    lines = [
        "URML checks intent against the declared world model (rooms + objects).",
        f"robot: {manifest['robot_id']}",
        f"known rooms: {', '.join(rooms)}",
        f"known objects: {', '.join(vocab)}",
        "",
    ]
    for intent in intents:
        result = validate(intent["program"], manifest, policy=None)
        if result.accepted:
            lines.append(f"[ACCEPT] {intent['label']}")
            lines.append(f"   {_summary(intent['program'])}")
        else:
            codes = ", ".join(e.code_str for e in result.errors)
            lines.append(f"[REFUSE] {intent['label']}")
            lines.append(f"   {_summary(intent['program'])}  ->  [{codes}]")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "world-model-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
