---
rfc: 0024
title: Universal Robots integration — same robot, two URML adapters; request for comment from UniversalRobots maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-22
updated: 2026-08-27
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

# RFC-0024: Universal Robots integration — same robot, two URML adapters; request for comment from UniversalRobots maintainers

## Summary

Universal Robots is the only vendor in URML's Move #1 lighthouse program where the repository ships **two independent reference adapters for the same physical robot**: `UrAdapter` (over ROS 2 + MoveIt 2 via `ur_robot_driver`) and `UrRtdeAdapter` (over the vendor-native RTDE Python SDK with **zero ROS dependency**). The same URML program, validator, manifest, and conformance fixture work against both adapters with identical audit traces. This RFC documents the dual mapping, the substrate-neutrality acid test that UR uniquely realises, and **requests review and feedback from the `UniversalRobots` GitHub organization maintainers** — both for the ROS 2 driver (`UniversalRobots/Universal_Robots_ROS2_Driver`) and the RTDE Python client (`UniversalRobots/RTDE_Python_Client_Library`). No spec change is proposed here.

## Motivation

UR is the largest-installed-base collaborative arm vendor in the world, and the UR+ developer ecosystem co-markets several URML-integrated component vendors (Robotiq, OnRobot, Piab, SCHUNK). Successful alignment with UR halos to those Tier-1 / Tier-2 component vendors automatically.

More importantly for URML's design discipline: UR is the **unique vendor in the Tier-1 set where URML demonstrates the [RFC-0014](0014-substrate-conformance.md) zero-ROS acid test on a real product**, not just a sim. The Yaskawa / KUKA / FANUC / Stäubli / Mitsubishi / Kawasaki / Denso integrations all flow through the ROS 2 path; UR is the proof that URML's substrate-neutral Protocol survives the absence of ROS entirely on actual hardware. That property is asymmetrically valuable to UR — it documents publicly that the same URML program a customer writes against a ROS 2 UR cell can run unmodified against a UR cell driven by RTDE, which is the most common deployment topology for UR+ ecosystem partners shipping vendor-native integrations.

The case for filing this RFC publicly is the same as RFC-0023 (Yaskawa): correctness review by the actual vendor maintainers, and an invitation to become a conformance-listed runtime per [RFC-0014](0014-substrate-conformance.md).

## Detailed design

RFC-0024 is descriptive of existing URML artifacts plus an explicit feedback ask. No spec text changes.

### Two adapters, one robot, one URML program

URML ships two first-class UR adapters:

| Adapter | Package | Substrate | Vendor SDK / Driver | Bridge type |
|---|---|---|---|---|
| `UrAdapter` | `urml-industrial-arm-runtime` | ROS 2 (`rclpy`) + MoveIt 2 | `UniversalRobots/Universal_Robots_ROS2_Driver` (`ur_robot_driver`) | Host-side bridge; composes `RclpyAdapter` |
| `UrRtdeAdapter` | `urml-cobot-runtime` | Zero ROS | `UniversalRobots/RTDE_Python_Client_Library` (`ur_rtde` / `rtde_control` + `rtde_receive`) | Host-side bridge; lazy `_open()` over RTDE control + receive interfaces |

Both implement the same substrate-neutral `ROSAdapter` Protocol (`reference/ros2-runtime/src/urml_ros2_runtime/substrate/base.py`). The conformance fixture `conformance/fixtures/industrial/08_cobot_cell_positive.yaml` passes against both. The same `cobot_cell.yaml` manifest (with vendor `universal_robots`, country `DK`, Teradyne-US parent — declared in the description and the provenance block) drives both.

This is the substrate-neutrality acid test from [RFC-0014](0014-substrate-conformance.md), realised on real hardware: not "URML in principle survives without ROS" but "**this URML program survives without ROS on a UR5e in your shop today.**"

### URML v0.1 → UR primitive mapping (both paths)

