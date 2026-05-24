---
rfc: 0078
title: Orca4 / ros-maritime integration, research-collab proposal to community maintainers
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

# RFC-0078: Orca4 / ros-maritime integration, research-collab proposal to community maintainers

## Summary

URML already ships a `BlueRovAdapter` in [`reference/marine-runtime/`](../../reference/marine-runtime/) (per `marine-runtime/README.md`, the adapter speaks MAVLink to ArduSub on BlueROV2 hardware). This RFC does **not** propose a new adapter. It proposes alignment with the community-maintained Orca4 ROS 2 stack ([`clydemcqueen/orca4`](https://github.com/clydemcqueen/orca4), 183 stars, MIT, ROS 2 Humble) and the `ros-maritime` working group, so the URML marine-runtime can document interoperability with the upstream community AUV stack instead of competing with it. **Research-collab proposal** following the precedent of [RFC-0052 (Meta FAIR V-JEPA 2)](0052-meta-fair-vjepa2.md) and the established research-collab framing because `ros-maritime` is a community working group, not a commercial vendor.

This is the eighth Move #5 RFC, fourth Tier B entry.

## Motivation

URML's marine-runtime ships a BlueRobotics BlueROV2 + ArduSub adapter today, via MAVLink. The Orca4 community project sits one layer above MAVLink: it adds ROS 2 Humble integration, ORB_SLAM2-based pose generation, simulated sensors (barometer, IMU), down-facing stereo cameras, and a Gazebo Harmonic simulation lane. The URML adapter and the Orca4 stack are complementary, not competing. URML emits substrate-neutral primitives, Orca4 provides the ROS 2 substrate the primitives can dispatch to on BlueROV2 hardware.

This RFC is **alignment work, not adapter work**. The asks are:
1. Document the Orca4 ROS 2 surface as a supported dispatch path inside URML's marine-runtime, in addition to the direct-MAVLink path that ships today.
2. Coordinate the URML manifest schema's marine entries with any conventions Orca4 / ros-maritime expects.
3. Cross-reference URML's marine-runtime from the Orca4 README and from `ros-maritime`'s working-group docs if the community is receptive.

Three things make this RFC concrete. First, `clydemcqueen/orca4` is 183 stars, MIT-licensed, with Issues enabled (5 open at time of writing), C++ 67.7% and Python 24.8%, built on ArduSub + mavros + ORB_SLAM2 + ROS 2 Humble. Second, the institutional `ros-maritime` GitHub org or equivalent community surface needs verification at the time of outreach. The prior Move #4 research mentioned `ros-maritime/awesome-maritime-robotics` but the org page was not directly verified in this RFC's surface check. The RFC asks for the canonical community contact path. Third, the alignment work is cheap (documentation cross-references) but the institutional value is high: URML's marine-runtime becomes the natural natural-language layer above the community stack rather than a competing surface.

The maintainer surface is academic / community (clydemcqueen + ros-maritime contributors). URML's open-core commitment lands without translation.

## Detailed design

This is the lightest-weight Move #5 RFC because no new adapter ships. The detailed design is:

### URML marine-runtime documentation update

Existing `reference/marine-runtime/README.md` documents the MAVLink-direct BlueRovAdapter. After community feedback, the README would add:

- A "Dispatch via Orca4 (ROS 2)" section pointing to `clydemcqueen/orca4` as the supported ROS 2 path.
- A note that URML's substrate Protocol supports both transports (direct MAVLink and Orca4-mediated ROS 2 Humble).
- A cross-reference to any `ros-maritime` working-group conventions for sensor naming, frame conventions, and the SLAM coordinate system.

### Proposed manifest extension (illustrative, not normative)

```yaml
brand: bluerov2_orca4
profile: marine
mobility: underwater_holonomic
transport: [mavlink, ros2_via_orca4]
ros2:
  package: clydemcqueen/orca4
  via: ardusub + mavros
  ros2_distro: humble
flight_controller: ardusub
slam: orb_slam2_optional
sensors:
  - imu_6dof
  - barometer
  - depth_camera_optional
  - stereo_camera_down_facing
provenance:
  upstream_community: ros-maritime
  default_policy: pass
```

The manifest is illustrative; the actual change is a documentation update once the community surface is confirmed.

### Cross-link to RFC-0041 (ArduPilot)

URML's existing [RFC-0041 (ArduPilot)](0041-ardupilot-integration.md) outreach is the institutional MAVLink-side relationship. RFC-0078 sits one layer above, at the ROS 2 / community-stack layer. The two RFCs are not redundant. They engage different community surfaces.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: `reference/marine-runtime/README.md` documentation update (deferred to a separate PR after community feedback).
- Conformance suite: optional new `orca4-integration.yml` CI workflow with a `URML_ORCA4_INTEGRATION` env gate; lower priority than the documentation update.

## Backward compatibility

Pre-v1.0. The existing direct-MAVLink BlueRovAdapter is unchanged. Orca4 dispatch path is purely additive.

## Drawbacks

- **Proposal-only.**
- **Community-surface ambiguity.** The `ros-maritime` working-group GitHub presence was not fully verified during this RFC's surface check. The canonical community contact path is an open question.
- **Multi-maintainer coordination.** `clydemcqueen` is one maintainer; `ros-maritime` is a working-group ostensibly with multiple contributors; the URML thread might need to fan out across surfaces.
- **Smaller institutional value.** This is an alignment-and-documentation RFC, not a new-adapter RFC. The institutional value is real but the engagement payload is lighter than the other Move #5 RFCs.

## Alternatives considered

1. **Skip Orca4 / ros-maritime entirely.** Rejected. Community alignment costs little and avoids surface-duplication friction.
2. **Build a parallel URML-native ROS 2 underwater stack.** Rejected. Orca4 already exists and reinventing it would violate URML's "consume existing substrates, don't compete" posture.
3. **Fold Orca4 alignment into [RFC-0041 (ArduPilot)](0041-ardupilot-integration.md).** Rejected. Different community, different abstraction layer.

## Prior art

- `clydemcqueen/orca4` (183 stars, MIT, ROS 2 Humble, ArduSub + mavros + ORB_SLAM2).
- `ros-maritime` (working-group surface; canonical GitHub presence pending verification).
- URML's existing `reference/marine-runtime/` BlueRovAdapter (already shipping).
- [RFC-0041 (ArduPilot)](0041-ardupilot-integration.md): the MAVLink-side institutional outreach.
- [RFC-0052 (Meta FAIR V-JEPA 2)](0052-meta-fair-vjepa2.md): research-collab framing precedent.

## Unresolved questions

1. **Canonical community contact.** Where is the `ros-maritime` working group's primary discussion surface (GitHub org? RFC repo? Discourse?), and is there a maintainer-of-record for outreach?
2. **Sensor naming and frame conventions.** Does the community have documented conventions URML's manifests should align with?
3. **Orca4 ROS 2 distro plans.** Is Orca4 planning to support Jazzy and Rolling alongside Humble?
4. **Cross-reference willingness.** Is the Orca4 maintainer open to a brief README mention of URML's marine-runtime as a complementary primitive-layer?
5. **`awesome-maritime-robotics` list inclusion.** Is URML's marine-runtime appropriate for inclusion in `ros-maritime/awesome-maritime-robotics` (or wherever the canonical list lives)?
6. **Conformance lane.** Open to a URML conformance line in Orca4's README?
7. **Anything else.**

## Implementation note

RFC-0078 ships as a single RFC document PR. No adapter code in this PR. Research-collab framing. The actual documentation update to `reference/marine-runtime/README.md` follows in a later PR after community feedback. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from Orca4 maintainer and ros-maritime community)

1. Canonical community contact path.
2. Sensor naming / frame conventions.
3. Orca4 ROS 2 distro plans.
4. README cross-reference willingness.
5. `awesome-maritime-robotics` inclusion path.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`clydemcqueen/orca4` has Issues enabled (5 open; verified 2026-05-24). URML's planned channel: open a single Issue on `clydemcqueen/orca4` labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC. If the maintainer prefers a `ros-maritime` working-group thread, the URML follow-up moves there once the surface is confirmed.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Honest about scope: alignment + documentation, not new-adapter.
- [x] Existing URML marine-runtime / BlueRovAdapter referenced as shipping baseline.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, community-surface ambiguity, multi-maintainer coordination, smaller engagement payload).
- [x] Backward compatibility: additive; existing BlueRovAdapter unchanged.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified as of 2026-05-24; `ros-maritime` community-surface gap honestly noted.
- [x] CLAUDE.md compliance check passed.
