---
rfc: 0185
title: Franka Robotics (Panda / FR3 cobot arm) integration, request for comment from frankaemika maintainers
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

# RFC-0185: Franka Robotics (Panda / FR3 cobot arm) integration

## Summary

URML does not yet ship a Franka manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Franka Robotics' Panda / FR3 cobot arms over [`frankaemika/franka_ros2`](https://github.com/frankaemika/franka_ros2) (Apache-2.0), and **requests review and feedback from the frankaemika maintainers**. No spec change.

This RFC is the **correct-layer engagement** for Franka. RFC-0185 was deferred from Move-13 Theme C (open-source actuators + embedded + maker) because Franka is a cobot OEM, not an actuator vendor — Theme B (mobile manipulators + humanoids) is the right placement.

## Motivation

Franka Robotics GmbH (formerly Franka Emika, Munich DE) makes the Panda and FR3 — high-precision research-grade cobot arms widely used in academic robotics labs, manipulation research, and benchmarking pipelines (the Franka Kitchen environment in Open-X-Embodiment, ALOHA fine-tuning, Diffusion Policy demonstrations, etc.). Repo at [`frankaemika/franka_ros2`](https://github.com/frankaemika/franka_ros2) (Apache-2.0, 337 stars, Issues enabled, last commit `2026-05-19` active, **not archived**).

URML benefits from documenting the Franka manifest mapping because:

1. **Franka is the de facto research-cobot reference.** URML's existing cobot-runtime fixtures (`kinova_cobot_cell`, `ur_cell`, `kassow_cobot_cell`, etc.) imply support that Franka completes at the high-precision research class.
2. **Apache-2.0 ROS 2 driver is clean adapter substrate.** URML's `reference/ros2-runtime/` composes naturally; the manifest declares Franka FR3 as the actuator class.
3. **The pick_from / place_at / swap_tool industrial primitives (RFC-0013) dispatch via franka_ros2.** URML's existing primitive vocabulary maps onto Franka's MoveIt + control interfaces.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `franka_fr3_cell.yaml` fixture)

| URML field | Maps to Franka attribute |
|---|---|
| `name` | Specific model (`franka_panda`, `franka_fr3`) |
| `actuators.dof: 7` | 7-DoF revolute (clean fit for URML's cobot pattern) |
| `actuators.precision_class: custom` (`research_grade_high_precision`) | Franka's distinguishing feature — research-grade torque sensing per joint |
| `actuators.payload_kg: 3.0` | Panda / FR3 payload class |
| `safety_envelope` | Franka's CE-certified safety surface composes with URML's RFC-0012 envelope semantics |

### What URML v0.1 does not yet express for Franka

1. **Cobot-arm precision-class declaration.** URML's actuator manifest currently declares DoF + payload but not precision class (research-grade torque sensing per joint vs industrial-grade position-only). Spec RFC queued.
2. **Per-joint torque-sensing declaration.** Franka's distinguishing feature is integrated torque sensors at every joint. URML's manifest cannot today declare this capability.
3. **CE / industrial-safety certification declaration.** Franka FR3 is CE-certified for cobot deployment alongside humans; URML's manifest could declare safety-certification class but does not today.

### Compatibility notes

- **Vendor org.** [`frankaemika`](https://github.com/frankaemika) — Franka Robotics GmbH, Munich DE.
- **Flagship repo.** [`frankaemika/franka_ros2`](https://github.com/frankaemika/franka_ros2) — Apache-2.0, 337 stars, Issues enabled, last commit 2026-05-19 active, **not archived**.
- **Origin.** Franka Robotics GmbH, Munich, Germany. Passes US-federal default policy (NATO+EU).
- **License fit.** Apache-2.0 cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active vendor-direct surface (9 days from cutoff).

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; cobot-arm precision-class + per-joint torque-sensing + safety-certification declaration Spec RFCs queued.
- Reference runtime: future `reference/cobot-runtime/FrankaAdapter` is a candidate — sibling to URML's existing cobot manifest fixtures.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Cobot-arm precision-class Spec RFC prerequisite.**
- **Per-joint torque-sensing declaration is novel manifest territory.**
- **CE certification declaration** is operator-relevant but not first-class in URML v0.1.

## Alternatives considered

1. **Engage Franka at the broader org level.** Considered. `franka_ros2` is the canonical ROS 2 surface; per-flagship engagement is the cleaner shape.
2. **Bundle Franka with sibling Move-14 cobot RFCs (Kinova).** Rejected. Per-vendor RFCs.
3. **Engage on libfranka (the C++ low-level library) instead.** Considered. `franka_ros2` is the URML-compatible boundary; libfranka is the deeper layer for a future engagement.

## Prior art

- [`frankaemika/franka_ros2`](https://github.com/frankaemika/franka_ros2) — the upstream ROS 2 driver.
- URML's existing cobot fixtures (`kinova_cobot_cell.yaml`, `ur_cell.yaml`, `kassow_cobot_cell.yaml`, etc.) — the cobot pattern Franka extends at research-grade precision.
- [RFC-0013 (industrial profile pick_from / place_at / swap_tool)](0013-industrial-pick-place-tool.md) — the URML primitives Franka's MoveIt interfaces dispatch.
- [RFC-0186 (Kinova Robotics)](0186-kinovarobotics-kinova-ros-outreach.md) — sibling Move-14 cobot-arm RFC.
- Open-X-Embodiment, ALOHA, Diffusion Policy — Move-2/11 VLA / DP research targets that use Franka as the benchmark cobot.

## Unresolved questions

For the frankaemika maintainers:

1. **Cobot-arm precision-class manifest fields.** URML's v0.1 actuator manifest doesn't declare precision class. Spec RFC queued. Manifest field expectations from the Franka perspective?
2. **Per-joint torque-sensing declaration.** Franka's distinguishing capability — manifest field shape?
3. **CE / safety-certification declaration.** Should URML's manifest declare safety-certification class?
4. **Adapter home.** URML repo (`reference/cobot-runtime/FrankaAdapter`), Franka-maintained `frankaemika/franka-urml-bridge`, or both?
5. **Conformance listing.** Would Franka Robotics consider a README link to URML's compatible-runtimes registry once a working adapter ships?
6. **Anything else.**

## Implementation note

RFC-0185 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move14.yaml`](../../examples/lighthouses/outreach-move14.yaml).

## How to respond

`frankaemika/franka_ros2` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (Apache-2.0, 337 stars, Issues enabled, last commit 2026-05-19 active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (Spec-RFC prerequisites, novel manifest declarations).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Franka Robotics GmbH DE Munich; default policy passes.
- [x] CLAUDE.md compliance check passed.
