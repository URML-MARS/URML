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

The maintainer's follow-up raised two more fieldbus gaps URML now models: the
substrate clock / time-synchronization regime (RFC-0477) and ordered bring-up /
recovery sequences (RFC-0478). This script validates the base CiA-402 drive
against variants in all three areas and prints, per case, whether the
declaration is coherent and why a rejected one is not. It is hermetic (the
validator only, no bus, no robot) and deterministic, so the committed
``operation-mode-report.txt`` is byte-asserted in CI.
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


def _clock_regime(clock: dict[str, Any]) -> str:
    hw = ", hardware-timestamped" if clock.get("hardware_timestamping") else ""
    proto = clock.get("sync_protocol", "none")
    return f"reference: {clock['reference']} / {proto}{hw}"


def _bringup_regime(bringup: dict[str, Any]) -> str:
    parts = []
    for el in bringup["elements"]:
        deps = el.get("depends_on") or []
        parts.append(el["id"] + (f"(after {','.join(deps)})" if deps else ""))
    return " | ".join(parts)


def _emit(lines: list[str], label: str, manifest: dict[str, Any], regime: str) -> None:
    result = validate(_program(), manifest, policy=None)
    verdict = "VALID" if result.accepted else "REJECTED"
    lines.append(f"[{verdict}] {label}")
    lines.append(f"   {regime}")
    if not result.accepted:
        codes = ", ".join(e.code_str for e in result.errors)
        lines.append(f"   -> incoherent declaration [{codes}]; not commissioned.")
    lines.append("")


def render_report() -> str:
    base = _load(MANIFEST)

    lines = [
        "URML fieldbus declaration check: one CiA-402 EtherCAT drive.",
        "URML declares the regime above the controller; the validator checks coherence.",
        f"drive: {base['robot_id']}",
        "",
        "# Operation mode (RFC-0016 cyclic / RFC-0469 acyclic)",
        "",
    ]

    # 1. Operation mode: cyclic PDO vs acyclic SDO.
    cyclic_only = copy.deepcopy(base)
    cyclic_only["realtime"].pop("acyclic", None)
    coherent = copy.deepcopy(base)
    incoherent = copy.deepcopy(base)
    incoherent["realtime"]["acyclic"]["timeout_ms"] = 0.5  # shorter than the 1 ms cycle
    for label, m in [
        ("cyclic PDO only (no mailbox path declared)", cyclic_only),
        ("cyclic PDO + coherent acyclic SDO", coherent),
        ("cyclic PDO + SDO timeout shorter than one cycle", incoherent),
    ]:
        _emit(lines, label, m, _regime(m["realtime"]))

    # 2. Clock / time synchronization (RFC-0477).
    lines += ["# Clock / time synchronization (RFC-0477)", ""]
    bus_dc = copy.deepcopy(base)  # the drive's declared DC reference
    master_no_proto = copy.deepcopy(base)
    master_no_proto["substrate"]["clock"] = {"reference": "master_synced"}
    for label, m in [
        ("bus clock as reference (EtherCAT DC, hardware-timestamped)", bus_dc),
        ("master-synced without a sync protocol", master_no_proto),
    ]:
        _emit(lines, label, m, _clock_regime(m["substrate"]["clock"]))

    # 3. Ordered bring-up / recovery (RFC-0478).
    lines += ["# Ordered bring-up / recovery (RFC-0478)", ""]
    chain = copy.deepcopy(base)  # power_bus -> drive_axis_1 -> gripper
    cyclic_dep = copy.deepcopy(base)
    cyclic_dep["substrate"]["bringup"]["elements"][0]["depends_on"] = ["gripper"]
    for label, m in [
        ("power_bus -> drive_axis_1 -> gripper", chain),
        ("circular bring-up dependency", cyclic_dep),
    ]:
        _emit(lines, label, m, _bringup_regime(m["substrate"]["bringup"]))

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "operation-mode-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
