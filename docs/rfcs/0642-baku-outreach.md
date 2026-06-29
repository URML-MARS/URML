---
rfc: 0642
title: BAKU (siddhanthaldar/BAKU) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-28
updated: 2026-06-28
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

# RFC-0642: BAKU integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #63 (VLA / robot-foundation mini-wave).

## Summary

[`siddhanthaldar/BAKU`](https://github.com/siddhanthaldar/BAKU) (NYU, Lerrel Pinto's group) is a transformer architecture for multi-task policy learning: one policy, many tasks, emitting action chunks. URML (Apache-2.0) sits one step downstream of an action chunk, validating it against the robot's declared capability manifest and safety envelope before it reaches the motors. A multi-task policy is a good stress test for that idea, because the same policy produces actions for tasks with very different admissible envelopes.

## The relationship (URML beside BAKU)

A single multi-task policy is exactly where a per-robot, per-context check earns its place. The action chunk a policy emits for "wipe the counter" and the chunk it emits for "lift the box" land on the same hardware with different force and reach implications. URML validates the emitted chunk against the manifest (reach, payload, gripper force) and the active envelope (keep-out volumes, speed ceiling) before dispatch, regardless of which task produced it.

URML does not touch the policy, the training, or the action representation. It reads the chunk the policy already emits and answers one question: is this admissible on this robot right now.

## What is asked

1. For a multi-task policy, is a single declared-capability check at the action-chunk boundary a sensible safety complement, or does task-conditioning already cover that ground in practice?
2. Would a small worked example mapping a BAKU action chunk onto a URML manifest (validated, no execution) be useful?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a multi-task action-chunking policy. MIT-licensed; NYU. Part of Move #63.

## Implementation note

Outreach only. The post is a GitHub Issue on `siddhanthaldar/BAKU` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move63.yaml`.
