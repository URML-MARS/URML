---
rfc: 0062
title: Petoi (Bittle / Nybble) integration, request for comment from PetoiCamp maintainers
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

# RFC-0062: Petoi (Bittle / Nybble) integration, request for comment from PetoiCamp maintainers

## Summary

URML does not yet ship a Petoi integration. This RFC proposes a `PetoiAdapter` family that wraps the OpenCat firmware on Bittle X, Bittle (original), and Nybble Q, using the OpenCat serial command protocol exposed by [`PetoiCamp/OpenCat`](https://github.com/PetoiCamp/OpenCat) and the Python wrappers in [`PetoiCamp/Petoi_MindPlusLib`](https://github.com/PetoiCamp/Petoi_MindPlusLib). URML's Layer-2 primitives map onto OpenCat's skill vocabulary (named gaits like `walk`, `trot`, `bound`, `sit`, plus posture and head-pan commands) without requiring changes to Petoi's firmware. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the PetoiCamp maintainers.

This is the second Move #3 RFC, paired with [RFC-0061 (WLKATA)](0061-wlkata-outreach.md). Move #3 targets the affordable / desktop / educational tier. WLKATA is the desktop-arm anchor; Petoi is the hobby-quadruped anchor. Bittle X sells for $299 and supports an open-source firmware with a 4.8k-star community. It is the smallest legged-robot target in URML's outreach landscape and the only one a typical reader can plausibly own.

## Motivation

The demo most likely to travel for URML is a $299 robot dog on a desk acting out an English sentence. Petoi's Bittle X is that robot. The hardware is open (BiBoard ESP32), the firmware is open (`PetoiCamp/OpenCat`, MIT-licensed, 4.8k stars), and Petoi already publishes Python, Arduino / C++, mobile-app, and block-based interfaces to the same underlying skill vocabulary. URML's Layer-2 primitive set sits cleanly above all four.

Three things make this RFC concrete rather than aspirational. First, OpenCat already speaks a documented serial command protocol with named skill calls (single-letter tokens followed by parameters). URML's `report` and `wait_for` primitives compose with that protocol without firmware changes. Second, Petoi has published a separate ROS integration repo (`PetoiCamp/ros_opencat`, 24 stars, CMake), so URML's existing ROS 2 substrate path has a partial precedent to consume. Third, OpenCat ships a `SkillLibrary` of pre-recorded gaits (walk, trot, bound, sit, balance, push-up) that map to URML's posture and locomotion primitives directly; the policy-trained motion debate around large quadrupeds (Spot, ANYmal, Unitree) is sidestepped because Bittle's motion is library-driven by design.

Petoi's posture is open-source and education-leaning: MIT license on `OpenCat`, English-first documentation, books and curricula published by Dr. Rongzhong Li (Petoi's founder), and an active mobile-app surface. URML's open-core commitment (see [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md)) lands without translation. The two are orthogonal: Petoi makes a quadruped that already moves; URML is the spec that gives the quadruped a substrate-neutral English-to-motion path with static validation.

## Detailed design

URML's existing artifacts that feed into a Petoi adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`spec/profiles/educational/`](../../spec/profiles/educational/) ([RFC-0011](0011-educational-profile.md)): the natural home for Bittle / Nybble.
- [`spec/layer-1-hal/`](../../spec/layer-1-hal/) plus [RFC-0009](0009-legged-humanoid-mobility.md): the legged-mobility capability surface a Bittle manifest declares against.
- [`reference/cobot-runtime/`](../../reference/cobot-runtime/): the runtime sibling family. Petoi's adapter would more naturally live in a new `reference/petoi-runtime/` or under a generic `reference/desktop-quadruped-runtime/`; the placement is open.
- [`reference/llm-bridge/`](../../reference/llm-bridge/): the English-to-URML translation reference. The hero demo for Petoi leans on this hardest.

### Proposed `PetoiAdapter` shape

One adapter, parameterised by product (Bittle X, Bittle original, Nybble Q). Package layout:

```
reference/petoi-runtime/src/petoi_runtime/
├── __init__.py
├── adapter.py             # PetoiAdapter
├── opencat_protocol.py    # OpenCat single-letter command vocabulary
├── skills.py              # mapping from URML primitives to OpenCat skill names
└── manifests/
    ├── petoi_bittle_x.yaml
    ├── petoi_bittle.yaml
    └── petoi_nybble.yaml
```

