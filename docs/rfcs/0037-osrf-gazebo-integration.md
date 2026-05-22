---
rfc: 0037
title: OSRF / Gazebo Sim integration — proposal-only RFC (no shipping adapter); request for comment from gazebosim maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-22
updated: 2026-05-22
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

# RFC-0037: OSRF / Gazebo Sim integration — proposal-only RFC; request for comment from gazebosim maintainers

## Summary

URML does not yet ship a Gazebo-Sim adapter. This RFC **proposes** the integration shape for a future `urml-gazebo-runtime` reference adapter sitting on top of `gazebosim/gz-sim` (the modern Gazebo successor to gazebo-classic). It documents the URML v0.1 primitive-to-Gazebo Transport mapping URML would adopt, and **requests review and feedback from the gazebosim / Open Robotics maintainers** on the proposed mapping, on the strategic alignment with OSRF, and on whether OSRF would be open to the long-term institutional path documented in URML's [`GOVERNANCE.md`](../../GOVERNANCE.md) (the Phase-3 structural-separation question). No spec change.

This is a **proposal-only RFC** — distinct from RFCs 0023–0036 which document already-shipping adapters / manifests. The "no shipping adapter" posture follows the Optimus/Figure/Apollo precedent (manifest+spec-only when the runtime artifact is not yet built) and [RFC-0020](0020-autoware-av-substrate.md) (Autoware AV).

## Motivation

Gazebo Sim is *the* canonical robotics-simulation substrate in the ROS ecosystem. URML's reference runtimes already pass the URML conformance suite hermetically (via `MockROSAdapter`); a Gazebo-Sim-backed conformance lane would prove URML programs survive in a high-fidelity physics-and-sensor simulation, validating the substrate-neutral Protocol at the simulator boundary.

The strategic motivation goes further. OSRF (Open Source Robotics Foundation) is documented in [`GOVERNANCE.md`](../../GOVERNANCE.md) as one candidate Phase-3 structural-separation home for URML when the foundation question becomes live. A successful Gazebo-Sim integration is the most natural technical lead-in to that institutional conversation — proving the engineering alignment before the foundation conversation.

