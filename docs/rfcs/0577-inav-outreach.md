---
rfc: 0577
title: INAV integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0577: INAV integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the motor-control / RTOS substrate wave (Move #53). INAV is the navigation-focused sibling of the flight-controller cluster, which makes the mission framing more direct than for a stabilization-first firmware.

## Summary

[`iNavFlight/inav`](https://github.com/iNavFlight/inav) (GPL-3.0) is flight-controller firmware focused on autonomous navigation: waypoint missions, return-to-home, GPS-driven flight. That is exactly the level a declared mission intent speaks to. URML expresses a mission as a goal plus constraints, validates it against the craft's declared capabilities and a safety envelope, then dispatches to INAV. This is a consume / dispatch note (cross-citation only, since INAV is GPL-3.0).

## The mapping (URML beside INAV)

- **A mission is a declared, checkable intent.** "Fly this waypoint route, hold these altitude and geofence bounds, return home on this condition" is a goal-plus-constraints intent. URML declares it, validates it against the craft's capabilities and an envelope, then hands it to INAV to execute. INAV keeps full ownership of navigation and control.
- **Geofence and limits as an envelope.** The operating bounds INAV already enforces (geofence, altitude, failsafe conditions) map onto a URML safety envelope, so an inadmissible mission is rejected before upload.

## What is asked

1. Does a declared, validated mission intent (waypoints + bounds, checked against the craft) fit how INAV missions are defined and uploaded?
2. Do INAV's existing geofence and failsafe bounds map onto a URML safety envelope cleanly enough to be worth a shared representation?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's drone profile, the plan_path / follow_trajectory consume model (RFC-0020), the safety-envelope validation, and the capability manifest. Part of Move #53; the navigation half of the flight-controller cluster (with Betaflight RFC-0576).

## Implementation note

Outreach only. The post is a GitHub Issue on `iNavFlight/inav` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is GPL-3.0; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move53.yaml`.
