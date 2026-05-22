---
rfc: 0034
title: Festo integration — request for comment from Festo-se maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-22
updated: 2026-05-22
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

# RFC-0034: Festo integration — request for comment from Festo-se maintainers

## Summary

URML ships a brand-named Festo manifest (`festo_dhep_cell.yaml`) and conformance fixture (`industrial/27_festo_dhep_cell_positive.yaml`) covering Festo's servo-electric and pneumatic gripper product lines (DHEP, DHPS, HGPL, etc.) via the existing v0.1 `Gripper` schema. This RFC documents the URML manifest mapping and **requests review and feedback from the Festo-se GitHub maintainers**. No spec change.

## Motivation

Festo is the global leader in industrial pneumatic and electric automation, with a particularly strong educational/training arm (Festo Didactic) that aligns with [RFC-0011](0011-educational-profile.md) (educational profile). Their gripper line plus the broader pneumatics / valves / drives ecosystem represents a different parts-vendor profile from SCHUNK (gripping-only) — Festo is gripping plus the *automation infrastructure that drives the gripper*.

The `Festo-se/phand-ros` repo is **vendor-direct**, active, with Issues open.

## Detailed design

Descriptive of an existing URML manifest fixture plus a feedback ask. No spec text changes.

### URML v0.1 capability-manifest mapping for Festo grippers

| URML field | Type | Maps to Festo product attribute |
|---|---|---|
| `name` | `Identifier` | A deployment-chosen handle (e.g. `dhep_40`, `hgpl_25_pneumatic`) |
| `kind` | enum | DHEP / DHPS / HGPL: `servo_electric` or `pneumatic` per series |
| `force_min_n` / `force_max_n` | float | Festo's published gripping-force range |
| `accepted_classes` | list | Application-side classification |

The shipping `festo_dhep_cell.yaml` fixture declares a DHEP servo-electric gripper with `vendor: festo` (DE origin); the bundled US-federal default policy ACCEPTS with no flagging.

### What URML v0.1 *does not yet* express for Festo

1. **Pneumatic infrastructure declaration.** Festo's grippers are part of a broader pneumatic system (valve terminals, regulators, accumulators). URML's manifest doesn't model the pneumatic infrastructure.
2. **CPX / Festo Motion Terminal integration.** Festo's smart-pneumatics platforms (CPX-E, VTEM Motion Terminal) expose programmable motion via piezo valves. URML has no specific manifest for these.
3. **Educational kit alignment.** Festo Didactic ships robotics training kits widely deployed in vocational and university programs. URML's [RFC-0011](0011-educational-profile.md) educational profile could potentially declare a "festo_didactic" platform alongside VEX V5 / LEGO SPIKE / Thymio.
4. **Parametric grip force during motion** (same gap as SCHUNK RFC-0031).
5. **Compressed-air consumption / energy efficiency telemetry.** Industry-standard sustainability concern; URML doesn't model it.

### Compatibility notes

- **Vendor org.** `Festo-se` is the active GitHub org reflecting the 2023 SE & Co. KGaA corporate form.
- **Origin.** Festo SE & Co. KGaA, Esslingen am Neckar, Germany; passes the US-federal default policy without flagging.
- **Educational tie.** Festo Didactic's training-kit alignment with [RFC-0011](0011-educational-profile.md) makes Festo a unique parts-vendor with both industrial and educational lighthouse value.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `festo_dhep_cell.yaml` + `conformance/fixtures/industrial/27_festo_dhep_cell_positive.yaml` already shipping from Track I-C.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Pneumatic infrastructure is broader than URML v0.1.** Festo's most distinctive offering (smart pneumatics, valve terminals, CPX platforms) is genuinely outside URML's v0.1 scope. The RFC documents the gap honestly.

## Alternatives considered

1. **Combine with SCHUNK RFC into a single grippers RFC.** Rejected: Festo's pneumatic-infrastructure + educational dimensions distinguish it from SCHUNK; per-vendor framing keeps the conversations distinct.
2. **Wait for a future "pneumatic infrastructure" RFC.** Rejected: Festo's review is what would inform such an RFC.

## Prior art

- `Festo-se/phand-ros` — the upstream driver.
- Festo's product catalogues (DHEP / DHPS / HGPL / CPX / VTEM Motion Terminal).
- Festo Didactic training-kit documentation.
- RFC-0011 (educational profile) for the educational tie.
- RFC-0023..0033 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending Festo-se maintainer feedback:

1. **Pneumatic infrastructure scope.** Should URML model valve terminals, regulators, CPX platforms, or stay deployment-side?
2. **Festo Didactic platform.** Should the educational profile add `festo_didactic` alongside VEX V5 / LEGO SPIKE / Thymio?
3. **Smart pneumatics.** Should URML's manifest support VTEM Motion Terminal / CPX-E programmability?
4. **Energy/efficiency telemetry.** Should the manifest carry compressed-air consumption / energy metrics?
5. **Parametric grip force** (same as SCHUNK RFC-0031).
6. **Conformance / directory listing per [RFC-0007](0007-manufacturer-go-to-market.md).**

## Implementation note

RFC-0034 ships as a single RFC document PR. No code / manifest / fixture change. Draft state.

## Requested feedback (from Festo-se maintainers)

1. **Correctness of the mapping description.**
2. **The five v0.1 gaps.**
3. **Festo Didactic + RFC-0011 educational profile alignment.**
4. **Conformance / manufacturer-directory listing per [RFC-0007](0007-manufacturer-go-to-market.md).**
5. **Anything else.**

## How to respond

URML public Discussions:

> https://github.com/URML-MARS/URML/discussions

Or Issue on `Festo-se/phand-ros`. Private via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in concrete vendor relationship + educational-tie distinctiveness.
- [x] Detailed design names every affected component (Track I-C manifest / fixture).
- [x] At least one alternative considered (two are).
- [x] Drawbacks are real.
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md); compliant.
