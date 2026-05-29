---
rfc: 0210
title: Eclipse iceoryx (zero-copy intra-process IPC substrate) integration, request for comment from iceoryx maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0210: Eclipse iceoryx (zero-copy intra-process IPC substrate) integration

## Summary

URML's substrate manifest declares the RMW middleware class but does not declare the IPC sub-substrate (zero-copy intra-process transport). iceoryx is the canonical zero-copy IPC for ROS 2 intra-process and is integrated as a shared-memory backend in Fast DDS and Cyclone DDS. This RFC documents the proposed URML v0.1 capability-manifest mapping for the IPC-substrate class, engaged at the Eclipse Foundation governance layer via [`eclipse-iceoryx/iceoryx`](https://github.com/eclipse-iceoryx/iceoryx) (Apache-2.0), and **requests review and feedback from the iceoryx maintainers**. No spec change.

This is a **Tier B IPC-substrate** engagement. Third of three Eclipse Foundation engagements in Move-16 (Cyclone DDS sibling [RFC-0204](0204-cyclone-dds-outreach.md), Zenoh sibling [RFC-0209](0209-zenoh-outreach.md), iceoryx).

## Motivation

iceoryx provides true zero-copy IPC for ROS 2 intra-process communication and is the standard transport for high-frequency-large-payload paths (camera images, lidar point clouds). URML's substrate manifest currently leaves the IPC sub-substrate unspecified; high-throughput deployments need it explicit.

