---
rfc: 0645
title: RoboPoint (wentaoyuan/RoboPoint) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-28
updated: 2026-06-28
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

# RFC-0645: RoboPoint integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #63 (VLA / robot-foundation mini-wave).

## Summary

[`wentaoyuan/RoboPoint`](https://github.com/wentaoyuan/RoboPoint) (University of Washington) is a vision-language model that predicts spatial affordances: given an instruction and an image, it answers where, as image-space or 3D keypoints a downstream policy then acts on. URML (Apache-2.0) is honest about where it sits relative to this: not at the point prediction, but one step lower, when those points have become a motion the robot is about to make.

## The relationship (URML beside RoboPoint)

This is a deliberately narrow claim. RoboPoint answers "where should the robot act." URML does not weigh in on that; predicting the affordance is the model's job and a good one. URML's surface opens only after the point becomes a planned motion: at that point a robot's declared manifest and safety envelope can check that the motion to the predicted location is in reach, clear of declared keep-out volumes, and within speed and force limits, before the arm moves.

So the relationship is layered, not overlapping. RoboPoint sits above the point-to-action step; URML sits below it, checking the resulting action. The honest version of the pitch is that URML validates the motion, not the affordance.

## What is asked

1. Given that RoboPoint stops at the predicted point and a separate step turns it into motion, is a capability and envelope check on that downstream motion a useful guardrail, or does it belong entirely to whatever consumes the points?
2. Would a small worked example, taking a predicted affordance point through to a URML-validated motion (no execution), help show where the line sits?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied below a spatial-affordance predictor. Apache-2.0; University of Washington (Wentao Yuan). Part of Move #63.

## Implementation note

Outreach only. The post is a GitHub Issue on `wentaoyuan/RoboPoint` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move63.yaml`.
