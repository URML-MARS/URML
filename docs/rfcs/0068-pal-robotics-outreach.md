---
rfc: 0068
title: PAL Robotics integration, request for comment from pal-robotics maintainers
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

# RFC-0068: PAL Robotics integration, request for comment from pal-robotics maintainers

## Summary

URML does not yet ship a PAL Robotics integration. This RFC proposes a `PalAdapter` family under [`reference/humanoid-runtime/`](../../reference/humanoid-runtime/) and [`reference/mobile-runtime/`](../../reference/mobile-runtime/) targeting the [`pal-robotics` GitHub org](https://github.com/pal-robotics) (195 public repos, Apache-2.0 predominant). The adapter routes URML Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) and the industrial-profile extensions ([RFC-0013](0013-industrial-layer2-primitives.md): `pick_from`, `place_at`, `swap_tool`) onto the published ROS 2 packages for TIAGo (single-arm mobile manipulator), TIAGo Pro (dual-arm), and PMB2 (mobile base). No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the pal-robotics maintainers.

This is the fourth Move #4 RFC. PAL Robotics anchors **commercial-research mobile manipulation** in the Move #4 sweep: mature European commercial player with a strong ROS 2 ecosystem, safety-rated mobile manipulator hardware, and an Apache-2.0 software stack across the published simulation and driver packages.

## Motivation

PAL Robotics fills a distinctive niche in URML's outreach landscape: a **commercial mobile-manipulator vendor** with a mature ROS 2 ecosystem. Move #1's industrial OEMs (Yaskawa, FANUC, UR, etc.) are stationary arms. Move #3's Trossen Interbotix is stationary research arms. Boston Dynamics Spot ([RFC-0043](0043-boston-dynamics-spot-integration.md)) and ANYbotics ANYmal ([RFC-0049](0049-anybotics-anymal-integration.md)) are legged platforms without arms. AgileX's mobile bases ([RFC-0066](0066-agilex-outreach.md)) have no arms. PAL's TIAGo (single-arm) and TIAGo Pro (dual-arm) are the missing combination: a wheeled mobile base with a torque-controlled manipulator on top, sold commercially, with full ROS 2 support.

Three things make this RFC concrete rather than aspirational. First, the `pal-robotics` GitHub org publishes 195 public repos with Apache-2.0 license predominant across the platform-specific packages (`tiago_simulation`, `tiago_pro_robot`, `tiago_pro_head_robot`, `pal_mjlab`, `pal_sea_arm`, `pal_urdf_utils`). The most-starred org repos (`aruco_ros` 596 stars, `backward_ros` 241 stars, `realsense_gazebo_plugin` 226 stars) are general-purpose ROS contributions that signal the maintainer team's quality. Second, PAL has been a fixture in the ROS ecosystem since the early days (PAL was named in "Top 10 ROS companies to watch" in 2019), and the TIAGo platform has documented academic deployments across European universities. Third, the safety story matters for URML: TIAGo Pro ships with Series Elastic Actuators and rated brake systems, which are exactly the manifest-declarable safety capabilities URML's validator can reason about at static-verification time.

PAL's posture is open ROS 2 software (Apache-2.0) on a proprietary hardware platform. The URML adapter consumes the open software surface without proposing changes to the proprietary hardware. PAL is Spain-domiciled (Barcelona); URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) passes at the manifest level for the EU origin without organisational override on PAL specifically.

## Detailed design

URML's existing artifacts that feed into a PAL adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/research/`](../../spec/profiles/research/) ([RFC-0012](0012-research-profile.md)): the natural home for TIAGo in academic deployments.
- [`spec/profiles/industrial/`](../../spec/profiles/industrial/) plus [RFC-0013](0013-industrial-layer2-primitives.md): the `pick_from` / `place_at` / `swap_tool` extensions TIAGo Pro can exercise.
- [RFC-0009](0009-legged-humanoid-mobility.md): TIAGo Pro Head is a humanoid-class upper body on a wheeled base; the capability surface applies.
- [RFC-0010](0010-whole-body-bimanual-manipulation.md) (Draft): the whole-body and bimanual primitives that TIAGo Pro could exercise.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the arm sibling adapter family.
- [`reference/mobile-runtime/`](../../reference/mobile-runtime/): the mobile-base sibling adapter family.
- [`reference/humanoid-runtime/`](../../reference/humanoid-runtime/): the humanoid sibling adapter family (TIAGo Pro Head fits here).
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference.

### Proposed `PalAdapter` family shape

One adapter family, three concrete adapters. Package layout:

```
reference/pal-runtime/src/pal_runtime/
├── __init__.py
├── adapter_pmb2.py          # PMB2 mobile base
├── adapter_tiago.py         # TIAGo single-arm mobile manipulator
├── adapter_tiago_pro.py     # TIAGo Pro dual-arm + head
├── common.py                # shared PAL ROS 2 helpers
└── manifests/
    ├── pal_pmb2.yaml
    ├── pal_tiago_steel.yaml
    ├── pal_tiago_iron.yaml
    ├── pal_tiago_titanium.yaml
    ├── pal_tiago_pro.yaml
    └── pal_tiago_pro_head.yaml
```

Each adapter implements URML's substrate Protocol. The mobile-base adapter dispatches to `/cmd_vel` and Nav2 goal-pose topics; the mobile-manipulator adapters dispatch to both the base and the arm action servers; the TIAGo Pro adapter additionally exposes the head-pan-and-tilt surface as URML `measure` and `wait_for` event topics.

### Proposed URML v0.1 to PAL mapping

| URML primitive | PMB2 (base) | TIAGo (single-arm) | TIAGo Pro (dual-arm + head) |
|---|---|---|---|
| `move_to(pose)` | `geometry_msgs/Twist` on `/cmd_vel`, Nav2 goal-pose where loaded. | Base `move_to` for chassis pose; arm `move_to` for end-effector pose via the published joint-trajectory action. | Per-arm `move_to` via `arm_left` / `arm_right` action servers; chassis `move_to` via base topic. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable; manifest declares no gripper. | Gripper service on the arm's gripper topic. | Per-arm gripper service. The bimanual coordination of grasps is a Layer-3 composition. |
| `measure(sensor_id)` | LIDAR, IMU, optional depth camera. | Plus joint-state on the arm, plus force-torque sensor (TIAGo Iron / Titanium variants). | Plus head-mounted camera, plus per-arm wrist sensors, plus the published whole-body state. |
| `wait_for(...)` | ROS 2 subscriber with debounce. | Same. | Same. |
| `report(status)` | `/urml/<adapter>/report` topic. | Same. | Same. |
| `pick_from(source)` / `place_at(destination)` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Not applicable. | Layer-3 composition over `move_to` plus `grasp` / `release`. | Per-arm composition; bimanual `pick_from` raised as an open question pending [RFC-0010 (Whole-body bimanual manipulation)](0010-whole-body-bimanual-manipulation.md). |
| `swap_tool(tool_id)` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Not applicable. | Composes onto a tool-changer add-on if present. | Same per-arm, gated on hardware. |

### Proposed capability manifest

Per-platform manifests under `reference/pal-runtime/src/pal_runtime/manifests/`. A condensed shape for `pal_tiago_pro`:

```yaml
brand: pal_tiago_pro
profile: research
mobility: wheeled_differential
mass_kg: 75.0
payload_kg: 5.0
manipulator:
  arms:
    - id: arm_left
      dof: 7
      reach_m: 0.92
      payload_kg: 3.0
      gripper: pal_gripper
    - id: arm_right
      dof: 7
      reach_m: 0.92
      payload_kg: 3.0
      gripper: pal_gripper
  whole_body: true
  series_elastic_actuator: true
transport: ros2
ros2:
  package: pal-robotics/tiago_pro_robot
  base_cmd_vel_topic: /mobile_base_controller/cmd_vel
  arm_left_action: /arm_left_controller/follow_joint_trajectory
  arm_right_action: /arm_right_controller/follow_joint_trajectory
  moveit_compatible: true
sensors:
  - lidar_2d
  - rgbd_camera_head
  - imu_6dof
  - wrist_force_torque_per_arm
safety:
  brake_rated: true
  iso_collaborative: pending_per_deployment
provenance:
  origin: ES
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `safety.brake_rated: true` field is the new addition URML's validator can use: when a program requires a brake-rated manifest (e.g., for a human-collaborative task), URML rejects manifests without it. This is the right shape but [RFC-0014 (Substrate conformance)](0014-substrate-conformance.md) needs to pin the safety field semantics before the validator surfaces them. The RFC raises this as an open question rather than proposing the spec change here.

### Proposed conformance integration

A `URML_PAL_INTEGRATION=1` env-gated CI workflow installs the PAL Robotics ROS 2 packages, runs each platform's adapter against a hermetic mock that replays joint-state and action-result responses, and asserts that the emitted commands match per-platform golden traces. The in-tree conformance suite continues to use `MockROSAdapter`.

### Cross-link to whole-body and bimanual primitives

[RFC-0010 (Whole-body and bimanual manipulation)](0010-whole-body-bimanual-manipulation.md) is in Draft. TIAGo Pro is a natural target deployment for the bimanual primitives once that spec lands, joining [RFC-0047 (Allen Institute MolmoAct)](0047-allen-institute-molmoact.md) and [RFC-0056 (Stanford ALOHA)](0056-stanford-aloha.md) as outreach threads that raised the bimanual question. This RFC observes the alignment; the bimanual spec direction is a separate Spec RFC process.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none in this RFC. The `safety.brake_rated` proposed manifest field is flagged as an open question for a future spec RFC.
- Reference runtime: proposed new package `reference/pal-runtime/`. Not built in this PR. The RFC requests pal-robotics maintainer feedback first.
- Conformance suite: proposed new `pal-integration.yml` CI workflow and a `URML_PAL_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. PAL Robotics gains nothing yet; the adapter consumes the published Apache-2.0 ROS 2 packages without proposing changes to them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants pal-robotics input on the per-variant manifest split (TIAGo Steel / Iron / Titanium variants) and on the safety-field schema before shipping.
- **The bimanual primitive question is unresolved.** TIAGo Pro is the third URML outreach target after MolmoAct (RFC-0047) and ALOHA (RFC-0056) to raise the bimanual question without resolving it. The status quo is acceptable for this RFC, but the unresolved question is a real product limitation.
- **TIAGo variant proliferation.** TIAGo Steel, TIAGo Iron (force-controlled), TIAGo Titanium (force-controlled + premium components), TIAGo OMNI (omnidirectional base), TIAGo Pro (dual-arm), TIAGo Pro Head (with humanoid head); the variant tree is wide. Per-variant manifests give static-verification rigour but add maintenance cost; a parametric manifest with a `variant:` field would be lighter but less precise.
- **Per-deployment safety certification.** ISO collaborative-robot certification is per-deployment, not per-product, so the manifest can declare "brake_rated" honestly but not "certified" without the operator's contractor adding the certification context. URML's validator can surface this gap, but the responsibility boundary needs explicit user-facing copy.
- **PAL's commercial pricing.** TIAGo platforms are six-figure deployments. The audience for the URML adapter is academic and corporate research, not the maker / educator tier Move #3 targeted. This RFC sits closer to Move #1's industrial OEMs in audience than Move #3's $300 Bittle X.

## Alternatives considered

1. **Ship the adapter first, ask pal-robotics maintainers later.** Rejected. The variant-manifest split and the safety-field schema are observable choices worth maintainer input on.
2. **Target only TIAGo (single-arm) and skip TIAGo Pro.** Rejected. The dual-arm story is what makes PAL distinctive among URML's existing manipulator targets, and skipping it forfeits the bimanual-research alignment.
3. **Fold PAL into [RFC-0064 (Trossen Interbotix)](0064-trossen-interbotix-outreach.md) as another arm vendor.** Rejected. Interbotix is stationary; PAL is mobile + manipulator. Different mobility category, different audience.
4. **Wait for [RFC-0010 (Whole-body bimanual)](0010-whole-body-bimanual-manipulation.md) to land before opening outreach.** Rejected. The single-arm and per-arm-bimanual paths work without the whole-body spec. Waiting forfeits engagement timing.

## Prior art

- `pal-robotics` GitHub org (195 public repos, 332 followers, Apache-2.0 predominant): the upstream organisation.
- `pal-robotics/tiago_simulation` (97 stars): the canonical TIAGo simulation package.
- `pal-robotics/tiago_pro_robot`, `pal-robotics/tiago_pro_head_robot`: the TIAGo Pro packages.
- `pal-robotics/pal_mjlab`, `pal-robotics/pal_sea_arm`, `pal-robotics/pal_urdf_utils`: adjacent infrastructure.
- `pal-robotics/aruco_ros` (596 stars), `pal-robotics/backward_ros` (241 stars), `pal-robotics/realsense_gazebo_plugin` (226 stars): general ROS contributions that signal the team's ecosystem reach.
- PAL Robotics product page at `pal-robotics.com`.
- [RFC-0010](0010-whole-body-bimanual-manipulation.md): the whole-body and bimanual manipulation Spec RFC (Draft).
- [RFC-0014](0014-substrate-conformance.md): the substrate-conformance Spec RFC (Draft) that should pin the `safety.brake_rated` semantics.
- [RFC-0043](0043-boston-dynamics-spot-integration.md), [RFC-0049](0049-anybotics-anymal-integration.md): the legged-platform Move #1 follow-ons (different mobility).
- [RFC-0047](0047-allen-institute-molmoact.md), [RFC-0056](0056-stanford-aloha.md): the bimanual-question-raising Move #2 RFCs.
- [RFC-0064](0064-trossen-interbotix-outreach.md): the stationary-arm Move #3 RFC.

## Unresolved questions

Provisional pending pal-robotics maintainer feedback:

1. **Adapter home.** Should URML host the adapter under `reference/pal-runtime/` (URML-side), under a new repo in the `pal-robotics` org as a contributed example, or both?
2. **Variant manifest granularity.** Per-variant manifests (Steel / Iron / Titanium / OMNI / Pro / Pro Head) versus a single parametric `tiago` manifest with `variant:` field?
3. **Safety-field schema.** What is the right declarative shape for `safety.brake_rated`, `safety.iso_collaborative`, and related fields URML's validator can reason about, and how should the manifest distinguish per-platform capability from per-deployment certification?
4. **Bimanual coordination at the ROS 2 layer.** Is there a path for a `coordinate(arm_left, arm_right, ...)` Layer-2 primitive that targets TIAGo Pro's whole-body controller, or should bimanual coordination stay at the policy / behaviour-tree layer above URML?
5. **Whole-body controller cross-link.** TIAGo Pro Head's whole-body controller is one of the more mature commercial implementations. Is there interest in coordinating with URML's RFC-0010 spec work?
6. **Conformance lane.** Open to a URML conformance line in the TIAGo simulation README or PAL product documentation?
7. **Anything else.**

## Implementation note

RFC-0068 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/pal-runtime/` package follows in a later session, gated on pal-robotics maintainer feedback. Draft state. Fourth Move #4 RFC. Ledger entry in [`examples/lighthouses/outreach-move4.yaml`](../../examples/lighthouses/outreach-move4.yaml).

## Requested feedback (from pal-robotics maintainers)

1. Adapter home (URML repo, pal-robotics contributed example, both).
2. Variant manifest granularity.
3. Safety-field schema.
4. Bimanual primitive at the ROS 2 layer.
5. Whole-body controller cross-link.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`pal-robotics` org has 195 public repos and 332 followers (verified 2026-05-24). The most-active TIAGo platform repo is `tiago_simulation` at 97 stars; per-repo Issue / Discussion settings were not visible from the org landing page. URML's planned channel: open a single Issue on `pal-robotics/tiago_simulation` (or whichever TIAGo Pro repo the maintainers point to) labelled with the closest `enhancement` equivalent, pointing to this RFC, with optional cross-references on the dual-arm-specific repos if maintainers prefer to thread there.

URML's own public Discussions for the broader Move #4 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the fourth Move #4 RFC).
- [x] Motivation grounded in verified technical alignment (195 public repos under pal-robotics with Apache-2.0 predominant, TIAGo / TIAGo Pro / PMB2 product line, mature ROS 2 maintenance, ARUCO / Backward / RealSense Gazebo Plugin general contributions) plus the commercial-research mobile-manipulator positioning.
- [x] Detailed design uses verified repo names (`tiago_simulation`, `tiago_pro_robot`, `tiago_pro_head_robot`, `pal_mjlab`, `pal_sea_arm`, `pal_urdf_utils`).
- [x] At least one alternative considered (four are: ship-first, TIAGo-only, fold-into-Trossen, wait-for-RFC-0010).
- [x] Drawbacks are real (proposal-only, unresolved bimanual primitive, variant proliferation, per-deployment safety certification, commercial pricing).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The `safety.brake_rated` proposed manifest field is flagged as an open question for a separate Spec RFC, not proposed here.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of the `pal-robotics` GitHub org as of 2026-05-24.
- [x] Provenance row (`origin: ES`) recorded; US-federal default policy passes for the EU origin without override.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
