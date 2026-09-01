---
rfc: 0690
title: PyBEAR (Westwood-Robotics/PyBEAR) integration — request for comment
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

# RFC-0690: PyBEAR (Westwood-Robotics/PyBEAR) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the small-open-robot wave (Move #72).

## Summary

[`Westwood-Robotics/PyBEAR`](https://github.com/Westwood-Robotics/PyBEAR) is the Python driver for the BEAR actuators used as the joints of the BRUCE kid-size open humanoid. Because the driver writes a concrete torque, position, or velocity command to a real actuator, URML's validate-before-actuate gate has a surface at the finest granularity: the robot declares each actuator's limits (torque, velocity, position) as a capability manifest and a safety envelope, and URML checks a command is admissible before the driver writes it to the bus. This is a request for comment.

## The relationship (URML beside PyBEAR)

- **The controller proposes, the validator gates.** Whatever produces the command (a whole-body controller, a learned policy) decides the actuator target; URML checks the concrete torque/position/velocity is within the declared actuator limits, inside the safety envelope, before PyBEAR writes to the bus. URML does the check; PyBEAR keeps the actuation.
- **Actuator-level is the honest place for a static envelope.** A declared per-actuator limit is exactly what a command can be checked against before dispatch, off-hardware, in contexts where a runtime monitor cannot yet run (an LLM or a policy in the loop before anything is connected).
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above the driver rather than depending on its internals, and cross-cites (no vendoring).

## What is asked

1. Would a declared per-actuator limit + safety envelope, checked before PyBEAR writes a command to the bus, be a useful guard on top of the driver?
2. Would a small worked example mapping a BEAR actuator command onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, actuation range checks (RFC-0017), and the static validate-before-actuate gate. Part of the Move #72 small-open-robot wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `Westwood-Robotics/PyBEAR` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move72.yaml`.