The adapter implements URML's substrate Protocol. The transport is USB-serial first (the common case), with Bluetooth as a future addition (ESP32 supports it on Bittle X but the protocol surface is the same).

### Proposed URML v0.1 to OpenCat mapping

| URML primitive | OpenCat realisation |
|---|---|
| `move_to(pose)` | The closest documented gait from OpenCat's `SkillLibrary` (`kwk` walk, `ktr` trot, `kbd` bound, `kbk` backward) is selected per the pose's direction and magnitude. Distance is implemented as gait duration; orientation as the pre-gait turn token (`kvtL` / `kvtR`). |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable on stock Bittle / Nybble (no gripper). The adapter raises a manifest-load-time validation error if a program uses these primitives on a Petoi manifest. Bittle add-ons (claw, gripper extensions sold by Petoi or third parties) can be modelled in a future per-add-on manifest. |
| `measure(sensor_id)` | Subscribe to a one-shot read of Bittle's IMU, gyroscope, or attached ultrasonic sensor via the OpenCat status query (`g` for gyro, `j` for joint, plus per-sensor commands). |
| `wait_for(event \| threshold \| signal)` | Polling loop over the IMU / sensor stream with a debounce, mirroring the pattern in URML's existing substrate adapters. |
| `report(status)` | Append to a per-session log file and to stdout, mirroring `MockROSAdapter`'s shape. Optional: emit Petoi's status tokens to the OpenCat serial stream for mobile-app observability. |
| `pose(posture_id)` (Layer-3 composition) | OpenCat posture tokens (`ksit`, `kstr` stretch, `krest`, `klap` lap-sit) called via the SkillLibrary. |

The crucial design observation: Bittle and Nybble are skill-library-driven, not joint-target-driven at the URML surface. URML programs do not emit per-joint trajectories; they emit posture and gait primitives, and the OpenCat firmware plays back the recorded skill. This keeps URML's contract substrate-neutral and matches the educational and hobby-tier audience Move #3 is aimed at.

### Proposed capability manifest

The manifests live under `reference/petoi-runtime/src/petoi_runtime/manifests/`. A condensed shape for Bittle X:

```yaml
brand: petoi_bittle_x
profile: educational
mobility: legged_quadruped
dof: 9  # 8 leg + 1 head pan
mass_kg: 0.31
payload_kg: 0.05
transport: [serial, bluetooth]
controller: biboard_esp32
skills:
  - walk
  - trot
  - bound
  - sit
  - rest
  - stretch
  - push_up
  - balance
sensors:
  - imu_6dof
  - ultrasonic_optional
gripper: none
provenance:
  origin: CN
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The `gripper: none` row matters because it lets the URML validator reject a `grasp` primitive at static-verification time, rather than letting the program get to runtime and fail confusingly. The `provenance.origin: CN` row matches the disclosure pattern from [RFC-0061](0061-wlkata-outreach.md); the operator's policy file ([RFC-0004](0004-compliance-policy.md)) decides whether a Petoi manifest is acceptable in a given deployment context.

### Proposed conformance integration

A `URML_PETOI_INTEGRATION=1` env-gated CI workflow installs the OpenCat serial-command emulator, runs `PetoiAdapter` against a hermetic mock that replays IMU and joint-state responses, and asserts that the emitted commands match a recorded golden trace. The in-tree conformance suite continues to use `MockROSAdapter`. Hardware-in-the-loop against a real Bittle X is out of scope for this RFC.

### Hero-demo cross-link

URML's planned hero demo for Move #3 is a Bittle X on a desk executing a one-sentence English instruction ("walk forward two steps and sit") through URML's NL → primitive → adapter path. The demo is hermetic against `MockROSAdapter` (per the existing demo discipline) and uses `PetoiAdapter` only for the optional real-hardware lane. The cross-link to URML's existing hero discipline (per [`CLAUDE.md`](../../CLAUDE.md) §README hero and demo discipline) is intentional: a $299 quadruped is the smallest-scale, most-shareable demo URML's existing outreach landscape lacks.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none. The educational-profile manifest schema and the legged-mobility capability schema already accommodate a Bittle.
- Reference runtime: proposed new package `reference/petoi-runtime/`. Not built in this PR. The RFC requests PetoiCamp maintainer feedback first.
- Conformance suite: proposed new `petoi-integration.yml` CI workflow and a `URML_PETOI_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. No changes to existing URML artifacts. Petoi gains nothing yet; the adapter consumes OpenCat's published protocol surface without proposing changes to it.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.** The honest framing: URML wants PetoiCamp input on the skill-library mapping before shipping, because the `move_to`-to-gait-selection mapping is a design choice the OpenCat protocol does not pin down.
- **Skill-library motion forfeits fine-grained control.** A user who wants per-joint trajectory authoring will hit URML's deliberate ceiling on Petoi. The compensating frame: URML's audience on a Bittle is the educator / hobbyist who values English-to-motion, not the researcher who wants joint-level optimisation. The researcher path lives on Unitree, ANYmal, Spot, and Petoi's BiBoard if hand-rolled.
- **Gripper validation surface is small but real.** Programs written for an industrial arm cannot be retargeted to a Petoi without surgery, because the static-verification step rejects `grasp` / `release` on a no-gripper manifest. This is the right behaviour but worth flagging to a reader who expects substrate-neutrality to mean substrate-fungibility.
- **Bluetooth transport is not in the first cut.** Bittle X supports Bluetooth on its BiBoard ESP32, but the URML adapter starts with USB-serial. The future Bluetooth path is an additional surface to test and version.
- **Hardware acquisition cost is real but bounded.** URML's adapter authors need a Bittle X to validate the integration end-to-end. $299 is a small commitment relative to URML's other Move #1 targets, but it is a commitment.

