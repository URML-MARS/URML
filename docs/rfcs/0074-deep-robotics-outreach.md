---
rfc: 0074
title: DEEP Robotics integration, request for comment from DeepRoboticsLab maintainers
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

# RFC-0074: DEEP Robotics integration, request for comment from DeepRoboticsLab maintainers

## Summary

URML does not yet ship a DEEP Robotics integration. This RFC proposes a `DeepRoboticsAdapter` family under [`reference/legged-runtime/`](../../reference/legged-runtime/) (or as an extension into a future `reference/wheeled-legged-runtime/`) targeting the [`DeepRoboticsLab` GitHub org](https://github.com/DeepRoboticsLab) (19 public repos, 624 followers, BSD-3-Clause / MIT / GPL-2.0 mix). The adapter routes URML Layer-2 primitives onto the published `Lite3_MotionSDK` and `sdk_deploy` ROS 2 surfaces for the Lite3 and M20 quadrupeds today, with the **Lynx S10 wheeled-legged hybrid** (launched 2026-05-22) as a forward target pending SDK publication. No spec change on URML's side in this RFC, but the wheeled-legged mobility class is flagged as an **open question for a future Spec RFC**. This RFC documents the proposed mapping and requests review and feedback from the DeepRoboticsLab maintainers.

This is the fourth Move #5 RFC. DEEP Robotics introduces a **mobility class URML has not previously declared**: wheeled-legged hybrid. The Lynx S10 (16 joints, sub-20kg, 8 m/s, IP66, $1.4–$2.8k tier) is the first URML outreach target with this morphology.

## Motivation

The Lynx S10 launch (2026-05-22) is two days old at the time of this RFC's drafting. The platform is a wheeled-legged hybrid. Wheels for fast flat-ground locomotion, legs for stairs and obstacles. A class that exists in URML's adjacent landscape ([Boston Dynamics Stretch](0043-boston-dynamics-spot-integration.md) is similar but warehouse-only; ANYmal is pure-legged) but has never been the explicit target of URML's manifest schema. DEEP Robotics' broader product line (Lite3 mid-size quadruped at ~$3k tier, M20 industrial quadruped, X20 / X30 inspection-class) all run on the same DeepRoboticsLab SDK family, so a single URML adapter family covers the line and Lynx S10 falls into it once its SDK is published.

Three things make this RFC concrete rather than aspirational. First, the `DeepRoboticsLab` GitHub org has a mature SDK presence for the existing quadrupeds: `rl_training` (203 stars, Isaac Lab-based RL training), `Lite3_rl_deploy` (123 stars, sim-to-sim and sim-to-real for Lite3), `Lite3_MotionSDK` (86 stars, motion control SDK), `robotserver_sdk` (58 stars), `deep_robotics_model` (41 stars, URDF/MJCF/USD). License mix BSD-3-Clause / MIT / GPL-2.0; last commit on `rl_training` on 2026-05-13. Second, ROS 2 packages already exist (`Lite3_ROS`, `sdk_deploy` "ROS2 Version" supporting M20 and Lite3). Third, the **wheeled-legged mobility class is genuinely new** to URML's outreach landscape; capturing the engagement now while the Lynx S10 is fresh sets the standard before any other vocabulary anchors.

DEEP Robotics' posture is open SDK (BSD-3 / MIT predominant) on commercial hardware. URML's open-core commitment lands without translation. The company is Hangzhou-domiciled (China, founded 2017); URML's provenance discipline records `origin: CN` honestly, with the policy decision delegated to the operator's policy file per [RFC-0004](0004-compliance-policy.md).

## Detailed design

### Proposed `DeepRoboticsAdapter` family shape

```
reference/legged-runtime/src/legged_runtime/deep_robotics/
├── __init__.py
├── adapter_lite3.py            # Lite3 mid-size quadruped
├── adapter_m20.py              # M20 industrial quadruped
├── adapter_x20_x30.py          # X20 / X30 inspection-class (gated on SDK availability)
├── adapter_lynx_s10.py         # Lynx S10 wheeled-legged (SDK TBD)
├── common.py                   # shared DeepRoboticsLab helpers
└── manifests/
    ├── deep_robotics_lite3.yaml
    ├── deep_robotics_m20.yaml
    ├── deep_robotics_x20.yaml          # placeholder, gated on SDK
    ├── deep_robotics_x30.yaml          # placeholder, gated on SDK
    └── deep_robotics_lynx_s10.yaml     # placeholder, gated on SDK publication
```

The Lite3 and M20 adapters consume the existing `Lite3_MotionSDK` and `sdk_deploy` (ROS 2) surfaces today. The X20 / X30 / Lynx S10 adapters are placeholders pending SDK publication; the manifests document the platforms' specifications but the adapters do not ship until the upstream SDK is available.

### Proposed URML v0.1 to DEEP Robotics mapping (Lite3, M20)

| URML primitive | Lite3 / M20 realisation |
|---|---|
| `move_to(pose)` | A motion command via `Lite3_MotionSDK` (`SetMotionCommand`) or the equivalent ROS 2 topic in `sdk_deploy`. URML's pose maps to a gait + direction + duration tuple, mirroring the skill-library pattern from [RFC-0062 (Petoi)](0062-petoi-bittle-outreach.md) at a larger scale. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable on the stock quadruped (no gripper); manifest declares `gripper: none`. Future M20 deployments with mounted arms would compose a quadruped manifest with an arm manifest. |
| `measure(sensor_id)` | IMU, joint-state, optional LIDAR (`Hokuyo` or `Ouster` add-on, both URML-covered via Move #1 RFCs), depth camera. |
| `wait_for(...)` | ROS 2 subscriber or SDK polling with debounce. |
| `report(status)` | Publish to `/urml/<adapter>/report`. |

### Wheeled-legged mobility class. Open Spec question

URML's manifest schema ([RFC-0009](0009-legged-humanoid-mobility.md)) declares `mobility:` values: `wheeled_differential`, `wheeled_mecanum`, `wheeled_omnidirectional`, `wheeled_skid_steer`, `legged_bipedal`, `legged_quadruped`, `legged_hexapod`, etc. Lynx S10 is **wheeled-legged hybrid**. Wheels at the foot end of each leg, leg articulation for obstacle / stair traversal, wheel rolling for flat ground.

The right vocabulary value (`wheeled_legged_quadruped`? `hybrid_quadruped`? `legged_with_wheels`?) is a Spec RFC question, not an outreach question. RFC-0074 surfaces the gap and proposes the manifest field as `mobility: wheeled_legged_quadruped` provisionally; the spec direction is for a future Spec RFC.

### Proposed capability manifest (Lite3 example)

```yaml
brand: deep_robotics_lite3
profile: research
mobility: legged_quadruped
dof: 12
mass_kg: 12.0
payload_kg: 7.5
max_speed_m_s: 4.0
transport: [ros2, motion_sdk]
ros2:
  package: DeepRoboticsLab/sdk_deploy
  motion_topic: /lite3/motion_command
motion_sdk:
  cpp_lib: Lite3_MotionSDK
  python_wrapper: rl_training_helpers
sensors:
  - imu_6dof
  - joint_state
  - lidar_2d_optional
gripper: none
provenance:
  origin: CN
  ndaa_section_889_status: not_listed
  default_policy: pass
```

And for `deep_robotics_lynx_s10` (placeholder):

```yaml
brand: deep_robotics_lynx_s10
profile: research
mobility: wheeled_legged_quadruped  # provisional, pending Spec RFC
dof: 16
mass_kg: 19.5  # approximate, from launch announcement
payload_kg: 8.0  # effective; 120 kg max per spec
max_speed_m_s: 8.0
obstacle_clearance_cm: 50
ip_rating: IP66
operating_temperature_c: [-20, 55]
transport: tbd  # SDK not yet published
sensors:
  - lidar_2d_dual
  - rgb_camera_4x
  - imu_6dof
gripper: none
provenance:
  origin: CN
  ndaa_section_889_status: not_listed
  default_policy: pass
sdk_status: pending_publication_2026_05_22_launch
```

The `sdk_status: pending_publication_2026_05_22_launch` field is honest documentation: URML does not pretend to ship an adapter against an SDK that has not been published. The manifest is a forward-declaration so URML programs can target Lynx S10 specifications today, and the adapter activates when the SDK lands.

### Spec / validator / reference-runtime / conformance changes

- Spec: no change in this RFC. The wheeled-legged mobility-class addition to [RFC-0009](0009-legged-humanoid-mobility.md) is raised as an **open question for a future Spec RFC**, not proposed inline.
- Validator: provisional acceptance of `mobility: wheeled_legged_quadruped` until the spec resolves.
- Reference runtime: proposed new sub-package `reference/legged-runtime/src/legged_runtime/deep_robotics/`. Not built in this PR.
- Conformance suite: proposed new `deep-robotics-integration.yml` CI workflow and a `URML_DEEP_ROBOTICS_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. The wheeled-legged mobility value is provisional and will be reconciled with the future Spec RFC.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.**
- **Lynx S10 SDK not yet published.** The Lynx S10 portion of this RFC is forward-declared. The adapter activates only when the upstream SDK lands.
- **Wheeled-legged mobility class is provisional.** Until the Spec RFC resolves the vocabulary, the manifest's `mobility:` field uses a provisional value that future spec changes may rename.
- **`rl_training` repo has Issues disabled.** The most-starred DEEP Robotics repo is not the canonical engagement surface. URML must pick a sibling repo (likely `Lite3_MotionSDK` or `sdk_deploy`) for the outreach Issue.
- **Origin disclosure friction.** `origin: CN` is honest but triggers the US-federal default policy's per-deployment review. URML's posture: that decision belongs to the operator.

## Alternatives considered

1. **Ship the adapter first.** Rejected. Lynx S10 SDK not available, Spec RFC not authored.
2. **Skip Lynx S10 entirely and target only Lite3 / M20.** Rejected. Lynx S10 introduces a mobility class URML genuinely lacks; capturing it now is the right move even if the adapter waits.
3. **File the Spec RFC for wheeled-legged inline.** Rejected. The spec is a separate process, and conflating outreach with spec changes muddles the index.
4. **Wait for the Lynx S10 SDK to publish before opening any DEEP Robotics outreach.** Rejected. The Lite3 / M20 SDKs are sufficient to ship an initial adapter; delaying loses the institutional engagement timing.

## Prior art

- `DeepRoboticsLab` GitHub org (19 public repos, 624 followers, BSD-3-Clause / MIT / GPL-2.0 mix).
- `DeepRoboticsLab/rl_training` (203 stars, Isaac Lab-based), `Lite3_rl_deploy` (123 stars), `Lite3_MotionSDK` (86 stars), `robotserver_sdk` (58 stars), `deep_robotics_model` (41 stars).
- Lynx S10 launch announcement at deeprobotics.cn (2026-05-22).
- [RFC-0009](0009-legged-humanoid-mobility.md): the legged-mobility capability schema that needs extension for wheeled-legged.
- [RFC-0043](0043-boston-dynamics-spot-integration.md), [RFC-0049](0049-anybotics-anymal-integration.md): the Move #1 / #2 legged-quadruped RFCs.
- [RFC-0050](0050-nvidia-isaac-lab-integration.md): the Isaac Lab RFC; `rl_training` builds on Isaac Lab.

## Unresolved questions

1. **Lynx S10 SDK timeline.** When is the published SDK expected? URML's adapter waits.
2. **Adapter home.** URML repo or `DeepRoboticsLab` contributed example?
3. **Engagement Issue surface.** Best repo to file the outreach Issue on, given `rl_training` has Issues disabled? `Lite3_MotionSDK`? `sdk_deploy`?
4. **Wheeled-legged mobility class.** Vocabulary recommendation for URML's manifest schema?
5. **Isaac Lab cross-link.** `rl_training` is Isaac Lab-based; interest in coordinating with URML's open [RFC-0050](0050-nvidia-isaac-lab-integration.md) outreach?
6. **Conformance lane.** Open to a URML conformance line on `Lite3_MotionSDK` README or DEEP Robotics product documentation?
7. **Anything else.**

## Implementation note

RFC-0074 ships as a single RFC document PR. No adapter code in this PR. The Lynx S10 portion is forward-declared pending SDK publication. The wheeled-legged mobility-class Spec RFC is deferred to a separate process. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from DeepRoboticsLab maintainers)

1. Lynx S10 SDK timeline.
2. Adapter home.
3. Best Issue surface (`rl_training` Issues are disabled).
4. Wheeled-legged mobility-class vocabulary recommendation.
5. Isaac Lab cross-link with URML's RFC-0050.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`DeepRoboticsLab` org has 19 public repos and 624 followers (verified 2026-05-24). The most-starred repo `rl_training` (203 stars) has Issues DISABLED. Sibling repos with active Issue surfaces: `Lite3_MotionSDK` (86 stars), `sdk_deploy`, `Lite3_rl_deploy` (123 stars). URML's planned channel: open a single Issue on `DeepRoboticsLab/Lite3_MotionSDK` labelled with the closest `enhancement` equivalent, pointing to this RFC, with optional cross-reference on `Lite3_rl_deploy` if maintainers prefer to thread there.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary tells the proposal-only story, Move #5 framing, and the wheeled-legged-class flag.
- [x] Motivation grounded in verified `DeepRoboticsLab` org and Lynx S10 launch.
- [x] Detailed design uses verified repo names and explicit pending-SDK acknowledgement.
- [x] Wheeled-legged mobility-class question raised as **open Spec question**, not proposed inline.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (proposal-only, SDK pending, provisional vocabulary, `rl_training` Issues disabled, origin disclosure friction).
- [x] Backward compatibility additive; provisional vocabulary documented.
- [x] No Layer-2 primitive added. New `mobility:` vocabulary flagged for Spec RFC, not proposed.
- [x] Implementation note explicit.
- [x] Surface verified as of 2026-05-24; `rl_training` Issues-disabled noted; alternative Issue surface picked.
- [x] Provenance `origin: CN` recorded honestly.
- [x] CLAUDE.md compliance check passed.
