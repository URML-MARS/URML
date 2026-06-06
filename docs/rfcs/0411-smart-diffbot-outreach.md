---
rfc: 0411
title: smart_diffbot (Saxion) integration — request for comment
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

# RFC-0411: smart_diffbot (Saxion) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime and the Nav2 engagement (Move #16).

## Summary

[`SaxionMechatronics/smart_diffbot`](https://github.com/SaxionMechatronics/smart_diffbot) (Apache-2.0, ~17 stars, active) is a ROS 2 differential-drive robot with Nav2-based outdoor GNSS navigation — a small, clean, permissively-licensed platform that fits URML's Nav2-targeting runtime exactly. It is a Tier-B but low-risk engagement: an outdoor GNSS rover is a common agricultural / field-robot shape. This RFC asks whether a validated intent layer above it is interesting.

## The mapping (URML above smart_diffbot)

URML sits above the robot as a validated intent layer:

- URML's `move_to` lowers onto smart_diffbot's Nav2 navigation (Nav2 is already a URML substrate from the Move #16 spine work), so "drive to this GNSS waypoint and report" maps cleanly.
- Validate-before-actuate refuses a request outside the declared speed / area envelope before the rover moves.
- The outdoor-GNSS shape is a useful, minimal manifest case (drive type, speed limits, GNSS frame, field boundaries).

## What is asked

Request for comment from the smart_diffbot maintainers:

1. Is URML's `move_to`-onto-Nav2 mapping the right seam for an outdoor GNSS rover?
2. What should a URML manifest declare to describe an outdoor GNSS diff-drive robot honestly (drive type, speed limits, GNSS frame, geofence / field boundaries)?
3. Is a validated natural-language layer interesting as a teaching / demonstration add-on?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 runtime; the Nav2 engagement (Move #16). smart_diffbot is the small, clean outdoor-GNSS vertex of the agriculture wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `SaxionMechatronics/smart_diffbot` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move33.yaml`.
