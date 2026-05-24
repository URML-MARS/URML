---
rfc: 0064
title: Trossen Robotics Interbotix integration, request for comment from Interbotix maintainers
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

# RFC-0064: Trossen Robotics Interbotix integration, request for comment from Interbotix maintainers

## Summary

URML does not yet ship an Interbotix integration. This RFC proposes a `InterbotixAdapter` under [`reference/cobot-runtime/`](../../reference/cobot-runtime/) that targets [`Interbotix/interbotix_ros_manipulators`](https://github.com/Interbotix/interbotix_ros_manipulators) (BSD-3-Clause, 181 stars at time of writing) plus the sibling `interbotix_ros_core` and `interbotix_ros_toolboxes`. The adapter routes URML Layer-2 primitive calls (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) and the industrial-profile primitives ([RFC-0013](0013-industrial-layer2-primitives.md): `pick_from`, `place_at`, `swap_tool`) onto the X-Series joint-trajectory action goals and gripper services across ROS 2 Humble, ROS 2 Rolling, and (legacy lane) ROS 1 Noetic. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the Interbotix maintainers.

This is the fourth Move #3 RFC. It pairs with [RFC-0061 (WLKATA)](0061-wlkata-outreach.md), [RFC-0062 (Petoi)](0062-petoi-bittle-outreach.md), and [RFC-0063 (Hiwonder)](0063-hiwonder-outreach.md). Move #3 targets the affordable / desktop / educational tier. Interbotix is the US-domiciled anchor of the four (Trossen Robotics is headquartered in Downers Grove, IL), which counter-balances the three Asia-domiciled siblings in this wave and aligns directly with URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) without flagging at the provenance check.

## Motivation

Interbotix sits where URML's educational, research, and US-federal-compliant lanes converge. The X-Series manipulators (PX100, PX150, RX150, RX200, WX200, WX250, WX250S, VX250, VX300, VX300S) are the de-facto research-arm population in US robotics curricula and in published research artifacts: Mobile ALOHA's four-arm bimanual rig uses ViperX 300 (VX300) units, the LeRobot SO-100 distribution channel passes through Trossen, and university curricula at Stanford, CMU, MIT, and Berkeley reference Interbotix hardware as the working assumption. URML's value-add at this layer is the substrate-neutral vocabulary that lets a program written against an Interbotix VX300S retarget to a UR3, a Franka, or a WLKATA Haro380 without source changes, with static validation as the safety boundary.

Three things make this RFC concrete rather than aspirational. First, `interbotix_ros_manipulators` is BSD-3-Clause, supports ROS 2 Humble and Rolling on the active lane plus ROS 2 Galactic and ROS 1 Noetic on a legacy lane, and exposes published joint-trajectory action goals plus per-arm gripper services. URML's existing ROS 2 substrate path already covers the dispatch surface. Second, the sibling repos `Interbotix/interbotix_ros_core` and `Interbotix/interbotix_ros_toolboxes` cover the lower-level Dynamixel-servo and U2D2-USB transport that the adapter does not need to wrap directly; the existing surfaces are sufficient. Third, the institutional cross-link to two URML Move #2 RFCs is material: [RFC-0040 (Hugging Face LeRobot)](0040-hugging-face-lerobot.md) covers the policy library distributed in part on Interbotix hardware, and [RFC-0056 (Stanford ALOHA)](0056-stanford-aloha.md) covers the upstream recording pipeline that runs on Interbotix arms.

Interbotix's posture is permissive open-source: BSD-3-Clause across the active repos, public Issue tracker (25 open issues at time of writing on `interbotix_ros_manipulators`), English-first documentation, and a published cross-ROS-version support matrix. URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. Interbotix does not compete with URML for the substrate-neutral vocabulary role. Interbotix is the hardware and the ROS driver. URML is the spec a program above the driver can target.

## Detailed design

URML's existing artifacts that feed into an Interbotix adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/research/`](../../spec/profiles/research/) ([RFC-0012](0012-research-profile.md)): the natural home for Interbotix arms in academic deployments.
- [`spec/profiles/educational/`](../../spec/profiles/educational/) ([RFC-0011](0011-educational-profile.md)): the secondary profile for classroom deployments.
- [`spec/profiles/industrial/`](../../spec/profiles/industrial/) plus [RFC-0013](0013-industrial-layer2-primitives.md): the `pick_from` / `place_at` / `swap_tool` extensions WX250S-class arms can exercise.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime that hosts arm-style adapters today (Franka, UR, SO-100). Interbotix joins this family directly.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference.

### Proposed `InterbotixAdapter` shape

One adapter, parameterised by arm model. Package layout:

```
reference/cobot-runtime/src/cobot_runtime/interbotix/
├── __init__.py
├── adapter.py             # InterbotixAdapter
├── x_series.py            # PX100/PX150/RX150/RX200/WX200/WX250/VX250/VX300/WX250S/VX300S profiles
├── ros2.py                # ROS 2 Humble + Rolling dispatch
├── ros1.py                # ROS 1 Noetic legacy dispatch (optional)
└── manifests/
    ├── interbotix_px100.yaml
    ├── interbotix_px150.yaml
    ├── interbotix_rx150.yaml
    ├── interbotix_rx200.yaml
    ├── interbotix_wx200.yaml
    ├── interbotix_wx250.yaml
    ├── interbotix_wx250s.yaml
    ├── interbotix_vx250.yaml
    ├── interbotix_vx300.yaml
    └── interbotix_vx300s.yaml
```

The adapter implements URML's substrate Protocol (the same one used by `MockROSAdapter` and the `FrankaAdapter`). The ROS 2 path is primary; ROS 1 Noetic is supported only for the legacy lane and can be excluded by build flag in URML deployments that no longer run ROS 1.

### Proposed URML v0.1 to Interbotix mapping

| URML primitive | Interbotix ROS 2 realisation |
|---|---|
| `move_to(pose)` | `JointTrajectory` action goal on the arm's published joint-trajectory action server (Cartesian goals via the Interbotix MoveIt configuration where loaded; joint goals direct otherwise). |
| `grasp(gripper_id)` | Gripper-close service on the arm's published gripper service (X-Series gripper is a finger-style gripper driven by a position command). |
| `release(gripper_id)` | Gripper-open service, same surface. |
| `measure(sensor_id)` | Subscribe to `/<arm_name>/joint_states` for one sample, or to any externally-published sensor topic the deployment has added. |
| `wait_for(event \| threshold \| signal)` | ROS 2 subscriber on the named event topic with a debounce, identical pattern to URML's other ROS 2 adapters. |
| `report(status)` | Publish to a URML-namespaced status topic (`/urml/<arm_name>/report`). |
| `pick_from(source)` / `place_at(destination)` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Layer-3 composition over `move_to` plus `grasp` / `release`. No new Protocol method. Validates only on arms with grippers (PX100, RX150, etc., per the manifest's `gripper:` field). |
| `swap_tool(tool_id)` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Composes onto the existing docking-goal path; applicable to tool-changer add-ons sold by Trossen or third parties. |

### Proposed capability manifest

Per-arm manifests under `reference/cobot-runtime/src/cobot_runtime/interbotix/manifests/`, following [RFC-0009](0009-legged-humanoid-mobility.md)'s capability-manifest schema and the industrial-profile extensions in [RFC-0013](0013-industrial-layer2-primitives.md). A condensed shape for the VX300S (the Mobile ALOHA arm):

```yaml
brand: interbotix_vx300s
profile: research
dof: 6
reach_m: 0.75
payload_kg: 0.75
transport: ros2
ros2:
  package: Interbotix/interbotix_ros_manipulators
  joint_trajectory_action: /vx300s/arm_controller/follow_joint_trajectory
  gripper_service: /vx300s/gripper/close
  moveit_compatible: true
gripper: finger_position
servo: dynamixel
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `provenance.origin: US` row is what differentiates this manifest from the other three Move #3 manifests. Trossen Robotics is US-domiciled; the arms ship from Illinois; the default US-federal policy ([RFC-0003](0003-us-alignment.md)) passes without organisational override. For procurement-sensitive deployments this is a meaningful property.

### Proposed conformance integration

A `URML_INTERBOTIX_INTEGRATION=1` env-gated CI workflow installs the Interbotix ROS 2 packages, runs `InterbotixAdapter` against a hermetic mock ROS 2 system that replays joint-state and action-result responses, and asserts that the emitted commands match per-arm golden traces. The in-tree conformance suite continues to use `MockROSAdapter`. A hardware-in-the-loop lane against a real Interbotix arm (the most likely target for first hardware validation is a WX250 or a VX300S given their academic presence) is out of scope for this RFC.

### Cross-link to RFC-0040 (LeRobot) and RFC-0056 (Stanford ALOHA)

A URML-conformant program emitted by a LeRobot policy ([RFC-0040](0040-hugging-face-lerobot.md)) and executed via `InterbotixAdapter` closes a loop URML's Move #2 outreach mapped but did not implement. Mobile ALOHA recordings on four VX300S arms ([RFC-0056](0056-stanford-aloha.md)) annotated with URML primitives become substrate-fungible training data: the same policy can be evaluated on a non-Interbotix substrate without retraining the joint-target layer. This RFC observes the alignment; the integration work is gated on the upstream feedback from the Move #2 threads.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/cobot-runtime/src/cobot_runtime/interbotix/`. Not built in this PR. The RFC requests Interbotix maintainer feedback first.
- Conformance suite: proposed new `interbotix-integration.yml` CI workflow and a `URML_INTERBOTIX_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. The Interbotix side gains nothing yet; the adapter consumes the published ROS 2 packages without proposing changes to them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants Interbotix input on per-arm vs. parametric manifest granularity (Q1 below) and on the gripper-variant surface across the X-Series before shipping, because those choices have curriculum-visible consequences.
- **Per-arm manifests are numerous.** Ten X-Series arms is ten manifests. The kinematic and payload differences are real, so a single parametric manifest would forfeit static-verification rigour; the duplication is honest cost.
- **Gripper variation across the X-Series adds surface.** The PX-class arms have a finger-position gripper; the WX250S has a larger gripper with different payload limits; some research deployments swap in custom end-effectors. The `gripper:` field needs to cover the variation cleanly.
- **ROS 1 Noetic legacy lane is a maintenance commitment.** Interbotix still publishes ROS 1 Noetic packages alongside ROS 2 Humble. URML's adapter can omit the ROS 1 lane and target ROS 2 only, but the choice forfeits the curriculum still running on Noetic. The trade-off is worth maintainer input.
- **Bimanual coordination remains an open question.** Mobile ALOHA uses four VX300S arms coordinated through ALOHA's recording stack, not through Interbotix's ROS 2 layer. URML's Layer-2 vocabulary does not yet have a bimanual-coordination primitive ([RFC-0047](0047-allen-institute-molmoact.md) and [RFC-0056](0056-stanford-aloha.md) both raise this). The Interbotix adapter inherits the open question.

## Alternatives considered

1. **Ship the adapter first, ask Interbotix maintainers later.** Rejected. The per-arm manifest split (Q1) and the gripper-variant surface (Q3) are observable choices worth maintainer input on.
2. **Cover only the VX300S (the ALOHA arm) and skip the other nine X-Series models.** Rejected. The cross-curriculum value of supporting the PX100 (the most-bought entry arm in undergraduate courses) and the WX250S (the most-bought research arm outside Mobile ALOHA) is too high. The implementation can start with VX300S, but the RFC scope stays wide.
3. **Fold Interbotix into [RFC-0040 (LeRobot)](0040-hugging-face-lerobot.md) as a sub-section instead of a standalone RFC.** Rejected. The audiences and engagement surfaces are different; the LeRobot maintainers are not the Interbotix maintainers.
4. **Skip Interbotix in Move #3 and route through Trossen's commercial channel later.** Rejected. The open-source surface is exactly the surface URML's outreach pattern is designed for; routing through commercial would forfeit the standard's neutrality posture.

## Prior art

- `Interbotix/interbotix_ros_manipulators`: the upstream manipulator package (BSD-3-Clause, 181 stars, 25 open issues, ROS 1 Noetic + ROS 2 Galactic / Humble / Rolling, verified 2026-05-24).
- `Interbotix/interbotix_ros_core`: the lower-level Dynamixel-and-transport package.
- `Interbotix/interbotix_ros_toolboxes`: the higher-level utilities and demo applications.
- The X-Series product page at `trossenrobotics.com`: the canonical hardware catalogue.
- Mobile ALOHA paper (2401.02117) and the four-arm VX300S configuration that drove the ALOHA hardware standard.
- [RFC-0009](0009-legged-humanoid-mobility.md): the capability-manifest schema.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): the profiles this RFC targets.
- [RFC-0013](0013-industrial-layer2-primitives.md): the industrial-profile primitives.
- [RFC-0040](0040-hugging-face-lerobot.md): the LeRobot RFC; cross-links via SO-100 distribution and policy hosting.
- [RFC-0056](0056-stanford-aloha.md): the Stanford ALOHA RFC; cross-links via the VX300S four-arm Mobile ALOHA configuration.
- [RFC-0061](0061-wlkata-outreach.md), [RFC-0062](0062-petoi-bittle-outreach.md), [RFC-0063](0063-hiwonder-outreach.md): the parallel Move #3 RFCs.

## Unresolved questions

Provisional pending Interbotix maintainer feedback:

1. **Per-arm vs. parametric manifests.** Is one manifest per X-Series arm the right granularity, or would Interbotix prefer a single parametric `interbotix_x_series` manifest with a `model:` field?
2. **ROS 1 Noetic legacy lane.** Should URML's adapter cover ROS 1 Noetic on the legacy lane, or target ROS 2 only?
3. **Gripper-variant surface.** The X-Series gripper covers several variants (finger-position, custom end-effectors); is the `gripper:` field's single-value design sufficient, or does Interbotix recommend a richer schema?
4. **Adapter home.** Should URML host the adapter under `reference/cobot-runtime/` (URML-side), under a new repo in the `Interbotix` GitHub org as a contributed example, or both?
5. **Bimanual coordination.** Mobile ALOHA coordinates four VX300S arms via ALOHA's recording stack. Does Interbotix see a path for a `coordinate(arm0, arm1, ...)` Layer-2 primitive at the ROS 2 layer, or does coordination naturally stay at the recording / policy layer?
6. **Conformance lane.** Would Interbotix be open to a URML conformance lane published on the `interbotix_ros_manipulators` README or in the X-Series documentation?
7. **Anything else.**

## Implementation note

RFC-0064 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/cobot-runtime/src/cobot_runtime/interbotix/` package follows in a later session, gated on Interbotix maintainer feedback. Draft state. Fourth Move #3 RFC; closes the Move #3 pilot batch. Ledger entry in [`examples/lighthouses/outreach-move3.yaml`](../../examples/lighthouses/outreach-move3.yaml).

## Requested feedback (from Interbotix maintainers)

1. Manifest granularity (per-arm or parametric).
2. ROS 1 Noetic legacy coverage.
3. Gripper-variant schema.
4. Adapter home (URML repo, Interbotix contributed example, both).
5. Bimanual coordination at the ROS 2 layer.
6. Conformance-lane interest on the package README or X-Series documentation.
7. Anything else.

## How to respond

The `Interbotix/interbotix_ros_manipulators` repo has Issues enabled (25 open at time of writing); Discussions status was not visible on the repo page (verified 2026-05-24). The repo's build-status matrix is the most active surface (ROS Noetic, Galactic, Humble, Rolling are all built per push). URML's planned channel: open a single Issue on `Interbotix/interbotix_ros_manipulators` labelled with the closest `enhancement` or `feature` equivalent, pointing to this RFC, with optional cross-references on `interbotix_ros_core` and `interbotix_ros_toolboxes` if the maintainers prefer to thread there.

URML's own public Discussions for the broader Move #3 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the fourth Move #3 RFC closing the pilot batch).
- [x] Motivation grounded in verified technical alignment (BSD-3-Clause `interbotix_ros_manipulators` at 181 stars supporting ROS 2 Humble + Rolling + legacy ROS 1 Noetic, the sibling `interbotix_ros_core` and `interbotix_ros_toolboxes`, the academic-curriculum presence including Mobile ALOHA's four VX300S configuration) plus the US-domiciled provenance positioning.
- [x] Detailed design uses verified repo names (`Interbotix/interbotix_ros_manipulators`, `Interbotix/interbotix_ros_core`, `Interbotix/interbotix_ros_toolboxes`) and adapter-Protocol shape consistent with `reference/cobot-runtime/`.
- [x] At least one alternative considered (four are: ship-first, VX300S-only, fold-into-LeRobot, route-via-commercial).
- [x] Drawbacks are real (proposal-only, per-arm manifest proliferation, gripper-variant surface, ROS 1 legacy commitment, bimanual coordination open question).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The mapping uses the existing vocabulary plus the industrial-profile extensions from RFC-0013; the bimanual question is raised but not resolved here.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of `Interbotix/interbotix_ros_manipulators` as of 2026-05-24; the channel choice is honest about Discussions visibility.
- [x] Provenance row (`origin: US`) recorded honestly; the cross-Move-3 contrast with the three Asia-domiciled siblings made explicit.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
