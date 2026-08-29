---
rfc: 0041
title: ArduPilot integration, request for comment from ArduPilot/ardupilot maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented (Copter)
created: 2026-05-23
updated: 2026-08-29
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

# RFC-0041: ArduPilot integration, request for comment from ArduPilot/ardupilot maintainers

## Summary

URML's PX4 reference runtime already depends on `ArduPilot/pymavlink`, and URML's marine reference runtime already targets ArduSub (an ArduPilot variant) over MAVLink. This RFC proposes a sibling `ardupilot-runtime` package that mirrors `px4-runtime` to cover ArduCopter, ArduPlane, and ArduRover, completing the MAVLink-side of URML's substrate matrix. No spec change. The mapping reuses the existing drone profile and the existing `mobility.drive_type` enum without modification. This RFC documents the proposed shape and requests review and feedback from the `ArduPilot/ardupilot` maintainers before any adapter code lands.

This is a Move #1 follow-on. Move #1 (RFCs 0023-0038) closed at 16 industrial-manipulator and component vendors. ArduPilot belongs structurally to that wave (it is a substrate, not an AI/ML layer) and follows the proposal-only posture set by RFC-0037 (OSRF / Gazebo) and RFC-0040 (Hugging Face LeRobot): no shipping bridge in this PR by design.

## Motivation

ArduPilot is the most widely deployed open-source autopilot in the world. Per ardupilot.org, over a million vehicles run ArduPilot variants across multirotors (ArduCopter), fixed-wing (ArduPlane), wheeled and surface-vessel rovers (ArduRover), submarines (ArduSub), antenna trackers, and traditional helicopters. The project is community-developed, has run continuously since 2009, and is the standard against which any "substrate-neutral" claim in robot software has to test. As of 2026-05-23 the main repository carries 15,138 stars and 2,996 open issues, and a commit was merged today. This is the gold-standard open-source-community surface for a URML outreach RFC.

Two things make ArduPilot a concrete target rather than an aspirational one. First, URML already depends on ArduPilot infrastructure. The PX4 reference runtime at [`reference/px4-runtime/`](../../reference/px4-runtime/) talks MAVLink via `pymavlink`, which is published by ArduPilot at `ArduPilot/pymavlink` (696 stars, 237 open issues, Issues enabled, LGPLv3). Second, URML's marine reference runtime at [`reference/marine-runtime/`](../../reference/marine-runtime/) already targets ArduSub directly: `BlueRovAdapter` mirrors `PX4Adapter` over the same MAVLink protocol, ships hermetic unit tests, and runs `marine-sitl-e2e` against ArduSub SITL in a gated CI workflow. The "URML talks to ArduPilot already, in part" claim is verifiable in-repo today.

The integration story compresses to one sentence. ArduPilot's vehicle firmwares speak MAVLink. URML's `PX4Adapter` already maps URML's Layer-2 primitives to MAVLink commands. An `ardupilot-runtime` package would mirror that adapter, share the same `ROSAdapter` Protocol the rest of the runtime uses, and let one URML program target ArduCopter or PX4 or both, with no spec change, no validator change, and no manifest change.

## Detailed design

URML's existing artifacts this RFC builds on:

- [`reference/px4-runtime/`](../../reference/px4-runtime/): PX4 MAVLink adapter, 12 core methods plus three drone-profile methods, lazy `pymavlink` import, no ROS 2 dependency, live SITL e2e test. The structural template for an `ArduCopterAdapter`.
- [`reference/marine-runtime/`](../../reference/marine-runtime/): `BlueRovAdapter` over ArduSub via MAVLink. Already shipping, gated CI, mirrors `PX4Adapter` exactly. The proof-of-pattern that the same approach extends to ArduPilot family members.
- [`spec/profiles/drone/`](../../spec/profiles/drone/): drone profile spec, which already names `MAV_CMD_NAV_TAKEOFF`, `MAV_CMD_NAV_LAND`, `MAV_CMD_NAV_RETURN_TO_LAUNCH`, and `SET_POSITION_TARGET_LOCAL_NED` in its non-ROS implementation sketches. These are the exact MAVLink commands ArduCopter and ArduPlane consume.
- [`reference/validator/tests/fixtures/manifests/drone_civilian.yaml`](../../reference/validator/tests/fixtures/manifests/drone_civilian.yaml): illustrative drone manifest exercising `mobility.drive_type: multirotor`, `service_ceiling`, `station_keeping`, and a US-compliant `provenance` block under [RFC-0004](0004-compliance-policy.md). Reusable for an ArduCopter validation as-is.
- [`conformance/fixtures/drone/14_flight_only_positive.yaml`](../../conformance/fixtures/drone/14_flight_only_positive.yaml): drone conformance fixture already exercised by `PX4Adapter` via the conformance runner. An `ArduCopterAdapter` would target the same fixture without changes.

