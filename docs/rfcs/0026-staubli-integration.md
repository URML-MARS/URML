---
rfc: 0026
title: Stäubli integration — request for comment from ros-industrial/staubli_val3_driver maintainers
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

# RFC-0026: Stäubli integration — request for comment from ros-industrial/staubli_val3_driver maintainers

## Summary

URML ships `StaubliAdapter` (`reference/industrial-arm-runtime/.../adapter.py`) compiling URML programs onto Stäubli arms via `ros-industrial/staubli_val3_driver` (the VAL 3 protocol bridge over the CS9 controller) + MoveIt 2. This RFC documents the v0.1 primitive-to-driver mapping and **requests review and feedback from the ROS-Industrial Stäubli maintainers**. No spec change.

## Motivation

Stäubli (Switzerland) is a high-precision industrial-arm vendor with a strong electronics/pharma/medical-device installed base — a different market segment from the FANUC/Yaskawa/KUKA automotive-heavy mainline. Their VAL 3 controller language is unique among the big industrial arms (closer to Pascal than to KRL/INFORM/KAREL). The ROS-Industrial `staubli_val3_driver` is the canonical public bridge, maintained on the `ros-industrial/` org with Discussions enabled, making it the lighthouse-ready venue.

## Detailed design

Descriptive of existing URML artifacts. No spec text changes.

### URML v0.1 → Stäubli driver primitive mapping

`StaubliAdapter` composes `RclpyAdapter`. Gripper-server default: `_BRAND_GRIPPER_SERVER["staubli"]` = `/staubli/gripper/gripper_cmd`. Mapping identical in shape to KUKA / Yaskawa (industrial-arm pattern); the Stäubli-specific bits are the VAL 3 driver layer and the CS9 controller. The mapping table below is reused verbatim from the industrial-arm template (RFC-0025) — `move_to` / `grasp` / `release` / `measure` / `wait_for` / `wait` / `report` map to the same Protocol methods; `dock` / `detect` / `scan` / `capture` / `speak` / `listen` return `not_supported_on_industrial_arm[staubli]` sentinels with the companion-adapter pattern; the RFC-0013 industrial primitives (`pick_from` / `place_at` / `swap_tool`) compose Layer-3 sequences over the same Protocol methods, with `swap_tool` riding `send_docking_goal` per RFC-0013's design.

The Stäubli-specific routing: MoveIt 2 plans a trajectory; the `staubli_val3_driver` translates `control_msgs/FollowJointTrajectory` to the CS9 controller over the VAL 3 protocol; the controller's VAL 3 application executes the motion. Gripper commands route to `/staubli/gripper/gripper_cmd` (a `control_msgs/GripperCommand` action exposed by the deployment's gripper driver — Stäubli sells `TX2-touch` cobots with electric grippers, but third-party grippers via UR+/SCHUNK are common too).

A bare Stäubli cell (TX2-90 / TX2-160 / TX2-touch with a generic gripper + wrist RGB) with RFC-0013 industrial primitives is expressible today through `StaubliAdapter` and ACCEPTS under the bundled US-federal default policy ([RFC-0004](0004-compliance-policy.md)) — Switzerland (CH) is allied; `staubli` is not on the denylist.

### Compatibility notes

- **Controller line.** `ros-industrial/staubli_val3_driver` targets the CS9 controller (current generation; CS8 / CS8C legacy). The VAL 3 protocol is stable across CS9 firmware revisions.
- **VAL 3 invocation.** Stäubli's on-controller programming language is VAL 3 (Pascal-derived). [RFC-0015](0015-control-program-invocation.md) (`call_program`) is the proposed binding for invoking a named VAL 3 application.
- **TX2-touch cobot.** The TX2-touch is Stäubli's collaborative arm in the TX2 family; the same `StaubliAdapter` handles it — no separate cobot adapter (the VAL 3 driver covers both classical and cobot variants).
- **Origin.** Stäubli International AG, Pfäffikon, Switzerland; passes the US-federal default policy without flagging.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator / reference runtime: none.
- Conformance: none. `staubli_cell.yaml` + `conformance/fixtures/industrial/10_staubli_cell_positive.yaml` already shipping from Track A.

## Backward compatibility

Pre-v1.0; purely additive (RFC document only — no manifest / fixture / code change).

## Drawbacks

