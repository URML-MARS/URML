---
rfc: 0295
title: Intuition Robotics / ElliQ integration, research-collab proposal (off-GitHub)
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

# RFC-0295: Intuition Robotics / ElliQ integration, research-collab proposal (off-GitHub)

No spec change is proposed here. This is an Outreach RFC: it proposes a future mapping from URML v0.1 to an existing target, not a change to URML's normative surface.

## Summary

URML proposes courtesy alignment with Intuition Robotics (the ElliQ elder-care companion, Israel-domiciled). The ask is **research-collab**: a documented intent of how URML's home-profile speech extensions would map to an ElliQ-style companion routine, and a question about whether a developer surface exists. **Engagement surface is off-GitHub**: ElliQ publishes no public developer API or SDK; the channel is the company contact surface. ElliQ is a stationary tabletop companion, so the honest mapping is a **lower-bound speech-and-sensing subset**, not a mobility mapping. RFC-0102 (Bear Robotics) is the off-GitHub-courtesy precedent; [RFC-0103 (Maytronics)](0103-maytronics-dolphin-outreach.md) is the IL-origin sibling and the lower-bound-mapping precedent.

## Motivation

Intuition Robotics (Ramat Gan, Israel; allied, default-policy pass) builds ElliQ, a proactive AI companion for older adults that combats loneliness and supports healthy aging through voice interaction, reminders, check-ins, and a caregiver-relay solution. It is a stationary tabletop device, not a mobile robot.

ElliQ is the first Move #20 target whose value lives almost entirely in URML's home-profile `speak` / `listen` extensions rather than mobility or manipulation: a caregiver expressing "ask my mother how she slept, and tell me what she says" maps to `listen(...)` + `report(...)`, with no `move_to` or `grasp` in the picture. This exercises the honest-substrate-limit norm ([RFC-0014](0014-substrate-conformance.md)): primitives a stationary companion cannot honor return `not_supported`, not a silent fudge.

Verified surface (2026-05-31):
- Company: [`intuitionrobotics.com`](https://www.intuitionrobotics.com/); product site [`elliq.com`](https://elliq.com/), including an ElliQ Caregiver solution.
- **No public developer API or SDK located.** ElliQ's published surfaces are consumer / caregiver apps. Engagement is off-GitHub.
- HQ: Ramat Gan, Israel.

## Detailed design (light, research-collab + off-GitHub)

1. **Courtesy outreach via the Intuition Robotics / ElliQ contact surface.** URML's identity, motivation, and one question: is there (or planned) any developer / integration surface a substrate-neutral language could target? Light payload.
2. **If a developer surface exists or opens**, URML proposes a future `ElliQAdapter` under [`reference/home-runtime/`](../../reference/home-runtime/) exposing only the lower-bound subset ElliQ reliably surfaces: `speak`, `listen`, `measure` (presence / interaction state), `report`. `move_to`, `grasp`, `release` return `not_supported_on_stationary_companion` per RFC-0014's honest-substrate-limit norm.
3. **Caregiver-relay framing.** ElliQ's caregiver solution is the natural place a URML-authored check-in routine would live; documented at the URML side, not contingent on a response.

## Backward compatibility

Pre-v1.0. Purely additive if ever implemented. Zero URML code in this RFC.

## Drawbacks

- **No verified developer surface.** Intuition Robotics has not published an API / SDK. URML documents this honestly; this RFC is a courtesy + question.
- **Stationary platform.** ElliQ has no mobility or manipulation; the URML mapping is a deliberately narrow speech-and-sensing subset. Named honestly, with `not_supported` returns for the rest.
- **Privacy sensitivity.** Elder-care voice interaction is privacy-sensitive; any future integration would have to honor URML's no-telemetry-without-opt-in posture. Flagged up front.
- **Light engagement payload.** Depth depends on Intuition Robotics' response.

## Alternatives considered

1. **Skip ElliQ because it is stationary.** Rejected; the stationary speech-only case is exactly where URML's `speak` / `listen` extensions and the honest-substrate-limit norm earn their keep, and ElliQ is a market leader in the companion niche.
2. **Ship an adapter against a private app surface.** Rejected; no public developer surface, and reverse-engineering a privacy-sensitive elder-care device is out of bounds.
3. **Fold ElliQ into a generic companion-robot RFC with Buddy ([RFC-0293](0293-blue-frog-buddy-outreach.md)) and Abi ([RFC-0296](0296-andromeda-abi-outreach.md)).** Rejected; different origins, surfaces, and mobility profiles; conflating obscures each engagement.

## Prior art

- [`intuitionrobotics.com`](https://www.intuitionrobotics.com/), [`elliq.com`](https://elliq.com/).
- [RFC-0103 (Maytronics Dolphin)](0103-maytronics-dolphin-outreach.md): IL-origin sibling; the lower-bound-mapping precedent (expose only what the substrate reliably surfaces).
- [RFC-0102 (Bear Robotics)](0102-bear-robotics-servi-outreach.md): off-GitHub courtesy precedent.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the honest-substrate-limit norm.
- [`spec/profiles/home/`](../../spec/profiles/home/): the home profile's `speak` / `listen` extensions.

## Unresolved questions

For Intuition Robotics:

1. **Developer surface.** Does ElliQ expose (or plan) any API / SDK / integration surface?
2. **Engagement channel.** Is the company contact form the right surface, or is there a partnerships / dev-relations contact?
3. **Speech-subset mapping.** Is a `speak` / `listen` / `measure` / `report` lower-bound subset the right characterization for ElliQ?
4. **Caregiver-relay fit.** Is URML's natural-language routine authoring of interest to the ElliQ Caregiver product?
5. **Anything else.**

## Implementation note

RFC-0295 ships as a single RFC document PR. No adapter code in this PR. Research-collab + off-GitHub framing. Ledger entry in [`examples/lighthouses/outreach-move20.yaml`](../../examples/lighthouses/outreach-move20.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

The contact surface is [`elliq.com`](https://elliq.com/) / [`intuitionrobotics.com`](https://www.intuitionrobotics.com/). URML's planned channel: a courtesy message via the company contact surface pointing at this RFC. If Intuition Robotics responds with a developer surface or a specific contact, URML pivots accordingly.

This RFC and any accompanying outreach are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub + research-collab framing explicit; absence of a developer surface acknowledged honestly.
- [x] Stationary lower-bound speech subset framed via the RFC-0014 honest-substrate-limit norm.
- [x] Privacy sensitivity of elder-care voice surfaced up front.
- [x] Cross-link to RFC-0103 (IL sibling + lower-bound precedent), RFC-0102 (off-GitHub precedent), RFC-0014, home profile.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no developer surface, stationary, privacy, light payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-31 (absence of developer surface documented).
- [x] Provenance `origin: IL`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
