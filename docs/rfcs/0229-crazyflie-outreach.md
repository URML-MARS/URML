---
rfc: 0229
title: Crazyflie / Bitcraze (open nano-drone research platform) integration, request for comment from Bitcraze maintainers
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

# RFC-0229: Crazyflie / Bitcraze (open nano-drone research platform) integration

## Summary

> **Maintainer-correction note (2026-06-08):** @ataffanel (Bitcraze co-founder)
> stated on the sibling firmware thread (RFC-0181, crazyflie-firmware#1636) that
> `crazyflie-lib-python` declares **GPLv3**. This RFC's "GPL-2.0" for `cflib`
> below is corrected to **GPLv3**; the integration stance (no vendoring, compose
> at the CRTP / `cflib` IPC boundary) is unchanged. Bitcraze's stated bar for a
> future approach: an external URML-maintained adapter plus a working demo with
> tests and clear safety limits, raised in a host-side repo.

URML does not yet ship a Crazyflie manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the Crazyflie nano-quadcopter over [`bitcraze/crazyflie-lib-python`](https://github.com/bitcraze/crazyflie-lib-python) (GPL-2.0), and **requests review and feedback from the Bitcraze maintainers**. No spec change.

**This is a Move-18 frame-break RFC.** The Crazyflie is an open, ~27-gram research quadcopter that is a fixture in university swarm and control labs. URML's `multirotor` mobility class already fits it, which makes it the cleanest flight demo in the frame-break wave: one sentence to a hovering nano-drone, over an entirely non-ROS, non-MAVLink stack.

## Motivation

The Crazyflie is controlled from a host through `cflib` over the CRTP (Crazy RealTime Protocol) radio link. `cflib` exposes a high-level commander (takeoff, go-to, land) that maps directly onto URML motion intent. Repo at [`bitcraze/crazyflie-lib-python`](https://github.com/bitcraze/crazyflie-lib-python) (GPL-2.0, 334 stars, Issues enabled, last commit 2026-05-12, **not archived**); the firmware at [`bitcraze/crazyflie-firmware`](https://github.com/bitcraze/crazyflie-firmware) (GPL-3.0) is daily-active.

URML benefits from documenting the Crazyflie manifest mapping because:

1. **`multirotor` already fits, so the mapping is honest and small.** URML's `drive_type` enum has `multirotor` with `station_keeping` and `service_ceiling`. The Crazyflie exercises exactly those fields with no new mobility class required.
2. **CRTP is a substrate URML has never touched.** Prior drone work (RFC-0196 PX4, RFC-0197 MAVLink) assumes MAVLink. The Crazyflie speaks CRTP. Mapping it tests whether URML's manifest can declare a non-MAVLink flight protocol.
3. **The research-lab audience is the right reader.** Bitcraze's users are exactly the roboticists URML writes its docs for, and the high-level commander is a clean, demoable target.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `crazyflie_nano_cell.yaml` fixture)

`mobility` + `substrate` blocks:

| URML field | Maps to Crazyflie attribute |
|---|---|
| `name` | Deployment handle (`crazyflie_2_1`, `crazyflie_brushless`, etc.) |
| `mobility.drive_type: multirotor` | Clean fit (quadcopter) |
| `mobility.station_keeping: true` | Holds position via the high-level commander / onboard estimator |
| `mobility.service_ceiling` | Indoor operating envelope (m) |
| `mobility.max_velocity` | `cflib` high-level commander velocity limit (m/s) |
| `substrate.autopilot: custom` (`crazyflie`) | Declares the Crazyflie firmware as the flight substrate |
| `protocol: custom` (`crtp`) | **No v0.1 protocol-class field**; CRTP declaration is a queued Spec RFC |

### What URML v0.1 does not yet express for Crazyflie

1. **CRTP protocol-class declaration.** URML's manifest has no field to declare which flight protocol class (CRTP, MAVLink, DroneCAN) a deployment uses. Spec RFC queued; CRTP is the alternate of the MAVLink class discussed in RFC-0197.
2. **Nano-scale platform envelope.** The Crazyflie's mass, indoor-only envelope, and positioning-system dependence (e.g. Lighthouse, Loco) have no v0.1 manifest field.
3. **Swarm composition.** The Crazyflie's signature use is multi-agent swarms. URML's manifest describes a single robot's capability; swarm composition is out of v0.1 scope and noted as a boundary.

### Compatibility notes

- **Vendor.** [`bitcraze`](https://github.com/bitcraze) — Bitcraze AB, Malmö, Sweden. Open-hardware and open-source company.
- **Engagement repo.** [`bitcraze/crazyflie-lib-python`](https://github.com/bitcraze/crazyflie-lib-python) — GPL-2.0, 334 stars, Issues enabled, last commit 2026-05-12, **not archived**. Firmware at `bitcraze/crazyflie-firmware` (GPL-3.0) is daily-active.
- **Origin.** Sweden (allied; not on any covered list). Passes US-federal default policy.
- **License fit.** `cflib` is GPL-2.0, the firmware GPL-3.0. Neither composes into URML's Apache-2.0 by code vendoring. Integration stays at the CRTP / `cflib` IPC boundary, no Bitcraze code in the URML repo. Same shape as RFC-0166 (piper1-gpl) and RFC-0122 (GelSight).
- **Maintainer signal.** Active firmware and library development; community-friendly, with an active forum and Discord.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; protocol-class declaration (CRTP) + nano-scale envelope are queued Spec RFCs.
- Reference runtime: a future `CrazyflieAdapter` driving the `cflib` high-level commander is a candidate. No code in this RFC.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Spec-RFC prerequisite** (CRTP protocol-class field).
- **Swarm gap.** The Crazyflie's most compelling use is swarms, which URML v0.1 does not model. The single-robot mapping undersells the platform.
- **Dual GPL boundary** (GPL-2.0 lib, GPL-3.0 firmware) constrains integration to IPC; no shared-code path.

## Alternatives considered

1. **Engage the firmware repo (`crazyflie-firmware`) instead of the Python lib.** Rejected. The motion-intent boundary is the `cflib` high-level commander on the host; the firmware is below the line URML maps to.
2. **Treat the Crazyflie under the existing MAVLink drone work (RFC-0196 / RFC-0197).** Rejected. The Crazyflie speaks CRTP, not MAVLink. Folding it into the MAVLink RFCs would misrepresent the protocol and miss the point of mapping a second flight protocol.
3. **Wait until URML models swarms before engaging.** Rejected. The single-drone mapping is honest and useful now; swarm support is a later, separable conversation.

## Prior art

- [`bitcraze/crazyflie-lib-python`](https://github.com/bitcraze/crazyflie-lib-python) — the upstream host library.
- [RFC-0009 (mobility specialization)](0009-legged-humanoid-mobility.md) — the mobility-class vocabulary; `multirotor` already covers the Crazyflie.
- [RFC-0197 (MAVLink)](0197-mavlink-outreach.md) — the MAVLink protocol RFC that CRTP is the alternate of.
- [RFC-0014 (substrate conformance)](0014-substrate-conformance.md) — the compatible-runtimes registry a Crazyflie adapter could list against.
- [RFC-0227 (Klipper)](0227-klipper-outreach.md), [RFC-0228 (WPILib)](0228-wpilib-outreach.md), [RFC-0230 (OpenBCI / BrainFlow)](0230-openbci-brainflow-outreach.md) — sibling Move-18 frame-break RFCs.

## Unresolved questions

For the Bitcraze maintainers:

1. **Protocol-class declaration.** URML's manifest has no flight-protocol-class field. Spec RFC queued. Is declaring `crtp` at the manifest level the right shape, or is the protocol below the line a capability manifest should describe?
2. **Integration boundary.** Is the `cflib` high-level commander the boundary you would expect an external intent layer to drive, or is a lower-level setpoint interface more appropriate?
3. **Positioning dependence.** The Crazyflie's position hold depends on an external system (Lighthouse, Loco, flow deck). Should URML's manifest declare the positioning method as a capability precondition for `station_keeping`?
4. **Nano-scale envelope.** Are mass and indoor-only operating envelope worth declaring in a capability manifest?
5. **Swarm scope.** URML v0.1 describes a single robot. Is a single-Crazyflie mapping useful to your users, or is the swarm case the only one that matters in practice?
6. **License boundary.** URML stays Apache-2.0 and integrates at the CRTP / `cflib` IPC boundary with no Bitcraze code vendored. Does that match your expectation?
7. **Adapter home and conformance listing.** URML repo (a `CrazyflieAdapter`), a Bitcraze-side example, or neither? Would Bitcraze consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported, no obligation.)
8. **Anything else.**

## Implementation note

RFC-0229 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## How to respond

`bitcraze/crazyflie-lib-python` has Issues enabled. Bitcraze's cultural home for discussion is the Bitcraze forum (and Discord). URML's planned channel: a forum thread pointing to this RFC, with a GitHub Issue (labelled `question`) only if the maintainers prefer it. If the GitHub-Issue venue is not the right place for a cross-project RFC, that answer is useful and URML will route to the forum.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-29 (cflib GPL-2.0, 334 stars, Issues enabled, last commit 2026-05-12, isArchived: false; firmware GPL-3.0).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (CRTP Spec-RFC prerequisite, swarm gap, dual-GPL IPC-only boundary).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Sweden (allied, passes default policy); GPL integration at the IPC boundary; default policy passes.
- [x] CLAUDE.md compliance check passed.
