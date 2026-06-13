---
rfc: 0548
title: RoboComp integration — request for comment
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

# RFC-0548: RoboComp integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. **Completes** the swarm / multi-robot / alternative-framework wave (Move #49).

## Summary

[`robocomp/robocomp`](https://github.com/robocomp/robocomp) (GPL-3.0, ~128 stars, active, University of Extremadura) is an open robotics component framework for creating and managing robot software components, a non-ROS alternative substrate. URML is substrate-neutral and can dispatch validated intent to whatever runtime a deployment uses; a RoboComp component system is one such substrate. This RFC asks whether the mapping is useful (cross-citation only; RoboComp is GPL-3.0).

## The mapping (URML beside RoboComp)

- **A non-ROS substrate.** URML validates an intent against the robot's declared capabilities and a safety envelope, then dispatches; RoboComp's components execute it. URML is the typed intent + validation layer; RoboComp is the component runtime.
- **Component interfaces toward a manifest.** RoboComp's component interface definitions describe what a component does, which maps toward a URML capability manifest the validator checks against. No code reuse is proposed (RoboComp is GPL-3.0).

## What is asked

Request for comment from the RoboComp maintainers:

1. Is "URML validates intent, then dispatches to RoboComp components" a sensible substrate mapping?
2. Could RoboComp component interfaces inform a URML capability manifest?
3. Which is the cleaner first seam?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's substrate-neutral dispatch model and the decide-then-do split (RFC-0002); the alternative-middleware / framework engagements (RobotRaconteur RFC-0501, OpenRTM-aist RFC-0547). Completes Move #49.

## Implementation note

Outreach only. The post is a GitHub Issue on `robocomp/robocomp` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is GPL-3.0; state it, do not ask). Tracked in `examples/lighthouses/outreach-move49.yaml`.
