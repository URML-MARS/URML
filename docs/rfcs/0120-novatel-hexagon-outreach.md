---
rfc: 0120
title: NovAtel / Hexagon (OEM7 / SPAN GNSS + INS) integration, request for comment from novatel maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-27
updated: 2026-05-27
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

# RFC-0120: NovAtel / Hexagon (OEM7 / SPAN GNSS + INS) integration, request for comment from novatel maintainers

## Summary

URML does not yet ship a NovAtel manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for NovAtel's OEM7 GNSS receivers and SPAN-class GNSS+INS combined systems over [`novatel/novatel_oem7_driver`](https://github.com/novatel/novatel_oem7_driver) (MIT, dual ROS 1 / ROS 2 driver with Discussions enabled), and **requests review and feedback from the NovAtel maintainers**. No spec change.

## Motivation

`novatel/novatel_oem7_driver` is the cleanest GNSS+INS Tier-A vendor surface in URML's Move #10 verification: MIT-licensed, 120 stars, 6 open issues, **Discussions enabled** (rare among industrial vendors and an explicit invitation to dialogue), last commit ~2 months from verification. Vendor org Hexagon | NovAtel, Calgary CA (Hexagon parent SE). Both NATO-allied; US-federal default policy passes cleanly.

NovAtel's SPAN line is structurally distinct from the other Move-10 GNSS vendors because it integrates the IMU + GNSS in one product, emitting fused pose directly. This is the same INS-fusion declaration question RFC-0117 (MicroStrain) and RFC-0118 (SBG) surface, plus the GNSS-class schema questions RFC-0119 (Septentrio) surfaces, in one product family. Engaging the maintainer about the combined surface helps the Spec RFCs that follow handle both lanes coherently.

## Detailed design

Descriptive of a planned manifest mapping plus a feedback ask. No spec text changes in this RFC.

### URML v0.1 capability-manifest mapping (planned `novatel_oem7_cell.yaml` fixture)

`Sensor` block:

| URML field | Maps to NovAtel product attribute |
|---|---|
| `name: gnss` (Sensor) | OEM7 receiver (OEM719, PwrPak7, etc.) |
| `measurement_type: custom` (gnss_position) | Latitude / longitude / altitude |
| `measurement_type: custom` (gnss_heading) | Dual-antenna heading where present (ALIGN) |
| `measurement_type: custom` (rtk_status) | RTK fix state |
| `name: ins` (Sensor; SPAN deployments only) | SPAN tightly-coupled GNSS+INS pose |
| `measurement_type: custom` (ins_pose) | Fused position + orientation from SPAN |
| `units` | `degrees` (lat/lon/heading), `m` (alt/position), `rad` (orientation) |

### What URML v0.1 does not yet express for NovAtel

The schema gaps are the union of the GNSS-class gaps (same as RFC-0119 Septentrio) and the INS-class gaps (same as RFC-0117 MicroStrain, RFC-0118 SBG):

1. **Constellation declaration** (GNSS).
2. **Frequency-band declaration** (GNSS).
3. **RTK / NTRIP-correction declaration** (GNSS).
4. **Dual-antenna heading / ALIGN** (GNSS — NovAtel-specific term).
5. **SPAN tight-coupling declaration** (INS) — "this device emits GNSS+INS fused pose, not just GNSS position alongside IMU."
6. **Multi-mode accuracy declaration** (per Zivid RFC-0035 precedent: no single-scalar accuracy).

### Compatibility notes

