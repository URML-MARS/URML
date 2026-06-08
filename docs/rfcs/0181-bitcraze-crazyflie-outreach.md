---
rfc: 0181
title: Bitcraze Crazyflie (research nano-quadcopter platform) integration, request for comment from bitcraze maintainers
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

# RFC-0181: Bitcraze Crazyflie (research nano-quadcopter platform) integration, request for comment from bitcraze maintainers

## Summary

URML does not yet ship a Crazyflie manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest cross-citation for Bitcraze's Crazyflie nano-quadcopter platform over [`bitcraze/crazyflie-firmware`](https://github.com/bitcraze/crazyflie-firmware) (GPL-3.0), and **requests review and feedback from the bitcraze maintainers**. **GPL-3.0 — cross-citation framing** (URML's Apache-2.0 adapter pattern does not embed GPL-3.0 firmware; URML composes at the protocol / Crazyradio boundary). No spec change.

> **Maintainer-correction note (2026-06-08):** @ataffanel (Arnaud Taffanel,
> Bitcraze co-founder) corrected a license error and closed the thread.
> `crazyflie-lib-python` is **GPLv3, not Apache-2.0**, so the "Apache-2.0
> client-library boundary" argument used below is **withdrawn**. Both the
> firmware and the host library are GPL; URML's Apache-2.0 adapter composes at
> the **CRTP protocol / IPC boundary** (no code vendoring), not at an Apache-2.0
> client surface. Bitcraze will not host a bridge or add registry links on a
> proposal alone; the path forward is an **external URML-maintained adapter plus
> a working demo with tests and clear safety limits**, raised in the relevant
> **host-side** repository, not the firmware tracker. The "Apache-2.0 client"
> references below are superseded by this note.

## Motivation