| URML v0.1 primitive | `UrAdapter` (ROS 2) | `UrRtdeAdapter` (zero ROS) | Notes |
|---|---|---|---|
| `move_to` (named location → pose) | MoveIt 2 plan + `control_msgs/FollowJointTrajectory` via `ur_robot_driver` | `rtde_control.RTDEControlInterface.moveL(vec, speed)` after `CobotConfig.resolve_location(name)` | Named-pose semantics identical; planner differs. |
| `hover` (station-keeping pose) | Same as `move_to` to a declared home_pose | Same as `move_to` to a declared home_pose | Fixed-base arm; `hover` ≡ `move_to` for industrial profile. |
| `grasp` | `control_msgs/GripperCommand` on the deployment-declared gripper server; **no brand default is baked in** (`_BRAND_GRIPPER_SERVER["ur"]` unset). Robotiq's `/ur/robotiq_gripper/gripper_cmd` is documented as one example only, and note there is no official vendor-maintained ROS 2 Robotiq driver (what exists is community-maintained). | `_open()` is sufficient at v0.1 fidelity; scalar `force_n` returned via `ManipulationResult.grip_force_n` | RTDE path does not currently command a specific gripper out of the box (UR+ ecosystem ships per-gripper SDKs on top of RTDE — a v0.1 SPEC-GAPS item, [RFC-0017](0017-digital-io-actuation.md) covers raw digital-I/O tool actuation). |
| `release` | Same `GripperCommand` action | Same as `grasp` — `_open()` + `ManipulationResult(success=True)` | |
| `measure` | One-shot read from `/joint_states` or a wrench topic | `rtde_receive.RTDEReceiveInterface.getActualTCPForce()` | RTDE exposes TCP force directly; ROS 2 path uses MoveIt 2 / `wrench` topics. |
| `wait_for` (event / threshold / signal) | Block on a ROS topic / latched event | One-shot RTDE read returning `WaitResult(success=True, timed_out=False)` | Threshold-watch via polling on RTDE is a candidate refinement (SPEC-GAPS), not invented here. |
| `wait` (passive dwell) | Host-side sleep | Host-side sleep | Identical. |
| `report` (structured status upstream) | Publish on configured `outputs.named_endpoints` topic | Append to in-memory `_reports` list; flush is a host-side concern | UR cells typically report to a PLC; both paths accept the same Layer-3 `report` step. |
| `dock` | Returns `not_supported_on_industrial_arm[ur]: …no docking station` (UR5e/UR10e bare arms) | Returns `not_supported_on_bare_cobot: …no docking station` | Pair with a docking-station companion; RFC-0013 `swap_tool` rides this when a tool-change station is declared. |
| `detect` | Returns `not_supported_on_industrial_arm[ur]: …no onboard perception` | Returns `not_supported_on_bare_cobot: …no onboard detection` | Companion-adapter pattern. URML's `cobot_cell.yaml` declares a wrist-mounted RGB camera and routes `detect` through a companion. |
| `scan`, `capture`, `speak`, `listen`, `take_off`, `land`, `return_to_home` | All return the appropriate `not_supported_on_industrial_arm[ur]` sentinel | All return the appropriate `not_supported_on_bare_cobot` or `not_applicable_cobot` sentinel | Industrial / cobot profile programs do not invoke these primitives. |
| `pick_from` (RFC-0013) | Composed: `send_navigation_goal(source)` → `query_detection` (companion) → `send_manipulation_goal(action="grasp", force_n=...)` | Same composition; same Protocol methods | Conformance fixture `industrial/08_cobot_cell_positive.yaml` exercises this end-to-end. |
| `place_at` (RFC-0013) | Composed: `send_navigation_goal(target)` → `send_manipulation_goal(action="release", release_mode=...)` | Same | |
| `swap_tool` (RFC-0013) | `send_docking_goal(station=..., service="swap_tool")` → FollowJointTrajectory to tool-change pose | `send_docking_goal(...)` — RTDE adapter returns `not_supported_on_bare_cobot` unless a `docking_stations[]` with `services: [swap_tool]` is declared and a tool-change routine is wired (deployment-specific) | UR+ tool-change stations (Robotiq AGC, ATI QC) are common; the RFC-0013 design does not require a new Protocol method. |

