---
rfc: 0146
title: OpenMind OM1 (mobile-humanoid AI runtime) integration, request for comment from OpenMind maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-28
updated: 2026-05-28
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

# RFC-0146: OpenMind OM1 (mobile-humanoid AI runtime) integration, request for comment from OpenMind maintainers

## Summary

URML does not yet ship an OpenMind OM1 manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for OpenMind's OM1 mobile-humanoid AI runtime over [`OpenMind/OM1`](https://github.com/OpenMind/OM1) (MIT), and **requests review and feedback from the OpenMind maintainers**. No spec change.

OpenMind has been quietly building an open mobile-humanoid OS layer; OM1 is the flagship runtime. The URML-fit framing is **URML sits one layer above OM1** — URML provides the substrate-neutral typed intent vocabulary, OM1 is the OS layer that dispatches.

## Motivation

`OpenMind/OM1` is the flagship in the OpenMind org. MIT license, 2.8k stars, Issues enabled, last commit `2026-05-27` very active (daily commits), **not archived**. OpenMind HQ is documented as United States; the org has 28 public repos with `openmind.com` as the corporate domain.

The structural URML alignment is clean:

- OpenMind ships the mobile-humanoid **runtime** (OS layer).
- URML ships the substrate-neutral **intent language** (one layer above).
- An OM1 deployment with URML's adapter can consume validated typed primitives and dispatch them onto the humanoid; the manifest declares the OM1 binding.

This is structurally similar to URML's existing relationships with ROS 2 / PX4 / Isaac Lab — URML sits above as the vocabulary; the substrate dispatches below.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `openmind_om1_cell.yaml` fixture)

| URML field | Maps to OM1 attribute |
|---|---|
| `name` | Deployment handle (`openmind_om1_default`) |
| `substrate: custom` (`openmind_om1`) | Declares the OM1 runtime is the OS-layer below URML |
| `substrate.version` | OM1 version pin |
| `mobility` block | OM1's mobile-humanoid mobility primitives (URML's existing biped / quadruped / mobile-base mobility classes) |
| `actuators` block | OM1's joint / EEF declarations |
| `cameras` + `sensors` blocks | OM1's perception modules |

### What URML v0.1 does not yet express for OM1

1. **OS-layer substrate declaration.** URML's manifest does not today have a first-class `substrate.os` field. The closest existing concept is the substrate-runtime declaration (ROS 2 / PX4 / vendor SDK); a Spec RFC adding `os_runtime` as a distinct class is queued.
2. **OS-vs-policy boundary declaration.** OM1 ships both OS-level functionality (process management, scheduling) and policy-level functionality (some learned controllers). URML's manifest cannot today distinguish.
3. **Mobile-humanoid mobility specialization.** URML's `mobility.drive_type` includes `biped` per RFC-0009 but not `mobile_humanoid` (mobile-base + biped torso); a Spec RFC adding the composite class is queued.

### Compatibility notes

- **Vendor org.** [`OpenMind`](https://github.com/OpenMind) — vendor-direct.
- **Flagship repo.** [`OpenMind/OM1`](https://github.com/OpenMind/OM1) — MIT, 2.8k stars, Issues enabled, last commit 2026-05-27 daily activity, **not archived**.
- **Origin.** OpenMind (openmind.com), United States. Passes US-federal default policy.
- **License fit.** MIT cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Very active surface (28 public repos, 372 followers, daily commits). Active commercial-startup engagement.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; OS-layer substrate declaration Spec RFC queued + mobile-humanoid mobility-class Spec RFC queued.
- Reference runtime: future `reference/humanoid-runtime/OpenMindOM1Adapter` is a strong candidate; complements existing humanoid-runtime work and the Move-1 mobile-base runtime.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Two Spec-RFC prerequisites** (OS-layer substrate + mobile-humanoid mobility class).
- **OS-vs-policy boundary in OM1 is implicit.** URML's manifest declares the OM1 binding but cannot today reason about which OM1 functionality is OS-level vs policy-level.

## Alternatives considered

1. **Engage OpenMind broader (the 28 public repos).** Rejected. OM1 is the flagship; engaging at the flagship is the cleaner shape for vendor-direct discussion.
2. **Bundle OpenMind OM1 + humanoid OEMs (Apptronik, Sanctuary, 1X, Figure — Move-12 backlog Theme B) into one humanoid-stack RFC.** Rejected. OM1 is OS-layer; OEMs are hardware-layer. Different abstractions.
3. **Cross-citation only.** Rejected. The OS-substrate manifest declaration is a concrete enough question for direct engagement.

## Prior art

- [`OpenMind/OM1`](https://github.com/OpenMind/OM1) — the upstream flagship.
- URML's existing humanoid manifest fixtures (`anymal_quadruped.yaml`, `apollo_biped.yaml`, `digit_biped.yaml`, etc.) — the manifest patterns OM1's mobile-humanoid topology composes with.
- [RFC-0009 (Layer-1 mobility specialization)](0009-layer1-mobility-specialization.md) — Spec RFC that added `biped` / `quadruped` mobility types; mobile-humanoid is the missing composite.

## Unresolved questions

For the OpenMind OM1 maintainers:

1. **OS-layer substrate manifest declaration.** URML's v0.1 has no `substrate.os` field. A Spec RFC adding it is queued. What manifest fields would an OM1 deployment expect (OS version, supported hardware, capability flags)?
2. **OS-vs-policy boundary declaration.** OM1 ships both OS-level and policy-level functionality. Should URML's manifest declare which is active at which boundary?
3. **Mobile-humanoid mobility class.** URML's `mobility.drive_type` includes `biped` but not `mobile_humanoid` (mobile-base + biped torso). Manifest field expectations from OpenMind?
4. **Adapter home.** URML repo (`reference/humanoid-runtime/OpenMindOM1Adapter`), OpenMind-maintained `OpenMind/OM1-urml-bridge`, or both?
5. **Conformance listing.** Would the OpenMind maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
6. **Anything else.**

## Implementation note

RFC-0146 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move11.yaml`](../../examples/lighthouses/outreach-move11.yaml).

## How to respond

`OpenMind/OM1` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the OS-layer-substrate question explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (MIT, 2.8k stars, Issues enabled, last commit 2026-05-27 daily activity, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (two Spec-RFC prerequisites, OS-vs-policy boundary implicit).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: OpenMind US; default policy passes.
- [x] CLAUDE.md compliance check passed.
