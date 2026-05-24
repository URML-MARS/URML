---
rfc: 0061
title: WLKATA integration, request for comment from wlkata maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-24
updated: 2026-05-24
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

# RFC-0061: WLKATA integration, request for comment from wlkata maintainers

## Summary

URML does not yet ship a WLKATA integration. This RFC proposes a `WlkataAdapter` family under [`reference/cobot-runtime/`](../../reference/cobot-runtime/) that targets WLKATA's four published ROS 2 packages (`Wlkata_Mirobot_Ros2`, `Wlkata_MT4_ROS2`, `Wlkata_Haro380_Ros2`, and the umbrella `ROS2_WLKATA`) and the `wlkatapython` Python SDK. The adapter routes URML Layer-2 primitive calls (`move_to`, `grasp`, `release`, `measure`, `wait_for`, `report`) and the industrial-profile primitives ([RFC-0013](0013-industrial-layer2-primitives.md): `pick_from`, `place_at`, `swap_tool`) onto WLKATA's G-code-over-serial protocol where ROS is not available, and onto the published ROS 2 topics where it is. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the wlkata maintainers.

This is the first **Move #3** RFC. Move #1 (RFCs 0023–0038) targeted Tier-1 robot OEMs and component vendors. Move #2 (RFCs 0040–0060) targeted the AI/ML layer above the substrate. Move #3 turns the outreach to the affordable / desktop / educational tier between them: programmable robot arms and quadrupeds in the $300 to $8k range that already expose Python and ROS 2 surfaces. WLKATA is the desktop-arm anchor for this move.

## Motivation

WLKATA's product line spans the exact range URML's substrate-neutral story needs: Mirobot (entry-level 6-DOF education arm, sub-$1k), MT4 (4-axis SCARA), and Haro380 (industrial-grade 6-axis desktop arm, ~$5.7k). One physical vendor covers maker, classroom, and light-industrial deployments with a single control protocol family. URML's value proposition lands at every tier of that range: an English sentence ("pick the red mug and place it in the bin") compiles down to the same URML primitive sequence whether the substrate is a Mirobot on a student's desk or a Haro380 in a teaching lab.

Three things make this RFC concrete rather than aspirational. First, WLKATA publishes per-product ROS 2 packages (`Wlkata_Mirobot_Ros2`, `Wlkata_MT4_ROS2`, `Wlkata_Haro380_Ros2`) plus an umbrella `ROS2_WLKATA` repository under the `wlkata` GitHub org. URML's existing ROS 2 substrate path already covers the dispatch surface. Second, the `wlkatapython` SDK is Apache-compatible MIT and exposes a clean G-code-over-serial path for the no-ROS deployments (a maker on Windows with a USB-serial dongle, a classroom Raspberry Pi without a full ROS 2 install). URML's `cobot-runtime` already speaks both substrates. Third, WLKATA also publishes a BRAVE reinforcement-learning suite with Gazebo, MuJoCo, and Isaac Lab / Isaac Gym backends. URML's [RFC-0050 (NVIDIA Isaac)](0050-nvidia-isaac-lab-integration.md) and [RFC-0060 (MuJoCo)](0060-mujoco-integration.md) target the same simulators; a WLKATA arm becomes a real-hardware target for policies trained in URML-aware sims.

WLKATA's posture is open: MIT licenses on the SDKs, public GitHub org, English documentation, sales channels in the US (passes the URML US-federal default policy at [RFC-0003](0003-us-alignment.md) without flagging on the arm itself; the founding entity is Chinese-headquartered, so the procurement-side compliance pass depends on the deploying organization's policy, not the URML adapter). URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. WLKATA does not compete with URML for the substrate-neutral vocabulary role. WLKATA is the hardware. URML is the spec a WLKATA program can target without locking the user to G-code or to ROS 2 specifically.

## Detailed design

URML's existing artifacts that feed into a WLKATA adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives a WLKATA program would emit.
- [`spec/profiles/industrial/`](../../spec/profiles/industrial/): the industrial-profile primitives ([RFC-0013](0013-industrial-layer2-primitives.md): `pick_from`, `place_at`, `swap_tool`).
- [`spec/profiles/educational/`](../../spec/profiles/educational/) ([RFC-0011](0011-educational-profile.md)): the profile that matches the Mirobot classroom use case.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime that hosts arm-style adapters today (Franka, UR, SO-100). WLKATA's adapter joins this family.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference. The classroom story leans on this.