A bare UR cell (UR5e / UR10e + a manifest-declared UR+ gripper, Robotiq 2F-85 as one example + wrist RGB camera) with RFC-0013 industrial primitives is expressible today through **either** adapter and validates ACCEPTED under the bundled US-federal default compliance policy ([RFC-0004](0004-compliance-policy.md)) — Denmark (DK) origin + Teradyne (US) parent passes; `universal_robots` is not on the denylist.

### Substrate-neutrality demonstration — the unique-on-UR proof

The conformance fixture `conformance/fixtures/industrial/08_cobot_cell_positive.yaml` parametrizes over `adapter_factory`. Three runs:

1. **MockROSAdapter** — the default hermetic mock (CI green today).
2. **`UrAdapter` via gated `industrial-arm-integration.yml`** — same program, ROS 2 + MoveIt 2 + `ur_robot_driver`, identical audit trace.
3. **`UrRtdeAdapter` via gated `cobot-integration.yml`** — same program, **zero ROS**, identical audit trace.

That third run is the [RFC-0014](0014-substrate-conformance.md) zero-ROS acid test passing on real Universal Robots hardware. No other Tier-1 vendor in the lighthouse program currently has both adapters; UR is the asymmetric proof.

The PRs that built this proof: Track A (industrial-arm-runtime baseline including `UrAdapter`), Track B (cobot-runtime including `UrRtdeAdapter`), Track H1 / I-H (claims-audit reconciliation that traces these). The architecture is documented in `reference/cobot-runtime/src/urml_cobot_runtime/adapter.py` (module docstring).

### Compatibility notes

- **UR controllers.** `UrAdapter` and `UrRtdeAdapter` both target the URe-series controllers (CB3 deprecated; e-Series and PolyScope 5.x recommended). Future PolyScope X migration is out of scope for v0.1 — the RTDE protocol is the stability anchor.
- **PolyScope versions.** `ur_rtde >=1.5,<2` (the pinned RTDE Python client) supports PolyScope 5.4 and later. The ROS 2 path requires `ur_robot_driver >=2.0` for ROS 2 Humble / Iron / Jazzy.
- **MoveIt 2 dependency.** Only the ROS 2 path; the RTDE path is fully MoveIt-free.
- **Gripper coupling.** No brand gripper is assumed as a default. The gripper is declared in the manifest and routed through a companion adapter at the deployment layer; Robotiq 2F-85 is documented as one example among many UR+ options (OnRobot RG2 / RG6 / VG10, Schmalz vacuum, Piab vacuum, Soft Robotics). Baking in a brand default was avoided per UR maintainer feedback (2026-08-27): the UR+ catalogue is broad, deployments pick from it, and there is no official vendor-maintained ROS 2 Robotiq driver, so a spec default would couple to a community dependency neither project controls. The URML manifest fixture for any of those grippers is already shipping (see RFC-0031 SCHUNK, the forthcoming RFC-0032..0036 parts RFCs).
- **Origin.** Universal Robots A/S, Odense, Denmark; Teradyne (US) parent since 2015. DK + Teradyne-US passes the US-federal default policy ([RFC-0003](0003-us-alignment.md) / [0004](0004-compliance-policy.md)) without flagging.

### Spec changes

None. RFC-0024 is descriptive of the existing v0.1 Protocol and its two UR adapter realisations.

### Validator changes

None.

### Reference runtime changes

None for the existing `UrAdapter` or `UrRtdeAdapter`. A brand-named manifest fixture `ur_cell.yaml` is added in the same PR for symmetry with the Track-A / Track-I-A brands; `cobot_cell.yaml` (the original) stays as the cobot-runtime canonical fixture so the conformance suite remains stable. A new conformance fixture exercising the brand-named manifest is added.

### Conformance suite changes

One new positive fixture under `conformance/fixtures/industrial/` exercising the RFC-0013 `pick_from`/`place_at` happy path on a UR-branded cell against `MockROSAdapter`. One additional `MANIFEST_REGISTRY` entry. The brand-agnostic conformance assertions stay unchanged.

## Backward compatibility

Pre-v1.0; purely additive (new RFC doc + new manifest + new conformance fixture). Cannot break prior URML behaviour.

