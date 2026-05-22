---
rfc: 0023
title: Yaskawa / MotoROS2 integration — request for comment from Yaskawa-Global maintainers
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

# RFC-0023: Yaskawa / MotoROS2 integration — request for comment from Yaskawa-Global maintainers

## Summary

URML — the substrate-neutral robot-intent language defined by this repository — already ships a `YaskawaAdapter` that compiles URML programs onto Yaskawa industrial arms through the Motoman ROS-Industrial driver lineage (which `Yaskawa-Global/motoros2` now succeeds). This RFC documents the v0.1 primitive-to-MotoROS2 mapping, identifies the gaps the YRC controller surface reveals that URML v0.1 cannot yet express, and **requests review and feedback from the Yaskawa-Global maintainers** on the mapping's correctness and on whether Yaskawa would consider becoming a conformance-listed runtime per [RFC-0014](0014-substrate-conformance.md). No spec change is proposed here.

## Motivation

Yaskawa is a ROS-Industrial founding member and one of the "big four" industrial-arm vendors. The `Yaskawa-Global/motoros2` project is a vendor-direct, recent, actively-maintained ROS 2 driver that runs *inside* the YRC controller (MotoPlus runtime) and exposes the URML-relevant action surface (joint-trajectory execution, gripper command, robot status, IO). That architectural choice — a controller-resident bridge — exercises URML's substrate-neutral Protocol in a different shape than host-side gateways (e.g. UR `ur_rtde`), and it is precisely the kind of substrate URML must remain neutral over.

The case for filing this RFC publicly, today, is twofold:
1. **Correctness check.** Every URML adapter docstring is a tacit claim about a vendor's API. Asking the vendor's own maintainers to review the mapping is the most honest way to validate that claim.
2. **Standards alignment.** Yaskawa's ROS-Industrial heritage and Motoman's deep installed base make Yaskawa a natural early conformance-listed runtime if the mapping is sound.

## Detailed design

This RFC is descriptive of existing URML artifacts plus an explicit feedback ask. No spec text changes.

### URML v0.1 → Yaskawa MotoROS2 primitive mapping

The frozen v0.1 substrate Protocol (`reference/ros2-runtime/src/urml_ros2_runtime/substrate/base.py`) is implemented for Yaskawa by `YaskawaAdapter` (`reference/industrial-arm-runtime/src/urml_industrial_arm_runtime/adapter.py`), composing `RclpyAdapter` with brand-default action-server config. The mapping below reflects that composition.

