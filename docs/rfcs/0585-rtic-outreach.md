---
rfc: 0585
title: RTIC integration — request for comment
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

# RFC-0585: RTIC integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the motor-control / RTOS substrate wave (Move #53), and with it the 2026-06-13 second candidate slate.

## Summary

[`rtic-rs/rtic`](https://github.com/rtic-rs/rtic) (Apache-2.0 / MIT) is a concurrency framework for real-time embedded Rust, built around predictable, priority-based task scheduling. That predictability is the interesting hook: URML recently grew a real-time timing block (RFC-0016) that lets a manifest declare cyclic timing and a watchdog, and RTIC is exactly the kind of substrate where such declared timing has a clean place to land.

## The relationship (URML beside RTIC)

- **Declared timing meets a real-time scheduler.** URML's real-time block (RFC-0016) declares cyclic timing requirements as part of a capability manifest. RTIC schedules tasks with predictable timing. The seam is whether URML's declared timing can map onto an RTIC task set, so that "this intent needs a 10 ms cycle with this watchdog" becomes a checkable claim against what RTIC actually guarantees.
- **A Rust executor with timing guarantees.** A minimal URML executor (RFC-0018 minimal_node) that needs predictable timing is a natural fit for RTIC's model.

## What is asked

1. Can URML's declared cyclic-timing requirements (RFC-0016) map onto an RTIC task set in a way that makes the timing claim checkable?
2. Is a small, pre-validated intent executor with timing requirements a sensible thing to express in RTIC?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's real-time timing block (RFC-0016), the minimal_node MCU execution shape (RFC-0018), and the Rust-leaning infrastructure direction. Completes Move #53 and the second candidate slate; the real-time-Rust target of the wave (with Embassy RFC-0584).

## Implementation note

Outreach only. The post is a GitHub Issue on `rtic-rs/rtic` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0 / MIT). Tracked in `examples/lighthouses/outreach-move53.yaml`.
