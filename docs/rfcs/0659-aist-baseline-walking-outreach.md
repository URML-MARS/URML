---
rfc: 0659
title: AIST BaselineWalkingController (isri-aist/BaselineWalkingController) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-03
updated: 2026-07-03
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

# RFC-0659: AIST BaselineWalkingController integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #68 (Japan lane).

## Summary

[`isri-aist/BaselineWalkingController`](https://github.com/isri-aist/BaselineWalkingController) (AIST, Intelligent Systems Research Institute) is a bipedal walking controller that computes and commands whole-body motion for a humanoid, one of a family of humanoid-control components from the group (centroidal control, multi-contact, NMPC, force control). URML is a small Apache-2.0 language whose one job is to check an intended motion against a robot's declared capability manifest and safety envelope before it runs. A walking controller commands the whole body, which is exactly what URML's most recent addition was written for.

## The relationship (URML beside BaselineWalkingController)

URML has a whole-body manifest block (RFC-0384: kinematic structure plus stability limits, center of mass and support polygon). A walking controller drives the whole body toward a gait; URML can declare the humanoid's support polygon and center-of-mass bounds and check that a commanded whole-body motion stays inside that declared envelope before it executes. It is a static admissibility check beside the controller, not a stabilizer inside it.

URML does not walk, balance, or optimize a gait. It declares what admissible means for the humanoid and checks the commanded motion against it. The controller keeps the continuous stabilization; URML is the pre-dispatch envelope check.

## What is asked

1. Does a declared whole-body envelope (support polygon, center-of-mass bounds, per RFC-0384) line up with how a walking controller already reasons about a feasible step, or is the real envelope only meaningful at runtime inside the stabilizer?
2. Would a small worked example mapping a commanded whole-body motion onto a URML RFC-0384 manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the RFC-0384 whole-body / stability block, and the validate-before-actuate gate, applied to a humanoid walking controller. BSD-2-Clause; AIST (Intelligent Systems Research Institute), Japan. Part of Move #68.

## Implementation note

Outreach only. The post is a GitHub Issue on `isri-aist/BaselineWalkingController` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move68.yaml`.
