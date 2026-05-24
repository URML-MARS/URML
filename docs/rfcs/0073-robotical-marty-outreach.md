---
rfc: 0073
title: Robotical (Marty) integration, request for comment from robotical maintainers
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

# RFC-0073: Robotical (Marty) integration, request for comment from robotical maintainers

## Summary

URML does not yet ship a Robotical integration. This RFC proposes a `RoboticalMartyAdapter` under [`reference/edu-runtime/`](../../reference/edu-runtime/) (or as a sibling to the existing `reference/petoi-runtime/` family if the educational-runtime placement does not fit) targeting [`robotical/martypy`](https://github.com/robotical/martypy) (Apache-2.0, Python 99.4%, v3.6.6 release 2024-01-12). The adapter routes URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`, plus posture composition) onto MartyPy's serial / WebSocket / BLE command surface for Marty v1 and Marty v2. No spec change on URML's side. This RFC documents the proposed mapping and requests review and feedback from the robotical maintainers.

This is the third Move #5 RFC. Robotical fills the **bipedal educational walking robot** niche: the closest analogue in URML's existing outreach is [RFC-0062 (Petoi Bittle / Nybble)](0062-petoi-bittle-outreach.md), but Petoi is quadruped and Marty is bipedal. The bipedal-classroom audience has been uncovered.

## Motivation

Marty is the bipedal counterpart to Petoi's Bittle in URML's outreach landscape: a commercial educational walking-robot vendor (UK-domiciled, Edinburgh) with a Python SDK, a Scratch-based block-coding surface (MartyBlocks), and a real classroom presence in UK and European STEM curricula. The audience overlap with Petoi is small (different mobility morphology, different curricular use cases), so a Marty integration broadens URML's educational footprint rather than duplicating it.

Three things make this RFC concrete rather than aspirational. First, `robotical/martypy` is Apache-2.0, Python 99.4%, with Issues enabled (2 open at time of writing); latest release v3.6.6 on 2024-01-12. The Python SDK is the canonical engagement surface. Second, Marty v2 (the current generation, released 2020) is a 9-DOF bipedal humanoid with an ESP32 controller and a documented serial / WebSocket / BLE command protocol that the SDK wraps. Third, the MartyBlocks visual-coding interface is conceptually adjacent to URML's English-to-program path: both wrap the same robot-intent surface with a more accessible programming abstraction; URML can position as the natural-language layer above MartyBlocks's block-based layer.

Robotical's posture is open SDK on closed hardware: MIT / Apache-2.0 across the public-facing Python SDK and example code, proprietary firmware on the Marty hardware. URML's adapter consumes the SDK and the documented command protocol without proposing firmware changes. Robotical is UK-domiciled; URML's US-federal default policy ([RFC-0003](0003-us-alignment.md)) passes at the manifest level for the UK origin without organisational override.

## Detailed design

### Proposed `RoboticalMartyAdapter` shape

One adapter, parameterised by Marty generation (v1 / v2). Package layout:

```
reference/edu-runtime/src/edu_runtime/robotical/
├── __init__.py
├── adapter.py             # RoboticalMartyAdapter
├── martypy_wrapper.py     # martypy SDK call wrappers
├── skills.py              # mapping URML primitives to Marty skill commands
└── manifests/
    ├── robotical_marty_v1.yaml
    └── robotical_marty_v2.yaml
```

The adapter implements URML's substrate Protocol via `martypy.Marty` connection objects. Three transports per Marty v2: USB-serial, WebSocket (over Wi-Fi), BLE; the URML manifest declares which transport the deployment uses.

### Proposed URML v0.1 to Robotical mapping

| URML primitive | Marty realisation |
|---|---|
| `move_to(pose)` | A `walk` / `kick` / `arms` / `lean` / `eyes` skill call via `martypy.Marty(...).walk(...)` or similar. URML's pose maps to direction + step-count + speed. Like Bittle ([RFC-0062](0062-petoi-bittle-outreach.md)), Marty is skill-library-driven rather than per-joint-trajectory; the URML adapter does not emit joint targets. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable on stock Marty (no gripper). Manifest declares `gripper: none`; static verifier rejects programs using these primitives on a Marty manifest. |
| `measure(sensor_id)` | A `get_accelerometer()` / `get_battery_voltage()` / etc. call via the SDK. Marty v2 has an IMU and battery sensor at minimum. |
| `wait_for(...)` | Polling loop on the sensor stream with debounce. |
| `report(status)` | Append to per-session log file plus stdout; optional `martypy.Marty().eyes(...)` for visible status indication. |
| `pose(posture_id)` (Layer-3 composition) | A named-skill call from the Marty skill library (e.g., `stand_straight`, `kick`, `wave`). |

### Proposed capability manifest

A condensed shape for `robotical_marty_v2`:

```yaml
brand: robotical_marty_v2
profile: educational
mobility: legged_bipedal
dof: 9
mass_kg: 0.85
height_m: 0.35
transport: [serial, websocket, ble]
python_sdk: martypy
sdk_version_min: 3.6.6
skills:
  - walk
  - kick
  - arms
  - lean
  - eyes
  - dance
gripper: none
controller: esp32
provenance:
  origin: GB
  ndaa_section_889_status: not_listed
  default_policy: pass
```

The skill list mirrors Bittle's structure ([RFC-0062](0062-petoi-bittle-outreach.md)). Robotical and Petoi both speak skill-library command languages even though their hardware morphologies differ.

### Cross-link to RFC-0062 (Petoi)

Marty (bipedal) and Bittle (quadruped) are the two URML educational legged-robot targets. The adapter pattern is intentionally consistent: skill-library mapping with no joint-target emission, gripper-less manifest, low-cost educational tier. A URML program written for Bittle does not directly retarget to Marty (the gait vocabulary differs), but the URML primitive-set the program emits does.

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/edu-runtime/src/edu_runtime/robotical/`. Not built in this PR.
- Conformance suite: proposed new `robotical-integration.yml` CI workflow and a `URML_ROBOTICAL_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only is a weaker artifact than a shipping adapter.**
- **Skill-library motion forfeits joint-target authoring.** Same trade-off as Bittle ([RFC-0062](0062-petoi-bittle-outreach.md)).
- **martypy star count is low (6 stars).** Low GitHub footprint doesn't reflect the actual classroom deployment scale, which is documented at `robotical.io` but not reflected in repo stars.
- **martypy release cadence has slowed.** Latest release v3.6.6 on 2024-01-12 (about 18 months stale at time of writing); needs maintainer input on whether the platform is actively developed or in maintenance mode.
- **Triple transport (serial / WebSocket / BLE).** Increases the test matrix.

## Alternatives considered

1. **Ship the adapter first.** Rejected.
2. **Skip Marty v1 and target only Marty v2.** Rejected. V1 deployments remain in classroom use; the SDK already supports both.
3. **Fold Marty into [RFC-0062 (Petoi)](0062-petoi-bittle-outreach.md) as another DIY-walking-robot vendor.** Rejected. Different audiences (Petoi is global maker / hobbyist; Marty is UK / European education-channel), different morphologies.
4. **Wait for MartyBlocks 2.0 / Marty v3.** Rejected. Current SDK is sufficient for the proposal.

## Prior art

- `robotical/martypy` (Apache-2.0, 6 stars, Python 99.4%, v3.6.6 2024-01-12).
- MartyBlocks: the Scratch-based visual coding interface.
- Marty v2 product page at `robotical.io`.
- [RFC-0011](0011-educational-profile.md): the educational profile.
- [RFC-0062](0062-petoi-bittle-outreach.md): the parallel quadruped DIY-walking-robot RFC.

## Unresolved questions

1. **Adapter home.** URML repo or robotical contributed example?
2. **Active development cadence.** Is the platform actively developed or in maintenance mode?
3. **Transport priority.** Which transport should URML's adapter default to (serial / WebSocket / BLE)?
4. **MartyBlocks alignment.** Is there interest in coordinating URML's natural-language layer with MartyBlocks's block-based layer?
5. **Conformance lane.** Open to a URML conformance line on `robotical/martypy` README or `robotical.io` docs?
6. **Anything else.**

## Implementation note

RFC-0073 ships as a single RFC document PR. No adapter code in this PR. Ledger entry in [`examples/lighthouses/outreach-move5.yaml`](../../examples/lighthouses/outreach-move5.yaml).

## Requested feedback (from robotical maintainers)

1. Adapter home.
2. Active development cadence.
3. Transport priority.
4. MartyBlocks coordination.
5. Conformance-lane interest.
6. Anything else.

## How to respond

`robotical/martypy` has Issues enabled (2 open at time of writing; verified 2026-05-24). URML's planned channel: open a single Issue on `robotical/martypy` labelled with the closest `enhancement` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Summary, Motivation, and Detailed design grounded in verified `robotical/martypy` surface.
- [x] At least one alternative considered (four).
- [x] Drawbacks real (proposal-only, skill-library motion ceiling, low star count, stale release cadence, triple transport).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified as of 2026-05-24.
- [x] Provenance `origin: GB` recorded; US-federal default policy passes.
- [x] CLAUDE.md compliance check passed.
