---
rfc: 0296
title: Andromeda Robotics / Abi integration, research-collab proposal (off-GitHub, early-stage)
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

# RFC-0296: Andromeda Robotics / Abi integration, research-collab proposal (off-GitHub, early-stage)

No spec change is proposed here. This is an Outreach RFC: it proposes a future mapping from URML v0.1 to an existing target, not a change to URML's normative surface.

## Summary

URML proposes courtesy alignment with Andromeda Robotics (the Abi companion robot for aged care and assisted living, Australia-domiciled). The ask is **research-collab**: a documented intent of how URML's home-profile vocabulary would map to an Abi companion routine, and a question about whether a developer surface is planned. **Engagement surface is off-GitHub** and the target is **early-stage**: Andromeda raised funding in early 2026 and is building its platform internally, with no public developer API or SDK yet. The RFC is a forward-looking courtesy touch. RFC-0102 (Bear Robotics) is the off-GitHub-courtesy precedent. Closes the Move #20 home-assistance round-two wave.

## Motivation

Andromeda Robotics (Melbourne, Australia; allied, default-policy pass) builds Abi, a child-sized humanoid companion robot for aged-care and assisted-living residents, focused on empathy, conversation, and friendship. As of early 2026 the company is scaling its team and platform engineering (reproducible dev environments, simulation orchestration, CI), which signals a developer surface may emerge.

Abi is the youngest target in Move #20. The value of a courtesy touch now is to put URML's substrate-neutral natural-language layer on Andromeda's radar before their integration surface solidifies, so that if and when one exists it can be substrate-neutral from the start.

Verified surface (2026-05-31):
- Company: [`andromedarobotics.ai`](https://andromedarobotics.ai/); product page for Abi; news / funding announcements.
- **No public developer API or SDK located.** The platform is in active build-out; engagement is off-GitHub.
- HQ: Melbourne, Australia.

## Detailed design (light, research-collab + off-GitHub, early-stage)

1. **Courtesy outreach via the Andromeda company contact surface.** URML's identity, motivation, and one forward-looking question: as Andromeda builds out its platform, is a developer / integration surface planned that a substrate-neutral language could target? Light payload; no ask for a commitment.
2. **If a developer surface emerges**, URML proposes a future `AbiAdapter` under [`reference/home-runtime/`](../../reference/home-runtime/) exercising the home-profile `speak` / `listen` extensions plus mobility primitives appropriate to a child-sized humanoid (legged or wheeled per Abi's actual platform, declared in the manifest), with manipulation declared only if Abi exposes it.
3. **Empathy-and-conversation framing.** Abi's value is companionship; a URML mapping would center `speak` / `listen` / `measure(presence)` / `report`, with the honest-substrate-limit norm ([RFC-0014](0014-substrate-conformance.md)) governing anything the platform does not expose.

## Backward compatibility

Pre-v1.0. Purely additive if ever implemented. Zero URML code in this RFC.

## Drawbacks

- **Early-stage target.** Andromeda is scaling; a developer surface may be a year or more away, or may never be public. The RFC is honest that this is a forward-looking touch, not an integration plan.
- **No verified developer surface.** No API / SDK / GitHub org located. Documented honestly.
- **Privacy sensitivity.** Aged-care conversational data is privacy-sensitive; any future integration must honor URML's no-telemetry-without-opt-in posture. Flagged up front.
- **Light engagement payload.** Depth depends entirely on Andromeda's response and timeline.

## Alternatives considered

1. **Wait until Andromeda ships a developer surface.** Considered, rejected; an early courtesy touch is low-cost and the platform-engineering hiring signals the right moment to be on their radar.
2. **Fold Abi into a generic companion-robot RFC with Buddy and ElliQ.** Rejected; different origins (AU vs FR vs IL), maturity stages, and platform types (humanoid vs wheeled vs stationary).
3. **Skip Abi for Move #20.** Rejected; an AU-domiciled aged-care humanoid is a distinctive home-assistance data point and rounds out the wave's geographic spread.

## Prior art

- [`andromedarobotics.ai`](https://andromedarobotics.ai/).
- [RFC-0102 (Bear Robotics)](0102-bear-robotics-servi-outreach.md): off-GitHub courtesy precedent; senior-living adjacency.
- [RFC-0293 (Blue Frog Buddy)](0293-blue-frog-buddy-outreach.md), [RFC-0295 (Intuition Robotics ElliQ)](0295-intuition-robotics-elliq-outreach.md): the Move #20 companion-robot siblings.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md): the honest-substrate-limit norm.
- [`spec/profiles/home/`](../../spec/profiles/home/): the home profile's `speak` / `listen` extensions.

## Unresolved questions

For Andromeda Robotics:

1. **Developer surface.** Is a developer / integration surface planned for Abi as the platform matures?
2. **Engagement channel.** Is the company contact form the right surface, or is there a partnerships contact?
3. **Platform type.** Is Abi's mobility legged, wheeled, or stationary, for an accurate URML mobility manifest?
4. **Companion mapping.** Is a `speak` / `listen` / `measure` / `report`-centered mapping the right characterization for Abi's companionship focus?
5. **Anything else.**

## Implementation note

RFC-0296 ships as a single RFC document PR. No adapter code in this PR. Research-collab + off-GitHub + early-stage framing. Closes the Move #20 wave. Ledger entry in [`examples/lighthouses/outreach-move20.yaml`](../../examples/lighthouses/outreach-move20.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

The contact surface is [`andromedarobotics.ai`](https://andromedarobotics.ai/). URML's planned channel: a forward-looking courtesy message via the company contact surface pointing at this RFC. If Andromeda responds with a developer surface or a specific contact, URML pivots accordingly.

This RFC and any accompanying outreach are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub + research-collab + early-stage framing explicit; absence of a developer surface acknowledged honestly.
- [x] Forward-looking-touch rationale stated without overclaiming an integration plan.
- [x] Privacy sensitivity of aged-care conversation surfaced up front.
- [x] Cross-link to RFC-0102 (off-GitHub precedent), RFC-0293 / RFC-0295 (Move #20 companion siblings), RFC-0014, home profile.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (early-stage, no developer surface, privacy, light payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-31 (absence of developer surface documented).
- [x] Provenance `origin: AU`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
