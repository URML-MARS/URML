---
rfc: 0691
title: Control-program invocation, part 2 — control-handover semantics (RFC-0015 refinement)
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-03
updated: 2026-09-03
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

# RFC-0691: Control-program invocation, part 2 — control-handover semantics (RFC-0015 refinement)

## Summary

[RFC-0015](0015-control-program-invocation.md) added `call_program`, the primitive for invoking a named substrate program. Its model is a call-and-return: transfer control to a substrate routine, await its result, and continue. A Universal Robots maintainer (`urrsk`) reviewing the URML-to-UR mapping ([Universal_Robots_ROS2_Driver discussion #1799](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver/discussions/1799)) showed that on UR, and by extension on many industrial controllers, invoking a named program is not a call inside a running trajectory. It is a **mode handover**: it stops whatever is running, hands the robot to the named program, and the caller reacquires control only afterward. RFC-0015's call-and-return model does not map to that.

This RFC refines RFC-0015 by adding an optional, declared **control-handover semantic** to a program declaration, so the difference between "call and return, control preserved" and "yield control, run, reacquire" is stated in the manifest and checkable before dispatch. It also clarifies argument passing and preconditions for substrates that do not accept in-band arguments. It is a **Draft for maintainer decision**; no schema or validator change lands until it advances.

## Motivation

On UR, sending a program to the secondary interface stops the currently running program. In the ROS 2 case that terminates External Control, and the ROS controllers lose the robot until the program is restarted (the `resend_robot_program` service in headless mode, or the play button otherwise). Named invocation of something installed on the robot is a distinct mechanism again: the Dashboard server (`load <name>.urp`, then `play`) on PolyScope 5, exposed as the ROS 2 dashboard client services, or the REST Robot API on PolyScope X.

So on UR, `call_program` is a mode handover, not a call-and-return with live control. If RFC-0015 assumes call-and-return while ROS control stays live, it does not map. If URML can express "yield control, run the named program, reacquire control", it maps cleanly.

This is not UR-specific. Many PLC and controller substrates treat "run program P" as a mode change that suspends the external command channel for the duration. Modelling only call-and-return quietly assumes the OPC UA method-call shape (the RFC-0015 motivator) is universal. It is not. Leaving the handover implicit in each adapter is exactly the silent substrate leak the RFC-0014 spec-gap loop exists to prevent, so the gap is written down.

Two further constraints the same review surfaced:

- **No in-band argument passing on some substrates.** A UR `.urp` takes no arguments; values are passed out of band via I/O, RTDE input registers, installation variables, or by generating script text with values inlined. RFC-0015's `call_program.args` (in-band literals) has no target on such a program.
- **Mode preconditions.** On e-Series and newer, the robot must be in remote-control mode to accept remote script at all. A named-program call can be inadmissible for a reason outside the call itself.

## Detailed design

All additions are optional and default to RFC-0015's current behavior, so every existing manifest and program is unaffected.

### 1. `control_handover` on the program declaration (Layer 1)

Add an optional field to each entry in the manifest `programs:` list (RFC-0015 §Layer 1):

```
programs:
  - name: Job17
    control_handover: call_return | mode_handover   # optional; default call_return
    args_inband: true | false                        # optional; default true
    requires: [ <precondition token> ]               # optional; e.g. remote_control
    args: [ { name: tray, type: string } ]           # as RFC-0015
```

- **`control_handover: call_return`** (default) is the RFC-0015 semantic: the substrate runs the named program and returns; the caller's control context is preserved. The OPC UA `objects.call_method` motivator is this.
- **`control_handover: mode_handover`** declares that invoking the program **yields control**: any live external control (for example ROS External Control on UR) is suspended or stopped, the named program runs to completion, and control is reacquired afterward. The `call_program` step is then understood as a control boundary, not an inline call.

### 2. `args_inband` and out-of-band arguments

`args_inband: false` declares that the substrate cannot receive the `call_program.args` as literals passed into the call (the UR `.urp` case). When it is false, the validator rejects a `call_program` that supplies `args`, and the manifest is expected to document the out-of-band path (I/O, registers, installation variables, inlined script) in the program `description`. This keeps URML honest: it does not pretend to pass arguments the substrate cannot receive.

### 3. `requires` preconditions

An optional `requires` list of substrate-neutral precondition tokens (initial set: `remote_control`) lets a program declare a mode precondition. The validator surfaces it in the audit; enforcement of the live mode is the adapter's job (URML cannot read the pendant), but the declaration means the requirement is visible before dispatch rather than discovered as a runtime failure.

### Spec changes

- **Layer 1**: the `Program` model gains optional `control_handover`, `args_inband`, and `requires`. Purely additive; defaults reproduce RFC-0015.
- **Layer 2**: no new primitive. `call_program` is unchanged; its meaning is refined by the declared handover of the program it names.
- **Validator**: Pass-2 rejects `args` on an `args_inband: false` program (`capability.program_args_out_of_band`); records `control_handover` and `requires` in the audit. A `mode_handover` call is flagged in the audit as a control boundary. A stricter optional check (warn when a `mode_handover` call sits between motion primitives that assume continuous control) is noted as a follow-up, not required for a first landing.
- **Layer 4**: no grammar change; the verb mapping is unchanged.

### Reference runtime changes

Each adapter maps `control_handover`. **UR sketch**: a `mode_handover` named program is the Dashboard `load`/`play` (PolyScope 5, via the ROS 2 dashboard client services) or the REST Robot API (PolyScope X); the adapter suspends External Control, runs the program, and resends the robot program to reacquire control. **OPC UA sketch**: `objects.call_method` stays `call_return`, unchanged. Substrates with no named-program mechanism are unaffected.

### Naming correction carried from the review

RFC-0015's ROS-2 sketch and the RFC-0024 mapping referred to `rtde_control.sendCustomScript(...)`. That is SDU's `ur_rtde`, not the UR `RTDE_Python_Client_Library` or the UR Client Library the ROS 2 driver builds on. The UR-stack path for sending *anonymous* script is the secondary interface (port 30002), and on ROS 2 the `urscript_interface` node via `/urscript_interface/script_command`. That anonymous-script path is explicitly **not** `call_program`: it ships opaque raw script, which is the opaque-escape-hatch failure mode RFC-0015 §Drawbacks warns against, one step worse. `call_program` remains named-invocation only. (The RFC-0024 doc was already corrected; this records the rule at the spec level.)

## Backward compatibility

Fully compatible. All three fields are optional; their defaults reproduce RFC-0015 exactly. Every existing `programs:` declaration, manifest, and adapter is unchanged. Pre-v1.0.

## Drawbacks

- It adds surface to `call_program`, already the spec's opaque escape hatch. The mitigation is that the additions make the escape hatch **more** honest, not less: a mode handover is a genuine safety event (external control is suspended), and declaring it is better than an adapter doing it silently.
- `mode_handover` cannot be fully validated: URML cannot prove the named program respects the safety envelope during the handover, and the envelope guarantee is suspended for that interval. The RFC-0015 hard norm still applies, and the audit now at least marks the boundary.
- `requires` is advisory (URML cannot read the pendant mode). It is a declaration, not an enforcement, and should be documented as such.

## Alternatives considered

1. **Leave `call_program` as call-and-return only.** Rejected: it does not map to UR, the largest-installed-base collaborative-arm substrate, whose maintainer surfaced the gap directly. Silently ignoring it would repeat the RFC-0015 motivation in reverse.
2. **Handle the handover implicitly in each adapter.** Rejected: the whole point of the spec-gap loop is that substrate behavior which changes the meaning of a URML step is written down, not hidden in an adapter.
3. **A new `yield_control` primitive.** Rejected as heavier: the handover is a property of *which named program* is invoked, so it belongs on the program declaration, not as a separate verb the author has to remember to wrap around every call.
4. **Encode the precondition as an envelope field rather than a program `requires`.** Deferred: `remote_control` is a controller mode, not a safety-envelope bound; keeping it on the program declaration is the tighter fit.

## Prior art

RFC-0015 (`call_program`, the primitive this refines) and RFC-0014 (the spec-gap loop that filed it). The Universal Robots maintainer review on discussion #1799 (`urrsk`) is the direct motivator. UR External Control / Dashboard / RTDE / secondary-interface behavior. The AUTOSAR and OPC UA method-call models are the call-and-return end of the spectrum; the UR mode handover is the other end this RFC adds.

## Unresolved questions

- **Precondition vocabulary.** `remote_control` is the first token. Others (for example a homed/referenced precondition, cf. the igus Robolink DP note) can be added as substrates surface them, or the field can stay a free string set. Maintainer input welcome.
- **Interleaving check strength.** Whether the validator should hard-reject, warn, or only record a `mode_handover` call that sits between primitives assuming continuous control. Proposed: record now, warn later, never silently accept.
- **Companion: RFC-0016 clock authority.** The same review flagged that a cyclic-rate manifest should not hardcode one rate (500 Hz on e-Series / PolyScope X, 125 Hz on CB3) and should declare which clock is authoritative (external-slaved-to-robot-clock being the endorsable pattern). That is a separate refinement to [RFC-0016](0016-realtime-cyclic-manifest-block.md) and is tracked as its own follow-on RFC, not folded in here.

## Implementation note

This RFC is a **Draft**. No schema, validator, or adapter change lands until it advances. On advance it lands additively in the `0.1.x` line like the RFC-0013 / RFC-0015 additions: the three optional `Program` fields, the Pass-2 out-of-band-args check, the audit records for handover and preconditions, and the UR adapter's suspend/run/reacquire mapping. The URML-to-UR RFC (RFC-0024) is updated to reference the handover model once it is accepted.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed and why now.
- [x] The Motivation is grounded in a concrete, named maintainer review, not a hypothetical.
- [x] The Detailed design names every affected spec layer and the reference-runtime mapping; both a non-ROS (OPC UA) and a ROS-2 (UR) sketch are present.
- [x] At least one alternative is genuinely considered (four are).
- [x] Drawbacks are real: the handover suspends the envelope guarantee, and `requires` is advisory only.
- [x] Backward compatibility is honest: additive, defaults reproduce RFC-0015.
- [x] The implementation note explains this is a Draft and what lands on advance.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed compliance (no substrate coupling: the handover is defined substrate-neutrally, with UR and OPC UA as the two ends).
