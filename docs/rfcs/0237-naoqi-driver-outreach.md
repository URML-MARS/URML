---
rfc: 0237
title: NAOqi-driver (NAO and Pepper) integration, request for comment from ros-naoqi maintainers
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

# RFC-0237: NAOqi-driver (NAO and Pepper) integration, request for comment from ros-naoqi maintainers

## Summary

URML is a small open language for robot intent that compiles to whatever runtime sits below. `ros-naoqi/naoqi_driver` is a C++ ROS-libqi bridge that covers both NAO and Pepper at the NAOqi layer, so a single engagement can land both SoftBank platforms. The repo is Apache-2.0 and not archived, but the last commit is 2024-09-17 (about 1.5 years stale at time of writing). This RFC acknowledges that staleness up front and asks the ros-naoqi maintainers a single question. No spec change proposed, nothing for you to maintain.

## Concrete example

An English sentence:

> Walk to the demo spot, wave, then sit.

becomes a URML program:

```yaml
program:
  - move_to: { pose: demo_spot }
  - gesture: { name: wave }
  - sit: {}
```

`naoqi_driver` dispatches each step into NAOqi over libqi (`ALMotion.moveTo`, `ALMotion.angleInterpolation` for the wave joint trajectory, `ALRobotPosture.goToPosture("Sit")`). URML's pre-flight `validate` step reads a manifest naming `naoqi_driver` as the bridge and the NAO or Pepper as the robot, so the English plan is checked against the platform's capabilities before any motion command leaves the host.

## Why URML on this target

NAOqi-driver is the only maintained public ROS bridge that covers both NAO and Pepper at the NAOqi/libqi layer, so a URML adapter against this surface lands both SoftBank social-humanoid platforms for one integration cost. The ask is light: read the manifest mapping, tell us if ros-naoqi is still the right venue, point out anything wrong. Apache-2.0 on both sides means composition is clean.

## Capability-manifest mapping

| URML primitive       | naoqi_driver / NAOqi surface                            |
| -------------------- | ------------------------------------------------------- |
| `move_to(pose)`      | `ALMotion.moveTo(x, y, theta)` via `cmd_vel` topic      |
| `gesture(name)`      | `ALMotion.angleInterpolationWithSpeed` (named joint set)|
| `sit() / stand()`    | `ALRobotPosture.goToPosture("Sit" / "Stand")`           |
| `play_sound(clip)`   | `ALAudioPlayer.playFile`                                |
| `read_sensor(lidar)` | `sensor_msgs/LaserScan` from `naoqi_driver`             |

## Drawbacks

- Last commit 2024-09-17 (about 1.5 years stale); maintainer responsiveness is uncertain.
- SoftBank's commercial support for NAO and Pepper has shifted over the last few years; the canonical engagement point may have moved off the ros-naoqi org.
- NAOqi is closed-source under libqi; URML's adapter cannot reach below the bridge.

## Unresolved questions

Is the `ros-naoqi` org still the canonical engagement point for NAOqi-based integrations, or has SoftBank platform support moved elsewhere since the 2024 cadence slowdown?

## How to respond

Best channel is a GitHub Issue on `ros-naoqi/naoqi_driver` (Issues are enabled). The stale-substrate framing is acknowledged in the issue's opening lines. Ledger row and full thread tracked at [`examples/lighthouses/outreach-move18.yaml`](../../examples/lighthouses/outreach-move18.yaml).

## Self-review (Phase 0)

- [x] Apache-2.0 compatibility verified (naoqi_driver is Apache-2.0).
- [x] Repo is not archived; last commit 2024-09-17 (about 1.5 years stale).
- [x] No spec change proposed; manifest-mapping only.
- [x] Ledger row drafted in `outreach-move18.yaml`.
- [x] AI-assisted authoring disclosed (see [`VIBE.md`](../../VIBE.md)).
- [x] Stale-substrate friction acknowledged; abandonment-signal risk recorded for founder decision.
- [x] Post-Nav2 structure applied: concrete example first, 1-2 questions, no compound-noun jargon, under-2-min read aloud, zero em-dashes.