Bitcraze AB (Sweden) makes the Crazyflie — the canonical open-source nano-quadcopter research platform. Used widely in swarm-robotics research, distributed-control experiments, and educational labs. Firmware + Python client + hardware all open-source under GPL-3.0 / Apache-2.0 mix. Repo at [`bitcraze/crazyflie-firmware`](https://github.com/bitcraze/crazyflie-firmware) (GPL-3.0, 1.5k stars, Issues enabled, last commit `2026-05-26` very active, **not archived**).

URML-fit angle: Crazyflie is the natural research-nano-quadcopter target for URML's drone profile (RFC-0008) + multirotor mobility class. The integration shape is host-side via the Bitcraze Python client (`crazyflie-lib-python`) — URML adapter speaks to the host library which speaks to the Crazyradio dongle which speaks to the swarm.

**GPL-3.0 on the firmware** is the cross-citation gate: URML's Apache-2.0 adapter pattern doesn't embed GPL-3.0 firmware. The right composition is at the protocol layer (CRTP — Crazy RealTime Protocol) and the Python client boundary, both of which are licensed compatibly for URML's adapter pattern.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `bitcraze_crazyflie_cell.yaml` fixture)

| URML field | Maps to Crazyflie attribute |
|---|---|
| `name` | Specific model (`crazyflie_2_1`, `crazyflie_bolt`, `crazyflie_2_1_brushless`) |
| `mobility.drive_type: multirotor` | Native v0.1 multirotor class (clean fit) |
| `mobility.payload_class: custom` (`nano_research`) | Sub-100g research nano-quadcopter class |
| `host_interface: custom` (`crazyradio_2_0` + `crtp_protocol`) | Crazyradio dongle + CRTP wireless protocol |
| `firmware_license: gpl_3_0` | URML manifest declares firmware-license boundary (cross-citation framing) |

### What URML v0.1 does not yet express for Crazyflie

1. **Nano-quadcopter payload-class declaration.** URML's `multirotor` mobility class doesn't today distinguish sub-100g nano-class from larger drones; relevant for safety-envelope defaults.
2. **CRTP protocol substrate declaration.** Crazyflie's CRTP wireless protocol is the integration boundary; URML's manifest cannot today declare protocol-class substrates at this layer.
3. **Firmware-license boundary declaration.** Cross-citation framing requires explicit manifest acknowledgement that the firmware is GPL-3.0 and URML's adapter composes at the host-side Apache-2.0 boundary; URML's manifest cannot today carry this.

### Compatibility notes

- **Vendor org.** [`bitcraze`](https://github.com/bitcraze) — Bitcraze AB, Sweden.
- **Flagship repo.** [`bitcraze/crazyflie-firmware`](https://github.com/bitcraze/crazyflie-firmware) — GPL-3.0, 1.5k stars, Issues enabled, last commit 2026-05-26 very active, **not archived**.
- **Companion repo** (GPLv3 host-side): `bitcraze/crazyflie-lib-python` — reached at the CRTP / IPC boundary, not vendored (corrected per the note above).
- **Origin.** Bitcraze AB, Malmö, Sweden. Passes US-federal default policy (NATO+EU).
- **License fit.** GPL-3.0 firmware and GPLv3 client library (`crazyflie-lib-python`); neither is Apache-2.0, so URML integrates at the CRTP / IPC boundary with no code vendoring.
- **Maintainer signal.** Very active surface; vendor-direct commercial entity.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; payload-class + CRTP-substrate + firmware-license-boundary Spec RFCs queued.
- Reference runtime: future `reference/drone-runtime/CrazyflieAdapter` is a candidate — composes with `crazyflie-lib-python` (GPLv3) at the CRTP / IPC boundary, no code vendoring; URML manifest declares the boundary.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **GPL-3.0 firmware** requires cross-citation framing; URML's adapter cannot embed firmware modifications.
- **Multiple Spec-RFC prerequisites** (nano-class payload, CRTP substrate, firmware-license-boundary declaration).
- **Crazyradio 2.0 dongle dependency** — URML's manifest needs to declare the host-side hardware dependency for radio bridging.

## Alternatives considered

1. **Skip Crazyflie as overlapping with sibling drone-OEM engagement.** Rejected. Crazyflie is research-nano specific; no overlap with industrial-drone vendors URML may engage later.
2. **Engage only at the `crazyflie-lib-python` layer (Apache-2.0).** Considered. The Python client is the URML-compatible boundary; this RFC engages the firmware repo too because the research community treats the firmware as the canonical engagement surface even though URML integrates at the host-side.
3. **Cross-citation only with no manifest mapping.** Considered. Tier B framing keeps cross-citation as the recommended posture while still presenting a manifest sketch for maintainer evaluation.

## Prior art

- [`bitcraze/crazyflie-firmware`](https://github.com/bitcraze/crazyflie-firmware) — the upstream firmware (GPL-3.0).
- [`bitcraze/crazyflie-lib-python`](https://github.com/bitcraze/crazyflie-lib-python) — Apache-2.0 host-side Python client (URML's integration boundary).
- [RFC-0008 (drone profile)](0008-drone-profile.md) — URML's drone profile that Crazyflie populates.
- [RFC-0009 (Layer-1 mobility specialization)](0009-layer1-mobility-specialization.md) — multirotor mobility class.

## Unresolved questions

For the bitcraze maintainers:

1. **Nano-quadcopter payload-class manifest fields.** URML's `multirotor` class doesn't today distinguish nano (sub-100g research) from larger. Manifest field expectations?
2. **CRTP protocol substrate declaration.** Should URML's manifest declare CRTP as the integration substrate, and at what granularity (protocol version, channel/band, throughput class)?
3. **Firmware-license-boundary declaration.** Should URML's manifest declare the GPL-3.0-firmware / Apache-2.0-client license boundary explicitly?
4. **Crazyradio dongle declaration.** Manifest field for the host-side radio dependency?
5. **Bridge home.** URML repo (`reference/drone-runtime/CrazyflieAdapter`), Bitcraze-maintained `bitcraze/crazyflie-urml-bridge`, or external?
6. **Conformance listing.** Would Bitcraze consider a README link to URML's compatible-runtimes registry once a working bridge ships?
7. **Anything else.**

## Implementation note

RFC-0181 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move13.yaml`](../../examples/lighthouses/outreach-move13.yaml).

## How to respond

`bitcraze/crazyflie-firmware` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC, with the cross-citation framing + Apache-2.0 client-library integration boundary explicit.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (GPL-3.0 firmware / Apache-2.0 client, 1.5k stars, Issues enabled, last commit 2026-05-26 very active, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (GPL-3.0 cross-citation gate, multiple Spec-RFC prerequisites, Crazyradio dongle dependency).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Bitcraze AB Sweden; default policy passes.
- [x] CLAUDE.md compliance check passed.
