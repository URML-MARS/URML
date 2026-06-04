---
rfc: 0370
title: esmini (ASAM OpenSCENARIO player) integration, request for comment from the esmini maintainers
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

# RFC-0370: esmini integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's tooling, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`esmini/esmini`](https://github.com/esmini/esmini), a lightweight player and
tool suite for ASAM OpenSCENARIO and OpenDRIVE files, used to define, replay,
and test driving and robot scenarios. It **requests review and feedback from the
esmini maintainers**.

URML statically validates intent against a capability manifest and a safety
envelope before a single command is dispatched. esmini sits at a complementary
lifecycle point: it executes standardized OpenSCENARIO test scenarios. For URML,
esmini is a standards-based test harness. A URML-governed system can be the ego
or agent exercised by an OpenSCENARIO scenario, which gives a portable way to
check that URML's static validation and the resulting Layer-3 behavior hold up
in defined situations.

URML does not run scenarios and does not replace the player. It declares intent
plus an envelope and validates before dispatch; esmini provides the scenario
standard and the player that drives the system-under-test through a defined
situation. The relationship is composition at the test boundary, not overlap.

## Motivation

OpenSCENARIO is the industry standard for describing test situations, and esmini
is a widely used open player for it. A standards-based scenario harness is the
right place to demonstrate that URML's validate-before-you-move contract survives
contact with defined, repeatable situations:

1. **It is the scenario STANDARD, not a bespoke harness.** esmini plays ASAM
   OpenSCENARIO and OpenDRIVE. Wiring a URML-governed agent as the controlled
   entity gives a portable, standards-anchored way to exercise URML behavior, one
   that other tools in the OpenSCENARIO ecosystem can reuse.
2. **It exercises the envelope under defined situations.** A safety envelope
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): geofence,
   occupancy, velocity and altitude bounds, link-loss) is only as good as the
   situations it faces. An OpenSCENARIO scenario is a defined situation; running
   a URML agent through one tests that the static check and the behavior match
   intent under stress.
3. **It complements Scenic, it does not duplicate it.** Scenic (RFC-0366) is a
   probabilistic scenario LANGUAGE for generating situations. OpenSCENARIO with
   esmini is the industry STANDARD player for executing them. URML stays the
   intent plus envelope layer above both; the two scenario surfaces are
   complementary, generation and standardized execution.
4. **It grounds substrate-neutrality.** A URML behavior wired as an
   OpenSCENARIO entity must also drive real hardware unchanged. esmini is one
   scenario player; the value is showing the same validated behavior under a
   standard test, not engine-shaping the behavior to one player.

Repo at [`esmini/esmini`](https://github.com/esmini/esmini) (about 916 stars,
Issues enabled, not archived, very active, last push 2026-06-02). Origin:
open-source community (Swedish lineage, NATO-allied).

## Detailed design

### URML v0.1 to OpenSCENARIO / esmini mapping (system-under-test framing)

| URML concept | Maps to OpenSCENARIO / esmini concept |
|---|---|
| `robot_id`, `description` | The controlled entity's identity within the scenario's entity set |
| `frames`, `declared_locations` | The scenario's road network and named positions (OpenDRIVE frame, scenario reference points) |
| `mobility.drive_type` / `max_velocity` | The entity's movement model and the speed bounds it is exercised against in the scenario |
| `perception.cameras[]` / `sensors[]` | The entity's sensing surface the scenario's environment and other actors are observed through |
| Layer-3 behavior (the validated program) | The controller logic driving the ego or agent entity through the scenario |
| Safety envelope limits (Pass 3) | The bounds the scenario stresses; URML validates statically before the run, esmini drives the situation |

URML stays above the player: validated intent produces the entity's behavior, the
scenario drives the situation, and the run reports whether the envelope held.

### Queued Spec RFC gaps (not proposed here)

These are gaps surfaced by the mapping, flagged as *queued Spec RFCs* for
separate follow-up. **They are not proposed in this Outreach RFC.**

1. **Scenario-standard linkage.** URML has no way to declare a Layer-3 behavior
   as the system-under-test in an OpenSCENARIO run. A future Spec RFC could add an
   optional scenario-linkage so a validated behavior can be named as the
   controlled entity in a standardized scenario, shared with the Scenic linkage
   (RFC-0366).
2. **Monitorable-property attachment.** Pairing an executed scenario with a
   runtime check of the envelope wants a monitorable property attached to the
   safety envelope. A future Spec RFC could add that, shared with the runtime
   monitoring siblings (RFC-0362, RFC-0371). It would not model the scenario
   format itself.

### Compatibility notes

