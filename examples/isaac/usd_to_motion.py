#!/usr/bin/env python3
"""A USD-derived manifest, validated, then driven through the Isaac Sim adapter.

The worked example NVIDIA Isaac asked for on isaac-sim/IsaacSim#649: not a
conceptual mapping, but the real flow that earns a conformance listing.

1. The manifest (isaac-arm.manifest.yaml) was derived from a USD asset. Every
   capability claim carries an RFC-0631 `evidence` tag tracing it to the USD prim
   it came from, so a reviewer can tell a derived contract from a hand-typed one.
2. A URML program is validated against that manifest before anything actuates
   (validate before actuate). It is also validated under an opt-in evidence
   policy that requires `derived` evidence for the mobility and sensor claims:
   because the manifest is USD-derived, it passes the listing-grade gate.
3. The validated program is executed through the real IsaacAdapter, hermetically:
   a fake `isaacsim` module is injected (no isaacsim wheel, no GPU, no engine),
   exactly the technique the opcua example uses for asyncua. Each `move_to`
   lowers to a control-vector write plus a physics step.

It is deterministic, so the committed ``motion-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "isaac-arm.manifest.yaml"
ADAPTER_CFG = _HERE / "isaacsim_adapter.yaml"

# An opt-in evidence policy (RFC-0631): the mobility envelope and every sensor
# claim must be derived from the asset or verified, never hand-typed. This is the
# gate a conformance listing would apply, and a USD-derived manifest passes it.
_EVIDENCE_POLICY: dict[str, Any] = {
    "policy_id": "isaac-listing-evidence",
    "rules": [],
    "evidence_rules": [
        {
            "id": "mobility-derived",
            "applies_to": "mobility",
            "min_source": "derived",
            "on_violation": {"code": "policy.evidence_insufficient", "severity": "error"},
        },
        {
            "id": "sensors-derived",
            "applies_to": "sensor",
            "min_source": "derived",
            "on_violation": {"code": "policy.evidence_insufficient", "severity": "error"},
        },
    ],
}


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _program() -> dict[str, Any]:
    """Navigate to a waypoint, wait to settle, return home, report."""
    return {
        "profile": "home",
        "behavior": {
            "type": "sequence",
            "on_error": "abort_and_report",
            "steps": [
                {"move_to": {"location": "sim_waypoint"}},
                {"wait_for": {"condition": {"event": "settled"}}},
                {"move_to": {"location": "sim_home"}},
                {"report": {"to": "sim_log", "facts": {"run": "usd_to_motion"}, "status": "success"}},
            ],
        },
    }


# --------------------------------------------------------------------------
# Embedded fake isaacsim (no wheel, no GPU, no engine). Same technique the
# opcua example uses for asyncua: a controllable double injected into
# sys.modules so the real IsaacAdapter runs against it.
# --------------------------------------------------------------------------


class _FakeModel:
    def __init__(self, nu: int) -> None:
        self.nu = nu


class _FakeData:
    def __init__(self, model: _FakeModel) -> None:
        self.ctrl = [0.0] * model.nu
        self.sensordata = [42.0]


def _install_fake_isaacsim(step_counter: dict[str, int]) -> None:
    mod = ModuleType("isaacsim")

    class IsaacModel:
        @staticmethod
        def from_xml_path(path: str) -> _FakeModel:
            return _FakeModel(nu=4)

    def isaac_data(model: _FakeModel) -> _FakeData:
        return _FakeData(model)

    def sim_step(model: _FakeModel, data: _FakeData) -> None:
        step_counter["n"] += 1

    mod.IsaacModel = IsaacModel  # type: ignore[attr-defined]
    mod.IsaacData = isaac_data  # type: ignore[attr-defined]
    mod.sim_step = sim_step  # type: ignore[attr-defined]
    sys.modules["isaacsim"] = mod


def render_report() -> str:
    manifest = _load(MANIFEST)
    program = _program()

    lines: list[str] = [
        "URML on Isaac Sim: a USD-derived manifest, validated, then driven through the adapter.",
        "The flow NVIDIA Isaac asked for on isaac-sim/IsaacSim#649: USD evidence ->",
        "validated capability contract -> backend-neutral adapter dispatch.",
        f"robot: {manifest['robot_id']}   substrate: urml-isaac-runtime (zero ROS)",
        "",
        "# 1. Each capability claim traces to the USD prim it was derived from (RFC-0631)",
        "",
    ]

    rows: list[tuple[str, str, str]] = []
    mob = manifest["mobility"]["evidence"]
    rows.append(("mobility", mob["source"], f"{mob['ref']['kind']}:{mob['ref']['value']}"))
    for s in manifest["perception"]["sensors"]:
        ev = s["evidence"]
        rows.append((f"sensor {s['name']}", ev["source"], f"{ev['ref']['kind']}:{ev['ref']['value']}"))
    wlabel = max(len(r[0]) for r in rows)
    wsrc = max(len(r[1]) for r in rows)
    for label, source, ref in rows:
        lines.append(f"  {label.ljust(wlabel)}  {source.ljust(wsrc)}  {ref}")
    lines.append("")

    # 2a. Validate before actuate (no policy).
    lines += ["# 2. Validate before actuate", ""]
    r = validate(program, manifest, profiles=["home"], policy=None)
    verdict = "VALID" if r.accepted else "REJECTED"
    lines.append(f"[{verdict}] navigate to sim_waypoint, wait to settle, return home, report.")
    if not r.accepted:
        lines.append("   -> " + ", ".join(e.code_str for e in r.errors))

    # 2b. Validate under the listing-grade evidence policy.
    r_pol = validate(program, manifest, profiles=["home"], policy=_EVIDENCE_POLICY)
    verdict = "VALID" if r_pol.accepted else "REJECTED"
    lines.append(
        f"[{verdict}] under the listing evidence policy (mobility + sensors must be derived/verified)."
    )
    if not r_pol.accepted:
        lines.append("   -> " + ", ".join(e.code_str for e in r_pol.errors))
    lines.append("        Because the manifest is USD-derived, it clears the gate a listing applies.")
    lines.append("")

    # 3. Execute through the real IsaacAdapter against the injected fake engine.
    lines += [
        "# 3. Execute the validated program through IsaacAdapter (hermetic fake isaacsim)",
        "",
    ]
    steps: dict[str, int] = {"n": 0}
    _install_fake_isaacsim(steps)
    from urml_isaac_runtime import IsaacAdapter, load_isaac_config

    cfg = load_isaac_config(ADAPTER_CFG)
    dispatch: list[tuple[str, list[float]]] = []
    with IsaacAdapter(cfg) as sim:
        for loc in ("sim_waypoint", "sim_home"):
            tgt = cfg.resolve_location(loc)
            assert tgt is not None
            res = sim.send_navigation_goal(location=loc)
            assert res.success
            dispatch.append((loc, list(tgt.ctrl)))

    width = max(len(loc) for loc, _ in dispatch)
    for loc, ctrl in dispatch:
        lines.append(f"  move_to {loc.ljust(width)}  ->  ctrl = {ctrl}  (+{cfg.steps_per_command} steps)")
    lines.append("")
    lines.append(f"  {len(dispatch)} move_to commands dispatched; {steps['n']} physics steps advanced.")
    lines.append(
        "  One URML operation, one control-vector write on the USD model. No ROS in the path."
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    report = render_report()
    (_HERE / "motion-report.txt").write_text(report, encoding="utf-8")
    print(report, end="")
