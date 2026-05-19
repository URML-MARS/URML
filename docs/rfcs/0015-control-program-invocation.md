---
rfc: 0015
title: Control-program invocation — calling a named substrate program
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

- The exact manifest declaration shape for `programs:` (arg signature
  typing depth).
- Whether `call_program` is core or profile-gated (industrial/research
  only).
- Whether a returned `value` needs a typed schema or stays opaque.

Each is small enough to settle before this RFC moves Open → Accepted.

## Implementation note

Draft only — no code lands from this RFC until the maintainer decides
it. The `urml-opcua-runtime` ships against the frozen Protocol with
program invocation **absent** (the adapter exposes nav/dock/grasp/
measure/report; a program call is not offered). If accepted, landing is
one coordinated change (Layer 1 + Layer 2 + Layer 4 + validator +
conformance + the OPC UA and ROS 2 adapter mappings) — a multi-layer
change, hence correctly an RFC.

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
