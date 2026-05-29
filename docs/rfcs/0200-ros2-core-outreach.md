---
rfc: 0200
title: ROS 2 core (Open Robotics Foundation primary substrate) integration, request for comment from ROS 2 maintainers
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

# RFC-0200: ROS 2 core (Open Robotics Foundation primary substrate) integration

## Summary

URML ships a ROS 2 reference runtime ([`reference/ros2-runtime/`](../../reference/ros2-runtime/)). This RFC documents the proposed URML v0.1 capability-manifest mapping for ROS 2 as URML's **primary substrate**, engaged foundation-direct at the Open Robotics Foundation layer via [`ros2/ros2`](https://github.com/ros2/ros2) (multi-license per module), and **requests review and feedback from the ROS 2 maintainers**. No spec change.

**This is the most identity-load-bearing engagement in Move-16.** URML's primary substrate is ROS 2; the reference runtime already exists; this RFC formalizes the engagement-channel upstream at the foundation layer.

## Motivation

ROS 2 is URML's primary substrate. The `reference/ros2-runtime/` Python package translates URML programs into rclpy actions, services, and topics; the conformance suite asserts the translation semantics. Every URML demo in `examples/` that touches a real robot threads through ROS 2 today.

Repo at [`ros2/ros2`](https://github.com/ros2/ros2) (multi-license per module, 5.5k stars, Issues enabled, last commit `2026-05-28`, **not archived**). Open Robotics Foundation governance under the Linux Foundation umbrella.

URML benefits from documenting the engagement because:

1. **URML's primary substrate engagement should be explicit.** Fifteen prior moves engaged vendors and tools composing above ROS 2; Move-16 RFC-0200 engages the ROS 2 maintainers themselves. URML's substrate-neutral claim ("ROS 2 is the first reference runtime because its community is largest; URML works everywhere", per [`CLAUDE.md`](../../CLAUDE.md)) depends on this being a real conversation, not implicit.
2. **Manifest formalization at the foundation layer.** URML's manifest declares `substrate.class: ros2` and `substrate.distro: humble | iron | jazzy | rolling`; the field shape benefits from ROS 2 maintainer review against actual distro-evolution patterns.
3. **Adapter-home convention.** The reference runtime lives in this repo today (in-repo per [`CONTRIBUTING.md`](../../CONTRIBUTING.md)); the question of whether ROS 2 core, OSRF, or a future Foundation home is the right long-term venue benefits from upstream input.

## Detailed design

### URML v0.1 capability-manifest mapping (the existing `reference/ros2-runtime/` adapter)

| URML field | Maps to ROS 2 attribute |
|---|---|
| `name` | Deployment handle (`ros2_humble_turtlebot4`) |
| `substrate.class: ros2` | URML's primary substrate enum value |
| `substrate.distro` | ROS 2 distro (humble / iron / jazzy / rolling) |
| `substrate.rmw_implementation` | RMW layer (default: Fast DDS sibling RFC-0203 or Cyclone DDS sibling RFC-0204) |
| `node_namespace` | ROS 2 namespace for URML-emitted nodes |
| `qos.reliability` / `qos.durability` / `qos.history` | ROS 2 QoS profile fields surfaced through URML |
| `mobility.dispatch: nav2` | Sibling RFC-0201; navigation stack binding |
| `manipulation.dispatch: moveit2` | Sibling RFC-0202; manipulation stack binding |

### What URML v0.1 does not yet express for ROS 2

1. **Distro evolution semantics.** URML's manifest declares `distro` but lacks distro-deprecation / EOL signaling. ROS 2 maintainers' input on distro lifecycle for manifest semantics.
2. **RMW-implementation substitution.** URML's manifest declares `rmw_implementation`; what does runtime substitution look like (env var, launch param, manifest override)?
3. **Composable-node declaration.** ROS 2 component-container architecture (intra-process zero-copy via [iceoryx](https://github.com/eclipse-iceoryx/iceoryx) sibling RFC-0210) is not expressible in URML's manifest today.
4. **Action-server vs service-call semantics.** URML's Layer-2 primitives dispatch to one or the other implicitly; manifest could declare per-primitive override.
5. **Distro-locked package version pinning.** Determinism RFC future work.

### Compatibility notes

- **Vendor org.** [`ros2`](https://github.com/ros2) — Open Robotics Foundation / Linux Foundation Robotics governance.
- **Engagement repo.** [`ros2/ros2`](https://github.com/ros2/ros2) — multi-license per module, 5.5k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** `ros2/rclcpp`, `ros2/rclpy`, `ros2/rmw`, `ros2/launch`, `ros2/rosbag2` — the ROS 2 core ecosystem.
- **Origin.** Open Robotics Foundation US; Linux Foundation Robotics. Passes US-federal default policy.
- **License fit.** Multi-license per module (predominantly Apache-2.0 and BSD-3-Clause). Clean fit.
- **Maintainer signal.** Daily-cadence commits; the dominant open robotics middleware.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; distro / rmw-implementation / composable-node / action-vs-service Spec RFCs queued.
- Reference runtime: `reference/ros2-runtime/` already ships; this RFC formalizes its engagement-channel upstream rather than adding new code.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only). The existing `reference/ros2-runtime/` adapter is unchanged.

## Drawbacks

- **Proposal-only.**
- **Identity-load-bearing** — URML's primary substrate engagement is now an explicit open question; the substrate-neutral claim is tested against the maintainer group itself.
- **Multi-RFC dependency surface** — RMW substitution (sibling RFCs 0203 Fast DDS, 0204 Cyclone DDS) and dispatch (sibling RFCs 0201 Nav2, 0202 MoveIt 2) are all in-flight in the same wave.
- **Distro evolution risk** — URML's manifest must remain stable across ROS 2 distro cuts.

## Alternatives considered

1. **Skip the foundation engagement; lean on the existing reference runtime.** Rejected. URML's substrate-neutral claim is explicit only if engaged explicitly; an existing adapter is necessary but not sufficient.
2. **Engage at the OSRF Discourse or REP / PEP review process instead.** Considered. The GitHub Issues surface on `ros2/ros2` is the lowest-friction first-contact channel; downstream REP or OSRF-Discourse threads remain open if the maintainers prefer.
3. **Bundle ROS 2 core with Nav2 + MoveIt 2 in a single RFC.** Rejected. Different working groups (OSRF core vs ROS 2 Navigation WG vs MoveIt WG); per-WG RFCs let conversation thread per group.

## Prior art

- [`ros2/ros2`](https://github.com/ros2/ros2) — the upstream ROS 2 metapackage (engagement anchor).
- [`reference/ros2-runtime/`](../../reference/ros2-runtime/) — URML's existing ROS 2 reference runtime.
- [RFC-0001 (architecture overview)](0001-architecture.md) — URML's layered architecture; ROS 2 named as primary substrate.
- [RFC-0014 (substrate conformance)](0014-conformance.md) — URML's substrate-conformance framework.
- [RFC-0201 (Nav2 outreach)](0201-nav2-outreach.md), [RFC-0202 (MoveIt 2 outreach)](0202-moveit2-outreach.md), [RFC-0203 (Fast DDS outreach)](0203-fast-dds-outreach.md), [RFC-0204 (Cyclone DDS outreach)](0204-cyclone-dds-outreach.md) — sibling Move-16 batch-2 RFCs.

## Unresolved questions

For the ROS 2 / OSRF maintainers:

1. **Distro-evolution manifest semantics.** What does ROS 2 distro lifecycle look like in URML's manifest field? Per-distro EOL signaling needed at validate time?
2. **RMW-implementation substitution surface.** Manifest field, launch param, env var, or per-node component-container? URML's preferred default surface.
3. **Composable-node declaration.** Should URML's manifest declare intent-to-compose, or is that always launch-time?
4. **Action vs service dispatch.** Per-primitive override at the manifest layer, or always ROS 2-side?
5. **Adapter home.** `reference/ros2-runtime/` in URML's repo today; long-term — OSRF, Open Robotics Foundation, future URML Foundation, or some combination?
6. **REP / PEP cross-link.** Is there an existing REP or PEP that URML's manifest field semantics should align with explicitly?
7. **Conformance listing.** Would the ROS 2 ecosystem consider a `ros.org` link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0200 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`ros2/ros2` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the primary-substrate + foundation-direct framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (multi-license per module, 5.5k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (identity-load-bearing, multi-RFC dependency surface, distro evolution risk).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Open Robotics Foundation / Linux Foundation Robotics governance; default policy passes.
- [x] CLAUDE.md compliance check passed.
