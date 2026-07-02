---
rfc: 0654
title: Neobotix neo_mpc_planner2 (neobotix/neo_mpc_planner2) integration — request for comment
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

# RFC-0654: Neobotix neo_mpc_planner2 integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #66.

## Summary

[`neobotix/neo_mpc_planner2`](https://github.com/neobotix/neo_mpc_planner2) (Neobotix, Germany) is a model-predictive local planner for omnidirectional mobile bases: it computes and emits velocity commands to drive the platform toward a goal while respecting constraints. URML is a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs. A velocity command headed for the wheels is a clean place for that check, because it is the last artifact before motion.

## The relationship (URML beside neo_mpc_planner2)

The MPC computes a velocity command; URML can declare the platform's envelope (maximum linear and angular velocity, acceleration bounds, footprint and any keep-out region) and confirm the commanded setpoint is inside that declaration before it reaches the base. It is a static admissibility check on the emitted command, not a planner and not a controller. The MPC keeps optimizing the motion; URML only asks whether the command it hands down is within the declared limits for this specific base.

URML does not plan, optimize, or drive the wheels. It declares the platform's envelope and confirms a commanded velocity is inside it before dispatch.

## What is asked

1. For an MPC local planner, is a declared platform-envelope check (velocity, acceleration, footprint) on the emitted velocity command useful before dispatch, or are those limits already fully enforced inside the MPC constraints in practice?
2. Would a small worked example mapping a mobile-base velocity setpoint onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a model-predictive local planner for an omnidirectional mobile base. MIT; Neobotix GmbH, Germany. Part of Move #66.

## Implementation note

Outreach only. The post is a GitHub Issue on `neobotix/neo_mpc_planner2` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move66.yaml`.
