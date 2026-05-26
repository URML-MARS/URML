---
rfc: 0096
title: INRAE Romea integration, research-collab proposal to Romea maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-26
updated: 2026-05-26
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

# RFC-0096: INRAE Romea integration, research-collab proposal to Romea maintainers

## Summary

URML proposes alignment with INRAE Romea (Robotique et mobilité pour l'environnement et l'agriculture) via the [`Romea` GitHub org](https://github.com/Romea) (79 public repos, 19 followers, Apache-2.0 predominant). The ask is **research-collab**: URML's substrate-neutral primitive vocabulary as a complementary intent layer above Romea's ROS 2-native agriculture-robotics stack (`romea-ros2`, `romea_controllers`, `four_wheel_steering_tools`, `cropcraft` procedural-world generator). No spec change on URML's side. Fifth Move #7 RFC; the EU-academic counterpart to RFC-0095 (UCLA AgriCruiser).

## Motivation

INRAE Romea is the **strongest EU-academic ag-robotics surface** in URML's outreach landscape. ROS 2 native, Apache-2.0 predominant license, 79 public repos with active maintenance through May 2026, and a flagship `cropcraft` procedural world generator (105 stars) used by the ag-robotics simulation community.

Verified surface (2026-05-26):
- `Romea` GitHub org: 79 public repos, 19 followers.
- Top-starred: `cropcraft` (105 stars, Python, procedural world generator for agricultural robotics simulation), `romea_controllers` (7 stars, C++, archived), `four_wheel_steering_tools` (3 stars, C++, archived), `romea-ros2-localisation-imu-plugin` (3 stars, C++), `romea-ros2-mobile-base` (2 stars, C++).
- License pattern: Apache-2.0 most common; LGPL-3.0 on the `hunter` repository.
- Last commit on `romea-ros2-joy`: 2026-05-22 (actively maintained as of three days before this RFC drafts).
- INRAE is France's National Research Institute for Agriculture, Food and Environment.

URML's specific value for INRAE Romea:
- **ROS 2 + Apache-2.0 license alignment.** Direct composition with URML's existing ROS 2 substrate path. No license-fit nuance (URML's `reference/` is Apache-2.0 too; cross-citation and direct adapter integration are both clean).
- **Cropcraft simulation cross-link.** URML's reference runtimes ship hermetic test lanes against simulated substrates; cropcraft's procedural world generator is a candidate complement for the agriculture-runtime conformance test fixtures.
- **EU-academic agriculture-robotics gateway.** A documented URML cross-citation in `cropcraft` or `romea-ros2-mobile-base` reaches the broader EU ag-robotics research community (including Wageningen Field Robot Event participants, see [RFC-0099 (Wageningen FRE)](0099-wageningen-field-robot-event-outreach.md)).
- **Multi-platform mobility coverage.** `romea-ros2-mobile-base` plus `four_wheel_steering_tools` covers four-wheel-steering platforms that URML's existing `reference/mobile-runtime/` does not yet target. The cross-link is composition, not competition.

## Detailed design (light, research-collab)

URML proposes:

1. **`cropcraft` cross-link.** A documented note that URML's hermetic conformance test fixtures for `agriculture-runtime` can compose with `cropcraft`-generated worlds. The cross-link is documentation, not code.
2. **`romea-ros2-mobile-base` composition.** URML's mobile-runtime sub-package for four-wheel-steering platforms can compose with Romea's ROS 2 mobile-base layer. URML's `move_to` primitive dispatches via Romea's published topics; a documented mapping is paper-worthy.
3. **Cross-link to RFC-0095 (UCLA AgriCruiser).** US + EU academic ag-rover counterparts; URML's substrate-neutral story across both is the natural value proposition.
4. **Future `spec/profiles/agriculture/` co-design.** RFC-0067 raised this; INRAE Romea is a candidate research input alongside AgriCruiser, FarmBot, and the Wageningen FRE community.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No URML code in this RFC.

## Drawbacks

