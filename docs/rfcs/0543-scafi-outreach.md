---
rfc: 0543
title: ScaFi integration — request for comment
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

# RFC-0543: ScaFi integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the swarm / multi-robot / alternative-framework wave (Move #49).

## Summary

[`scafi/scafi`](https://github.com/scafi/scafi) (Apache-2.0, ~36 stars, active, University of Bologna) is a Scala framework for Aggregate Computing: programming a collective of devices as a single field-based program. URML is a language peer at the individual-robot layer: it declares typed, validated intent per robot and addresses many through a fleet roster. This RFC is a language-to-language request for comment.

## The relationship (URML beside ScaFi)

- **Aggregate behavior + per-robot validated intent.** ScaFi expresses collective behavior over a field of devices; URML declares each device's intent validated against its capability manifest and safety envelope (RFC-0286 fleet roster, RFC-0291 deconfliction). A composition: the aggregate program decides the collective, and the per-device actions are URML primitives checked before dispatch.
- **Two declarative styles.** Aggregate computing is declarative over a field; URML is declarative over a single robot's capabilities. Naming the boundary helps a deployment use both.

## What is asked

Request for comment from the ScaFi maintainers:

1. Is "ScaFi expresses the aggregate behavior; URML validates the per-device intent" a sensible layering?
2. Does URML's fleet roster + deconfliction complement aggregate computing's field model?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's multi-robot fleet addressing (RFC-0286), cross-robot deconfliction (RFC-0291), and the decide-then-do split (RFC-0002). Part of Move #49; ScaFi is an aggregate-computing language peer.

## Implementation note

Outreach only. The post is a GitHub Issue on `scafi/scafi` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move49.yaml`.
