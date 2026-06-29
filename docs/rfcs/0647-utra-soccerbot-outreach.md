---
rfc: 0647
title: UTRA soccerbot (utra-robosoccer/soccerbot) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-29
updated: 2026-06-29
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

# RFC-0647: UTRA soccerbot integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #64 (university research-lab lane).

## Summary

[`utra-robosoccer/soccerbot`](https://github.com/utra-robosoccer/soccerbot) (University of Toronto Robotics Association, RoboCup Humanoid League) is a full, actively maintained software stack for an autonomous humanoid soccer robot: perception, localization, planning, and whole-body locomotion on a real bipedal platform. URML is a small Apache-2.0 language for declaring what a robot can do and checking an intended motion against that declaration before it runs. A bipedal soccer robot is a good fit for the part of URML written most recently: a whole-body manifest block (RFC-0384) declaring kinematic structure and stability limits, center of mass and support polygon.

## The relationship (URML beside soccerbot)

A humanoid that kicks, walks, and recovers balance is commanding its whole body, which is where a declared stability envelope earns its place. URML can declare the support polygon and center-of-mass bounds for the platform, and check that a commanded whole-body motion (a kick, a step) stays inside that declared envelope before the locomotion controller executes it. It is a static admissibility check beside the controller, not a balance loop inside it.

URML does not walk, kick, or balance, and it does not replace any part of the stack. It declares what admissible means for this humanoid and checks the commanded motion against it.

## What is asked

1. Does a declared whole-body envelope (support polygon, center-of-mass bounds, per RFC-0384) line up with how a humanoid soccer stack already reasons about a stable kick or step, or is the real envelope only knowable at runtime?
2. Would a small worked example mapping a soccerbot whole-body motion onto a URML RFC-0384 manifest (validated, no execution) be useful, especially as a teaching artifact for new team members?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the RFC-0384 whole-body / stability block, and the validate-before-actuate gate, applied to a RoboCup humanoid soccer stack. BSD-3-Clause; University of Toronto Robotics Association (a student competition team, not a PI research lab), Canada. Part of Move #64.

## Implementation note

Outreach only. The post is a GitHub Issue on `utra-robosoccer/soccerbot` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move64.yaml`.
