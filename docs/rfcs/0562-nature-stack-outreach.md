---
rfc: 0562
title: NATURE stack (off-road autonomy) integration — request for comment
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

# RFC-0562: NATURE stack (off-road autonomy) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the AV / ADAS / off-road wave (Move #51).

## Summary

[`CGoodin/nature-stack`](https://github.com/CGoodin/nature-stack) (BSD-3-Clause) is an off-road autonomous-navigation stack (the NATURE autonomy stack, Mississippi State University): perception, mapping, and planning for unstructured terrain. URML is interesting at the intent layer above it: it declares the navigation goal and the operating constraints (the off-road equivalent of an ODD), validates them against the platform's capabilities and a safety envelope, and consumes the planned path. This RFC asks whether the mapping is useful.

## The mapping (URML beside the NATURE stack)

- **Declare the goal and the terrain bounds, validate, consume the path.** Off-road navigation has hard operating bounds (slope, traversability, standoff). URML expresses the goal plus those bounds as a safety envelope, validates the intent against the platform's declared capabilities, then consumes the path the stack plans (RFC-0020). The stack keeps ownership of terrain reasoning and planning.
- **A typed off-road ODD.** The contribution is a typed, declarative statement of where the vehicle is allowed to operate, checked before the planner commits.

## What is asked

Request for comment from the NATURE stack maintainers:

1. Is a typed, validated intent layer (goal + off-road operating bounds, validated, then consume the path) useful above an off-road stack?
2. Does URML's safety-envelope model map onto how off-road operating bounds (slope, traversability) are expressed?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the safety-envelope validation, and the substrate-neutral dispatch model. Part of Move #51; the off-road / unstructured-terrain target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `CGoodin/nature-stack` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move51.yaml`.
