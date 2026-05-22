---
rfc: 0033
title: SICK integration — request for comment from SICKAG/sick_safetyscanners2 maintainers
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

# RFC-0033: SICK integration — request for comment from SICKAG/sick_safetyscanners2 maintainers

## Summary

URML ships a brand-named SICK manifest (`sick_safety_lidar_cell.yaml`) and conformance fixture (`industrial/23_sick_safety_lidar_positive.yaml`) covering SICK's safety lidar product line (microScan3 / nanoScan3 / TiM safety series). This RFC documents the URML manifest mapping and **requests review and feedback from the SICKAG GitHub maintainers**. No spec change.

## Motivation

SICK is the global leader in industrial safety sensing — particularly safety-rated lidars (Type 3 / SIL2 / PL d) deployed in factory cells, AMR perimeters, and personnel-protection zones. Safety sensing is a *first-class* URML concern (Pass 3 safety-envelope validation lives in the validator's people-occupancy-zone checks), so SICK is asymmetrically valuable: their feedback could directly inform what URML's safety-envelope schema needs.

The `SICKAG/sick_safetyscanners2` repo is **vendor-direct**, active, with Issues open. SICK also publishes `SICKAG/scan_tools` and per-product driver repos under the same org.

## Detailed design

Descriptive of an existing URML manifest fixture plus a feedback ask. No spec text changes.

### URML v0.1 capability-manifest mapping for SICK safety lidars

URML's manifest schema declares safety lidars under the `Sensor` block:

| URML field | Type | Maps to SICK product attribute |
|---|---|---|
| `name` | `Identifier` | A deployment-chosen handle (e.g. `microscan3`, `nanoscan3`) |
| `measurement_type` | enum incl. `distance` | All SICK safety scanners report ranged distance for personnel-occupancy detection |
| `range_min` / `range_max` | float | SICK's scan field (microScan3: 0.05m–5.5m; nanoScan3: 0.05m–3m) |
| `units` | string | `m` |

URML's *safety envelope* layer (separate from `Sensor`) declares zones the validator checks via Pass 3 (occupancy-zone people exclusion). The SICK lidar provides the runtime evidence that those zones are clear; URML's manifest declares the lidar's existence, not the zone-clearance logic itself (that's the safety controller's job).

The shipping `sick_safety_lidar_cell.yaml` fixture declares a microScan3 on an industrial cell with `vendor: sick` (DE origin); the bundled US-federal default policy ACCEPTS with no flagging.

### What URML v0.1 *does not yet* express for SICK safety lidars

1. **Safety integrity level (SIL / PL).** SICK's safety scanners are rated SIL2 / PL d / Type 3 (per IEC 61496 / EN ISO 13849). URML's `Sensor` doesn't capture safety ratings. URML's *safety envelope* is application-level, not sensor-level.
2. **Safety-zone configuration uplink.** SICK scanners run with on-device zone configurations loaded via SICK Safety Designer. URML has no manifest-level link to zone configurations.
3. **Failure / fault telemetry.** SICK safety scanners publish health / fault status via EtherNet/IP, EFI-pro, or OSSDs. URML doesn't model failure-mode reporting.
4. **Mute / override / EDM (External Device Monitoring).** Standard safety-system features absent from URML v0.1.
5. **EtherCAT FSoE / PROFIsafe / OPC UA Safety integration.** Industry-standard safety fieldbus protocols; URML's [RFC-0019](0019-autosar-adaptive-substrate.md) covers AUTOSAR's `ara::com` but doesn't extend to fieldbus safety layers.

These are not bugs — they reflect URML's v0.1 boundary where safety is application-level (envelope-validated by Pass 3) and sensor-level safety integrity is a deployment / certification concern. SICK's feedback could promote any of them to a future RFC.

### Compatibility notes

- **Vendor org.** `SICKAG/sick_safetyscanners2` (current), `SICKAG/sick_scan_xd` (general non-safety lidar), `SICKAG/scan_tools` (utilities).
- **Origin.** SICK AG, Waldkirch, Germany; passes the US-federal default policy without flagging.
- **Safety-relevant primitive.** URML's Pass 3 (safety envelope) is the most safety-relevant pass; SICK lidars are the evidence source that occupancy zones are clear. The dataflow is: SICK lidar → safety controller (SICK Flexi Safe / vendor-specific PLC) → application emergency-stop → URML's `declared_events.emergency_stop` event.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `sick_safety_lidar_cell.yaml` + `conformance/fixtures/industrial/23_sick_safety_lidar_positive.yaml` already shipping from Track C.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Safety is delicate.** URML deliberately does not encode SIL ratings or zone-clearance logic — that's the safety controller's job, certified separately. Documenting the boundary clearly is important; an RFC could be misread as URML claiming safety certification, which it does not.
- **Five v0.1 gaps.** Safety domains have more standardized vocabulary than most areas; the gaps reflect URML's intentional v0.1 boundary, not an oversight.

## Alternatives considered

1. **Defer until URML adds first-class safety-rating fields.** Rejected: SICK is part of the lighthouse Tier-1 set; the manifest is shipping; the feedback ask makes sense now and SICK's input could shape any future safety-rating RFC.
2. **Combine with safety-system RFC scope.** Rejected: no safety-system RFC exists yet; SICK's review could be what informs one.

## Prior art

- `SICKAG/sick_safetyscanners2` — the upstream driver.
- `SICKAG/scan_tools`, `SICKAG/sick_scan_xd` — non-safety lidar drivers (sister repos).
- IEC 61496 (electro-sensitive protective equipment) and EN ISO 13849 (machinery safety).
- RFC-0023..0032 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending SICKAG/sick_safetyscanners2 maintainer feedback:

1. **SIL / PL rating fields.** Should URML's `Sensor` block carry `safety_rating: { sil: 2, pl: d }` for safety sensors? Or should this stay deployment-side / certification-side?
2. **Safety-zone configuration links.** Should the URML manifest link to safety-zone configuration files (SICK Safety Designer projects)?
3. **Failure / fault telemetry.** Should URML model sensor health / fault reporting? If so, in `Sensor.telemetry[]` or top-level `declared_events`?
4. **Fieldbus safety integration.** Should URML have safety-fieldbus manifest fields (FSoE / PROFIsafe / OPC UA Safety)?
5. **Boundary clarity.** Does SICK agree with URML's posture that *application-level safety envelope* (Pass 3) is in scope and *sensor-level safety integrity / certification* is out of scope?
6. **Conformance / directory listing per [RFC-0007](0007-manufacturer-go-to-market.md).**

## Implementation note

RFC-0033 ships as a single RFC document PR. No code / manifest / fixture change (Track C covered both). Draft state.

## Requested feedback (from SICKAG maintainers)

1. **Correctness of the mapping description.**
2. **The five v0.1 gaps** — which should be promoted to URML RFCs?
3. **Safety-boundary clarity** — does SICK agree with URML's application-vs-sensor-certification split?
4. **Conformance / manufacturer-directory listing interest.**
5. **Anything else.**

## How to respond

URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Or open an Issue on `SICKAG/sick_safetyscanners2`. Private channel via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in concrete safety-domain relationship + first-class URML safety primitive.
- [x] Detailed design names every affected component (Track C manifest / fixture).
- [x] At least one alternative considered (two are).
- [x] Drawbacks are real (safety domain delicacy; risk of misreading the RFC as a safety claim).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant.
