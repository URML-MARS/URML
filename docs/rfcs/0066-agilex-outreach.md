---
rfc: 0066
title: AgileX Robotics integration, request for comment from agilexrobotics maintainers
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

# RFC-0066: AgileX Robotics integration, request for comment from agilexrobotics maintainers

## Summary

URML does not yet ship an AgileX integration. This RFC proposes an `AgileXAdapter` family targeting the six published mobile-base ROS 2 packages under the [`agilexrobotics` GitHub org](https://github.com/agilexrobotics): `tracer_ros2`, `limo_ros2`, `scout_ros2`, `hunter_ros2`, `bunker_ros2`, `ranger_ros2`. The adapter routes URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) onto each base's published `geometry_msgs/Twist` topic, joint-state topic, and (where loaded) Nav2 goal-pose interface, plus the shared `ugv_sdk` C++ library where deployments need the no-ROS path. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the agilexrobotics maintainers.

This is the second Move #4 RFC. The Move #4 frame is **adjacent niches not touched by Moves #1–#3**. AgileX qualifies because [RFC-0056 (Stanford ALOHA)](0056-stanford-aloha.md) names AgileX Tracer as Mobile ALOHA's chassis but the institutional outreach to AgileX itself has never happened. This RFC closes that gap and extends to the full AgileX catalog.

## Motivation

AgileX's catalog covers the research-grade mobile-base tier between Hiwonder's hobby platforms ([RFC-0063](0063-hiwonder-outreach.md)) and Clearpath / Husky-class enterprise platforms. The six platforms span the kinematic surface URML cares about: Tracer (differential), Limo (multi-modal: differential / Ackermann / tracked / Mecanum at $1.5k tier), Scout (4WD differential), Hunter (Ackermann steering), Bunker (tracked), Ranger (omnidirectional). One adapter family covers all five URML mobility profiles via configuration, and a researcher who buys an AgileX Limo for an undergraduate course can later add a Scout Mini for off-road work and keep the same URML programs.

Three things make this RFC concrete rather than aspirational. First, the `agilexrobotics` org publishes 90 public repos including ROS 2 driver packages for every platform (`tracer_ros2`, `limo_ros2`, `scout_ros2`, `hunter_ros2`, `bunker_ros2`, `ranger_ros2`) plus the shared `ugv_sdk` C++ library at 108 stars. Top-starred repos: `scout_ros` (163 stars), `ugv_sdk` (108 stars), `limo_ros` (94 stars), `hunter_ros` (60 stars), `tracer_ros` (48 stars). Second, AgileX hardware already powers Mobile ALOHA's chassis (per RFC-0056), so URML's existing outreach to Stanford ALOHA implicitly already runs on AgileX silicon; an AgileX-side adapter closes the loop. Third, the AgileX-Hugging Face cross-link is publicly documented: AgileX has worked with the LeRobot ecosystem on mobile bases for SO-100-class deployments, which means the URML LeRobot RFC-0040 surface and the AgileX surface are already aligned at the ecosystem level.

AgileX's posture is open ROS drivers and open SDK code with proprietary hardware. License visibility was incomplete from the org landing page (verified attempt 2026-05-24); URML's adapter assumes the per-repo licenses match the ROS-driver convention and asks the maintainers to confirm. The hardware origin is China; URML's provenance discipline records this honestly, with the policy decision delegated to the operator's policy file per [RFC-0004](0004-compliance-policy.md).

## Detailed design

URML's existing artifacts that feed into an AgileX adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/research/`](../../spec/profiles/research/) ([RFC-0012](0012-research-profile.md)): the research profile, the natural home for AgileX hardware in academic deployments.
- [`spec/profiles/educational/`](../../spec/profiles/educational/) ([RFC-0011](0011-educational-profile.md)): the secondary profile for the Limo tier.
- [`reference/mobile-runtime/`](../../reference/mobile-runtime/): the runtime family that hosts wheeled-base adapters.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference.

### Proposed `AgileXAdapter` family shape

One adapter family, six concrete adapters parameterised by platform. Package layout:

```
reference/mobile-runtime/src/mobile_runtime/agilex/
├── __init__.py
├── adapter_tracer.py        # Tracer (differential)
├── adapter_limo.py          # Limo (mecanum / differential / Ackermann / tracked configurable)
├── adapter_scout.py         # Scout, Scout 2.0, Scout Mini (4WD differential)
├── adapter_hunter.py        # Hunter (Ackermann)
├── adapter_bunker.py        # Bunker (tracked)
├── adapter_ranger.py        # Ranger (omnidirectional)
├── ugv_sdk_helpers.py       # shared C++ UGV SDK bindings
└── manifests/
    ├── agilex_tracer.yaml
    ├── agilex_limo_diff.yaml
    ├── agilex_limo_mecanum.yaml
    ├── agilex_limo_ackermann.yaml
    ├── agilex_limo_tracked.yaml
    ├── agilex_scout.yaml
    ├── agilex_scout_mini.yaml
    ├── agilex_hunter.yaml
    ├── agilex_bunker.yaml
    └── agilex_ranger.yaml
```

The Limo's four-chassis-mode design earns per-mode manifests because each kinematic constraint surfaces differently in URML's static verifier (a Mecanum chassis accepts lateral `move_to` components that an Ackermann chassis rejects).

### Proposed URML v0.1 to AgileX mapping

| URML primitive | AgileX ROS 2 realisation |
|---|---|
| `move_to(pose)` | `geometry_msgs/Twist` on `/cmd_vel` for direct drive; Nav2 goal-pose on `/goal_pose` where the navigation stack is loaded; per-chassis kinematic constraints enforced by URML's validator from the manifest. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable on the mobile-base line; manifests declare no gripper. A future mobile-manipulator variant (e.g., a Tracer with a UR or Franka top) would compose a wheeled manifest with an arm manifest. |
| `measure(sensor_id)` | LIDAR (`/scan` if equipped), depth camera, IMU, wheel-encoder odometry. Per-platform sensor inventory recorded in the manifest. |
| `wait_for(...)` | ROS 2 subscriber with debounce, identical pattern to URML's other ROS 2 adapters. |
| `report(status)` | Publish to `/urml/<adapter>/report`. |

### Proposed capability manifest

Per-platform manifests under `reference/mobile-runtime/src/mobile_runtime/agilex/manifests/`. A condensed shape for `agilex_tracer`:

```yaml
brand: agilex_tracer
profile: research
mobility: wheeled_differential
chassis: differential
mass_kg: 26.0
payload_kg: 100.0
max_speed_m_s: 1.6
transport: [ros2, ugv_sdk]
ros2:
  package: agilexrobotics/tracer_ros2
  cmd_vel_topic: /cmd_vel
  odom_topic: /odom
  nav2_compatible: true
sensors:
  - imu_6dof
  - wheel_encoder
gripper: none
controller: ugv_sdk_v1
provenance:
  origin: CN
  ndaa_section_889_status: not_listed
  default_policy: pass
mobile_aloha_compatible: true
```

The `mobile_aloha_compatible: true` field is the institutional cross-link to [RFC-0056](0056-stanford-aloha.md): Tracer is the documented Mobile ALOHA chassis. URML's static verifier can use this field to validate that a Mobile-ALOHA-style four-arm composition manifest is mounted on a chassis with sufficient payload.

### Proposed conformance integration

A `URML_AGILEX_INTEGRATION=1` env-gated CI workflow installs the AgileX ROS 2 packages, runs each platform's adapter against a hermetic mock that replays odometry and IMU responses, and asserts that the emitted commands match per-platform golden traces. The in-tree conformance suite continues to use `MockROSAdapter`.

### Cross-link to RFC-0056 (Stanford ALOHA) and RFC-0040 (LeRobot)

Two existing URML outreach threads run through AgileX silicon. [RFC-0056 (Stanford ALOHA)](0056-stanford-aloha.md) describes Mobile ALOHA's four-VX300S configuration mounted on an AgileX Tracer; the ALOHA data-recording stack runs on the Tracer for the mobile-manipulation experiments. [RFC-0040 (Hugging Face LeRobot)](0040-hugging-face-lerobot.md) describes the policy library that hosts the ALOHA models. A direct AgileX engagement closes the institutional triangle: ALOHA / LeRobot consume AgileX hardware, URML's adapter family makes AgileX a first-class substrate target, and the upstream policies can retarget across substrates via URML.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none. The Limo multi-chassis support fits within the existing `mobility:` capability vocabulary.
- Reference runtime: proposed new sub-package `reference/mobile-runtime/src/mobile_runtime/agilex/`. Not built in this PR. The RFC requests agilexrobotics maintainer feedback first.
- Conformance suite: proposed new `agilex-integration.yml` CI workflow and a `URML_AGILEX_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. AgileX gains nothing yet; the adapter consumes the published ROS 2 packages and `ugv_sdk` without proposing changes to them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants AgileX input on the Limo per-chassis-mode manifest split and on the `ugv_sdk` direct-call path before shipping.
- **Six platforms widens the test matrix.** Each platform earns at least one manifest and one mock-trace fixture; the Limo earns four. Catalog growth (e.g., a future AgileX Cobot or Aerial line) adds proportional test cost.
- **License visibility was incomplete on the org landing page.** URML's adapter assumes the per-repo licenses match the ROS-driver convention; the RFC asks maintainers to confirm across all six platforms.
- **`ugv_sdk` is C++ first.** URML's mobile-runtime adapters are Python first. The C++ binding layer is a real engineering cost the RFC documents but does not solve.
- **Origin disclosure is necessary but politically loaded.** Recording `origin: CN` on the manifests is correct per URML's provenance discipline, but it means the default US-federal policy ([RFC-0003](0003-us-alignment.md), [RFC-0004](0004-compliance-policy.md)) will surface a procurement-compliance prompt to deploying organizations. URML's posture is that the decision belongs to the operator, not to URML.

## Alternatives considered

1. **Ship the adapter first, ask agilexrobotics maintainers later.** Rejected. The Limo multi-mode manifest design and the `ugv_sdk` binding choice are observable choices worth maintainer input on.
2. **Cover only Tracer (the Mobile ALOHA chassis) and skip the rest.** Rejected. The catalog-breadth value across six platforms under one institutional contact is the most distinctive thing AgileX offers; reducing scope forfeits it.
3. **Fold AgileX into [RFC-0056 (Stanford ALOHA)](0056-stanford-aloha.md) as a chassis appendix.** Rejected. The audiences are distinct (ALOHA is academic; AgileX is the hardware vendor), and surfacing AgileX only as an appendix would forfeit the direct vendor relationship.
4. **One parametric manifest covering all four Limo modes.** Rejected. The kinematic constraint differences matter at validation time; per-mode manifests preserve the static-verification rigour.

## Prior art

- `agilexrobotics/tracer_ros2`, `agilexrobotics/limo_ros2`, `agilexrobotics/scout_ros2`, `agilexrobotics/hunter_ros2`, `agilexrobotics/bunker_ros2`, `agilexrobotics/ranger_ros2`: the per-platform ROS 2 driver packages.
- `agilexrobotics/scout_ros` (163 stars), `agilexrobotics/limo_ros` (94 stars), `agilexrobotics/hunter_ros` (60 stars), `agilexrobotics/tracer_ros` (48 stars): the ROS 1 predecessors.
- `agilexrobotics/ugv_sdk` (108 stars): the shared C++ SDK for the UGV line.
- AgileX product line documentation at agilex.ai.
- [RFC-0009](0009-legged-humanoid-mobility.md): the capability-manifest schema (used here for the wheeled-mobility surface).
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): the URML profiles this RFC's manifests target.
- [RFC-0040](0040-hugging-face-lerobot.md): the LeRobot RFC; cross-links via Mobile ALOHA on Tracer.
- [RFC-0056](0056-stanford-aloha.md): the Stanford ALOHA RFC; cross-links via Mobile ALOHA's Tracer chassis.
- [RFC-0063](0063-hiwonder-outreach.md): the parallel mobile-platform RFC at a different tier.

## Unresolved questions

Provisional pending agilexrobotics maintainer feedback:

1. **License confirmation.** Could you confirm the licenses on `tracer_ros2`, `limo_ros2`, `scout_ros2`, `hunter_ros2`, `bunker_ros2`, `ranger_ros2`, and `ugv_sdk`?
2. **Adapter home.** Should URML host the adapter family under `reference/mobile-runtime/src/mobile_runtime/agilex/` (URML-side), under a new repo in the `agilexrobotics` org as a contributed example, or both?
3. **Limo manifest granularity.** Per-mode manifests (Mecanum / differential / Ackermann / tracked) versus a single parametric manifest with a `chassis_mode:` field?
4. **`ugv_sdk` direct path.** Is the C++ `ugv_sdk` library URML's recommended no-ROS path, or does AgileX recommend the ROS 2 driver even in non-ROS deployments?
5. **Mobile ALOHA cross-link.** Is there interest in a documented note (`tracer_ros2` README or AgileX product page) acknowledging the Mobile ALOHA chassis use case via URML?
6. **LeRobot cross-link.** Is there interest in coordinating the URML integration with the existing AgileX–LeRobot ecosystem alignment?
7. **Conformance lane.** Open to a URML conformance line on the platform-repo READMEs?
8. **Anything else.**

## Implementation note

RFC-0066 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/mobile-runtime/src/mobile_runtime/agilex/` package follows in a later session, gated on agilexrobotics maintainer feedback. Draft state. Second Move #4 RFC. Ledger entry in [`examples/lighthouses/outreach-move4.yaml`](../../examples/lighthouses/outreach-move4.yaml).

## Requested feedback (from agilexrobotics maintainers)

1. License confirmation across the six platform repos plus `ugv_sdk`.
2. Adapter home (URML repo, agilexrobotics contributed example, both).
3. Limo per-mode manifest granularity.
4. `ugv_sdk` direct-path recommendation.
5. Mobile ALOHA cross-link note.
6. LeRobot ecosystem coordination.
7. Conformance-lane interest.
8. Anything else.

## How to respond

`agilexrobotics` GitHub org has 90 public repos and 1.3k followers (verified 2026-05-24). The most-active per-platform repo is `scout_ros` at 163 stars; the most-recent ROS 2 driver activity is on `tracer_ros2`. URML's planned channel: open a single Issue on the most-active platform repo (`scout_ros` or `tracer_ros2`) pointing to this RFC, with optional cross-references on `ugv_sdk` for the SDK-specific questions.

URML's own public Discussions for the broader Move #4 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the second Move #4 RFC).
- [x] Motivation grounded in verified technical alignment (90 public repos in the agilexrobotics org, per-platform ROS 2 drivers, `ugv_sdk` C++ library at 108 stars, Mobile ALOHA chassis cross-link to RFC-0056) plus the catalog-breadth positioning.
- [x] Detailed design uses verified repo names (`tracer_ros2`, `limo_ros2`, `scout_ros2`, `hunter_ros2`, `bunker_ros2`, `ranger_ros2`, `ugv_sdk`).
- [x] At least one alternative considered (four are: ship-first, Tracer-only, fold-into-ALOHA, parametric-Limo-manifest).
- [x] Drawbacks are real (proposal-only, six-platform test matrix, license-visibility gap, C++ vs Python first, origin disclosure friction).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of the agilexrobotics GitHub org as of 2026-05-24.
- [x] Provenance row (`origin: CN`) recorded honestly per URML's discipline, with the policy-decision boundary made explicit.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
