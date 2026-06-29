---
rfc: 0643
title: human2humanoid (LeCAR-Lab/human2humanoid) integration — request for comment
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

# RFC-0643: human2humanoid integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #63 (VLA / robot-foundation mini-wave).

## Summary

[`LeCAR-Lab/human2humanoid`](https://github.com/LeCAR-Lab/human2humanoid) (CMU's LeCAR lab) learns whole-body humanoid control from human motion, producing real-time policies that drive a full humanoid body. URML is a small language for declaring robot capability and checking intent against it before execution. URML recently added a whole-body / legged manifest block (RFC-0384: kinematic structure plus stability limits, center of mass and support polygon), and a learned whole-body controller is the most direct consumer that block was written for.

## The relationship (URML beside human2humanoid)

A whole-body policy commands the whole body, which is exactly where a declared stability envelope matters. RFC-0384 lets a humanoid declare its support-polygon and center-of-mass limits; URML can then check that a commanded whole-body motion stays inside that declared envelope before it executes, as a static admissibility check that sits beside, not inside, the controller.

URML does not do balance, does not run a control loop, and does not replace the policy. It declares what "admissible" means for this specific humanoid and checks the commanded motion against it. The continuous balancing stays entirely in the learned controller.

## What is asked

1. Does a declared whole-body envelope (support polygon, center-of-mass bounds, per-RFC-0384) line up with how a learned humanoid controller already reasons about feasibility, or is the real envelope only knowable at runtime?
2. Would a small worked example mapping a humanoid whole-body command onto a URML RFC-0384 manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the RFC-0384 whole-body / stability block, and the validate-before-actuate gate, applied to a learned humanoid whole-body controller. CMU LeCAR lab. Part of Move #63.

## Implementation note

Outreach only. The post is a GitHub Issue on `LeCAR-Lab/human2humanoid` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move63.yaml`.