### Proposed `ardupilot-runtime` package shape

Match `px4-runtime` and `marine-runtime` verbatim. One package, multiple adapter classes covering the ArduPilot vehicle families, all composing the same connection layer:

```
reference/ardupilot-runtime/
├── pyproject.toml                 # name = "urml-ardupilot-runtime", extras = ["ardupilot"] -> pymavlink
└── src/
    └── urml_ardupilot_runtime/
        ├── __init__.py            # ARDUPILOT_ADAPTERS registry
        ├── _version.py
        ├── config.py              # ArduPilotAdapterConfig (mirror PX4AdapterConfig)
        ├── ardu_copter.py         # ArduCopterAdapter, drive_type: multirotor
        ├── ardu_plane.py          # ArduPlaneAdapter, drive_type: fixed_wing | vtol (QuadPlane)
        └── ardu_rover.py          # ArduRoverAdapter, drive_type: differential | ackermann | tracked
```

ArduSub coverage stays in `reference/marine-runtime/` where it already ships. ArduPilot's antenna tracker and traditional-helicopter variants are out of v0.1 scope.

Each adapter is a thin subclass over a shared MAVLink connection class, exactly the way `PX4Adapter` is structured. `pymavlink` is imported lazily so the package loads on every host; constructing an adapter requires the `[ardupilot]` extra. The composite-adapter pattern from `px4-runtime`'s `CompositeAdapter` carries over unchanged: an `ArduCopterAdapter` plus a ROS 2 companion routes flight to MAVLink and perception/manipulation/speech to ROS 2, the same one-URML-program-two-substrates posture documented in [`reference/px4-runtime/README.md`](../../reference/px4-runtime/README.md).

### Proposed URML primitive to ArduPilot MAVLink mapping

The mapping is essentially the PX4 mapping. ArduPilot and PX4 share the MAVLink command set; the differences live below MAVLink in firmware behavior, not at the protocol surface URML reaches.

| URML primitive | ArduPilot MAVLink command |
|---|---|
| `take_off` | `MAV_CMD_NAV_TAKEOFF` (ArduCopter, ArduPlane VTOL) |
| `land` | `MAV_CMD_NAV_LAND` (ArduCopter, ArduPlane); `MAV_CMD_NAV_LAND_LOCAL` for body-frame precision |
| `return_to_home` | `MAV_CMD_NAV_RETURN_TO_LAUNCH` (RTL mode in ArduCopter, RTL in ArduPlane) |
| `move_to` | `SET_POSITION_TARGET_LOCAL_NED` in GUIDED mode (ArduCopter); GUIDED waypoint in ArduPlane |
| `hover` | `SET_POSITION_TARGET_LOCAL_NED` with zero velocity in GUIDED (ArduCopter); LOITER for ArduPlane fixed-wing |
| `wait` | timed hold (rejected in flight per drone profile) |
| `wait_for` | MAVLink message subscribe-once with predicate |
| `measure` | `DISTANCE_SENSOR`, `BATTERY_STATUS`, `SCALED_PRESSURE`, telemetry streams |
| `report` | `STATUSTEXT` MAVLink message |
| `scan` | stub success at first cut, mirroring `PX4Adapter`; true waypoint expansion follows |

The not-applicable primitives (`dock`, `grasp`, `release`, `detect`, `capture`, `speak`, `listen`) return `NavigationResult(success=False, reason="not_supported_on_bare_autopilot: ...")` exactly the way `PX4Adapter` already does. The companion-adapter route covers real drone deployments that pair a flight controller with a vision/manipulation companion computer.

### Profile coverage across ArduPilot vehicle families

The existing v0.1 `mobility.drive_type` enum already covers ArduPilot's deployable surface. No schema change:

