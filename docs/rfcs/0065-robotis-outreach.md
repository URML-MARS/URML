---
rfc: 0065
title: ROBOTIS integration, request for comment from ROBOTIS-GIT maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-24
updated: 2026-05-24
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

# RFC-0065: ROBOTIS integration, request for comment from ROBOTIS-GIT maintainers

## Summary

URML does not yet ship a ROBOTIS integration. This RFC proposes a `RobotisAdapter` family targeting four published surfaces under the [`ROBOTIS-GIT` GitHub org](https://github.com/ROBOTIS-GIT): `turtlebot3` (2k stars, Apache-2.0, ROS 2 Humble + Jazzy + Rolling), `turtlebot3_manipulation`, the OP3 humanoid line (newly reboot for ROS 2 in 2025), and the `dynamixel_sdk` servo backbone that URML's existing [RFC-0064 (Trossen Interbotix)](0064-trossen-interbotix-outreach.md) already implicitly depends on. The adapter routes URML Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) onto ROBOTIS's published ROS 2 topics, services, and Dynamixel protocol calls without proposing changes to the upstream stack. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the ROBOTIS-GIT maintainers.

This is the first **Move #4** RFC. Move #3 (RFCs 0061–0064) targeted the affordable / desktop / educational tier. Move #4 opens an adjacent-niches sweep across categories Moves #1–#3 did not touch: ROBOTIS is the Korean-anchored education + research mobile + humanoid + servo backbone that URML's prior outreach implicitly leaned on but never directly engaged.

## Motivation

ROBOTIS sits at three intersections URML cares about simultaneously. First, **TurtleBot 3** is the de-facto introductory ROS 2 mobile platform in global robotics education (acknowledged in [RFC-0011 (Educational profile)](0011-educational-profile.md) but never the subject of dedicated outreach). Second, **OP3** is the open-platform humanoid that just got a ROS 2 re-release in 2025, making it the most accessible programmable humanoid in the sub-$10k tier outside of Berkeley Humanoid Lite and the LeRobot SO-100 line. Third, **Dynamixel** smart servos are the actuator standard that several already-covered URML targets transitively use: Trossen Interbotix X-Series (RFC-0064), Stanford ALOHA's gripper line (RFC-0056), LeRobot SO-100 (RFC-0040). URML's prior outreach has implicitly leaned on the Dynamixel ecosystem without ever surfacing the institutional relationship.

Three things make this RFC concrete rather than aspirational. First, `ROBOTIS-GIT/turtlebot3` is Apache-2.0 with active multi-branch maintenance across ROS 2 Humble, Jazzy, and Rolling; latest release 2.3.6 on 2025-12-15. Issues enabled (11 open at time of writing), CONTRIBUTING.md present. Second, the sibling repos (`turtlebot3_msgs`, `turtlebot3_simulations`, `turtlebot3_manipulation`, `OpenCR`, `open_manipulator`) form a coherent ROS 2 ecosystem URML's existing ROS 2 substrate path already covers at the dispatch layer. Third, the ROBOTIS company is one of the longest-running ROS-ecosystem commercial entities (founded 1999, Seoul), and the open-platform line has visible academic-curriculum reach across Asia, Europe, and North America.

ROBOTIS's posture is open-source for the open-platform line (Apache-2.0 on TurtleBot 3, BSD on related packages) and proprietary on the servo silicon (Dynamixel chips), with the `dynamixel_sdk` exposing the protocol surface in open source. URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. ROBOTIS does not compete with URML for the substrate-neutral vocabulary role. ROBOTIS makes the hardware and the ROS driver. URML is the spec the program above the driver can target.

## Detailed design

URML's existing artifacts that feed into a ROBOTIS adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/educational/`](../../spec/profiles/educational/) ([RFC-0011](0011-educational-profile.md)): the TurtleBot 3 home profile.
- [`spec/profiles/research/`](../../spec/profiles/research/) ([RFC-0012](0012-research-profile.md)): the OP3 home profile.
- [RFC-0009](0009-legged-humanoid-mobility.md): the humanoid mobility capability surface for OP3.
- [`reference/mobile-runtime/`](../../reference/mobile-runtime/): the runtime that hosts wheeled-base adapters.
- [`reference/humanoid-runtime/`](../../reference/humanoid-runtime/): the runtime that hosts OP3-class humanoids.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime that hosts the `open_manipulator` arm.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference.

### Proposed `RobotisAdapter` family shape

One adapter family, three concrete adapters parameterised by platform. Package layout:

```
reference/robotis-runtime/src/robotis_runtime/
├── __init__.py
├── adapter_turtlebot3.py    # TurtleBot 3 (Burger, Waffle, Waffle Pi)
├── adapter_op3.py           # OP3 humanoid
├── adapter_open_manipulator.py  # OpenManipulator-X arm
├── dynamixel.py             # shared Dynamixel SDK helpers
└── manifests/
    ├── robotis_turtlebot3_burger.yaml
    ├── robotis_turtlebot3_waffle.yaml
    ├── robotis_turtlebot3_waffle_pi.yaml
    ├── robotis_op3.yaml
    └── robotis_open_manipulator_x.yaml
```

Each adapter implements URML's substrate Protocol. The wheeled-base adapter dispatches to `/cmd_vel` and Nav2 goal-pose topics; the OP3 adapter dispatches to the OP3-specific motion-module topics; the arm adapter dispatches to `JointTrajectory` action goals.

### Proposed URML v0.1 to ROBOTIS mapping

| URML primitive | TurtleBot 3 | OP3 humanoid | OpenManipulator-X arm |
|---|---|---|---|
| `move_to(pose)` | `geometry_msgs/Twist` on `/cmd_vel` direct drive; Nav2 goal-pose on `/goal_pose` when the navigation stack is loaded. | OP3 walk-engine commands plus head-tracking on the OP3 module topics. | `JointTrajectory` action goal on the arm's published trajectory action server. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable; manifest declares no gripper. | OP3 has hand servos but no documented gripper-grasp surface; declared `none` until upstream confirms a stable API. | Gripper service on the OpenManipulator-X gripper topic. |
| `measure(sensor_id)` | LIDAR (`/scan`), IMU, optional camera. | IMU + foot-pressure sensors. | Joint-state and any externally added sensor. |
| `wait_for(...)` | ROS 2 subscriber with debounce, identical pattern to other URML ROS 2 adapters. | Same pattern. | Same pattern. |
| `report(status)` | `/urml/<adapter>/report` topic. | Same. | Same. |
| `pick_from` / `place_at` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Not applicable. | Not applicable on stock OP3 (no gripper). | Layer-3 composition over `move_to` plus `grasp` / `release`. |

### Proposed capability manifest

The manifests live under `reference/robotis-runtime/src/robotis_runtime/manifests/`. A condensed shape for `robotis_turtlebot3_burger`:

```yaml
brand: robotis_turtlebot3_burger
profile: educational
mobility: wheeled_differential
mass_kg: 1.0
payload_kg: 0.5
transport: ros2
ros2:
  package: ROBOTIS-GIT/turtlebot3
  cmd_vel_topic: /cmd_vel
  scan_topic: /scan
  nav2_compatible: true
sensors:
  - lidar_2d
  - imu_6dof
gripper: none
controller: opencr
provenance:
  origin: KR
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `provenance.origin: KR` row passes the URML US-federal default policy at [RFC-0003](0003-us-alignment.md) without organisational override. South Korea is a US treaty ally without procurement-rule flagging on ROBOTIS specifically (verify per-deployment for sensitive contracts via the operator's policy file per [RFC-0004](0004-compliance-policy.md)).

### Proposed conformance integration

A `URML_ROBOTIS_INTEGRATION=1` env-gated CI workflow installs the TurtleBot 3 ROS 2 packages, runs each platform's adapter against a hermetic mock that replays joint-state / scan / IMU responses, and asserts that the emitted commands match per-platform golden traces. The in-tree conformance suite continues to use `MockROSAdapter`.

### Cross-link to existing URML outreach

RFC-0064 (Trossen Interbotix) and RFC-0056 (Stanford ALOHA) both depend on Dynamixel servos transitively. A direct ROBOTIS engagement closes the institutional loop: URML's adapter family ships against the servo backbone its existing outreach already leans on, and a ROBOTIS conformance lane on the Dynamixel side makes the dependency mutual and documented.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new package `reference/robotis-runtime/`. Not built in this PR. The RFC requests ROBOTIS-GIT maintainer feedback first.
- Conformance suite: proposed new `robotis-integration.yml` CI workflow and a `URML_ROBOTIS_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. ROBOTIS gains nothing yet; the adapter consumes the published ROS 2 packages and Dynamixel protocol without proposing changes to them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** RFCs 0023–0036 reference real adapter code. This RFC references a proposal.
- **OP3 motion surface is module-specific.** OP3 uses a custom motion-module topic shape rather than the generic `JointTrajectory` action of the arm. URML's `move_to` on OP3 is not directly substitutable with `move_to` on a UR or Franka without an OP3-specific posture vocabulary at Layer-3.
- **OpenManipulator-X gripper is fragile.** The grip surface is a position-controlled servo, not a torque-aware gripper; programs that assume torque feedback (some industrial-profile pick-and-place compositions) will not retarget cleanly.
- **Dynamixel SDK is the institutional anchor but Dynamixel chips are closed silicon.** The protocol-level adapter is fine; firmware-level customisation is not in URML's scope and never should be.
- **Multi-platform support widens the test matrix.** Three adapters (TurtleBot 3, OP3, OpenManipulator-X) means three integration lanes; ROBOTIS catalog growth (e.g., a future TurtleBot 4-equivalent from ROBOTIS directly) would add a fourth.

## Alternatives considered

1. **Ship the adapter first, ask ROBOTIS-GIT maintainers later.** Rejected. OP3's motion surface and the cross-platform Dynamixel SDK boundary are observable choices worth maintainer input on; a pre-RFC saves rework.
2. **Target only TurtleBot 3 and skip OP3 and the arm.** Rejected. The catalog-breadth value of one institutional contact reaching three platforms is too high to leave on the table.
3. **Fold ROBOTIS into [RFC-0064 (Trossen Interbotix)](0064-trossen-interbotix-outreach.md) as a Dynamixel-shared-backbone note.** Rejected. The institutional audiences are distinct (Trossen is a US distributor; ROBOTIS is the Korean OEM), and the platforms are different (Interbotix is arms; TurtleBot 3 is mobile; OP3 is humanoid).
4. **Wait for OP3 ROS 2 to mature before opening outreach.** Rejected. The 2025 re-release is the right moment: too late forfeits the standard-setting opportunity; too early would block on instability the URML adapter can paper over.

## Prior art

- `ROBOTIS-GIT/turtlebot3`: the upstream TurtleBot 3 package (2k stars, Apache-2.0, ROS 2 Humble + Jazzy + Rolling, 2.3.6 on 2025-12-15, Issues enabled, CONTRIBUTING.md present, C++ + Python + CMake).
- `ROBOTIS-GIT/turtlebot3_msgs`, `turtlebot3_simulations`, `turtlebot3_manipulation`: the sibling packages.
- `ROBOTIS-GIT/OpenCR`: the controller-board firmware.
- `ROBOTIS-GIT/open_manipulator`: the OpenManipulator-X arm package.
- `ROBOTIS-GIT/dynamixel_sdk`: the Dynamixel protocol SDK (used transitively by RFC-0064 and RFC-0056).
- OP3 emanual at `emanual.robotis.com/docs/en/platform/op3/`: the canonical OP3 documentation.
- [RFC-0011](0011-educational-profile.md): the URML profile this RFC's TurtleBot 3 manifest targets.
- [RFC-0012](0012-research-profile.md): the URML profile this RFC's OP3 manifest targets.
- [RFC-0040](0040-hugging-face-lerobot.md), [RFC-0056](0056-stanford-aloha.md), [RFC-0064](0064-trossen-interbotix-outreach.md): the existing Dynamixel-transitive URML outreach.
- [RFC-0061](0061-wlkata-outreach.md) through [RFC-0064](0064-trossen-interbotix-outreach.md): the Move #3 per-vendor outreach pattern.

## Unresolved questions

Provisional pending ROBOTIS-GIT maintainer feedback:

1. **Adapter home.** Should URML host the adapter under `reference/robotis-runtime/` (URML-side), under a new repo in the `ROBOTIS-GIT` org as a contributed example, or both?
2. **OP3 motion surface.** Is the OP3 motion-module topic the right place for URML's `move_to` to dispatch, or would ROBOTIS recommend a higher-level walk-engine interface (and is one stable enough for URML to target)?
3. **Dynamixel cross-link.** Is there interest in a documented note in `dynamixel_sdk` README acknowledging the URML adapters (Trossen RFC-0064, ALOHA RFC-0056, LeRobot RFC-0040) that transitively depend on it?
4. **TurtleBot 3 variants.** Per-variant manifests (Burger, Waffle, Waffle Pi) versus a single parametric manifest?
5. **OpenCR custom firmware.** Should URML's adapter target stock OpenCR firmware, or is there a documented path for custom firmware variants?
6. **Conformance lane.** Open to a URML conformance line on `turtlebot3`'s README or in the OP3 emanual?
7. **Anything else.**

## Implementation note

RFC-0065 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/robotis-runtime/` package follows in a later session, gated on ROBOTIS-GIT maintainer feedback. Draft state. First Move #4 RFC. Ledger entry in [`examples/lighthouses/outreach-move4.yaml`](../../examples/lighthouses/outreach-move4.yaml).

## Requested feedback (from ROBOTIS-GIT maintainers)

1. Adapter home (URML repo, ROBOTIS-GIT contributed example, both).
2. OP3 motion-surface choice.
3. Dynamixel cross-link interest.
4. TurtleBot 3 variant manifest granularity.
5. OpenCR firmware coverage.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`ROBOTIS-GIT/turtlebot3` has Issues enabled (verified 2026-05-24); CONTRIBUTING.md is present and documents the contribution path. URML's planned channel: open a single Issue on `ROBOTIS-GIT/turtlebot3` labelled with the closest `enhancement` equivalent, pointing to this RFC, with optional cross-references on `ROBOTIS-GIT/dynamixel_sdk` (institutional backbone surface) and the OP3 emanual if maintainers prefer to thread there.

URML's own public Discussions for the broader Move #4 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the first Move #4 RFC).
- [x] Motivation grounded in verified technical alignment (Apache-2.0 TurtleBot 3 with active ROS 2 maintenance, OP3 2025 re-release, dynamixel_sdk as institutional backbone for three existing URML outreach RFCs) plus the Korean / academic-curriculum positioning.
- [x] Detailed design uses verified repo names (`ROBOTIS-GIT/turtlebot3`, `turtlebot3_msgs`, `turtlebot3_simulations`, `turtlebot3_manipulation`, `OpenCR`, `open_manipulator`, `dynamixel_sdk`).
- [x] At least one alternative considered (four are: ship-first, TurtleBot-only, fold-into-Trossen, wait-for-OP3-maturity).
- [x] Drawbacks are real (proposal-only, OP3 motion surface specificity, gripper fragility, closed Dynamixel silicon, multi-platform test matrix).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The mapping uses the existing vocabulary plus the industrial-profile extensions from RFC-0013.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of `ROBOTIS-GIT/turtlebot3` as of 2026-05-24.
- [x] Provenance row (`origin: KR`) recorded honestly per URML's discipline.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
