---
rfc: 0493
title: linorobot2 integration — request for comment
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

# RFC-0493: linorobot2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the open robot-platforms wave (Move #44).

## Summary

[`linorobot/linorobot2`](https://github.com/linorobot/linorobot2) (Apache-2.0, ~910 stars, active) is an open ROS 2 stack for building 2WD / 4WD / Mecanum autonomous mobile robots. URML is interesting to a build-your-own mobile base as the natural-language front door above the ROS 2 navigation stack: "go to the kitchen" becomes a typed `move_to`, validated against the base's declared mobility and the map's declared locations before it is dispatched to the existing Nav2-based pipeline. This RFC asks whether the mapping is useful.

## The mapping (URML beside linorobot2)

- **Capability manifest.** The base's drive type (differential / mecanum), velocity limits, and the deployment's named locations and frames map onto a URML Layer-1 manifest. A program's `move_to(location)` is validated against that manifest: the location resolves, the drive type supports the motion, the envelope permits it.
- **NL front door, then dispatch.** URML turns a natural-language request into the typed primitive and validates it, then hands the goal to linorobot2's ROS 2 navigation. URML adds the capability/envelope gate and the typed intent record; it does not replace the navigation stack.

## What is asked

Request for comment from the linorobot2 maintainers:

1. Does mapping a linorobot2 base (drive type, velocity limits, named locations) onto a URML manifest read right?
2. Is an English-to-validated-`move_to` front door above the ROS 2 nav stack interesting for the build-your-own audience?
3. Which is the cleaner first seam — the manifest mapping, or the validated-dispatch adapter against the existing Nav2 goals?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's `mobility` block, named-location/frame resolution, and the decide-then-do split (RFC-0002). The headline path "one English sentence makes a robot move" is exactly what a mobile base demonstrates. Part of Move #44, the open robot-platforms wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `linorobot/linorobot2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask. Tracked in `examples/lighthouses/outreach-move44.yaml`.
