---
rfc: 0288
title: Microsoft MakeCode (classroom programming environment) integration, request for comment from MakeCode maintainers
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

# RFC-0288: Microsoft MakeCode (classroom programming environment) integration, request for comment from MakeCode maintainers

**Kind: Outreach. No spec change is proposed here.**

## Summary

URML ships an educational profile (RFC-0011) and a `microbit_edu` manifest fixture (RFC-0018) for the BBC micro:bit, one of MakeCode's flagship targets. This RFC proposes how URML's natural-language and validated-intent layer could sit alongside MakeCode as a front door, and **requests review and feedback from the MakeCode (`microsoft/pxt`) maintainers**. It complements the micro:bit Foundation thread (RFC-0172) at the IDE / authoring layer. No spec change.

## Motivation

Microsoft MakeCode ([`microsoft/pxt`](https://github.com/microsoft/pxt), MIT, ~2.3k stars, Issues enabled, active, **not archived**; with [`microsoft/pxt-microbit`](https://github.com/microsoft/pxt-microbit), ~800 stars, verified 2026-05-31) is one of the highest-reach classroom programming environments in the world. It compiles blocks and TypeScript to micro:bit, Arcade, and other targets, and is used in enormous numbers of schools.

Three concrete points:

1. **micro:bit overlap.** URML's `microbit_edu` manifest (RFC-0018) describes the same device MakeCode's flagship editor targets. The micro:bit Foundation engagement (RFC-0172) is the platform-foundation thread; MakeCode is the authoring-environment thread, a distinct and complementary conversation.
2. **A front door, not a replacement.** URML turns one English sentence into a validated program. A teacher could let students phrase intent in English, see it validated against the device's declared capabilities, and use that as a bridge into a MakeCode program. URML proposes nothing for MakeCode to maintain.
3. **License composes.** MIT and Apache-2.0 compose cleanly.

## Detailed design

### What URML already ships

- Educational profile (RFC-0011); `microbit_edu` manifest fixture (RFC-0018).
- `reference/edu-runtime/` with a CircuitPython adapter (RFC-0174, *engaged*) and a micro:bit-class path.
- `examples/educational/` worked programs plus [Tutorial 5](../tutorials/05-teaching-urml.md), a no-API-key, offline classroom lesson.

### Proposed relationship (request for comment)

| URML concept | MakeCode concept | Proposed relationship |
|---|---|---|
| Natural-language layer (Layer 4) | (none today) | English→validated-intent as an optional on-ramp toward a MakeCode program. |
| Capability manifest (Layer 1) | Target / board definition (`pxtarget.json`, board JSON) | A mapping so a URML manifest aligns with a MakeCode board definition for the shared device classes. |
| Intent primitives (Layer 2) | MakeCode block / API namespaces | A documented primitive↔namespace correspondence for the micro:bit-class subset. |

### What URML v0.1 does not yet express

1. **Authoring-environment-as-substrate declaration** (MakeCode vs MicroPython vs C++ as the loaded firmware-language substrate) — shared with the micro:bit question in RFC-0172. Spec RFC candidate, not proposed here.
2. **Board-definition-derived manifests.** Deriving a URML manifest from a MakeCode board JSON is unspecified.

### Spec / validator / reference-runtime / conformance changes

None in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Large, busy project.** MakeCode is a major Microsoft-maintained codebase; a single-maintainer RFC may get a light-touch response.
- **Overlap with RFC-0172.** The micro:bit story spans two threads (Foundation + MakeCode); the post must state the boundary clearly to avoid looking duplicative.

## Alternatives considered

1. **Fold into the micro:bit Foundation RFC (0172).** Rejected: the Foundation owns the platform; MakeCode owns the authoring environment. Different maintainer groups, different asks.
2. **Pitch a runtime adapter.** Rejected: the front-door / manifest-alignment framing is the honest fit; URML already has the device adapter path.
3. **Skip MakeCode given its size.** Rejected: classroom reach is the entire point of an education move.

## Prior art

- [`microsoft/pxt`](https://github.com/microsoft/pxt), [`microsoft/pxt-microbit`](https://github.com/microsoft/pxt-microbit).
- [RFC-0172 (micro:bit Foundation)](0172-microbit-foundation-outreach.md), [RFC-0018 (minimal-MCU manifest)](0018-minimal-mcu-manifest.md), [RFC-0174 (CircuitPython)](0174-adafruit-circuitpython-outreach.md).
- Sibling environment RFCs: [RFC-0287 (Open Roberta)](0287-open-roberta-outreach.md), [RFC-0289 (Snap!)](0289-snap-outreach.md).

## Unresolved questions

For the MakeCode maintainers:

1. **Front-door fit.** Is an English→validated-intent on-ramp toward a MakeCode program interesting, or out of scope for the project?
2. **Board definitions.** Could a URML manifest align with a MakeCode target / board definition? What grain is most useful?
3. **Boundary with RFC-0172.** Does splitting the micro:bit conversation into Foundation (platform) and MakeCode (environment) threads make sense from your side?
4. **Adapter home.** URML-side (`reference/edu-runtime/`) or MakeCode-side, if anything ships?
5. **Anything else.**

## Implementation note

RFC-0288 ships as a single RFC document. Ledger entry in [`examples/lighthouses/outreach-move19.yaml`](../../examples/lighthouses/outreach-move19.yaml).

## How to respond

`microsoft/pxt` has Issues enabled (Discussions are not). URML's planned channel: a single Issue pointing to this RFC, framed as a request for comment, with the RFC-0172 boundary explicit so it does not read as duplicate outreach.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-31 (`pxt` MIT ~2.3k stars; `pxt-microbit` ~800 stars; Issues enabled; active; isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, large project light-touch risk, RFC-0172 overlap).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Microsoft, US; default policy passes.
- [x] CLAUDE.md compliance check passed (educational scope; no commercial surface).
