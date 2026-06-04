---
rfc: 0367
title: VerifAI (formal analysis and falsification for AI/autonomy) integration, request for comment from the VerifAI maintainers
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

# RFC-0367: VerifAI integration

**No spec change is proposed here.** This is an Outreach RFC: it proposes a
relationship between URML v0.1 and an existing target, and requests review from
that target's maintainers. It does not modify URML's normative surface.

## Summary

Move #28 is URML's safety and runtime-verification wave. This RFC reaches
[`BerkeleyLearnVerify/VerifAI`](https://github.com/BerkeleyLearnVerify/VerifAI),
a toolkit for the formal design and analysis of systems with AI and ML
components: falsification, error-table analysis, and data augmentation, often
driven by Scenic. It **requests review and feedback from the VerifAI
maintainers**.

The honest framing is **peer and compose, not URML above**. URML
([`spec/layer-4-nl-grammar/`](../../spec/layer-4-nl-grammar/) down to
[`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md)) is a
specification language for robot **intent** and declared **capability**: an
English sentence becomes a typed primitive, statically validated against a
capability manifest and a safety envelope before dispatch. VerifAI is a
falsification and formal-analysis toolkit that searches for inputs and
scenarios under which a system violates its specification.

The natural pairing: URML's safety envelope declares **properties** the system
must hold; VerifAI searches for scenarios that **falsify** those properties
against a URML-governed system; a falsifying counterexample feeds back as an
envelope or capability **refinement**. URML provides a structured, declared
property set and a validated system under test. VerifAI provides the
falsification loop around it.

## Motivation

VerifAI is the most established falsification and analysis toolkit in the
autonomy-verification community, and it composes with URML cleanly:

1. **URML declares properties; VerifAI looks for violations.** The safety
   envelope ([`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md),
   Pass 3) is a declared, structured set of limits the validator conjoins before
   dispatch. That declaration is exactly the kind of specification a
   falsification search wants as its target.
2. **A URML-governed system is a well-defined system under test.** Because intent
   passes static validation before it runs, a URML-governed system has a fixed,
   inspectable commanded behavior and an explicit capability surface. That is a
   cleaner falsification target than an opaque controller.
3. **Counterexamples have a home to land in.** A falsifying counterexample is
   only useful if it changes something. In URML it maps to a concrete artifact:
   a tightened safety-envelope limit, or a corrected capability declaration. The
   falsification loop closes back into the specification rather than into a
   report.
4. **The Scenic coupling is already there.** VerifAI commonly drives its search
   with Scenic ([RFC-0366](0366-scenic-outreach.md)). URML pairs with Scenic as
   the scenario half of a test; pairing with VerifAI completes the loop:
   specify intent (URML) times world (Scenic), then falsify against the envelope
   (VerifAI).

Repo at [`BerkeleyLearnVerify/VerifAI`](https://github.com/BerkeleyLearnVerify/VerifAI)
(about 214 stars, Issues enabled, not archived, active, last push 2026-05-13).
Origin: UC Berkeley (United States); passes US-federal default policy
(open-source research toolkit, no provenance gate at the analysis layer).
VerifAI and Scenic ([RFC-0366](0366-scenic-outreach.md)) are from the same
BerkeleyLearnVerify group and are designed to work together; VerifAI often uses
Scenic to generate the scenarios it falsifies against.

## Detailed design

### URML safety envelope to VerifAI falsification pairing

| URML side | VerifAI side |
|---|---|
| Safety envelope limits (Pass 3, strictest-wins) | The specification / monitor a falsification search targets |
| A URML-governed system (validated intent plus capability manifest) | The system under test exposed to the search loop |
| Capability manifest ([Layer 1](../../spec/layer-1-hal/v0.1.0.md)) | The declared action and sensor surface bounding the search space |
| Scenic scenario ([RFC-0366](0366-scenic-outreach.md)) | The scenario generator that feeds the falsification loop |
| A falsifying counterexample | A refinement: an envelope tightening or a capability correction in URML terms |
| Error-table analysis output | The map from violated property back to the URML artifact that must change |

The relationship composes a specification (URML) with an analysis loop
(VerifAI). URML does not run VerifAI's search; VerifAI does not author URML's
intent.

### Queued Spec RFC gaps (not proposed here)

These are gaps the pairing surfaces. They are **not proposed in this Outreach
RFC** and would each be a separate Spec RFC.

1. **Falsifiable-property export from the safety envelope.** The envelope
   declares limits the validator conjoins at Pass 3 but does not export them as a
   machine-readable property set a falsification tool can consume. A future Spec
   RFC could add a falsifiable-property export (shared with
   [RFC-0366](0366-scenic-outreach.md)), so a VerifAI specification can be
   derived from the envelope rather than restated by hand.
2. **Scenario-spec linkage.** URML has no declared link between a Layer-3
   behavior and the scenario it is exercised against. A future Spec RFC could
   define a behavior-to-scenario linkage, which the VerifAI plus Scenic loop
   would consume to know which behavior is under test in which world.

### Compatibility notes

- **Org.** [`BerkeleyLearnVerify`](https://github.com/BerkeleyLearnVerify)
  (UC Berkeley, the same group behind Scenic).
- **Engagement repo.** [`BerkeleyLearnVerify/VerifAI`](https://github.com/BerkeleyLearnVerify/VerifAI),
  the falsification and formal-analysis toolkit.
- **Origin / policy.** United States (UC Berkeley). Passes US-federal default
  policy (open-source research toolkit, no provenance gate at the analysis
  layer).
- **Relationship.** Open-source; relationship is cross-citation and
  composition, not vendoring. URML supplies a declared property set and a
  validated system under test; VerifAI supplies the falsification loop. Neither
  embeds the other.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: **none in this RFC.** The falsifiable-property export and
  the scenario-spec linkage are queued Spec RFCs.
- Reference runtime: no change in this RFC. A worked pairing would expose a
  URML-governed system as a VerifAI system under test and would document how a
  falsifying counterexample maps back to an envelope or capability refinement.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). No existing manifest, envelope,
behavior, or runtime changes.

## Drawbacks

- **Proposal-only.** No code lands with this RFC; it is a request for comment.
- **No property export exists yet.** The envelope's limits are not yet a
  machine-readable property set, so a first pairing would restate properties by
  hand. The export is queued as a Spec RFC, not assumed here.
- **Falsification needs an executable system.** VerifAI falsifies against a
  running system under test. URML's contract is static validation before
  dispatch, so the pairing depends on a runtime (a reference runtime or a
  simulator) standing the validated behavior up to be searched against.

## Alternatives considered

1. **Frame URML as sitting above VerifAI.** Rejected as dishonest. VerifAI is
   not a substrate URML compiles onto; it is a peer analysis toolkit. URML
   supplies the specification and the system under test, VerifAI supplies the
   search; the composition is side by side, not a layer stack.
2. **Treat falsification as a runtime monitor.** Rejected. VerifAI is a
   design-time and analysis-time falsification toolkit, not a runtime monitor.
   The runtime-monitoring counterpart in this wave is RFC-0362 (RTAMT). Conflating
   the two would misrepresent both.
3. **Propose the property export as a spec change now.** Rejected. Defining a
   falsifiable-property export in URML's normative surface before the maintainers
   confirm an envelope property is a usable VerifAI specification would invert
   the order. It is queued as a Spec RFC, gated on this conversation.

## Prior art

- [RFC-0366 (Scenic outreach)](0366-scenic-outreach.md): the sibling
  BerkeleyLearnVerify engagement; Scenic generates the scenarios VerifAI
  falsifies against, and pairs with URML as the scenario half of a test.
- RFC-0362 (RTAMT outreach): the Move #28 wave anchor; runtime verification of
  temporal-logic properties, the monitoring counterpart to VerifAI's design-time
  falsification.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the
  compatible-runtimes registry and honest-substrate-limit norm.
- [RFC-0006 (connectivity and link loss)](0006-connectivity-and-link-loss.md):
  a link-loss property a falsification search could target.
- [RFC-0291 (UTM strategic deconfliction)](0291-utm-strategic-deconfliction.md):
  a domain whose safety properties are exactly the kind a falsification loop
  would probe.
- [`spec/layer-4-nl-grammar/`](../../spec/layer-4-nl-grammar/) and
  [`spec/layer-1-hal/v0.1.0.md`](../../spec/layer-1-hal/v0.1.0.md): URML's
  specification surfaces; the safety envelope is the property set this pairing
  falsifies against.

## Unresolved questions

For the VerifAI maintainers:

1. **Envelope property as specification.** Is a URML safety-envelope property
   (a geofence, an altitude bound, a velocity limit, a link-loss rule) a usable
   VerifAI specification or monitor, or does it need restating in a particular
   form first?
2. **Exposing the system under test.** How would a URML-governed system best
   expose itself as a VerifAI system under test: through a simulator the
   validated behavior runs in, a reference runtime, or a thinner interface?
3. **Counterexample mapping.** When VerifAI finds a falsifying counterexample,
   what should it map back to in URML terms: an envelope tightening, a capability
   correction, or a flagged gap in the manifest? Is there a natural error-table
   to URML-artifact correspondence?
4. **Scenic coupling.** VerifAI commonly drives its search with Scenic. With URML
   pairing Scenic as the scenario half ([RFC-0366](0366-scenic-outreach.md)), is
   the three-way loop (URML intent, Scenic world, VerifAI falsification) the
   right shape, or is a tighter two-way pairing preferable first?
5. **Conformance listing.** Would VerifAI consider a project link to URML's
   compatible-runtimes registry ([RFC-0014](0014-substrate-conformance.md)),
   framed as a composing analysis toolkit rather than a runtime?
6. **Anything else.**

## Implementation note

RFC-0367 ships as a single RFC document PR alongside the Move #28 ledger
([`examples/lighthouses/outreach-move28.yaml`](../../examples/lighthouses/outreach-move28.yaml))
and the post bodies
([`examples/lighthouses/posts-move28.md`](../../examples/lighthouses/posts-move28.md)).

## How to respond

The live channel is a GitHub Issue on
[`BerkeleyLearnVerify/VerifAI`](https://github.com/BerkeleyLearnVerify/VerifAI)
pointing at this RFC (the repo has Issues enabled). If the maintainers prefer
another venue, URML will move the thread there.

## Self-review (Phase 0)

- [x] Surface verified 2026-06-04 (about 214 stars, not archived, Issues
      enabled, active, last push 2026-05-13).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, no property export yet, falsification needs
      an executable system).
- [x] Backward compatibility additive; no spec change.
- [x] No Layer-2 primitive added; the falsifiable-property export and the
      scenario-spec linkage are flagged as queued Spec RFCs, not proposed here.
- [x] Provenance: US (UC Berkeley); default policy passes at the analysis layer.
- [x] CLAUDE.md compliance check passed (peer-and-compose framing, not
      URML-above; VerifAI is an analysis-toolkit peer, coupled with Scenic in
      RFC-0366, not vendored).
