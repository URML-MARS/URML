---
rfc: 0363
title: Reelay (runtime verification monitors) integration, request for comment from the Reelay maintainers
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

# RFC-0363: Reelay integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`doganulus/reelay`](https://github.com/doganulus/reelay), a header-only C++
library and toolset that builds efficient runtime monitors from temporal-logic
and timed-automata specifications (Metric Temporal Logic and past-time MTL). It
**requests review and feedback from the Reelay maintainers**.

URML performs static validation of robot intent before any actuator moves. A
validated English sentence becomes a typed Layer-2 primitive, the validator
checks it against the robot's capability manifest (Pass 2) and the active safety
envelope (Pass 3), and only an admissible program is dispatched. Runtime
verification operates at the complementary point in the lifecycle: it monitors
temporal-logic and safety properties during execution. URML composes with a
runtime monitor; it does not replace one.

Reelay is the runtime-monitor implementation that could enforce a URML envelope
property on the robot. URML's safety envelope is in effect a set of declared
properties (a geofence, an occupancy bound, a velocity or altitude limit, a
link-loss contract). URML rejects intent that cannot satisfy those properties
before dispatch. A Reelay monitor, built from a temporal-logic specification of
the same property, could enforce it at runtime, with the embedded and real-time
emphasis a header-only C++ library brings to on-robot deployment. URML is static
and pre-dispatch; Reelay is runtime; together they cover the lifecycle.

This RFC is the deployment-side complement to the wave anchor RFC-0362 (RTAMT,
STL in Python). RTAMT is the reference STL specification and monitoring library;
Reelay emphasizes past-time MTL and efficient C++ monitors suited to deployment.
URML engages both because the static-to-runtime composition is the same; the
runtime half differs in language, temporal fragment, and deployment target.

## Motivation

Reelay supplies the runtime-monitor implementation URML's safety envelope can
point at. The envelope today declares limits the validator enforces statically;
it does not yet carry a temporal-logic property a monitor could enforce on the
robot.

1. **It builds efficient monitors from temporal-logic specs.** Reelay compiles
   MTL and past-MTL specifications into monitors. URML declares a safety envelope
   and validates intent against it once, before motion. A Reelay monitor would
   enforce the same envelope property as the robot runs.
2. **Header-only C++ fits the on-robot boundary.** A URML envelope property
   enforced at runtime wants to run where the robot runs, often on a constrained
   target. Reelay's header-only C++ and real-time emphasis are the right shape for
   an on-robot monitor, where a Python library may not fit.
3. **Past-time MTL suits envelope properties.** Many envelope properties are
   bounded-history statements (a velocity that must have stayed under a limit, a
   link that must not have been lost longer than a tolerance per
   [RFC-0006](0006-connectivity-and-link-loss.md)). Past-time temporal logic
   monitors these without unbounded lookahead, which matters for a deployed
   monitor.
4. **It is substrate-neutral.** A temporal-logic monitor reads signals, not a ROS
   topic by name. A URML envelope property compiled to a Reelay specification and
   fed a signal trace works against a ROS 2, PX4, or zero-ROS runtime. The acid
   test holds: the property is engine-independent.

Repo at [`doganulus/reelay`](https://github.com/doganulus/reelay) (about 43
stars, Issues enabled, not archived, active, last push 2026-01-03). Origin:
Dogan Ulus (academic; NATO-allied lineage). Treated as INTL.

## Detailed design

### URML v0.1 safety-envelope mapping (planned `reelay_envelope_cell.yaml` fixture)

| URML field | Maps to Reelay / temporal-logic construct |
|---|---|
| `robot_id`, `description` | Monitored-system identity (carried at the manifest envelope; not a Reelay concept) |
| Envelope velocity / altitude limit (Pass 3) | An MTL predicate over the velocity or altitude signal compiled to a Reelay monitor |
| Envelope geofence containment (Pass 3) | A temporal-logic predicate over position signals asserting containment within the declared region |
| Envelope occupancy / clearance bound (Pass 3) | A predicate over a range or clearance signal asserting a minimum distance has held |
| Link-loss contract ([RFC-0006](0006-connectivity-and-link-loss.md)) | A past-time timed property over a link-health signal: loss bounded in history before the declared failsafe must fire |
| Layer-3 behavior phase (sequence / parallel) | The temporal scope the monitor evaluates over; a window aligned to a behavior step |
| Signal interface (the trace URML would emit) | The named signals a Reelay monitor consumes per timestamp; URML declares the property, the runtime emits the trace |
| Monitor deployment boundary | URML emits the trace and declares the property; the Reelay monitor runs on the robot |

### What URML v0.1 does not yet express

These are **gaps surfaced by the mapping**, flagged as *queued Spec RFCs* for
separate follow-up. **They are not proposed in this Outreach RFC.**

1. **A monitorable-property specification on the safety envelope.** URML's
   envelope declares limits the validator enforces statically; it does not yet
   attach a machine-checkable temporal-logic property (the MTL specification a
   Reelay monitor would consume) to a limit. A future Spec RFC could add an
   optional monitorable-property field so an envelope limit also names its
   runtime-checkable form.
2. **A linkage from a behavior or envelope to an external runtime monitor.** URML
   has no field that points a behavior or envelope at the on-robot monitor that
   enforces its properties, nor a declared signal interface for the trace. A
   future Spec RFC could add an optional monitor-linkage so a deployment can name
   the runtime monitor and the signals it consumes.

