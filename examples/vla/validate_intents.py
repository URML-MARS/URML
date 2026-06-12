#!/usr/bin/env python3
"""URML as the validated-intent gate between a vision-language model and a robot.

The worked example from the OpenMind / OM1 engagement (OpenMind/OM1#2587), where
@TangmereCottage asked the right question: how does URML coexist with world models
and vision-language models?

The answer this example demonstrates: URML does not interpret perception and does
not compete with the model. The model (VLM / VLA / world model) turns multimodal
input (voice, gesture) into an *intent*; URML is the typed layer that **validates
that intent against the capability manifest and the safety envelope before it
reaches an actuator**. Safe intents dispatch; unsafe ones are rejected at the
gate, with a reason, and never actuate.

This script takes a set of model-interpreted intents (``interpreted-intents.yaml``,
as if emitted by a VLM), validates each against the home-service manifest and
safety envelope, and prints the gate decision per intent. It is hermetic (the
validator only, no model, no robot) and deterministic, so the committed
``gate-report.txt`` is byte-asserted in CI.

URML already carries the pieces this composes: the LLM bridge is Layer 4 (the
model-to-URML front door), a learned policy can be the bounded substrate
(`learned_policy`, RFC-0383), and fast safety reflexes (the "Stop" reflex) are
pre-declared monitorable properties (RFC-0382) a runtime monitor enforces, so the
gate does not add latency to a reflex.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "home-service.manifest.yaml"
ENVELOPE = _HERE / "safety-envelope.yaml"
INTENTS = _HERE / "interpreted-intents.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _summary(program: dict[str, Any]) -> str:
    parts = []
    for step in program.get("behavior", {}).get("steps", []):
        verb, args = next(iter(step.items()))
        args = args or {}
        if verb == "move_to":
            parts.append(f"move_to({args.get('location')})")
        elif verb == "detect":
            parts.append(f"detect({args.get('object')})")
        elif verb == "grasp":
            parts.append(f"grasp(force={args.get('force')})")
        else:
            parts.append(f"{verb}(...)")
    return " -> ".join(parts)


def render_gate_report() -> str:
    manifest = _load(MANIFEST)
    envelope = _load(ENVELOPE)
    intents = _load(INTENTS)["intents"]

    lines = [
        "URML intent gate: a vision-language model proposes, URML validates, the robot",
        "acts only on what passes.",
        f"robot: {manifest['robot_id']}  |  envelope: {envelope['deployment_id']}",
        "",
    ]
    for intent in intents:
        result = validate(intent["program"], manifest, envelope, policy=None)
        verdict = "DISPATCH" if result.accepted else "REJECTED"
        lines.append(f"[{verdict}] {intent['label']}")
        lines.append(f"   model interpreted  {intent['modality']}")
        if result.accepted:
            lines.append(f"   -> {_summary(intent['program'])}; validated, dispatched to the substrate.")
        else:
            codes = ", ".join(e.code_str for e in result.errors)
            lines.append(f"   -> {_summary(intent['program'])}; rejected at the gate [{codes}]. No actuator command sent.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "gate-report.txt"
    out.write_text(render_gate_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
