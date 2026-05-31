---
rfc: 0289
title: Snap! (UC Berkeley block language / CS curriculum) integration, request for comment from Snap! maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-31
updated: 2026-05-31
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

# RFC-0289: Snap! (UC Berkeley block language / CS curriculum) integration, request for comment from Snap! maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

Snap! is the block language behind UC Berkeley's Beauty and Joy of Computing (BJC) curriculum, used widely in high-school and introductory-college CS. This RFC proposes how URML's natural-language and validated-intent layer could serve as a teaching bridge from English to robot intent in a Snap!-based course, and **requests review and feedback from the Snap! maintainers**. Snap! is AGPL-3.0, so the proposal is cross-citation and a documented mapping, not code bundling. No spec change.

## Motivation

Snap! ([`jmoenig/Snap`](https://github.com/jmoenig/Snap), AGPL-3.0, ~1.6k stars, Issues enabled, active, **not archived**, verified 2026-05-31) is a mature, education-first block language with first-class procedures and a strong CS-curriculum footprint (BJC). Its audience is the high-school CS classroom, exactly the reader URML's educational profile is built for.

Three concrete points:

1. **Curriculum reach.** Snap!/BJC reaches high-school CS students at scale. URML's pitch to schools is "an English sentence becomes a validated robot action"; a Snap!-based course is a natural place to teach that loop.
2. **Conceptual fit.** Snap! teaches students to compose behavior from named blocks. URML teaches them to express intent in a small primitive vocabulary that is validated before anything moves. The two reinforce the same mental model from different sides.
3. **Honest license handling.** AGPL-3.0 means no vendoring of Snap! code into URML's Apache-2.0 tree. The integration is a documented mapping and cross-citation, which composes without license friction.

## Detailed design

### What URML already ships

- Educational profile (RFC-0011); `examples/educational/` worked programs; [Tutorial 5](../tutorials/05-teaching-urml.md), a 30-minute offline lesson.
- `reference/edu-runtime/` for the common classroom platforms.

### Proposed relationship (request for comment)

| URML concept | Snap! concept | Proposed relationship |
|---|---|---|
| Natural-language layer (Layer 4) | (student authoring in blocks) | English→validated-intent as a teaching bridge demonstrated in a Snap! lesson. |
| Intent primitives (Layer 2) | Snap! custom blocks | A documented correspondence so a lesson can show the same intent in both. |
| Educational profile safety rules | (lesson design) | URML's fail-closed `detect` and gentle-grasp defaults as a teachable safety idea. |

The deliverable that would actually help a classroom is a *lesson artifact* (a short BJC-compatible module), not a code dependency. That keeps the AGPL boundary clean.

### What URML v0.1 does not yet express

- No block-language-environment substrate declaration (shared with RFC-0287 / RFC-0288). Spec RFC candidate, not proposed here.

### Spec / validator / reference-runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **AGPL boundary.** Limits integration to mapping / cross-citation / lesson material; no shared code.
- **Audience is curriculum, not a device.** The value is pedagogical reach, harder to measure than an adapter shipping.

## Alternatives considered

1. **Treat Snap! as a runtime target.** Rejected: Snap! is a teaching environment, and the AGPL boundary makes a code adapter the wrong shape. A lesson bridge is the honest fit.
2. **Approach the BJC curriculum team directly instead of the Snap! repo.** Considered; the repo is the open, public channel and the right first touch. A curriculum-team conversation can follow if the maintainers point there.
3. **Skip Snap! and rely on MakeCode / Open Roberta.** Rejected: Snap!/BJC owns a distinct high-school CS niche neither covers.

## Prior art

- [`jmoenig/Snap`](https://github.com/jmoenig/Snap) — the Snap! environment.
- [RFC-0011 (educational profile)](0011-educational-profile.md).
- Sibling environment RFCs: [RFC-0287 (Open Roberta)](0287-open-roberta-outreach.md), [RFC-0288 (Microsoft MakeCode)](0288-makecode-outreach.md).

## Unresolved questions

For the Snap! maintainers:

1. **Lesson bridge.** Would a short BJC-compatible lesson showing English→validated-intent be useful to point students at, or off-scope?
2. **Block correspondence.** Is a documented Snap!-block↔URML-primitive mapping interesting, kept on URML's side under Apache-2.0?
3. **Channel.** Is the Snap! repo the right place for this, or should it go to the BJC curriculum team?
4. **Anything else.**

## Implementation note

RFC-0289 ships as a single RFC document. Ledger entry in [`examples/lighthouses/outreach-move19.yaml`](../../examples/lighthouses/outreach-move19.yaml).

## How to respond

`jmoenig/Snap` has Issues enabled (Discussions are not). URML's planned channel: a single Issue pointing to this RFC, framed as a request for comment, with the AGPL boundary stated up front so the proposal is unambiguous about not asking for shared code.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-31 (AGPL-3.0, ~1.6k stars, Issues enabled, active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, AGPL boundary, hard-to-measure curriculum value).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: UC Berkeley, US; default policy passes.
- [x] CLAUDE.md compliance check passed (educational scope; no commercial surface).
