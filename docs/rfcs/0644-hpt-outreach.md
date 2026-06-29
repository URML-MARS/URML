---
rfc: 0644
title: Heterogeneous Pre-trained Transformers (liruiw/HPT) integration — request for comment
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

# RFC-0644: Heterogeneous Pre-trained Transformers integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of Move #63 (VLA / robot-foundation mini-wave).

## Summary

[`liruiw/HPT`](https://github.com/liruiw/HPT) (MIT) pre-trains a shared policy trunk across many embodiments, with embodiment-specific stems and heads mapping each robot's proprioception and action space onto the shared representation. URML is a small Apache-2.0 language built on exactly that premise from the other direction: a per-robot capability manifest that declares one robot's action space, so an intended action can be checked against it before it runs. The two share a worldview, that the robot-specific surface is a thin declared boundary around a substrate-neutral core.

## The relationship (URML beside HPT)

HPT's per-embodiment head is the place where the shared policy becomes a specific robot's actions. URML's per-robot manifest is the declaration of what that specific robot can admissibly do. They meet at the same seam: the head emits an action in one robot's action space, and the manifest says whether that action is inside the robot's declared reach, payload, and envelope. URML validates the head's output against the manifest for that embodiment, before dispatch.

URML does not touch the trunk, the stems, or the training. It is interested only in the boundary HPT already draws per embodiment, and in checking the action that crosses it.

## What is asked

1. Since HPT already factors out a per-embodiment stem and head, could that per-embodiment action space double as a declared capability surface, the way URML's manifest declares one, or are the two describing different things?
2. Would a small worked example mapping an HPT head's action for one embodiment onto a URML manifest (validated, no execution) be useful?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, applied to a cross-embodiment policy with per-embodiment heads. MIT-licensed; MIT (Lirui Wang). Part of Move #63.

## Implementation note

Outreach only. The post is a GitHub Issue on `liruiw/HPT` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move63.yaml`.
