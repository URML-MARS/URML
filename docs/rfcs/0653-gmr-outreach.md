---
rfc: 0653
title: GMR General Motion Retargeting (YanjieZe/GMR) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-07-02
updated: 2026-07-02
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

# RFC-0653: GMR General Motion Retargeting integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #66.

## Summary

[`YanjieZe/GMR`](https://github.com/YanjieZe/GMR) (Stanford) retargets human motion onto a humanoid in real time, producing robot-specific joint commands the target robot can execute. URML is a small Apache-2.0 language whose one job is to check an intended motion against a robot's declared capability manifest and safety envelope before it runs. Retargeting is a natural fit for that check, because a motion that is valid on the source can land outside the target robot's limits, and the retargeted trajectory is exactly the artifact you want confirmed admissible before it drives the hardware.

## The relationship (URML beside GMR)

GMR maps a source motion onto the target embodiment; the result still has to be admissible on that specific humanoid. URML recently added a whole-body manifest block (RFC-0384: kinematic structure plus stability limits, center of mass and support polygon). It can check that a retargeted whole-body trajectory stays inside the target's declared joint limits and stability envelope before the robot executes it. The check sits between the retargeting output and the controller, and touches neither the retargeting method nor the control loop.

URML does not retarget, does not run a balance loop, and does not replace GMR. It declares what admissible means for the target humanoid and confirms the retargeted motion is inside it.

## What is asked

1. For real-time retargeting, is a declared whole-body envelope check (joint limits, center-of-mass and support-polygon bounds, per RFC-0384) on the retargeted trajectory useful before it runs on the target robot, or is feasibility already enforced inside the retargeting?
2. Would a small worked example mapping a retargeted humanoid motion onto a URML RFC-0384 manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the RFC-0384 whole-body / stability block, and the validate-before-actuate gate, applied to a real-time motion-retargeting framework. MIT; Stanford (Yanjie Ze), US. Part of Move #66.

## Implementation note

Outreach only. The post is a GitHub Issue on `YanjieZe/GMR` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move66.yaml`.