## Drawbacks

- **Two-adapter cognitive load.** Documenting both paths makes the RFC longer than the single-adapter Yaskawa RFC-0023. The trade-off is that the dual mapping is what makes UR uniquely valuable to URML's substrate-neutrality story; abbreviating it would understate UR's role.
- **Same vendor, two communities to engage.** The ROS 2 driver community and the RTDE Python community are largely overlapping but not identical; the feedback ask spans both repos, which may diffuse a single conversation thread.
- **PolyScope X transition risk.** Universal Robots is migrating to a new controller platform (PolyScope X). The RTDE protocol is expected to remain, but a long-horizon spec drift could require RFC revisions; documented here for honesty.

## Alternatives considered

1. **One RFC per adapter** (RFC-0024 ROS 2 UR + RFC-0024b RTDE UR). Rejected: the substrate-neutrality story is the *combination*; splitting them would lose the asymmetric value UR brings.
2. **Merge UR and Yaskawa RFCs into a single "ROS-Industrial big-four" RFC.** Rejected for the same reason RFC-0023 was filed separately: per-vendor RFCs are individually citable and individually closeable when each vendor responds.
3. **Defer the brand-named `ur_cell.yaml` manifest.** Rejected: every Track-A / Track-I-A brand has one; UR not having one was a symmetry gap from the v0.1 era, and this RFC's PR is the natural place to close it.

## Prior art

- The Universal Robots developer hub (`universal-robots.com/developer`), the UR+ partner ecosystem, and the public RTDE protocol specification.
- The ROS-Industrial Consortium's `Universal_Robots_ROS_Driver` (ROS 1, archived) → `Universal_Robots_ROS2_Driver` lineage.
- The `ur_rtde` C++/Python library by Anders Prier Lindvig (SDU Robotics), which the RTDE Python Client Library tracks.
- RFC-0014 (substrate conformance) for the normative zero-ROS acid test.
- RFC-0023 (Yaskawa MotoROS2 integration) for the per-vendor RFC pattern this RFC continues.

## Unresolved questions

