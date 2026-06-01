---
rfc: 0292
title: OhmniLabs / Ohmni integration, research-collab proposal (off-GitHub developer portal)
author: Ido Yahalomi (greenvh@gmail.com)
state: Withdrawn
created: 2026-05-31
updated: 2026-06-01
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

# RFC-0292: OhmniLabs / Ohmni integration, research-collab proposal (off-GitHub developer portal)

No spec change is proposed here. This is an Outreach RFC: it proposes a mapping from URML v0.1 to an existing target's API, not a change to URML's normative surface.

## Summary

URML proposes alignment with OhmniLabs (Ohmni telepresence + home-care robot, US-domiciled) via the **Ohmni Developer Edition** documented at [`docs.ohmnilabs.com`](https://docs.ohmnilabs.com/). The ask is **research-collab**: a documented mapping from URML's substrate-neutral primitive vocabulary to Ohmni's WebAPI and ROS-on-Docker surfaces, with the option of a future `OhmniAdapter` under [`reference/home-runtime/`](../../reference/home-runtime/) once engagement signals confirm the right shape. **Engagement surface is off-GitHub**: the [`ohmnilabs`](https://github.com/ohmnilabs) GitHub org exists but its repositories have been dormant since 2018; the live developer surface is the documentation portal, not GitHub. RFC-0102 (Bear Robotics) is the off-GitHub-courtesy precedent.

## Motivation

OhmniLabs (Santa Clara, CA, USA; default-policy pass) builds Ohmni, a telepresence robot widely used in remote home care, senior connection, healthcare, and education. Ohmni ships a **Developer Edition** with four layers of development API, and an active documentation portal. The home-assistance adjacency is direct: telepresence-for-aging-in-place and remote caregiving sit on the home-assistance continuum that Move #8 opened.

Verified surface (2026-05-31):
- **Ohmni Developer Manual** at [`docs.ohmnilabs.com`](https://docs.ohmnilabs.com/): documents a WebAPI (include `Ohmni.js`), a `bot_shell.js` / Ohmni API layer, an Arduino devkit layer, and **ROS-on-Ohmni via a Docker virtualization layer** (`ohmnilabs/ohmnidev`, `tb_control` images).
- [`ohmnilabs`](https://github.com/ohmnilabs) GitHub org: present, but `ohmni-ros-demo` (Apache-2.0) and `ohmni-devkit-arduino` were last pushed in 2018. Issues are technically enabled but the org is dormant; **the live, maintained surface is the documentation portal**, so URML engages off-GitHub.
- HQ: Santa Clara, CA, USA.

URML's specific value for Ohmni:
- **Substrate-neutral intent above the Ohmni WebAPI / ROS surface.** A URML program describes intent ("go to the kitchen, announce dinner, return to dock"); the Ohmni WebAPI / ROS layer executes it. URML's substrate-Protocol abstraction sits at the intent layer.
- **Natural-language authoring for non-technical caregivers.** A family member authoring a daily check-in routine benefits from URML's Layer-4 path above raw WebAPI calls.
- **ROS-on-Docker fit.** Ohmni's documented ROS layer is a clean target for a URML adapter that reuses URML's ROS 2 reference-runtime machinery rather than a bespoke transport.

## Detailed design (light, research-collab + off-GitHub)

URML's engagement is off-GitHub by default. The proposal is:

1. **Courtesy outreach via OhmniLabs' developer / contact surface** ([`ohmnilabs.com`](https://ohmnilabs.com/) and the `docs.ohmnilabs.com` developer portal). URML's identity, motivation, and feedback questions; light engagement payload; the RFC asks who at OhmniLabs is the right contact for substrate-neutral-orchestration discussion.
2. **If maintainers respond with a substantive engagement signal**, URML proposes an `OhmniAdapter` under [`reference/home-runtime/`](../../reference/home-runtime/) (proposed by [RFC-0100](0100-irobot-roomba-outreach.md)) targeting either the WebAPI or the ROS-on-Docker surface. Adapter integration follows the [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md) pattern: shipped in URML's reference runtime with hermetic fake-SDK tests.
3. **ROS-layer reuse.** Because Ohmni documents ROS-on-Docker, a `OhmniAdapter` can compose with URML's existing ROS 2 reference runtime rather than introducing a new transport. Documented at the URML side, not contingent on Ohmni's response.

### Proposed URML v0.1 to Ohmni mapping (sketch)

| URML primitive | Ohmni realisation |
|---|---|
| `move_to(pose)` | Navigation / drive command via the WebAPI or the ROS `tb_control` layer; manifest declares the mobility model Ohmni exposes. |
| `grasp(...)` / `release(...)` | Not applicable (Ohmni has no manipulator). `gripper: none`. |
| `measure(sensor_id)` | Battery, pose, camera / sensor state via the WebAPI. |
| `wait_for(...)` | Polling on a named event (e.g. `docked`, `arrived`). |
| `report(status)` | Per-session log; optional spoken announcement. |
| `speak` / `listen` (home ext.) | Ohmni's audio + telepresence channel, if exposed to the Developer Edition. |

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **GitHub org dormant since 2018.** The maintained developer surface is the documentation portal, not GitHub; URML frames engagement off-GitHub honestly rather than posting on a near-dead repository.
- **Developer Edition gating.** The Ohmni Developer Edition (Docker / ROS access) may be a paid or licensed tier; substantive adapter work depends on access. The RFC asks for clarification.
- **No manipulation.** Ohmni is a mobile telepresence platform; the URML mapping covers mobility + speech + sensing, not grasping. Named honestly.
- **Light engagement payload.** Off-GitHub courtesy means less detail than a Tier A vendor RFC with a public adapter pre-design; depth comes from OhmniLabs' response.

## Alternatives considered

1. **Post an Issue on the dormant `ohmnilabs` GitHub org.** Rejected; the org has been inactive since 2018 and a post there is unlikely to reach a maintainer, reading as spam rather than outreach.
2. **Ship an `OhmniAdapter` first against the public-documented WebAPI without engaging.** Rejected; the Developer Edition access posture is unclear.
3. **Skip OhmniLabs for Move #20.** Rejected; Ohmni's telepresence-for-aging-in-place positioning is squarely on the home-assistance continuum and it is one of the few US-domiciled home-care platforms with a documented developer API.

## Prior art

- Ohmni Developer Manual at [`docs.ohmnilabs.com`](https://docs.ohmnilabs.com/).
- [`ohmnilabs`](https://github.com/ohmnilabs) GitHub org (dormant since 2018).
- [RFC-0102 (Bear Robotics)](0102-bear-robotics-servi-outreach.md): off-GitHub developer-portal courtesy precedent; senior-living / care-home adjacency.
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md): engagement → adapter-shipment pattern.
- [RFC-0100 (iRobot Roomba)](0100-irobot-roomba-outreach.md): proposes the `reference/home-runtime/` package.

## Unresolved questions

For OhmniLabs developer relations:

1. **Engagement surface.** Is the developer-portal contact form the right channel, a specific dev-relations email, or a different surface?
2. **Developer Edition access posture.** Is WebAPI / ROS-on-Docker access available to integration partners on request, or licensed?
3. **Adapter home.** If URML ships an `OhmniAdapter`, would `reference/home-runtime/` (URML-side) be appropriate, or would OhmniLabs prefer a contributed example?
4. **WebAPI vs ROS target.** Which surface does OhmniLabs recommend a substrate-neutral adapter target?
5. **Speech / telepresence primitives.** Does the Developer Edition expose audio I/O suitable for URML's `speak` / `listen`?
6. **Anything else.**

## Implementation note

RFC-0292 ships as a single RFC document PR. No adapter code in this PR. Research-collab + off-GitHub framing. Ledger entry in [`examples/lighthouses/outreach-move20.yaml`](../../examples/lighthouses/outreach-move20.yaml).

## Requested feedback

Items 1–6 from "Unresolved questions" above.

## How to respond

OhmniLabs' maintained surface is the developer portal at `docs.ohmnilabs.com` and the company site `ohmnilabs.com`. URML's planned channel: courtesy outreach via the developer-portal / company contact surface pointing at this RFC. If OhmniLabs responds with a public GitHub Issue surface or a specific dev-relations email, URML pivots accordingly.

This RFC and any accompanying outreach are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Maintainer response (2026-06-01) — RFC withdrawn

URML sent this outreach on 2026-06-01 and received a templated reply from OhmniLabs Support. The reply reports that **the Ohmni Telepresence Robot is end-of-life as of 2026-01-01**: no ongoing technical support, troubleshooting, parts replacement, or software updates, except where required under active extended warranties. OhmniLabs is now a product line of Symbotic (acquired December 2024), and its currently supported platforms are **OhmniCare** (telehealth) and **OhmniClean** (UV-C disinfection robots). The base cloud at `app.ohmnilabs.com` remains available for calling and basic functionality with no retirement plan, but no new features are planned.

This undercuts the premise of this RFC: the proposed `OhmniAdapter` targeted the telepresence robot's Developer Edition (WebAPI / ROS-on-Docker), which is no longer a supported platform. The two supported lines (telehealth, UV-C disinfection) are outside the home-assistance scope of Move #20.

**Outcome: withdrawn.** No `OhmniAdapter` will be pursued for the telepresence robot. This RFC stays in the directory as an honest record of an outreach that found its target discontinued. A future RFC could revisit a Symbotic/Ohmni surface if URML develops a use case for a currently-supported line, but that is out of scope here. The ledger row in [`examples/lighthouses/outreach-move20.yaml`](../../examples/lighthouses/outreach-move20.yaml) records `response: acked` (templated support reply) with the EOL substance.

## Self-review (Phase 0)

- [x] Off-GitHub + research-collab framing explicit; GitHub dormancy acknowledged honestly.
- [x] ROS-on-Docker surface noted as the clean adapter target.
- [x] Cross-link to RFC-0102 (off-GitHub precedent), RFC-0073 (engagement-to-adapter), RFC-0100 (home-runtime parent).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (dormant GitHub, Developer Edition gating, no manipulation, light payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-31 (GitHub dormancy documented).
- [x] Provenance `origin: US`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
