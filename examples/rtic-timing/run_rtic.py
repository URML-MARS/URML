#!/usr/bin/env python3
"""A declared cyclic-timing requirement, checked for coherence and mapped onto RTIC.

For rtic-rs/rtic#1188. URML's RFC-0016 `realtime` block lets a robot's manifest
declare the cyclic timing a control node runs under: a control-cycle period and a
watchdog deadline that faults to a safe state if a cycle is missed. URML does no
scheduling, no WCET, and no schedulability analysis. It states the requirement;
a real-time substrate such as RTIC is what honors and proves it.

This example shows two things.

1. The one thing URML checks: internal coherence. A watchdog shorter than one
   control cycle is incoherent (it would fault before a single cycle completes),
   and the validator rejects it with `capability.watchdog_shorter_than_cycle`.
   This is a sanity check on the declaration, not a real-time guarantee.

2. How the declared timing maps onto an RTIC task set, aligned with the modular
   compilation-pass model of RTIC eVo (rtic-mc-experiments): the declared period
   becomes a periodic task, and the declared watchdog becomes a run-time monitor.
   URML declares; an RTIC pass generates. URML does not emit the Rust.

Hermetic and deterministic (validator only, no MCU, no RTIC), so the committed
``rtic-timing-report.txt`` is byte-asserted in CI.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "mcu-controller.manifest.yaml"
_PROFILES = ("industrial",)

# A trivial, always-valid program: the example is about the manifest's realtime
# coherence (a Pass-2 manifest check), so the program just has to validate.
_PROGRAM: dict[str, Any] = {
    "profile": "industrial",
    "behavior": {"type": "sequence", "on_error": "abort_and_report", "steps": [{"wait": {"duration": 1.0}}]},
}


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _mapping_lines(rt: dict[str, Any]) -> list[str]:
    """Render how the declared timing maps onto an RTIC (eVo) task set."""
    period = rt["cyclic_period_ms"]
    watchdog = rt["watchdog_ms"]
    guarantee = rt["guarantee"]
    return [
        "# How the declaration maps onto an RTIC task set",
        "",
        "URML declares the requirement; an RTIC compilation pass generates the code",
        "that honors it. Aligned with RTIC eVo's modular passes (rtic-mc-experiments),",
        "where rtic-deadline-pass already turns deadlines into priorities, a periodic",
        "-task-plus-verification pass would consume this declaration as:",
        "",
        f"  realtime.cyclic_period_ms = {period} ms  ->  a periodic task released every {period} ms",
        f"  realtime.watchdog_ms      = {watchdog} ms  ->  a watchdog monitor armed to {watchdog} ms,",
        "                                           cleared by the periodic task each cycle;",
        "                                           it fires if a cycle overruns the deadline",
        f"  realtime.guarantee        = {guarantee!r}   ->  scheduled under RTIC's fixed-priority SRP model",
        "",
        "Illustrative sketch of what such a pass could generate (NOT emitted by URML,",
        "and not verified Rust; the shape, not the syntax):",
        "",
        "  #[periodic(period = 10.ms(), watchdog = 50.ms())]",
        "  fn control_loop(cx: control_loop::Context) {",
        "      // one control cycle; must complete and clear the watchdog within 50 ms",
        "  }",
        "  // a generated monitor faults to a safe state if the watchdog is not cleared",
        "",
        "URML does not schedule, compute WCET, or prove schedulability. The declared",
        "period and watchdog are the inputs an RTIC pass and an SRP response-time",
        "analysis consume; the guarantee is RTIC's to provide.",
    ]


def render_report() -> str:
    manifest = _load(MANIFEST)
    rt = manifest["realtime"]

    lines = [
        "URML: a declared cyclic-timing requirement, coherence-checked and mapped to RTIC.",
        "RFC-0016 lets a manifest declare a control-cycle period and a watchdog. URML",
        "checks the declaration is coherent; it does no scheduling, WCET, or analysis.",
        "For rtic-rs/rtic#1188.",
        "",
        f"Declared: {rt['cyclic_period_ms']} ms cycle, {rt['watchdog_ms']} ms watchdog, "
        f"guarantee = {rt['guarantee']!r}.",
        "",
        "# 1. The coherent declaration validates",
        "",
    ]

    ok = validate(_PROGRAM, manifest, profiles=_PROFILES, policy=None)
    verdict_ok = "VALID" if ok.accepted else "REJECTED"
    lines.append(f"[{verdict_ok}] watchdog {rt['watchdog_ms']} ms >= cycle {rt['cyclic_period_ms']} ms")
    if ok.accepted:
        lines.append("   The watchdog allows at least one full control cycle; the declaration is coherent.")
    else:
        lines.append("   -> " + ", ".join(sorted({e.code_str for e in ok.errors})))
    lines.append("")

    # The same manifest with an incoherent watchdog (shorter than one cycle).
    bad = copy.deepcopy(manifest)
    bad["realtime"]["watchdog_ms"] = 5.0
    lines += ["# 2. An incoherent declaration is rejected (watchdog shorter than one cycle)", ""]
    over = validate(_PROGRAM, bad, profiles=_PROFILES, policy=None)
    verdict_bad = "VALID" if over.accepted else "REJECTED"
    codes = sorted({e.code_str for e in over.errors})
    lines.append(f"[{verdict_bad}] watchdog 5.0 ms < cycle {bad['realtime']['cyclic_period_ms']} ms")
    lines.append("   -> " + ", ".join(codes))
    msgs = {e.code_str: e.message for e in over.errors}
    if "capability.watchdog_shorter_than_cycle" in msgs:
        lines.append(f"   capability.watchdog_shorter_than_cycle: {msgs['capability.watchdog_shorter_than_cycle']}")
    lines.append("")

    lines += _mapping_lines(rt)

    # Assert the claims, so a behavior drift fails CI.
    assert ok.accepted, "the coherent realtime declaration should validate"
    assert not over.accepted, "a watchdog shorter than one cycle should be rejected"
    assert "capability.watchdog_shorter_than_cycle" in codes, "the incoherent case should carry the RFC-0016 code"

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "rtic-timing-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
