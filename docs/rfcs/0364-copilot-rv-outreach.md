---
rfc: 0364
title: Copilot (stream-based runtime verification) integration, request for comment from the Copilot maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-04
updated: 2026-06-04
state: Draft
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

# RFC-0364: Copilot runtime-verification integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`Copilot-Language/copilot`](https://github.com/Copilot-Language/copilot), a
stream-based hard-real-time runtime-verification language embedded in Haskell
that generates provably hard-real-time C monitors. It **requests review and
feedback from the Copilot maintainers**.

URML performs **static** validation of intent before any actuator moves: an
English sentence becomes a typed Layer-2 primitive, the validator's passes
check it against a Layer-1 capability manifest and an active safety envelope,
and only an admissible program is dispatched. Runtime verification operates at
the **complementary** point: it monitors safety properties **during**
execution. URML composes **with** a monitor, it does not replace one. URML's
safety envelope is a set of declared properties (geofence, occupancy,
velocity and altitude bounds, link-loss behavior); a runtime monitor enforces
those properties at runtime while URML rejects inadmissible intent before
dispatch.

Copilot is the deployment-grade end of that composition. Its specifications
compile to hard-real-time C monitors fit for aerospace use, which is exactly
the artifact a URML-governed robot would run alongside the validated program.
The honest division of labor: URML is static and pre-dispatch; Copilot is the
generated runtime guard.

## Motivation

Copilot's lineage (NASA Langley and Galois) and its hard-real-time guarantee
make it the strongest existing target for the runtime side of URML's safety
story:

1. **It closes the half URML deliberately does not own.** URML's contract ends
   at dispatch: a program that violates the declared envelope is rejected
   statically, before motion. It cannot observe the running system. A monitor
   watches the executing system against the same declared properties. Copilot
   generates that monitor, so the static check and the runtime check govern one
   coherent set of properties from two sides.
2. **Its specifications are the runtime shadow of a URML envelope.** A URML
   safety envelope ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)
   section 1.2) declares geofence, occupancy, velocity and altitude limits, and
   link-loss behavior ([RFC-0006](0006-connectivity-and-link-loss.md)). Each is
   a property a Copilot stream specification can express over sampled signals.
   The envelope says what must hold; a Copilot monitor watches that it holds.
3. **Hard-real-time output suits the substrate.** A robot guard must run with
   bounded time and memory. Copilot generates C with that property, which is the
   deployment grade a real on-robot monitor needs. URML stays substrate-neutral
   above it; Copilot produces the concrete guard.
4. **It grounds the static / runtime boundary cleanly.** Drawing the line at
   "URML declares the property and emits the signals, Copilot generates the C
   monitor that watches them" keeps each tool at its own altitude. URML adds no
   runtime-verification engine of its own; it reuses the deployment-grade one.

