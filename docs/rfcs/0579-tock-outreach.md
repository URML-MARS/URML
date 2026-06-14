---
rfc: 0579
title: Tock OS integration — request for comment
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

# RFC-0579: Tock OS integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the motor-control / RTOS substrate wave (Move #53). Of the RTOS targets, Tock is the closest in spirit, because both projects treat capabilities as a safety boundary.

## Summary

[`tock/tock`](https://github.com/tock/tock) is a secure, embedded operating system for microcontrollers, notable for a capability-based isolation model that limits what each component is allowed to do. URML validates an intent against a declared capability manifest before it runs. The shared idea, capabilities as the thing that bounds what is permitted, is what makes this worth a note rather than a generic "please integrate" ask.

## The relationship (URML beside Tock)

- **Two capability models, one question.** Tock enforces capabilities at the OS level; URML checks an intent against a declared capability manifest at the language level. A natural thought: a minimal URML executor running as a Tock process would have its allowed actions bounded twice, once statically by the manifest and once at runtime by Tock's grants. Whether that double boundary is useful or redundant is a genuine question for people who think hard about embedded capabilities.
- **Honest altitude.** URML sits well above an OS. The seam here is narrow and specific: a constrained URML executor (RFC-0018 minimal_node) as a Tock app, with the two capability notions lined up.

## What is asked

1. Does aligning a language-level capability manifest with Tock's OS-level capability model make sense, or do the two notions of "capability" not usefully correspond?
2. Is a minimal, statically-validated intent executor a sensible shape for a Tock application?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the minimal_node MCU execution shape (RFC-0018), and the five-pass validator. Part of Move #53; the capability-secure RTOS target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `tock/tock` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the license is dual Apache-2.0 / MIT, reported as non-standard by GitHub; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move53.yaml`.
