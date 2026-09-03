---
rfc: 0692
title: panda-py (JeanElsner/panda-py) integration — request for comment
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

# RFC-0692: panda-py (JeanElsner/panda-py) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Anchors a manipulation/control wave (Move #73).

## Summary

[`JeanElsner/panda-py`](https://github.com/JeanElsner/panda-py) (Technical University of Munich) is a Python library over libfranka that exposes real-time controllers (joint-position, Cartesian-pose, torque) which dispatch straight to a Franka arm. Because each commanded setpoint becomes a real actuation, URML's validate-before-actuate gate has a surface: the arm declares a capability manifest (joint limits, reachable workspace, torque/force bounds) and a safety envelope, and URML checks a setpoint is admissible before the real-time controller drives the arm. This is a request for comment.

## The relationship (URML beside panda-py)

- **The program proposes, the validator gates.** Whatever produces the setpoint (a script, a policy, an LLM) decides the target; URML checks the concrete joint/Cartesian/torque command is admissible on the declared Franka (within its limits, inside the safety envelope) before the controller dispatches. URML does the check; panda-py keeps the real-time control.
- **The library is a clean seam.** Because `panda_py.controllers` is the single programmatic surface, a per-arm capability manifest is the natural declaration a setpoint is checked against before it goes real-time.
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above the controller interface rather than depending on its internals, and cross-cites (no vendoring).

## What is asked

1. Would a declared capability manifest + safety envelope, checked before a setpoint reaches the real-time controller, be a useful guard on top of panda-py?
2. Would a small worked example mapping a panda-py setpoint onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Anchor of the Move #73 manipulation/control wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `JeanElsner/panda-py` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move73.yaml`.
