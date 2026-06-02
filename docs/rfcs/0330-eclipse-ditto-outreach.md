---
rfc: 0330
title: Eclipse Ditto (IoT digital-twin framework) integration, request for comment from the Eclipse Ditto maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-06-02
updated: 2026-06-02
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

# RFC-0330: Eclipse Ditto integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
mapping from URML v0.1 to an existing target's framework, and requests review
from that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #24 is URML's simulation and digital-twin wave. The sibling RFCs reach the
simulators (RFC-0322 Genesis, RFC-0323 Isaac Sim, RFC-0325 CARLA, RFC-0329
Brax). This RFC reaches the **digital-twin anchor** of the wave, which is a
different concept: [`eclipse-ditto/ditto`](https://github.com/eclipse-ditto/ditto),
the Eclipse Foundation framework that manages digital twins of IoT devices via a
Thing / Feature model and a state / twin API. It **requests review and feedback
from the Eclipse Ditto maintainers**.

The angle is not simulation. Ditto keeps a live digital twin of a device: a
`Thing` with `Features`, each Feature carrying properties that mirror the
device's declared and current state. URML's capability manifest is, in effect, a
robot's **capability twin**: a machine-readable self-declaration of what the
robot can do. The two compose. URML's manifest maps onto a Ditto `Thing`
definition (capability blocks become Features, declared state surfaces as Feature
properties); URML validates intent against the declared twin **before dispatch**,
and Ditto reflects live state at runtime.

URML composes **above** the twin layer: URML intent -> validated Layer-2
primitives -> dispatch, with the capability manifest as the static contract. The
differentiator is **static validation against the capability manifest and the
active safety envelope before anything executes**. Ditto's contribution is the
runtime reflection of state; URML's is the pre-dispatch check.

The Eclipse Foundation already knows URML: sibling engagements exist with
[Eclipse iceoryx (RFC-0210)](0210-iceoryx-outreach.md) and
[Eclipse Zenoh (RFC-0209)](0209-zenoh-outreach.md). This RFC adds the digital-twin
framework to that set.

## Motivation

Digital twins and capability manifests are the same idea seen from two sides, and
Ditto is the reference framework for the runtime side:

1. **The manifest is a capability twin.** URML's Layer-1 manifest
   ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) is a
   self-declaration: `mobility`, `manipulation`, `perception` blocks describe
   what a robot can do. A Ditto `Thing` with `Features` describes the same robot
   to a fleet management plane. Mapping one onto the other lets a URML-validated
   robot publish its declared capability as a twin without a second schema.
2. **Static validation complements runtime reflection.** Ditto reflects the
   twin's live state and routes commands to the device. URML's contribution is
   one step earlier: a static check, before any command is sent, that the
   declared capability and the safety envelope admit the requested intent. The
   twin says what is; URML says what is allowed. They do not overlap.
3. **A fleet is many twins.** Ditto manages many Things. URML's fleet work
   ([RFC-0286](0286-multi-robot-fleet-addressing.md)) addresses many robots. A
   Ditto-backed twin per robot is a natural substrate for fleet-scale URML
   validation, with each robot's capability twin checked independently.

