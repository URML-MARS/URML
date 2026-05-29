---
rfc: 0239
title: Poppy Humanoid (open-hardware) integration, request for comment from poppy-project maintainers
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

# RFC-0239: Poppy Humanoid (open-hardware) integration, request for comment from poppy-project maintainers

## Summary

URML is a small open language for robot intent that compiles to whatever runtime sits below. Poppy Humanoid is an INRIA-origin open-hardware 3D-printed humanoid, historically driven through a Python control library over Dynamixel servos. The repo is not archived but the last commit is 2021-12-06 (about 4.5 years stale at time of writing) and carries no LICENSE file. This RFC acknowledges that staleness up front and asks one question. No spec change proposed, nothing for you to maintain. The founder may choose to hold rather than post this one, given the post-Nav2 fit-honest rule and the high abandonment-signal risk.

## Concrete example

An English sentence:

> Raise both arms then nod.

becomes a URML program:

```yaml
program:
  - gesture: { name: raise_arms }
  - gesture: { name: nod }
```

The Poppy Python control library dispatches each gesture to the humanoid's Dynamixel servos (`pypot.robot.Robot` setting target positions for shoulder, elbow, and neck motor groups). URML's pre-flight `validate` step reads a manifest naming the Poppy library as the bridge and the Poppy Humanoid as the platform, so the English plan is checked against the robot's joint set before any servo command is issued.

## Why URML on this target

Poppy is one of the few fully open-hardware humanoid platforms, and the URML manifest layer is the right place to declare its joint set and gesture vocabulary so an English plan can target it the same way it targets a closed commercial humanoid. The ask is light: confirm the project is still maintained, point us at the right Python-control-library entry point, ignore the rest. License clarity is part of the same question.

## Capability-manifest mapping

| URML primitive       | Poppy / pypot surface                                   |
| -------------------- | ------------------------------------------------------- |
| `gesture(name)`      | `pypot.primitive.Primitive` with named joint trajectory |
| `sit() / stand()`    | named posture primitive (community gesture library)     |
| `read_sensor(joint)` | `pypot.robot.Robot.motors[*].present_position`          |
| `set_compliant`      | `pypot.dynamixel.motor.DxlMotor.compliant`              |

## Drawbacks

- Last commit 2021-12-06 (about 4.5 years stale); high risk of an unanswered thread.
- No LICENSE file in the repo at time of writing; URML cannot ship adapter code referencing Poppy without that clarified.
- The control-library surface has shifted across `pypot`, `poppy-creature`, and `poppy-humanoid` packages over the project's lifetime; the canonical entry point in 2026 is unclear.

## Unresolved questions

Is the poppy-project still maintained, and if so what is the canonical Python-control-library entry point today (the README install list is several years old)?

## How to respond

Best channel is a GitHub Issue on `poppy-project/poppy-humanoid` (Issues are enabled). The stale-substrate framing and license-clarification ask are acknowledged in the issue's opening lines. Ledger row and full thread tracked at [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## Self-review (Phase 0)

- [x] Repo is not archived; last commit 2021-12-06 (about 4.5 years stale).
- [x] License clarification ask noted (no LICENSE file present at time of drafting).
- [x] No spec change proposed; manifest-mapping only.
- [x] Ledger row drafted in `outreach-move18.yaml`.
- [x] AI-assisted authoring disclosed (see [`VIBE.md`](../../VIBE.md)).
- [x] Stale-substrate friction acknowledged; abandonment-signal risk recorded for founder decision.
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
