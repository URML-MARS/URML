---
rfc: 0551
title: retico-core integration — request for comment
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

# RFC-0551: retico-core integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the HRI / conversational / robot-data wave (Move #50).

## Summary

[`retico-team/retico-core`](https://github.com/retico-team/retico-core) (Apache-2.0) is a framework for incremental spoken dialogue processing: it handles language as it arrives, incrementally, rather than in complete turns. URML is a peer at a later layer: once a dialogue system has recognized an actionable intent, URML is a typed representation of that intent, validated against the robot's capabilities and a safety envelope before dispatch. This RFC is a layering note.

## The relationship (URML beside retico-core)

- **Incremental recognition, then validated commit.** retico-core processes dialogue incrementally and recognizes intent as it forms. URML is what the recognized intent commits to: a typed primitive checked against a capability manifest + safety envelope before it reaches the robot. The incremental layer stays responsive; the commit is statically validated.
- **A clean boundary.** retico-core is about understanding language in real time; URML is about turning a recognized intent into something safe and runnable. Naming the seam lets an incremental-dialogue robot reuse both.

## What is asked

Request for comment from the retico-core maintainers:

1. Is "retico recognizes the intent incrementally; URML is the validated representation it commits to" a sensible layering for a dialogue-driven robot?
2. Does URML's capability + safety-envelope validation fit where an incremental dialogue system hands off to actuation?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-4 natural-language grammar, the five-pass validator, and the decide-then-do split (RFC-0002). Part of Move #50; the dialogue-recognition complement to the LLM-bridge framing in ROSGPT (RFC-0549) and DialoStack (RFC-0550).

## Implementation note

Outreach only. The post is a GitHub Issue on `retico-team/retico-core` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move50.yaml`.