### Proposed `WlkataAdapter` family shape

One adapter family, three concrete adapters parameterised by product and transport. Package layout:

```
reference/cobot-runtime/src/cobot_runtime/wlkata/
├── __init__.py
├── adapter_ros2.py        # WlkataRos2Adapter, wraps wlkata's ROS 2 packages
├── adapter_serial.py      # WlkataSerialAdapter, wraps wlkatapython over USB-serial
├── product.py             # Mirobot / MT4 / Haro380 capability profiles
└── manifests/
    ├── wlkata_mirobot.yaml
    ├── wlkata_mt4.yaml
    └── wlkata_haro380.yaml
```

Both adapters implement URML's substrate Protocol (the same one used by `MockROSAdapter` and the `FrankaAdapter`). Selection at validation time depends on the manifest's `transport:` field. The ROS 2 path is preferred where the deployment already runs ROS 2; the serial path is the no-ROS fallback for classroom and maker setups.

### Proposed URML v0.1 to WLKATA mapping

| URML primitive | WlkataRos2Adapter (ROS 2) | WlkataSerialAdapter (G-code / wlkatapython) |
|---|---|---|
| `move_to(pose)` | `JointTrajectory` action goal on the product's published joint-trajectory topic. | `G0` / `G1` G-code line via `wlkatapython.WlkataMirobot.set_joint_angle(...)` or equivalent per product. |
| `grasp(gripper_id)` | Gripper-close service call on the product's published gripper topic. | `M3` / `M5` gripper command via the SDK's gripper API. |
| `release(gripper_id)` | Gripper-open service call. | The complementary G-code via the SDK. |
| `measure(sensor_id)` | Subscribe to the product's joint-state or tool-state topic for one sample. | `wlkatapython` joint-state query plus any conveyor / slide / external sensor IO the SDK already exposes. |
| `wait_for(event \| threshold \| signal)` | ROS 2 subscriber on the named event or signal topic with a debounce. | Polling loop over the SDK's status query with a timeout. |
| `report(status)` | Publish to a URML-namespaced status topic (`/urml/<adapter>/report`). | Append to a per-session log file and to stdout, mirroring `MockROSAdapter`'s log shape. |
| `pick_from(source)` / `place_at(destination)` ([RFC-0013](0013-industrial-layer2-primitives.md)) | Layer-3 composition over `move_to` plus `grasp` / `release`, no new Protocol method on the adapter. | Same. |
| `swap_tool(tool_id)` | Composes onto the existing docking-goal path per [RFC-0013](0013-industrial-layer2-primitives.md) (`send_docking_goal`). | Same composition; the SDK exposes tool-change as a sequence the adapter scripts. |

### Proposed capability manifest

The three manifests live under `reference/cobot-runtime/src/cobot_runtime/wlkata/manifests/` and follow [RFC-0009](0009-legged-humanoid-mobility.md)'s capability-manifest schema plus the industrial-profile extensions in [RFC-0013](0013-industrial-layer2-primitives.md). A condensed shape for the Haro380:

