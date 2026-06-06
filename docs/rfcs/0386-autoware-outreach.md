---
rfc: 0386
title: Autoware integration — request for comment from the Autoware community
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0386: Autoware integration — request for comment from the Autoware community

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment that proposes how URML v0.1 maps onto an existing target, and asks that target's maintainers for feedback. The normative surface it builds on, [RFC-0020](0020-autoware-av-substrate.md) (the research-grade `av` profile and the `plan_path` / `follow_trajectory` primitives), already shipped (Implemented 2026-06-06); this RFC is the conversation with Autoware now that there is a concrete artifact to show.

## Summary

[Autoware](https://github.com/autowarefoundation/autoware) (Autoware Foundation, Apache-2.0, ~11.7k stars, the leading open-source autonomous-driving stack) is named in URML's manifesto as a Layer-0 target. URML's `av` profile (RFC-0020) was designed against Autoware's operational model: `plan_path` is a compute verb that cost-maps a trajectory, and `follow_trajectory` executes it. This RFC maps those onto Autoware's pipeline and asks the maintainers whether the mapping is faithful and whether a thin URML intent layer above Autoware is interesting to the community.

## The mapping (URML above Autoware)

URML sits one layer above Autoware as a substrate-neutral, validated intent vocabulary. It does not replace any Autoware component; it declares intent and a capability/ODD envelope, validates a request before dispatch, then hands off:

- `plan_path(from, to, along)` → Autoware's planning pipeline (`mission_planner` → `behavior_path_planner` / `behavior_velocity_planner` → `motion_planner`). It binds the planned trajectory; it does not actuate.
- `follow_trajectory($route, speed_envelope)` → Autoware's control stack (`pure_pursuit` / MPC controllers). The only URML verb that actuates.
- The `av` manifest block declares the HD map (format-neutral; Lanelet2 is Autoware's), the ODD (speed cap, regions), and the Minimum-Risk Maneuver. URML's validator checks a trajectory's speed envelope against the ODD cap before dispatch and that `follow_trajectory` consumes a `plan_path`-produced trajectory.

URML is explicitly **research-grade** for AV (`production_safety_certified: false`); it does not certify autonomous-vehicle safety and makes no SOTIF / UNECE-R157 claim. The value offered is an honest, validated, human-readable intent layer for research, simulation, and demonstration, with the validate-before-actuate guarantee.

## What is asked

Request for comment from Autoware maintainers:

1. Is the `plan_path` → planning, `follow_trajectory` → control mapping faithful to Autoware's architecture, or does it mis-model the mission/behavior/motion split?
2. What should a URML `av` manifest declare to honestly describe an Autoware deployment's ODD (beyond a speed cap and regions)?
3. Where is the right seam for a URML→Autoware adapter — the planning/trajectory ROS 2 interface, or higher (the mission interface)?

Nothing here asks Autoware to adopt, host, or maintain anything. A future `reference/autoware-runtime/` adapter is URML's to build and maintain.

## Prior art / context

RFC-0020 (the `av` profile this binds); RFC-0042 (Waymo Motion Dataset) and RFC-0040-family (CARLA) are the recorded-driving and simulator vertices of URML's AV triangle, of which Autoware is the runtime vertex. Autoware Universe houses the component implementations referenced above.

## Implementation note

Outreach only. The artifact already exists (RFC-0020, shipped). The post is a GitHub Discussion (or Issue) on `autowarefoundation/autoware` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the repo is Apache-2.0). Tracked in `examples/lighthouses/outreach-move30.yaml`.
