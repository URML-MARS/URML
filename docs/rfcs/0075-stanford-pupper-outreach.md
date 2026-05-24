---
rfc: 0075
title: Stanford Pupper integration, research-collab proposal to stanfordroboticsclub maintainers
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

# RFC-0075: Stanford Pupper integration, research-collab proposal to stanfordroboticsclub maintainers

## Summary

URML does not yet ship a Stanford Pupper integration. This RFC proposes a `StanfordPupperAdapter` under [`reference/legged-runtime/`](../../reference/legged-runtime/) targeting [`stanfordroboticsclub/StanfordQuadruped`](https://github.com/stanfordroboticsclub/StanfordQuadruped) (1.7k stars, MIT, Python 98.9%, Pupper v1 / v2) and the Pupper v3 line (Raspberry Pi 5 + 400W brushless motors + Luxonis SR depth camera, where it has separate-repo presence). URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`, plus posture composition) map onto the Pupper Python control surface without changes upstream. No spec change on URML's side. This is a **research-collab proposal** following the precedent of [RFC-0052 (Meta FAIR V-JEPA 2)](0052-meta-fair-vjepa2.md) and [RFC-0056 (Stanford ALOHA)](0056-stanford-aloha.md) because the maintainer is a Stanford student club, not a commercial vendor.

This is the fifth Move #5 RFC and the first Tier B (research-collab) entry in the wave.

## Motivation

Stanford Pupper is the canonical academic-club open-source quadruped: 1.7k stars on the original `StanfordQuadruped` repo, MIT-licensed, $1.5–$2k build cost, used in Stanford CS-225a / EE-148-style coursework and replicated in dozens of university maker spaces globally. The platform sits below Move #3's Petoi Bittle in cost (Pupper assembles from off-the-shelf hobby servos rather than custom firmware) but above it in capability (12-DOF brushed or brushless, Raspberry Pi compute, sub-$2k vs Bittle's $299 stock). For URML, the value is the **education-via-construction** audience: students who build their own quadruped from a published BOM and want a substrate-neutral programming abstraction to share between Pupper, Bittle, MIT CHAMP-supported research quadrupeds, and commercial platforms.

Two things make this RFC concrete rather than aspirational. First, `stanfordroboticsclub/StanfordQuadruped` has 1.7k stars, MIT license, Issues enabled (21 open at time of writing), Python 98.9% with the main program `run_robot.py` and joystick-interface plus hardware-control modules in Python. Second, the README notes "end-of-life status, with development shifting to Pupper v3" featuring Raspberry Pi 5 + 400W GIM4305 brushless motors + Luxonis depth camera; URML's adapter should target both the legacy v1/v2 surface (still in active classroom use) and the v3 line (active development).

Stanford Robotics Club's posture is fully open: MIT license, English-first README, US-domiciled. URML's open-core commitment lands without translation. The maintainer is a student organisation, so the RFC's frame is research-collaborative rather than vendor-pitching.

## Detailed design

### Proposed `StanfordPupperAdapter` shape

```
reference/legged-runtime/src/legged_runtime/stanford_pupper/
├── __init__.py
├── adapter_v1_v2.py            # Pupper v1 / v2 (StanfordQuadruped)
├── adapter_v3.py               # Pupper v3 (gated on stable v3 repo)
├── gait_library.py             # mapping URML primitives to Pupper gait calls
└── manifests/
    ├── stanford_pupper_v1.yaml
    ├── stanford_pupper_v2.yaml
    └── stanford_pupper_v3.yaml
```

### Proposed URML v0.1 to Stanford Pupper mapping

| URML primitive | Pupper realisation |
|---|---|
| `move_to(pose)` | A trot / walk command via `StanfordQuadruped`'s `run_robot.py`-equivalent surface. Direction + speed scaling, mirroring URML's [RFC-0062 Petoi](0062-petoi-bittle-outreach.md) skill-library pattern. |
| `measure(sensor_id)` | IMU on Pi 4 / Pi 5, joint-state via the servo bus, optional Luxonis depth camera (v3). |
| `wait_for(...)` | Polling on sensor stream with debounce. |
| `report(status)` | Per-session log file plus stdout. |
| `pose(posture_id)` | A named-pose call (`sit`, `stand`, `lay_down`) from the Pupper gait library. |

### Proposed capability manifest (v3 example)

```yaml
brand: stanford_pupper_v3
profile: educational
mobility: legged_quadruped
dof: 12
mass_kg: 4.0  # approximate; v3 spec pending confirmation
transport: python_local
python_module: stanford_pupper_v3  # path TBD pending stable v3 repo
controller: raspberry_pi_5
sensors:
  - imu_6dof
  - depth_camera_luxonis_sr
gripper: none
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/legged-runtime/src/legged_runtime/stanford_pupper/`. Not built in this PR.
- Conformance suite: proposed new `stanford-pupper-integration.yml` CI workflow.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **End-of-life on v1/v2.** The legacy repo is in maintenance mode while v3 development happens elsewhere. URML's adapter against the legacy surface has shrinking real-world relevance.
- **v3 repo location not surfaced from the legacy README.** The RFC asks the maintainers to confirm the canonical Pupper v3 repo path.
- **Approximate v3 manifest values.** Mass, DOF, height pending maintainer confirmation.
- **Student-club maintainer cadence.** Stanford Robotics Club's review and engagement cadence is academic-calendar driven; the wait window for response may exceed the 14-day window URML uses for vendor RFCs.

## Alternatives considered

1. **Ship the adapter first.** Rejected.
2. **Target only v1/v2 (the canonical 1.7k-star repo) and skip v3.** Rejected. V3 is the actively developed line.
3. **Fold Pupper into [RFC-0062 (Petoi)](0062-petoi-bittle-outreach.md) as another DIY quadruped.** Rejected. Different audiences (Stanford Robotics Club education vs. global maker hobbyist).

## Prior art

- `stanfordroboticsclub/StanfordQuadruped` (1.7k stars, MIT, Python 98.9%, 21 open issues, v1/v2 line).
- Pupper v3 announcement (Raspberry Pi 5 + 400W brushless + Luxonis SR; repo location pending verification).
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md).
- [RFC-0052](0052-meta-fair-vjepa2.md), [RFC-0056](0056-stanford-aloha.md): research-collab framing precedents.
- [RFC-0062](0062-petoi-bittle-outreach.md): the parallel DIY-quadruped Move #3 RFC at a different price tier.