## Alternatives considered

1. **Ship the adapter first, ask PetoiCamp maintainers later.** Rejected. The skill-library mapping (Q1 below) is a design choice with educator-visible consequences; a pre-RFC saves rework.
2. **Target only the existing `PetoiCamp/ros_opencat` ROS integration; skip native OpenCat serial.** Rejected. `ros_opencat` is at 24 stars and not the audience surface for Bittle X buyers; a hobbyist on Windows with a USB-serial dongle is the modal user, and that user does not run ROS 2.
3. **Fold Petoi into [RFC-0043 (Boston Dynamics Spot)](0043-boston-dynamics-spot-integration.md) or [RFC-0049 (ANYmal)](0049-anybotics-anymal-integration.md) as another quadruped row.** Rejected. The Move #1 quadruped audience is procurement-grade ($10k–$80k arms-length deployment); Petoi is hobby-tier ($299 desk toy). Conflating them blurs the Move #3 framing.
4. **Wait for OpenCat to publish a richer protocol surface.** Rejected. The existing skill-library surface is sufficient for URML's intent; URML's value-add is the substrate-neutral vocabulary and validation, not finer-grained motion control.

## Prior art

- `PetoiCamp/OpenCat`: the upstream firmware (4.8k stars, MIT, C++ primary, multi-platform).
- `PetoiCamp/OpenCatEsp32-Quadruped-Robot`: the ESP32 / BiBoard variant powering Bittle X (220 stars, MIT).
- `PetoiCamp/Petoi_MindPlusLib`: the Python wrapper around the OpenCat protocol (MIT, 7 stars).
- `PetoiCamp/ros_opencat`: the existing ROS integration (24 stars, CMake).
- `PetoiCamp/DesktopAppRelease` and the iOS / Android Petoi mobile apps: the parallel UI surfaces that share the OpenCat serial protocol.
- Petoi's books and curricula by Dr. Rongzhong Li: the education-channel context.
- [RFC-0009](0009-legged-humanoid-mobility.md): the legged-mobility capability schema this RFC's manifests use.
- [RFC-0011](0011-educational-profile.md): the educational profile.
- [RFC-0061](0061-wlkata-outreach.md): the parallel Move #3 RFC.
- [RFC-0043](0043-boston-dynamics-spot-integration.md), [RFC-0049](0049-anybotics-anymal-integration.md): the procurement-grade quadrupeds whose audience Petoi sits below.

## Unresolved questions

Provisional pending PetoiCamp maintainer feedback:

