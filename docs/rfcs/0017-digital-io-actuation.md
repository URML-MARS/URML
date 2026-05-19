---
rfc: 0017
title: Digital-I/O actuation — driving a named substrate output
author: Ido Yahalomi (ido@jacob-ai.com)
state: Draft
created: 2026-05-19
updated: 2026-05-19
supersedes: —
superseded-by: —
---

<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# RFC-0017: Digital-I/O actuation — driving a named substrate output

## Summary

Collaborative arms and PLC-driven cells act on the world through raw
**digital outputs**: set DO-3 to fire a glue gun, pulse a blow-off,
raise a conveyor-handshake line, trigger a weld. URML has no way to say
"set the named output O to value V". This RFC is filed as a **Draft for
maintainer decision** by the spec-gap loop (RFC-0014); the
`urml-cobot-runtime` build surfaced it. It proposes — for discussion,
not yet accepted — a narrow `set_output` primitive, deliberately
scoped so it does not become a second opaque escape hatch.

## Motivation

`grasp`/`release` cover a gripper. They do not cover the large class of
end-effectors and cell signals that are *just a digital line*: a glue
dispenser, a vacuum solenoid, a paint trigger, a "cycle done" handshake
to a PLC. Modelling each as `grasp` is a lie (there is nothing grasped);
modelling it as `report` is a lie (it actuates the world, it does not
inform a recipient); and it is not a station service, so RFC-0013's
`swap_tool`-rides-`send_docking_goal` precedent — which worked precisely
because a tool change *is* a station service — does not apply. A cobot
cell that cannot fire its tool is not a useful URML target, so the gap
is real, not theoretical. It is a one-way-door primitive (RFC-0002),
which is exactly why it is an RFC and not a quiet adapter feature.

## Detailed design

A single new Layer-2 primitive:

```
set_output:
  output: <Identifier>     # a manifest-declared output line
  value: bool | number     # discrete on/off or an analog setpoint
  pulse_ms: <number>       # optional; auto-revert after the pulse
```

`output` MUST be declared in the capability manifest (a new
`effectors:`/`outputs.lines[]` declaration — the RFC-gated schema
part) with its type (digital|analog) and safe-state, so the validator
rejects an undeclared line and Pass 3 can refuse a value outside a
declared range *before* anything actuates. Unlike a hypothetical
generic `call_program` (RFC-0015), `set_output` is **not** opaque: its
effect is a single typed line write the validator fully understands —
that boundedness is the design's whole point and what keeps it from
becoming an escape hatch.

### Spec changes

- **Layer 2**: add the `set_output` primitive + JSON Schema.
- **Layer 1**: add an `outputs.lines[]` (name, kind, range, safe_state)
  declaration so a write is capability- and range-checked.
- **Layer 4**: one NL verb mapping ("turn on the glue gun" →
  `set_output`).

### Validator changes

Pass-2: `set_output.output` must be a declared line. Pass-3: a numeric
`value` must be within the declared range; a digital line rejects a
non-bool. No change to Passes 1/4/5.

### Reference runtime changes

**ROS 2 sketch**: publish to / call the declared line's `std_msgs`
topic or a `SetIO`-style service (UR and many cells expose exactly
this in their ROS driver). **Non-ROS sketch (the motivating case)**: UR
`rtde_control.setStandardDigitalOut(n, v)`; Franka FCI digital output;
an OPC UA boolean variable write. The acid test passes: the primitive
is "write a named declared line," defined with no ROS concept.

### Conformance suite changes

A `conformance/fixtures/industrial/` positive (`set_output` on a
declared line, hermetic on MockROSAdapter) and a negative (undeclared
line / out-of-range value rejected at Pass 2/3).

## Backward compatibility

Fully compatible. Additive optional primitive + optional manifest
declaration; every existing program/manifest/runtime is unchanged.
Pre-v1.0.

## Drawbacks

Even bounded, `set_output` invites cell-specific programs that lean on
raw lines instead of modelling intent ("set DO-4" instead of a real
verb), eroding readability and substrate-neutrality at the program
level even though each call is validatable. It also pushes URML one
step toward being a PLC language, which is explicitly not its job. The
mitigation — mandatory manifest declaration with type/range/safe-state,
and likely an industrial/research profile gate so `home` programs
cannot use it — is real but does not fully remove the "it becomes the
lazy answer" risk; that risk is the honest cost of supporting real
cells at all.

## Alternatives considered

1. **Compose from existing primitives.** Rejected: no primitive denotes
   a raw line write; `grasp`/`report` are category errors here.
2. **Overload `grasp` with a "kind: io" mode.** Rejected: it would make
   `grasp` mean "grasp or also any digital write," which is the same
   semantic-dilution failure RFC-0013 avoided for `dock`.
3. **Fold it into RFC-0015 `call_program`.** Rejected: a typed,
   validatable single-line write is strictly better than an opaque
   program call for this case; collapsing them would throw away the
   validator's ability to range-check, which is the entire safety
   argument for preferring `set_output`.
4. **Leave it adapter-private.** Rejected: the cobot adapter would
   silently do it while URML pretended cobots can't fire tools — the
   exact silent substrate leak the spec-gap loop exists to surface.

## Prior art

ISA/PLC discrete-output instructions; ROS 2 `ur_robot_driver` `SetIO`;
UR RTDE `setStandardDigitalOut`; Franka FCI I/O; OPC UA boolean
variable writes. URML-internal: RFC-0013 (the compose-don't-add
precedent and the `dock`-dilution it avoided), RFC-0015 (the opaque
counterexample that motivates keeping this one typed and bounded), and
RFC-0002 (primitive economy).

## Unresolved questions

- Whether `set_output` is core or profile-gated (industrial/research
  only — recommended).
- Analog vs. digital in one primitive vs. two.
- Whether `pulse_ms` belongs in v0.1 or is a follow-up.

Each is settle-able before Open → Accepted.

## Implementation note

Draft only — no code lands until the maintainer decides. The
`urml-cobot-runtime` ships against the frozen Protocol with **no** raw
I/O exposed (only `grasp`/`release`); the gap is recorded in its
`SPEC-GAPS.md`, not worked around. If accepted, landing is one
coordinated change (Layer 1 + Layer 2 + Layer 4 + validator +
conformance + the UR/Franka/OPC UA/ROS 2 mappings) — multi-layer,
hence correctly an RFC.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] If this RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test).
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
