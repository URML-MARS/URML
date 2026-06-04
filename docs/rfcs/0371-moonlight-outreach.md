---
rfc: 0371
title: MoonLight (spatio-temporal logic monitoring) integration, request for comment from the MoonLight maintainers
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

# RFC-0371: MoonLight integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's tool, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`MoonLightSuite/moonlight`](https://github.com/MoonLightSuite/moonlight), a tool
for monitoring temporal and spatio-temporal logic properties (Spatio-Temporal
Reach and Escape Logic, STREL) over signals. It **requests review and feedback
from the MoonLight maintainers**.

URML statically validates intent against a capability manifest and a safety
envelope before a single command is dispatched. MoonLight sits at the
complementary lifecycle point: it monitors spatio-temporal properties over
signals during execution. That is exactly the right vocabulary for URML envelope
properties that are inherently spatial AND temporal: a geofence held over time, a
separation distance maintained across a fleet, an occupancy constraint observed
through a window.

MoonLight is the spatio-temporal sibling of RTAMT (RFC-0362, STL and temporal).
URML declares the spatial plus temporal envelope; a MoonLight monitor enforces it
at runtime. URML does not monitor and does not replace the monitor. It declares
intent plus an envelope and validates before dispatch; MoonLight is the runtime
complement to that static check.

## Motivation

A URML safety envelope ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md))
carries constraints that are spatial and temporal at once, and a spatio-temporal
monitor is the natural runtime enforcer for them:

1. **STREL matches the envelope's shape.** A geofence is a spatial constraint;
   "held for the whole mission" makes it temporal. A separation distance across a
   fleet is spatial; "maintained at all times" makes it temporal. STREL's reach
   and escape operators are built for exactly this spatial-plus-temporal class,
   which is the part of the envelope plain temporal logic cannot express alone.
2. **It is the runtime complement to the static check.** URML's contribution is a
   static check before dispatch that the declared capability and envelope admit
   the intent. A monitor closes the loop at runtime: the static check says the
   plan is admissible, the monitor confirms the execution stayed inside the
   spatial-plus-temporal envelope. The two are complementary, not redundant.
3. **It serves the multi-robot case directly.** Fleet deconfliction
   (RFC-0291) is spatial-plus-temporal by nature: separation volumes maintained
   over time. STREL over a spatial graph of robots is the right monitoring
   vocabulary for that, the runtime sibling of the static deconfliction check.
4. **It pairs with the temporal sibling.** RTAMT (RFC-0362) covers STL and
   purely temporal envelope properties (a velocity bound held over a window).
   MoonLight covers the properties that are also spatial. Engaging both gives the
   envelope a runtime-monitoring complement across its full temporal and
   spatio-temporal surface.

