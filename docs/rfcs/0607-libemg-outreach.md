---
rfc: 0607
title: LibEMG integration — request for comment
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

# RFC-0607: LibEMG integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the soft-robotics / assistive wave (Move #57). Research-scope: no clinical claim is made or intended.

## Summary

[`LibEMG/libemg`](https://github.com/LibEMG/libemg) (MIT, University of New Brunswick) is an open library for myoelectric control: it takes EMG signals through acquisition, featurization, and classification to an online control decision. URML is a natural consumer of the output: a decoded EMG intent is exactly the kind of recognized intent URML can take, validate against an assistive device's declared capabilities and a safety envelope, and dispatch. URML does not decode EMG; it consumes the recognized intent. This RFC asks whether that boundary is useful.

## The relationship (URML beside LibEMG)

- **Decode below, validate-and-dispatch above.** LibEMG turns muscle activity into a control decision. URML's role is what happens next: take that decoded intent, validate the resulting action against the device's declared capabilities and an operating envelope, then dispatch. For an assistive device, the "is this action admissible for this user and this device right now" check is exactly where a typed validation layer earns its place. LibEMG keeps the signal processing and the classifier.
- **Honest scope.** This is research-scope, matching LibEMG's own posture; nothing here is a clinical claim, and URML stays out of the decoding entirely.

## What is asked

1. Is a typed, validated action layer downstream of a decoded EMG intent (the action checked against the device's declared capabilities + envelope, then dispatched) useful for assistive-device research?
2. Does a decoded LibEMG control decision map cleanly onto a recognized-intent input to URML?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's decide-then-do split (RFC-0002), the capability manifest, the safety-envelope validation, and the consume-the-recognized-intent pattern (sibling to the dialogue-recognition framing in Move #50). Part of Move #57; the myoelectric / assistive target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `LibEMG/libemg` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Research-scope; no clinical claim. Tracked in `examples/lighthouses/outreach-move57.yaml`.
