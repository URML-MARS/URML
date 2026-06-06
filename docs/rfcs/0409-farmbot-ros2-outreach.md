---
rfc: 0409
title: FarmBot-ROS2 (AURA / Maynooth) integration — request for comment
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

# RFC-0409: FarmBot-ROS2 (AURA / Maynooth) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime. It anchors one engagement on the `farmbot-ros` org (the [`interfaces`](https://github.com/farmbot-ros/interfaces) repo) rather than posting to each module.

## Summary

The `farmbot-ros` project (AURA / Maynooth University; MIT) is a modular ROS 2 Humble re-implementation of FarmBot control (cartograph / trailblazer / taskforce / polestar and a shared `interfaces` package). Where FarmBot's own stack (RFC-0404) is bound via its sequence API, FarmBot-ROS2 is a pure ROS 2 agricultural control stack that URML's ROS 2 runtime targets directly. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above FarmBot-ROS2)

URML sits above the ROS 2 stack as a validated intent layer:

- URML's ROS 2 runtime meets `farmbot-ros` on its ROS 2 action/service surface; a "seed bed 2 and water it" intent lowers onto the cartograph / taskforce modules.
- The shared `interfaces` package is the natural place to align URML's typed intent with the project's message contracts (target the standard interfaces, the Nav2 / ros2_control pattern).
- Validate-before-actuate refuses an undeclared tool or out-of-bounds coordinate before dispatch.

## What is asked

Request for comment from the FarmBot-ROS2 (AURA / Maynooth) maintainers:

1. Does URML's typed intent map cleanly onto the `interfaces` message contracts, and where should it target them rather than a generic ROS surface?
2. What should a URML capability manifest declare to describe a FarmBot-class gantry in ROS 2 (bed geometry, tool set, plant vocabulary, coordinate bounds)?
3. Is a validated natural-language layer interesting for the project?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the Nav2 (Move #16) / ros2_control (Move #23) pattern of targeting standard interfaces; the sibling FarmBot engagement (RFC-0404) on the non-ROS FarmBot stack. This is the ROS 2 FarmBot vertex of the agriculture wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `farmbot-ros/interfaces` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). The sibling module repos are referenced, not posted to separately (org-anchor). Tracked in `examples/lighthouses/outreach-move33.yaml`.