| URML v0.1 primitive | Adapter method | MotoROS2 / ROS-Industrial action or topic | Notes |
|---|---|---|---|
| `move_to` (Cartesian / named pose) | `send_navigation_goal(location=..., pose=..., frame=...)` | `control_msgs/FollowJointTrajectory` via MoveIt 2 planning to a named pose declared in the manifest | The arm is a fixed-base manipulator; `move_to` is an end-effector / named-pose move planned in MoveIt 2 using the YRC robot model. |
| `hover` (drive to a station-keeping pose) | `send_navigation_goal(...)` | Same FollowJointTrajectory action; the manifest's home_pose is the typical target | Equivalent to `move_to` on a fixed-base arm; the conformance suite treats them identically for industrial arms. |
| `grasp` | `send_manipulation_goal(action="grasp", force_n=...)` | `control_msgs/GripperCommand` on the configured `_BRAND_GRIPPER_SERVER["yaskawa"]` = `/motoman/gripper/gripper_cmd` | Scalar `force_n` is honoured at v0.1 fidelity; parametric impedance is a SPEC-GAPS item (`reference/industrial-arm-runtime/SPEC-GAPS.md`), not invented here. |
| `release` | `send_manipulation_goal(action="release", release_mode=..., release_at=...)` | Same `GripperCommand` action, opposite command | |
| `measure` | `take_measurement(what=..., target=..., sensor=...)` | Typically a one-shot read from `/joint_states`, an FT topic if declared, or a ROS-Industrial-published wrench | Sensor name comes from the manifest. |
| `wait_for` (event / sensor threshold / signal) | `wait_for_condition(kind=..., name=..., input_mode=..., threshold=...)` | Block on a ROS topic / latched event / signal declared in `declared_events` | |
| `wait` (passive dwell) | `wait_passively(duration_seconds=...)` | Host-side sleep; no controller action | |
| `report` (structured status upstream) | `emit_report(to=..., facts=..., status=..., severity=...)` | A publish on a configured outputs/named_endpoints topic | |
| `dock` | `send_docking_goal(station=..., service=..., until=...)` | Returns `not_supported_on_industrial_arm[yaskawa]: a fixed-base manipulator has no docking station …` | A bare fixed-base arm has no station to dock to; a cell that pairs the arm with a docking station declares it via a companion adapter (the existing RFC-0013 `swap_tool` already rides this method when a tool-change station is declared). |
| `detect` | `query_detection(object_class=..., attributes=..., where_near=..., where_within=...)` | Returns `not_supported_on_industrial_arm[yaskawa]: …no onboard perception. Pair the arm with a companion adapter (vision)…` | A bare arm has no onboard perception; a cell with a wrist-mounted RGB camera or a fixed vision system dispatches `detect` through a companion adapter, exactly as the drone stack pairs flight with a ROS 2 companion. |
| `scan` | `run_scan(area=..., pattern=..., overlap=..., altitude=..., media=..., sensor=...)` | Returns `not_supported_on_industrial_arm[yaskawa]: …no area-scan capability` | Same companion-adapter pattern as `detect`. |
| `capture` (photo / video) | `capture_media(media=..., target=..., duration_seconds=...)` | Returns `not_supported_on_industrial_arm[yaskawa]: …no onboard camera` | Companion-adapter pattern. |
| `speak` (home profile) | `emit_speech(...)` | Returns `not_supported_on_industrial_arm[yaskawa]: …no speaker` | Industrial cells do not host speech; programs that target the industrial profile do not invoke it. |
| `listen` (home profile) | `acquire_speech(...)` | Returns `not_supported_on_industrial_arm[yaskawa]: …no microphone` | Same. |
| `take_off` / `land` / `return_to_home` (drone profile) | `send_takeoff_goal(...)` / `send_land_goal(...)` / `send_return_to_home_goal(...)` | Returns `not_supported_on_industrial_arm[yaskawa]: …no flight capability` | Industrial profile does not invoke flight primitives. |
| `pick_from` (industrial profile, RFC-0013) | composed: `send_navigation_goal` to declared `source` location → `query_detection` (if vision companion) → `send_manipulation_goal(action="grasp", force_n=...)` | The same FollowJointTrajectory + GripperCommand pair, scripted in URML Layer 3 sequence | Adapter does not need a new method; the primitive is a behavior-composition. |
| `place_at` (industrial profile, RFC-0013) | composed: `send_navigation_goal` to declared `target` → `send_manipulation_goal(action="release", release_mode=...)` | Same | |
| `swap_tool` (industrial profile, RFC-0013) | `send_docking_goal(station=..., service="swap_tool")` | A FollowJointTrajectory to the declared `tool_change_station` pose | Rides the existing `send_docking_goal` Protocol method; declared in the cell manifest's `docking_stations[].services`. No new Protocol method per RFC-0013's design. |

A bare Yaskawa cell with a manipulator base + RGB wrist camera + RFC-0013 industrial primitives can be expressed today end-to-end through `YaskawaAdapter` and validated against the bundled US-federal default compliance policy ([RFC-0004](0004-compliance-policy.md)) with no flagging — Japan (JP) is allied; the `yaskawa` vendor token is not on the denylist (`reference/validator/src/urml_validator/policies/us_federal_default.yaml`).

