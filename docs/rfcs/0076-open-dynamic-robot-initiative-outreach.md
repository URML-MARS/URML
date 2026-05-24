---
rfc: 0076
title: Open Dynamic Robot Initiative (Solo) integration, research-collab proposal
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

# RFC-0076: Open Dynamic Robot Initiative (Solo) integration, research-collab proposal to open-dynamic-robot-initiative maintainers

## Summary

URML does not yet ship a Solo integration. This RFC proposes a `SoloAdapter` under [`reference/legged-runtime/`](../../reference/legged-runtime/) targeting the [`open-dynamic-robot-initiative` GitHub org](https://github.com/open-dynamic-robot-initiative) (41 public repos, 677 followers, BSD-2 / BSD-3-Clause). The adapter routes URML Layer-2 primitives onto Solo 8 / Solo 12's torque-controlled actuators via the consortium's published `master-board` firmware interface and the broader actuator stack. No spec change on URML's side. **Research-collab proposal** following the precedent of [RFC-0052 (Meta FAIR V-JEPA 2)](0052-meta-fair-vjepa2.md) and [RFC-0056 (Stanford ALOHA)](0056-stanford-aloha.md) because the maintainer is a multi-institution research consortium (MPI Tübingen, NYU, ETH Zürich), not a commercial vendor.

This is the sixth Move #5 RFC, second Tier B entry.

## Motivation

The Open Dynamic Robot Initiative (ODRI) is the European multi-institution open-hardware consortium for **torque-controlled** quadruped research. Where Stanford Pupper ([RFC-0075](0075-stanford-pupper-outreach.md)) is hobby-servo / educational, ODRI's Solo is research-grade torque-controlled. The platform academic robotics labs use when they need to do whole-body dynamics, sim-to-real transfer with realistic actuator models, and locomotion-policy research that requires more than position control.

Three things make this RFC concrete. First, the org's GitHub footprint is substantial for an academic project: 41 repos, 677 followers, with `open_robot_actuator_hardware` at **1.4k stars**, `master-board` at 133 stars (Solo's control electronics; last commit 2026-05-07. Actively maintained), `open-motor-driver-initiative` at 111 stars. License pattern BSD-2 / BSD-3-Clause across the repos. Second, the URML cross-link to other research-collab targets is real: ODRI's Solo is in the same population as Stanford Pupper (RFC-0075), MIT CHAMP-supported research quadrupeds (RFC-0077 below), and Berkeley Humanoid Lite ([RFC-0069](0069-berkeley-humanoid-lite-outreach.md)). All four are academic-research substrates for legged research; URML's substrate-neutral vocabulary is the natural cross-platform interface. Third, ODRI is ERC-funded (European Research Council) with explicit open-science commitments documented in published papers; URML's open-core posture aligns institutionally.

ODRI's posture is fully open: BSD across the consortium's published code and hardware files, English-first documentation. URML's open-core commitment lands without translation. The lead institution is MPI Tübingen (Germany); URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) passes at the manifest level for the DE origin without organisational override.

## Detailed design

### Proposed `SoloAdapter` shape

```
reference/legged-runtime/src/legged_runtime/odri_solo/
├── __init__.py
├── adapter.py             # SoloAdapter (Solo 8 + Solo 12 parameterised)
├── master_board.py        # master-board firmware interface wrapper
└── manifests/
    ├── odri_solo_8.yaml
    └── odri_solo_12.yaml
```

The adapter implements URML's substrate Protocol against the master-board firmware command surface. Solo 8 (8-DOF) and Solo 12 (12-DOF, the more capable variant) get distinct manifests.

### Proposed URML v0.1 to Solo mapping

| URML primitive | Solo realisation |
|---|---|
| `move_to(pose)` | A torque-controlled joint-target command via master-board, optionally wrapped by a published controller (e.g., Inverse Dynamics or MPC). Solo can target end-effector poses for the feet; URML's `move_to` for the base pose maps to a higher-level locomotion-policy call. |
| `measure(sensor_id)` | Joint position / velocity / torque sensors at each actuator; IMU. |
| `wait_for(...)` | Polling on the master-board feedback stream with debounce. |
| `report(status)` | Per-session log file plus stdout. |
| `pose(posture_id)` | A pre-defined posture call from the published controller library. |

The crucial design observation: Solo is **torque-controlled**, not position-controlled. URML's `move_to` semantics need to be unambiguous about which side of the control boundary the primitive sits on. The RFC asks ODRI maintainers whether URML's `move_to` should target the position-level high-level controller (the policy or planner above the torque loop) or the torque-level interface directly.

