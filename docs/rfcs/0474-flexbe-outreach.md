---
rfc: 0474
title: FlexBE integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-12
updated: 2026-06-15
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

# RFC-0474: FlexBE integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's Layer-3 behavior composition. Tier B.

## Summary

[`FlexBE/flexbe_behavior_engine`](https://github.com/FlexBE/flexbe_behavior_engine) (BSD, ~72 stars, active) is a hierarchical finite-state-machine engine for ROS 2 with an operator-in-the-loop model — a human can supervise, pause, and intervene mid-behavior. URML's validate-before-actuate is a natural complement to that supervisory model: a validated typed intent is exactly what an operator wants to see and approve before a state actuates. This RFC asks how they should interop.

## The mapping (URML on FlexBE)

Two complementary seams:

- **URML lowers to a FlexBE state machine.** A validated URML program's control flow maps to FlexBE states + outcomes; URML primitives are dispatched from state execution, with the typed args + capability + envelope check verified before the behavior is started.
- **A FlexBE state dispatches a validated primitive.** A FlexBE state wraps one URML primitive so the operator-in-the-loop engine gets validate-before-actuate per state, and the validation verdict is something the operator UI can surface.

The operator-supervision model and validate-before-actuate reinforce each other: one is a human gate, the other a static gate.

## What is asked

Request for comment from the FlexBE maintainers:

1. Which seam is more natural — URML lowering to a FlexBE state machine, or a FlexBE state that dispatches a validated URML primitive?
2. Could the validation verdict (accepted / refused + reason) surface in the FlexBE operator UI before a state runs?
3. Does URML's sequence/parallel/branch/retry map cleanly onto FlexBE's hierarchical states + outcomes?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's Layer-3 behavior composition (RFC-0002) and its validate-before-actuate audit trail; the behavior-tree anchor (RFC-0470). FlexBE is the operator-in-the-loop-FSM vertex of the orchestration wave (Tier B).

## Implementation note

Outreach only. The post is a GitHub Issue on `FlexBE/flexbe_behavior_engine` (Discussions not enabled) under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (BSD). Tracked in `examples/lighthouses/outreach-move41.yaml`.

## Engagement log

**2026-06-13 — engaged (off-platform).** David Conner (Associate Professor, Christopher Newport University; directs CHRISLab; FlexBE lineage; DARPA Robotics Challenge Team ViGIR PI) reached back via LinkedIn, then email. His research is capability-based synthesis of HFSM controllers, which maps onto URML's Layer-1 capability manifest and Layer-3 behavior composition; CHRISLab runs ROS 2 on Turtlebot / Kinova / UR3e / drones, all direct URML manifest targets.

**2026-06-15 — seam chosen, worked example shipped.** Conner replied pointing to his FlexBE + behavior-tree paper ([arxiv 2203.05389](https://arxiv.org/abs/2203.05389)), where FlexBE invoked a ROS 2 action server that managed BT invocation, and to his latest paper, *Capability-based Robot Controller Synthesis* (GR(1)/Slugs/FlexBE). He proposed the concrete seam: give FlexBE **a ROS 2 action interface to URML**, then write FlexBE states that call it, demonstrated against `flexbe_turtlesim_demo`. This is **the second seam above** (a FlexBE state dispatches a validated URML program), and it is what URML built in response.

The capabilities framing aligns directly: in Conner et al. each "capability" is a state with pre/post-conditions and an outcome; a validated URML primitive is exactly such a capability, with the manifest + safety envelope as its precondition and the validation verdict as the admissibility gate an operator approves.

## Shipped: the `ExecuteURML` ROS 2 action

URML now exposes itself as a ROS 2 action so any behavior engine can drive it through validate-before-actuate. The worked example lives under [`examples/flexbe/`](../../examples/flexbe/).

- **Interface** — `urml_ros2_msgs/action/ExecuteURML.action`. Goal: a validated URML `program_yaml` **or** a natural-language `sentence`, plus `manifest_yaml`, optional `envelope_yaml`, `profiles`, `no_policy`. Result: `success`, `refused`, `reason`, `steps_executed`, `audit_log_json`, `bindings_json`. Feedback: `phase` + `detail`.
- **Server** — `urml_ros2_runtime.action_server`. The rclpy-free core `execute_request()` runs the CLI's `translate? -> validate -> execute` flow against any substrate adapter; the `URMLActionServerNode` rclpy shell serves it. Validation always runs before actuation; a rejected program returns `refused` with the verdict and nothing actuates.
- **FlexBE side** — `urml_flexbe_states.ExecuteUrmlState` calls the action and maps the result to `done` / `failed` / `refused`, surfacing the verdict to the operator; the `URML Turtle Patrol` behavior gates it behind an operator approval (collaborative autonomy), mirroring Fig. 5 of Conner et al.
- **Hermetic proof** — `reference/ros2-runtime/tests/test_action_server.py` and the `flexbe/turtle_sequence_positive` conformance fixture run the URML side with no ROS 2. The live FlexBE + turtlesim run is the gated, fail-loud `flexbe-integration` workflow.

Still outreach in spirit: no spec change, no new primitive. URML exposing a ROS 2 action and shipping FlexBE glue is a reference-runtime + example artifact, the same shape as the engagement-driven adapters (Marty, Petoi).
