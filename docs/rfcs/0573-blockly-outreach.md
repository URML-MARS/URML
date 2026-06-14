---
rfc: 0573
title: Raspberry Pi Foundation Blockly integration — request for comment
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

# RFC-0573: Raspberry Pi Foundation Blockly integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the education / competition wave (Move #52). This is a language-to-language note.

## Summary

[`RaspberryPiFoundation/blockly`](https://github.com/RaspberryPiFoundation/blockly) (Apache-2.0) is the Raspberry Pi Foundation's Blockly, the block-based visual programming toolkit behind learner-friendly coding editors. URML and block-based programming share a goal: lower the barrier to telling a machine what to do. They do it differently, and the boundary is interesting. This RFC is a conceptual-peer note, not an integration ask.

## The relationship (URML beside Blockly)

- **Two ways to lower the barrier.** Blockly lets a learner assemble a program from blocks. URML lets a learner (or an LLM) express a robot intent in a small typed language, optionally from an English sentence, and validates it against the robot's declared capabilities before it runs. For robotics specifically, a block palette could emit URML as its target representation, getting typed validation and a capability check for free.
- **Validation as a teaching tool.** URML's contribution to a block-based robotics editor would be the "is this actually possible on this robot, and why not" check, expressed in typed form.

## What is asked

Request for comment from the Raspberry Pi Foundation Blockly maintainers:

1. For robotics use, is a typed, validated intent representation (with a capability check) a useful compile target for a block palette?
2. Is the block-based / typed-intent boundary an interesting comparison for learner-facing robotics tools?
3. Which aspect, if any, is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the small typed primitive vocabulary (RFC-0002), the capability manifest, and the educational profile (RFC-0011). Part of Move #52; the visual-programming peer of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `RaspberryPiFoundation/blockly` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move52.yaml`.
