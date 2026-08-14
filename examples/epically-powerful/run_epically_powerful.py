#!/usr/bin/env python3
"""A declared actuator envelope, checked before dispatch, beside a runtime monitor.

For gatech-epic-power/epically-powerful#32. Epically Powerful commands QDD
actuators over CAN and enforces per-motor limits at run time. URML's manifest
declares the same envelope (RFC-0018 `minimal_node` + RFC-0017 analog
`outputs.lines`) and checks a command against it statically, before anything is
sent over CAN.

The question raised on the issue was whether this duplicates the runtime monitor.
It does not. The two are complementary layers:

  - URML's static check is the FIRST line, off-hardware. It runs in an LLM
    planning loop, in CI, or in simulation, before any command reaches the bus.
  - Epically Powerful's runtime monitor is the LAST line, on-hardware, during
    execution.

The static gate catches an inadmissible command (an LLM emitting a 50 Nm target
on a +/-35 Nm actuator) in exactly the contexts where a runtime monitor cannot
run, because there is no hardware in the loop yet. And the envelope is one
substrate-neutral declaration that covers CubeMars, RobStride, and CyberGear
actuators alike, from a single manifest.

Envelope numbers are cross-cited from Epically Powerful's own motor table (the
CubeMars AKE80-8-V3 entry in epicallypowerful/actuation/motor_data.py, commit
2a3941278c59). No code is vendored and there is no dependency on their package.

Hermetic and deterministic (validator only, no CAN, no hardware), so the committed
``epically-powerful-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "qdd-exo.manifest.yaml"
_PROFILES = ("research",)

# AKE80-8-V3 declared limits (cross-cited from motor_data.py, commit 2a3941278c59).
_TORQUE_LINE = "joint_torque_nm"
_TORQUE_LIMIT = 35.0
_VELOCITY_LINE = "joint_velocity_rad_s"
_VELOCITY_LIMIT = 20.0


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _program(line: str, value: float) -> dict[str, Any]:
    """A one-step program that writes a setpoint to a declared actuator line."""
    return {
        "profile": _PROFILES[0],
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"set_output": {"output": line, "value": value}}],
        },
    }


def _run(manifest: Any, line: str, value: float) -> tuple[bool, list[str], dict[str, str]]:
    res = validate(_program(line, value), manifest, profiles=_PROFILES, policy=None)
    codes = sorted({e.code_str for e in res.errors})
    msgs = {e.code_str: e.message for e in res.errors}
    return res.accepted, codes, msgs


def render_report() -> str:
    manifest = _load(MANIFEST)

    lines = [
        "URML: a declared actuator envelope, checked before dispatch, beside a runtime monitor.",
        "RFC-0018 minimal_node + RFC-0017 analog output lines let a manifest declare a QDD",
        "actuator's command envelope. URML checks a command against it statically, before",
        "anything reaches the CAN bus. For gatech-epic-power/epically-powerful#32.",
        "",
        "Envelope cross-cited from Epically Powerful's CubeMars AKE80-8-V3 entry",
        "(epicallypowerful/actuation/motor_data.py, commit 2a3941278c59):",
        f"  {_TORQUE_LINE}     range +/-{_TORQUE_LIMIT} Nm   (torque_limits)",
        f"  {_VELOCITY_LINE}  range +/-{_VELOCITY_LIMIT} rad/s (velocity_limits)",
        "",
        "# 1. A command inside the declared envelope validates",
        "",
    ]

    ok, ok_codes, _ = _run(manifest, _TORQUE_LINE, 20.0)
    lines.append(f"[{'VALID' if ok else 'REJECTED'}] set_output {_TORQUE_LINE} = 20.0 Nm  (|20.0| <= {_TORQUE_LIMIT})")
    if ok:
        lines.append("   Admissible: within the actuator's declared torque limit. Dispatch may proceed.")
    else:
        lines.append("   -> " + ", ".join(ok_codes))
    lines.append("")

    lines += ["# 2. A torque command beyond the declared limit is rejected before dispatch", ""]
    bad_t, bad_t_codes, bad_t_msgs = _run(manifest, _TORQUE_LINE, 50.0)
    lines.append(f"[{'VALID' if bad_t else 'REJECTED'}] set_output {_TORQUE_LINE} = 50.0 Nm  (|50.0| > {_TORQUE_LIMIT})")
    lines.append("   -> " + ", ".join(bad_t_codes))
    if "capability.output_value_out_of_range" in bad_t_msgs:
        lines.append(f"   capability.output_value_out_of_range: {bad_t_msgs['capability.output_value_out_of_range']}")
    lines.append("   Caught off-hardware, before the command ever reaches epically-powerful's CAN path.")
    lines.append("")

    lines += ["# 3. The same check generalizes across limit types (velocity, not just torque)", ""]
    bad_v, bad_v_codes, bad_v_msgs = _run(manifest, _VELOCITY_LINE, 30.0)
    lines.append(f"[{'VALID' if bad_v else 'REJECTED'}] set_output {_VELOCITY_LINE} = 30.0 rad/s  (|30.0| > {_VELOCITY_LIMIT})")
    lines.append("   -> " + ", ".join(bad_v_codes))
    if "capability.output_value_out_of_range" in bad_v_msgs:
        lines.append(f"   capability.output_value_out_of_range: {bad_v_msgs['capability.output_value_out_of_range']}")
    lines.append("")

    lines += [
        "# Complementary layers, not duplicates",
        "",
        "URML's static envelope check is the first line, off-hardware: it runs in an LLM",
        "planning loop, in CI, or in simulation, before any command reaches the bus. Epically",
        "Powerful's runtime monitor is the last line, on-hardware, during execution. The static",
        "gate catches an inadmissible command where a runtime monitor cannot run, because there",
        "is no hardware in the loop yet, and the envelope is one substrate-neutral declaration",
        "that covers CubeMars, RobStride, and CyberGear actuators from a single manifest.",
        "",
        "URML declares and statically checks; Epically Powerful monitors at run time and drives",
        "the CAN bus. No code is vendored and there is no dependency on their package.",
    ]

    # Assert the claims, so a behavior drift fails CI.
    assert ok, "a torque command within the declared limit should validate"
    assert not bad_t, "a torque command beyond the declared limit should be rejected"
    assert "capability.output_value_out_of_range" in bad_t_codes, "the torque case should carry the RFC-0017 range code"
    assert not bad_v, "a velocity command beyond the declared limit should be rejected"
    assert "capability.output_value_out_of_range" in bad_v_codes, "the velocity case should carry the RFC-0017 range code"

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "epically-powerful-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