Repo at [`MoonLightSuite/moonlight`](https://github.com/MoonLightSuite/moonlight)
(about 21 stars, Issues enabled, not archived, active, last push 2026-01-25). The
star count is low; MoonLight is a specialized tool and the reference STREL
monitor. Origin: IMT School / consortium (Italy, NATO-allied).

## Detailed design

### URML v0.1 envelope to STREL / MoonLight mapping (runtime-monitoring framing)

| URML concept | Maps to STREL / MoonLight concept |
|---|---|
| Safety envelope geofence | A spatial reach property over the robot's position signal, held over the mission interval |
| Safety envelope occupancy | A spatial property over an occupancy signal, monitored across a temporal window |
| Safety envelope velocity / altitude bounds | A bounded property over the corresponding signal, the temporal part a MoonLight monitor evaluates over time |
| Fleet separation (RFC-0291 deconfliction volumes) | A spatio-temporal property over the spatial graph of robots, separation maintained across the fleet over time |
| `connectivity` link-loss expectation (RFC-0006) | A temporal property over a link-state signal a monitor can evaluate alongside the spatial ones |
| Static envelope check (Pass 3) | The pre-dispatch complement; MoonLight evaluates the same envelope as a monitorable property at runtime |

URML stays above the monitor: it declares the spatial plus temporal envelope, and
a MoonLight monitor consumes the signals (and the spatial graph) to confirm the
envelope held during execution.

### Queued Spec RFC gaps (not proposed here)

These are gaps surfaced by the mapping, flagged as *queued Spec RFCs* for
separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Spatio-temporal monitorable-property attachment.** URML has no way to attach
   a spatio-temporal monitorable property to the safety envelope so a runtime
   monitor can consume it directly. A future Spec RFC could add an optional
   monitorable-property attachment, shared with the temporal sibling (RFC-0362)
   and the scenario-execution sibling (RFC-0370). It would not model STREL itself.
2. **Spatial-graph / signal interface.** Feeding a spatial monitor wants a
   declared signal and spatial-graph interface (positions, separation, occupancy)
   the monitor reads. A future Spec RFC could specify that interface, especially
   for the multi-robot case (RFC-0291). It stays an interface; the monitor logic
   lives in MoonLight.

### Compatibility notes

- **Engagement repo.** [`MoonLightSuite/moonlight`](https://github.com/MoonLightSuite/moonlight):
  a temporal and spatio-temporal (STREL) logic monitor over signals; the
  reference STREL monitor; specialized and active.
- **Origin / policy.** IMT School / consortium (Italy, NATO-allied). Treated as
  INTL; passes US-federal default policy (open-source tooling, no provenance gate
  at the monitoring layer).
- **Relationship.** Open-source; the relationship is cross-citation and
  composition, not vendoring. URML cites MoonLight as the runtime spatio-temporal
  monitoring complement and composes with it at the envelope boundary; neither
  tool embeds the other.
- **Substrate-neutrality.** MoonLight is one spatio-temporal monitor among
  possible runtime monitors; URML declares the envelope as a property and stays
  monitor-agnostic, so the same envelope can be monitored by another tool.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The spatio-temporal
  monitorable-property attachment and the spatial-graph / signal interface are
  queued Spec RFCs.
- Reference runtime: no change in this RFC. A future mapping would expose a
  URML envelope as a STREL specification and stream the signals (and the spatial
  graph) a MoonLight monitor evaluates; this RFC documents the framing only.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Specialized, small-audience tool.** MoonLight is the reference STREL monitor
  but has a small user base. The engagement is honest that this is a precise,
  niche fit rather than a high-traffic target; the value is correctness of the
  vocabulary, not reach.
- **Property-translation gap.** Expressing a URML geofence or separation envelope
  as a STREL specification is real work that does not exist yet. This RFC frames
  the fit and asks whether the mapping is sound; it does not claim the translation
  is built.

## Alternatives considered

1. **Use only a temporal monitor (RTAMT) and skip spatio-temporal.** Rejected.
   Pure STL cannot express the spatial-plus-temporal envelope properties (a
   geofence held over time, fleet separation maintained over time) without
   awkward encoding. STREL is the right vocabulary for the spatial part, so
   MoonLight is engaged as the spatial sibling of RTAMT (RFC-0362).
2. **Encode spatial constraints by hand inside the static validator.** Rejected.
   The static check is a pre-dispatch admissibility test, not a runtime monitor.
   Reimplementing spatio-temporal monitoring inside the validator would duplicate
   a mature tool and blur the static-versus-runtime boundary URML keeps clean.
3. **Model STREL operators inside the URML envelope schema.** Rejected. The
   monitoring logic is a runtime-verification concern below URML's altitude; URML
   declares the envelope as a monitorable property, not the monitor's logic.
   Modelling STREL would fail the substrate-neutrality acid test.

## Prior art

- [RFC-0362 (RTAMT outreach)](0362-rtamt-outreach.md): the Move #28 wave anchor;
  STL runtime monitoring, the temporal sibling of this spatio-temporal engagement.
- [RFC-0366 (Scenic outreach)](0366-scenic-outreach.md): sibling Move #28
  engagement; a scenario specification language.
- [RFC-0370 (esmini outreach)](0370-esmini-outreach.md): sibling Move #28
  engagement; a standardized scenario player.
- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  the multi-robot separation-volume surface this monitoring vocabulary serves.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the link-state surface a temporal monitor can evaluate alongside the spatial
  properties.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance and honest-substrate-limit norm this engagement follows.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md): the
  envelope and behavior surfaces this engagement exercises.

## Unresolved questions

For the MoonLight maintainers:

1. **Envelope-to-STREL soundness.** Does a URML geofence, occupancy, or
   separation envelope map cleanly onto a STREL specification, or are there
   envelope shapes STREL cannot express without distortion?
2. **Multi-robot spatial monitoring.** The fleet deconfliction case (RFC-0291)
   wants separation maintained across a spatial graph of robots over time. Is that
   a natural STREL use, and what spatial-graph representation does MoonLight expect
   for it?
3. **Signal / spatial-graph interface.** What signal and spatial-graph interface
   does a MoonLight monitor expect (sample format, graph topology, update rate),
   so URML can document the right boundary for streaming envelope-relevant signals?
4. **Offline vs online monitoring.** Does MoonLight target offline trace
   evaluation, online runtime monitoring, or both, and which is the better fit for
   confirming a URML envelope held during a live execution?
5. **Conformance listing.** Would MoonLight consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0371 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`MoonLightSuite/moonlight`](https://github.com/MoonLightSuite/moonlight) pointing
at this RFC. If the maintainers prefer another channel, URML will move the thread
there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 21 stars, not archived, Issues enabled,
      active, last push 2026-01-25; reference STREL monitor, specialized tool).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, specialized small-audience tool,
      property-translation gap).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; envelope gaps flagged as queued Spec RFCs, not
      proposed here.
- [x] Provenance: IMT School / consortium (Italy, NATO-allied); default policy
      passes at the monitoring layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; MoonLight is one
      spatio-temporal monitor, URML stays monitor-agnostic; composed-with, not
      assumed).
