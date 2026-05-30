---
rfc: 0235
title: PyBricks LEGO MicroPython integration, request for comment from pybricks maintainers
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

# RFC-0235: PyBricks LEGO MicroPython integration, request for comment from pybricks maintainers

## Summary

URML is a small open language for robot intent. The URML edu-runtime already ships a SPIKE Prime adapter, and PyBricks is the natural firmware substrate underneath it. This RFC asks the PyBricks maintainers two short questions about license and venue, and proposes a PyBricks runtime-class declaration for the URML manifest. Apache-2.0 on URML's side, no spec change proposed, nothing for you to maintain.

## Concrete example

An English sentence from a classroom:

> Drive forward 30 cm, then beep.

becomes a URML program:

```yaml
program:
  - move_to: { pose: { x: 0.30, y: 0, theta: 0 } }
  - play_sound: { clip: beep }
```

PyBricks runs the MicroPython firmware on a LEGO SPIKE Prime hub and dispatches the two primitives to `DriveBase.straight(300)` and `Speaker.beep()`. URML's pre-flight `validate` step reads a manifest that names the hub model and the PyBricks runtime, so the English plan can be checked before the kid's robot rolls off the desk.

## Why URML on this target

PyBricks is one of the cleanest education on-ramps in robotics: real Python (well, MicroPython) on real LEGO hardware that kids already have. URML's edu-runtime already targets the SPIKE Prime API surface; PyBricks is the firmware layer below that. The proposal here is to declare PyBricks as a named runtime-class in the URML manifest so adapters can target it explicitly. The ask is light: confirm the license, point us at the right channel, ignore the rest.

## Capability-manifest mapping

| URML primitive       | PyBricks API                              |
| -------------------- | ----------------------------------------- |
| `move_to(pose)`      | `DriveBase.straight()` / `DriveBase.turn()` |
| `play_sound(clip)`   | `Speaker.beep()` / `Speaker.play_notes()` |
| `set_led(state)`     | `Light.on()` / `ColorLight.on(color)`     |
| `read_sensor(color)` | `ColorSensor.color()`                     |
| `grasp(object)`      | `Motor.run_target()` on attached gripper  |

## Drawbacks

- The license badge on `pybricks/pybricks-micropython` currently reads "Other", which blocks a clean Apache-2.0 composition story until clarified.
- Issues are disabled on the main firmware repo; routing community Q&A through `pybricks/support` adds a step.
- PyBricks targets multiple hub generations (SPIKE, EV3, BOOST, WeDo) with different motor counts; one manifest per hub is unavoidable.

## Unresolved questions

1. Is the upstream PyBricks firmware license MIT-style or something more constrained? The GitHub badge currently says "Other" and we want to get the URML manifest's runtime-class declaration right.
2. Is `pybricks/support` the right channel for a Q&A of this kind, or is there a better venue?

## How to respond

Best channel is a GitHub Issue on `pybricks/support` (Issues are enabled there; the main `pybricks-micropython` repo has Issues disabled). Ledger row and full thread tracked at [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## Self-review (Phase 0)

- [x] License clarification flagged as an explicit open question.
- [x] Repo is not archived; last commit 2026-05-28.
- [x] No spec change proposed; manifest-mapping plus runtime-class declaration only.
- [x] Ledger row drafted in `outreach-move18.yaml`.
- [x] AI-assisted authoring disclosed (see [`VIBE.md`](../../VIBE.md)).
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