- **VAL 3 is niche.** Outside the Stäubli installed base, VAL 3 is unfamiliar to most ROS-Industrial integrators; a URML program that calls into a VAL 3 application via Draft [RFC-0015](0015-control-program-invocation.md) is not portable to other vendors without a per-vendor rewrite. This is a general property of `call_program`, not Stäubli-specific.
- **CS9-only.** Older CS8 / CS8C controllers are not currently supported by the driver, which excludes some long-installed Stäubli arms. Documented for honesty.

## Alternatives considered

1. **Wait for a vendor-direct Stäubli ROS 2 repo** (analog to `Yaskawa-Global/motoros2`). Rejected: `ros-industrial/staubli_val3_driver` is the actively-maintained public venue today; vendor-direct may emerge later and be a follow-on RFC.
2. **Folder into a "ROS-Industrial Consortium" omnibus RFC** (RFC-0038 in flight). Rejected: per-vendor RFCs remain individually citable; the consortium RFC is the institutional umbrella, not a substitute.

## Prior art

- `ros-industrial/staubli_val3_driver` — the upstream driver.
- Stäubli's VAL 3 programming reference (vendor documentation).
- RFC-0023 / 0024 / 0025 for the per-vendor RFC pattern.
- [RFC-0014](0014-substrate-conformance.md) for the substrate-neutral runtime contract.

## Unresolved questions

Provisional pending ros-industrial/staubli_val3_driver maintainer feedback:

1. **CS8 / CS8C support.** Is there community interest in extending the driver to older controllers, and if so should URML's adapter docstring carry a controller-compatibility footnote?
2. **VAL 3 invocation.** Should [RFC-0015](0015-control-program-invocation.md) `call_program` bind to a VAL 3 application launch (a specific path through the VAL 3 protocol), and what is the preferred handle (application name? `xxx.pjx` project file?)?
3. **TX2-touch vs classical.** Should URML expose the TX2-touch collaborative-mode parameters (lower velocity caps, contact-force limits) through the manifest, or are they purely deployment config?
4. **Conformance listing.** Would the ROS-Industrial Stäubli maintainers (and through them, Stäubli International) consider listing `StaubliAdapter` in the URML compatible-runtimes registry per [RFC-0014](0014-substrate-conformance.md)?

## Implementation note

RFC-0026 ships as a single RFC document PR. No code / manifest / fixture change (all shipping from Track A). Hermetic conformance suite remains green by virtue of zero edits to it. Draft state; promotion to Open is Founder-action when the Phase-0 launch gate un-halts.

## Requested feedback (from ros-industrial/staubli_val3_driver maintainers)

If you maintain `ros-industrial/staubli_val3_driver` (or contribute to the broader ROS-Industrial Stäubli track), URML is asking you for:

1. **Correctness of the mapping description.** Anywhere the description misrepresents the VAL 3 driver shape, the CS9 controller's behaviour, or the MoveIt 2 integration — please correct.
2. **Controller-line guidance.** Should the URML adapter docstring reference CS9 only, or document a path for older controllers?
3. **VAL 3 invocation.** Binding for Draft [RFC-0015](0015-control-program-invocation.md), and the preferred handle/path?
4. **TX2-touch manifest extensions.** Should collaborative-mode parameters be in the manifest?
5. **Conformance interest.** Would Stäubli (via the ROS-Industrial track) list `StaubliAdapter` per [RFC-0014](0014-substrate-conformance.md)?
6. **Anything else.** Corrections welcome.

## How to respond

URML public Discussions (per [RFC-0008](0008-community-discussions.md)):

> https://github.com/URML-MARS/URML/discussions

Categories: **Q&A**, **Ideas**, **Builders & Makers**.

Private channel via `MAINTAINERS.md`.

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed.
- [x] Motivation grounded in concrete vendor relationship (`ros-industrial/staubli_val3_driver` + Stäubli International).
- [x] Detailed design names every affected component (none changed; existing `StaubliAdapter` + Track-A manifest/fixture referenced).
- [x] At least one genuine alternative considered (two are).
- [x] Drawbacks are real (VAL 3 niche, CS9-only).
- [x] Backward compatibility: purely additive (RFC document only).
- [x] No Layer-2 primitive added; dual-substrate sketch not required.
- [x] Implementation note explains how this lands (smaller than 0023/0024/0025 — no manifest + no fixture added since Track A already shipped them).
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant.
