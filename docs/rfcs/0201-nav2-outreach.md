---
rfc: 0201
title: Nav2 (ROS 2 Navigation Working Group navigation substrate) integration, request for comment from Nav2 maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0201: Nav2 (ROS 2 Navigation Working Group navigation substrate) integration

## Summary

URML's mobility primitives (`move_to`, `dock`, `scan_area`) dispatch via Nav2 in ROS 2 mobile-base deployments today. This RFC documents the proposed URML v0.1 capability-manifest mapping for Nav2 as URML's canonical ROS 2 navigation substrate, engaged via [`ros-navigation/navigation2`](https://github.com/ros-navigation/navigation2) (Apache-2.0 / BSD-3 mixed), and **requests review and feedback from the Nav2 maintainers**. No spec change.

## Motivation

Nav2 is the canonical ROS 2 navigation stack and the substrate URML's mobility primitives compose against in every mobile-base example. The behavior-tree-driven planning model in Nav2 maps cleanly onto URML's manifest-validated dispatch: URML validates intent before dispatch; Nav2 plans the trajectory and recovers from failure.

Repo at [`ros-navigation/navigation2`](https://github.com/ros-navigation/navigation2) (Apache-2.0 / BSD-3 mixed, 4.3k stars, Issues enabled, last commit `2026-05-28`, **not archived**). ROS 2 Navigation Working Group governance, OSRF-adjacent.

URML benefits from documenting the engagement because:

1. **Mobility-primitive dispatch is Nav2-shaped.** URML's `move_to(target_pose)` translates to a Nav2 navigate-to-pose action; `dock` translates to a Nav2 dock action; `scan_area` composes Nav2 with perception primitives. The semantic surface is Nav2-aligned today.
2. **Behavior-tree composition vs URML manifest validation.** Nav2's behavior-tree composability is a degree of freedom URML's manifest does not yet declare; the engagement is the natural place to gather requirements.
3. **Multi-robot / fleet semantics.** Nav2's costmap, planning, and recovery layers are per-robot today; URML's manifest could declare fleet-level intent ([RFC-0006 multi-robot](0006-multi-robot.md) area).

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_nav2_diffdrive_cell.yaml` fixture)

| URML field | Maps to Nav2 attribute |
|---|---|
| `name` | Deployment handle (`nav2_humble_diffdrive`) |
| `substrate.class: ros2` (RFC-0200) | Parent substrate enum |
| `mobility.dispatch: nav2` | Nav2 as mobility dispatcher |
| `mobility.behavior_tree` | Nav2 behavior tree XML reference |
| `mobility.planner_plugin` | NavfnPlanner / SmacPlanner / Theta* |
| `mobility.controller_plugin` | DWB / RPP / MPPI |
| `mobility.costmap_plugins` | Static / inflation / obstacle / voxel layer list |
| `mobility.recovery_behaviors` | Spin / wait / backup / drive-on-heading |

### What URML v0.1 does not yet express for Nav2

1. **Behavior-tree composition declaration.** URML's manifest treats `mobility.dispatch` as a dispatcher class; the behavior-tree composition degree of freedom is not declared.
2. **Plugin-set declaration.** Planner / controller / costmap / recovery plugin selection; URML's manifest declares only the dispatcher class today.
3. **Multi-robot fleet coordination.** Nav2 is per-robot; URML's manifest could declare fleet-level intent (sibling [RFC-0006 multi-robot](0006-multi-robot.md)).
4. **Behavior-tree-side error propagation.** Nav2 behavior-tree failure modes; URML manifest could declare which failure types are recoverable at manifest-validate time vs Nav2-runtime time.

### Compatibility notes

- **Vendor org.** [`ros-navigation`](https://github.com/ros-navigation) — ROS 2 Navigation Working Group, OSRF-adjacent.
- **Engagement repo.** [`ros-navigation/navigation2`](https://github.com/ros-navigation/navigation2) — Apache-2.0 / BSD-3 mixed, 4.3k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** `ros-navigation/navigation2_tutorials`, `ros-navigation/opennav_docking` — the Nav2 ecosystem.
- **Origin.** ROS 2 Navigation Working Group US (OSRF-adjacent). Passes US-federal default policy.
- **License fit.** Apache-2.0 / BSD-3 mixed; predominantly Apache-2.0. Clean fit.
- **Maintainer signal.** Daily-cadence commits; the canonical ROS 2 navigation stack.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; behavior-tree-composition + plugin-set + fleet-coordination Spec RFCs queued.
- Reference runtime: URML's existing `reference/ros2-runtime/` adapter targets Nav2 today for mobility dispatch; manifest-side Nav2-specific fields are the proposed extension.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Plugin enumeration risk** — Nav2 plugin sets evolve; URML's manifest must remain stable across Nav2 release cuts.
- **Behavior-tree-composition novelty** — URML's first declarative-composition-aware manifest field.

## Alternatives considered

1. **Skip Nav2 manifest fields; let URML stay dispatcher-class-only.** Rejected. The plugin-set degree of freedom is real; ignoring it leaves URML's manifest incomplete for production Nav2 deployments.
2. **Engage Nav2 only after URML's multi-robot RFC lands.** Rejected. Multi-robot is downstream; per-robot Nav2 engagement is the right first step.
3. **Bundle Nav2 with MoveIt 2 in a single dispatch-substrate RFC.** Rejected. Different Working Groups, different primitive shapes (mobility vs manipulation); per-WG RFCs let conversation thread per group.

## Prior art

- [`ros-navigation/navigation2`](https://github.com/ros-navigation/navigation2) — the upstream Nav2 stack (engagement anchor).
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent substrate engagement.
- [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md) — sibling Move-16 batch-2 RFC; manipulation Working Group.
- [RFC-0006 (multi-robot)](0006-multi-robot.md) — URML's multi-robot manifest direction; relevant for Nav2 fleet-coordination future work.

## Unresolved questions

For the Nav2 / ROS 2 Navigation Working Group maintainers:

1. **Behavior-tree composition manifest field.** Should URML's manifest declare a Nav2 behavior-tree XML reference, or is composition always Nav2-side?
2. **Plugin-set manifest fields.** Planner / controller / costmap / recovery plugin selection — manifest-level declaration, or always launch-param?
3. **Fleet-coordination layer.** Where does URML's multi-robot fleet manifest meet Nav2's per-robot stack?
4. **Failure-mode declaration.** Should URML's manifest declare which Nav2 failure types are recoverable at manifest-validate vs Nav2-runtime time?
5. **Adapter home.** `reference/ros2-runtime/` (URML-maintained) targets Nav2 today; should Nav2-specific manifest mapping live in a Nav2-adjacent companion package?
6. **Conformance listing.** Would Nav2 / the ROS 2 Navigation Working Group consider a README link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md)) once a working Nav2 bridge ships?
7. **Anything else.**

## Implementation note

RFC-0201 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`ros-navigation/navigation2` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the mobility-dispatch + Working-Group framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Apache-2.0 / BSD-3 mixed, 4.3k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (plugin enumeration risk, behavior-tree-composition novelty).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: ROS 2 Navigation Working Group US (OSRF-adjacent); default policy passes.
- [x] CLAUDE.md compliance check passed.
