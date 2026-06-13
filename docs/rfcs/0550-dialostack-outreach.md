---
rfc: 0550
title: DialoStack integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0550: DialoStack integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the HRI / conversational / robot-data wave (Move #50).

## Summary

[`aquintan4/DialoStack`](https://github.com/aquintan4/DialoStack) (MIT) connects an LLM dialogue layer to ROS 2, turning a conversation into robot actions. URML sits exactly at that handoff: it is a typed intent representation that the dialogue layer can target, validated against the robot's declared capabilities and a safety envelope before dispatch. This RFC asks whether the mapping is useful.

## The relationship (URML beside DialoStack)

- **Validated target for the dialogue layer.** DialoStack turns a conversation into ROS 2 actions. URML is the intermediate, statically-checkable representation between dialogue and execution: the dialogue layer emits URML intent, the validator checks it (argument typing, capability, safety envelope, bindings, policy), then it dispatches. The dialogue stays the creative part; the validator is the gate.
- **Runtime-neutral.** Because URML validates against a capability manifest rather than ROS specifics, the same dialogue front end can drive non-ROS substrates too.

## What is asked

Request for comment from the DialoStack maintainer:

1. Is a typed, validated intent representation a useful target for an LLM dialogue layer that drives ROS 2?
2. Does URML's capability + safety-envelope validation address the "the dialogue produced an action the robot can't safely do" case?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the LLM bridge, the five-pass validator, and the decide-then-do split (RFC-0002). Part of Move #50; sibling framing to ROSGPT (RFC-0549).

## Implementation note

Outreach only. The post is a GitHub Issue on `aquintan4/DialoStack` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move50.yaml`.