- **Vendor org.** [`novatel/novatel_oem7_driver`](https://github.com/novatel/novatel_oem7_driver), 6 public vendor repos.
- **Origin.** Hexagon | NovAtel, Calgary CA; Hexagon parent SE. Passes US-federal default policy (CA + SE both NATO allied).
- **License fit.** MIT; cleanly composes with URML's Apache-2.0 stance.
- **Surface signal.** Discussions enabled is rare among industrial GNSS/INS vendors — an explicit dialogue-ready posture URML's outreach can engage with.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC.
- Reference runtime: a future `reference/perception-runtime/` or `reference/sensor-runtime/` package with `NovatelOem7Adapter` (covering OEM7) and potentially a separate `NovatelSpanAdapter` for SPAN tightly-coupled deployments. Or one adapter parameterized by SPAN-on / SPAN-off. Vendor preference matters here.
- Conformance: a future `novatel_oem7_cell.yaml` manifest fixture + positive conformance case after the GNSS-class + INS-fusion Spec RFCs clarify the schema.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.** No adapter code; engagement-driven per RFC-0073 precedent.
- **Six schema-extension gaps surfaced.** The union of GNSS-class + INS-class gaps; queued as parallel Spec RFCs, not closed here.
- **SPAN tight-coupling is harder to model than loose-coupled INS.** Other vendors (SBG Quanta-N, MicroStrain GQ7) emit fused pose; SPAN's coupling is at a different layer and the manifest declaration question is more nuanced.

## Alternatives considered

1. **Combine NovAtel + Septentrio into one GNSS-vendor RFC.** Rejected. Per-vendor RFCs let the conversation thread per vendor; NovAtel and Septentrio have different SPAN-vs-no-INS posture worth surfacing separately.
2. **Wait for the GNSS-class + INS-class Spec RFCs.** Rejected. NovAtel's feedback informs both.
3. **One adapter spanning OEM7 + SPAN.** Considered, leaves the decision to NovAtel maintainers (Question 4 below).

## Prior art

- [`novatel/novatel_oem7_driver`](https://github.com/novatel/novatel_oem7_driver) — the upstream driver.
- [RFC-0119 (Septentrio)](0119-septentrio-outreach.md) — parallel GNSS RFC, BE origin.
- [RFC-0117 (MicroStrain by HBK)](0117-microstrain-hbk-outreach.md) — parallel IMU/INS RFC.
- [RFC-0118 (SBG Systems)](0118-sbg-systems-outreach.md) — parallel IMU/INS RFC, FR origin.
- [RFC-0035 (Zivid)](0035-zivid-integration.md) — "multi-dimensional accuracy, no single scalar" precedent.

## Unresolved questions

For the `novatel/novatel_oem7_driver` maintainers:

1. **Constellation declaration.** Should URML's manifest declare which constellations (GPS / GLONASS / Galileo / BeiDou / QZSS / SBAS) a deployment uses? Partly a policy-fit question (BeiDou + US-federal), partly a capability declaration.
2. **Frequency-band declaration.** L1 / L2 / L5 multi-band — manifest declaration or runtime parameter?
3. **SPAN tight-coupling declaration.** SPAN emits GNSS+INS fused pose at a tightly-coupled layer. Is "this device emits SPAN-class fused pose" a manifest declaration URML should carry, vs the loose-coupling INS declaration in RFC-0117 / RFC-0118?
4. **Adapter shape.** One `NovatelOem7Adapter` covering OEM7 + SPAN parameterized by SPAN-on/off, or two adapters (`NovatelOem7Adapter` + `NovatelSpanAdapter`)? Your maintenance preference matters more than URML's instinct.
5. **ALIGN dual-antenna heading.** How should URML's manifest declare antenna topology for heading?
6. **Adapter home.** When the URML-side adapter ships, should it live in URML's `reference/perception-runtime/`, in a separately-maintained `novatel/novatel-urml` repo, or external in URML-MARS/URML only? URML's default assumption is the URML repo unless invited otherwise.
7. **Conformance listing.** Would the NovAtel / Hexagon team consider a README or Discussions link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0120 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## Requested feedback (from NovAtel maintainers)

Items 1–8 from Unresolved questions above.

## How to respond

`novatel/novatel_oem7_driver` has both Issues and Discussions enabled. URML's planned channel: open a single Discussion on `novatel/novatel_oem7_driver` (Discussions on means there's a dialogue surface ready), pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary, Motivation, and Detailed design grounded in verified `novatel/novatel_oem7_driver` surface (MIT, 120 stars, 6 open issues, Issues + Discussions both enabled, last commit 2026-03-18).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, six schema gaps, SPAN-coupling subtlety).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change of any kind.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-27.
- [x] Provenance: NovAtel CA / Hexagon SE; default policy passes without flagging.
- [x] CLAUDE.md compliance check passed.
