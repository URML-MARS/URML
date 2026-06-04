---
rfc: 0365
title: Ogma (runtime-monitor code generation) integration, request for comment from the Ogma maintainers
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

# RFC-0365: Ogma runtime-monitor code-generation integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's tool, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`nasa/ogma`](https://github.com/nasa/ogma), a NASA tool that generates
runtime-monitoring applications from formal requirements, producing Copilot
monitors ([RFC-0364](0364-copilot-rv-outreach.md)) and integrations for
frameworks including ROS and cFS. It **requests review and feedback from the
Ogma maintainers**.

URML performs **static** validation of intent before any actuator moves: an
English sentence becomes a typed Layer-2 primitive, the validator's passes
check it against a Layer-1 capability manifest and an active safety envelope,
and only an admissible program is dispatched. Runtime verification operates at
the **complementary** point: it monitors safety properties **during**
execution. URML composes **with** a monitor, it does not replace one. URML's
safety envelope is a set of declared properties; a runtime monitor enforces
them at runtime while URML rejects inadmissible intent before dispatch.

Ogma is the closest existing tool to the path a URML safety envelope wants
downstream: a route from a declared requirement to a generated,
framework-integrated monitor. Ogma takes formal requirements, emits Copilot,
and already targets ROS, which URML targets too. The honest, exciting fit: a
URML safety envelope could become an Ogma input, and the monitor Ogma generates
would run alongside the validated program. URML stays the intent and envelope
declaration; Ogma generates the monitor.

## Motivation

Ogma sits exactly where URML's safety story points downstream, and it already
solves the requirement-to-monitor problem URML does not want to solve itself:

1. **It turns a declared requirement into a deployed monitor.** URML declares
   safety-envelope properties ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)
   section 1.2): geofence, occupancy, velocity and altitude bounds, link-loss
   behavior ([RFC-0006](0006-connectivity-and-link-loss.md)). Ogma turns formal
   requirements into running monitors. A URML envelope lowered to an Ogma input
   would yield a monitor that watches the declared properties at runtime, which
   is the half URML deliberately does not own.
2. **It already targets the substrate URML targets.** Ogma generates ROS
   integrations (and cFS). URML's first reference runtime is ROS 2. A monitor
   Ogma generates for ROS could run beside a URML-validated program on the same
   substrate with no new bridge to invent.
3. **It builds on Copilot, the deployment-grade output layer.** Ogma emits
   Copilot monitors, and RFC-0364 engages Copilot directly. Engaging Ogma adds
   the requirement-to-monitor front end above that output layer, so the wave
   covers both the generator and the language it generates.
4. **It keeps the static / runtime boundary honest.** Drawing the line at "URML
   declares the property, Ogma generates the monitor, the monitor watches the
   running system" leaves URML entirely static and pre-dispatch. URML adds no
   monitor generator of its own; it reuses NASA's.

Repo at [`nasa/ogma`](https://github.com/nasa/ogma) (about 564 stars, Issues
enabled, not archived, active, last push 2026-06-02). Origin: NASA (United
States); passes US-federal default policy ([RFC-0004](0004-compliance-policy.md)).

## Detailed design

### URML safety-envelope to Ogma mapping (illustrative, no code in this RFC)

| URML concept | Maps to Ogma concept |
|---|---|
| Safety-envelope property (declared, Layer-1 section 1.2) | A formal requirement Ogma consumes as input |
| Geofence / occupancy / velocity / altitude bound | A requirement over sampled state, lowered to a generated monitor |
| Link-loss rule ([RFC-0006](0006-connectivity-and-link-loss.md)) | A temporal requirement over link liveness (outage tolerance as a time bound) |
| URML reference runtime (ROS 2) | Ogma's ROS integration target; the monitor runs on the same substrate |
| Generated monitor (Ogma emits Copilot) | The runtime guard running beside the URML-validated program |
| Monitor verdict | A runtime signal the URML-governed system consumes (URML stays above it) |
| Validator passes (static, pre-dispatch) | Out of Ogma's scope by design; the complementary half |

### Queued Spec RFC gaps (not proposed here)

The mapping surfaces two spec gaps. **They are not proposed in this Outreach
RFC**; they are flagged as queued Spec RFCs for separate follow-up.

1. **A monitorable-property / temporal-logic spec on the safety envelope.** The
   envelope today declares bounds and a link-loss rule; it does not carry a
   formal, monitorable requirement an Ogma-style generator could consume
   directly. A future Spec RFC could attach such a property spec to the envelope
   so a monitor generator has a normative source to lower from.