**Maintainer feedback received (2026-08-27).** A Universal Robots maintainer (`urrsk`) gave a detailed point-by-point review on [Universal_Robots_ROS2_Driver discussion #1799](https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver/discussions/1799). The gripper-default (Q2) and the `sendCustomScript` naming (part of Q3) are corrected in this revision. The deeper modeling their feedback calls for, splitting anonymous-script from named-program invocation and expressing the yield-control / run / reacquire mode-handover, goes into [RFC-0015](0015-control-program-invocation.md), and the clock-authority / per-controller-rate point (Q4) into an [RFC-0016](0016-realtime-cyclic-manifest-block.md) amendment, through the normal RFC process rather than being resolved here.

1. **PolyScope 5 vs PolyScope X path forward.** Answered: RTDE is the stable part across the transition, so the RTDE data exchange does not need a generation branch; the generation distinction belongs only to the layer above it (program loading, program state, URCaps; PolyScope X replaces the Dashboard server with a REST Robot API).
2. **Gripper-coupling defaults.** Resolved: **unset the brand default; deployment chooses** from the UR+ catalogue, with Robotiq 2F-85 documented as an example only. Applied above (mapping table + compatibility notes).
3. **URScript invocation.** Naming corrected: `sendCustomScript` is SDU's `ur_rtde`, not the `RTDE_Python_Client_Library` / UR Client Library the ROS 2 driver builds on. The UR-stack path for anonymous script is the secondary interface (port 30002), and on ROS 2 the `urscript_interface` node via `/urscript_interface/script_command`. Named-program invocation is a *separate* mechanism (Dashboard `load`/`play` on PolyScope 5 via the dashboard client services; the REST Robot API on PolyScope X), and on UR it is a mode handover that stops External Control, not a call inside a running trajectory. Also to encode: no argument passing to a `.urp` (values via I/O, RTDE input registers, installation variables, or inlined script) and remote-control mode required on e-Series and newer. The RFC-0015 modeling of this is tracked in [RFC-0015](0015-control-program-invocation.md).
4. **Realtime / cyclic execution.** Refined: script is evaluated at 500 Hz on e-Series / PolyScope X but 125 Hz on CB3, so a manifest must not hardcode a single rate; and the manifest should state which clock is authoritative, with the endorsable pattern being the external computer slaved to the robot clock (block on incoming RTDE data) rather than running its own loop. Tracked for an [RFC-0016](0016-realtime-cyclic-manifest-block.md) amendment.
5. **UR+ ecosystem conformance.** Would Universal Robots be open to URML-conformance becoming a UR+ badge criterion in the future? (No commitment requested — exploratory.)
6. **Which repo for feedback?** Both `Universal_Robots_ROS2_Driver` and `RTDE_Python_Client_Library` have Discussions enabled. Which would maintainers prefer as the canonical thread for this RFC? (URML's Discussions are also available as a neutral venue.)

## Implementation note

RFC-0024 ships as a single PR alongside the new `ur_cell.yaml` manifest + a `conformance/fixtures/industrial/<NN>_ur_cell_positive.yaml`. Hermetic conformance suite + validator suite must remain green. Draft state; promotion to Open is Founder-action when the Phase-0 launch gate un-halts.

No code change in `UrAdapter` or `UrRtdeAdapter`. No new dependency. No new Protocol method. The frozen v0.1 surface is unchanged.

## Requested feedback (from UniversalRobots maintainers)

If you are a maintainer of `UniversalRobots/Universal_Robots_ROS2_Driver`, `UniversalRobots/RTDE_Python_Client_Library`, or a member of the UR+ developer-relations team, URML is asking you for:

1. **Correctness of both mappings above.** ROS 2 driver action surface, RTDE Python API surface, PolyScope compatibility footnotes — please correct anywhere the table misrepresents reality.
2. **PolyScope X guidance.** What should the URML adapters do during the PolyScope X transition? Pin? Branch? Wait?
3. **URScript binding.** Should URML's [RFC-0015](0015-control-program-invocation.md) call_program bind to URScript invocation, and through which path (ROS 2 driver vs RTDE direct)?
4. **Default gripper assumption.** Is documenting Robotiq 2F-85 as the brand-default appropriate, or would UR prefer a gripper-agnostic default?
5. **Conformance interest.** Would Universal Robots consider listing both adapters in the URML compatible-runtimes registry per [RFC-0014](0014-substrate-conformance.md)? (No CI obligation requested at this stage.)
6. **UR+ alignment exploration.** Is URML-conformance something that could plausibly feed into the UR+ certification program in a future direction?
7. **Anything else.** Corrections, additions, and "you got that wrong" are explicitly invited.

## How to respond

Open a thread in the URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Categories that fit best: **Q&A** (factual corrections), **Ideas** (proposals for URML primitives UR needs that v0.1 lacks), **Builders & Makers** (runtime authorship / conformance listing). Substantive spec changes go through a follow-on RFC per [RFC-0001](0001-rfc-process.md).

UR maintainers may alternatively open Discussions in their own repos linking back to this RFC; URML maintainers will track and respond.

For a private channel before any public discussion, contact via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete vendor relationship and a concrete asymmetric proof (UR is the unique dual-adapter substrate-neutrality demo).
- [x] The Detailed design names every affected component (none changed; both adapters and the conformance fixture are referenced verbatim).
- [x] At least one alternative is genuinely considered (three are — split per adapter, merge with Yaskawa, defer the manifest).
- [x] Drawbacks are listed; "two-adapter cognitive load" and "PolyScope X risk" are real downsides.
- [x] Backward compatibility is honest: purely additive.
- [x] This RFC does not add a Layer-2 primitive; the dual-substrate sketch *is* the substrate-neutrality demonstration.
- [x] The implementation note explains how this lands: one PR, Draft, no adapter code change.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed compliance — in particular: URML does not couple to ROS 2 (UR is precisely the proof URML does not); no commercial / partnership surface enters the repository (RFC-0024 is descriptive of existing technical artifacts and explicitly invites feedback); no Apache-2.0 commitment changes.
