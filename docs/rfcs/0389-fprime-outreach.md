---
rfc: 0389
title: F´ (F Prime) integration — request for comment on a flight-software binding
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

# RFC-0389: F´ (F Prime) integration — request for comment on a flight-software binding

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target, and asking its maintainers for feedback. It builds on URML's existing substrate-binding pattern ([RFC-0015](0015-control-program-invocation.md) `call_program` + [RFC-0019](0019-autosar-adaptive-substrate.md)'s AUTOSAR binding) and the `realtime` block ([RFC-0016](0016-realtime-cyclic-manifest-block.md)).

## Summary

[F´ / F Prime](https://github.com/nasa/fprime) (JPL, Apache-2.0, ~11k stars) is a component-driven flight-software framework for CubeSats, SmallSats, and instruments — a non-ROS substrate whose surface is named components that expose commands. URML already has a pattern for exactly this shape: a substrate that exposes named operations is bound to `call_program`, not given a new primitive (the AUTOSAR `ara::com` precedent, RFC-0019). This RFC asks the F´ maintainers whether a URML → F´ command binding is a faithful mapping.

## The mapping (URML above F´)

URML sits above F´ as a validated intent layer; F´ remains the flight-software substrate that executes:

- An F´ component command (component + opcode + typed arguments) is declared in the URML manifest as a `program` with a binding, exactly as RFC-0019 binds an AUTOSAR `ara::com` service method. `call_program(name, args)` is the verb; URML validates the binding is complete and the args match the declared signature before dispatch.
- F´ rate groups / cyclic execution map onto URML's descriptive `realtime` block (RFC-0016): cycle period and watchdog as declarations, with no claim that URML enforces hard real-time.
- URML adds no F´-specific primitive: command dispatch rides `call_program`, the substrate-neutral discipline the spec-gap loop (RFC-0014) requires.

## What is asked

Request for comment from F´ maintainers:

1. Is a declared `program` + command binding (component / opcode / typed args) the right granularity to name an F´ command from an outside intent layer, or is a different handle more natural?
2. Does mapping F´ rate-group timing onto a descriptive `realtime` declaration (period + watchdog, no enforcement claim) read as honest from your side?
3. Where would a URML → F´ binding sit relative to the ground command/dictionary tooling (the command dictionary as the source of the binding declarations)?

Nothing here asks F´ to adopt, host, or maintain anything.

## Prior art / context

RFC-0015 (`call_program`), RFC-0019 (the AUTOSAR `ara::com` binding this mirrors), RFC-0016 (`realtime`). OPC UA Robotics method nodes are the structural precedent: a service/command-oriented substrate bound rather than given a new primitive.

## Implementation note

Outreach only. The post is a GitHub Discussion on `nasa/fprime` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move31.yaml`.