Repo at [`Copilot-Language/copilot`](https://github.com/Copilot-Language/copilot)
(about 829 stars, Issues enabled, not archived, active, last push 2026-05-08).
Origin: NASA Langley / Galois lineage (United States); passes US-federal default
policy ([RFC-0004](0004-compliance-policy.md)).

## Detailed design

### URML safety-envelope to Copilot mapping (illustrative, no code in this RFC)

| URML concept | Maps to Copilot concept |
|---|---|
| Safety-envelope property (declared, Layer-1 section 1.2) | A monitored stream property in a Copilot specification |
| Geofence / occupancy bound | A predicate over sampled pose and occupancy streams |
| Velocity / altitude limit | A bound predicate over the sampled velocity / altitude stream |
| Link-loss rule ([RFC-0006](0006-connectivity-and-link-loss.md)) | A temporal property over a link-liveness stream (outage tolerance as a time bound) |
| URML signal emission (validated program publishes envelope-relevant signals) | The input streams a Copilot monitor samples |
| Monitor verdict | A Copilot trigger the surrounding system consumes (URML stays above it) |
| Validator passes (static, pre-dispatch) | Out of Copilot's scope by design; the complementary half |

### Queued Spec RFC gaps (not proposed here)

The mapping surfaces two spec gaps. **They are not proposed in this Outreach
RFC**; they are flagged as queued Spec RFCs for separate follow-up.

1. **A monitorable-property / temporal-logic spec on the safety envelope.** The
   envelope today declares bounds and a link-loss rule; it does not carry a
   formal, monitorable temporal-logic statement of the properties a runtime
   monitor should watch. A future Spec RFC could attach such a property spec to
   the envelope so a monitor generator has a normative source.
2. **A linkage from a URML behavior or envelope to a generated monitor.** There
   is no declared seam from a URML envelope (or a Layer-3 behavior,
   [`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md))
   to a generated monitor artifact. A future Spec RFC could define that linkage
   so the static and runtime halves reference one property set.

### Compatibility notes

- **Engagement repo.** [`Copilot-Language/copilot`](https://github.com/Copilot-Language/copilot):
  a stream-based hard-real-time runtime-verification language embedded in
  Haskell, generating hard-real-time C monitors.
- **Origin / policy.** United States (NASA Langley / Galois lineage). Passes
  US-federal default policy; runtime verification carries no provenance gate.
- **Relationship.** Open-source; the relationship is cross-citation and runtime
  composition, not vendoring. URML would not embed Copilot; a URML-governed
  deployment would run a Copilot-generated monitor alongside the validated
  program.
- **Substrate-neutrality.** A monitor generated from a declared URML property is
  not ROS-shaped; the same envelope property maps to a monitor on a PX4 or
  zero-ROS runtime.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The monitorable-property spec and the
  envelope-to-monitor linkage are queued Spec RFCs.
- Reference runtime: no change in this RFC. A Copilot mapping would lower a
  declared envelope property to a Copilot stream specification and run the
  generated C monitor beside the validated program; the validator's
  static role is unchanged.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, envelope,
fixture, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Two-spec dependency.** A real envelope-to-Copilot path depends on the two
  queued Spec RFCs (a monitorable-property spec and the monitor linkage). Until
  those land, the composition is described, not shipped.
- **Boundary discipline.** Keeping URML strictly static and pre-dispatch while
  Copilot owns the runtime guard is a line that must be defended on every future
  PR; the temptation to absorb runtime checks into the validator would blur both
  tools' altitudes.

## Alternatives considered

1. **Build a runtime-verification engine inside URML.** Rejected. It would
   duplicate a mature, aerospace-grade tool, pull a runtime concern into a
   static layer, and violate the project's prefer-composition discipline. URML's
   value is the static intent and envelope layer; the runtime guard is a
   complementary artifact, not a feature to absorb.
2. **Treat the safety envelope as runtime-only and drop the static check.**
   Rejected. The static pre-dispatch check is URML's core safety boundary and
   must never be weakened. The point is that static and runtime checks compose;
   neither replaces the other.
3. **Target a higher-level monitor generator first and skip Copilot.** Rejected
   as the first move. Copilot is the deployment-grade C generator that a
   higher-level generator (RFC-0365, Ogma) itself builds on, so engaging Copilot
   establishes the runtime-output layer the rest of the wave references.

## Prior art

- [RFC-0006 (connectivity and link-loss)](0006-connectivity-and-link-loss.md):
  the existing declared safety contract a runtime monitor would watch; the
  closest in-repo precedent for an envelope property with runtime consequence.
- [RFC-0004 (compliance policy)](0004-compliance-policy.md): the optional-block,
  static-check posture this engagement composes with at runtime.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance-listing and honest-limit norms applied here.
- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  related safety-and-airspace engagement at the declared-constraint altitude.
- Sibling Move #28 RFCs: RFC-0362 (RTAMT, the wave anchor) and RFC-0363
  (Reelay), the other runtime-verification targets in this wave.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md):
  the safety-envelope and behavior surfaces this engagement exercises.

## Unresolved questions

For the Copilot maintainers:

1. **Property mapping.** Does a URML safety-envelope property (a geofence,
   velocity, altitude, or link-loss bound) map naturally to a Copilot stream
   specification, or is there a property class URML would need to reshape before
   it expresses cleanly?
2. **Boundary placement.** Is "URML declares the property and emits the input
   signals, Copilot generates the C monitor that watches them" the right seam,
   and is there a stable interface for feeding sampled signals into a generated
   monitor?
3. **Hard-real-time guarantees.** What would a URML-governed deployment need to
   declare (signal rates, sampling periods, bounded inputs) for Copilot's
   hard-real-time guarantee to hold over an envelope-derived monitor?
4. **Verdict feedback.** When a generated monitor's trigger fires at runtime,
   what is the idiomatic way to surface that verdict so a surrounding
   URML-governed system can react without URML reaching into the runtime layer?
5. **Conformance listing.** Would Copilot consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0364 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`Copilot-Language/copilot`](https://github.com/Copilot-Language/copilot)
pointing at this RFC (Issues are enabled on the repo). If the maintainers prefer
another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 829 stars, not archived, Issues
      enabled, active, last push 2026-05-08).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, two-spec dependency, boundary discipline).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; the monitorable-property spec and the
      envelope-to-monitor linkage are flagged as queued Spec RFCs, not proposed
      here.
- [x] Provenance: US (NASA Langley / Galois lineage); default policy passes; no
      provenance gate at the runtime-verification layer.
- [x] CLAUDE.md compliance check passed (static / pre-dispatch boundary kept;
      the safety boundary is strengthened by composition, not weakened; runtime
      verification is complementary, not absorbed; no license-ask, no vendoring).
