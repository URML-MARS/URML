---
rfc: 0655
title: VITRA (microsoft/VITRA) integration — request for comment
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

# RFC-0655: VITRA integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #67.

## Summary

[`microsoft/VITRA`](https://github.com/microsoft/VITRA) (Microsoft Research) is a scalable vision-language-action model pretrained on real-life human-activity video, emitting manipulation actions for a robot. URML is a small Apache-2.0 language whose one job is to check an intended action against a robot's declared capability manifest and safety envelope before it runs. A model that learns manipulation from human video is a good fit for that check, because what a human demonstrated is not automatically admissible on the specific robot that will execute it.

## The relationship (URML beside VITRA)

VITRA produces an action; that action still has to be admissible on the target robot. URML can declare the robot's reach, payload, gripper force, and the active keep-out and speed envelope, and validate the emitted action against that declaration before it drives the hardware. The check sits between the model output and the actuators, and touches neither the pretraining nor the policy.

URML does not learn, does not model, and does not replace VITRA. It is the static admissibility step that answers whether a given emitted action is inside the declared envelope for this robot.

## What is asked

1. For a VLA pretrained on human-activity video, is a declared-capability and envelope check on the emitted action a useful step before it drives a specific robot, or is embodiment feasibility already handled inside the model in practice?
2. Would a small worked example mapping a VITRA action onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a human-video-pretrained VLA. MIT; Microsoft Research, US. Part of Move #67.

## Implementation note

Outreach only. The post is a GitHub Issue on `microsoft/VITRA` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move67.yaml`.
