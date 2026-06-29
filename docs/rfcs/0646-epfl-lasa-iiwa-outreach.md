---
rfc: 0646
title: EPFL LASA iiwa_ros (epfl-lasa/iiwa_ros) integration — request for comment
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

# RFC-0646: EPFL LASA iiwa_ros integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #64 (university research-lab lane).

## Summary

[`epfl-lasa/iiwa_ros`](https://github.com/epfl-lasa/iiwa_ros) (EPFL Learning Algorithms and Systems Lab, Aude Billard) is a maintained software stack for controlling the KUKA LBR iiwa arm in simulation and on hardware, with impedance control and a learning-from-demonstration pipeline above it. URML is a small Apache-2.0 language whose one job is to check an intended motion against a robot's declared capability manifest and safety envelope before it executes. A learning-from-demonstration stack is a natural place for that check, because a demonstrated or generalized trajectory is exactly the kind of motion you want to confirm is admissible on the specific arm before you send it to the controller.

## The relationship (URML beside iiwa_ros)

LfD produces a trajectory from human demonstration; that trajectory still has to be admissible on the iiwa it will run on. URML can declare the arm's reach, payload, joint limits, and the active keep-out and speed envelope, and check a generalized trajectory against that declaration before the impedance controller consumes it. The check sits between the learned or generalized motion and the joint commands, and touches neither the demonstration nor the control law.

URML does not do impedance control, does not learn, and does not replace the stack. It is the static admissibility step that says whether a given trajectory is inside the declared envelope for this arm.

## What is asked

1. For a learning-from-demonstration pipeline, is a declared-capability and envelope check on the generalized trajectory a useful step before the controller runs it, or is feasibility already guaranteed upstream in practice?
2. Would a small worked example mapping an iiwa trajectory onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a KUKA iiwa control and learning-from-demonstration stack. GPL-3.0; EPFL LASA (Aude Billard), Switzerland. Part of Move #64.

## Implementation note

Outreach only. The post is a GitHub Issue on `epfl-lasa/iiwa_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move64.yaml`.