### Substrate-neutrality demonstration

The conformance suite ([`conformance/`](../../conformance/)) parametrizes each fixture over an `adapter_factory`. The same URML program (a RFC-0013 `pick_from` / `place_at` sequence) passes:
- through `MockROSAdapter` (the default hermetic mock), used for the in-tree CI run;
- through `YaskawaAdapter` (which composes `RclpyAdapter`) in the `industrial-arm-integration.yml` gated CI lane;
- through the brand-agnostic conformance assertions (the audit-trace shape is identical across brands).

This is the [RFC-0014](0014-substrate-conformance.md) zero-ROS acid test applied to Yaskawa: the URML program, manifest, and validator are unchanged across substrates. Yaskawa-specific code lives **only** in `YaskawaAdapter` (a thin brand-class on `IndustrialArmAdapter` + one entry in `_BRAND_GRIPPER_SERVER`).

### Compatibility notes

- **Controller compatibility.** `Yaskawa-Global/motoros2` targets YRC1000 / YRC1000micro / DX200 controllers running a recent MotoPlus runtime. `YaskawaAdapter`'s default config (move_group=`/move_action`, gripper=`/motoman/gripper/gripper_cmd`) follows the vanilla ROS-Industrial Motoman convention; sites that namespace their cells override it through `AdapterConfig` exactly as `RclpyAdapter` documents.
- **MoveIt 2 dependency.** The mapping presumes MoveIt 2 is configured for the target arm model (HC10, GP series, MOTOMAN-SDA10F, etc.). The vendor-published URDFs at `Yaskawa-Global/motoman_*` cover the common SKUs.
- **Driver lineage.** Historically `motoman_ros_driver` (ROS 1) → `motoman_ros2` → `Yaskawa-Global/motoros2` (current vendor-direct). The adapter docstring still references the legacy `motoman` package name for continuity; this RFC's table reflects the modern vendor-direct path.
- **Origin.** Japan (Yaskawa-Global, headquartered in Kitakyushu); passes the US-federal default compliance policy ([RFC-0003](0003-us-alignment.md)/[0004](0004-compliance-policy.md)) without flagging.

### Spec changes

None. RFC-0023 is descriptive of the existing v0.1 Protocol and its `YaskawaAdapter` realization. Any gap discovered during Yaskawa review that the frozen Protocol cannot express is recorded as a new entry in `reference/industrial-arm-runtime/SPEC-GAPS.md` and surfaced for Founder decision per [RFC-0014](0014-substrate-conformance.md)'s spec-gap loop — never silently bolted on.

### Validator changes

None.

### Reference runtime changes

None for the existing `YaskawaAdapter`. A brand-named manifest fixture `yaskawa_cell.yaml` plus a `conformance/fixtures/industrial/<NN>_yaskawa_cell_positive.yaml` are added in the same PR for symmetry with the Track-A and Track-I-A brands (Kawasaki / Stäubli / Comau / Mitsubishi / Denso / Hyundai / Nachi / Epson / Omron / Hanwha), which already carry brand-specific manifests. Pure data — no schema, no Protocol method change.

### Conformance suite changes

One new positive fixture under `conformance/fixtures/industrial/` exercising the RFC-0013 `pick_from`/`place_at` happy path on a Yaskawa-branded cell against `MockROSAdapter`. One additional `MANIFEST_REGISTRY` entry in `conformance/src/urml_conformance/fixtures.py`. The brand-agnostic conformance assertions stay unchanged.

## Backward compatibility

Pre-v1.0 spec; no version-bump implication. RFC-0023 is purely additive (a new RFC document plus one new manifest + one new conformance fixture). It cannot break any prior URML behavior because it changes neither schemas nor adapter Protocols.

## Drawbacks