- **Engagement repo.** [`esmini/esmini`](https://github.com/esmini/esmini): a
  lightweight ASAM OpenSCENARIO and OpenDRIVE player and tool suite; very active.
- **Origin / policy.** Open-source community, Swedish lineage (NATO-allied).
  Treated as INTL; passes US-federal default policy (open-source tooling, no
  provenance gate at the scenario-test layer).
- **Relationship.** Open-source; the relationship is cross-citation and
  composition, not vendoring. URML cites esmini as a standards-based test harness
  and composes with it at the scenario boundary; neither tool embeds the other.
- **Substrate-neutrality.** esmini is one scenario player among possible test
  surfaces; the same URML behavior runs unchanged on real hardware, so wiring it
  as an OpenSCENARIO entity does not shape the behavior to the player.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The scenario-standard linkage and the
  monitorable-property attachment are queued Spec RFCs.
- Reference runtime: no change in this RFC. A future mapping would expose a
  validated Layer-3 behavior as the controlled entity in an esmini-played
  OpenSCENARIO run; this RFC documents the framing only.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **AV-centric standard.** OpenSCENARIO grew from the automated-driving world.
  Its entity and road-network vocabulary fits ground vehicles best; mapping a
  general robot or an aerial agent onto it may need framing the maintainers can
  help settle (question 3).
- **Test-boundary fit.** URML's value to esmini is as a system-under-test
  governor, not as a feature esmini needs. The engagement is honest about that
  asymmetry: URML gains a standards-based test harness more than esmini gains the
  mapping.

## Alternatives considered

1. **Skip standardized scenarios and test only with ad-hoc scripts.** Rejected.
   An ad-hoc harness is not portable and not reusable by the broader ecosystem. A
   standards-based player gives URML a repeatable, shareable way to show the
   envelope holds under defined situations.
2. **Engage only Scenic and treat it as the single scenario surface.** Rejected.
   Scenic (RFC-0366) is a probabilistic scenario language; OpenSCENARIO with
   esmini is the industry standard player. They sit at different points
   (generation versus standardized execution) and are engaged as complements, not
   substitutes.
3. **Model OpenSCENARIO entities inside the URML manifest.** Rejected. The
   scenario format and the road network are a test-harness concern below URML's
   altitude; URML declares capability and envelope over the agent, not the
   scenario. Modelling the scenario would fail the substrate-neutrality acid test.

## Prior art

- [RFC-0362 (RTAMT outreach)](0362-rtamt-outreach.md): the Move #28 wave anchor;
  STL runtime monitoring, the temporal complement to URML's static envelope check.
- [RFC-0366 (Scenic outreach)](0366-scenic-outreach.md): sibling Move #28
  engagement; a probabilistic scenario specification language, the generation
  complement to this standardized-player engagement.
- [RFC-0371 (MoonLight outreach)](0371-moonlight-outreach.md): sibling Move #28
  engagement; spatio-temporal runtime monitoring.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  conformance and honest-substrate-limit norm this engagement follows.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md) and
  [`spec/layer-3-behavior/README.md`](../../spec/layer-3-behavior/README.md): the
  capability, envelope, and behavior surfaces this engagement exercises.

## Unresolved questions

For the esmini maintainers:

1. **Controlled-entity wiring.** What is the right seam for wiring a
   URML-governed agent as the controlled entity in an OpenSCENARIO run played by
   esmini? Is esmini's external-controller interface the intended boundary for an
   outside behavior to drive an entity?
2. **Capability-to-entity alignment.** Does URML's mobility and perception
   capability declaration line up with OpenSCENARIO entity definitions, or is
   there a richer entity description URML should read against instead?
3. **AV-centric vs general-robot scope.** OpenSCENARIO grew from automated
   driving. How well does its entity and road-network model fit a general mobile
   robot or an aerial agent, and is that scope esmini wants to support?
4. **Scenario-as-test framing.** Would the maintainers find a documented
   pattern useful, where a URML-validated behavior is the system-under-test
   exercised by a standard OpenSCENARIO scenario, and is there a preferred example
   scenario to anchor it on?
5. **Conformance listing.** Would esmini consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
6. **Anything else.**

## Implementation note

RFC-0370 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`esmini/esmini`](https://github.com/esmini/esmini) pointing at this RFC. If the
maintainers prefer another channel, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 916 stars, not archived, Issues enabled,
      very active, last push 2026-06-02).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, AV-centric standard, test-boundary fit).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest and envelope gaps flagged as queued
      Spec RFCs, not proposed here.
- [x] Provenance: open-source community (Swedish lineage, NATO-allied); default
      policy passes at the scenario-test layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; esmini is one
      scenario player, the same validated behavior runs on real hardware;
      composed-with, not assumed).