Repo at [`eclipse-iceoryx/iceoryx`](https://github.com/eclipse-iceoryx/iceoryx) (Apache-2.0, 2.1k stars, Issues enabled, last commit `2026-05-28`, **not archived**). Eclipse Foundation governance.

URML benefits from documenting the engagement because:

1. **IPC-substrate declaration is URML's missing manifest sub-layer.** RMW choice + IPC choice are independent degrees of freedom; URML's manifest could declare both for production determinism.
2. **Zero-copy shared-memory budget hints.** iceoryx's memory pool configuration is performance-tier relevant; URML's manifest could declare hints.
3. **iceoryx2 successor track.** The `iceoryx2` rewrite is under active development; URML's manifest could declare which iceoryx generation is active.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `ros2_iceoryx_cell.yaml` fixture)

| URML field | Maps to iceoryx attribute |
|---|---|
| `name` | Deployment handle (`ros2_humble_iceoryx`) |
| `substrate.class: ros2` (RFC-0200) | Parent substrate enum |
| `substrate.ipc_substrate: iceoryx` | URML's first IPC-substrate enum value |
| `substrate.ipc_generation: iceoryx1` / `iceoryx2` | iceoryx vs iceoryx2 generation |
| `ipc.shared_memory_pool_size_mb` | iceoryx memory-pool budget hint |
| `ipc.max_publisher_count` / `ipc.max_subscriber_count` | iceoryx pub/sub count budgets |
| `ipc.runtime_name` | RouDi runtime name |

### What URML v0.1 does not yet express for iceoryx

1. **IPC-substrate enum.** First-class IPC-sub-substrate field; URML's first.
2. **IPC-generation field.** iceoryx vs iceoryx2 (the C++ vs Rust rewrites); URML's manifest could declare per-deployment generation.
3. **Memory-pool budget hints.** Shared-memory budget is deployment-critical; URML's manifest could declare hints for envelope-validation.
4. **RouDi runtime name.** The iceoryx runtime daemon name is deployment configuration; URML's manifest could declare.

### Compatibility notes

- **Vendor org.** [`eclipse-iceoryx`](https://github.com/eclipse-iceoryx) — Eclipse Foundation.
- **Engagement repo.** [`eclipse-iceoryx/iceoryx`](https://github.com/eclipse-iceoryx/iceoryx) — Apache-2.0, 2.1k stars, Issues enabled, last commit 2026-05-28, **not archived**.
- **Companion repos.** [`eclipse-iceoryx/iceoryx2`](https://github.com/eclipse-iceoryx/iceoryx2) — the Rust rewrite under active development.
- **Origin.** Eclipse Foundation. NATO-allied; passes US-federal default policy.
- **License fit.** Apache-2.0. Clean fit.
- **Maintainer signal.** Active commits; the canonical ROS 2 zero-copy IPC.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; IPC-substrate enum + IPC-generation field + memory-pool budget hints Spec RFCs queued.
- Reference runtime: URML's existing `reference/ros2-runtime/` adapter is IPC-agnostic today; iceoryx is RMW-side env-var configuration. Manifest-side declaration is the proposed extension.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **IPC-substrate-novelty** — URML's first IPC-sub-substrate declaration; no prior pattern.
- **iceoryx1 vs iceoryx2 generation drift** — the Rust rewrite is the future; URML's manifest must accommodate the generation transition cleanly.
- **Memory-pool semantic complexity** — shared-memory budgets are deployment-critical and easy to misconfigure; URML's manifest hint semantics need care.

## Alternatives considered

1. **Skip iceoryx; let RMW choice imply IPC choice.** Rejected. IPC is a real independent degree of freedom; production users routinely override IPC per-deployment.
2. **Engage at the iceoryx2 successor instead of iceoryx1.** Considered. iceoryx2 is sub-stable; engagement at iceoryx covers both via the same maintainer group.
3. **Bundle iceoryx with Zenoh in a single Eclipse-IPC RFC.** Rejected. iceoryx is intra-host zero-copy IPC; Zenoh is network pub-sub overlay. Different layers, different concerns; per-project RFCs let conversation thread per group.

## Prior art

- [`eclipse-iceoryx/iceoryx`](https://github.com/eclipse-iceoryx/iceoryx) — the upstream iceoryx stack (engagement anchor).
- [RFC-0200 (ROS 2 core outreach)](0200-ros2-core-outreach.md) — parent substrate engagement.
- [RFC-0203 (Fast DDS outreach)](0203-fast-dds-outreach.md), [RFC-0204 (Cyclone DDS outreach)](0204-cyclone-dds-outreach.md) — sibling Move-16 batch-2 RFCs; the RMW layer above iceoryx.
- [RFC-0209 (Zenoh outreach)](0209-zenoh-outreach.md) — sibling Move-16 batch-3 RFC under shared Eclipse Foundation governance.

## Unresolved questions

For the Eclipse iceoryx maintainers:

1. **IPC-substrate enum manifest field.** URML's first; preferred enum value (`iceoryx`, `eclipse_iceoryx`)?
2. **IPC-generation field.** iceoryx1 vs iceoryx2 — manifest field shape, and timing of URML's recommended generation default?
3. **Memory-pool budget hint shape.** Shared-memory budget is deployment-critical; URML's preferred manifest hint format?
4. **RouDi runtime name declaration.** Manifest field for the iceoryx daemon name, or always launch-side?
5. **Per-pub / per-sub limit declaration.** Should URML's manifest declare `max_publisher_count` / `max_subscriber_count` budgets for envelope-validation?
6. **iceoryx2 migration path.** Does the iceoryx team have a position on URML's manifest declaring the migration intent (e.g. `ipc_generation: iceoryx2-preferred-fallback-iceoryx1`)?
7. **Conformance listing.** Would iceoryx / the Eclipse Foundation consider a project link to URML's compatible-runtimes registry ([RFC-0014](0014-conformance.md))?
8. **Anything else.**

## Implementation note

RFC-0210 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`eclipse-iceoryx/iceoryx` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the IPC-substrate-declaration + Eclipse-Foundation framing explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (Apache-2.0, 2.1k stars, Issues enabled, last commit 2026-05-28, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (IPC-substrate novelty, iceoryx1 vs iceoryx2 generation drift, memory-pool semantic complexity).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Eclipse Foundation; NATO-allied; default policy passes.
- [x] CLAUDE.md compliance check passed.