- **Proposal-only.**
- **Two top-3 `romea_controllers` + `four_wheel_steering_tools` repos are archived.** URML's adapter should target the actively-maintained successor packages (`romea-ros2-*`, `cropcraft`); the RFC asks the maintainers to confirm the canonical first-class repos.
- **79-repo org is hard to navigate.** Same maintenance posture as RFC-0086 (ETH ASL, 458 repos): URML's RFC documents top repos but asks maintainers for the canonical entry points.
- **Star counts are small but the org is active.** The institutional value is the INRAE research network and the cropcraft simulation work, not GitHub repo stars.
- **Language fluency.** Romea's documentation is mostly English on GitHub; substantive technical discussion welcome in either English or French.

## Alternatives considered

1. **Ship an `EthRomeaAdapter` or `RomeaAdapter` in URML's `reference/`.** Rejected as too narrow a framing. Romea is a 79-repo ROS 2 ecosystem, not a single product; URML's composition is at the documentation + cropcraft-conformance-fixture level first, with adapter code following maintainer guidance on which packages are first-class.
2. **Fold INRAE Romea into RFC-0095 (UCLA AgriCruiser) as one ag-academic RFC.** Rejected; different countries, different research institutions, different funding sources, different software stacks (C++ controller vs ROS 2 ecosystem). Conflating obscures both engagements.

## Prior art

- `Romea` GitHub org (79 public repos, 19 followers, Apache-2.0 predominant + LGPL-3.0 on hunter).
- `Romea/cropcraft` (105 stars, Python procedural ag-sim world generator).
- `Romea/romea_controllers` (7 stars, C++, archived).
- `Romea/four_wheel_steering_tools` (3 stars, C++, archived).
- `Romea/romea-ros2-localisation-imu-plugin` (3 stars, active).
- `Romea/romea-ros2-mobile-base` (2 stars, active).
- INRAE (French National Research Institute for Agriculture, Food and Environment).
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Acorn)](0092-twisted-fields-acorn-outreach.md), [RFC-0094 (Burro)](0094-burro-robotics-outreach.md), [RFC-0095 (UCLA AgriCruiser)](0095-ucla-agricruiser-outreach.md): agriculture-vertical precedents.
- [RFC-0099 (Wageningen FRE)](0099-wageningen-field-robot-event-outreach.md): parallel EU ag-research-community RFC.
- [RFC-0086 (ETH ASL)](0086-eth-asl-outreach.md): large-ROS-2-org template precedent.

## Unresolved questions

For the INRAE Romea maintainers:

1. **Canonical first-class repos.** Of the 79 repos in the Romea org, which are the canonical first-class entry points for URML's substrate-neutral story?
2. **`romea_controllers` + `four_wheel_steering_tools` archive status.** Are these archived because replaced by the `romea-ros2-*` family, or for different reasons?
3. **`cropcraft` conformance-fixture composition.** Interest in URML documenting `cropcraft` worlds as conformance-test fixtures for `reference/agriculture-runtime/`?
4. **Cross-link to AgriCruiser + Wageningen FRE.** Is there interest in coordinating across the ag-robotics research community URML's Move #7 reaches?
5. **Agriculture-profile co-design.** RFC-0067 raised this; INRAE Romea is a candidate input.
6. **Language fluency.** English or French for substantive technical discussion?
7. **Conformance lane.** Open to a URML conformance line on the `cropcraft` or `romea-ros2-mobile-base` README?
8. **Anything else.**

## Implementation note

RFC-0096 ships as a single RFC document PR. No code in this PR. Research-collab framing. Fifth Move #7 RFC; URML's strongest EU-academic agriculture engagement. Ledger entry in [`examples/lighthouses/outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml).

## Requested feedback

Items 1–8 from "Unresolved questions" above.

## How to respond

`Romea/cropcraft` is the most-visible repo at 105 stars (verified 2026-05-26). URML's planned channel: open a single Issue on `Romea/cropcraft` or `romea-ros2-mobile-base` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional cross-reference on `romea-ros2-localisation-imu-plugin` if maintainers prefer to thread there.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] ROS 2 + Apache-2.0 license alignment surfaced.
- [x] cropcraft conformance-fixture composition framed honestly (documentation, not code).
- [x] Cross-link to RFC-0067 / RFC-0092 / RFC-0094 / RFC-0095 / RFC-0099 explicit.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, archived top repos, 79-repo navigation, small star counts, language fluency).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: FR`; default policy passes.
- [x] CLAUDE.md compliance check passed.
