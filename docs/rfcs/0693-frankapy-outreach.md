---
rfc: 0693
title: frankapy (iamlab-cmu/frankapy) integration — request for comment
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

# RFC-0693: frankapy (iamlab-cmu/frankapy) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the manipulation/control wave (Move #73).

## Summary

[`iamlab-cmu/frankapy`](https://github.com/iamlab-cmu/frankapy) (Carnegie Mellon Intelligent Autonomous Manipulation Lab) is a Python skill API for the Franka arm (`goto_pose`, `goto_joints`, `execute_trajectory`) over a franka-interface action server. A skill call is already a typed intent, which is exactly where URML's validate-before-actuate gate has a surface: the arm declares a capability manifest (joint limits, reachable workspace, force bounds) and a safety envelope, and URML checks a skill call is admissible before the action server executes it. This is a request for comment.

## The relationship (URML beside frankapy)

- **The skill call is the intent; the validator gates it.** `goto_pose` / `goto_joints` / `execute_trajectory` state what should happen; URML checks the concrete target is admissible on the declared Franka (within its limits and workspace, inside the safety envelope) before the action server runs it. URML does the check; frankapy keeps the execution.
- **A typed skill API is a natural fit.** Because the API is already a small set of named skills with typed parameters, a per-arm capability manifest is the declaration each call is checked against.
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above the skill API rather than depending on its internals, and cross-cites (no vendoring).

## What is asked

1. Would a declared capability manifest + safety envelope, checked before a frankapy skill call reaches the action server, be a useful guard?
2. Would a small worked example mapping a frankapy skill call onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #73 manipulation/control wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `iamlab-cmu/frankapy` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move73.yaml`.
