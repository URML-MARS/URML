---
rfc: 0508
title: Husarion UGV (husarion_ugv_ros) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0508: Husarion UGV (husarion_ugv_ros) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the middleware / control / drivers wave (Move #45).

## Summary

[`husarion/husarion_ugv_ros`](https://github.com/husarion/husarion_ugv_ros) (Apache-2.0, ~80 stars, active) is the ROS 2 package set for Husarion's Panther and Lynx mobile robots (the platform HAL and drivers). URML is interesting as the natural-language front door above a concrete UGV's driver stack: "go to the loading bay" becomes a typed `move_to`, validated against the UGV's declared mobility and the deployment's locations, then dispatched onto the existing ROS 2 stack. This RFC asks whether the mapping is useful.

## The mapping (URML beside husarion_ugv_ros)

- **Capability manifest from a real UGV.** Panther / Lynx mobility (drive type, velocity limits) and the deployment's named locations and frames map onto a URML manifest. A `move_to(location)` is validated against it before dispatch.
- **Validated intent, then the Husarion stack.** URML adds the typed intent and the capability/envelope gate; `husarion_ugv_ros` stays the driver/control layer that drives the robot. A `HusarionAdapter` would target the published ROS 2 packages, CI-gated, with hardware validation deferred — the established URML adapter pattern.

## What is asked

Request for comment from the Husarion maintainers:

1. Does mapping a Panther / Lynx UGV (mobility, velocity limits, locations) onto a URML manifest read right?
2. Is an English-to-validated-`move_to` front door above `husarion_ugv_ros` interesting?
3. Which is the cleaner first seam — the manifest mapping, or a `HusarionAdapter` against the ROS 2 packages?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `mobility` block, named-location/frame resolution, the decide-then-do split (RFC-0002), and the mobile-base front-door path. Part of Move #45, the middleware / control / drivers wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `husarion/husarion_ugv_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move45.yaml`.
