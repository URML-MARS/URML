#!/usr/bin/env python3
"""URML on a Robotiq Hand-E: declare a force envelope, refuse a grasp that breaks it.

The worked example promised on AGH-CEAI/robotiq_hande_driver#44. A Hand-E is a
single-DoF parallel-jaw gripper, so URML declares it as an ordinary (non-dexterous)
gripper with a force range (force_min_n / force_max_n) and the object classes it
accepts. That force range is the envelope the validator checks a grasp against,
before anything is dispatched to the ros2_control hardware interface.

Two programs, same manifest:
  1. Grasp a small part at 60 N. Inside the declared 20-185 N envelope: ACCEPTED.
  2. Grasp the same part at 250 N. Over the 185 N cap: REJECTED with
     envelope.force_exceeded, before the gripper ever closes.

The point macmacal and I agreed on: URML is additive to ros2_control. It reads
the same numbers your URDF/driver already know (aperture range, force limit) and
refuses an out-of-envelope grasp pre-dispatch; the driver keeps the actuation.

Static validation only, no execution and no hardware. It is deterministic, so the
committed ``robotiq-hande-report.txt`` is byte-asserted.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "robotiq-hande.manifest.yaml"
_PROFILES = ("industrial",)

# The declared Hand-E force envelope, for the report header.
_FORCE_MAX_N = 185.0
_OK_FORCE_N = 60.0
_OVER_FORCE_N = 250.0


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _grasp_program(force_n: float) -> dict[str, Any]:
    """Detect a small part, grasp it at `force_n`, place it on the fixture."""
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"detect": {"object": "small_part", "store_as": "part"}},
                {"grasp": {"target": "$part", "force": {"newtons": force_n}}},
                {"release": {"mode": "place", "at": "assembly_fixture"}},
            ],
        },
    }


def render_report() -> str:
    manifest = _load(MANIFEST)

    lines = [
        "URML on a Robotiq Hand-E - issue robotiq_hande_driver#44.",
        "A single-DoF parallel-jaw gripper, declared as an ordinary (non-dexterous)",
        "gripper with a force envelope. URML checks a grasp against that envelope",
        "before the command reaches the ros2_control hardware interface.",
        f"gripper: hand_e   kind: servo_electric   force envelope: 20.0 - {_FORCE_MAX_N} N"
        "   accepts: small_part",
        "",
        "# 1. A grasp inside the declared envelope (validate before actuate)",
        "",
    ]

    ok = validate(_grasp_program(_OK_FORCE_N), manifest, profiles=_PROFILES, policy=None)
    ok_verdict = "VALID" if ok.accepted else "REJECTED"
    lines.append(f"[{ok_verdict}] grasp small_part at {_OK_FORCE_N} N")
    if not ok.accepted:
        lines.append("   -> " + ", ".join(sorted({e.code_str for e in ok.errors})))
    else:
        lines.append(f"   {_OK_FORCE_N} N is within the declared 20.0 - {_FORCE_MAX_N} N envelope; the grasp is admissible.")
    lines.append("")

    lines += ["# 2. The same grasp over the declared force cap", ""]
    over = validate(_grasp_program(_OVER_FORCE_N), manifest, profiles=_PROFILES, policy=None)
    over_verdict = "VALID" if over.accepted else "REJECTED"
    lines.append(f"[{over_verdict}] grasp small_part at {_OVER_FORCE_N} N")
    codes = sorted({e.code_str for e in over.errors})
    lines.append("   -> " + ", ".join(codes))
    # The over-force grasp is refused on two independent, honest grounds.
    msgs = {e.code_str: e.message for e in over.errors}
    if "capability.missing_gripper" in msgs:
        lines.append(f"   capability.missing_gripper: {msgs['capability.missing_gripper']}")
    if "envelope.force_exceeded" in msgs:
        lines.append(f"   envelope.force_exceeded:    {msgs['envelope.force_exceeded']}")
    lines.append("   Both fire because 250 N is outside the declared 20.0 - 185.0 N range:")
    lines.append("   no declared gripper is rated for it, and it exceeds the force cap.")
    lines.append("")

    lines += [
        "# What the manifest declares (and what it does not)",
        "",
        "  URML's simple-gripper model states a force range and the object classes",
        "  the gripper accepts. That force range is first-class and enforced above.",
        "  There is no explicit aperture field: on a single-DoF gripper, 'what fits'",
        "  is carried by accepted_classes and 'how hard' is the force envelope. The",
        "  ros2_control hardware interface keeps the actuation (Modbus / UR tool comm /",
        "  the fake backend); URML is only the pre-dispatch admissibility check, and it",
        "  behaves identically across those backends because it runs before the command.",
    ]

    # The example is a claim; assert the claim holds.
    assert ok.accepted, "the 60 N grasp should be admissible"
    assert not over.accepted, "the 250 N grasp should be refused"
    assert "envelope.force_exceeded" in codes, "the refusal should be envelope.force_exceeded"
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "robotiq-hande-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
