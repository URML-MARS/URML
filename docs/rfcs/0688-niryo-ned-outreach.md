---
rfc: 0688
title: Niryo Ned ROS stack (NiryoRobotics/ned_ros) integration — request for comment
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

# RFC-0688: Niryo Ned ROS stack (NiryoRobotics/ned_ros) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the small-open-robot wave (Move #72).

## Summary

[`NiryoRobotics/ned_ros`](https://github.com/NiryoRobotics/ned_ros) is the ROS stack for the Niryo Ned / Ned2, a popular educational 6-axis desktop arm, with a `pyniryo` Python client for programming it. Because a joint, pose, or gripper command becomes a real actuation on the arm, URML's validate-before-actuate gate has a surface: the arm declares a capability manifest (joint limits, reachable workspace, gripper force) and a safety envelope, and URML checks a motion or grasp is admissible before `pyniryo` or the ROS stack drives the arm. This is a request for comment.

## The relationship (URML beside the Ned stack)

- **The program proposes, the validator gates.** Whatever produces the command (a `pyniryo` script, a block program, an LLM) decides the action; URML checks the concrete joint/pose/grasp is admissible on the declared Ned (within its limits, inside the safety envelope) before the stack actuates. URML does the check; Ned keeps the motion.
- **Legible for education.** On a teaching arm, refusing an out-of-reach pose or an over-force grasp on paper, with the reason, is a clear and safe demonstration of intent-before-actuation.
- **Neutral by construction.** URML is substrate- and model-neutral. It composes above `pyniryo` / the ROS interface rather than depending on internals, and cross-cites only (the stack is GPL-3.0; no code is reused and no license question is raised).

## What is asked

1. Would a declared capability manifest + safety envelope, checked before a `pyniryo` / ROS command drives the Ned, be a useful guard, especially for classroom use?
2. Would a small worked example mapping a Ned motion or grasp onto a URML manifest (validated, no execution) be worth having, in your examples or ours?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate. Part of the Move #72 small-open-robot wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `NiryoRobotics/ned_ros` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move72.yaml`.