### Proposed capability manifest (Solo 12)

```yaml
brand: odri_solo_12
profile: research
mobility: legged_quadruped
dof: 12
mass_kg: 2.5  # approximate; per ODRI published BOM
control_mode: torque
transport: master_board_serial
master_board:
  repo: open-dynamic-robot-initiative/master-board
sensors:
  - joint_position_per_actuator
  - joint_velocity_per_actuator
  - joint_torque_per_actuator
  - imu_6dof
gripper: none
provenance:
  origin: DE  # MPI Tübingen lead; consortium includes NYU (US), ETH (CH)
  ndaa_section_889_status: not_listed
  default_policy: pass
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none. The `control_mode: torque` field already exists in URML's capability schema; Solo is the first explicit deployment using it.
- Reference runtime: proposed new sub-package `reference/legged-runtime/src/legged_runtime/odri_solo/`. Not built in this PR.
- Conformance suite: proposed new `odri-solo-integration.yml` CI workflow.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **Torque vs position control semantics.** URML's `move_to` has not previously targeted a pure-torque-controlled substrate. The semantic disambiguation is the key open question.
- **Multi-institution maintainer cadence.** ODRI spans MPI Tübingen, NYU, ETH; review and engagement may need to thread across institutions.
- **Approximate manifest values pending publication.** Solo 12 mass and BOM specifics need maintainer confirmation.
- **Solo is a build-it-yourself research platform.** Unlike commercial quadrupeds, Solo requires assembly from the published BOM. URML's adapter assumes a built robot; the build itself is out of scope.

## Alternatives considered

1. **Ship the adapter first.** Rejected.
2. **Fold Solo into [RFC-0077 (MIT CHAMP)](0077-mit-champ-outreach.md) as another control framework.** Rejected. Solo is hardware + consortium, CHAMP is a control framework. Different abstraction layers.
3. **Cover only Solo 12 and skip Solo 8.** Rejected. Solo 8 is still in research use; both manifests are needed.

## Prior art

- `open-dynamic-robot-initiative` GitHub org (41 repos, 677 followers).
- `open-dynamic-robot-initiative/open_robot_actuator_hardware` (1.4k stars).
- `open-dynamic-robot-initiative/master-board` (133 stars, last commit 2026-05-07).
- `open-dynamic-robot-initiative/open-motor-driver-initiative` (111 stars).
- Solo 8/12 published BOM and design papers from MPI Tübingen.
- [RFC-0009](0009-legged-humanoid-mobility.md).
- [RFC-0012](0012-research-profile.md).
- [RFC-0052](0052-meta-fair-vjepa2.md), [RFC-0056](0056-stanford-aloha.md), [RFC-0075](0075-stanford-pupper-outreach.md): research-collab precedents and parallel Move #5 Tier B RFCs.

## Unresolved questions

1. **`move_to` semantics on torque-controlled hardware.** Target the high-level controller (policy / planner) above the torque loop, or the torque interface directly?
2. **Adapter home.** URML repo or `open-dynamic-robot-initiative` contributed example?
3. **Authoritative Solo 8 / Solo 12 manifest values.** DOF, mass, dimensions, BOM cost pending consortium confirmation.
4. **Cross-institution coordination.** Best contact thread across MPI / NYU / ETH for substantive design discussion?
5. **Research-publication alignment.** Is there interest in coordinating a URML conformance lane with an ODRI publication?
6. **Conformance lane.** Open to a URML conformance line on `master-board` README or ODRI documentation?
7. **Anything else.**

## Implementation note

RFC-0076 ships as a single RFC document PR. No adapter code in this PR. Research-collab framing. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from open-dynamic-robot-initiative maintainers)

1. `move_to` semantics on torque-controlled hardware.
2. Adapter home.
3. Authoritative manifest values.
4. Cross-institution coordination.
5. Research-publication alignment.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`open-dynamic-robot-initiative/master-board` is the most actively maintained core repo (133 stars, last commit 2026-05-07; verified 2026-05-24). URML's planned channel: open a single Issue on `master-board` labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit.
- [x] Motivation grounded in verified ODRI surface (41 repos, 677 followers, 1.4k-star `open_robot_actuator_hardware`).
- [x] Torque-control semantics flagged as the key open question.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, torque-vs-position semantics, multi-institution cadence, approximate values, build-it-yourself).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified as of 2026-05-24.
- [x] Provenance `origin: DE` recorded; default policy passes.
- [x] CLAUDE.md compliance check passed.
