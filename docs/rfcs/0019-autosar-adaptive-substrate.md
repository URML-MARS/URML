---
rfc: 0019
title: AUTOSAR Adaptive substrate — binding ara::com to URML
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-20
updated: 2026-06-06
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

**State: Implemented** (2026-06-06). RFC-0015 (`call_program`) and RFC-0016
(`realtime`) have both shipped, so the binding lands: an optional `ara_com`
binding on a declared `program` (the service / instance / method id triple),
plus a Pass-2 check that the triple is complete
(`capability.ara_com_binding_incomplete`). No new primitive; AUTOSAR cyclic
timing uses the `realtime` block as-is. A green `reference/autoware`-style
AUTOSAR adapter that routes `call_program` through the binding is a follow-on.

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

Shipped: Pass-2 (`_check_program_bindings`) requires that a `programs[*]`
with `binding: { kind: ara_com }` declares the full id triple
(`service_id` / `instance_id` / `method_id`), else
`capability.ara_com_binding_incomplete`. The program's `args` remain the
typed argument template a `call_program` is already checked against
(RFC-0015 `capability.program_arg_mismatch`). The id fields are optional in
the schema and required by this check, so an incomplete binding yields a
stable `capability.*` code rather than a generic argument error.

### Reference runtime changes

`urml-autosar-runtime` (the scaffold PR riding this RFC) implements
the frozen Protocol over `ara::com` for nav/measure/report only. When
RFC-0019 + RFC-0015 ratify, the runtime's `call_program` path resolves
through the manifest binding and calls the declared service method.
The opcua-runtime is the structural precedent: that runtime shipped
its frozen-Protocol subset and filed RFC-0015/0016 for what it could
not express; AUTOSAR follows the same pattern.

### Conformance suite changes

Shipped: `industrial/48_autosar_ara_com_positive` invokes an ara::com-bound
program via `call_program` (the manifest declares the full binding triple and
a `realtime` block; the call validates and executes hermetically), and
`industrial/49_autosar_ara_com_incomplete_rejected` proves an incomplete
binding is rejected (`capability.ara_com_binding_incomplete`). Manifests
`autosar_ara_com` / `autosar_ara_com_incomplete`; unit tests in
`test_ara_com_binding.py`.

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

## Resolved / unresolved questions

Resolved on implementation (2026-06-06):

- **`arg_template` shape:** reuses RFC-0015's `programs[*].args` (a list of
  `{name, type}` scalars). The binding adds only the routing triple, not a
  second type system.
- **`instance_id`:** **required** when a binding is present (named instance),
  alongside `service_id` and `method_id`. Find-any-instance can be narrowed in
  later if a real deployment needs it.
- **Events:** deferred. `ara::com` events are waited on (`wait_for` territory);
  no separate binding entry until a real fixture needs it (Alternative 2).

## Implementation note

Shipped as a Layer-1-only slice: the optional `AraComBinding` on the RFC-0015
`Program` model, the Pass-2 `_check_program_bindings` check + the
`capability.ara_com_binding_incomplete` code, two conformance fixtures + their
manifests, unit tests, and the layer-1 §2.8a spec note. No new primitive and no
runtime change: `call_program` already executes (the Mock resolves it by name);
a real AUTOSAR adapter routes through the binding's id triple, which is a
follow-on `reference/autosar-runtime/` PR. AUTOSAR Execution Management timing
uses the `realtime` block (RFC-0016) unchanged.

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
