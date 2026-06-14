---
rfc: 0595
title: NIMS-OS integration — request for comment
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

# RFC-0595: NIMS-OS integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the lab-automation wave (Move #54).

## Summary

[`nimsos-dev/nimsos`](https://github.com/nimsos-dev/nimsos) (National Institute for Materials Science, Japan) is NIMS-OS, software for running autonomous materials-science experiments: it closes the loop between an AI decision layer and robotic experimental equipment, including a file-exchange path so non-Python instruments can participate. URML is a conceptual peer at the per-device step. This RFC asks where the two layers meet.

## The relationship (URML beside NIMS-OS)

- **AI decision above, validated device action below.** NIMS-OS decides the next experiment and drives the equipment to run it. URML's candidate role is the typed, pre-dispatch validation of the equipment-facing action: checked against that equipment's declared capabilities and limits before NIMS-OS issues it. The AI loop and the experiment design stay with NIMS-OS.
- **A neutral action representation across the file-exchange boundary.** Because NIMS-OS already crosses into non-Python instruments via file exchange, a small, typed, runtime-neutral action representation is a natural fit for what travels across that boundary, and a capability manifest is what it would be checked against.

## What is asked

1. Is a typed, validated device action (checked against declared equipment capabilities before dispatch) useful in the NIMS-OS loop?
2. Could a runtime-neutral typed action representation help at the file-exchange boundary to non-Python instruments?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the decide-then-do split (RFC-0002), and the substrate-neutral dispatch model. Completes Move #54; the autonomous-materials-experiment peer of the wave (with AlabOS RFC-0591).

## Implementation note

Outreach only. The post is a GitHub Issue on `nimsos-dev/nimsos` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. The repository has no license file, so the post states that and makes no licensing request and proposes no code reuse. Tracked in `examples/lighthouses/outreach-move54.yaml`.
