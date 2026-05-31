---
rfc: 0294
title: Labrador Systems / Retriever integration, research-collab proposal (off-GitHub)
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

# RFC-0294: Labrador Systems / Retriever integration, research-collab proposal (off-GitHub)

No spec change is proposed here. This is an Outreach RFC: it proposes a future mapping from URML v0.1 to an existing target, not a change to URML's normative surface.

## Summary

URML proposes courtesy alignment with Labrador Systems (the Labrador Retriever assistive home robot, US-domiciled). The ask is **research-collab**: a documented intent of how URML's substrate-neutral primitive vocabulary would map to a Labrador assistance routine, and a question to Labrador about whether a developer surface exists or is planned. **Engagement surface is off-GitHub**: Labrador publishes no public developer API, SDK, or GitHub org at this time; the channel is the company contact surface. RFC-0102 (Bear Robotics) is the off-GitHub-courtesy precedent. Of all Move #20 targets, Labrador is the closest pure home-assistance fit.

## Motivation

Labrador Systems (Oak Park, CA, USA; default-policy pass) builds the Labrador Retriever, an assistive home robot designed to help people live independently: delivering meals, moving laundry, and keeping daily-use items within reach. It is commanded by app, voice (including via Alexa-enabled devices), or a preset schedule, and it navigates to saved locations ("bus stops") in the home.

This is the archetype of URML's home-assistance frame: a non-technical user expressing a daily-living intent ("bring my medication tray to the recliner at 9am") that compiles to a small set of validated primitives plus a delivery dispatch.

Verified surface (2026-05-31):
- Company: [`labradorsystems.com`](https://labradorsystems.com/). Product pages, reservation flow, company contact.
- **No public developer API, SDK, or GitHub org located.** Control surfaces named publicly are the consumer app, voice assistants, and scheduling. Engagement is off-GitHub.
- HQ: Oak Park, CA, USA.

URML's specific value, if a developer surface ever opens:
- **Natural-language daily-living routines** above a delivery platform, validated before dispatch.
- **Cross-platform retargetability** across assistive home platforms by manifest swap.
- **Home-profile fit.** The Retriever's "navigate to a saved location and deliver" model maps cleanly onto region-based `move_to` plus `report`, with the 0.5 m/s home-profile velocity ceiling already matching a human-occupied-space assistive robot.

## Detailed design (light, research-collab + off-GitHub)

1. **Courtesy outreach via the Labrador company contact surface.** URML's identity, motivation, and one question: does Labrador expose (or plan) any developer / integration surface a substrate-neutral language could target? Light payload.
2. **If a developer surface exists or opens**, URML proposes a future `LabradorAdapter` under [`reference/home-runtime/`](../../reference/home-runtime/) (proposed by [RFC-0100](0100-irobot-roomba-outreach.md)), targeting whatever Labrador documents. No adapter is proposed against a private surface.
3. **Mapping sketch** (region-based delivery): `move_to(saved_location)` → drive to a Retriever bus-stop; `measure(...)` → battery / tray / position; `wait_for(...)` → arrival / dock; `report(...)` → status; manipulation declared `not_applicable` (the Retriever is a self-loading tray platform, not a manipulator).

## Backward compatibility

Pre-v1.0. Purely additive if ever implemented. Zero URML code in this RFC.

## Drawbacks

- **No verified developer surface.** Labrador has not published an API / SDK / GitHub org. URML documents this honestly; this RFC is a courtesy + question, not an adapter pre-design.
- **Consumer-only control today.** App / voice / schedule are end-user surfaces, not integration surfaces. A substrate-neutral adapter depends on a developer surface that may not exist.
- **Light engagement payload.** Depth depends entirely on Labrador's response.

## Alternatives considered

1. **Reverse-engineer the consumer app surface and ship an adapter.** Rejected; brittle, non-portable, and contrary to URML's validator-first posture.
2. **Skip Labrador until a developer surface is announced.** Considered, rejected; a courtesy touch puts URML on Labrador's radar and the home-assistance fit is the strongest in Move #20.
3. **Fold Labrador into the Bear Robotics RFC.** Rejected; different vertical (in-home daily living vs hospitality / senior-living dining) and different (absent) surface.

## Prior art

- [`labradorsystems.com`](https://labradorsystems.com/).
- [RFC-0102 (Bear Robotics)](0102-bear-robotics-servi-outreach.md): off-GitHub courtesy precedent; senior-living adjacency.
- [RFC-0100 (iRobot Roomba)](0100-irobot-roomba-outreach.md): home-runtime parent; consumer-product-without-vendor-API engagement pattern.
- [`spec/profiles/home/`](../../spec/profiles/home/): the home profile and its 0.5 m/s human-occupied-space velocity ceiling.

## Unresolved questions

For Labrador Systems:

1. **Developer surface.** Does Labrador expose (or plan) any API / SDK / integration surface a third party could target?
2. **Engagement channel.** Is the company contact form the right surface, or is there a dev-relations / partnerships contact?
3. **Mobility model.** Is "navigate to saved bus-stops" the right characterization for a URML region-based mobility manifest?
4. **Home-assistance framing.** Is URML's substrate-neutral natural-language layer of interest to Labrador's product side?
5. **Anything else.**

## Implementation note

RFC-0294 ships as a single RFC document PR. No adapter code in this PR. Research-collab + off-GitHub framing. Ledger entry in [`examples/lighthouses/outreach-move20.yaml`](../../examples/lighthouses/outreach-move20.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

Labrador's contact surface is [`labradorsystems.com`](https://labradorsystems.com/). URML's planned channel: a courtesy message via the company contact surface pointing at this RFC. If Labrador responds with a developer surface or a specific contact, URML pivots accordingly.

This RFC and any accompanying outreach are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub + research-collab framing explicit; absence of a developer surface acknowledged honestly.
- [x] Strongest pure home-assistance fit in Move #20 stated without overclaiming a surface.
- [x] Cross-link to RFC-0102 (off-GitHub precedent), RFC-0100 (home-runtime parent), home profile.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no developer surface, consumer-only control, light payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-31 (absence of developer surface documented).
- [x] Provenance `origin: US`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
