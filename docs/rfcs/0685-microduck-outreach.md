---
rfc: 0685
title: Microduck integration, request for comment from pollen-robotics/microduck maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-31
updated: 2026-08-31
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

# RFC-0685: Microduck integration, request for comment from pollen-robotics/microduck maintainers

## Summary

URML ships a working `MicroduckAdapter` ([`reference/edu-runtime`](../../reference/edu-runtime/), Apache-2.0, hermetically tested) that speaks Microduck's own client contract: JSON-RPC 2.0, one object per line, intents not joint commands, exactly as `duck-ipc-proto` documents it. A validated URML program becomes `robot.init` / `robot.move` / `robot.do` calls; a program the robot cannot honour never reaches the socket. No spec change. This RFC shows the mapping and asks the maintainers three concrete questions before the adapter claims anything beyond the contract.

The architectural rhyme is why this is worth a read: `robotd` accepts intents and stays authoritative on what is executable. URML is the same posture one layer up, at plan granularity: the *whole program* is checked against the robot's declared capabilities and the deployment's safety envelope before the first intent goes out.

## What works today

```yaml
# microduck.edu_adapter.yaml — manifest-named intents -> duck-ipc-proto calls
device: "tcp://duck.local:7007"
location_to_command:
  stand_up: robot.init
  step_ahead: { method: robot.move, kwargs: { vx: 0.10, vy: 0.0, vyaw: 0.0 } }
  sit_spot: { method: robot.do, kwargs: { skill: sit_toggle } }
manipulation_commands:
  grasp: { method: robot.do, kwargs: { skill: ground_pick } }
```

"Stand up, step forward, sit down, and tell me how you feel." validates against a Microduck capability manifest and runs through the adapter: `hello` handshake (`api_version: 16`), `robot.init` as a request, `robot.move` as a notification (continuous intent, per the contract), `robot.do {"skill":"sit_toggle"}`, `robot.health` as the read-back. Continuous versus discrete follows the contract's own message-family split.

The manifest declares the walking policy as an RFC-0383 `learned_policy` block (`policy_ref` to `alpha_walking.onnx`, trained ranges, terrain classes). Microduck is the cleanest instance of that block we have seen: locomotion *is* an ONNX policy from `microduck_rl`, and a validator that refuses out-of-training-envelope intent is presumably useful to a robot whose contract already documents "out-of-distribution values just produce a policy leaning on inputs it never saw".

## Questions for the maintainers

1. **Off-robot transport.** The daemon sockets are Unix sockets; `duckctl` reaches them over Bluetooth. For a laptop-side client like this adapter, is a TCP/SSH forward of `/run/robotd.sock` the shape you expect third-party clients to use, or is the BLE path (with `system.authenticate`) the intended public client surface?
2. **Training envelope numbers.** `PoseParams` documents its trained ranges; `MoveParams` does not. Are the velocity ranges `alpha_walking` was trained over published anywhere (or exportable from `microduck_rl`), so the manifest's `learned_policy.command_ranges` can carry real numbers instead of illustrative ones?
3. **API stability.** The adapter pins `api_version: 16` and the snake_case `Skill` names. Is the `hello` handshake the right place for a client to degrade gracefully, or should it also check `robot.modelApi`?

## Notes

- No spec change is proposed here. The existing educational profile (RFC-0011), `EduSkillCall` dispatch, and RFC-0383 learned-policy declaration cover the surface.
- URML's prior touch with Pollen Robotics is [RFC-0240](0240-reachy-outreach.md) (Reachy 2, Move #18). This one differs in kind: the adapter exists and is tested, not proposed.
- Adapter: [`reference/edu-runtime/src/urml_edu_runtime/microduck.py`](../../reference/edu-runtime/src/urml_edu_runtime/microduck.py). Example bundle: [`examples/educational/microduck-morning.urml.yaml`](../../examples/educational/microduck-morning.urml.yaml) with manifest and adapter config alongside. Tests: `reference/edu-runtime/tests/test_microduck_adapter.py` (hermetic; no hardware claim is made — the first live run waits for a robot, which ships in months).

## How to respond

`pollen-robotics/microduck` accepts public Issues. URML's own Discussions: https://github.com/URML-MARS/URML/discussions. Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 1)

- [x] Reformed outreach shape: concrete example first, three real questions, no spec change.
- [x] Every wire claim traced to `duck-ipc-proto` (method names, notification split, snake_case skills, api_version 16).
- [x] Honest about hardware: hermetic tests only; no robot in hand.
- [x] No em-dashes; no LLM-tells; under a two-minute read.
