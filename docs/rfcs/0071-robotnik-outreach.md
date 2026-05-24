---
rfc: 0071
title: Robotnik Automation integration, request for comment from RobotnikAutomation maintainers
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

# RFC-0071: Robotnik Automation integration, request for comment from RobotnikAutomation maintainers

## Summary

URML does not yet ship a Robotnik integration. This RFC proposes a `RobotnikAdapter` family under [`reference/mobile-runtime/`](../../reference/mobile-runtime/) targeting the [`RobotnikAutomation` GitHub org](https://github.com/RobotnikAutomation) (456 public repos, BSD-3-Clause / Apache-2.0 / MIT mix). The adapter routes URML Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) and the industrial-profile extensions ([RFC-0013](0013-industrial-layer2-primitives.md): `pick_from`, `place_at`, `swap_tool`) onto the published Summit XL, RB-1, RB-VOGUI, AGVS, and rbcar ROS 2 packages. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the RobotnikAutomation maintainers.

This is the first **Move #5** RFC. Move #5 promotes the Tier 2 parked candidates from URML's Move #4 adjacent-niches research plus one mid-plan addition (DEEP Robotics, RFC-0074). Robotnik is the European commercial-mobile-robotics anchor: a Spanish vendor with a 456-repo GitHub footprint and mature ROS 2 ecosystem alongside Move #4's PAL Robotics ([RFC-0068](0068-pal-robotics-outreach.md)).

## Motivation

Robotnik fills a distinctive position in URML's outreach landscape between Move #4's PAL Robotics (commercial mobile manipulator, Spain) and Move #4's AgileX Robotics ([RFC-0066](0066-agilex-outreach.md), research-grade mobile bases, China). Robotnik makes commercial industrial mobile robots (Summit XL series, RB-1, RB-VOGUI, AGVS) that ship to research labs, factories, and inspection deployments across Europe and globally. The platforms are ROS 2 native, BSD-3-Clause licensed at the simulation and driver layer, and have been a fixture in the ROS ecosystem since the early 2010s.

Three things make this RFC concrete rather than aspirational. First, the `RobotnikAutomation` GitHub org publishes 456 public repos with 161 followers (verified 2026-05-24). The top-starred repos directly cover the platform line: `agvs` (195 stars, "ROS package for the robot AGVS, intended for indoor transportation tasks"), `summit_xl_sim` (79 stars, Summit XL / Summit XL HL / Summit-X simulation), `summit_xl_common` (79 stars, URDF descriptions and platform messages), `rbcar_sim` (61 stars), `robotnik_simulation` (57 stars). License pattern: BSD-3-Clause predominant. Second, Robotnik's customer base includes academic-research deployments at scale across Europe; the URML conformance lane would land on a population already running ROS 2 on Robotnik substrates. Third, the institutional cross-link with PAL Robotics ([RFC-0068](0068-pal-robotics-outreach.md)) closes the European-commercial-mobile-manipulator pair: both Spanish (PAL Barcelona, Robotnik Valencia), both ROS 2 native, both targeting the research and commercial deployment tiers above Move #3's affordable consumer hardware.

Robotnik's posture is open ROS 2 software (BSD-3-Clause predominant) on proprietary hardware. URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. The URML adapter consumes the published software surface without proposing changes to the proprietary hardware. Robotnik is Spain-domiciled (Valencia); URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) passes at the manifest level for the EU origin without organisational override.

## Detailed design

URML's existing artifacts that feed into a Robotnik adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/research/`](../../spec/profiles/research/) ([RFC-0012](0012-research-profile.md)): the natural home for Robotnik platforms in academic deployments.
- [`spec/profiles/industrial/`](../../spec/profiles/industrial/) plus [RFC-0013](0013-industrial-layer2-primitives.md): the industrial-profile extensions for mobile-manipulator configurations (Summit XL plus arm).
- [`spec/profiles/warehouse/`](../../spec/profiles/warehouse/) ([RFC-0022](0022-warehouse-domain-profile.md), Draft): the AGVS use case directly.
- [`reference/mobile-runtime/`](../../reference/mobile-runtime/): the runtime that hosts wheeled-base adapters today (alongside the Move #4 AgileX sub-package).
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference.

### Proposed `RobotnikAdapter` family shape

One adapter family, several concrete adapters parameterised by platform. Package layout:

```
reference/mobile-runtime/src/mobile_runtime/robotnik/
├── __init__.py
├── adapter_summit_xl.py        # Summit XL / Summit XL HL / Summit-X
├── adapter_rb1.py              # RB-1 mobile manipulator
├── adapter_rb_vogui.py         # RB-VOGUI omnidirectional
├── adapter_agvs.py             # AGVS warehouse AGV
├── adapter_rbcar.py            # rbcar Ackermann research platform
├── common.py                   # shared Robotnik ROS 2 helpers
└── manifests/
    ├── robotnik_summit_xl.yaml
    ├── robotnik_summit_xl_hl.yaml
    ├── robotnik_summit_x.yaml
    ├── robotnik_rb1.yaml
    ├── robotnik_rb_vogui.yaml
    ├── robotnik_agvs.yaml
    └── robotnik_rbcar.yaml
```

Each adapter implements URML's substrate Protocol against the platform-specific ROS 2 topic shape (Summit XL is differential / skid-steer; RB-VOGUI is omnidirectional; rbcar is Ackermann; AGVS is differential warehouse-class).

### Proposed URML v0.1 to Robotnik mapping

| URML primitive | Robotnik ROS 2 realisation |
|---|---|
| `move_to(pose)` | `geometry_msgs/Twist` on `/cmd_vel` direct drive, or Nav2 goal-pose on `/goal_pose` where the navigation stack is loaded. Per-platform kinematic constraints enforced by URML's static verifier from the manifest. |
| `grasp(gripper_id)` / `release(gripper_id)` | If the manifest declares a mounted arm (e.g., Summit XL plus UR5 or Franka), gripper service on that arm's gripper topic. Not applicable on the pure mobile-base manifests. |
| `measure(sensor_id)` | LIDAR (Hokuyo or SICK, both already URML targets per Move #1), IMU, optional depth camera. Per-platform sensor inventory in the manifest. |
| `wait_for(...)` | ROS 2 subscriber with debounce, identical pattern to URML's other ROS 2 adapters. |
| `report(status)` | Publish to `/urml/<adapter>/report`. |
| `pick_from` / `place_at` / `swap_tool` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Layer-3 composition over `move_to` plus `grasp` / `release`, gated on a mounted-arm manifest declaration. |

### Proposed capability manifest

A condensed shape for `robotnik_summit_xl`:

```yaml
brand: robotnik_summit_xl
profile: research
mobility: wheeled_skid_steer
mass_kg: 65.0
payload_kg: 65.0
transport: ros2
ros2:
  package: RobotnikAutomation/summit_xl_common
  cmd_vel_topic: /summit_xl/cmd_vel
  scan_topic: /summit_xl/scan
  nav2_compatible: true
sensors:
  - lidar_2d_hokuyo
  - imu_6dof
  - depth_camera_optional
gripper: none
mounted_arm_optional:
  - ur5
  - franka_panda
provenance:
  origin: ES
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `mounted_arm_optional` field is the new shape: Summit XL ships as a pure base or with an arm bolted on (UR or Franka most commonly). The URML manifest declares the slot; the deploying organisation composes the mobile manifest with an arm manifest (already shipping in `reference/cobot-runtime/` per Move #1). The static verifier reasons about the composite at validation time.

### Proposed conformance integration

A `URML_ROBOTNIK_INTEGRATION=1` env-gated CI workflow installs the Robotnik ROS 2 packages, runs each platform's adapter against a hermetic mock, and asserts emitted commands match per-platform golden traces. The in-tree conformance suite continues to use `MockROSAdapter`.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none. The `mounted_arm_optional` field uses the existing manifest composition surface.
- Reference runtime: proposed new sub-package `reference/mobile-runtime/src/mobile_runtime/robotnik/`. Not built in this PR.
- Conformance suite: proposed new `robotnik-integration.yml` CI workflow and a `URML_ROBOTNIK_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. Robotnik gains nothing yet; the adapter consumes the published BSD-3-Clause ROS 2 packages without proposing changes.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants RobotnikAutomation input on the per-platform manifest split and on the mounted-arm composition design before shipping.
- **456-repo org is hard to navigate.** Robotnik's GitHub footprint is one of the largest of any URML outreach target. The RFC's per-platform repo pointers are best-effort; the maintainers' canonical recommendation for which repos are first-class would help.
- **Per-platform proliferation.** Summit XL alone has three variants (Summit XL / XL HL / X). RB-1, RB-VOGUI, AGVS, rbcar each earn their own manifest. Seven base manifests plus arm composition adds maintenance cost.
- **Mounted-arm composition is novel.** URML's prior outreach has targeted base-only or arm-only manifests. Summit XL plus UR5 is the first composition where the customer expects URML to reason about the combined manifest. The composition surface needs documentation work that this RFC sketches but does not finish.

## Alternatives considered

1. **Ship the adapter first, ask RobotnikAutomation maintainers later.** Rejected. The per-platform manifest split and the mounted-arm composition design are observable choices.
2. **Cover only Summit XL and skip the rest.** Rejected. Summit XL is the most-cited Robotnik platform but the catalog breadth is the differentiator from Move #4's PAL and AgileX RFCs.
3. **Fold Robotnik into [RFC-0066 (AgileX)](0066-agilex-outreach.md) as another mobile-base vendor.** Rejected. Different audiences (Robotnik is commercial European industrial; AgileX is research-grade China-based) and different price tiers.
4. **Fold Robotnik into [RFC-0068 (PAL Robotics)](0068-pal-robotics-outreach.md) as another Spanish mobile-manipulator vendor.** Rejected. PAL is humanoid-tier ergonomics on a wheeled base; Robotnik is industrial-tier hardware. Different audiences.

## Prior art

- `RobotnikAutomation` GitHub org (456 public repos, 161 followers, BSD-3-Clause / Apache-2.0 / MIT mix).
- `RobotnikAutomation/agvs` (195 stars), `summit_xl_sim` (79 stars), `summit_xl_common` (79 stars), `rbcar_sim` (61 stars), `robotnik_simulation` (57 stars).
- Robotnik product page at `robotnik.eu`.
- [RFC-0066](0066-agilex-outreach.md), [RFC-0068](0068-pal-robotics-outreach.md): the Move #4 European-mobile-platform RFCs this RFC complements.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md), [RFC-0022](0022-warehouse-domain-profile.md) (Draft): the URML profiles this RFC's manifests target.
- [RFC-0013](0013-industrial-layer2-primitives.md): the industrial-profile primitives the mounted-arm composition exercises.

## Unresolved questions

Provisional pending RobotnikAutomation maintainer feedback:

1. **Adapter home.** Should URML host the adapter under `reference/mobile-runtime/src/mobile_runtime/robotnik/` (URML-side), under a new repo in the `RobotnikAutomation` org as a contributed example, or both?
2. **Canonical per-platform repos.** Could you confirm the canonical first-class repos for Summit XL, RB-1, RB-VOGUI, AGVS, and rbcar in your 456-repo org?
3. **Mounted-arm composition.** What is your recommended approach to URML composing a Summit-XL-base manifest with a UR5-arm manifest at validation time?
4. **AGVS warehouse-profile coordination.** Is there interest in coordinating with URML's RFC-0022 warehouse-profile draft on the AGVS use case?
5. **Per-platform variant manifests.** Per-variant manifests (Summit XL / XL HL / X) versus a parametric manifest with a `variant:` field?
6. **Conformance lane.** Open to a URML conformance line on the platform-repo READMEs or at `robotnik.eu`?
7. **Anything else.**

## Implementation note

RFC-0071 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/mobile-runtime/src/mobile_runtime/robotnik/` package follows in a later session, gated on RobotnikAutomation maintainer feedback. Draft state. First Move #5 RFC. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from RobotnikAutomation maintainers)

1. Adapter home (URML repo, RobotnikAutomation contributed example, both).
2. Canonical per-platform repos.
3. Mounted-arm composition design.
4. AGVS coordination with RFC-0022 warehouse profile.
5. Per-platform variant manifest granularity.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`RobotnikAutomation` GitHub org has 456 public repos and 161 followers (verified 2026-05-24). The most-active platform repo is `agvs` (195 stars). URML's planned channel: open a single Issue on the most-active Robotnik platform repo (`agvs` or `summit_xl_common`) labelled with the closest `enhancement` equivalent, pointing to this RFC. If maintainers prefer a different surface (a single umbrella repo, an email contact, the `robotnik.eu` feedback path), the thread will follow their preference.

URML's own public Discussions for the broader Move #5 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the first Move #5 RFC).
- [x] Motivation grounded in verified technical alignment (456-repo `RobotnikAutomation` org, agvs / summit_xl_sim / summit_xl_common / rbcar_sim / robotnik_simulation as top repos, BSD-3-Clause predominant, European commercial industrial-mobile-robotics positioning).
- [x] Detailed design uses verified repo names.
- [x] At least one alternative considered (four are: ship-first, Summit-XL-only, fold-into-AgileX, fold-into-PAL).
- [x] Drawbacks are real (proposal-only, 456-repo navigation, per-platform proliferation, mounted-arm composition novelty).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The `mounted_arm_optional` field uses existing manifest composition surface.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of the `RobotnikAutomation` GitHub org as of 2026-05-24.
- [x] Provenance row (`origin: ES`) recorded; US-federal default policy passes without override.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
