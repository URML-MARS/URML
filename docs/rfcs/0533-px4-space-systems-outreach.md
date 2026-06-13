---
rfc: 0533
title: PX4-Space-Systems integration — request for comment
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

# RFC-0533: PX4-Space-Systems integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48).

## Summary

[`DISCOWER/PX4-Space-Systems`](https://github.com/DISCOWER/PX4-Space-Systems) (BSD-3-Clause, active, KTH Space Robotics Lab) is a PX4 fork for space free-flyer systems (the ATMOS air-bearing testbed; PX4 + ROS 2). URML already targets PX4 as a substrate (the PX4 runtime / PX4Adapter), and this fork extends that frame to free-flyers: a validated URML intent dispatched to a PX4-based space platform. This RFC asks whether the mapping is useful.

## The mapping (URML beside PX4-Space-Systems)

- **A known substrate, new domain.** URML's PX4Adapter dispatches validated intent to a PX4 autopilot. A free-flyer running PX4-Space-Systems is the same substrate in a microgravity domain: the manifest declares the free-flyer's mobility and constraints, and URML validates intent against them before dispatch.
- **Reuses the substrate seam.** This is not a new mechanism; it is URML's existing PX4 substrate mapping applied to a space free-flyer.

## What is asked

Request for comment from the DISCOWER maintainers:

1. Does URML's existing PX4 substrate mapping extend cleanly to a PX4-based free-flyer?
2. What does a free-flyer manifest need that a drone manifest does not (microgravity mobility, attitude/translation constraints)?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's PX4 runtime / PX4Adapter and the drone profile, the space engagements (Move #31), and the decide-then-do split (RFC-0002). Part of Move #48.

## Implementation note

Outreach only. The post is a GitHub Issue on `DISCOWER/PX4-Space-Systems` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
