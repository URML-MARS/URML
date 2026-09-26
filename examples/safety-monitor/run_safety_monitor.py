#!/usr/bin/env python3
"""Declare a runtime-monitorable safety property, check it before dispatch, monitor it at run time.

RFC-0382. A deployment envelope declares temporal-logic properties over the robot's
runtime signals (speed, person_distance, a declared stop_requested event). URML does two
things with them, and this example shows both, hermetically (validator only, no ROS, no robot):

  1. Validate (before dispatch): the validator parses each property and resolves its signals
     against the manifest. A malformed expression or a signal the robot cannot sense is
     refused at validation time, with a typed code, before anything runs.
  2. Monitor (at run time): the same property is evaluated over a trace of signal samples.
     URML ships the evaluator (urml_validator.monitor); a runtime shield or `urml validate
     --rehearse` uses it to catch a violation. URML declares and checks; it does not itself
     drive the robot.

The headline property is "slow near people": never move faster than 0.3 m/s while a person is
within 2 m. It validates cleanly, a compliant trace satisfies it, and a fast-near-a-person
trace violates it.

Deterministic and byte-asserted: the committed ``safety-monitor-report.txt`` is checked in CI.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml
from urml_validator import validate
from urml_validator.monitor import Sample, evaluate_trace
from urml_validator.monitorable import parse_property

_HERE = Path(__file__).resolve().parent
MANIFEST = _HERE / "slow-near-people.manifest.yaml"
PROGRAM = _HERE / "slow-near-people.urml.yaml"
ENVELOPE = _HERE / "slow-near-people.envelope.yaml"
_PROFILES = ("home",)

_SLOW_NEAR_PEOPLE = "always (person_distance < 2.0 implies speed <= 0.3)"


def _load(path: Path) -> Any:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _validate(program: Any, manifest: Any, envelope: Any) -> tuple[bool, list[str], dict[str, str]]:
    res = validate(program, manifest, envelope, profiles=_PROFILES, policy=None)
    codes = sorted({e.code_str for e in res.errors})
    msgs = {e.code_str: e.message for e in res.errors}
    return res.accepted, codes, msgs


def _with_property(envelope: Any, name: str, expression: str) -> Any:
    """A copy of the envelope with its monitorable_properties replaced by one property."""
    variant = copy.deepcopy(envelope)
    variant["monitorable_properties"] = [{"name": name, "dialect": "stl", "expression": expression}]
    return variant


def render_report() -> str:
    manifest = _load(MANIFEST)
    program = _load(PROGRAM)
    envelope = _load(ENVELOPE)

    lines = [
        "URML: declare a monitorable safety property, check it before dispatch, monitor it at run time.",
        "RFC-0382. The deployment envelope declares temporal-logic properties over runtime signals.",
        "The validator parses them and resolves their signals before dispatch; the monitor evaluates",
        "them over a signal trace at run time. URML declares and checks; it does not run the robot.",
        "",
        "Signals available: built-ins speed, altitude, payload, grip_force, person_distance, plus",
        "the manifest's declared events (here: stop_requested) and declared sensors.",
        "",
        "# 1. Validate before dispatch",
        "",
    ]

    ok, ok_codes, _ = _validate(program, manifest, envelope)
    lines.append(f"[{'VALID' if ok else 'REJECTED'}] envelope with slow_near_people + bounded_stop")
    if ok:
        lines.append("   Both properties parse and every signal resolves. Dispatch may proceed;")
        lines.append("   a monitor backend enforces them at run time.")
    else:
        lines.append("   -> " + ", ".join(ok_codes))
    lines.append("")

    bad_parse, parse_codes, parse_msgs = _validate(
        program, manifest, _with_property(envelope, "unterminated", "always (")
    )
    lines.append(f"[{'VALID' if bad_parse else 'REJECTED'}] a malformed expression: \"always (\"")
    lines.append("   -> " + ", ".join(parse_codes))
    if "envelope.monitorable_parse_error" in parse_msgs:
        lines.append("   " + parse_msgs["envelope.monitorable_parse_error"])
    lines.append("")

    bad_sig, sig_codes, sig_msgs = _validate(
        program, manifest, _with_property(envelope, "battery_guard", "always (battery_temp < 80)")
    )
    lines.append(f"[{'VALID' if bad_sig else 'REJECTED'}] a property on an undeclared signal: battery_temp")
    lines.append("   -> " + ", ".join(sig_codes))
    if "envelope.monitorable_undeclared_signal" in sig_msgs:
        lines.append("   " + sig_msgs["envelope.monitorable_undeclared_signal"])
    lines.append("   You cannot monitor what the manifest never said the robot can sense.")
    lines.append("")

    lines += [
        "# 2. Monitor at run time",
        "",
        f"Property slow_near_people: {_SLOW_NEAR_PEOPLE}",
        "",
    ]

    node = parse_property(_SLOW_NEAR_PEOPLE, dialect="stl")
    compliant = [
        Sample(t=0.0, signals={"speed": 1.0, "person_distance": 5.0}),
        Sample(t=1.0, signals={"speed": 0.2, "person_distance": 1.0}),
    ]
    violating = [
        Sample(t=0.0, signals={"speed": 1.0, "person_distance": 5.0}),
        Sample(t=1.0, signals={"speed": 1.0, "person_distance": 1.0}),
    ]
    compliant_ok = evaluate_trace(node, compliant)
    violating_ok = evaluate_trace(node, violating)
    lines.append(
        f"[{'SATISFIED' if compliant_ok else 'VIOLATED'}] trace: slows to 0.2 m/s as a person closes to 1 m"
    )
    lines.append(
        f"[{'SATISFIED' if violating_ok else 'VIOLATED'}] trace: holds 1.0 m/s with a person at 1 m"
    )
    lines.append("")
    lines += [
        "# The two layers",
        "",
        "The static check is the first line, off-hardware: a malformed or unmonitorable property",
        "is refused before dispatch, in an LLM planning loop or in CI. The monitor is the last line,",
        "on-hardware: the ros2 shield (ShieldedAdapter) or `urml validate --rehearse` evaluates the",
        "property over the live or simulated signal trace and blocks a critical violation. Same",
        "declaration, checked once and enforced continuously. URML runs neither the planner nor the",
        "robot; it declares the property and provides the checker and the evaluator.",
    ]

    # Assert the claims so a behavior drift fails CI.
    assert ok, "the well-formed envelope should validate"
    assert not bad_parse and "envelope.monitorable_parse_error" in parse_codes, "malformed expr should be rejected"
    assert not bad_sig and "envelope.monitorable_undeclared_signal" in sig_codes, "undeclared signal should be rejected"
    assert compliant_ok, "the compliant trace should satisfy slow_near_people"
    assert not violating_ok, "the fast-near-a-person trace should violate slow_near_people"

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    out = _HERE / "safety-monitor-report.txt"
    out.write_text(render_report(), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
