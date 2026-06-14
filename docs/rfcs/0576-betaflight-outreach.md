---
rfc: 0576
title: Betaflight integration — request for comment
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

# RFC-0576: Betaflight integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the motor-control / RTOS substrate wave (Move #53), leading with flight-controller firmware because the altitude is cleanest there.

## Summary

[`betaflight/betaflight`](https://github.com/betaflight/betaflight) (GPL-3.0) is flight-controller firmware running on a very large fleet of multirotors. URML is a small, Apache-2.0 language for robot intent: an intent is validated against the craft's declared capabilities and a safety envelope, then dispatched to whatever flies it. Betaflight is the substrate that flies it. This RFC is a consume / dispatch note (cross-citation only, since Betaflight is GPL-3.0).

## The mapping (URML beside Betaflight)

- **URML declares and validates; Betaflight flies.** A flight intent plus its operating bounds (geometry, speed, the conditions under which a maneuver is allowed) is what URML expresses and checks against the craft's declared capabilities before anything is sent. Betaflight keeps full ownership of stabilization and control. URML does not fly; it gates and dispatches.
- **The craft's limits map onto a manifest.** A multirotor's actuatable envelope maps onto a URML Layer-1 capability manifest, so an intent the craft cannot safely do is rejected before it reaches the firmware.

## What is asked

1. Is a typed, validated intent layer (declare flight intent + bounds, validate against the craft, then dispatch) useful above Betaflight, or does the relevant safety reasoning already live in the firmware and the configurator?
2. Does a craft's operating envelope map cleanly onto the way Betaflight already describes a craft's limits?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's drone profile, the capability manifest, the safety-envelope validation, and the decide-then-do split (RFC-0002). Anchor of Move #53; the flight-controller cluster (with INAV RFC-0577).

## Implementation note

Outreach only. The post is a GitHub Issue on `betaflight/betaflight` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is GPL-3.0; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move53.yaml`.