Repo at [`eclipse-ditto/ditto`](https://github.com/eclipse-ditto/ditto) (887
stars, Issues **and** Discussions enabled, not archived, last push 2026-06-01).
License is asked as a question below (understood to be EPL-2.0; the GitHub API
did not surface an SPDX id at verification time). Eclipse Foundation governance;
origin is the Eclipse Foundation (international, allied; passes US-federal
default policy as an open-source framework with no provenance gate at the
framework layer).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ditto_thing_cell.yaml` fixture)

| URML field | Maps to Ditto Thing attribute |
|---|---|
| `robot_id`, `description` | `Thing` ID and attributes (the twin's identity) |
| `mobility` block | A `mobility` Feature; `drive_type` / `max_velocity` / `max_payload` as Feature properties |
| `manipulation` block | A `manipulation` Feature; `arm_count` and per-`grippers[]` (`kind`, `force_max_n`, `accepted_classes`) as Feature properties |
| `perception` block | A `perception` Feature; `cameras[]`, `sensors[].measurement_type`, `object_vocabulary` as Feature properties |
| `declared_locations`, `frames` | Feature properties on a `world` Feature (declared places and frames the twin advertises) |
| `docking_stations[].services` | A `docking` Feature; each station's services as properties |
| `provenance` block | Twin-level attributes carrying the hardware-provenance claim (a twin can carry provenance for a fleet plane to read) |
| Live actuator / sensor state | Ditto Feature properties updated at runtime (URML does not write these; it validates against the declared twin) |

### What URML v0.1 does not yet express for Ditto

These are **manifest gaps surfaced by the mapping**, flagged as *queued Spec
RFCs* for separate follow-up. **They are not proposed in this Outreach RFC.**

1. **WoT Thing-Description alignment.** Ditto aligns with the W3C Web of Things
   (WoT) Thing Description. URML's manifest is its own YAML schema with no WoT TD
   binding. A future Spec RFC could define an optional mapping (or generator)
   between URML's capability manifest and a WoT TD, so a URML robot's declared
   capability is publishable as a standard Thing Description Ditto can ingest.
2. **Twin-sync hint.** URML's manifest declares baseline capability, not a
   pointer to where a live twin reflects state. A future Spec RFC could add an
   optional twin-sync hint (a twin endpoint a fleet plane reads) so the static
   manifest and a runtime twin are explicitly linkable, without URML reaching
   into the twin's live state.

### Compatibility notes

- **Vendor org.** [`eclipse-ditto`](https://github.com/eclipse-ditto) is an
  Eclipse Foundation project under foundation governance.
- **Engagement repo.** [`eclipse-ditto/ditto`](https://github.com/eclipse-ditto/ditto)
  is the digital-twin framework (Thing / Feature model, twin API).
- **Origin / policy.** Eclipse Foundation (international, allied). Passes
  US-federal default policy (open-source framework, no provenance gate at the
  framework layer). Sibling Eclipse engagements (iceoryx RFC-0210, Zenoh
  RFC-0209) already exist.
- **License fit.** Understood to be EPL-2.0; asked below. EPL-2.0 and URML's
  Apache-2.0 differ, but the engagement is cross-citation (a documented mapping
  and a registry link), not vendoring Ditto code into URML or the reverse, so
  the license difference does not bind.
- **Substrate-neutrality.** Ditto is one twin / fleet plane among several; the
  same URML manifest maps onto any twin model. The capability manifest is the
  source of truth, and a Ditto `Thing` is one projection of it.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The WoT-TD alignment and twin-sync hint
  are queued Spec RFCs, not proposed here.
- Reference runtime: no change. A Ditto mapping would project a validated URML
  manifest onto a `Thing` definition; the planned `ditto_thing_cell.yaml` fixture
  would demonstrate the manifest -> Thing projection hermetically, with no live
  Ditto instance required for the static half.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, fixture, or
runtime changes. The manifest stays the source of truth; a Ditto Thing is a
downstream projection.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **Layer mismatch risk.** Ditto is a runtime twin plane; URML is a static intent
  and capability layer. The mapping is clean on capability, but the live-state
  half is Ditto's, not URML's. The RFC must keep that boundary crisp or the twin
  and the manifest blur together (question 2 below).
- **WoT TD not yet modeled.** Aligning URML's manifest with WoT Thing Description
  is the right long-term move and is not done; this RFC only opens the question
  (gap 1, queued Spec RFC).

## Alternatives considered

1. **Fold Ditto into the simulator RFCs (Genesis / Isaac Sim / CARLA / Brax).**
   Rejected. Ditto is a digital-twin framework, not a simulator; the mapping
   concern (Thing / Feature model, runtime state reflection) is conceptually
   distinct from a physics simulator's. It earns its own request for comment.
2. **Model a full live twin in the URML manifest.** Rejected. Live state is
   Ditto's job; URML declares baseline capability, not runtime state (the Layer-1
   spec draws exactly this line). Modeling live state would duplicate Ditto and
   break the static-validation boundary.
3. **Engage at WoT (W3C) directly instead of Ditto.** Rejected as the anchor for
   this wave. WoT TD alignment is queued as a Spec RFC (gap 1), but the
   request-for-comment here is to the maintainers running a real twin framework;
   the standards-body conversation is a separate altitude and a later step.

## Prior art

- [RFC-0210 (Eclipse iceoryx outreach)](0210-iceoryx-outreach.md) and
  [RFC-0209 (Eclipse Zenoh outreach)](0209-zenoh-outreach.md) are sibling Eclipse
  Foundation engagements; the foundation already knows URML.
- [RFC-0286 (multi-robot fleet addressing)](0286-multi-robot-fleet-addressing.md):
  a fleet is many twins; a Ditto Thing per robot is a natural fleet substrate.
- [RFC-0004 (compliance policy)](0004-compliance-policy.md): a capability twin
  could carry the provenance claim a fleet plane reads.
- Sibling Move #24 RFCs: RFC-0322 (Genesis), RFC-0323 (Isaac Sim), RFC-0325
  (CARLA), RFC-0329 (Brax), the simulator side of the wave.
- [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  Hardware Abstraction layer, the manifest this engagement projects onto a twin.

## Unresolved questions

For the Eclipse Ditto maintainers:

1. **Manifest <-> Thing-model alignment and grain.** Is the right mapping
   "URML capability block -> Ditto Feature, declared property -> Feature
   property", and is the capability-block altitude the right grain, or should a
   URML robot publish a finer-grained Thing?
2. **Twin-as-validation-target boundary.** URML validates intent against the
   *declared* capability twin before dispatch; Ditto reflects *live* state. Does
   that split read cleanly to you, or is there overlap (for example, validating
   against live twin state) you would expect URML to use?
3. **WoT Thing-Description alignment.** Ditto aligns with W3C WoT TD. Should
   URML's capability manifest define an optional mapping to a WoT TD so a URML
   robot's declared capability is ingestible as a standard Thing Description?
4. **Provenance on the twin.** Would carrying URML's provenance claim
   ([RFC-0004](0004-compliance-policy.md)) as twin attributes fit Ditto's model,
   or is provenance better kept outside the twin?
5. **License.** What is the current license of `eclipse-ditto/ditto` (the GitHub
   API did not surface an SPDX id at verification time; understood EPL-2.0)? Does
   a cross-citation and a registry link raise any concern given URML is Apache-2.0?
6. **Conformance listing.** Would Eclipse Ditto consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md))?
7. **Anything else.**

## Implementation note

RFC-0330 ships as a single RFC document PR alongside the Move #24 ledger
([`examples/lighthouses/outreach-move24.yaml`](../../examples/lighthouses/outreach-move24.yaml))
and the post bodies
([`examples/lighthouses/posts-move24.md`](../../examples/lighthouses/posts-move24.md)).

## How to respond

The live channel is a GitHub Issue or Discussion on
[`eclipse-ditto/ditto`](https://github.com/eclipse-ditto/ditto) pointing at this
RFC (the repo has both enabled). If the maintainers prefer an Eclipse Foundation
mailing list or the project's own forum, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-02 (887 stars, not archived, Issues and
      Discussions enabled, last push 2026-06-01).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, layer-mismatch risk, WoT TD not yet modeled).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; manifest gaps (WoT-TD alignment, twin-sync hint)
      flagged as queued Spec RFCs, not proposed here.
- [x] Provenance: Eclipse Foundation, international allied; default policy passes
      at the framework layer.
- [x] CLAUDE.md compliance check passed (substrate-neutral; a Ditto Thing is one
      projection of the manifest, which stays the source of truth).
