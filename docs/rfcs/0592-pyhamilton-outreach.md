---
rfc: 0592
title: PyHamilton integration — request for comment
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

# RFC-0592: PyHamilton integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the lab-automation wave (Move #54).

## Summary

[`dgretton/pyhamilton`](https://github.com/dgretton/pyhamilton) (MIT) is a Python interface for programming Hamilton liquid-handling robots, widely used to script real protocols. It is a vendor-specific substrate, the kind of concrete runtime URML is designed to dispatch validated intent to. This RFC asks whether a typed intent layer above PyHamilton is useful.

## The relationship (URML beside PyHamilton)

- **A concrete substrate for validated intent.** URML validates an intent against a declared capability manifest and a safety envelope, then dispatches to whatever executes it. PyHamilton is one such executor: a protocol step, once checked against the configured deck's capabilities and limits, is realized as PyHamilton calls. URML adds the typed, pre-dispatch check and (via Layer 4) an optional natural-language front door; PyHamilton stays the Hamilton interface.
- **Deck configuration toward a manifest.** A PyHamilton script assumes a particular deck layout and labware; that configuration is the lab-automation analogue of a capability manifest a step could be validated against.

## What is asked

1. Is a typed, validated intent layer (a step checked against the configured deck before it becomes PyHamilton calls) useful above PyHamilton?
2. Could a deck/labware configuration serve as the capability manifest the validation checks against?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the Layer-4 natural-language grammar, the five-pass validator, and the substrate-neutral dispatch model. Part of Move #54; the vendor-specific liquid-handler substrate of the wave (sibling to the hardware-agnostic PyLabRobot RFC-0587).

## Implementation note

Outreach only. The post is a GitHub Issue on `dgretton/pyhamilton` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move54.yaml`.
