---
rfc: 0031
title: SCHUNK integration — request for comment from SCHUNK-SE-Co-KG maintainers
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

# RFC-0031: SCHUNK integration — request for comment from SCHUNK-SE-Co-KG maintainers

## Summary

URML ships a brand-named SCHUNK manifest (`schunk_mpg_cell.yaml`) and conformance fixture (`industrial/17_schunk_gripper_positive.yaml`) covering SCHUNK's pneumatic gripper line via the existing v0.1 capability-manifest `Gripper` schema. This RFC documents the URML manifest mapping for SCHUNK's gripper product line and **requests review and feedback from the SCHUNK-SE-Co-KG GitHub maintainers** on the mapping's correctness and on whether SCHUNK would consider becoming a conformance-listed component vendor per [RFC-0007](0007-manufacturer-go-to-market.md). No spec change.

This is the first **parts-vendor** RFC in the Move #1 lighthouse program. Parts vendors differ from arm/cobot vendors in that they are components that URML does not control directly — they are declared in the manifest and selected/operated by whichever arm adapter drives the cell. The credibility lead-in is therefore "we shipped a URML reference manifest for your product" rather than "we shipped an adapter that drives your product."

## Motivation

SCHUNK is the global leader in industrial gripping technology — over 11,000 standard end-of-arm tools across pneumatic, electric, vacuum, and magnetic gripping. SCHUNK is a UR+, ABB, KUKA, FANUC ecosystem-listed partner, and an integration target for every URML lighthouse arm RFC (0023–0030). A URML mapping RFC framed as request for comment from SCHUNK opens a credible standards-collaboration channel both directly and through the arm ecosystems SCHUNK already partners with.

The `SCHUNK-SE-Co-KG/schunk_mechatronic_gripper` repo is **vendor-direct**, with recent commits (May 2026) and Issues open — the highest-quality public engagement venue among the lighthouse parts vendors.

## Detailed design

Descriptive of an existing URML manifest fixture plus a feedback ask. No spec text changes.

### URML v0.1 capability-manifest mapping for SCHUNK grippers

URML's manifest schema (`reference/validator/src/urml_validator/schemas/manifest.py`) defines `Gripper` with the following relevant fields:

| URML field | Type | Maps to SCHUNK product attribute |
|---|---|---|
| `name` | `Identifier` | A deployment-chosen handle (e.g. `mpg_plus_25`, `egp_40_n_n_b`) |
| `kind` | enum `{pneumatic, servo_electric, vacuum, magnetic, compliant}` | SCHUNK's product family: MPG/MPP (pneumatic), EGP/EGK/EGN (servo_electric), SVH (compliant five-finger), CMM (electric multi-finger) |
| `force_min_n` / `force_max_n` | float | SCHUNK's published gripping-force range |
| `accepted_classes` | list of object class identifiers | Application-side classification — declares which object classes the gripper is sized for |
| `movable` | bool | Always `true` for SCHUNK grippers (they are wrist-mounted, not fixed) |

The shipping `schunk_mpg_cell.yaml` fixture exercises an MPG-plus pneumatic gripper on a generic industrial cell, with `vendor: schunk` in the provenance block. Germany (DE) is allied; the bundled US-federal default policy ACCEPTS the manifest with no flagging.

### What URML v0.1 *does not yet* express for SCHUNK grippers

The v0.1 `Gripper` schema is intentionally minimal. The following SCHUNK capabilities are **not currently expressible** in the manifest:

1. **Parametric grip force during motion.** SCHUNK's electric grippers (EGP, EGK) expose force-curve control during the close stroke; URML v0.1 captures only `force_min_n` / `force_max_n` envelope. This is a known SPEC-GAPS item for parametric impedance.
2. **Tactile / force feedback channels.** SCHUNK's smart electric grippers (e.g. EGI / EGP-C series) publish tactile data. URML v0.1 has no `Gripper.sensors[]` sub-block; tactile data would route through a top-level `Sensor`.
3. **Multi-finger five-DOF kinematics.** The SCHUNK SVH (servo-electric five-finger hand) has 9 actuators across 5 fingers. URML v0.1's `Gripper` is one-handle; SVH-style multi-finger manipulation is a candidate area for a future RFC (cross-references [RFC-0010](0010-whole-body-bimanual-manipulation.md) on whole-body / bimanual manipulation).
4. **Tool-change interface compatibility.** SCHUNK ATC (Auto Tool Changer) and the gripper-on-coupling interface have specific compatibility constraints (force, payload, electrical) that URML's manifest does not encode beyond `force_max_n`.

These are not bugs — they are intentional v0.1 boundaries documented for SCHUNK's review. SCHUNK feedback could promote any of them to a future RFC.

