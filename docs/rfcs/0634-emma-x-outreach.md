---
rfc: 0634
title: Emma-X (declare-lab/Emma-X) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-25
updated: 2026-06-25
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

# RFC-0634: Emma-X (declare-lab/Emma-X) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the VLA / robot-foundation-model wave (Move #61).

## Summary

[`declare-lab/Emma-X`](https://github.com/declare-lab/Emma-X) (DeCLaRe Lab, SUTD, Singapore) is an embodied multimodal action model with grounded chain-of-thought and look-ahead spatial reasoning. Its output is a grounded action *sequence*, and that sequence is exactly what URML can validate: a robot declares a capability manifest (grippers, reach, payload, object vocabulary) and a safety envelope, and URML checks each action in the sequence against that declaration before execution. This is a request for comment.

## The relationship (URML beside Emma-X)

- **Validate the whole sequence before the first motion.** Because Emma-X reasons with explicit look-ahead, it proposes a sequence rather than a single step. URML can check that whole sequence against the manifest before anything actuates, flagging a step that is out of capability or outside the declared object vocabulary.
- **Reasoning proposes, the validator confirms.** The grounded reasoning decides; a static checker confirms each step is admissible on the specific robot before it runs.

## What is asked

1. Is a declared capability + safety envelope a useful guardrail for the kind of manipulation Emma-X targets?
2. Would a small worked example mapping an Emma-X action sequence onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the static validate-before-actuate gate, applied to a multi-step action sequence. Part of Move #61; Singapore (allied) academic target.

## Implementation note

Outreach only. The post is a GitHub Issue on `declare-lab/Emma-X` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
