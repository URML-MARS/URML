---
rfc: 0695
title: Sesame Robot (dorianborian/sesame-robot) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-09-03
updated: 2026-09-03
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

# RFC-0695: Sesame Robot (dorianborian/sesame-robot) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the Move #73 wave.

## Summary

[`dorianborian/sesame-robot`](https://github.com/dorianborian/sesame-robot) is an open and affordable mini quadruped robot based on the ESP32. A quadruped commands leg-joint positions to walk, sit, and pose, and that is where URML's validate-before-actuate gate has a surface: the robot declares a capability manifest (per-leg joint limits, gait bounds) and a safety envelope, and URML checks a gait or pose command is admissible before it drives the servos. This is a request for comment.

## The relationship (URML beside Sesame)

- **The gait proposes, the validator gates.** Whatever produces the motion (a gait generator, a pose command, an LLM) decides the leg targets; URML checks the concrete command is admissible on the declared quadruped (within its per-leg joint limits, inside the safety envelope) before the servos move. URML does the check; Sesame keeps the actuation.
- **A small open robot is a good place to make the check legible.** On an affordable ESP32 quadruped, refusing an out-of-range joint command on paper, with the reason, is a clear demonstration of intent-before-actuation, and it is the same shape as URML's existing small-quadruped work (Petoi Bittle / Nybble).
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above the command interface rather than depending on internals, and cross-cites (no vendoring).

## What is asked

1. Would a declared per-leg capability manifest + safety envelope, checked before a gait or pose command drives the servos, be a useful guard on Sesame?
2. Would a small worked example mapping a Sesame gait or pose onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #73 wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `dorianborian/sesame-robot` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move73.yaml`.
