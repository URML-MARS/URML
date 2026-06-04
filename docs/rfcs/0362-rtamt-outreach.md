---
rfc: 0362
title: RTAMT (Signal Temporal Logic runtime monitoring) integration, request for comment from the RTAMT maintainers
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

# RFC-0362: RTAMT integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 opens URML's engagement with the safety and runtime-verification layer.
This RFC anchors the wave on [`nickovic/rtamt`](https://github.com/nickovic/rtamt),
the reference open-source Python library for Signal Temporal Logic (STL)
specification and online and offline runtime monitoring. It **requests review
and feedback from the RTAMT maintainers**.

URML performs static validation of robot intent before any actuator moves. A
validated English sentence becomes a typed Layer-2 primitive, the validator
checks it against the robot's capability manifest (Pass 2) and the active safety
envelope (Pass 3), and only an admissible program is dispatched. Runtime
verification operates at the complementary point in the lifecycle: it monitors
temporal-logic and safety properties during execution. URML composes with a
runtime monitor; it does not replace one.

The clean complement is this. URML's safety envelope is in effect a set of
declared properties (a geofence, an occupancy bound, a velocity or altitude
limit, a link-loss contract). URML rejects intent that cannot satisfy those
properties before dispatch. An RTAMT monitor expressed in STL could enforce the
same properties at runtime, catching a violation that only manifests while the
robot moves. URML is static and pre-dispatch; RTAMT is runtime; together they
cover the lifecycle.

## Motivation

RTAMT is the formal vocabulary URML's safety envelope lacks. The envelope today
declares limits the validator enforces statically; it does not yet carry a
machine-checkable temporal-logic statement a monitor could consume.

1. **It is the reference open STL monitoring library.** RTAMT specifies STL and
   monitors traces online and offline. URML declares a safety envelope and
   validates intent against it once, before motion. The two address different
   ends of the same property: URML admits or rejects at author and dispatch time,
   RTAMT watches the same property hold (or fail) as the trace arrives.
2. **An envelope limit is a candidate STL property.** A velocity bound, an
   altitude ceiling, a geofence containment, an occupancy clearance, and the
   link-loss contract of
   [RFC-0006](0006-connectivity-and-link-loss.md) each read naturally as a
   temporal-logic predicate over a signal. The envelope is the declaration; an
   STL formula is the runtime-checkable form of the same statement.
3. **It closes the lifecycle honestly.** URML's static pass cannot catch a sensor
   that drifts, an actuator that overshoots, or a world that changes after
   dispatch. A runtime monitor can. Naming that boundary, and pointing at RTAMT
   for the runtime half, is more honest than implying static validation covers
   execution.
4. **It is substrate-neutral.** STL is defined over signals, not over ROS. A URML
   envelope property compiled to STL and monitored by RTAMT works against a
   ROS 2 trace, a PX4 telemetry stream, or a zero-ROS runtime's signal log. The
   acid test holds: the property is engine-independent.

Repo at [`nickovic/rtamt`](https://github.com/nickovic/rtamt) (about 76 stars,
Issues enabled, not archived, active, last push 2025-11-20). Origin: Dejan
Nickovic and the AIT Austrian Institute of Technology (Austria, NATO-allied).

## Detailed design

### URML v0.1 safety-envelope mapping (planned `rtamt_envelope_cell.yaml` fixture)

| URML field | Maps to RTAMT / STL construct |
|---|---|
| `robot_id`, `description` | Monitored-system identity (carried at the manifest envelope; not an STL concept) |
| Envelope velocity / altitude limit (Pass 3) | A bounded STL predicate over the velocity or altitude signal (`always (v <= v_max)`) |
| Envelope geofence containment (Pass 3) | An STL predicate over position signals asserting containment within the declared region |
| Envelope occupancy / clearance bound (Pass 3) | An STL predicate over a range or clearance signal asserting a minimum distance holds |
| Link-loss contract ([RFC-0006](0006-connectivity-and-link-loss.md)) | A timed STL property over a link-health signal: loss bounded in duration before the declared failsafe must fire |
| Layer-3 behavior phase (sequence / parallel) | The temporal scope a property is monitored over; an STL window aligned to a behavior step |
| Signal interface (the trace URML would emit) | The named signals RTAMT expects per timestamp; URML declares the property, the runtime emits the trace |

### What URML v0.1 does not yet express

These are **gaps surfaced by the mapping**, flagged as *queued Spec RFCs* for
separate follow-up. **They are not proposed in this Outreach RFC.**

1. **A monitorable-property specification on the safety envelope.** URML's
   envelope declares limits the validator enforces statically; it does not yet
   attach a machine-checkable temporal-logic property (the STL formula a monitor
   would consume) to a limit. A future Spec RFC could add an optional
   monitorable-property field so an envelope limit also names its runtime-checkable
   form.
2. **A linkage from a behavior or envelope to an external runtime monitor.** URML
   has no field that points a behavior or envelope at the monitor that enforces
   its properties at runtime, nor a declared signal interface for the trace. A
   future Spec RFC could add an optional monitor-linkage so a deployment can name
   the runtime monitor and the signals it consumes.

### Compatibility notes

- **Vendor org.** [`nickovic`](https://github.com/nickovic) (Dejan Nickovic, AIT
  Austrian Institute of Technology).
- **Engagement repo.** [`nickovic/rtamt`](https://github.com/nickovic/rtamt): a
  Python library for STL specification and online and offline runtime monitoring;
  active.
- **Origin / policy.** Austria (AIT). Treated as INTL (NATO-allied); passes
  US-federal default policy ([RFC-0004](0004-compliance-policy.md)): an
  open-source monitoring library is not a provenance-gated component.
- **License note.** Open-source; URML's relationship is cross-citation and
  runtime composition, not code vendoring.
- **Substrate-neutrality.** STL is defined over signals, not over a substrate; an
  envelope property monitored by RTAMT works against a ROS 2, PX4, or zero-ROS
  trace with no change to the property.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The monitorable-property specification
  and the monitor-linkage are queued Spec RFCs.
- Reference runtime: no change in this RFC. A mapping would compile a declared
  envelope property to an STL formula and emit the matching signal trace; the
  planned `rtamt_envelope_cell.yaml` fixture would document the property and the
  signal interface hermetically.
- Conformance: no change. A monitor sits at runtime, below URML's static
  conformance surface ([RFC-0014](0014-substrate-conformance.md)).

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, envelope,
fixture, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Two-end mismatch.** URML reasons at author and dispatch time over declared
  intent; RTAMT reasons at runtime over signal traces. The mapping is honest
  that the two meet only at the shared property, not in a single execution path.
- **Property-translation fidelity.** A safety-envelope limit is coarse; an STL
  formula is precise. The translation from one to the other has freedom, and a
  naive compilation could assert more or less than the envelope intends. The
  mapping is described at the property altitude to keep that translation explicit.

## Alternatives considered

1. **Build URML's own runtime monitor.** Rejected. Runtime verification is a
   mature research field with reference tooling; reimplementing an STL monitor
   inside URML would be worse than the existing libraries and would couple a
   monitor to URML's release cycle. Composition with RTAMT is the on-ethos choice.
2. **Express envelope properties only statically and stop there.** Rejected. It
   would imply static validation covers execution, which it does not. A drifting
   sensor or a changed world is a runtime fact; declining to name the runtime half
   would overclaim URML's guarantee.
3. **Embed STL syntax directly in the URML envelope schema now.** Rejected as
   premature. Attaching a temporal-logic property to the envelope is a normative
   spec change that deserves its own Spec RFC with the monitoring community's
   input, not a quiet addition folded into an outreach thread.

## Prior art

- [RFC-0006 (connectivity and link-loss)](0006-connectivity-and-link-loss.md):
  the link-loss contract that reads most naturally as a timed monitorable property.
- [RFC-0004 (compliance policy)](0004-compliance-policy.md): the static-policy
  evaluation URML already performs before dispatch, the pattern a runtime monitor
  complements.
- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  related work on declared constraints that a runtime layer enforces.
- Sibling Move #28 RFCs: RFC-0363 (Reelay), RFC-0364 (Copilot),
  RFC-0365 (Ogma), RFC-0371 (MoonLight).
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) (section 1.2,
  the manifest-vs-envelope boundary) and
  [`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md): the
  envelope and behavior surfaces this engagement exercises.

## Unresolved questions

For the RTAMT maintainers:

1. **Envelope-to-STL mapping.** Could a URML safety-envelope property (a velocity
   bound, a geofence containment, an occupancy clearance) be expressed as or
   compiled to an STL formula RTAMT monitors? Is there a property class where the
   translation is clean and one where it is not?
2. **Signal interface.** What signal interface does an RTAMT monitor expect (named
   signals per timestamp, sampling assumptions, dense vs discrete time) so URML
   could emit the right trace from a runtime?
3. **Static-pre-dispatch vs runtime-monitoring division.** Does the division URML
   draws hold up from a runtime-verification standpoint: URML rejects inadmissible
   intent before dispatch, RTAMT catches a runtime violation of the same envelope
   property? Where would you redraw the line?
4. **Online vs offline.** For an on-robot deployment, is online monitoring the
   right mode, and what latency or throughput envelope should URML assume when
   it decides what to emit?
5. **Conformance listing.** Would RTAMT consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md)) as a
   composing runtime-verification target?
6. **Anything else.**

## Implementation note

RFC-0362 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`nickovic/rtamt`](https://github.com/nickovic/rtamt) pointing at this RFC
(Issues are enabled on the repo). If the maintainers prefer another channel,
URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 76 stars, not archived, Issues enabled,
      active, last push 2025-11-20).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, two-end mismatch, property-translation
      fidelity).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; envelope gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: Austria (AIT), INTL / NATO-allied; default policy passes for an
      open-source monitoring library.
- [x] CLAUDE.md compliance check passed (substrate-neutral; STL is defined over
      signals, the same property monitors a ROS 2, PX4, or zero-ROS trace; URML
      composes with the monitor, does not replace it).
