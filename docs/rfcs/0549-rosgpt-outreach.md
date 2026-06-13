---
rfc: 0549
title: ROSGPT integration — request for comment
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

# RFC-0549: ROSGPT integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It anchors the HRI / conversational / robot-data wave (Move #50). ROSGPT is the clearest conceptual peer in the wave: it also turns natural language into robot action.

## Summary

[`aniskoubaa/rosgpt`](https://github.com/aniskoubaa/rosgpt) (Prince Sultan University) is a widely-cited project that maps unstructured natural language onto structured ROS commands via an LLM, with a published methodology. URML solves the same end-to-end problem from a different angle: a natural-language instruction becomes a *typed* primitive that is validated against the robot's declared capabilities and an active safety envelope before anything is dispatched. This RFC is a language-to-language note about where the two meet.

## The relationship (URML beside ROSGPT)

- **The same seam, with a validation gate.** ROSGPT turns language into ROS commands. URML turns language into a typed primitive, then runs five validation passes (argument typing, capability check against a manifest, safety-envelope check, variable bindings, compliance policy) before dispatch. One natural composition: an LLM proposes intent (ROSGPT-style), URML is the intermediate representation that is statically checked before it reaches ROS. The LLM stays free to be creative; the validator refuses anything the robot cannot safely do.
- **A representation worth targeting.** Where ROSGPT emits commands directly, URML is a small, human-readable, runtime-neutral intent language an LLM can emit and a validator can check. It is not ROS-specific, so the same validated intent can target PX4, a vendor SDK, or a non-ROS substrate.

## What is asked

Request for comment from the ROSGPT author:

1. Is a typed, statically-validated intermediate representation (validated against a capability manifest + safety envelope) a useful layer between an LLM and ROS?
2. Does URML's five-pass validation address the "the LLM emitted an unsafe or unsupported command" failure mode that an LLM-to-ROS bridge has to handle somewhere?
3. Which boundary, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the LLM bridge (`reference/llm-bridge`), the five-pass validator, and the decide-then-do split (RFC-0002). Anchor of Move #50; ROSGPT is the most-recognized natural-language-to-ROS peer found in the 2026-06-13 candidate search.

## Implementation note

Outreach only. The post is a GitHub Issue on `aniskoubaa/rosgpt` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Pure conceptual-peer framing, no manifest ask and no licensing discussion. Tracked in `examples/lighthouses/outreach-move50.yaml`.
