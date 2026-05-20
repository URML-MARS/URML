---
rfc: 0019
title: AUTOSAR Adaptive substrate — binding ara::com to URML
author: Ido Yahalomi (ido@jacob-ai.com)
state: Draft
created: 2026-05-20
updated: 2026-05-20
supersedes: —
superseded-by: —
---

<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="100%"></a>
</p>

<p align="center">
  A small, opinionated, human-readable language for describing robot intent.
</p>

<p align="center">
  <a href="https://urml.dev"><b>urml.dev</b></a>
</p>

---

# RFC-0019: AUTOSAR Adaptive substrate — binding ara::com to URML

## Summary

AUTOSAR Adaptive is named in the manifesto as a target URML must run on
("URML works everywhere — PX4, AUTOSAR Adaptive, Autoware, OPC UA
Robotics, vendor SDKs"). Its native programming model is `ara::com` —
service-oriented RPC with methods, events, and fields exposed by
service instances, and Execution Management with a declared cyclic
period and watchdog. This RFC is filed as a **Draft for maintainer
decision** by the spec-gap loop (RFC-0014); the `urml-autosar-runtime`
scaffold surfaced it. The proposal introduces **no new Layer-2
primitive**: AUTOSAR's "invoke method M on service S" is the **same
family** as RFC-0015 `call_program`, and its cyclic Execution
Management is the **same gap** as RFC-0016's real-time manifest block.
RFC-0019 is the *binding* layer between AUTOSAR and those two existing
Drafts — never a third proposal.

## Motivation

A bare `urml-autosar-runtime` scaffold can ship the frozen-Protocol
subset (nav/measure/report mapped onto configured `ara::com` service
calls), but it cannot today express the most common AUTOSAR operation:
invoking a named service method on a declared service instance. That
is the same expressiveness gap OPC UA hit and that RFC-0015 already
proposed `call_program` to close. AUTOSAR also has a cyclic timing
contract (period, deadline, watchdog) — the same gap RFC-0016 proposed
to close for OPC UA/fieldbus.

Without writing the binding down, two failure modes follow: (1) every
AUTOSAR runtime quietly invents its own service-call primitive and
diverges, defeating the substrate-neutral vocabulary; (2) the manifest
cannot honestly state the cyclic timing the ECU is commissioned to,
which Layer 1's "faithful description of the hardware" purpose
requires. RFC-0019 writes the binding down so AUTOSAR ships honestly
under existing or accepted RFCs, not under a silent superset.

## Detailed design

**No new primitive.** AUTOSAR-side capability is exposed through two
binding mechanisms that ride existing or pending RFCs:

1. **Service-method invocation** rides **RFC-0015 `call_program`**. A
   service instance + method name + typed arg payload becomes the
   `call_program.name` identifier and `args` payload. The manifest's
   `programs:` list (from RFC-0015) gains an **AUTOSAR binding
   profile** that declares the service id, instance id, method id, and
   the typed arg schema per program — exactly the validator-checkable
   level that keeps `call_program` from being an opaque escape hatch.

2. **Cyclic / Execution Management** rides **RFC-0016**'s `realtime:`
   manifest block. AUTOSAR's `MinimumCycleTime` maps to
   `cyclic_period_ms`; `WatchdogTimeout` maps to `watchdog_ms`; the
   declared `guarantee` defaults to `soft` until a runtime certifies
   `hard` (URML never claims to *enforce* hard real-time; the field is
   descriptive per RFC-0016).

The `urml-autosar-runtime` scaffold landing alongside this RFC ships
the frozen-Protocol subset only: `move_to`/`measure`/`report` mapped
onto configured `ara::com` methods (where each is a single named
service operation, not the general program-call surface). The general
program-call analog returns `not_yet_implemented_pending_rfc_0019_15`
until RFC-0019/RFC-0015 ratify.

### Spec changes

- **Layer 1**: extends RFC-0015's `programs:` model with an optional
  `binding` selector — `binding: ara_com` plus a `service_id` /
  `instance_id` / `method_id` triple and an `arg_template` shape. This
  is the *only* Layer-1 surface that lands with RFC-0019; the
  underlying `programs:` model itself is RFC-0015's responsibility.
- **Layer 2/3/4**: unchanged. No new primitive. `call_program` (when
  RFC-0015 lands) is the verb; RFC-0019 only constrains what its
  manifest declaration may carry.

### Validator changes

When RFC-0019 + RFC-0015 are both accepted, Pass-2 gains one
constraint: a `programs[*]` with `binding: ara_com` must declare the
full id triple and a non-empty `arg_template`, and any `call_program`
referencing it must satisfy the template. Until both ratify, the
validator change is nil and the AUTOSAR scaffold exposes only the
frozen-Protocol subset.

### Reference runtime changes

`urml-autosar-runtime` (the scaffold PR riding this RFC) implements
the frozen Protocol over `ara::com` for nav/measure/report only. When
RFC-0019 + RFC-0015 ratify, the runtime's `call_program` path resolves
through the manifest binding and calls the declared service method.
The opcua-runtime is the structural precedent: that runtime shipped
its frozen-Protocol subset and filed RFC-0015/0016 for what it could
not express; AUTOSAR follows the same pattern.

### Conformance suite changes

The scaffold's `industrial/<n>_autosar_ecu_positive.yaml` exercises
nav + report only (no service invocation), so it is green today
without RFC-0019 acceptance. A future `<n+1>_autosar_service_call_positive`
fixture exercises the binding once both RFCs ratify; deliberately not
filed in this RFC.

## Backward compatibility

Fully compatible. The Layer-1 `binding: ara_com` extension is optional
and namespaced under RFC-0015's `programs:` model; if RFC-0015 is
rejected, RFC-0019 is moot and no schema lands. No existing manifest,
program, runtime, or fixture changes.

## Drawbacks

This RFC's value depends on RFC-0015's acceptance — if RFC-0015 lands
as something other than `call_program`, RFC-0019's binding shape has
to follow. That's a real coupling cost: two RFCs in a sequencing
chain, with RFC-0020 (Autoware) potentially adding a third sibling
under RFC-0015. The mitigation is to keep RFC-0019 minimal — *just*
the binding, no new primitive — so it can be amended cheaply if
RFC-0015's surface evolves during its own review. A second drawback:
declaring service ids / instance ids in URML's manifest pulls AUTOSAR
implementation detail into a substrate-neutral document; the
counter-argument is that this is precisely how OPC UA node ids already
land in deployment config under RFC-0015, so the precedent is
consistent rather than novel.

## Alternatives considered

1. **Define a new `invoke_service` Layer-2 primitive instead of
   binding `call_program`.** Rejected: it duplicates RFC-0015's
   surface — two opaque escape hatches where one suffices — and makes
   `call_program` mean "everything except service calls," which is
   harder to reason about than one verb plus a binding declaration.
2. **Treat `ara::com` events as a separate primitive (`subscribe_event`).**
   Rejected for v0.1: events are *waited on*, which is `wait_for`
   territory; a separate primitive splits an existing well-understood
   verb. The binding may add an `events:` list under the service
   declaration later if a real fixture needs it.
3. **Leave AUTOSAR adapter-private (no RFC).** Rejected: the OPC UA
   precedent is the rule — when a substrate exposes something the
   frozen Protocol cannot express, that gap goes to an RFC, not into
   silent adapter code. Adopting AUTOSAR without writing the binding
   down would re-invent the bypass the RFC-0014 spec-gap loop
   explicitly prevents.

## Prior art

`ara::com` itself (the AUTOSAR Adaptive Platform Communication
Management spec); the AUTOSAR Execution Management cyclic timing
contract; ROS 2 service/action invocation; OPC UA Robotics method
nodes (the closest parallel — RFC-0015 was filed against exactly this
shape). URML-internal: RFC-0015 (the primitive RFC-0019 binds to),
RFC-0016 (the cyclic-timing manifest block RFC-0019 cross-refs),
RFC-0013 (the precedent for `swap_tool` riding `send_docking_goal`
when a substrate operation maps cleanly to an existing path —
RFC-0019 makes the same compositional choice for ara::com method
calls rather than inventing a new verb).

## Unresolved questions

- The exact `arg_template` shape (JSON Schema fragment? a small URML
  type DSL?). Inherits from RFC-0015's `programs:` typing decision.
- Whether `instance_id` should be optional (find-any-instance) or
  required (named instance). Lean: required for v0.1, narrowed later.
- Whether events warrant their own binding entry now or wait for a
  real fixture (per Alternative 2 above).

Each is small enough to settle before Open → Accepted.

## Implementation note

This is a Draft-only RFC. A companion PR `feat/autosar-runtime-scaffold`
lands the runtime against the frozen-Protocol subset (nav/measure/report
over `ara::com`); that PR's `SPEC-GAPS.md` cross-refs RFC-0019, RFC-0015,
and RFC-0016 and does not invent any primitive. If RFC-0019 + RFC-0015
both ratify, a follow-up PR adds the `call_program` resolution path
through the AUTOSAR binding plus a conformance fixture exercising it.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete use case, not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component.
- [x] At least one alternative is genuinely considered (not a strawman).
- [x] Drawbacks are listed; at least one of them is a real downside, not a humblebrag.
- [x] Backward compatibility is honest about what breaks.
- [x] If this RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test). — **N/A: this RFC adds no Layer-2 primitive**; AUTOSAR's service invocation is filed as a *binding* under RFC-0015 `call_program`, not as a new primitive. The cross-reference is the substantive content.
- [x] The implementation note explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it.