```yaml
brand: wlkata_haro380
profile: industrial
dof: 6
reach_m: 0.38
payload_kg: 0.5
transport: [ros2, serial]
ros2:
  package: wlkata/Wlkata_Haro380_Ros2
  joint_trajectory_topic: /haro380/joint_trajectory
  gripper_service: /haro380/gripper
serial:
  protocol: gcode
  python_sdk: wlkatapython
  baud: 115200
provenance:
  origin: CN
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `provenance.origin: CN` row is recorded honestly. URML's default US-federal policy filters at the *manifest-load* layer, not the *adapter-source* layer, and the policy decision is the operating organization's, not URML's. Deploying organizations under a strict US-federal procurement rule can override the default to a per-organization policy file (per [RFC-0004](0004-compliance-policy.md)) that rejects or scopes WLKATA accordingly. The adapter ships either way.

### Proposed conformance integration

A `URML_WLKATA_INTEGRATION=1` env-gated CI workflow installs the `wlkatapython` SDK, runs the WlkataSerialAdapter against a hermetic mock that replays G-code responses, and asserts that the emitted commands match a recorded golden trace. The in-tree conformance suite continues to use `MockROSAdapter`. A separate hardware-in-the-loop lane against a real Mirobot or Haro380 is out of scope for this RFC and would be a later contribution from the founder or a WLKATA maintainer with access.

### BRAVE simulation cross-link

WLKATA's BRAVE repositories train policies in Gazebo, MuJoCo, and Isaac Lab / Isaac Gym. URML's existing RFCs target the same three simulators:

- [RFC-0037](0037-osrf-gazebo-integration.md) (OSRF / Gazebo Sim)
- [RFC-0060](0060-mujoco-integration.md) (MuJoCo)
- [RFC-0050](0050-nvidia-isaac-lab-integration.md) (NVIDIA Isaac Lab + Isaac-GR00T)

A WLKATA arm trained under a URML-aware version of BRAVE becomes a real-hardware target for URML programs without a separate sim-to-real adapter. This RFC does not propose changes to BRAVE; it observes the alignment and leaves the contribution direction to the WLKATA maintainers' preference.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/cobot-runtime/src/cobot_runtime/wlkata/`. Not built in this PR. The RFC requests wlkata maintainer feedback first.
- Conformance suite: proposed new `wlkata-integration.yml` CI workflow and a `URML_WLKATA_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. The WLKATA side gains nothing yet; the adapter consumes the published packages without proposing changes to them.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** RFCs 0023–0036 reference real adapter code. This RFC references a proposal. The honest framing: URML wants WLKATA input on the manifest-per-product split and on the ROS 2-vs-serial transport-selection mechanism before shipping, because both choices have user-visible implications the published surface does not pin down.
- **Two transports double the test matrix.** The serial path is a real maker workflow (no ROS install required) and the ROS 2 path is a real lab workflow. Supporting both means twice the integration tests and twice the version drift to track.
- **Manifests are per-product, not per-family.** Each WLKATA arm gets its own manifest because the reach, DOF, payload, and joint limits differ. The duplication is honest but adds maintenance cost when WLKATA ships a new arm.
- **Origin disclosure is necessary but politically loaded.** Recording `origin: CN` on the manifests is correct per URML's provenance discipline, but it means the default US-federal policy ([RFC-0003](0003-us-alignment.md), [RFC-0004](0004-compliance-policy.md)) will surface a procurement-compliance prompt to deploying organizations. URML's posture is that the decision belongs to the operator, not to URML, but the surface still has to be designed.

## Alternatives considered

1. **Ship the adapter first, ask wlkata maintainers later.** Rejected. The WLKATA repos accept Issues but the per-product manifest split and the ROS 2-vs-serial selection are observable choices worth maintainer input on; a pre-RFC saves rework.
2. **Target only the ROS 2 path; skip serial.** Rejected. The classroom and maker audience is exactly the one Move #3 is aimed at, and that audience runs on USB-serial more often than on a full ROS 2 install. Skipping serial would forfeit half the value.
3. **One adapter for all WLKATA products instead of three manifests.** Rejected. The capability differences (DOF, reach, payload) are real and the URML validator needs them at manifest-load time to reject impossible programs. A single adapter parameterised by a `product:` field would push the validation downstream into the adapter, which weakens the static-verification guarantee.
4. **Fold WLKATA into [RFC-0024 (Universal Robots)](0024-universal-robots-integration.md) or another existing Move #1 RFC.** Rejected. WLKATA is a different audience (education and light-industrial) at a different price tier; the Move #1 audience was procurement-grade industrial. Conflating them blurs the Move #3 framing this RFC opens.

## Prior art

- `wlkata/WLKATA-Python-SDK-wlkatapython`: the Python SDK URML's serial adapter would wrap (MIT, requires Python >= 3.9, v0.1.1 on 2025-10-22).
- `wlkata/ROS2_WLKATA`: the umbrella ROS 2 package set the URML ROS 2 adapter would target.
- `wlkata/Wlkata_Haro380_Ros2`, `wlkata/Wlkata_Mirobot_Ros2`, `wlkata/Wlkata_MT4_ROS2`: the per-product ROS 2 packages.
- `wlkata/wlkata-Arduino-MEGA-2560`, `wlkata/WlkataC`, `wlkata/wlkata_micro_bit`: adjacent SDKs documenting the same G-code protocol surface.
- `wlkata/brave-*` (Gazebo / MuJoCo / Isaac Lab / Isaac Gym): the simulation cross-link.
- [RFC-0011](0011-educational-profile.md): the URML profile this RFC targets first.
- [RFC-0013](0013-industrial-layer2-primitives.md): the industrial-profile primitives used in the Haro380 path.
- [RFC-0023](0023-yaskawa-motoros2-integration.md) through [RFC-0038](0038-ros-industrial-consortium.md): the Move #1 per-vendor outreach pattern this RFC inherits.
- [RFC-0050](0050-nvidia-isaac-lab-integration.md), [RFC-0060](0060-mujoco-integration.md), [RFC-0037](0037-osrf-gazebo-integration.md): the simulator RFCs the BRAVE cross-link touches.

## Unresolved questions

Provisional pending wlkata maintainer feedback:

1. **Adapter home.** Should URML host the adapter under `reference/cobot-runtime/` (URML-side), under a new repo in the `wlkata` GitHub org as a contributed example, or both?
2. **Per-product vs. per-family manifests.** Is one manifest per arm (Mirobot, MT4, Haro380) the right granularity, or would wlkata prefer a single parametric manifest?
3. **Transport selection.** Should the manifest's `transport:` field be a list (ROS 2 + serial) with adapter auto-selection at execution time, or two distinct manifests per product (one per transport)?
4. **G-code protocol coverage.** Is the documented G-code surface in `WLKATA-Python-SDK-wlkatapython` the canonical reference, or does the Haro380 expose additional commands the SDK does not yet wrap?
5. **BRAVE alignment.** Is there interest in a URML-aware BRAVE branch where policies are trained against URML-primitive emissions instead of raw joint targets?
6. **Conformance lane.** Would wlkata be open to a URML conformance line on a Mirobot or Haro380 model card, similar to how UR publishes URDF-and-driver verification artifacts?
7. **Anything else.**

## Implementation note

RFC-0061 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/cobot-runtime/src/cobot_runtime/wlkata/` package follows in a later session, gated on wlkata maintainer feedback. Draft state. First Move #3 RFC. Ledger entry in [`examples/lighthouses/outreach-move3.yaml`](../../examples/lighthouses/outreach-move3.yaml).

