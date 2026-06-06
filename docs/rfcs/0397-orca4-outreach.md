---
rfc: 0397
title: orca4 integration — request for comment from the orca4 maintainer
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

# RFC-0397: orca4 integration — request for comment from the orca4 maintainer

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainer for feedback. It builds on URML's shipped marine-runtime and ROS 2 runtime.

## Summary

[`orca4`](https://github.com/clydemcqueen/orca4) (MIT, ~186 stars, Issues enabled, very active — an `orca5` successor referenced) is a ROS 2 autonomous underwater vehicle for the BlueROV2, built on ArduSub + Nav2 + mavros. It is the exact vehicle + flight-controller + navigation pairing URML's marine-runtime targets, and one of the most-starred open BlueROV2 autonomy stacks. This RFC asks whether a validated natural-language intent layer above orca4 is interesting and what an AUV manifest should declare.

## The mapping (URML above orca4)

URML sits above orca4 as a validated intent layer; orca4 / ArduSub / Nav2 execute:

- URML's marine-runtime drives a BlueROV2 over ArduSub/MAVLink — orca4's substrate. On the ROS 2 side, orca4's Nav2-based navigation is reached by URML's `move_to` (Nav2 is already a URML substrate from the Move #16 spine work), so a "go to this waypoint at depth and report" intent maps cleanly.
- Validate-before-actuate refuses a request outside the declared depth rating or mission envelope before it dispatches — useful for an untethered AUV mission.
- The split between a URML navigation intent and orca4's mission/behavior logic is a genuine design question worth the maintainer's view.

## What is asked

Request for comment from the orca4 maintainer:

1. What should a URML manifest declare to describe a BlueROV2-class AUV mission honestly (depth rating, mission/area bounds, battery/endurance, comms regime)?
2. Is a validated natural-language layer above orca4 useful, or does the existing mission interface already cover that need?
3. Where is the right seam — URML's `move_to` onto orca4's Nav2 navigation, or higher at the mission level?

Nothing here asks orca4 to adopt, host, or maintain anything.

## Prior art / context

URML's marine-runtime (BlueRovAdapter) and ROS 2 runtime; the Nav2 engagement (Move #16 substrate spine); the sibling BlueROV2 platform `blue` (RFC-0396). orca4 is the most-starred direct-fit vehicle in the marine wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `clydemcqueen/orca4` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move32.yaml`.
