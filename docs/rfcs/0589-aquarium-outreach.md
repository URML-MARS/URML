---
rfc: 0589
title: Aquarium (UW BIOFAB) integration — request for comment
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

# RFC-0589: Aquarium (UW BIOFAB) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the lab-automation wave (Move #54).

## Summary

[`aquariumbio/aquarium`](https://github.com/aquariumbio/aquarium) (MIT, University of Washington BIOFAB) is a laboratory operating system that represents protocols as typed unit operations with declared inputs and outputs and tracks samples and inventory through a workflow. The typed-operation idea is the hook: URML also represents what a robot should do as a small set of typed operations with declared, checkable arguments. This RFC compares the two notions of a typed operation.

## The relationship (URML beside Aquarium)

- **Typed operations, two domains.** Aquarium's unit operations carry typed inputs and outputs over samples and labware. URML's primitives carry typed arguments validated against a capability manifest. Where a step touches a physical instrument or robot, URML's per-step validation (does the configured equipment support this operation, within these limits) could complement Aquarium's typed-IO model.
- **Where the boundary sits.** Aquarium owns the protocol, the sample tracking, and the lab workflow. URML's candidate role is narrow: the typed, pre-dispatch check on the equipment-facing steps. The question is whether that check adds anything Aquarium's own typing does not already give.

## What is asked

1. Do Aquarium's typed unit operations and URML's typed primitives describe the same kind of thing closely enough that a shared capability check would be useful on equipment-facing steps?
2. Is a pre-dispatch validation of an operation against declared equipment capabilities meaningful in Aquarium's model, or is that already covered?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's typed primitive vocabulary (RFC-0002), the capability manifest, and the five-pass validator. Part of Move #54; the typed-protocol peer of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `aquariumbio/aquarium` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (MIT). Tracked in `examples/lighthouses/outreach-move54.yaml`.