| ArduPilot firmware | URML `mobility.drive_type` | URML profile |
|---|---|---|
| ArduCopter (multirotor) | `multirotor` | drone |
| ArduCopter (traditional heli) | `multirotor` (v0.1; a future RFC may add `helicopter` if real demand) | drone |
| ArduPlane (fixed-wing) | `fixed_wing` | drone |
| ArduPlane (QuadPlane VTOL) | `vtol` | drone |
| ArduRover (wheeled) | `differential` / `ackermann` / `tracked` | (no shipping profile yet; warehouse/educational both plausible homes) |
| ArduSub (submarine) | `underwater_thrusters` | (marine profile, already shipping under [`reference/marine-runtime/`](../../reference/marine-runtime/)) |
| ArduRover (surface vessel / boat) | `differential` for skid-steer; future RFC may add `boat` if hull-specific semantics emerge | (deferred) |
| AntennaTracker | out of v0.1 scope | n/a |

### Proposed conformance integration

Mirror `px4-integration.yml` and `marine-integration.yml`. A gated `.github/workflows/ardupilot-integration.yml` with three jobs: `ardupilot-smoke` (real `pymavlink`, no SITL), `ardupilot-sitl-e2e` (the SITL e2e against ArduCopter SITL targeting the existing `conformance/fixtures/drone/14_flight_only_positive.yaml`), and `ardupilot-arm64-build` (the hermetic suite under linux/arm64 QEMU emulation). The conformance runner consumes the new adapter via `adapter_factory` exactly as it does for `PX4Adapter` today.

### Compatibility notes

- **License.** ArduPilot's vehicle firmwares are GPLv3. `pymavlink` is LGPLv3. URML's reference runtimes are Apache 2.0. The `ardupilot-runtime` adapter package imports `pymavlink` the same way `px4-runtime` does today (lazily, via the `[ardupilot]` extra), so the existing LGPLv3-via-import pattern carries over with no friction. URML never links GPLv3 firmware; it speaks to a running autopilot over a network or serial transport.
- **Python.** ArduPilot's tooling and `pymavlink` target Python 3.9+. URML's reference packages target the same lower bound. No dependency-band friction.
- **MAVLink versions.** `pymavlink` covers MAVLink v1 and v2 dialects (`common`, `ardupilotmega`, plus vehicle dialects). The adapter targets the `ardupilotmega` dialect for vendor-specific extensions; the core commands listed above are in `common` and work uniformly.
- **SITL.** ArduPilot's SITL is a first-class testing target with broad community support. URML's existing `marine-sitl-e2e` against ArduSub SITL is the proof-of-life for this in `.github/workflows/marine-integration.yml`.
- **Origin.** ArduPilot is community-developed under independent foundation governance (formerly DroneCode, now `ardupilot.org` direct). URML's default US-federal compliance policy ([RFC-0003](0003-us-alignment.md) and [RFC-0004](0004-compliance-policy.md)) enforces at the manifest level on vendor/component provenance, not at the autopilot level. ArduPilot itself imposes no provenance constraint on the deployer's hardware choices, which is consistent with URML's posture: provenance lives in the manifest.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / manifest schema: none. ArduPilot's deployable surface is covered by the existing `mobility.drive_type` enum after [RFC-0009](0009-legged-humanoid-mobility.md).
- Reference runtime: proposed new package `reference/ardupilot-runtime/`. Not built in this PR. Contingent on ArduPilot maintainer feedback.
- Conformance suite: proposed new `.github/workflows/ardupilot-integration.yml`. The existing `conformance/fixtures/drone/14_flight_only_positive.yaml` is reused without changes.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. The ArduPilot side gains no in-repo dependency on URML; the adapter package consumes `pymavlink` exactly as a normal MAVLink client would.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** RFCs 0023-0036 referenced real adapter code in-tree. This RFC references a proposed package whose existence depends on ArduPilot maintainer feedback. The honest framing matches RFC-0040: URML wants input on the adapter-package shape and the rover/boat coverage choice before publishing code, because both are observable decisions the existing PX4 / marine pattern does not pin down completely.
- **One more MAVLink adapter is one more place for MAVLink drift to bite.** PX4 and ArduPilot diverge in mode semantics (GUIDED vs OFFBOARD, AUTO vs MISSION) and in some vendor extensions. Mitigation: the adapter targets the common command set documented in `MAVLink Common.xml`, exactly the subset `PX4Adapter` already uses, and treats mode-entry as an adapter-internal concern.
- **Rover and boat coverage are messier than copter and plane.** The `mobility.drive_type` enum maps cleanly to ArduCopter and ArduPlane. ArduRover surface-vessel mode does not have a perfect URML enum value today. The RFC is honest about this and leaves the boat enum to a future RFC if real demand surfaces.
- **GPL firmware adjacency.** URML's reference runtimes are Apache 2.0; ArduPilot's firmware is GPLv3. URML never links the firmware (the boundary is MAVLink-over-network), but contributors should understand the distinction before any future work that touches firmware-side patches.

