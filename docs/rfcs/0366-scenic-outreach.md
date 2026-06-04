---
rfc: 0366
title: Scenic (scenario specification language) integration, request for comment from the Scenic maintainers
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

# RFC-0366: Scenic integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
relationship between URML v0.1 and an existing target, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`BerkeleyLearnVerify/Scenic`](https://github.com/BerkeleyLearnVerify/Scenic),
a probabilistic programming language for specifying scenarios and environments
to test and train autonomous systems. It **requests review and feedback from
the Scenic maintainers**.

The honest framing here is **peer and compose, not URML above**. URML and
Scenic are both specification languages, on orthogonal axes. URML
([`spec/layer-4-nl-grammar/`](../../spec/layer-4-nl-grammar/) down to
[`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) specifies
robot **intent** and declared **capability**: an English sentence becomes a
typed primitive, statically validated against a capability manifest and a
safety envelope before dispatch. Scenic specifies the **scenario**: the world,
the agents, and the distribution of conditions the system under test faces.

Together the two languages describe both halves of a test. URML says what the
robot is told to do and what it is allowed to do. Scenic says what world the
robot is dropped into. A URML Layer-3 behavior is a natural system under test
that a Scenic scenario exercises, and the pairing yields a complete,
human-readable test specification: intent times environment.

## Motivation

Scenic is the most established scenario-specification language in the autonomy
community, and it sits exactly alongside URML rather than below it:

1. **Two specification languages, two axes.** URML specifies intent and
   capability; Scenic specifies the scenario and environment. Neither subsumes
   the other. A test needs both halves, and today they are written in unrelated
   formats with no shared reference point.
2. **A URML behavior is a clean system under test.** A Layer-3 behavior is a
   bounded, validated unit of intent. That is precisely the kind of ego or
   agent specification a Scenic scenario wants to drive: a system whose
   commanded behavior is fixed and inspectable, so the scenario varies the world
   and not the controller.
3. **Both languages are human-readable on purpose.** URML optimizes for a
   roboticist reading intent; Scenic optimizes for a researcher reading a
   scenario. A pairing keeps the full test description readable end to end
   rather than splitting it across a readable scenario and an opaque controller.
4. **The capability manifest and the scenario's agent assumptions should
   agree.** A Scenic scenario carries assumptions about what the ego can do.
   URML's capability manifest declares exactly that surface. Keeping the two
   consistent (the scenario does not assume an action the manifest forbids) is a
   real verification value the pairing could deliver.

Repo at [`BerkeleyLearnVerify/Scenic`](https://github.com/BerkeleyLearnVerify/Scenic)
(about 374 stars, Issues enabled, not archived, very active, last push
2026-06-03). Origin: UC Berkeley (United States); passes US-federal default
policy (open-source research language, no provenance gate at the
specification layer). Scenic and VerifAI ([RFC-0367](0367-verifai-outreach.md))
are both from the BerkeleyLearnVerify group and are designed to work together;
Scenic generates the scenarios VerifAI falsifies against.

## Detailed design

### URML behavior to Scenic scenario pairing

| URML side | Scenic side |
|---|---|
| Layer-3 behavior (validated intent, the system under test) | The ego / agent specification a scenario drives |
| Capability manifest ([Layer 1](../../spec/layer-1-hal/v0.1.0.md)) | The scenario's assumptions about the agent's action and sensor surface |
| `declared_locations`, `frames` | Named positions and the scene coordinate frame a scenario places objects in |
| `perception.object_vocabulary` | Object classes a scenario instantiates as agents or obstacles |
| Safety envelope limits (Pass 3) | The bounds a scenario should respect or deliberately probe at the edges of |
| A rejected URML program (static validation fails) | A scenario that never needs to run; the intent was inadmissible before the world existed |

The relationship is two specification languages meeting at the test. URML fixes
the intent and the capability; Scenic fixes the world. Neither compiles into the
other.

### Queued Spec RFC gaps (not proposed here)

These are gaps the pairing surfaces. They are **not proposed in this Outreach
RFC** and would each be a separate Spec RFC.

1. **Scenario-spec linkage.** URML has no declared link between a Layer-3
   behavior and an external scenario specification. A future Spec RFC could
   define an optional behavior-to-scenario linkage so a URML behavior can name
   the Scenic scenario it is meant to be exercised against, and so the two stay
   consistent under change.
2. **Falsifiable-property export from the safety envelope.** The safety envelope
   declares limits the validator conjoins at Pass 3, but it does not export those
   limits as a machine-readable property set a scenario or analysis tool can read.
   A future Spec RFC could add a falsifiable-property export (shared with
   [RFC-0367](0367-verifai-outreach.md)).

### Compatibility notes

- **Org.** [`BerkeleyLearnVerify`](https://github.com/BerkeleyLearnVerify)
  (UC Berkeley, the same group behind VerifAI).
- **Engagement repo.** [`BerkeleyLearnVerify/Scenic`](https://github.com/BerkeleyLearnVerify/Scenic),
  the scenario specification language.
- **Origin / policy.** United States (UC Berkeley). Passes US-federal default
  policy (open-source research language, no provenance gate at the
  specification layer).
- **Relationship.** Open-source; relationship is cross-citation and
  composition, not vendoring. URML does not embed Scenic and Scenic does not
  embed URML; they meet at a shared test description.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The scenario-spec linkage and the
  falsifiable-property export are queued Spec RFCs.
- Reference runtime: no change in this RFC. A worked pairing would express a
  URML Layer-3 behavior as the ego a Scenic scenario drives, and would document
  how the capability manifest and the scenario's agent assumptions are kept
  consistent.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, behavior,
envelope, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **No interchange point exists yet.** URML and Scenic have no shared format
  today, so the pairing is currently a description rather than a tool. The first
  concrete artifact would be a single worked example, not a general bridge.
- **Altitude has to stay honest.** It is tempting to claim URML drives Scenic or
  Scenic drives URML. Neither is true. The value is two specifications meeting at
  a test, and overstating the coupling would misrepresent both languages.

## Alternatives considered

1. **Frame URML as sitting above Scenic.** Rejected as dishonest. Scenic is not
   a substrate URML compiles onto; it is a peer specification language for a
   different axis. The composition is side by side, intent times environment, not
   a layer stack.
2. **Engage VerifAI only and treat Scenic as an implementation detail.**
   Rejected. Scenic is a specification language in its own right and the
   scenario half of the test is where URML's capability manifest finds its
   natural counterpart. VerifAI is engaged separately in
   [RFC-0367](0367-verifai-outreach.md); the two are coupled but distinct
   conversations.
3. **Propose the scenario linkage as a spec change now.** Rejected. Defining a
   behavior-to-scenario linkage in URML's normative surface before the
   maintainers have weighed in on whether an interchange point makes sense would
   invert the order. The linkage is queued as a Spec RFC, gated on this
   conversation.

## Prior art

- [RFC-0367 (VerifAI outreach)](0367-verifai-outreach.md): the sibling
  BerkeleyLearnVerify engagement; VerifAI falsifies against a specification,
  often using Scenic to generate the scenarios.
- RFC-0362 (RTAMT outreach): the Move #28 wave anchor; runtime verification of
  temporal-logic properties, the monitoring counterpart to the
  specification-language pairing described here.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  compatible-runtimes registry and honest-substrate-limit norm.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  the link-loss behavior a scenario could deliberately exercise.
- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  a domain where intent and environment must be specified together, the same
  shape this pairing generalizes.
- [`spec/layer-4-nl-grammar/`](../../spec/layer-4-nl-grammar/) and
  [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  specification surfaces, the half this pairing contributes.

## Unresolved questions

For the Scenic maintainers:

1. **Behavior as ego.** Could a URML Layer-3 behavior serve as the agent or ego
   specification a Scenic scenario drives, with Scenic varying the world while
   the commanded behavior stays fixed?
2. **Manifest / assumption consistency.** A Scenic scenario carries assumptions
   about what the ego can do. URML's capability manifest declares that surface.
   What is the right way to keep the two consistent, so a scenario does not
   assume an action the manifest forbids?
3. **Interchange point.** Is there a natural interchange point between the two
   languages (a shared object / pose vocabulary, a named-location convention),
   or are they better kept as independent specifications that a human pairs by
   hand for now?
4. **Direction of reference.** Should a URML behavior name the Scenic scenario it
   is exercised against, the reverse, or both, and at what granularity?
5. **Conformance listing.** Would Scenic consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md)),
   framed as a composing specification language rather than a runtime?
6. **Anything else.**

## Implementation note

RFC-0366 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`BerkeleyLearnVerify/Scenic`](https://github.com/BerkeleyLearnVerify/Scenic)
pointing at this RFC (the repo has Issues enabled). If the maintainers prefer
another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 374 stars, not archived, Issues
      enabled, very active, last push 2026-06-03).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, no interchange point yet, altitude must
      stay honest).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; the scenario-spec linkage and the
      falsifiable-property export are flagged as queued Spec RFCs, not proposed
      here.
- [x] Provenance: US (UC Berkeley); default policy passes at the specification
      layer.
- [x] CLAUDE.md compliance check passed (peer-and-compose framing, not
      URML-above; Scenic is a specification-language peer, paired with VerifAI
      in RFC-0367, not vendored).
