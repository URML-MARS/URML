---
rfc: 0553
title: USC-ICT Virtual Human Toolkit integration — request for comment
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

# RFC-0553: USC-ICT Virtual Human Toolkit integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the HRI / conversational / robot-data wave (Move #50). This is a conceptual-peer note about embodied-agent intent, not a physical-robot integration ask.

## Summary

[`USC-ICT/vhtoolkit`](https://github.com/USC-ICT/vhtoolkit) (custom USC license) is the Virtual Human Toolkit: a research platform for building embodied conversational virtual humans. URML represents intent for *physical* embodied agents. The shared question is interesting: how should an embodied agent represent an actionable intent so it is unambiguous and checkable. This RFC is a conceptual-peer note, with no code reuse (the toolkit is under a custom USC license).

## The relationship (URML beside the Virtual Human Toolkit)

- **Two embodiments, one intent question.** Virtual humans and physical robots both turn understanding into embodied action. URML's contribution is a typed intent representation validated against a declared capability set and a safety envelope before action. For a virtual human the "capabilities" are different, but the idea of a checkable intent representation may transfer.
- **Conceptual only.** Given the custom license, this proposes no shared code, only a comparison of how each represents actionable intent.

## What is asked

Request for comment from the Virtual Human Toolkit maintainers:

1. Does a typed, validatable intent representation (checked against a declared capability set) map onto how the toolkit drives a virtual human's embodied behavior?
2. Is the physical-robot / virtual-human intent boundary an interesting comparison?
3. Which aspect, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's intent primitives (Layer 2), the capability manifest, and the safety-envelope validation. Part of Move #50; the virtual-embodiment edge of the conversational cluster. Research-scope; no claim that URML drives a virtual human today.

## Implementation note

Outreach only. The post is a GitHub Issue on `USC-ICT/vhtoolkit` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the license is a custom USC license; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move50.yaml`.
