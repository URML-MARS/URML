---
rfc: 0186
title: Kinova Robotics (Jaco / Movo cobot arms) integration, request for comment from Kinovarobotics maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0186: Kinova Robotics (Jaco / Movo cobot arms) integration — staleness + ROS 2 successor ask

## Summary

URML does not yet ship a Kinova-specific manifest fixture or adapter beyond the existing `kinova_cobot_cell` fixture stub. This RFC documents the proposed URML v0.1 capability-manifest mapping for Kinova Robotics' Jaco / Movo cobot arms over [`Kinovarobotics/kinova-ros`](https://github.com/Kinovarobotics/kinova-ros) (BSD-3-Clause), and **requests review and feedback from the Kinovarobotics maintainers**. **Engagement is reactivating-nudge + ROS 2 successor question** — the repo is stale 654 days but carries 410 stars, signaling deployed-fleet adoption. No spec change.

## Motivation

Kinova Robotics (Montreal CA) makes the Jaco (research / assistive-class) and Movo (mobile-manipulator) cobot arms — widely used in assistive-robotics, accessibility-tech, and academic robotics research. Repo at [`Kinovarobotics/kinova-ros`](https://github.com/Kinovarobotics/kinova-ros) (BSD-3-Clause, 410 stars, Issues enabled, last commit `2024-08-12` — **stale 654 days from cutoff 2026-05-28**, **not archived**).

URML's existing `kinova_cobot_cell` manifest fixture implies engagement with the Kinova surface; this RFC closes the loop. The 410-star adoption signal is substantial despite the staleness — Kinova has substantial deployed fleet, particularly in assistive-robotics applications.

Two engagement angles:

1. **Reactivating-nudge.** The 1.5-year staleness on the GitHub surface may reflect Kinova engagement moving to private channels or a successor ROS 2 stack. URML's RFC asks for the canonical engagement-surface guidance.
2. **Assistive-class cobot manifest declaration.** Jaco's distinguishing application is assistive technology (wheelchair-mounted, accessibility deployments); URML's manifest could declare this deployment-class for safety-envelope semantics.

## Detailed design

### URML v0.1 capability-manifest mapping (refines existing `kinova_cobot_cell.yaml` fixture)

| URML field | Maps to Kinova attribute |
|---|---|
| `name` | Specific model (`kinova_jaco2_6dof`, `kinova_jaco2_7dof`, `kinova_gen3`, `kinova_movo`) |
| `actuators.dof` | 6 or 7 DoF (Jaco variants) |
| `actuators.application_class: custom` (`assistive_research`) | Jaco's distinguishing application class |
| `actuators.payload_kg` | Per-model (Jaco2: 1.0-1.6kg; Gen3: 2.0kg+) |
| `mobility.drive_type: custom` (`movo_mobile_base`) | Movo's omnidirectional mobile base (when applicable) |

### What URML v0.1 does not yet express for Kinova

1. **Assistive-application class declaration.** URML's manifest doesn't today declare deployment-class (assistive vs industrial vs research); relevant for safety-envelope defaults.
2. **Cobot-arm precision-class declaration.** Same shared gap as RFC-0185 Franka.
3. **ROS 1 vs ROS 2 successor question.** The `kinova-ros` repo is ROS 1; URML's adapter pattern is ROS 2. If Kinova has a `kinova-ros2` successor, URML's manifest should target that surface instead.

### Compatibility notes

- **Vendor org.** [`Kinovarobotics`](https://github.com/Kinovarobotics) — Kinova Robotics, Montreal CA.
- **Flagship repo.** [`Kinovarobotics/kinova-ros`](https://github.com/Kinovarobotics/kinova-ros) — BSD-3-Clause, 410 stars, Issues enabled, last commit 2024-08-12 (**stale 654 days**), **not archived**.
- **Origin.** Kinova Robotics, Montreal, Canada (CA). Passes US-federal default policy (NATO ally / Five Eyes).
- **License fit.** BSD-3-Clause cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Stale but durable adoption signal (410 stars on a niche cobot driver); engagement is partly a pulse-check.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; assistive-application-class + cobot-arm precision-class Spec RFCs queued.
- Reference runtime: future `reference/cobot-runtime/KinovaAdapter` is a candidate **if** active ROS 2 successor surface exists.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Staleness >1.5 years.** Engagement may yield slow / no response; reactivating-nudge is the realistic posture.
- **ROS 1 vs ROS 2 successor question.** The canonical ROS 2 engagement surface is unclear from the public GitHub presence.
- **Existing `kinova_cobot_cell` fixture stub.** URML already references Kinova at the fixture layer; engagement formalizes the upstream link.

## Alternatives considered

1. **Skip Kinova as the surface is stale.** Rejected. 410 stars + URML's existing fixture imply continued URML-side relevance; engagement is the right shape.
2. **Cross-citation only with no manifest mapping.** Considered. Manifest mapping is the artifact maintainers can evaluate; cross-citation alone is too thin given URML's existing fixture.
3. **Engage via the broader `Kinovarobotics` org instead of the stale repo.** Considered. The kinova-ros repo is the most-starred surface; engagement asks for redirect to the canonical successor if one exists.

## Prior art

- [`Kinovarobotics/kinova-ros`](https://github.com/Kinovarobotics/kinova-ros) — the upstream ROS 1 driver.
- URML's existing `kinova_cobot_cell.yaml` fixture stub — the URML-side declaration this RFC formalizes.
- [RFC-0185 (Franka Robotics)](0185-frankaemika-franka-ros2-outreach.md) — sibling Move-14 cobot-arm RFC at the research-grade precision class.
- [RFC-0013 (industrial profile pick_from / place_at / swap_tool)](0013-industrial-pick-place-tool.md) — the URML primitives Kinova interfaces dispatch.

## Unresolved questions

For the Kinovarobotics maintainers:

1. **Canonical ROS 2 engagement surface.** Is `Kinovarobotics/kinova-ros` the active engagement surface, or has a `kinova-ros2` (or similar) successor moved elsewhere?
2. **Repository status.** Stale 654 days — actively maintained on slower cadence, dormant-but-supported, or has development moved to a successor?
3. **Assistive-application-class manifest fields.** URML's manifest doesn't today declare deployment-class. Manifest field expectations from the Kinova assistive perspective?
4. **Cobot-arm precision-class manifest fields.** Shared question with RFC-0185 Franka.
5. **Adapter home.** URML repo (`reference/cobot-runtime/KinovaAdapter`), Kinova-maintained `Kinovarobotics/kinova-urml-bridge`, or both?
6. **Conformance listing.** Would Kinova consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0186 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move14.yaml`](../../examples/lighthouses/outreach-move14.yaml).

## How to respond

`Kinovarobotics/kinova-ros` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with explicit acknowledgement of the staleness + canonical-engagement-surface ask.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (BSD-3-Clause, 410 stars, Issues enabled, last commit 2024-08-12, stale 654d, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (staleness, ROS 1 vs ROS 2 successor question, existing fixture cross-link).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Kinova Robotics CA Montreal; default policy passes.
- [x] CLAUDE.md compliance check passed.
