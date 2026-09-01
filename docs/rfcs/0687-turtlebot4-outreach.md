---
rfc: 0687
title: TurtleBot 4 (turtlebot/turtlebot4) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-01
updated: 2026-09-01
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

# RFC-0687: TurtleBot 4 (turtlebot/turtlebot4) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the small-open-robot wave (Move #72).

## Summary

[`turtlebot/turtlebot4`](https://github.com/turtlebot/turtlebot4) (Clearpath Robotics / Open Robotics) is the ROS 2 software for TurtleBot 4, the widely used affordable educational mobile robot built on an iRobot Create 3 base. Because a navigation or docking intent becomes a Nav2 / velocity goal that drives a real base, URML's validate-before-actuate gate has a surface: the robot declares a capability manifest (mobility bounds) and a safety envelope (a geofence, a speed cap, keep-out zones), and URML checks a navigation intent is admissible before the base moves. This is a request for comment.

## The relationship (URML beside TurtleBot 4)

- **The navigator proposes, the validator gates.** Nav2 (or whatever produces the goal) decides the path; URML checks the intent is admissible against the declared mobility bounds and safety envelope (inside the geofence, under the speed cap) before dispatch. URML does the check; the ROS 2 stack keeps the driving.
- **An educational robot is a good place to make the check legible.** A student can see a too-fast or out-of-bounds command refused on paper, with the reason, before the base ever moves.
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above the Nav2 / velocity interface rather than depending on its internals.

## What is asked

1. Would a declared mobility + safety-envelope manifest, checked before a navigation or dock goal is dispatched, be a useful guard on top of the TurtleBot 4 stack, especially in classroom settings?
2. Would a small worked example mapping a TurtleBot 4 navigation intent onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope (geofence / speed caps), and the static validate-before-actuate gate. Part of the Move #72 small-open-robot wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `turtlebot/turtlebot4` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move72.yaml`.
