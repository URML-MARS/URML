---
rfc: 0015
title: Control-program invocation — calling a named substrate program
author: Ido Yahalomi (greenvh@gmail.com)
state: Open
created: 2026-05-19
updated: 2026-05-29
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

# RFC-0015: Control-program invocation — calling a named substrate program

## Summary

OPC UA Robotics cells (and PLC/fieldbus substrates generally) expose
capability as *named programs and methods* — "run `PickCycle`", "call
`HomeAll`", "execute ControlProgram `Job17` with `tray=red`". URML has
no way to say "invoke the substrate's named program P with arguments".
This RFC is filed as a **Draft for maintainer decision** by the spec-gap
loop (RFC-0014): the `urml-opcua-runtime` build surfaced this need, and
rather than bend a primitive to fit it, the gap is written down. It
proposes — for discussion, not yet accepted — a single new Layer-2
primitive, `call_program`, with a deliberately narrow contract.

## Motivation

The OPC UA Robotics companion specification models a robot's exposed
behavior as method nodes on an object. `swap_tool` (RFC-0013)
legitimately rides `send_docking_goal` because a tool change *is* a
station service. A general "run the cell's `Job17` program", however,
is not a station service, not navigation, not a grasp, and not a
report. It cannot be composed from the existing twelve primitives
because none of them denote "transfer control to a substrate-defined
routine and await its result." Without a primitive, an OPC UA cell's
single most common real-world operation — invoking a commissioned PLC
program — is inexpressible in URML, which directly undercuts the
"one sentence runs on the factory floor" claim.

This is exactly the kind of one-way door RFC-0002 warns about, which is
why it is an RFC and not a silent adapter convenience.

## Detailed design

A single new Layer-2 primitive:

```
call_program:
  name: <Identifier>          # substrate-declared program/method name
  args: { <str>: <scalar> }   # optional literal arguments
  expect: success | value     # optional; default success
  store_as: <Identifier>      # optional; binds the returned value
```

The program `name` MUST be declared in the capability manifest (a new
`programs:` list under an existing block — the smallest possible schema
addition, e.g. `manifest.programs[].name` with an arg signature) so the
validator can reject an undeclared or mis-typed call before execution,
preserving validate-before-actuate. `call_program` is **opaque by
design**: URML does not model what the program does. That opacity is
the danger and is addressed in Drawbacks.

### Spec changes

- **Layer 2**: add the `call_program` primitive definition + JSON
  Schema.
- **Layer 1**: add an optional `programs:` declaration so a call can be
  capability-checked. (A manifest-schema addition — itself the
  RFC-gated part.)
- **Layer 4**: the NL grammar/prompt-contract gains one verb mapping.

### Validator changes

A new Pass-2 check: `call_program.name` must be a declared program; if
`args`/`store_as` are used, arity/type must match the declared
signature. No change to Passes 1/3/4/5.

### Reference runtime changes

Each runtime maps `call_program` to its native mechanism. **ROS 2
sketch**: call an `action`/`service` by the declared name (or a
`/run_program` action with the name as goal). **Non-ROS sketch (OPC
UA, the motivating case)**: `objects.call_method(nodeid, *args)` — the
`OpcUaAdapter` already has the plumbing, gated behind this RFC. The
acid test passes: the primitive is defined in terms of "a named
substrate routine," not a ROS action.

### Conformance suite changes

A new `conformance/fixtures/industrial/` positive fixture exercising
`call_program` against MockROSAdapter, plus a negative (undeclared
program rejected at Pass 2).

## Backward compatibility

Fully compatible. Additive: a new optional primitive and an optional
manifest block. Every pre-existing program, manifest, and runtime is
unchanged. Pre-v1.0.

## Drawbacks

