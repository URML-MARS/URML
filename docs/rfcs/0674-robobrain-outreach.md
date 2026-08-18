---
rfc: 0674
title: RoboBrain 2.5 (FlagOpen/RoboBrain2.5) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-18
updated: 2026-08-18
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

# RFC-0674: RoboBrain 2.5 (FlagOpen/RoboBrain2.5) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It continues the VLA / robot-foundation-model wave (Move #61).

## Summary

[`FlagOpen/RoboBrain2.5`](https://github.com/FlagOpen/RoboBrain2.5) is an embodied foundation model whose upgrade is precise 3D spatial reasoning: it predicts complete 3D manipulation traces as ordered keypoint sequences under physical constraints, alongside affordance prediction and trajectory forecasting. Because the output is a concrete geometric trace rather than text, URML's validate-before-actuate gate has a surface: the robot declares a reachable workspace, payload, and a safety envelope, and URML checks the predicted keypoint trace is admissible on that specific robot before execution. This is a request for comment.

## The relationship (URML beside RoboBrain 2.5)

- **The model predicts the trace, the validator gates it.** RoboBrain 2.5 predicts the 3D manipulation trace; URML checks each keypoint (and the trace as a whole) lies within the declared reachable workspace and the active safety envelope before the arm moves. URML does not constrain the model; it makes the predicted trace checkable against a specific robot.
- **Aligned with reasoning under physical constraints.** The model already reasons about metric, depth-aware constraints; a declared capability + envelope is the same idea made explicit and per-robot, so the same predicted trace can be checked against whatever arm actually executes it.
- **A neutral layer.** URML is substrate- and model-neutral (the LLM bridge is provider-agnostic). It composes above the trace output rather than depending on the model's internals.

## What is asked

1. Would checking a predicted keypoint trace against a declared reachable workspace + safety envelope be a useful guard, given RoboBrain already predicts under physical constraints?
2. Would a small worked example mapping a RoboBrain trace onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #61 VLA / robot-foundation-model wave (open-weight tranche).

## Implementation note

Outreach only. The post is a GitHub Issue on `FlagOpen/RoboBrain2.5` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
