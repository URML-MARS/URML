---
rfc: 0584
title: Embassy integration — request for comment
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

# RFC-0584: Embassy integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the motor-control / RTOS substrate wave (Move #53); the Rust-embedded corner.

## Summary

[`embassy-rs/embassy`](https://github.com/embassy-rs/embassy) (Apache-2.0 / MIT) is a modern async embedded framework for Rust. URML's longer-running infrastructure (the validator service, the conformance harness) leans toward Rust by design, and on the device side a minimal URML executor (RFC-0018 minimal_node) for constrained targets is exactly the kind of thing Embassy is good at hosting.

## The relationship (URML beside Embassy)

- **A Rust executor on a Rust framework.** URML validates intent ahead of time and dispatches a checked plan. On a constrained Rust target, that executor wants an async, ergonomic embedded foundation, which is what Embassy provides. The seam is concrete: a minimal_node executor built on Embassy's async primitives.
- **Type-system alignment.** URML leans on types for its guarantees; Rust enforces a lot of that for free, so a Rust-side executor and URML's typed intent model are a natural pairing.

## What is asked

1. Is a small, pre-validated intent executor (async, on constrained targets) a sensible thing to build on Embassy?
2. Are there Embassy patterns you would steer such an executor toward, especially around timing and peripheral access?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's minimal_node MCU execution shape (RFC-0018), the Rust-leaning infrastructure direction, and the real-time timing block (RFC-0016). Part of Move #53; the Rust-embedded cluster (with RTIC RFC-0585).

## Implementation note

Outreach only. The post is a GitHub Issue on `embassy-rs/embassy` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0 / MIT). Tracked in `examples/lighthouses/outreach-move53.yaml`.