The `gazebosim/gz-sim` repo is **active**, Discussions enabled (plus a strong Discourse community via `robotics.stackexchange.com` / Gazebo's classic forum). The maintainer team is the OSRF / Open Robotics core, making this RFC's audience institutionally significant.

## Detailed design

This is a forward-looking proposal. URML's existing artifacts that would feed into `urml-gazebo-runtime`:

- `reference/ros2-runtime/.../substrate/base.py` — the frozen `ROSAdapter` Protocol that any new adapter must implement.
- `reference/ros2-runtime/.../substrate/rclpy_adapter.py` — the existing ROS 2 adapter the Gazebo adapter could compose (since gz-sim runs alongside ROS 2 via the `ros_gz_bridge`).
- `reference/mujoco-runtime/` — the closest sibling (a non-ROS physics simulator adapter); the architectural shape Gazebo would inherit.
- `reference/isaac-runtime/` — the other simulator sibling (NVIDIA Isaac Sim/Lab); proves URML's pattern accommodates multiple sim backends already.

### Proposed `urml-gazebo-runtime` shape

A new `reference/gazebo-runtime/` package mirroring `reference/mujoco-runtime/`:

- `GazeboAdapter` class implementing `ROSAdapter`, with `BRAND = "gazebo"`.
- Two construction paths to consider:
  1. **Compose `RclpyAdapter`** — talk to gz-sim via `ros_gz_bridge` (the conventional ROS 2 + Gazebo deployment). Simplest path; reuses everything.
  2. **Direct `gz transport`** — bind to Gazebo's native `gz-transport13` Python bindings without a ROS dependency. The [RFC-0014](0014-substrate-conformance.md) zero-ROS acid test would pass: URML programs in Gazebo without ROS.

URML's preference (subject to OSRF feedback): **support both, default to the ROS 2 path, document the zero-ROS path as a deployment option**. This mirrors how the UR integration (RFC-0024) ships two adapters for the same robot — Gazebo's two paths are an analogous demo.

### Proposed URML v0.1 → Gazebo Sim primitive mapping

| URML v0.1 primitive | Gazebo realisation |
|---|---|
| `move_to` / `hover` | A control plugin (`ignition::gazebo::systems::JointPositionController` / `DiffDrive` / equivalent) consumes a goal pose published on a gz-transport topic. |
| `grasp` / `release` | A `JointController` plugin on the gripper joints, gated by an explicit Gazebo-side fixed-joint attach (or detachment) on contact. |
| `measure` | Subscribe to a Gazebo sensor topic (Force/Torque plugin, IMU plugin, etc.). |
| `wait_for` (event / threshold / signal) | Subscribe to a Gazebo topic; latch on first matching message. |
| `wait` (passive dwell) | Host-side sleep. |
| `report` (structured status upstream) | Publish on a configured topic (`ros_gz_bridge`-mapped if running with ROS). |
| `dock` / `detect` / `scan` / `capture` / `speak` / `listen` | Substrate-dependent on what plugins the world declares; defaults to companion-adapter pattern when not directly supported by a plugin. |
| `take_off` / `land` / `return_to_home` (drone profile) | Gazebo + ArduPilot SITL or PX4 SITL plugin; URML's existing `PX4Adapter` (`reference/px4-runtime/`) is the canonical drone path. Gazebo provides the world; `PX4Adapter` provides the flight stack. |
| `pick_from` / `place_at` / `swap_tool` (industrial profile, RFC-0013) | Composed Layer-3 sequences over the methods above; no new Protocol method. |

### Proposed conformance integration

Mirror `mujoco-integration.yml` / `isaac-integration.yml` gating: a `URML_GAZEBO_INTEGRATION=1` env-gated workflow runs the conformance suite against a `GazeboAdapter` driving a `gz-sim` world (TurtleBot 4 + Nav2 demo world, e.g.). The hermetic in-tree suite continues to use `MockROSAdapter`.

### Compatibility notes

- **Gazebo versions.** `gazebosim/gz-sim` (Garden / Harmonic / Ionic / Jetty) is the modern lineage. Gazebo Classic (`osrf/gazebo`, archived) is out of scope — URML targets the modern Gazebo path.
- **ROS 2 distros.** Humble / Iron / Jazzy via `ros_gz_bridge`. The zero-ROS `gz-transport` path is distro-agnostic by definition.
- **Origin.** Open Robotics / OSRF, San Francisco, CA, USA; passes the US-federal default policy without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: **proposed new package** `reference/gazebo-runtime/`. Not built in this PR; the RFC requests OSRF feedback first.
- Conformance suite: **proposed new** `gazebo-integration.yml` CI workflow + a `URML_GAZEBO_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0; purely additive when implemented (RFC adds zero changes to existing artifacts).

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** RFCs 0023–0036 reference real code; RFC-0037 references a proposal. The honest framing: URML wants OSRF input *before* committing to an implementation path, given the institutional alignment stakes. The Optimus / Figure / Apollo precedent (manifest+spec-only when the runtime isn't built yet) covers this posture.
- **Two-path complexity.** Supporting both ROS 2-bridged and zero-ROS `gz-transport` paths doubles the surface area. The UR dual-adapter precedent (RFC-0024) shows it's achievable but adds maintenance cost.
- **Institutional dimension is delicate.** OSRF / Open Robotics relationship is more political than technical; the RFC must not over-promise the foundation conversation. Documented carefully here.

## Alternatives considered

1. **Ship the adapter first, ask OSRF later.** Rejected: the institutional alignment opportunity is the asymmetric value; building first risks landing the wrong adapter shape and having to rework it after feedback.
2. **Skip OSRF entirely until URML un-halts launch.** Rejected: the Phase-3 foundation conversation is years away anyway; technical alignment now costs nothing and seeds the relationship.
3. **Single-path adapter (ROS 2 only).** Rejected: the zero-ROS path is exactly what makes URML asymmetrically valuable to Gazebo's community (and to URML's RFC-0014 acid test). Both are worth pursuing.

## Prior art

- `gazebosim/gz-sim` — the upstream simulator.
- `osrf/gazebo` — Gazebo Classic (archived, for context).
- `gazebosim/ros_gz` — ROS-Gazebo bridge.
- `reference/mujoco-runtime/` — URML's existing physics-simulator sibling.
- `reference/isaac-runtime/` — URML's other simulator sibling.
- [RFC-0020](0020-autoware-av-substrate.md) — proposal-only RFC precedent.
- [`GOVERNANCE.md`](../../GOVERNANCE.md) §Phase 3 — the OSRF / foundation-home documentation.
- RFC-0023..0036 for the per-vendor RFC pattern.

## Unresolved questions

Provisional pending gazebosim / Open Robotics maintainer feedback:

1. **Bridge vs. native.** Does Open Robotics prefer URML's adapter to compose `RclpyAdapter` (`ros_gz_bridge` path) or to bind `gz-transport` directly (zero-ROS path)? Or both, as URML proposes?
2. **World / model alignment.** Should URML publish reference Gazebo worlds (TurtleBot 4 + Nav2 demo, industrial cell, drone arena) alongside its conformance fixtures?
3. **Conformance gate.** Would Open Robotics review a proposed `gazebo-integration.yml` workflow and the URML conformance suite for adoption as a Gazebo-side health check?
4. **Foundation alignment.** Is OSRF open to long-term institutional conversation about URML as a project that could be sponsored under or aligned with OSRF in a future structural-separation? (Exploratory only — not a Phase-0 commitment.)
5. **Anything else.**

## Implementation note

RFC-0037 ships as a single RFC document PR. **No adapter code in this PR.** The actual `reference/gazebo-runtime/` package follows in a later session, gated on OSRF feedback. Draft state.

## Requested feedback (from gazebosim / Open Robotics maintainers)

1. **Soundness of the proposed mapping** above.
2. **Bridge-vs-native architecture preference.**
3. **Reference-world publication interest.**
4. **Conformance-suite alignment for Gazebo CI.**
5. **Institutional / OSRF alignment** (exploratory).
6. **Anything else.**

## How to respond

URML public Discussions:

> https://github.com/URML-MARS/URML/discussions

Or open Discussions on `gazebosim/gz-sim` linking back, or post on the Gazebo Community forum / robotics.stackexchange.

Private channel: `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only).
- [x] Motivation grounded in concrete technical alignment + institutional Phase-3 dimension.
- [x] Detailed design proposes a runtime package, names mapping table, and lists two architectural paths.
- [x] At least one alternative considered (three are — ship-first, skip-OSRF, single-path).
- [x] Drawbacks are real (proposal-only weaker artifact; two-path complexity; institutional delicacy).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added (mapping is to existing primitives).
- [x] Implementation note explicitly says NO adapter code in this PR; later session contingent on feedback.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. The institutional dimension is documented (per GOVERNANCE.md) but the RFC does not commit URML to any partnership / sponsorship / re-licensing; the foundation conversation is explicitly exploratory.
