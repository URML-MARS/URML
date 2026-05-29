---
rfc: 0234
title: Webots simulator integration, request for comment from cyberbotics/webots maintainers
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

# RFC-0234: Webots simulator integration, request for comment from cyberbotics/webots maintainers

## Summary

URML is a small open language for robot intent that compiles to whatever runtime sits below. Webots is the first sim-substrate outside Gazebo that URML proposes to target. This RFC asks the Webots maintainers to look at the proposed manifest mapping and tell us if the scene-model declaration shape is sensible. Apache-2.0, no spec change proposed, nothing for you to maintain.

## Concrete example

An English sentence:

> Patrol two waypoints then dock.

becomes a URML program:

```yaml
program:
  - move_to: { pose: waypoint_a }
  - move_to: { pose: waypoint_b }
  - send_docking_goal: { dock_id: home }
```

Webots simulates a Pioneer 3-AT (or NAO, or Khepera IV) following the trajectory. URML's pre-flight `validate` step reads a manifest that names Webots as the substrate and the chosen scene's robot model, so an English plan can be checked against the simulated robot's capabilities before it ever runs.

## Why URML on this target

Webots is a clean fit for URML's pre-flight validator role. The Cyberbotics team ships dozens of model archetypes (NAO, Pioneer, Khepera, drones), each with different capability surfaces. URML's manifest layer is exactly the place to say "this scene uses the Pioneer 3-AT, so `move_to` is grounded and `grasp` is not." The ask here is light: read the proposed mapping, point out anything wrong, ignore the rest. Apache-2.0 on both sides means the composition is straightforward.

## Capability-manifest mapping

| URML primitive          | Webots scene-level surface                          |
| ----------------------- | --------------------------------------------------- |
| `move_to(pose)`         | `wb_supervisor_field_set_sf_vec3f` on robot translation, or differential-drive controller |
| `send_docking_goal`     | scene-defined dock node, controller-side navigation |
| `play_sound(clip)`      | `wb_speaker_play_sound`                             |
| `read_sensor(lidar)`    | `wb_lidar_get_range_image`                          |
| `set_led(state)`        | `wb_led_set`                                        |

## Drawbacks

- Webots scenes are heterogeneous; one manifest per scene is unavoidable.
- The Webots controller-API surface is large; URML only needs a small subset, which may look arbitrary to a Webots user.
- URML's static validator cannot catch dynamic scene mutations (objects added at runtime).

## Unresolved questions

What is the canonical way to declare a Webots scene's robot model in a third-party manifest, given Webots ships many model archetypes and a single `.wbt` file can contain multiple robots?

## How to respond

Best channel is a GitHub Discussion on `cyberbotics/webots` (Discussions are enabled on the repo). Ledger row and full thread tracked at [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## Self-review (Phase 0)

- [x] Apache-2.0 compatibility verified (Webots is Apache-2.0).
- [x] Repo is not archived; last commit 2026-05-28.
- [x] No spec change proposed; manifest-mapping only.
- [x] Ledger row drafted in `outreach-move18.yaml`.
- [x] AI-assisted authoring disclosed (see [`VIBE.md`](../../VIBE.md)).
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
