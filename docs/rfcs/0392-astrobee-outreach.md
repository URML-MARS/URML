---
rfc: 0392
title: Astrobee (NASA) integration — request for comment from the Astrobee maintainers
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

# RFC-0392: Astrobee (NASA) integration — request for comment from the Astrobee maintainers

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's shipped ROS 2 runtime and validate-before-actuate discipline.

## Summary

[Astrobee](https://github.com/nasa/astrobee) (NASA Ames, Apache-2.0, ~1.4k stars) is the family of free-flying robots aboard the ISS, with a ROS-based flight software stack and a simulator. It is a flagship ROS space robot, and exactly the kind of platform a substrate-neutral, validated intent layer should be able to sit above honestly. This RFC asks the Astrobee maintainers what a free-flyer capability declaration should carry and whether a URML demonstration is of interest.

## The mapping (URML above Astrobee)

URML sits above Astrobee's stack as a validated intent layer; Astrobee's flight software executes:

- URML's ROS runtime targets Astrobee's ROS surface; navigation, perception, and reporting intents map onto the existing command/action interface.
- The validate-before-actuate guarantee is the point in a crewed-vehicle context: a request that exceeds the declared capability manifest (a keep-out zone, a propulsion or speed limit, a docking-state precondition) is refused before it dispatches.
- The free-flyer shape stresses URML's manifest in a useful way: what a microgravity, station-keeping, keep-out-zone-bounded robot must declare is a genuine design question.

## What is asked

Request for comment from Astrobee maintainers:

1. What should a URML capability manifest declare to honestly describe a free-flyer (keep-out zones, propulsion / speed limits, docking-state preconditions, bay constraints)?
2. Is a validated natural-language intent layer above Astrobee's stack interesting for ground-side operations or research/education use?
3. Where is the right seam for a URML → Astrobee demonstration in the simulator?

Nothing here asks Astrobee to adopt, host, or maintain anything.

## Prior art / context

URML's ROS 2 reference runtime; the Space-ROS engagement ([RFC-0388](0388-space-ros-outreach.md)) as the sibling space-ROS target. Astrobee is the crewed-vehicle free-flyer vertex of the space wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `nasa/astrobee` (Discussions are not enabled there) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move31.yaml`.
