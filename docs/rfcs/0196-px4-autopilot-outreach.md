---
rfc: 0196
title: PX4-Autopilot (Linux Foundation Dronecode drone-autopilot substrate) integration, request for comment from PX4 maintainers
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

# RFC-0196: PX4-Autopilot (drone-autopilot substrate) integration

## Summary

URML does not yet ship a PX4 manifest fixture or adapter. This RFC documents the proposed URML v0.1 capability-manifest mapping for the PX4 drone autopilot over [`PX4/PX4-Autopilot`](https://github.com/PX4/PX4-Autopilot) (BSD-3-Clause), and **requests review and feedback from the PX4 maintainers**. No spec change.

**This is URML's first Move-16 substrate-spine RFC.** Theme A (substrate spine — drone autopilot + ROS 2 + middleware + SLAM) engages the substrate maintainers URML's substrate-neutral claim depends on. PX4 is the dominant open drone-autopilot stack and the foundation-direct engagement entry for URML's drone-runtime story.

## Motivation

PX4 is the foundation-governed open-source drone autopilot. Linux Foundation Dronecode Foundation governance (multi-vendor, vendor-neutral); BSD-3-Clause across the autopilot core. Repo at [`PX4/PX4-Autopilot`](https://github.com/PX4/PX4-Autopilot) (BSD-3-Clause, 11.8k stars, Issues enabled, last commit `2026-05-28` daily activity, **not archived**).

URML benefits from documenting the PX4 manifest mapping because:

1. **PX4 is URML's drone-runtime substrate.** URML's existing drone profile (RFC-0008) + multirotor / fixed_wing / vtol mobility classes (RFC-0009) implicitly target PX4 via MAVLink. URML's manifest should declare PX4 as the active autopilot substrate per drone deployment.
2. **Foundation-direct engagement at Dronecode is identity-load-bearing.** URML's substrate-neutral claim through 15 prior moves has been implicit; engaging the Dronecode Foundation at PX4 covers PX4 / MAVLink / MAVSDK / QGroundControl as a substrate-family.
3. **PX4's airframe + module declaration shape is what URML's manifest would compose with.** PX4's `Autopilot/ROMFS/px4fmu_common/init.d/airframes` catalog + module-set is the upstream-declared airframe inventory URML's manifest can cross-reference.

## Detailed design

### URML v0.1 capability-manifest mapping (planned `px4_airframe_cell.yaml` fixture)

`mobility` + `substrate` blocks:

| URML field | Maps to PX4 attribute |
|---|---|
| `name` | Deployment handle (`px4_holybro_x500_v2`, `px4_holybro_pixhawk6c`, etc.) |
| `mobility.drive_type` | URML's v0.1 enum (`multirotor` / `fixed_wing` / `vtol` / `underwater_thrusters`) — clean fit per RFC-0009 |
| `substrate.autopilot: custom` (`px4`) | Declares PX4 as the autopilot substrate |
| `substrate.px4_version` | PX4 release version pin (relevant for closed-loop reproducibility) |
| `substrate.airframe_id` | PX4 `SYS_AUTOSTART` airframe identifier (cross-references PX4's airframe catalog) |
| `substrate.module_set: custom` | PX4 module configuration (sensors / mixers / parameters) |
| `protocol.mavlink_version` | MAVLink protocol version (cross-link to RFC-0197) |

### What URML v0.1 does not yet express for PX4

1. **Autopilot-substrate declaration.** URML's v0.1 has no `substrate.autopilot` enum entry. Spec RFC queued — opens the autopilot-class substrate vocabulary that DroneCAN (RFC-0199) is the alternate of.
2. **Airframe-identifier cross-reference.** PX4's airframe catalog uses numeric identifiers (`SYS_AUTOSTART`) referencing a vendor-maintained airframe set; URML's manifest cannot today declare which airframe-ID the deployment targets.
3. **PX4 module-set declaration.** PX4's modular architecture means deployments enable / disable specific modules (e.g., `vmount`, `gimbal`, `airspeed_selector`); URML's manifest cannot today declare module-level substrate composition.
4. **Closed-loop parameter pinning.** PX4's hundreds of parameters tune the control loops; URML's manifest cannot today pin parameter sets for reproducible-control deployments.

### Compatibility notes

- **Vendor / foundation.** [`PX4`](https://github.com/PX4) — Linux Foundation Dronecode Foundation governance. Multi-vendor (Auterion CH commercial; Yuneec; others).
- **Flagship repo.** [`PX4/PX4-Autopilot`](https://github.com/PX4/PX4-Autopilot) — BSD-3-Clause, 11.8k stars, Issues enabled, last commit 2026-05-28 daily activity, **not archived**.
- **Origin.** Linux Foundation Dronecode Foundation (multi-national; foundation governance neutral). Passes US-federal default policy (foundation-direct + multi-vendor + Apache-class license).
- **License fit.** BSD-3-Clause cleanly composes with URML's Apache-2.0 stance.
- **Maintainer signal.** Daily activity; foundation-direct; the dominant open drone-autopilot stack across hobby / research / commercial deployments.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC; autopilot-substrate declaration + airframe-identifier cross-reference + module-set declaration + parameter-pinning Spec RFCs queued.
- Reference runtime: URML's existing `reference/ros2-runtime/` composes via MAVLink (RFC-0197); future `reference/drone-runtime/Px4Adapter` is a candidate at the autopilot-substrate layer.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only).

## Drawbacks

- **Proposal-only.**
- **Multiple Spec-RFC prerequisites** (autopilot-substrate, airframe-id, module-set, parameter-pinning).
- **Closed-loop reproducibility is novel manifest territory** — PX4's parameter sets affect deployed behavior; URML hasn't yet declared parameter-pin semantics.
- **Multi-vendor downstream complexity** — Auterion (commercial) and others extend PX4 with additional modules; URML's manifest cannot today distinguish.

## Alternatives considered

1. **Engage Auterion (commercial PX4 downstream) instead of foundation upstream.** Rejected. Auterion is covered via PX4 governance per Move-16 research; foundation-direct engagement is the cleaner shape.
2. **Bundle PX4 + ArduPilot into one autopilot RFC.** Rejected. ArduPilot was engaged separately via Move-2 RFC-0041 (response: declined 2026-05-25); per-vendor engagement is the right shape.
3. **Engage at the MAVLink protocol layer only (RFC-0197).** Rejected. PX4 is the autopilot substrate; MAVLink is the protocol layer. Separate engagement at each layer is appropriate.

## Prior art

- [`PX4/PX4-Autopilot`](https://github.com/PX4/PX4-Autopilot) — the upstream flagship.
- [RFC-0197 (MAVLink)](0197-mavlink-outreach.md) — sibling Move-16 protocol-substrate RFC; PX4 communicates via MAVLink.
- [RFC-0198 (MAVSDK)](0198-mavsdk-outreach.md) — sibling Move-16 SDK-layer RFC.
- [RFC-0199 (DroneCAN)](0199-dronecan-libcanard-outreach.md) — sibling alternate-protocol RFC; URML manifest declares which protocol class is active per deployment.
- [RFC-0008 (drone profile)](0008-drone-profile.md) + [RFC-0009 (Layer-1 mobility specialization)](0009-layer1-mobility-specialization.md) — URML's drone-profile + multirotor / fixed_wing / vtol mobility class that PX4 implements.
- [RFC-0041 (ArduPilot)](0041-ardupilot-outreach.md) — Move-2 sibling autopilot RFC (response: declined 2026-05-25).

## Unresolved questions

For the PX4 maintainers:

1. **Autopilot-substrate manifest fields.** URML's v0.1 has no `substrate.autopilot: px4` declaration. Spec RFC queued. What manifest fields would a PX4 deployment expect (version pin, airframe-id, module-set, parameter-pin)?
2. **Airframe-identifier cross-reference.** Should URML's manifest declare the PX4 `SYS_AUTOSTART` airframe-id directly, or maintain a URML-side airframe identifier mapped to PX4's catalog?
3. **Module-set declaration.** PX4's modular architecture enables / disables specific modules; manifest field shape for declaring which modules are active in a deployment?
4. **Parameter-pinning for reproducibility.** PX4's parameter sets tune control loops; should URML's manifest pin parameter sets (or parameter hash) for reproducible-control deployments?
5. **Dronecode-level engagement scope.** Linux Foundation Dronecode governs PX4 / MAVLink / MAVSDK / QGroundControl. Should URML engage per-project or at the Dronecode-level scope?
6. **Adapter home.** URML repo (`reference/drone-runtime/Px4Adapter`), PX4-maintained `PX4/px4-urml-bridge`, or both?
7. **Conformance listing.** Would PX4 consider a README link to URML's compatible-runtimes registry once a working adapter ships? (Per [RFC-0014](0014-substrate-conformance.md), self-reported tier, no continuous obligation.)
8. **Anything else.**

## Implementation note

RFC-0196 ships as a single RFC document PR. Ledger entry in [`examples/lighthouses/outreach-move16.yaml`](../../examples/lighthouses/outreach-move16.yaml).

## How to respond

`PX4/PX4-Autopilot` has Issues enabled. URML's planned channel: open a single Issue labelled `enhancement` or `question`, pointing to this RFC.

## Self-review (Phase 0)

- [x] Surface verified 2026-05-28 (BSD-3-Clause, 11.8k stars, Issues enabled, last commit 2026-05-28 daily activity, isArchived: false).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (multiple Spec-RFC prerequisites, parameter-pinning novelty, multi-vendor downstream complexity).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added; no spec change.
- [x] Provenance: Linux Foundation Dronecode (foundation-direct, multi-national); default policy passes.
- [x] CLAUDE.md compliance check passed.
