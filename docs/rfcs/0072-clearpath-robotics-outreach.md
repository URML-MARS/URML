---
rfc: 0072
title: Clearpath Robotics integration, request for comment from clearpathrobotics maintainers
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

# RFC-0072: Clearpath Robotics integration, request for comment from clearpathrobotics maintainers

## Summary

URML does not yet ship a Clearpath integration. This RFC proposes a `ClearpathAdapter` family under [`reference/mobile-runtime/`](../../reference/mobile-runtime/) targeting the [`clearpathrobotics` GitHub org](https://github.com/clearpathrobotics) (314 public repos, Apache-2.0 / BSD-3-Clause / MIT mix). The adapter covers TurtleBot 4 (iRobot-Create-3-based), Husky, Jackal, Dingo, and Warthog. URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) map onto the published ROS 2 packages without changes upstream. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the clearpathrobotics maintainers.

This is the second Move #5 RFC. The TurtleBot 4 platform sits explicitly alongside the TurtleBot 3 platform of [RFC-0065 (ROBOTIS)](0065-robotis-outreach.md): same TurtleBot name, different hardware lineage. URML treats both as first-class targets. This RFC differentiates them clearly.

## Motivation

Clearpath is the Canadian-anchored Western channel to URML's research-mobile-platform population. The org has been a fixture in the ROS ecosystem since the early 2010s, was acquired by Rockwell Automation in 2024, and currently maintains 314 public repos with 142 stars on its ROSCon 2024 workshop materials and 233 stars on `cpr_gazebo`. The platform line. TurtleBot 4 (the first TurtleBot pre-configured for ROS 2 out-of-box, iRobot Create 3 base), Husky (outdoor research workhorse, used at hundreds of research labs), Jackal (small outdoor), Dingo (compact indoor), Warthog (large all-terrain). Covers a deployment surface that complements [RFC-0066 (AgileX)](0066-agilex-outreach.md) (Chinese research-grade mobile bases) and [RFC-0071 (Robotnik)](0071-robotnik-outreach.md) (Spanish commercial-mobile-robotics) at the institutional level.

**TurtleBot 4 versus TurtleBot 3 disambiguation.** URML's [RFC-0065 (ROBOTIS)](0065-robotis-outreach.md) targets TurtleBot 3 (the ROBOTIS DIY-kit platform built on an OpenCR controller plus Dynamixel servos, Korean origin, $549-tier). This RFC targets TurtleBot 4 (the Clearpath-built pre-assembled platform on an iRobot Create 3 base, Canadian origin, $1k–$1.5k tier). Same TurtleBot trademark, different hardware, different audiences (DIY kit vs. ready-to-run lab equipment), different SDKs. Both are first-class URML adapter targets. The RFC body acknowledges this directly so a reader scanning the index does not collapse them.

Three things make this RFC concrete rather than aspirational. First, the `clearpathrobotics` org publishes 314 public repos with active maintenance; top-starred include `cpr_gazebo` (233 stars), `robot_upstart` (205 stars), `roscon2024-workshop-demystifying-ros2-networking` (142 stars), `LMS1xx` (58 stars, SICK LMS driver. Already implicitly in URML via the Move #1 SICK RFC-0033), `clearpath_common` (54 stars). License mix Apache-2.0 / BSD-3-Clause / MIT. Second, the platforms are ROS 2 native and have been since before ROS 2 was the default; the URML adapter consumes mature surfaces. Third, the post-Rockwell context gives Clearpath an industrial channel that complements URML's existing Move #1 industrial OEM outreach.

Clearpath's posture is open ROS 2 software on proprietary hardware; the URML adapter consumes the public software surface without proposing hardware changes. Clearpath is Canada-domiciled (Kitchener, Ontario); URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) passes at the manifest level for the CA origin without organisational override (Canada is a US treaty ally).

## Detailed design

### Proposed `ClearpathAdapter` family shape

```
reference/mobile-runtime/src/mobile_runtime/clearpath/
├── __init__.py
├── adapter_turtlebot4.py       # TurtleBot 4 Standard / Lite (Create 3 base)
├── adapter_husky.py            # Husky outdoor research
├── adapter_jackal.py           # Jackal small outdoor
├── adapter_dingo.py            # Dingo compact indoor
├── adapter_warthog.py          # Warthog large all-terrain
├── common.py                   # shared Clearpath ROS 2 helpers
└── manifests/
    ├── clearpath_turtlebot4_standard.yaml
    ├── clearpath_turtlebot4_lite.yaml
    ├── clearpath_husky.yaml
    ├── clearpath_jackal.yaml
    ├── clearpath_dingo_d.yaml      # differential
    ├── clearpath_dingo_o.yaml      # omnidirectional
    └── clearpath_warthog.yaml
```

### Proposed URML v0.1 to Clearpath mapping

| URML primitive | Clearpath ROS 2 realisation |
|---|---|
| `move_to(pose)` | `geometry_msgs/Twist` on `/cmd_vel` for direct drive; Nav2 goal-pose where loaded. Per-platform kinematic constraints from the manifest. |
| `measure(sensor_id)` | LIDAR (often SICK or Velodyne / Ouster), IMU, depth camera. Sensor inventory in manifest. |
| `wait_for(...)` | ROS 2 subscriber with debounce. |
| `report(status)` | Publish to `/urml/<adapter>/report`. |
| Industrial-profile primitives ([RFC-0013](0013-industrial-layer2-primitives.md)) | Not applicable on the mobile-base lineup; Clearpath manipulator product (Ridgeback or future mobile-manipulator) would compose with a `reference/cobot-runtime/` arm manifest. |

### Proposed capability manifest

Condensed shape for `clearpath_husky`:

```yaml
brand: clearpath_husky
profile: research
mobility: wheeled_skid_steer
mass_kg: 50.0
payload_kg: 75.0
transport: ros2
ros2:
  package: clearpathrobotics/husky
  cmd_vel_topic: /husky/cmd_vel
  scan_topic: /husky/scan
  nav2_compatible: true
sensors:
  - lidar_2d_or_3d
  - imu_6dof
  - gps_optional
gripper: none
controller: husky_mcu
provenance:
  origin: CA
  ndaa_section_889_status: not_listed
  default_policy: pass
post_rockwell_note: true  # Acquired by Rockwell Automation 2024; documents context for procurement
```

The `post_rockwell_note` flag documents the industrial-channel context for deploying organisations doing supply-chain due diligence, without claiming or asserting compliance specifics URML cannot verify per-deployment.

### Cross-link to TurtleBot 3 ([RFC-0065](0065-robotis-outreach.md))

URML's TurtleBot 4 manifest at `clearpath_turtlebot4_standard` is intentionally namespaced distinct from `robotis_turtlebot3_burger` in [RFC-0065](0065-robotis-outreach.md)'s manifest set. A program written for TurtleBot 3 retargets to TurtleBot 4 by switching the manifest; the URML validator handles the kinematic and sensor-inventory differences automatically. The institutional surfaces (Clearpath maintainers vs. ROBOTIS-GIT maintainers) are different but the URML adapter family pattern is consistent.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/mobile-runtime/src/mobile_runtime/clearpath/`. Not built in this PR.
- Conformance suite: proposed new `clearpath-integration.yml` CI workflow and a `URML_CLEARPATH_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.**
- **314-repo org is hard to navigate.** Verifying the canonical per-platform repos requires maintainer input.
- **Five platforms widens the test matrix** with per-platform manifests and golden traces.
- **TurtleBot 4 / TurtleBot 3 collision risk.** Static readers might confuse the two. The RFC body and the manifest namespacing minimise the risk but do not eliminate it.
- **Post-Rockwell organisational drift.** Clearpath's GitHub maintenance posture may shift under Rockwell ownership; URML's adapter takes on that risk.

## Alternatives considered

1. **Ship the adapter first.** Rejected. Same reasoning as RFC-0071.
2. **Cover only TurtleBot 4 and skip the rest.** Rejected. The platform breadth is the differentiator.
3. **Fold Clearpath into [RFC-0065 (ROBOTIS)](0065-robotis-outreach.md) as another TurtleBot-family vendor.** Rejected. TurtleBot 3 and TurtleBot 4 are different hardware and different audiences despite the shared name; institutional outreach to ROBOTIS does not cover Clearpath.
4. **Fold Clearpath into [RFC-0066 (AgileX)](0066-agilex-outreach.md) or [RFC-0071 (Robotnik)](0071-robotnik-outreach.md).** Rejected. Different geographies, different audiences, different price tiers.

## Prior art

- `clearpathrobotics` GitHub org (314 public repos, Apache-2.0 / BSD-3-Clause / MIT mix).
- `clearpathrobotics/cpr_gazebo` (233 stars), `robot_upstart` (205 stars), `roscon2024-workshop-demystifying-ros2-networking` (142 stars).
- TurtleBot 4 product page at `clearpathrobotics.com/turtlebot-4/`.
- Husky / Jackal / Dingo / Warthog product pages at `clearpathrobotics.com`.
- [RFC-0065](0065-robotis-outreach.md): the TurtleBot 3 RFC this one explicitly cross-references.
- [RFC-0066](0066-agilex-outreach.md), [RFC-0071](0071-robotnik-outreach.md): the other mobile-platform RFCs in URML's outreach landscape.
- [RFC-0033](0033-sick-integration.md): the SICK lidar Move #1 RFC; Clearpath ships SICK lidars by default on Husky.

## Unresolved questions

Provisional pending clearpathrobotics maintainer feedback:

1. **Adapter home.** URML repo (`reference/mobile-runtime/src/mobile_runtime/clearpath/`), Clearpath contributed example, both?
2. **Canonical per-platform repos.** Could you confirm the canonical first-class repos for TurtleBot 4 / Husky / Jackal / Dingo / Warthog in the 314-repo org?
3. **TurtleBot 4 cross-coordination.** Is there interest in coordinating with URML's open [RFC-0065 (ROBOTIS)](0065-robotis-outreach.md) outreach so the TurtleBot 3 and TurtleBot 4 URML manifests stay consistent at the program-portability layer?
4. **Dingo variant manifests.** Per-variant (D differential / O omnidirectional) or parametric?
5. **Post-Rockwell maintenance posture.** Has the GitHub maintenance and release cadence stabilised post-acquisition?
6. **Conformance lane.** Open to a URML conformance line on the TurtleBot 4 README or `clearpathrobotics.com` documentation?
7. **Anything else.**

## Implementation note

RFC-0072 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from clearpathrobotics maintainers)

1. Adapter home.
2. Canonical per-platform repos.
3. TurtleBot 4 cross-coordination with ROBOTIS TurtleBot 3.
4. Dingo manifest granularity.
5. Post-Rockwell maintenance posture.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`clearpathrobotics` org has 314 public repos (verified 2026-05-24). The most-active general repo is `cpr_gazebo` (233 stars). URML's planned channel: open a single Issue on `clearpathrobotics/cpr_gazebo` or `clearpathrobotics/clearpath_common` labelled with the closest `enhancement` equivalent, pointing to this RFC. If maintainers prefer a different per-platform thread, follow their preference.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary tells the proposal-only story and Move #5 framing.
- [x] Motivation grounded in verified 314-repo org, top repos, post-Rockwell context.
- [x] Detailed design uses verified repo names.
- [x] TurtleBot 3 / TurtleBot 4 disambiguation made explicit in motivation and manifest namespacing.
- [x] Four alternatives considered.
- [x] Drawbacks real (proposal-only, 314-repo navigation, five-platform test matrix, TurtleBot collision risk, post-Rockwell drift).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicitly says no adapter code.
- [x] Surface ("How to respond") verified against `clearpathrobotics` org as of 2026-05-24.
- [x] Provenance `origin: CA` recorded; US-federal default policy passes.
- [x] CLAUDE.md §What Claude Should Never Do reviewed; compliant.