### Compatibility notes

- **Vendor org.** [`doganulus`](https://github.com/doganulus) (Dogan Ulus,
  academic).
- **Engagement repo.** [`doganulus/reelay`](https://github.com/doganulus/reelay):
  a header-only C++ library and toolset that builds efficient runtime monitors
  from MTL and past-MTL and timed-automata specifications; active.
- **Origin / policy.** International (academic, NATO-allied lineage). Treated as
  INTL; passes US-federal default policy
  ([RFC-0004](0004-compliance-policy.md)): an open-source monitoring library is
  not a provenance-gated component.
- **License note.** Open-source; URML's relationship is cross-citation and
  runtime composition, not code vendoring.
- **Substrate-neutrality.** A temporal-logic monitor reads signals, not a
  substrate; an envelope property monitored by Reelay works against a ROS 2, PX4,
  or zero-ROS trace with no change to the property.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The monitorable-property specification
  and the monitor-linkage are queued Spec RFCs.
- Reference runtime: no change in this RFC. A mapping would compile a declared
  envelope property to a Reelay specification and emit the matching signal trace;
  the planned `reelay_envelope_cell.yaml` fixture would document the property,
  the signal interface, and the on-robot monitor boundary hermetically.
- Conformance: no change. An on-robot monitor sits at runtime, below URML's
  static conformance surface ([RFC-0014](0014-substrate-conformance.md)).

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, envelope,
fixture, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Two-end mismatch.** URML reasons at author and dispatch time over declared
  intent; Reelay reasons at runtime over signal traces on the robot. The mapping
  is honest that the two meet only at the shared property, not in a single
  execution path.
- **Deployment-boundary complexity.** Emitting a faithful signal trace from a
  runtime and running the monitor on a constrained target adds integration work
  the RFC does not yet solve. The mapping is described at the property and
  signal-interface altitude to keep that boundary explicit.

## Alternatives considered

1. **Engage only RTAMT and skip Reelay.** Rejected. RTAMT (RFC-0362) is the STL
   specification and Python-monitoring reference; Reelay covers the embedded and
   real-time deployment target with header-only C++ and past-time MTL. The runtime
   half of the composition has more than one shape, and URML benefits from both
   viewpoints.
2. **Build URML's own on-robot monitor.** Rejected. Efficient runtime monitoring
   from temporal-logic specs is exactly what Reelay already does well;
   reimplementing it inside URML would be worse and would couple a monitor to
   URML's release cycle. Composition is the on-ethos choice.
3. **Embed MTL syntax directly in the URML envelope schema now.** Rejected as
   premature. Attaching a temporal-logic property to the envelope is a normative
   spec change that deserves its own Spec RFC with the runtime-verification
   community's input, not a quiet addition folded into an outreach thread.

## Prior art

- [RFC-0362 (RTAMT outreach)](0362-rtamt-outreach.md): the Move #28 wave anchor;
  the STL and Python end of the same static-to-runtime composition.
- [RFC-0006 (connectivity and link-loss)](0006-connectivity-and-link-loss.md):
  the link-loss contract that reads most naturally as a past-time timed property.
- [RFC-0004 (compliance policy)](0004-compliance-policy.md): the static-policy
  evaluation URML already performs before dispatch, the pattern a runtime monitor
  complements.
- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  related work on declared constraints that a runtime layer enforces.
- Sibling Move #28 RFCs: RFC-0364 (Copilot), RFC-0365 (Ogma),
  RFC-0371 (MoonLight).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) (section 1.2,
  the manifest-vs-envelope boundary) and
  [`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md): the
  envelope and behavior surfaces this engagement exercises.

## Unresolved questions

For the Reelay maintainers:

1. **Envelope-to-specification mapping.** Could a URML safety-envelope property (a
   velocity bound, a geofence containment, an occupancy clearance) map to a Reelay
   specification a monitor enforces? Is there a property class where the
   translation is clean and one where it is not?
2. **On-robot monitor-deployment boundary.** If URML emits the trace and declares
   the property and Reelay runs the monitor on the robot, what does the monitor
   expect at the boundary (signal naming, time model, sampling) so the trace is
   faithful?
3. **Past-time vs future-time.** For envelope properties, is past-time MTL the
   right fragment (bounded-history statements over what must have held), and where
   would a future-time property be needed instead?
4. **Real-time and footprint.** For a constrained on-robot target, what compute
   and memory envelope should URML assume a Reelay monitor occupies when it
   decides what to emit and how often?
5. **Conformance listing.** Would Reelay consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md)) as a
   composing runtime-verification target?
6. **Anything else.**

## Implementation note

RFC-0363 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`doganulus/reelay`](https://github.com/doganulus/reelay) pointing at this RFC
(Issues are enabled on the repo). If the maintainers prefer another channel,
URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 43 stars, not archived, Issues enabled,
      active, last push 2026-01-03).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, two-end mismatch, deployment-boundary
      complexity).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; envelope gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: international academic (NATO-allied lineage), INTL; default
      policy passes for an open-source monitoring library.
- [x] CLAUDE.md compliance check passed (substrate-neutral; a temporal-logic
      monitor reads signals, the same property monitors a ROS 2, PX4, or zero-ROS
      trace; URML composes with the monitor, does not replace it).
