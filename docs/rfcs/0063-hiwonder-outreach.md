---
rfc: 0063
title: Hiwonder integration, request for comment from Hiwonder maintainers
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

# RFC-0063: Hiwonder integration, request for comment from Hiwonder maintainers

## Summary

URML does not yet ship a Hiwonder integration. This RFC proposes a `HiwonderAdapter` family under [`reference/cobot-runtime/`](../../reference/cobot-runtime/) and a parallel `reference/petoi-runtime/`-style mobile / quadruped family, both consuming the ROS 2 packages that Hiwonder publishes per platform: `MentorPi` (mobile AI base with Mecanum / Ackermann / tank chassis options), `PuppyPi` (compact quadruped), `JetRover` (Jetson-based mobile rover), `ROSPider` (hexapod), and the JetMax / DOFBOT educational arms. URML's Layer-2 primitives (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) map onto each platform's published ROS 2 topics and services without proposing changes to Hiwonder's stack. No spec change on URML's side. This RFC documents the proposed mapping per platform and requests review and feedback from the Hiwonder maintainers.

This is the third Move #3 RFC, paired with [RFC-0061 (WLKATA)](0061-wlkata-outreach.md) and [RFC-0062 (Petoi)](0062-petoi-bittle-outreach.md). Move #3 targets the affordable / desktop / educational tier. WLKATA covers desktop arms; Petoi covers hobby quadrupeds; Hiwonder covers the multi-platform educational catalog (arm, quadruped, mobile base, hexapod) in the $400 to $1k tier where most STEM and university curricula already sit.

## Motivation

Hiwonder is the broadest multi-platform vendor in the affordable / educational tier. The same brand sells a desktop arm, a quadruped, a Mecanum-wheeled mobile base, an Ackermann-steered rover, and a hexapod, with the same ROS 2-native software stack across all of them. For URML, that breadth is unique: one adapter family surfaces four URML mobility profiles (cobot, legged, wheeled, multi-legged) under one institutional contact. A teacher who buys a Hiwonder PuppyPi for a robotics elective can later add a JetMax arm or a JetRover mobile base and keep using URML's substrate-neutral primitives across the additions.

