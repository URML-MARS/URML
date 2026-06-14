---
rfc: 0564
title: AgOpenGPS integration — request for comment
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

# RFC-0564: AgOpenGPS integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the AV / ADAS / off-road wave (Move #51); the agriculture vertical.

## Summary

[`AgOpenGPS-Official/AgOpenGPS`](https://github.com/AgOpenGPS-Official/AgOpenGPS) (Apache-2.0) is a widely-used open agricultural guidance and auto-steer system: it plans coverage of a field and steers an implement along guidance lines. URML is interesting at the intent layer above it: a field operation is a goal (cover this field, follow this guidance pattern) plus constraints (implement width, headland, keep-out), which URML can declare, validate against the machine's declared capabilities and a safety envelope, and then let AgOpenGPS execute. This RFC asks whether the mapping is useful.

## The mapping (URML beside AgOpenGPS)

- **Declare the field operation, validate, AgOpenGPS guides.** A coverage task is a goal plus constraints. URML expresses it, validates against the machine and implement's declared capabilities and an operating envelope, then consumes the guidance plan AgOpenGPS produces. AgOpenGPS keeps ownership of guidance and steering.
- **A natural-language front door for field tasks.** Because URML's Layer 4 turns an instruction into validated intent, "cover the north field, 6 metre swath, skip the wet corner" can become a checked field operation. The agricultural framing is a real vertical, not a metaphor.

## What is asked

Request for comment from the AgOpenGPS maintainers:

1. Is a typed, validated intent layer (declare the field operation + constraints, validate, then guide) useful above AgOpenGPS?
2. Does URML's capability + safety-envelope model fit how a machine and implement's operating bounds are expressed?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's plan_path / follow_trajectory consume model (RFC-0020), the Layer-4 natural-language grammar, and the agriculture-profile direction. Part of Move #51; the agriculture vertical of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `AgOpenGPS-Official/AgOpenGPS` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move51.yaml`.
