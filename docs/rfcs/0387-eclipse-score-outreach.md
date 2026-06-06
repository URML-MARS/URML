---
rfc: 0387
title: Eclipse S-CORE integration — request for comment on the ara::com binding
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

# RFC-0387: Eclipse S-CORE integration — request for comment on the ara::com binding

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking that target's maintainers for feedback. The normative surface it builds on, [RFC-0019](0019-autosar-adaptive-substrate.md) (the AUTOSAR `ara::com` program binding), already shipped (Implemented 2026-06-06).

## Summary

[Eclipse S-CORE](https://github.com/eclipse-score/score) (the Eclipse Safe Open Vehicle Core, Apache-2.0; an Eclipse Foundation open-source software-defined-vehicle core for high-performance ECUs, backed by BMW, Mercedes-Benz, ETAS, Accenture, and Qorix) is the open, service-oriented, AUTOSAR-Adaptive-aligned platform URML's AUTOSAR work targets. URML's `ara::com` binding (RFC-0019) lets a manifest pin a `call_program` to a concrete service-method invocation (service / instance / method id triple). This RFC maps that onto S-CORE's communication layer and asks the maintainers whether a substrate-neutral, validated intent layer above S-CORE is interesting.

## The mapping (URML above S-CORE)

URML sits above the SDV stack as a validated intent vocabulary; S-CORE is the substrate that realizes the calls:

- A declared `program` with `binding: { kind: ara_com, service_id, instance_id, method_id }` (RFC-0019) names an S-CORE / AUTOSAR-Adaptive service method. `call_program(name, args)` (RFC-0015) is the verb; the validator checks the binding is complete and the args match the declared signature before dispatch.
- The cyclic timing contract of an S-CORE Execution-Management deployment maps onto URML's `realtime` block (RFC-0016): `MinimumCycleTime` → `cyclic_period_ms`, `WatchdogTimeout` → `watchdog_ms`. URML never claims to enforce hard real-time; the field is a descriptive, internally-checked declaration.
- URML adds no AUTOSAR-specific primitive: service-method invocation rides `call_program`, exactly the substrate-neutral discipline the spec-gap loop (RFC-0014) requires.

## What is asked

Request for comment from Eclipse S-CORE maintainers:

1. Is the `call_program` + `ara_com` binding (service/instance/method id triple) the right granularity to name an S-CORE service method from an outside intent layer, or is a different handle more natural?
2. Does mapping S-CORE Execution-Management timing onto URML's descriptive `realtime` block (period + watchdog, no enforcement claim) read as honest from your side?
3. Where would a URML → S-CORE adapter sit relative to the platform's communication and execution-management interfaces?

Nothing here asks S-CORE to adopt, host, or maintain anything. The adapter is URML's to build.

## Prior art / context

RFC-0019 (the binding this proposes), RFC-0015 (`call_program`, the verb it rides), RFC-0016 (`realtime`, the cyclic-timing block). The OPC UA Robotics engagement (RFC-0015's motivating case) is the structural precedent: a service-oriented substrate exposing named methods, bound rather than given a new primitive.

## Implementation note

Outreach only. RFC-0019 already shipped the binding. The post is a GitHub Discussion (or Issue) on `eclipse-score/score` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move30.yaml`.