## Requested feedback (from wlkata maintainers)

1. Adapter home (URML repo, wlkata org contributed example, both).
2. Manifest granularity (per-product, per-family, parametric).
3. Transport selection (single manifest with list, two manifests per product).
4. Canonical G-code reference (the Python SDK, a separate firmware doc, both).
5. BRAVE alignment interest.
6. Conformance-lane interest on the product model cards.
7. Anything else.

## How to respond

The `wlkata/WLKATA-Python-SDK-wlkatapython` repo has both Issues and Discussions enabled (verified 2026-05-24). The umbrella `wlkata/ROS2_WLKATA` repo is the better surface for a cross-product proposal, with Issues enabled. URML's planned channel: open a single Issue on the most appropriate wlkata repo (probably `ROS2_WLKATA` for cross-product visibility, with a courtesy cross-reference to the Python SDK Discussion surface), pointing to this RFC.

URML's own public Discussions for the broader Move #3 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the first Move #3 RFC).
- [x] Motivation grounded in verified technical alignment (four published ROS 2 packages, a Python SDK with G-code transport, BRAVE simulation suite intersecting URML's Move #2 simulator RFCs) plus the affordable / educational positioning.
- [x] Detailed design uses verified repo names (`Wlkata_Mirobot_Ros2`, `Wlkata_MT4_ROS2`, `Wlkata_Haro380_Ros2`, `ROS2_WLKATA`, `WLKATA-Python-SDK-wlkatapython`) and adapter-Protocol shape consistent with `reference/cobot-runtime/`.
- [x] At least one alternative considered (four are: ship-first, ROS-only, single-adapter, fold-into-Move-1).
- [x] Drawbacks are real (proposal-only, dual-transport test matrix, per-product manifests, origin disclosure friction).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The mapping uses the existing vocabulary plus the industrial-profile extensions from RFC-0013.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of the wlkata GitHub org as of 2026-05-24.
- [x] Provenance row (`origin: CN`) recorded honestly per URML's discipline, with the policy-decision boundary made explicit.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
