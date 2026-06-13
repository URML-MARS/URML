---
rfc: 0531
title: Project 11 integration — request for comment
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

# RFC-0531: Project 11 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the domain / standards / conceptual-peer wave (Move #48).

## Summary

[`CCOMJHC/project11`](https://github.com/CCOMJHC/project11) (BSD-2-Clause, active, UNH Center for Coastal & Ocean Mapping) is a ROS backseat-driver framework for Autonomous Surface Vehicles, with mission and helm managers (ROS 2 Jazzy). URML is interesting as the front door above the mission manager: a survey mission becomes a typed, validated URML program that the Project 11 mission manager executes. This RFC asks whether the mapping is useful.

## The mapping (URML beside Project 11)

- **Mission spec, validated.** A URML program declares an ASV survey / transit mission, validated against the vehicle's declared mobility (a marine `drive_type`) and a safety envelope (operating area, depth band), then handed to Project 11's mission manager.
- **Backseat-driver boundary.** Project 11's backseat-driver architecture is exactly the clean boundary URML likes: URML produces the validated mission; the autopilot / helm executes it. URML adds the typed intent and the capability/envelope gate above the mission manager.

## What is asked

Request for comment from the Project 11 maintainers:

1. Does a URML ASV mission program (mobility + operating-area envelope) fit how Project 11's mission manager is driven?
2. Is a validated-intent front door above the mission manager interesting for survey ASVs?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's marine `drive_type`, the safety-envelope geofence model (RFC-0291), and the decide-then-do split (RFC-0002). Part of Move #48.

## Implementation note

Outreach only. The post is a GitHub Issue on `CCOMJHC/project11` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move48.yaml`.
