---
rfc: 0635
title: CRAM (cram2/cognitive_robot_abstract_machine) integration — request for comment
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

# RFC-0635: CRAM (cram2/cognitive_robot_abstract_machine) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the VLA / robot-foundation-model + research-lab wave (Move #61, university lane).

## Summary

[`cram2/cognitive_robot_abstract_machine`](https://github.com/cram2/cognitive_robot_abstract_machine) (Institute for Artificial Intelligence, U. Bremen; Prof. Michael Beetz) is CRAM, a cognitive architecture that decomposes underspecified requests ("iron the laundry") into grounded, executed sub-actions, paired with the KnowRob knowledge base. That consume-intent-then-execute loop is the clearest case URML's validate-before-actuate gate sits beside: a robot declares a capability manifest and a safety envelope, and URML validates each concrete sub-action against that declaration before it executes. This is a request for comment.

## The relationship (URML beside CRAM)

- **A check at the action seam.** CRAM's action designators decide what to do; URML checks each resulting concrete action is admissible on the specific robot (within declared force, reach, mobility, object vocabulary, inside the safety envelope) before it actuates. The planner keeps the reasoning; URML is the pre-dispatch check.
- **Complementary to KnowRob.** KnowRob reasons about the world and the task; URML's manifest is a narrow, static, machine-checkable contract about what the specific robot can physically and admissibly do. The open question is whether that is useful or already covered.

## What is asked

1. Is there a natural seam between CRAM's action designators and a declared-capability check, or does KnowRob already cover it?
2. Would a small worked example mapping a CRAM sub-action onto a URML manifest (validated, no execution) be worth having?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, and the validate-before-actuate gate, beside a plan-based cognitive architecture. Part of Move #61 (university lane); Germany, U. Bremen IAI.

## Implementation note

Outreach only. The post is a GitHub Issue on `cram2/cognitive_robot_abstract_machine` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