- **Public artifact before vendor outreach.** Publishing this RFC creates a public record of URML's claims about Yaskawa's API before Yaskawa has reviewed them. If the mapping is wrong in a detail that matters to Yaskawa engineers, the public artifact is a slight cost to correct. Mitigation: the RFC is explicitly Draft, explicitly framed as "request for comment from Yaskawa-Global maintainers," and explicitly invites correction.
- **Asymmetry with non-mapping RFCs.** URML's prior RFCs are spec-changing (0002, 0009, 0013) or process / posture (0001, 0003, 0007, 0008). RFC-0023 is the first vendor-directed *mapping* RFC. The category itself is new, and the precedent it sets — that URML may file public RFCs aimed at specific vendors — is worth surfacing. This RFC is the first of a planned **Move #1 lighthouse** batch covering 16 Tier-1 lighthouse-ready vendors (see `[[project_partnership_targets]]` for the full list).

## Alternatives considered

1. **Keep the mapping in adapter docstrings only.** Already done; the adapter docstring is the in-code claim. Filing this RFC adds a public framing layer (vendor-directed feedback ask + standards-collaboration invitation) that an adapter docstring cannot carry.
2. **One combined "all Tier-1 vendors" RFC.** Rejected: per-vendor RFCs are individually citable, individually addressable in vendor outreach, and individually closeable when a vendor responds. A combined RFC dilutes both the credibility hook and the per-vendor feedback loop.
3. **Wait for Yaskawa to ask.** Rejected: URML's Phase-0 posture is to ship in-repo artifacts that *can* be reached out from when the launch gate opens. The RFC is the warm-touch hook; cold outreach without the artifact is the alternative this RFC eliminates.

## Prior art

- The ROS-Industrial Consortium's per-vendor driver tracks (`abb_ros2`, `fanuc_driver`, `motoros2`, etc.) — the closest existing form of a vendor-specific integration document, but framed as drivers, not as primitive-vocabulary mappings.
- Behavior-tree libraries (`py_trees`, BehaviorTree.CPP) ship per-substrate integration guides; URML's substrate-neutral Protocol means there is no per-substrate spec change, only a per-substrate *mapping*. RFC-0023 is the URML equivalent of those guides.
- [RFC-0014](0014-substrate-conformance.md) (substrate conformance) defines, normatively, what makes a runtime URML-compatible; RFC-0023 is a worked example of that contract applied to one vendor.

## Unresolved questions

These are the items where URML's view is provisional pending Yaskawa-Global maintainer feedback.

