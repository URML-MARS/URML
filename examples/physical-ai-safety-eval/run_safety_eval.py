#!/usr/bin/env python3
"""A safety-evaluation harness for AI agents operating physical equipment.

Anthropic's Model Hardware Standard opens to everyone after "safety
evaluations and best practices for AI systems that operate physical
equipment" exist. This harness is URML's contribution to that gate: a
corpus of agent intents against a lab-cell manifest shaped like the assay
in Anthropic's announcement (liquid handler, plate-handling arm, plate
reader) and a deployment envelope, judged before anything moves.

What it measures, exactly:

1. **Admissibility.** Each intent is validated whole against the manifest
   and the envelope (five passes). Refusals carry machine-readable codes.
2. **The second check.** Every accepted program is rehearsed under a
   declared motion model and the RFC-0667 envelope monitors judge the
   trace (the runtime shield's view of the same envelope).
3. **Evidence class.** For each refusal, the evidence tag (RFC-0631) of
   the capability it relied on, so a reviewer sees whether the limit that
   refused the action was declared, derived, or verified.
4. **Dispatch order.** Accepted programs, and only those, lower through
   the ``MhsAdapter`` scaffold onto read/write calls; the transport records
   that no refused intent ever produced a device call.

What it does not measure: physics. URML judges declared limits and intent
coherence. Whether a declaration is true is the integrator's, the vendor's,
or a runtime measurement's responsibility, and the evidence tag says which.

Hermetic: no model, no device, no network. The committed report is
byte-asserted in CI.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path
from typing import Any

import yaml

from mhs_adapter import FakeTransport, MhsAdapter, MhsKeyMap
from urml_validator import validate
from urml_validator.monitor import Sample, compile_envelope_monitors, evaluate_trace

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "lab-cell.manifest.yaml"
ENVELOPE = _HERE / "deploy.envelope.yaml"
INTENTS = _HERE / "intents.yaml"
REPORT = _HERE / "safety-eval-report.txt"

# Declared motion model for the rehearsal (RFC-0668 posture: evidence under a
# named model, never a guarantee). The tip cruises at 0.25 m/s between
# declared locations; the deployment cap is 0.3 m/s.
CRUISE_MPS = 0.25
TICK_HZ = 4.0
MOTION_VERBS = ("move_to", "pick_from", "place_at")

# Which declared capability each refusal code leans on, for the evidence column.
CODE_TO_CAPABILITY = {
    "envelope.force_exceeded": ("manipulation.grippers[plate_gripper]", "gripper"),
    "capability.missing_gripper": ("manipulation.grippers[plate_gripper]", "gripper"),
    "capability.missing_location": ("declared_locations", None),
    "capability.missing_object_class": ("perception.object_vocabulary", None),
    "capability.missing_sensor": ("perception.sensors", None),
    "capability.drive_type_not_aerial": ("mobility", "mobility"),
    "capability.missing_service_ceiling": ("mobility", "mobility"),
    "capability.missing_mobility": ("mobility", "mobility"),
}


def _load(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _evidence_of(manifest: dict[str, Any], which: str | None) -> str:
    if which == "gripper":
        ev = manifest["manipulation"]["grippers"][0].get("evidence") or {}
    elif which == "mobility":
        ev = manifest["mobility"].get("evidence") or {}
    else:
        return "n/a (declaration absent, nothing to be wrong about)"
    return f"{ev.get('source', 'untagged')}: {ev.get('note', '')}".strip()


def rehearse(program: dict[str, Any], envelope: dict[str, Any]) -> list[str]:
    """Kinematic trace under the declared model, judged by the envelope monitors."""
    ticks: list[Sample] = []
    for step in program["behavior"]["steps"]:
        (verb, _args), = step.items()
        if verb in MOTION_VERBS:
            for _ in range(math.ceil(2.0 * TICK_HZ)):  # 2 s of motion per step
                ticks.append(Sample(t=(len(ticks) + 1) / TICK_HZ, signals={"speed": CRUISE_MPS, "grip_force": 0.0}))
    if not ticks:
        ticks.append(Sample(t=1 / TICK_HZ, signals={"speed": 0.0, "grip_force": 0.0}))
    lines = []
    for prop in compile_envelope_monitors(envelope):
        ok = evaluate_trace(prop.node, ticks)
        lines.append(f"      monitor [{prop.severity}] {prop.name}: {'satisfied' if ok else 'VIOLATED'}")
    return lines


def render_report() -> str:
    manifest = _load(MANIFEST)
    envelope = _load(ENVELOPE)
    intents = _load(INTENTS)
    transport = FakeTransport(readings={"plate_reader.reading": 0.412, "deck_temperature.reading": 22.5})
    adapter = MhsAdapter(transport, MhsKeyMap(sensor_reading={"plate_reader": "plate_reader.reading", "deck_temperature": "deck_temperature.reading"}))

    out = [
        "PHYSICAL-AI SAFETY EVALUATION (hermetic; URML validator + RFC-0667 monitors)",
        f"manifest: {manifest['robot_id']} (vendor limits: tip {manifest['mobility']['max_velocity']} m/s, gripper {manifest['manipulation']['grippers'][0]['force_max_n']} N)",
        f"envelope: deployment caps tip {envelope['max_velocity']} m/s, grip {envelope['max_grip_force_n']} N (strictest wins)",
        f"motion model for rehearsal: cruise {CRUISE_MPS} m/s at {TICK_HZ:.0f} Hz",
        "",
    ]
    accepted = refused = 0
    for intent in intents:
        result = validate(intent["program"], manifest, envelope, profiles=("industrial",), policy=None)
        codes = sorted({str(getattr(e.code, "value", e.code)) for e in result.errors})
        verdict = "ACCEPT" if result.accepted else "REFUSE"
        assert (verdict == "ACCEPT") == (intent["expect"] == "accept"), (intent["id"], verdict, codes)
        out.append(f"[{verdict}] {intent['id']}: \"{intent['sentence']}\"")
        if result.accepted:
            accepted += 1
            out.extend(rehearse(intent["program"], envelope))
            for line in adapter.lower(intent["program"]):
                out.append(f"      dispatch: {line}")
        else:
            refused += 1
            expected = set(intent.get("codes", []))
            assert expected <= set(codes), (intent["id"], expected, codes)
            for code in codes:
                cap, which = CODE_TO_CAPABILITY.get(code, ("(unmapped)", None))
                out.append(f"      {code}  relied on {cap}; evidence {_evidence_of(manifest, which)}")
        out.append("")
    device_calls = len(transport.calls)
    out.append(f"SUMMARY: {accepted} accepted, {refused} refused, {device_calls} device calls, all from accepted programs.")
    out.append("MEASURES: admissibility of intent on declared hardware under a declared envelope; evidence class of every limit relied on.")
    out.append("DOES NOT MEASURE: physics. A declared limit is trusted; its evidence tag says how much.")
    text = "\n".join(out) + "\n"
    assert refused == sum(1 for i in intents if i["expect"] == "refuse")
    return text


def main() -> int:
    text = render_report()
    print(text, end="")
    REPORT.write_text(text, encoding="utf-8", newline="\n")
    print(f"(wrote {REPORT.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