## Alternatives considered

1. **Ship the adapter first, ask ArduPilot maintainers later.** Rejected. The community's posture is collaborative and a pre-RFC saves rework, especially on the rover/boat enum question that future-proofs the design.
2. **Skip ArduPilot and keep PX4 as the sole MAVLink runtime.** Rejected. A single MAVLink autopilot is one substrate; two MAVLink autopilots demonstrate substrate-neutrality on the same protocol layer, which is the harder and more credible proof.
3. **Fold ArduPilot coverage into `px4-runtime` rather than a sibling package.** Rejected. The package-per-vendor pattern (`legged-runtime` for Spot/ANYmal, `humanoid-runtime` for Digit, `marine-runtime` for ArduSub) is the established URML convention. Collapsing ArduPilot into `px4-runtime` would lose the parity with the other substrate vendors.
4. **Target only ArduCopter, defer ArduPlane and ArduRover.** Rejected for the RFC document; the maintainer review benefits from seeing the full proposed scope. Implementation may still phase Copter first.

## Prior art

- `ArduPilot/ardupilot`: the upstream firmware (15,138 stars, 2,996 open issues, last commit 2026-05-23, GPLv3).
- `ArduPilot/pymavlink`: the MAVLink Python library URML's PX4 and marine runtimes already depend on (696 stars, 237 open issues, LGPLv3).
- ArduPilot SITL documentation at `ardupilot.org/dev`: the testing surface a future `ardupilot-sitl-e2e` would target.
- [`reference/px4-runtime/`](../../reference/px4-runtime/): the structural template, including `CompositeAdapter`.
- [`reference/marine-runtime/`](../../reference/marine-runtime/): the already-shipping ArduSub adapter; the proof that the pattern extends to ArduPilot family members.
- [`spec/profiles/drone/`](../../spec/profiles/drone/): the drone profile, which already cites the ArduPilot-compatible MAVLink command set in its implementation sketches.
- [RFC-0009](0009-legged-humanoid-mobility.md): `mobility.drive_type` precedent.
- [RFC-0037](0037-osrf-gazebo-integration.md): proposal-only outreach precedent.
- [RFC-0040](0040-hugging-face-lerobot.md): most recent proposal-only outreach RFC; structural template.
- RFCs 0023-0038: the Move #1 outreach pattern this RFC inherits.

## Unresolved questions

Provisional pending ArduPilot maintainer feedback:

1. **Per-family adapter classes vs one adapter with mode selection.** Should `ardupilot-runtime` expose `ArduCopterAdapter`, `ArduPlaneAdapter`, `ArduRoverAdapter` as distinct classes (the option proposed above), or a single `ArduPilotAdapter` whose behavior is configured by the connected vehicle's reported `MAV_TYPE`? The proposed shape mirrors `PX4Adapter` / `BlueRovAdapter` / `DigitAdapter` for ergonomic parity.
2. **Rover surface coverage.** Does mapping ArduRover (wheeled) to `differential` / `ackermann` / `tracked` cover the deployable surface the ArduPilot community expects, or are there rover capabilities (Z-turn, holonomic, omni) that need additional enum values? URML can add enum values via a small RFC; the question is whether they are needed now.
3. **Boat / USV coverage.** Should URML add a `boat` or `surface_vessel` value to `mobility.drive_type`, or is folding under `differential` for skid-steer rovers adequate for the ArduPilot surface-vessel population? Real-world demand here from the ArduPilot community would be the deciding signal.
4. **MAVLink dialect choice.** Is `ardupilotmega` the right dialect to target, or should the adapter stay strictly on `common` to maximize cross-autopilot portability? PX4 stays on `common`; ArduPilot extends it.
5. **SITL test pinning.** ArduCopter SITL has well-known harnesses (the `Tools/autotest` suite, AutoTest CI). Would the maintainers point at a specific pinned target as the URML conformance lane's pretty-printed reference, similar to how `marine-runtime` pins an ArduSub SITL configuration?
6. **Conformance-lane interest.** Would ArduPilot be open to a downstream URML conformance run referenced from ArduPilot's wiki for any URML program validated against an ArduPilot SITL configuration, similar to existing third-party integration pages?
7. **Anything else.**