### Compatibility notes

- **Vendor org.** `SCHUNK-SE-Co-KG/schunk_mechatronic_gripper` is the active GitHub org as of 2026-05-22 (the SE & Co. KG legal-form reflects SCHUNK's 2024 corporate reorganization). Older SCHUNK GitHub presences (`SCHUNK-Carbon-Technology`, individual personal forks) are not authoritative.
- **Origin.** SCHUNK SE & Co. KG, Lauffen am Neckar, Germany; passes the US-federal default policy ([RFC-0004](0004-compliance-policy.md)) without flagging.
- **UR+ / ABB / KUKA / FANUC ecosystem.** SCHUNK ships UR+ / RobotApps / KUKA.connect / FANUC zDT-integrated configurations for the EGP, EGK, EGN, ATC-DGN, MPC, MPZ product families. URML's manifest captures the URML-relevant subset.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `schunk_mpg_cell.yaml` + `conformance/fixtures/industrial/17_schunk_gripper_positive.yaml` already shipping from Track C.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **No adapter to "show".** Unlike arm/cobot vendors where URML ships a driving adapter, parts vendors are declared in the manifest. The warm-touch artifact is the manifest + conformance fixture, not a runtime — slightly less impressive at first glance, more accurate to what URML actually does for components.
- **v0.1 gaps explicitly listed.** Listing the four expressibility gaps could be read as "URML can't fully describe SCHUNK products." More accurate framing: URML's v0.1 boundary is small by design; the gaps are RFC candidates, not bugs.

## Alternatives considered

1. **Defer parts RFCs until v0.2.** Rejected: SCHUNK is part of the lighthouse Tier-1 set; the manifest is shipping; the feedback ask makes sense now.
2. **Combine all 6 lighthouse parts RFCs (SCHUNK + Ouster + SICK + Festo + Zivid + Hokuyo) into one omnibus.** Rejected: per-vendor RFCs remain individually citable; each vendor has a distinct schema-mapping conversation.
3. **Wait for a SCHUNK-direct ROS 2 driver to land.** Rejected: components are declared, not driven, in URML — a driver is not on the critical path.

## Prior art

- `SCHUNK-SE-Co-KG/schunk_mechatronic_gripper` — the upstream driver repo.
- SCHUNK's product catalogues (MPG / EGP / EGK / SVH / ATC / etc.).
- UR+ ecosystem integrations.
- RFC-0007 (manufacturer go-to-market) — the underlying market wedge.
- RFC-0023..0030 for the per-vendor RFC pattern (arm-vendor variant).

## Unresolved questions

Provisional pending SCHUNK-SE-Co-KG maintainer feedback:

1. **Parametric grip force.** Should URML's manifest schema add a force-curve / impedance sub-block to `Gripper`? Is this URML's place or the arm-adapter's deployment config?
2. **Tactile feedback.** Should `Gripper.sensors[]` be added, or is the existing top-level `Sensor` declaration the right place for tactile data?
3. **SVH multi-finger hand.** Should URML v0.1's `Gripper` be extended to multi-DOF five-finger hands, or is this scope better left for [RFC-0010](0010-whole-body-bimanual-manipulation.md)?
4. **ATC / tool-change.** Should ATC compatibility be modelled in the manifest (a new `tool_change[]` capability) or stay deployment-side?
5. **Conformance listing.** Would SCHUNK consider listing in the URML compatible-runtimes registry / manufacturer directory per [RFC-0007](0007-manufacturer-go-to-market.md)?

## Implementation note

RFC-0031 ships as a single RFC document PR. No code / manifest / fixture change (Track C covered both). Draft state.

## Requested feedback (from SCHUNK-SE-Co-KG maintainers)

1. **Correctness of the schema mapping.**
2. **The four v0.1 gaps** (parametric force, tactile, multi-finger, ATC) — which (if any) should be promoted to URML RFCs?
3. **Conformance / manufacturer-directory listing interest per [RFC-0007](0007-manufacturer-go-to-market.md).**
4. **UR+ / ABB / KUKA / FANUC ecosystem co-marketing potential** — is URML alignment something SCHUNK could see value in for cross-ecosystem positioning?
5. **Anything else.**

## How to respond

URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Or open an Issue on `SCHUNK-SE-Co-KG/schunk_mechatronic_gripper`. Private channel via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is the first parts-vendor RFC).
- [x] Motivation grounded in concrete vendor relationship + cross-ecosystem positioning.
- [x] Detailed design names every affected component (Track C manifest / fixture; existing v0.1 schema).
- [x] At least one alternative considered (three are).
- [x] Drawbacks are real ("no adapter to show"; gaps could be misread).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explains how this lands.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant.