## Unresolved questions

Provisional pending stanfordroboticsclub maintainer feedback:

1. **Canonical Pupper v3 repo.** Where does v3 live on GitHub?
2. **Authoritative v3 manifest values.** DOF, mass, height, sensor inventory pending maintainer confirmation.
3. **Adapter home.** URML repo, contributed example under `stanfordroboticsclub`, both?
4. **Coursework integration.** Is there interest in including URML primitive emission in CS-225a or related Pupper-using courses?
5. **v1/v2 vs v3 priority.** Should URML's adapter prioritise the v3 line, the legacy v1/v2 surface, or both equally?
6. **Conformance lane.** Open to a URML conformance line in the Pupper README or course materials?
7. **Anything else.**

## Implementation note

RFC-0075 ships as a single RFC document PR. No adapter code in this PR. Research-collab framing, not vendor-pitch. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from stanfordroboticsclub maintainers)

1. Canonical Pupper v3 repo location.
2. Authoritative v3 manifest values.
3. Adapter home.
4. Coursework integration interest.
5. v1/v2 vs v3 priority.
6. Conformance-lane interest.
7. Anything else.

## How to respond

`stanfordroboticsclub/StanfordQuadruped` has Issues enabled (21 open; verified 2026-05-24). URML's planned channel: open a single Issue on `stanfordroboticsclub/StanfordQuadruped` labelled with the closest `enhancement` or `discussion` equivalent, pointing to this RFC. If the club prefers a different surface (a Stanford-internal mailing list, a course wiki, a v3 repo), the thread will follow their preference.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Research-collab framing explicit in Summary.
- [x] Motivation grounded in verified `stanfordroboticsclub/StanfordQuadruped` surface.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, end-of-life v1/v2, v3 location unconfirmed, approximate v3 values, student-club cadence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified as of 2026-05-24.
- [x] Provenance `origin: US` recorded; default policy passes.
- [x] CLAUDE.md compliance check passed.
