---
rfc: 0198
title: MAVSDK (Dronecode high-level MAVLink SDK) integration, request for comment from MAVSDK maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-29
updated: 2026-05-29
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

# RFC-0198: MAVSDK (high-level MAVLink SDK) integration

## Summary

URML does not yet ship a MAVSDK manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for MAVSDK — the high-level MAVLink SDK enabling cross-vendor vehicle control abstraction — over [`mavlink/MAVSDK`](https://github.com/mavlink/MAVSDK) (BSD-3-Clause), and **requests review and feedback from the MAVSDK maintainers**. No spec change.

MAVSDK is the **SDK-layer adapter target** for URML's drone-runtime. Where PX4 (RFC-0196) is the autopilot substrate and MAVLink (RFC-0197) is the protocol, MAVSDK is the high-level cross-vendor abstraction URML's adapter pattern composes at most naturally.

## Motivation

MAVSDK provides language bindings (C++, Python, Java, Swift, Go) over MAVLink, exposing a high-level API for mission management, telemetry, parameter control, and offboard control across PX4 / ArduPilot / compatible autopilots. Repo at [`mavlink/MAVSDK`](https://github.com/mavlink/MAVSDK) (BSD-3-Clause, 881 stars, Issues enabled, last commit `2026-05-26`, **not archived**).

URML benefits from documenting the MAVSDK manifest mapping because:

1. **MAVSDK is the natural adapter-entry layer.** URML's adapter pattern targets stable high-level APIs rather than raw protocol bytes. MAVSDK's `System` / `Telemetry` / `Action` / `Mission` / `Offboard` plugins map to URML's primitive vocabulary cleanly.
2. **Cross-vendor abstraction matches URML's substrate-neutrality.** MAVSDK abstracts over PX4 / ArduPilot / compatible autopilots; URML's manifest can declare MAVSDK-as-substrate without committing to a specific autopilot brand.
3. **BSD-3-Clause across the entire SDK** composes cleanly with URML's Apache-2.0 adapter stance.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `mavsdk_substrate_cell.yaml` fixture)

`substrate` + `capabilities` blocks:

| URML field | Maps to MAVSDK attribute |
|---|---|
| `substrate.sdk: custom` (`mavsdk`) | Declares MAVSDK as the high-level SDK substrate |
| `substrate.mavsdk_version` | MAVSDK release version pin |
| `substrate.language_binding` | `cpp` / `python` / `java` / `swift` / `go` — declares which MAVSDK binding the adapter consumes |
| `capabilities.plugins` | List of active MAVSDK plugins (`Action` / `Telemetry` / `Mission` / `Offboard` / `Param` / `Gimbal` / etc.) |
| `capabilities.offboard_mode` | Offboard control declaration (relevant for autonomous URML deployments vs human-supervised) |

### What URML v0.1 does not yet express for MAVSDK

1. **SDK-layer substrate declaration.** URML's v0.1 has no `substrate.sdk` field. Spec RFC queued (companion to RFC-0196 autopilot-substrate + RFC-0197 protocol-substrate at the SDK-abstraction layer).
2. **MAVSDK plugin-set declaration.** MAVSDK plugins enable per-capability functionality; URML's manifest cannot today declare which plugins are active.
3. **Offboard-vs-supervised mode declaration.** MAVSDK's Offboard plugin enables autonomous control (URML's natural deployment mode); URML's manifest cannot today declare this control-authority class.
4. **Language-binding declaration.** Adapter implementation language (C++ vs Python) affects URML's adapter shape; URML's manifest cannot today declare which binding is the active adapter substrate.

### Compatibility notes

- **Vendor / foundation.** [`mavlink`](https://github.com/mavlink) — Linux Foundation Dronecode Foundation (shared org with MAVLink protocol RFC-0197 and QGroundControl RFC-0208).
- **Flagship repo.** [`mavlink/MAVSDK`](https://github.com/mavlink/MAVSDK) — BSD-3-Clause, 881 stars, Issues enabled, last commit 2026-05-26, **not archived**.
- **Origin.** Dronecode Foundation. Passes US-federal default policy.
- **License fit.** BSD-3-Clause cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Active (2 days from cutoff); foundation-direct; the canonical high-level MAVLink SDK.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; SDK-substrate + plugin-set + offboard-mode + language-binding declaration Spec RFCs queued.
- Reference runtime: future `reference/drone-runtime/MavsdkAdapter` is a strong candidate — high-level SDK is the natural URML adapter-entry layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Multiple Spec-RFC prerequisites** (SDK substrate, plugin-set, offboard mode, language binding).
- **Plugin-set is deployment-specific** — URML's manifest needs a flexible declaration scheme to handle MAVSDK's growing plugin catalog.
- **MAVSDK abstraction-layer overhead** — for low-level / latency-critical deployments, raw MAVLink (RFC-0197) may be more appropriate; URML's manifest must support both layers.

## Alternatives considered

1. **Engage at the language-binding layer (MAVSDK-Python, MAVSDK-Java) separately.** Rejected. The core MAVSDK is the canonical engagement entry; per-binding engagement is downstream.
2. **Skip MAVSDK and engage only at the MAVLink protocol layer (RFC-0197).** Rejected. SDK-layer is where URML's adapter pattern composes most naturally; both layers warrant engagement.
3. **Bundle MAVSDK + PX4 + MAVLink into one Dronecode RFC.** Rejected. Per-project engagement is the cleaner shape; Dronecode-level convergence happens at the maintainer-discussion level if appropriate.

## Prior art

- [`mavlink/MAVSDK`](https://github.com/mavlink/MAVSDK) — the upstream SDK.
- [RFC-0196 (PX4-Autopilot)](0196-px4-autopilot-outreach.md), [RFC-0197 (MAVLink)](0197-mavlink-outreach.md), [RFC-0208 (QGroundControl)](0208-qgroundcontrol-outreach.md) — sibling Move-16 Dronecode-org RFCs.
- [RFC-0008 (drone profile)](0008-drone-profile.md) — URML's drone-profile that MAVSDK-class adapters implement.

## Unresolved questions

For the MAVSDK maintainers:

1. **SDK-substrate manifest fields.** URML's v0.1 has no `substrate.sdk` declaration. Spec RFC queued. Manifest field expectations from the MAVSDK perspective?
2. **Plugin-set declaration.** Should URML's manifest declare which MAVSDK plugins are active, and at what granularity (per-plugin enable, per-feature flag)?
3. **Offboard-vs-supervised mode declaration.** Manifest field for control-authority class (autonomous vs human-supervised)?
4. **Language-binding declaration.** Should URML's manifest declare which MAVSDK binding (C++ / Python / Java / Swift / Go) is the active adapter substrate?
5. **Adapter home.** URML repo (`reference/drone-runtime/MavsdkAdapter`), MAVSDK-maintained `mavlink/mavsdk-urml-bridge`, or both?
6. **Conformance listing.** Would the MAVSDK maintainers consider a README link to URML's compatible-runtimes registry once a working adapter ships?
7. **Anything else.**

## Implementation note

RFC-0198 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`mavlink/MAVSDK` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (BSD-3-Clause, 881 stars, Issues enabled, last commit 2026-05-26, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (multiple Spec-RFC prerequisites, plugin-set declaration flexibility, abstraction-overhead).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Linux Foundation Dronecode (foundation-direct); default policy passes.
- [x] CLAUDE.md compliance check passed.