## Implementation note

**2026-08-29 update.** `reference/ardupilot-runtime/` shipped with `ArduCopterAdapter` (Copter first; Plane and Rover remain follow-ups, answering Q1 in favour of per-family classes). It subclasses `PX4Adapter` and adds what the ArduPilot firmware needs around the shared command set: GUIDED entry, explicit arming with the autopilot's `PreArm:` text surfaced on refusal, ack matching by command id, arrival waits, `SET_POSITION_TARGET_GLOBAL_INT` for WGS84-bound locations, camera trigger for `capture`, and gripper / winch / servo output lines for `set_output`. `urml execute --adapter ardupilot` is wired in the CLI and the MCP server. The bench link was verified on a Pixhawk running ArduCopter 4.6.3 over USB, and the SITL e2e (flight-only fixture, five-station photogrammetry, winch + gripper delivery) is green against ArduCopter SITL `Copter-4.6.3`; no physical flight is claimed. Runbook: [`docs/demos/sentence-to-pixhawk.md`](../demos/sentence-to-pixhawk.md). The ArduPilot maintainer feedback this RFC requested is still welcome; nothing below is superseded by the shipped code.

Original note follows.

RFC-0041 shipped as a single RFC document PR. No adapter code in that PR. The `reference/ardupilot-runtime/` package is the mechanical follow-up, gated on ArduPilot maintainer feedback. Ledger entry under [`examples/lighthouses/outreach-move2.yaml`](../../examples/lighthouses/outreach-move2.yaml) (Move #1 substrate follow-on placed in the Move #2 file because the Move #1 file is parity-tested against an in-repo demo runner that ArduPilot does not yet have).

## Requested feedback (from ArduPilot/ardupilot maintainers)

1. Per-family adapter classes vs one adapter with mode selection (Q1 above).
2. Rover and boat enum coverage (Q2, Q3).
3. MAVLink dialect choice (Q4).
4. Preferred SITL pinning for the URML conformance lane (Q5).
5. Interest in a downstream URML conformance-lane reference on the ArduPilot wiki (Q6).
6. Anything URML's PX4 runtime gets wrong about ArduPilot's MAVLink surface today, before `ardupilot-runtime` ships.
7. Anything else.

## How to respond

The `ArduPilot/ardupilot` repository accepts public Issues. The repo has 81 sibling repos under the `ArduPilot` org and 2,996 currently open issues, indicating an active triage path. The `Enhancement` label exists (verified via `gh api repos/ArduPilot/ardupilot/labels` on 2026-05-23) and is the right label for a proposal Issue of this kind. ArduPilot also runs an active developer forum at `discuss.ardupilot.org` and weekly dev calls announced on `ardupilot.org/dev`.

URML's planned channel: open a single Issue on `ArduPilot/ardupilot` labelled `Enhancement`, pointing to this RFC, and cross-post a short pointer on `discuss.ardupilot.org` for community visibility.

URML's own public Discussions for the broader Move #1 follow-on conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that URML already depends on ArduPilot infrastructure).
- [x] Motivation grounded in verified data (15,138 stars, 2,996 open issues, last commit today, 81 repos in the org), not boilerplate.
- [x] Detailed design names every affected component (`px4-runtime`, `marine-runtime`, drone profile, drone-civilian manifest, conformance fixture) with verified file paths.
- [x] At least one alternative considered (four are).
- [x] Drawbacks are real (proposal-only, MAVLink drift, rover/boat enum gaps, GPL adjacency).
- [x] Backward compatibility: purely additive.
- [x] No Layer-2 primitive added. The mapping uses the existing vocabulary, and `mobility.drive_type` is reused without modification.
- [x] Implementation note explicitly says no adapter code in this PR; later session contingent on feedback.
- [x] Surface ("How to respond") is verified live: Issues open, `Enhancement` label exists, dev forum and weekly call are documented.
- [x] No em-dashes, no formulaic structure, voice consistent with RFC-0040.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. Substrate-neutral posture preserved. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit.
