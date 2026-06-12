#!/usr/bin/env python3
"""URML declares a fieldbus's cyclic (PDO) and acyclic (SDO) operation modes.

The worked example from the ethercat_driver_ros2 engagement
(ICube-Robotics/ethercat_driver_ros2#224, RFC-0320), where the driver's
maintainer flagged the operation-mode distinction precisely: in cyclic
communication (PDO) the bus answer is immediate, whereas for asynchronous
mailbox traffic (SDO) the answer time is not guaranteed, so error handling,
goal-reached checks, and timeouts change completely.

URML models both regimes in the capability manifest's ``realtime`` block. The
cyclic path is a control period plus a watchdog (RFC-0016); the acyclic path is
a timeout plus an explicit goal-reached check (RFC-0469). URML stays above the
controller: it declares the regime so the manifest is a faithful description of
the drive, and the validator rejects an incoherent timing declaration before the
cell is commissioned.

This script takes the base EtherCAT servo manifest and validates three timing
declarations against a trivial program: a cyclic-only drive, the same drive with
a coherent SDO regime, and a drive whose SDO timeout is shorter than one control
cycle (an incoherent declaration: a command that must return inside one cycle is
cyclic traffic, not acyclic). It is hermetic (the validator only, no bus, no
robot) and deterministic, so the committed ``operation-mode-report.txt`` is
byte-asserted in CI.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "ethercat-drive.manifest.yaml"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _program() -> dict[str, Any]:
    return {
        "profile": "industrial",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [{"move_to": {"location": "home"}}],
        },
    }


def _regime(rt: dict[str, Any]) -> str:
    cyc = f"cyclic: {rt['cyclic_period_ms']} ms period / {rt['watchdog_ms']} ms watchdog"
    ac = rt.get("acyclic")
    if ac is None:
        return cyc + "; acyclic: none declared"
    check = "read-back goal check" if ac.get("requires_goal_check", True) else "no goal check"
    return cyc + f"; acyclic: {ac['timeout_ms']} ms timeout / {check}"


def render_report() -> str:
    base = _load(MANIFEST)
    program = _program()

    # Three timing declarations over the same drive.
    cyclic_only = copy.deepcopy(base)
    cyclic_only["realtime"].pop("acyclic", None)

    coherent = copy.deepcopy(base)  # cyclic + a 500 ms SDO regime

    incoherent = copy.deepcopy(base)
    incoherent["realtime"]["acyclic"]["timeout_ms"] = 0.5  # shorter than the 1 ms cycle

    cases = [
        ("cyclic PDO only (no mailbox path declared)", cyclic_only),
        ("cyclic PDO + coherent acyclic SDO", coherent),
        ("cyclic PDO + SDO timeout shorter than one cycle", incoherent),
    ]

    lines = [
        "URML fieldbus operation-mode check: one drive, three timing declarations.",
        "URML declares the regime above the controller; the validator checks coherence.",
        f"drive: {base['robot_id']}",
        "",
    ]
    for label, manifest in cases:
        result = validate(program, manifest, policy=None)
        verdict = "VALID" if result.accepted else "REJECTED"
        lines.append(f"[{verdict}] {label}")
        lines.append(f"   {_regime(manifest['realtime'])}")
        if not result.accepted:
            codes = ", ".join(e.code_str for e in result.errors)
            lines.append(f"   -> incoherent declaration [{codes}]; not commissioned.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "operation-mode-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