`call_program` is an opaque escape hatch. Its real danger is that it
becomes the lazy answer to every hard mapping — "just `call_program`"
— hollowing out the substrate-neutral vocabulary that is URML's entire
point. A program invoked this way is unvalidatable beyond its
signature: URML cannot reason about what it moves or whether it
respects the safety envelope. That is a genuine erosion of the
validate-before-actuate guarantee for the duration of the call. Any
acceptance must come with a hard norm ("`call_program` is the
substrate-specific last resort, not a substitute for modelling a
behavior with real primitives") and possibly a profile-level opt-in so
it cannot be used silently in, say, the `home` profile.

## Alternatives considered

1. **Compose from existing primitives.** Rejected: there is no
   composition — no existing primitive denotes "run a substrate-named
   routine." This is why it is a true gap, not a documentation miss.
2. **Overload `send_docking_goal` / `swap_tool`.** Rejected: semantic
   abuse. RFC-0013 put `swap_tool` on the docking path because it *is*
   a station service; a general program call is not, and pretending it
   is would make `dock` mean "anything," which is worse than a new
   primitive.
3. **Keep it adapter-private (no primitive).** Rejected: it would make
   the most common OPC UA operation inexpressible in URML while the
   adapter quietly did it anyway — exactly the silent substrate leak
   the spec-gap loop exists to prevent.
4. **A constrained `call_skill` with a typed catalog instead of opaque
   programs.** Promising but heavier; noted as a possible refinement if
   this RFC advances to Open.

## Prior art

PDDL/behaviour-tree "external action" nodes; AUTOSAR service calls;
ROS 2 actions/services; the OPC UA Robotics `ControlProgram` /
method-node model (the direct motivator). URML-internal: RFC-0013
(`swap_tool` riding `send_docking_goal` — the precedent for *not*
adding a primitive when composition exists, and the contrast that
shows why this case is different) and RFC-0002 (primitive economy).

## Unresolved questions

Resolved on advance to **Open** (2026-05-29), informed by the Kawasaki-Robotics
maintainer endorsement (kurita-taisuke, khi_ros2 issue #9, Q2):

- **Manifest declaration shape for `programs:`** — minimal. Each entry is
  `name` (Identifier), optional `description`, and an optional `args` list of
  `{name, type}` where `type ∈ {string, number, boolean}`. Enough for Pass-2
  arity/type checking; deeper typing is deferred.
- **Core vs profile-gated** — neither, in the profile sense: `call_program` is
  a **manifest-gated** primitive available to any profile, but usable only
  against a manifest that declares the named program. The repo has no
  profile-gate mechanism (profiles are informational in the validator), and
  the manifest-declaration requirement is the real safety gate. A `home`
  manifest that declares no `programs:` cannot use it, which satisfies the
  Drawbacks concern without a new mechanism.
- **Returned value typing** — stays **opaque**. `expect: value` with
  `store_as` binds an opaque `program_result` that no other primitive consumes
  (it cannot be fed to `grasp`/`move_to`/etc.), preserving validate-before-
  actuate. A typed return is the noted future refinement (the `call_skill`
  alternative).

A constrained, typed `call_skill` catalog (alternative #4) remains a possible
future RFC if opaque `call_program` proves too blunt in practice.

## Implementation note

**Landed 2026-05-29** as one coordinated change on advance to Open:

- **Layer 1**: optional `programs:` manifest block (`Program` / `ProgramArg`
  models) — [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)
  §2.8a.
- **Layer 2**: the `call_program` primitive + `CallProgramArgs` —
  [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
  §3.9. Lands additively in the `0.1.x` line, like the RFC-0013 industrial
  primitives (no version-file bump; fully backward compatible).
- **Layer 4**: the verb is auto-derived from the exported schema; a `call_program`
  industrial few-shot was added to the bridge.
- **Validator**: Pass-2 `capability.missing_program` /
  `capability.program_arg_mismatch`; Pass-4 binds an opaque `program_result`.
- **Substrate**: `call_named_program` added to the `ROSAdapter` Protocol and to
  **every** reference adapter. The hermetic `MockROSAdapter`, the
  `IndustrialArmAdapter` family (Kawasaki et al., delegating to the inner
  adapter), and the `OpcUaAdapter` (`objects.call_method`, the motivating case)
  implement it for real; substrates with no named-program mechanism return a
  uniform `not_supported_on_<substrate>` result.
- **Conformance + demo**: `industrial/45_kawasaki_call_program_positive` and
  `industrial/46_call_program_undeclared_rejected`, plus the runnable
  [`examples/industrial/kawasaki-as-program`](../../examples/industrial/) demo
  (hermetic translate→validate→execute with a committed hero SVG).

The substrate-neutrality acid test holds: the OPC UA path
(`objects.call_method`) needs no ROS, and the ROS-2 path is a deployment
subclass binding its driver's program service (e.g. khi_ros2's AS-program
launch). The Kawasaki AS-language binding (RFC-0029 Q2, maintainer-endorsed) is
the headline instance.

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
