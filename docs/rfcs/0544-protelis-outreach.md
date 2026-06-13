---
rfc: 0544
title: Protelis integration — request for comment
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

# RFC-0544: Protelis integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the swarm / multi-robot / alternative-framework wave (Move #49).

## Summary

[`Protelis/Protelis`](https://github.com/Protelis/Protelis) (GPL-3.0-or-later, ~22 stars, active, University of Bologna / Raytheon BBN lineage) is a Java-hosted field-calculus language for aggregate programming of distributed systems. As with the other aggregate-computing peers in this wave, URML sits at the individual-robot layer: typed, validated intent per robot, with a fleet roster across many. This RFC is a language-to-language request for comment, with no code reuse implied (Protelis is GPL-3.0; the relationship is cross-citation only).

## The relationship (URML beside Protelis)

- **Field calculus + per-robot validated intent.** Protelis expresses computation over a field of devices; URML declares each device's intent validated against its capability manifest and safety envelope (RFC-0286 / RFC-0291). A composition: the field program decides the collective, the per-device actions are URML primitives checked before dispatch.
- **Cross-citation only.** Given Protelis's GPL-3.0 license, this proposes no shared code, only a conceptual boundary between two declarative robot/distributed-systems languages.

## What is asked

Request for comment from the Protelis maintainers:

1. Is "Protelis expresses the field computation; URML validates the per-device intent" a sensible layering?
2. Does URML's fleet roster + deconfliction complement field calculus's aggregate model?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's multi-robot fleet addressing (RFC-0286), cross-robot deconfliction (RFC-0291), and the decide-then-do split (RFC-0002). Part of Move #49; Protelis is a field-calculus aggregate-programming peer (sibling to ScaFi, RFC-0543).

## Implementation note

Outreach only. The post is a GitHub Issue on `Protelis/Protelis` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is GPL-3.0; state it, do not ask). Tracked in `examples/lighthouses/outreach-move49.yaml`.
