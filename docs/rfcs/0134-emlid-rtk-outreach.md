---
rfc: 0134
title: Emlid (Reach RTK GNSS) integration, request for comment from Emlid maintainers
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

# RFC-0134: Emlid (Reach RTK GNSS) integration, request for comment from Emlid maintainers

## Summary

URML does not yet ship an Emlid manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for Emlid's Reach RTK GNSS receivers (Reach RS3, Reach M2, Reach RX) over the [`emlid`](https://github.com/emlid) GitHub organization (43 public repos including Navio2, ntripbrowser), and **requests review and feedback from the Emlid maintainers**. No spec change.

This RFC complements [RFC-0119 (Septentrio)](0119-septentrio-outreach.md), [RFC-0120 (NovAtel / Hexagon)](0120-novatel-hexagon-outreach.md), and [RFC-0133 (u-blox)](0133-ublox-gnss-outreach.md). Emlid is the low-cost multi-band RTK lineage; the four together cover the GNSS slice of Move-10.

## Motivation

Emlid Tech Kft. (Budapest, Hungary) makes the Reach line of low-cost multi-band RTK GNSS receivers that powered a generation of UAS surveyors, agriculture-precision-tooling integrators, and academic robotics labs. Reach M2 and Reach RX are common in the cm-class positioning slot under $1000 USD. The vendor org has 43 public repos covering `ntripbrowser` (BSD-3-Clause), `Navio2` (BSD-3-Clause flight-controller add-on for Raspberry Pi), and several supporting tools.

**Provenance note.** Emlid was originally Hong Kong-registered (Emlid Ltd., HK) when founded by Russian-diaspora engineers. The active operating entity in 2026 is **Emlid Tech Kft. (Hungary, HU)** — passes US-federal default policy on current entity. The HK registration history is documented here so US-federal-procurement consumers can make their own call; the URML default policy assessment is on the current Emlid Tech Kft. (HU) status.

Reach firmware (ReachView3 on the Reach RS3 / RX) is closed binary; URML's adapter pattern reasons about NMEA / UBX standard interfaces from the receiver, not the closed firmware internals.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `emlid_reach_cell.yaml` fixture)

`Sensor` block, multi-measurement GNSS:

| URML field | Maps to Emlid product attribute |
|---|---|
| `name: gnss` (Sensor) | Emlid Reach RS3 / M2 / RX RTK GNSS receiver |
| `measurement_type: custom` (gnss_position) | Position fix (lat / lon / alt) — NMEA / UBX output |
| `measurement_type: custom` (gnss_velocity) | Velocity vector — NMEA output |
| `measurement_type: custom` (gnss_quality) | Fix-type + RTK status |

### What URML v0.1 does not yet express for Emlid

1. **GNSS-class measurement_types** — same gap shared with RFC-0119 / RFC-0120 / RFC-0133; one Spec RFC covers all.
2. **NTRIP correction-source declaration.** Emlid Reach pairs heavily with NTRIP for caster-based corrections; URML's manifest cannot today declare the NTRIP correction-source pattern.
3. **Closed Reach firmware declaration.** ReachView3 is closed binary; URML's adapter reasons about the standard-interface output, not the firmware. Same closed-core / open-wrapper pattern as RFC-0073 / RFC-0127 / RFC-0129.

### Compatibility notes

- **Vendor org.** [`emlid`](https://github.com/emlid) — 43 public repos.
- **Notable repos.** `ntripbrowser` (BSD-3-Clause, 32 stars, last 2025-07-21 stale ~10 mo), `Navio2` (BSD-3-Clause flight-controller).
- **Origin.** Emlid Tech Kft., Budapest, **Hungary** (HU) — current operating entity. Originally founded as Emlid Ltd. HK; HK history flagged for US-federal-procurement consumers.
- **License fit.** BSD-3-Clause on the open-source surface (clean fit); Reach firmware closed.
- **Maintainer signal.** Vendor email through emlid.com; ntripbrowser stale ~10 months but vendor org alive on slower cadence.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; GNSS-class Spec RFC queued in parallel (shared with RFC-0119 / RFC-0120 / RFC-0133).
- Reference runtime: future `reference/sensor-runtime/EmlidReachAdapter` is a candidate; adapter targets NMEA / UBX output not firmware internals.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **HK-registration history.** Current HU-domiciled entity passes default policy. US-federal-procurement consumers should make their own call. This RFC flags the history honestly without making the policy judgment for downstream operators.
- **Closed Reach firmware.** Adapter pattern reasons about standard-interface output, not firmware internals.
- **Slower-cadence vendor GitHub activity.** `ntripbrowser` last commit 2025-07-21 (~10 mo from cutoff); vendor likely engages off-GitHub primarily.
- **GNSS-class Spec RFC prerequisite.** Same gap as RFC-0119 / RFC-0120 / RFC-0133.

## Alternatives considered

1. **Defer Emlid until HK-registration history is fully out of public memory.** Rejected. The HK history is a fact; honest disclosure beats deferral. Current entity passes default policy.
2. **Bundle Emlid + u-blox into one low-cost-RTK RFC.** Rejected. Per-vendor RFCs let conversation thread per vendor.
3. **Cross-citation only.** Considered. Vendor presence on GitHub is real, BSD-3-Clause; adapter is the natural shape.

## Prior art

- [`emlid`](https://github.com/emlid) — the upstream organization.
- [RFC-0119 (Septentrio)](0119-septentrio-outreach.md) + [RFC-0120 (NovAtel / Hexagon)](0120-novatel-hexagon-outreach.md) + [RFC-0133 (u-blox)](0133-ublox-gnss-outreach.md) — sibling GNSS / RTK RFCs sharing the GNSS-class Spec-RFC gap.

## Unresolved questions

For the Emlid maintainers:

1. **Engagement-channel preference.** GitHub Issue on `emlid/ntripbrowser` or another active repo, Emlid forum, or vendor support email?
2. **GitHub roadmap.** Is the vendor org's GitHub activity expected to remain at its current cadence, or planned for revival?
3. **GNSS-class manifest fields.** Same questions as RFC-0119 / RFC-0120 / RFC-0133. Manifest-field expectations from Emlid's perspective (NMEA-default vs UBX-default output, RTK-status granularity)?
4. **NTRIP correction-source declaration.** Should URML's manifest declare the NTRIP caster pattern (URL, mountpoint, auth-method-class)?
5. **Adapter home.** URML repo (`reference/sensor-runtime/`), Emlid-maintained `emlid/emlid-urml` repo, or cross-citation only?
6. **Conformance listing.** Would Emlid consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
7. **Anything else.**

## Implementation note

RFC-0134 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move10.yaml`](../../examples/lighthouses/outreach-move10.yaml).

## How to respond

`emlid/ntripbrowser` has Issues enabled. URML's planned channel: open a single Issue there labelled `enhancement` or `question`, pointing to this RFC, with a request for redirect if vendor maintainers prefer a different repo.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-27 (43-repo org, BSD-3-Clause on open surface, ntripbrowser last commit 2025-07-21 slower cadence).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (HK-registration history honestly flagged, closed firmware, slower vendor cadence, GNSS-class Spec-RFC prerequisite).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Emlid Tech Kft. (HU current entity); default policy passes on current entity. HK-history flag included for operator decision.
- [x] CLAUDE.md compliance check passed.