1. **Driver lineage.** Should `YaskawaAdapter`'s docstring + `_BRAND_GRIPPER_SERVER["yaskawa"]` move from the legacy `motoman_*` naming to the modern `motoros2` naming entirely, or is the legacy `motoman_*` namespace still the more deployed-in-the-wild reality? Vendor signal welcome.
2. **MoveIt 2 vs MotoROS2-native trajectory planning.** Does Yaskawa recommend MoveIt 2 as the planning layer above MotoROS2's joint-trajectory action, or is there a Yaskawa-preferred planner / configuration?
3. **MotoROS2's INFORM-job invocation.** Yaskawa's INFORM language is the on-controller programming layer (analog of UR's URScript). [RFC-0015](0015-control-program-invocation.md) (`call_program`) is the proposed primitive for invoking a named substrate program; would Yaskawa support binding RFC-0015 to a MotoROS2 INFORM job?
4. **Realtime / cyclic execution.** [RFC-0016](0016-realtime-cyclic-manifest-block.md) (real-time / cyclic timing declaration) is the proposed manifest block for declaring cyclic period + watchdog. Does that match the YRC controller's execution model in a way Yaskawa would endorse?
5. **Conformance listing.** Would Yaskawa be open to becoming a conformance-listed runtime per [RFC-0014](0014-substrate-conformance.md), running the URML conformance suite against MotoROS2 in their CI?

## Implementation note

RFC-0023 ships as a single PR alongside the new `yaskawa_cell.yaml` manifest + `conformance/fixtures/industrial/<NN>_yaskawa_cell_positive.yaml`. The hermetic conformance suite + the validator suite must remain green (no regression). RFC-0023 lands in `Draft` state; promotion to `Open` is gated on this RFC being shared with Yaskawa-Global maintainers and the review window opening — that step is a Founder-action when the Phase-0 launch gate un-halts (see [[project_phase0_launch_halted]]).

No code change in `YaskawaAdapter` itself. No new dependency. No new Protocol method. The frozen v0.1 surface (`reference/ros2-runtime/src/urml_ros2_runtime/substrate/base.py`) is unchanged.

## Requested feedback (from Yaskawa-Global maintainers)

If you are a Yaskawa-Global maintainer (or a contributor to `Yaskawa-Global/motoros2`, `motoman_*`, or the broader Yaskawa ROS-Industrial track), URML is asking you for:

1. **Correctness of the primitive mapping above.** Anywhere the table mis-describes MotoROS2's action surface, the YRC controller's behaviour, or the MoveIt 2 integration shape — please correct it.
2. **Driver-name guidance.** Should the URML adapter docstring + brand defaults reflect `motoros2` (modern) or `motoman_*` (legacy) naming? Both?
3. **Conformance interest.** Would Yaskawa-Global consider listing `YaskawaAdapter` in the URML compatible-runtimes registry per [RFC-0014](0014-substrate-conformance.md), and (later) running the URML conformance suite against MotoROS2 in CI?
4. **Spec-gap signal.** Are there MotoROS2 capabilities URML v0.1 cannot express that you'd want surfaced as RFC candidates? The most likely candidates are already documented as Draft RFCs: [0015](0015-control-program-invocation.md) (call_program for INFORM jobs), [0016](0016-realtime-cyclic-manifest-block.md) (real-time / cyclic timing), [0017](0017-digital-io-actuation.md) (digital-I/O actuation).
5. **Anything else.** This RFC is explicitly a request, not a presentation; corrections, additions, and "you got that wrong" are exactly what URML is asking for.

## How to respond

Open a thread in the URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Categories that fit best for this RFC's feedback: **Q&A** (factual corrections of the mapping), **Ideas** (proposals for primitives Yaskawa needs that URML v0.1 lacks), or **Builders & Makers** (runtime authorship / conformance listing). For substantive proposed changes to the URML spec, the canonical channel is a follow-on RFC — Yaskawa contributors are welcome to file one directly, with URML maintainers reviewing per [RFC-0001](0001-rfc-process.md).

If you would prefer a private channel before any public discussion, the URML maintainer's contact is in `MAINTAINERS.md`.

## Self-review (Phase 0)

In Phase 0, the author reviews their own work. Before requesting state advance to **Open**:

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete vendor relationship (Yaskawa-Global / MotoROS2), not hypothetical needs.
- [x] The Detailed design names every affected spec document and reference component (none changed; the existing `YaskawaAdapter` is referenced verbatim).
- [x] At least one alternative is genuinely considered (three are — keep-mapping-in-docstring, one-combined-RFC, wait-for-vendor).
- [x] Drawbacks are listed; the "public artifact before vendor outreach" item is a real downside.
- [x] Backward compatibility is honest: purely additive.
- [x] This RFC does **not** add a Layer-2 primitive, so the dual-substrate sketch requirement does not apply. The mapping table itself is the substrate-neutrality demonstration for an existing primitive set.
- [x] The implementation note explains how this lands: one PR, Draft state, no code change in `YaskawaAdapter`.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed this proposal does not violate it. In particular: this RFC adds no commercial / partnership surface to the repository (it is descriptive of an existing technical artifact and explicitly invites feedback); it does not move anything Apache-2.0; it does not couple URML to a single substrate (URML remains substrate-neutral; Yaskawa is one of 16 Tier-1 vendors covered by the Move #1 lighthouse program).
