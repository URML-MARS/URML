---
rfc: 0565
title: GEMstack integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0565: GEMstack integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the AV / ADAS / off-road wave (Move #51).

## Summary

[`krishauser/GEMstack`](https://github.com/krishauser/GEMstack) (MIT, University of Illinois) is an educational full-stack autonomous-driving software framework, used to teach the AV pipeline end to end. URML is a good pedagogical companion: it gives students a typed, declarative way to state driving intent and its operating bounds (an ODD), validated against the vehicle's capabilities before the stack plans and acts. This RFC asks whether the mapping is useful for teaching.

## The mapping (URML beside GEMstack)

- **A typed intent + ODD layer for a teaching stack.** GEMstack teaches the full pipeline. URML adds a small, readable layer at the top: declare the driving goal and the operating bounds, validate against the vehicle's declared capabilities and a safety envelope, then let the stack plan and execute (RFC-0020). For students it makes "what are we allowed to do, and why was this rejected" explicit and checkable.
- **Natural-language to validated intent.** URML's Layer 4 lets a teaching scenario start from an English instruction and show exactly how it becomes a typed, validated plan, which is a useful thing to make visible in a course.

## What is asked

Request for comment from the GEMstack maintainer:

1. Is a typed, validated intent + ODD layer a useful teaching companion above the GEMstack pipeline?
2. Does showing the natural-language to validated-intent path add pedagogical value in an AV course?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the Layer-4 natural-language grammar, the safety-envelope validation, and the educational profile (RFC-0011). Completes Move #51; the educational-AV target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `krishauser/GEMstack` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move51.yaml`.