1. **Skill-library mapping.** Is the `move_to`-to-gait selection rule (direction and magnitude pick the gait token; duration scales the playback) the right shape, or would Petoi prefer a more explicit `gait()` primitive at URML's Layer-3?
2. **Adapter home.** Should URML host the adapter under `reference/petoi-runtime/` (URML-side), under a new repo in the `PetoiCamp` org as a contributed example, or both?
3. **Manifest granularity.** Is one manifest per product (Bittle X, Bittle original, Nybble Q) the right shape, or would Petoi prefer a single parametric `petoi` manifest with a variant field?
4. **`ros_opencat` alignment.** Should URML's adapter delegate to `PetoiCamp/ros_opencat` where ROS is present, or speak the OpenCat serial protocol directly even in ROS deployments?
5. **Add-ons.** Bittle has third-party and Petoi-made add-ons (gripper, claw, optional sensors). Is per-add-on manifest variation worth designing now, or deferred until first-party demand?
6. **Conformance lane.** Would Petoi be open to a URML conformance lane published on the OpenCat README or release notes?
7. **Anything else.**

## Implementation note

RFC-0062 ships as a single RFC document PR. No adapter code in this PR. The actual `reference/petoi-runtime/` package follows in a later session, gated on PetoiCamp maintainer feedback. Draft state. Second Move #3 RFC. Ledger entry in [`examples/lighthouses/outreach-move3.yaml`](../../examples/lighthouses/outreach-move3.yaml).

## Requested feedback (from PetoiCamp maintainers)

1. Skill-library mapping (implicit `move_to`-to-gait selection vs. explicit `gait()` primitive).
2. Adapter home (URML repo, PetoiCamp contributed example, both).
3. Manifest granularity (per-product, parametric).
4. `ros_opencat` alignment (delegate or speak protocol directly).
5. Add-on coverage (model now or defer).
6. Conformance-lane interest.
7. Anything else.

## How to respond

The `PetoiCamp/OpenCat` repo has Issues enabled (3 open at time of writing); Discussions status is not confirmed on the public page (verified attempt 2026-05-24). The repo is highly active and a labelled Issue is the documented surface. URML's planned channel: open a single Issue on `PetoiCamp/OpenCat` labelled `enhancement` (or the closest equivalent in the repo's label set), pointing to this RFC.

URML's own public Discussions for the broader Move #3 conversation:

> https://github.com/URML-MARS/URML/discussions

Private channel: [`MAINTAINERS.md`](../../MAINTAINERS.md).

## Self-review (Phase 0)

- [x] Summary alone tells a reader what is being proposed (and that this is proposal-only, and that this is the second Move #3 RFC).
- [x] Motivation grounded in verified technical alignment (OpenCat firmware at 4.8k stars MIT, OpenCatEsp32 at 220 stars MIT, Petoi_MindPlusLib Python wrapper, ros_opencat ROS integration, OpenCat skill library) plus the hero-demo positioning.
- [x] Detailed design uses verified repo names (`PetoiCamp/OpenCat`, `PetoiCamp/OpenCatEsp32-Quadruped-Robot`, `PetoiCamp/Petoi_MindPlusLib`, `PetoiCamp/ros_opencat`) and adapter-Protocol shape consistent with `reference/cobot-runtime/`.
- [x] At least one alternative considered (four are: ship-first, ROS-only, fold-into-Move-1-quadruped, wait-for-richer-protocol).
- [x] Drawbacks are real (proposal-only, skill-library motion ceiling, gripper-validation friction, USB-serial-only first cut, hardware acquisition cost).
- [x] Backward compatibility: purely additive when implemented.
- [x] No Layer-2 primitive added. The mapping uses the existing vocabulary; the `gait()` question is raised but the default mapping does not require a new primitive.
- [x] Implementation note explicitly says no adapter code in this PR.
- [x] Surface ("How to respond") is verified against the actual public surface of `PetoiCamp/OpenCat` as of 2026-05-24.
- [x] Provenance row (`origin: CN`) recorded honestly per URML's discipline, with the policy-decision boundary made explicit.
- [x] Re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do; compliant. No commercial-feature contribution. No cloud dependency. No telemetry. DCO sign-off applies to the RFC commit itself.
