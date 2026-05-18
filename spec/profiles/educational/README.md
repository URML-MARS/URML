# Educational Profile

**Status:** Draft (v0.1)
**Targets:** URML v0.1
**Created:** 2026-05-18
**RFC:** [RFC-0011](../../../docs/rfcs/0011-educational-profile.md)

The fourth URML profile: low-cost classroom and teaching robots authored by beginners, operating near students. It **adds no new primitives** — it constrains the [twelve core primitives](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) for a conservative, fail-loud teaching posture and defines the most cautious default safety envelope of any profile.

> **Documented vs enforced (read this first).** Every constraint below is a *documented default a conformant runtime must apply*. v0.1 adds **no new validator-enforced checks** (this is deliberate; mechanical enforcement is a tracked follow-up RFC, the same staging the industrial profile used). Do not read this profile as validator-enforced in v0.1.

## Application domain

A **beginner author, a student-occupied space, a robot used to learn**. TurtleBot/ROS classrooms, Franka teaching cells, LeRobot arms, micro:bit/VEX-class platforms. The defining shape is *the author is learning, the bystanders are children, and a surprising result should stop the robot and explain itself rather than improvise*.

## In scope

- Navigation exercises in a shared classroom (`move_to` between named stations).
- Simple fetch/inspect tasks teaching `detect` + `grasp` + `release` at low force.
- Conversational lessons (`speak`/`listen`) where the home profile's speech surface is reused for teaching dialogues.
- "Run my program and watch it stop safely when it is unsure" — the pedagogical core: failure is visible and safe.

## Out of scope

- Classroom drones (v0.1 educational is ground-only; flight in a classroom is a deliberate future tightening, not a default).
- Unattended operation. Educational programs assume a supervising instructor.
- High-force manipulation. The profile caps `grasp.force` at `gentle`.

## Profile-required Layer-1 manifest fields

An educational-profile manifest **must** declare:

- **`mobility`** with a ground `drive_type` (`differential`, `omnidirectional`, `tracked`, `manipulator_base`, `quadruped`, `biped`). Flight drive types are out of scope for v0.1 educational.
- **`declared_locations`** for every place a program references. Pose-based motion is discouraged: a student edits a named station list, not coordinates.

An educational-profile manifest **should** declare:

- **`perception.object_vocabulary`** — the closed set of classes lessons use; an undeclared `detect` target fails closed (the robot stops and reports) rather than guessing.
- **`provenance:`** when the platform is procured by a public institution under rules that reach classroom hardware.

## Default safety envelope

The most conservative v0.1 profile default. Strictest-wins against the manifest.

```yaml
envelope_version: "0.1"
deployment_id: <free-form>
description: <free-form>

max_velocity: 0.3                 # m/s; well below typical platform maxima
max_grip_force_n: 5.0             # gentle ceiling regardless of gripper rating
default_on_error: abort_and_report  # student programs halt loudly, never improvise
require_supervised: true          # documented: an instructor is present
```

## Core-primitive notes

- **`grasp`** — `force` defaults to `gentle` and is capped at the envelope's `max_grip_force_n`.
- **`move_to`** — speed is capped at the envelope's `max_velocity`; motion through a declared person-occupied zone is further slowed (documented default).
- **`detect`** — an undeclared object class fails closed: the program stops with a structured `not_found`-style result, never an improvised guess. This is the profile's pedagogical safety rule.
- **error policy** — every behavior node's `on_error` defaults to `abort_and_report`. A beginner's program fails visibly.

## Compliance policy alignment

The bundled [US-federal default policy](../../../docs/rfcs/0004-compliance-policy.md) applies unchanged. Public-institution procurement of classroom robots can be subject to the same NDAA-style restrictions; an educational manifest with a covered-vendor critical component is rejected exactly as any other profile's is.

## Conformance points

v0.1 educational programs are core-primitive programs and are already exercised by the core conformance fixtures. A dedicated `conformance/fixtures/educational/` lands with the follow-up RFC that makes the constraints above validator-enforced. No fixture asserts enforcement that does not yet exist.

## Layer-4 (LLM bridge) integration

The educational profile is where the bridge's *explain-what-it-will-do-before-doing-it* behavior matters most: a teaching deployment should surface the generated URML back to the student in plain language before execution. That is a bridge-side affordance, not normative to this profile, but it is the profile most likely to drive it.
