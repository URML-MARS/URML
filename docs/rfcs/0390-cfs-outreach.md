---
rfc: 0390
title: core Flight System (cFS) integration — request for comment on a flight-software binding
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-06
updated: 2026-06-06
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

# RFC-0390: core Flight System (cFS) integration — request for comment on a flight-software binding

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target, and asking its maintainers for feedback. It builds on URML's substrate-binding pattern ([RFC-0015](0015-control-program-invocation.md) + [RFC-0019](0019-autosar-adaptive-substrate.md)) and the `realtime` block ([RFC-0016](0016-realtime-cyclic-manifest-block.md)).

## Summary

[core Flight System (cFS)](https://github.com/nasa/cFS) (NASA Goddard, Apache-2.0, ~1.3k stars) is a generic flight-software architecture: a set of applications communicating over a software bus, flown on flagship spacecraft, human spacecraft, CubeSats, and even Raspberry Pi. Like F´ and AUTOSAR, its surface is named operations (app commands over the software bus). URML binds that shape to `call_program` rather than adding a primitive (RFC-0019 precedent). This RFC asks the cFS maintainers whether a URML → cFS command binding is faithful.

## The mapping (URML above cFS)

URML sits above cFS as a validated intent layer; cFS remains the substrate:

- A cFS app command (the app + command code + typed arguments / message) is declared in the URML manifest as a `program` with a binding, exactly as RFC-0019 binds an AUTOSAR `ara::com` method and RFC-0389 proposes for F´. `call_program(name, args)` is the verb; URML validates the binding and args before dispatch.
- cFS scheduler / cyclic table timing maps onto URML's descriptive `realtime` block (RFC-0016): period and watchdog as honest declarations, not an enforcement claim.
- No cFS-specific primitive: command dispatch rides `call_program`, the substrate-neutral discipline RFC-0014 requires.

## What is asked

Request for comment from cFS maintainers:

1. Is a declared `program` + command binding (app / command code / typed message) the right granularity to name a cFS command from an outside intent layer?
2. Does mapping the cFS scheduler's cyclic timing onto a descriptive `realtime` declaration read as honest?
3. Where would a URML → cFS binding sit relative to the command/telemetry database (the cmd/tlm definitions as the source of the binding declarations)?

Nothing here asks cFS to adopt, host, or maintain anything.

## Prior art / context

RFC-0015 (`call_program`), RFC-0019 (AUTOSAR `ara::com` binding), RFC-0389 (the sibling F´ binding), RFC-0016 (`realtime`). cFS and F´ are the two flight-software substrates in this wave; the binding shape is shared.

## Implementation note

Outreach only. The post is a GitHub Discussion on `nasa/cFS` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move31.yaml`.