Three things make this RFC concrete rather than aspirational. First, Hiwonder publishes 36 public repos under the `Hiwonder` GitHub org with English documentation at `docs.hiwonder.com`. The pinned repos (`MentorPi`, `PuppyPi`, `JetRover`, `ROSPider`, `LeRobot` fork) all declare ROS 2 support and ship Python SDKs alongside. URML's existing ROS 2 substrate path already covers the dispatch surface. Second, the hardware spans the right platforms for URML's profile family: the Hiwonder catalog covers educational (RFC-0011), research (RFC-0012), and the legged / mobile mobility surfaces from RFC-0009. Third, Hiwonder maintains a public fork of LeRobot ([RFC-0040](0040-hugging-face-lerobot.md)'s upstream), so the cross-stack alignment with the AI/ML layer URML's Move #2 targets is already visible at Hiwonder's level.

Hiwonder's posture is open documentation and ROS-native software. The license surface across the org's repos was not fully visible from the public landing page (verified attempt 2026-05-24); URML's adapter assumes per-repo licenses and asks the maintainers to confirm. English docs and a Raspberry Pi 5 / Jetson Orin hardware ecosystem mean the deployment story is portable. URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation.

## Detailed design

URML's existing artifacts that feed into a Hiwonder adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/educational/`](../../spec/profiles/educational/) ([RFC-0011](0011-educational-profile.md)): the natural home for JetMax / DOFBOT / PuppyPi / ROSPider.
- [`spec/profiles/research/`](../../spec/profiles/research/) ([RFC-0012](0012-research-profile.md)): MentorPi / JetRover sit closer to this surface when used for SLAM or navigation research.
- [RFC-0009](0009-legged-humanoid-mobility.md): the legged-mobility capability surface PuppyPi and ROSPider declare against.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime that hosts the JetMax / DOFBOT arm adapters.
- A new `reference/hiwonder-runtime/` (or a `reference/mobile-base-runtime/` plus extensions) for the mobile and legged platforms. The placement is open.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference.

### Proposed adapter shape: one family, several adapters

The breadth of the Hiwonder catalog makes a single monolithic adapter the wrong shape. The proposal is a family of adapters under one runtime, parameterised by platform:

```
reference/hiwonder-runtime/src/hiwonder_runtime/
├── __init__.py
├── adapter_mentorpi.py    # MentorPi (mobile AI base, Mecanum/Ackermann/tank)
├── adapter_puppypi.py     # PuppyPi (quadruped)
├── adapter_jetrover.py    # JetRover (Jetson rover)
├── adapter_rospider.py    # ROSPider (hexapod)
├── adapter_jetmax.py      # JetMax (educational arm; cross-references cobot-runtime)
├── common.py              # shared ROS 2 helpers
└── manifests/
    ├── hiwonder_mentorpi_mecanum.yaml
    ├── hiwonder_mentorpi_ackermann.yaml
    ├── hiwonder_mentorpi_tank.yaml
    ├── hiwonder_puppypi.yaml
    ├── hiwonder_jetrover.yaml
    ├── hiwonder_rospider.yaml
    └── hiwonder_jetmax.yaml
```

Each adapter implements URML's substrate Protocol independently because the underlying ROS 2 topic shape differs per platform (joint-trajectory for the arm, twist for the wheeled bases, gait-skill for the legged platforms). The shared helpers in `common.py` cover the Hiwonder-conventional topic-naming, parameter-server defaults, and the Python-SDK wrappers Hiwonder ships alongside ROS 2.

### Proposed URML v0.1 to Hiwonder mapping (per platform)

The single primitive that crosses platforms differently is `move_to`. The other Layer-2 primitives map uniformly:

| URML primitive | Wheeled (MentorPi, JetRover) | Legged (PuppyPi, ROSPider) | Arm (JetMax) |
|---|---|---|---|
| `move_to(pose)` | `geometry_msgs/Twist` on `/cmd_vel` for direct drive; or a Nav2 goal pose on `/goal_pose` if the platform's stack is loaded. | A gait-skill token on the platform's published skill topic (PuppyPi follows the OpenCat-style pattern from [RFC-0062](0062-petoi-bittle-outreach.md); ROSPider has its own hexapod-gait set). | `JointTrajectory` action goal on the arm's published trajectory topic. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable; manifest declares no gripper. | Not applicable; manifest declares no gripper. | Gripper-close / open service call on the arm's gripper topic. |
| `measure(sensor_id)` | LIDAR scan, depth camera, IMU subscriber for one sample. | IMU, joint-state, optional ultrasonic. | Joint-state, force-torque (if equipped). |
| `wait_for(...)` | ROS 2 subscriber with a debounce. | Same pattern. | Same pattern. |
| `report(status)` | Publish to `/urml/<adapter>/report`. | Same. | Same. |
| `pick_from` / `place_at` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Not applicable. | Not applicable. | Layer-3 composition over arm primitives, no new Protocol method. |
| `swap_tool` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Not applicable. | Not applicable. | Composes onto the existing docking-goal path (`send_docking_goal`). |

### Proposed capability manifests

The MentorPi chassis variants get distinct manifests because the kinematic model differs (Mecanum: omnidirectional; Ackermann: differential-with-steering-constraint; tank: differential). A condensed shape for `hiwonder_mentorpi_mecanum`:

```yaml
brand: hiwonder_mentorpi_mecanum
profile: research
mobility: wheeled_mecanum
chassis: mecanum
mass_kg: 4.5
payload_kg: 2.0
transport: ros2
ros2:
  package: Hiwonder/MentorPi
  cmd_vel_topic: /cmd_vel
  scan_topic: /scan
  nav2_compatible: true
sensors:
  - lidar_2d
  - depth_camera
  - imu_6dof
gripper: none
controller: raspberry_pi_5_plus_stm32
provenance:
  origin: CN
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The legged-platform manifests for PuppyPi and ROSPider declare `mobility: legged_quadruped` and `mobility: legged_hexapod` respectively, with platform-specific gait inventories. The provenance row mirrors the pattern in RFC-0061 / RFC-0062: honest origin disclosure, with the policy decision delegated to the operator's policy file per [RFC-0004](0004-compliance-policy.md).

### Proposed conformance integration

A `URML_HIWONDER_INTEGRATION=1` env-gated CI workflow installs the ROS 2 packages from the Hiwonder org, runs each platform's adapter against a hermetic mock, and asserts that the emitted commands match per-platform golden traces. The in-tree conformance suite continues to use `MockROSAdapter`. Hardware-in-the-loop against real Hiwonder hardware is out of scope for this RFC.

### Cross-platform classroom lane

Because Hiwonder's catalog spans the arm / quadruped / mobile / hexapod surface under one brand, URML's most distinctive contribution to a Hiwonder-equipped classroom is the substrate-fungibility of programs above the gripper-and-mobility line. A `move_to` and `wait_for` sequence written for a MentorPi reads almost verbatim on a JetRover; a posture-sequence written for a PuppyPi adapts to a ROSPider with a gait-vocabulary substitution. URML's existing profile system surfaces this directly. This RFC observes the alignment; it does not propose new profile primitives.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new package `reference/hiwonder-runtime/`. Not built in this PR. The RFC requests Hiwonder maintainer feedback first.
- Conformance suite: proposed new `hiwonder-integration.yml` CI workflow and a `URML_HIWONDER_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. The Hiwonder side gains nothing yet; the adapter consumes the published ROS 2 packages without proposing changes to them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants Hiwonder input on which platforms to prioritise (Q1 below) and on the per-platform manifest split before shipping, because the catalog's breadth makes "all of them at once" expensive to maintain.
- **Catalog breadth is also catalog drift risk.** Hiwonder ships platforms regularly. The URML adapter family takes on per-platform maintenance burden in proportion to the catalog's growth, and pinning the supported platforms keeps the test matrix tractable.
- **License visibility was incomplete on the org landing page.** URML's adapter assumes per-repo licenses; the RFC asks the maintainers to confirm the license surface across `MentorPi`, `PuppyPi`, `JetRover`, `ROSPider`, and `JetMax`.
- **Star counts at the time of writing are small.** The most-pinned `MentorPi` is at 13 stars (verified 2026-05-24). URML's outreach reach via Hiwonder's GitHub audience is small; the larger reach is through Hiwonder's commercial channel and `docs.hiwonder.com`, not through repo stars.
- **The Mecanum / Ackermann / tank chassis variation triples the MentorPi manifest count.** This is honest but adds maintenance cost. The alternative (one parametric manifest with a `chassis:` field) loses the static-verification benefit of declaring the kinematic constraint at manifest-load time.

## Alternatives considered

1. **Ship the adapter for one platform (PuppyPi) first, defer the rest.** Rejected for this RFC, but the cross-link to [RFC-0062 (Petoi)](0062-petoi-bittle-outreach.md) suggests PuppyPi might be the right first cut in implementation; the RFC keeps the scope wide and lets the implementation order be a separate decision.
2. **Fold Hiwonder into a generic "multi-vendor educational catalog" RFC alongside other catalog vendors (Yahboom, Elephant Robotics XGO).** Rejected. The vendors have different SDK shapes; collapsing them obscures the per-vendor mapping discipline.
3. **Skip per-chassis manifests on MentorPi; ship one parametric manifest with a `chassis:` field.** Rejected. The kinematic constraint matters at validation time. A `move_to` with a non-zero lateral component is valid on Mecanum and invalid on Ackermann; the static verifier needs to know.
4. **Target only the JetMax arm (closest to WLKATA's surface) and skip the mobile / legged platforms.** Rejected. The catalog breadth is the most distinctive feature of Hiwonder for URML, and surfacing only the arm forfeits the cross-platform substrate-fungibility story.

## Prior art

- `Hiwonder/MentorPi`: the mobile-AI-robot platform (13 stars; English README; Raspberry Pi 5 + STM32; ROS 2 native; Python SDK).
- `Hiwonder/PuppyPi`: the quadruped platform (8 stars).
- `Hiwonder/JetRover`: the Jetson rover platform (5 stars).
- `Hiwonder/ROSPider`: the hexapod platform (2 stars).
- `Hiwonder/LeRobot`: the maintained fork of [RFC-0040](0040-hugging-face-lerobot.md)'s upstream, which signals existing engagement with the AI/ML layer URML's Move #2 RFCs target.
- `docs.hiwonder.com`: the English-language documentation surface.
- [RFC-0009](0009-legged-humanoid-mobility.md): the legged-mobility capability schema.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): the URML profiles this RFC targets.
- [RFC-0061](0061-wlkata-outreach.md), [RFC-0062](0062-petoi-bittle-outreach.md): the parallel Move #3 RFCs.

## Unresolved questions

Provisional pending Hiwonder maintainer feedback:

1. **Platform priority.** Which Hiwonder platform is the best first integration target from your perspective: MentorPi (broadest catalog), PuppyPi (legged-quadruped story), JetMax (arm), or JetRover (Jetson-class mobile)?
2. **Adapter home.** Should URML host the adapter family under `reference/hiwonder-runtime/` (URML-side), under a new repo in the `Hiwonder` GitHub org as a contributed example, or both?
3. **License clarification.** Could you confirm the licenses on `MentorPi`, `PuppyPi`, `JetRover`, `ROSPider`, and `JetMax`?
4. **MentorPi chassis manifests.** Per-chassis manifests (Mecanum / Ackermann / tank) versus a single parametric manifest with a `chassis:` field?
5. **`Hiwonder/LeRobot` cross-link.** Is there interest in coordinating the URML integration with the LeRobot fork, given URML's open RFC-0040 outreach to upstream LeRobot?
6. **Conformance lane.** Would Hiwonder be open to a URML conformance line on `docs.hiwonder.com` or in the platform-repo READMEs?
7. **Anything else.**

## Implementation note

RFC-0063 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/hiwonder-runtime/` package follows in a later session, gated on Hiwonder maintainer feedback. Draft state. Third Move #3 RFC. Ledger entry in [`examples/lighthouses/outreach-move3.yaml`](../../examples/lighthouses/outreach-move3.yaml).

## Requested feedback (from Hiwonder maintainers)

1. Platform priority (MentorPi / PuppyPi / JetMax / JetRover / other).
2. Adapter home (URML repo, Hiwonder contributed example, both).
3. License confirmation across the pinned repos.
4. MentorPi chassis manifests (per-chassis or parametric).
5. `Hiwonder/LeRobot` cross-link interest.
6. Conformance-lane interest on the docs site or in repo READMEs.
7. Anything else.

## How to respond

The `Hiwonder` GitHub org has 36 public repos and 213 followers (verified 2026-05-24). Per-repo Issue and Discussion settings were not visible from the org landing page, so URML's planned channel is to open a single Issue on the most-active pinned repo (`MentorPi`) labelled with the closest available `enhancement` or `feature` equivalent, pointing to this RFC. If Hiwonder maintainers prefer a different surface (a single umbrella discussion repo, an email contact, the `docs.hiwonder.com` feedback path), the thread will follow their preference.

URML's own public Discussions for the broader Move #3 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the third Move #3 RFC).
- [x] Motivation grounded in verified technical alignment (36 public repos in the Hiwonder org, ROS 2-native platforms across arm / quadruped / mobile / hexapod, English documentation at docs.hiwonder.com, maintained LeRobot fork) plus the catalog-breadth positioning.
- [x] Detailed design uses verified repo names (`MentorPi`, `PuppyPi`, `JetRover`, `ROSPider`, `JetMax`) and adapter-Protocol shape consistent with `reference/cobot-runtime/`.
- [x] At least one alternative considered (four are: PuppyPi-first, multi-vendor catalog fold-in, parametric manifest on MentorPi, arm-only).
- [x] Drawbacks are real (proposal-only, catalog drift risk, license visibility gap, small star counts, MentorPi chassis manifest proliferation).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The mapping uses the existing vocabulary; cross-platform fungibility is observed but does not require new primitives.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of the Hiwonder GitHub org as of 2026-05-24; the channel choice is honest about the gaps (per-repo Issue / Discussion visibility was incomplete).
- [x] Provenance row (`origin: CN`) recorded honestly per URML's discipline, with the policy-decision boundary made explicit.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
