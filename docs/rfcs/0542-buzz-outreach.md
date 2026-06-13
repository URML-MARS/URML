---
rfc: 0542
title: Buzz integration — request for comment
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

# RFC-0542: Buzz integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. It is the anchor of the swarm / multi-robot / alternative-framework wave (Move #49). Several targets in this wave are *language peers*, and Buzz is the clearest.

## Summary

[`buzz-lang/Buzz`](https://github.com/buzz-lang/Buzz) (MIT, ~317 stars, active, NESTLab @ WPI + Polytechnique Montreal) is a programming language designed for robot swarms: it lets a developer express collective behavior that compiles down to per-robot execution. URML is also a language for robots, at a different layer: it declares *typed, validated intent* for an individual robot (checked against a capability manifest and a safety envelope) and addresses multiple robots through a fleet roster. This RFC is a language-to-language request for comment, not a request to adopt anything.

## The relationship (URML beside Buzz)

- **Two layers, complementary.** Buzz expresses swarm-level collective behavior; URML declares each robot's validated intent and the fleet's roster + cross-robot constraints (RFC-0286 / RFC-0291). One natural composition: a Buzz program coordinates the swarm, while the per-robot actions it issues are URML primitives validated against each robot's manifest before dispatch. URML adds the typed, statically-checkable per-robot gate; Buzz stays the swarm language.
- **No manifest ask.** This is a conversation between two robot languages about where each sits, not a proposal for Buzz to depend on URML.

## What is asked

Request for comment from the Buzz maintainers:

1. Is "Buzz coordinates the swarm; URML validates the per-robot intent it issues" a sensible layering?
2. Does URML's fleet roster + cross-robot deconfliction overlap or complement Buzz's swarm primitives?
3. Which boundary, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's multi-robot fleet addressing (RFC-0286) and cross-robot deconfliction (RFC-0291), and the decide-then-do split (RFC-0002). Anchor of Move #49; Buzz is the closest swarm-language peer found in the 2026-06-13 candidate search.

## Implementation note

Outreach only. The post is a GitHub Issue on `buzz-lang/Buzz` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move49.yaml`.
