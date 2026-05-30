---
rfc: 0236
title: PROS VEX V5 toolchain integration, request for comment from purduesigbots/pros maintainers
author: Ido Yahalomi (greenvh@gmail.com)
created: 2026-05-29
updated: 2026-05-29
state: Draft
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

# RFC-0236: PROS VEX V5 toolchain integration, request for comment from purduesigbots/pros maintainers

## Summary

URML is a small open language for robot intent. The URML edu-runtime already ships a VEX V5 adapter, but the adapter is toolchain-agnostic; it does not say whether the underlying C++ is compiled by PROS, VEXcode, or Robot Mesh. This RFC proposes a manifest field to declare the chosen toolchain and asks the PROS maintainers if the shape makes sense. Apache-2.0 on URML's side, no spec change proposed, nothing for you to maintain.

## Concrete example

A VRC team's English autonomous plan:

> Score four red balls in the high goal, then park.

becomes a URML program with autonomous-routine primitives:

```yaml
program:
  - move_to: { pose: ball_pickup_zone }
  - grasp: { object: red_ball, count: 4 }
  - move_to: { pose: high_goal_release }
  - release: { object: red_ball }
  - move_to: { pose: parking_zone }
```

PROS compiles the generated C++ for the V5 brain, linking against the PROS API (`pros::Motor`, `pros::adi::DigitalOut`). URML's pre-flight `validate` reads a manifest that names the toolchain so the right adapter shim is selected.

## Why URML on this target

PROS is the Purdue Sigma Bots toolchain that a large slice of competitive VRC teams already use. URML's existing VEX V5 adapter targets the V5 brain at the API level, but the same English plan can be compiled through three different toolchains (PROS, VEXcode, Robot Mesh) with different build systems and standard-library shapes. The proposal is a single manifest field, `toolchain: pros | vexcode | robot-mesh`, so adapters know which one to emit for. The ask is light: confirm the shape, point us at anything we got wrong about PROS, ignore the rest.

## Capability-manifest mapping

| URML primitive    | PROS API                                  |
| ----------------- | ----------------------------------------- |
| `move_to(pose)`   | `pros::Motor::move_absolute()` on drivetrain motors |
| `grasp(object)`   | `pros::Motor::move()` on intake, `pros::adi::DigitalOut` on pneumatic clamp |
| `release(object)` | inverse of grasp; pneumatic vent or intake reverse |
| `set_led(state)`  | `pros::adi::DigitalOut`                   |
| `read_sensor(imu)`| `pros::Imu::get_rotation()`               |

## Drawbacks

- License badge on `purduesigbots/pros` currently reads "Other", which blocks a clean Apache-2.0 composition story until clarified.
- Last commit was 2026-03-31, roughly two months stale; response cadence is unknown.
- A toolchain field in the manifest is a small spec-surface decision that future runtimes will inherit, even though no normative spec change is proposed in this RFC.

## Unresolved questions

How should a URML manifest declare PROS vs VEXcode vs Robot Mesh as the chosen toolchain, given URML's existing VEX adapter is toolchain-agnostic at the V5-brain API level?

## How to respond

Best channel is a single GitHub Issue on `purduesigbots/pros` (Issues are enabled). Use the `question` label if available. Cross-reference URML's existing VEX V5 edu-runtime adapter in the reply. Ledger row and full thread tracked at [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## Self-review (Phase 0)

- [x] License clarification flagged as an explicit drawback.
- [x] Repo is not archived; last commit 2026-03-31.
- [x] No spec change proposed; manifest-field addition only.
- [x] Ledger row drafted in `outreach-move18.yaml`.
- [x] AI-assisted authoring disclosed (see [`VIBE.md`](../../VIBE.md)).
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