2. **A linkage from a URML behavior or envelope to a generated monitor.** There
   is no declared seam from a URML envelope (or a Layer-3 behavior,
   [`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md))
   to a generated monitor artifact and back to a verdict. A future Spec RFC
   could define that linkage so the static and runtime halves reference one
   property set.

### Compatibility notes

- **Engagement repo.** [`nasa/ogma`](https://github.com/nasa/ogma): a NASA tool
  that generates runtime-monitoring applications from formal requirements,
  producing Copilot monitors and integrations for ROS and cFS.
- **Origin / policy.** United States (NASA). Passes US-federal default policy;
  runtime monitor generation carries no provenance gate.
- **Relationship.** Open-source; the relationship is cross-citation and runtime
  composition, not vendoring. URML would not embed Ogma; a URML-governed
  deployment would feed a declared envelope to Ogma and run the generated
  monitor alongside the validated program.
- **Substrate-neutrality.** Ogma targets ROS and cFS; a URML envelope lowered to
  an Ogma input is not ROS-shaped, so the same declared property can drive a
  monitor on a PX4 or zero-ROS runtime.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The monitorable-property spec and the
  envelope-to-monitor linkage are queued Spec RFCs.
- Reference runtime: no change in this RFC. An Ogma mapping would lower a
  declared envelope to an Ogma input and run the generated (Copilot-based)
  monitor beside the validated program on the ROS 2 runtime; the validator's
  static role is unchanged.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, envelope,
fixture, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Two-spec dependency.** A real envelope-to-Ogma path depends on the two
  queued Spec RFCs (a monitorable-property spec and the monitor linkage). Until
  those land, the composition is described, not shipped.
- **Input-format uncertainty.** Ogma accepts specific input forms (FRET-style
  requirements, a structured spec file). Whether a URML envelope lowers cleanly
  to one of them is exactly the open question below; the fit may need a
  translation step URML does not own.

## Alternatives considered

1. **Engage only Copilot and skip the generator layer.** Rejected. Copilot
   (RFC-0364) is the output language; Ogma is the requirement-to-monitor front
   end that already integrates with ROS. Engaging both covers the full path from
   a declared property to a deployed, framework-integrated monitor, which is
   what a URML envelope wants downstream.
2. **Build a URML-native monitor generator.** Rejected. It would duplicate a
   mature NASA tool, pull a runtime concern into a static layer, and break the
   prefer-composition discipline. URML's value is the intent and envelope
   declaration; the generator is a complementary tool to reuse.
3. **Lower URML envelopes straight to ROS monitor code, bypassing Ogma.**
   Rejected. Hand-rolling ROS monitor code would be substrate-coupled and would
   forgo the formal-requirement provenance Ogma carries. Targeting Ogma keeps
   the path through a verified generator and keeps URML substrate-neutral above
   it.

## Prior art

- [RFC-0364 (Copilot runtime verification)](0364-copilot-rv-outreach.md): the
  output language Ogma generates; the sibling engagement this one builds on.
- [RFC-0006 (connectivity and link-loss)](0006-connectivity-and-link-loss.md):
  the existing declared safety contract a generated monitor would watch.
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

For the Ogma maintainers:

1. **Input format.** What input does Ogma expect (FRET-style requirements, a
   structured spec file, another form), and could a URML safety envelope be
   lowered to it, or does the gap need a translation step?
2. **ROS-integration boundary.** Ogma generates ROS integrations and URML's
   first reference runtime is ROS 2. Is "URML declares the envelope, Ogma
   generates the ROS monitor, the monitor runs beside the validated program" the
   right boundary?
3. **Verdict feedback.** When a generated monitor reaches a verdict at runtime,
   what is the idiomatic way to surface it so a URML-governed system can react
   without URML reaching into the runtime layer?
4. **Property coverage.** Which envelope properties (geofence, velocity,
   altitude, link-loss timing) lower most naturally to an Ogma requirement, and
   which would need reshaping before they express cleanly?
5. **Conformance listing.** Would Ogma consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0365 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`nasa/ogma`](https://github.com/nasa/ogma) pointing at this RFC (Issues are
enabled on the repo). If the maintainers prefer another venue, URML will move
the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 564 stars, not archived, Issues
      enabled, active, last push 2026-06-02).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, two-spec dependency, input-format
      uncertainty).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; the monitorable-property spec and the
      envelope-to-monitor linkage are flagged as queued Spec RFCs, not proposed
      here.
- [x] Provenance: US (NASA); default policy passes; no provenance gate at the
      monitor-generation layer.
- [x] CLAUDE.md compliance check passed (static / pre-dispatch boundary kept;
      the safety boundary is strengthened by composition, not weakened; Ogma
      builds on Copilot, RFC-0364, and the coupling is referenced; no
      license-ask, no vendoring; substrate-neutral above ROS / cFS).
