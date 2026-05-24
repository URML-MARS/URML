---
rfc: 0077
title: MIT CHAMP integration, research-collab proposal to chvmp maintainers
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

# RFC-0077: MIT CHAMP integration, research-collab proposal to chvmp maintainers

## Summary

URML does not yet ship a CHAMP integration. This RFC proposes a `ChampAdapter` under [`reference/legged-runtime/`](../../reference/legged-runtime/) targeting [`chvmp/champ`](https://github.com/chvmp/champ) (2.2k stars, BSD-3-Clause, ROS 1, Issues + Discussions enabled). CHAMP is a quadruped controller framework (not a hardware platform): it implements MIT Cheetah Lab's quadruped controller and supports MIT Mini Cheetah, ANYmal, Boston Dynamics Spot, LittleDog, SpotMicroAI, OpenQuadruped, and a published URDF for each. URML's adapter consumes CHAMP rather than ship against a specific geometry, mirroring the [RFC-0070 (HEBI)](0070-hebi-robotics-outreach.md) per-customer-geometry pattern. **Research-collab proposal** because the maintainer is an academic lab and the upstream is a control-framework, not a vendor product.

This is the seventh Move #5 RFC, third Tier B entry.

## Motivation

CHAMP fills a unique slot in URML's outreach landscape: it is the **control-framework target**, not a hardware target. A URML adapter for CHAMP works on any URDF CHAMP supports. Which already includes URML-targeted substrates ANYmal ([RFC-0049](0049-anybotics-anymal-integration.md)) and Boston Dynamics Spot ([RFC-0043](0043-boston-dynamics-spot-integration.md)). The cross-link is structural: URML's Spot and ANYmal adapters route programs onto the platforms' native SDKs; a URML CHAMP adapter routes programs onto the CHAMP controller on the same platforms. Two paths to the same hardware, with different control characteristics. CHAMP gives the URML user access to an open-source whole-body controller that the proprietary SDKs do not expose.

Three things make this RFC concrete. First, `chvmp/champ` has 2.2k stars (the largest star count of any Move #5 target), BSD-3-Clause license, Issues enabled (51 open), Discussions enabled, with sibling repos `champ_setup_assistant`, `champ_teleop`, `libchamp`, `firmware`, `robots` (the URDF collection), `chicken_head` (demo). Active maintenance. Second, CHAMP is **ROS 1 only** (Kinetic / Melodic / Noetic), no ROS 2 support documented. URML's adapter would target ROS 1 Noetic on the legacy lane (similar to [RFC-0064 (Trossen Interbotix)](0064-trossen-interbotix-outreach.md) which also has a ROS 1 Noetic lane). Third, the audience overlap with URML's research-tier users is exact: graduate students and researchers running CHAMP on Mini Cheetah / ANYmal / Spot want a substrate-neutral programming layer above the controller, and CHAMP already abstracts the geometry.

CHAMP's posture is fully open: BSD-3-Clause, English-first README, MIT lineage. The maintainer (`chvmp` on GitHub, traced to MIT Cheetah Lab affiliation) is academic. URML's open-core commitment lands without translation.

## Detailed design

### Proposed `ChampAdapter` shape

```
reference/legged-runtime/src/legged_runtime/champ/
├── __init__.py
├── adapter.py             # ChampAdapter (URDF-parameterised from manifest)
├── ros1_dispatch.py       # ROS 1 Noetic dispatch
└── manifests/
    ├── champ_mini_cheetah_example.yaml
    ├── champ_anymal_example.yaml
    ├── champ_spot_example.yaml
    ├── champ_littledog_example.yaml
    ├── champ_spotmicroai_example.yaml
    └── champ_openquadruped_example.yaml
```

The `_example.yaml` suffix is intentional: like [RFC-0070 (HEBI)](0070-hebi-robotics-outreach.md), the per-deployment URML manifest is partly user-authored against the customer's URDF. URML ships example manifests covering CHAMP's supported URDFs, and the deploying user adapts.

### Proposed URML v0.1 to CHAMP mapping

| URML primitive | CHAMP realisation |
|---|---|
| `move_to(pose)` | A base-pose goal via CHAMP's published `cmd_vel` plus pose topics (ROS 1 Noetic). The whole-body controller handles the gait and joint trajectories internally. |
| `measure(sensor_id)` | Joint-state, IMU, optional LIDAR / depth via the URDF's declared sensor surface. |
| `wait_for(...)` | ROS 1 subscriber with debounce. |
| `report(status)` | Publish to `/urml/<adapter>/report`. |

### Proposed capability manifest (Mini Cheetah example)

```yaml
brand: champ_mini_cheetah_example
profile: research
mobility: legged_quadruped
dof: 12
mass_kg: 9.0  # MIT Mini Cheetah spec
control_mode: torque_via_champ_controller
transport: ros1_noetic
ros1:
  package: chvmp/champ
  cmd_vel_topic: /cmd_vel
  pose_topic: /base_pose_goal
urdf:
  source: chvmp/robots
  variant: mini_cheetah
sensors:
  - joint_state
  - imu_6dof
gripper: none
provenance:
  origin: US  # MIT lineage
  ndaa_section_889_status: not_listed
  default_policy: pass
```

### Cross-link to RFC-0043 (Spot) and RFC-0049 (ANYmal)

A URML program targeting `spot_quadruped` (RFC-0043 SpotAdapter, manifest spot_quadruped.yaml shipping today) and a URML program targeting `champ_spot_example` are two different routes to the same hardware. The former dispatches through Boston Dynamics' SDK; the latter dispatches through the open-source CHAMP controller on the same Spot. URML's user picks based on whether they need the proprietary SDK's full-feature surface (manipulator arm, navigation) or the open controller's customisability (gait research, sim-to-real). Both are first-class URML adapters.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/legged-runtime/src/legged_runtime/champ/`. Not built in this PR.
- Conformance suite: proposed new `champ-integration.yml` CI workflow (ROS 1 Noetic lane).

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **ROS 1 only.** CHAMP does not yet support ROS 2. URML's adapter takes on the ROS 1 Noetic legacy commitment.
- **Control-framework adapter is a novel pattern for URML.** Per-customer URDF manifests need documentation, similar to the HEBI pattern in [RFC-0070](0070-hebi-robotics-outreach.md).
- **Cross-link ambiguity.** A user might be confused whether to target Spot via `SpotAdapter` (RFC-0043) or via `ChampAdapter` on a Spot URDF. The RFC body addresses this, but the choice-architecture deserves UX work.
- **Whole-body controller vs URML's `move_to`.** CHAMP's controller does most of the work; URML's `move_to` reduces to a base-pose goal. This is the right shape but the URML user gets less direct control than the controller architecture suggests.

## Alternatives considered

1. **Ship the adapter first.** Rejected.
2. **Skip CHAMP entirely; defer to per-platform adapters (Spot, ANYmal, Mini Cheetah individually).** Rejected. CHAMP is the canonical academic-research entry point for whole-body quadruped control, and ignoring it forfeits the audience.
3. **Wait for CHAMP ROS 2 support before opening outreach.** Rejected. There is no documented timeline for ROS 2, and engaging now lets URML help shape the ROS 2 transition if it happens.

## Prior art

- `chvmp/champ` (2.2k stars, BSD-3-Clause, ROS 1 Kinetic/Melodic/Noetic, Issues+Discussions enabled).
- `chvmp/champ_setup_assistant`, `champ_teleop`, `libchamp`, `firmware`, `robots`, `chicken_head`.
- MIT Cheetah Lab publications (the controller's origin).
- [RFC-0043](0043-boston-dynamics-spot-integration.md), [RFC-0049](0049-anybotics-anymal-integration.md): the platform-specific adapters CHAMP overlaps with.
- [RFC-0070](0070-hebi-robotics-outreach.md): the per-customer-geometry manifest pattern this RFC mirrors.

## Unresolved questions

1. **ROS 2 timeline.** Is CHAMP ROS 2 support planned?
2. **Per-platform vs platform-agnostic manifests.** Should URML ship per-URDF example manifests or a single parametric `champ_*` manifest?
3. **Adapter home.** URML repo or `chvmp` contributed example?
4. **SpotAdapter / ChampAdapter coexistence.** Documented user-guidance for picking between proprietary-SDK and CHAMP paths on the same hardware?
5. **ANYmal cross-coordination.** Should URML coordinate with the existing [RFC-0049 (ANYmal)](0049-anybotics-anymal-integration.md) thread on CHAMP coexistence?
6. **Conformance lane.** Open to a URML conformance line on `chvmp/champ` README or in the Discussions?
7. **Anything else.**

## Implementation note

RFC-0077 ships as a single RFC document PR. No adapter code in this PR. Research-collab framing. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from chvmp maintainers)

1. ROS 2 timeline.
2. Per-platform vs parametric manifest design.
3. Adapter home.
4. SpotAdapter / ChampAdapter coexistence guidance.
5. ANYmal cross-coordination.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`chvmp/champ` has Issues enabled (51 open) and Discussions enabled (community forum). Verified 2026-05-24. URML's planned channel: open a Discussion on `chvmp/champ` (or labelled Issue if maintainers prefer), pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Motivation grounded in verified `chvmp/champ` surface (2.2k stars, BSD-3-Clause).
- [x] Control-framework-vs-hardware design observation made explicit.
- [x] Cross-link to RFC-0043 and RFC-0049 disambiguated.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, ROS 1 only, novel pattern, cross-link ambiguity, whole-body controller hiding `move_to` detail).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified as of 2026-05-24.
- [x] Provenance `origin: US` (MIT lineage) recorded; default policy passes.
- [x] CLAUDE.md compliance check passed.
