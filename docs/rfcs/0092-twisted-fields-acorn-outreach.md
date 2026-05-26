---
rfc: 0092
title: Twisted Fields / Acorn integration, request for comment from Twisted-Fields maintainers
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-26
updated: 2026-05-26
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

# RFC-0092: Twisted Fields / Acorn integration, request for comment from Twisted-Fields maintainers

## Summary

URML does not yet ship a Twisted Fields integration. This RFC proposes an `AcornAdapter` under [`reference/agriculture-runtime/`](../../reference/agriculture-runtime/) (the new runtime placeholder from RFC-0067) targeting the [`Twisted-Fields/acorn-precision-farming-rover`](https://github.com/Twisted-Fields/acorn-precision-farming-rover) software (275 stars, Apache-2.0, 7 open issues, last commit 2024-07-06), the [`acorn-robot-electronics`](https://github.com/Twisted-Fields/acorn-robot-electronics) KiCAD designs, and the [`acorn-mechanical-designs`](https://github.com/Twisted-Fields/acorn-mechanical-designs) CAD repository. The adapter routes URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) onto Acorn's control surface without proposing changes to the upstream Apache-2.0 codebase. No spec change on URML's side. First Move #7 RFC.

This is the second URML outreach into the agricultural vertical after [RFC-0067 (FarmBot)](0067-farmbot-outreach.md). Where FarmBot is a Cartesian gantry for fixed-plot raised-bed farming, Acorn is a **solar-powered modular precision-farming rover** for over-the-row autonomous navigation. Different morphology, same broad vertical.

## Motivation

Acorn is the cleanest open-source agriculture-rover URML has surfaced. The license is Apache-2.0 (matches URML's `reference/` posture), the audience is exactly the maker / farmer / educator who would benefit from URML's English-to-primitive path, and the platform is real hardware shipped by a US 501(c)(3) (Twisted Fields, Bay Area).

Verified surface (2026-05-26):
- Twisted-Fields org has 9 public repos and 238 followers.
- Top-starred: `rp2040-motor-controller` (413 stars), `acorn-precision-farming-rover` (275 stars, Apache-2.0), `acorn-robot-electronics` (79 stars, KiCAD PCBs), `acorn-mechanical-designs` (47 stars), `rp2040-motor-firmware` (Apache-2.0).
- 7 open issues on the core rover repo, 3 open PRs, 38 forks.
- Last commit on `acorn-precision-farming-rover`: 2024-07-06 (about 11 months stale).
- HQ: Bay Area, CA, USA.

URML's specific value for Twisted Fields:
- **English-to-rover-mission path.** A farmer writes "drive the rover along row 3 and measure soil moisture every 2 meters" in URML's natural-language layer; URML compiles to `move_to(...)` + `measure(soil_moisture, ...)` + `wait_for(distance, 2m)`; the AcornAdapter dispatches the primitives.
- **Cross-substrate retargetability.** A URML program written against an Acorn retargets to FarmBot (Cartesian gantry, RFC-0067), to a future agricultural drone, or to a research-grade ag rover with no source changes. The substrate-neutral story is exactly what an open-source DIY ag platform needs to grow beyond its own hardware.
- **Apache-2.0 license fit.** Direct code-reuse and contributions can flow both ways. Mirrors URML's `reference/marine-runtime/` BlueRovAdapter pattern (also Apache-2.0 upstream).

## Detailed design

URML's existing artifacts that feed into an Acorn adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md): the agricultural-vertical precedent; raises the future `spec/profiles/agriculture/` profile question (`plant` / `water` / `weed` / `scout` as Layer-3 vocabulary). Not proposed in this RFC.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles relevant to Acorn (the audience is educators + small-farm operators + researchers).
- A new `reference/agriculture-runtime/` package (already proposed by RFC-0067, not yet built). AcornAdapter would be the second adapter in that runtime, alongside `FarmBotAdapter`.

### Proposed `AcornAdapter` shape

```
reference/agriculture-runtime/src/agriculture_runtime/twisted_fields/
├── __init__.py
├── adapter.py             # AcornAdapter
├── acorn_protocol.py      # control-surface wrapper for the rover
└── manifests/
    └── twisted_fields_acorn.yaml
```

The adapter implements URML's substrate Protocol. The transport is the Acorn rover's control surface (the project's `acorn-precision-farming-rover` software, which runs on the rover's onboard compute).

### Proposed URML v0.1 to Acorn mapping

| URML primitive | Acorn realisation |
|---|---|
| `move_to(pose)` | A waypoint command to Acorn's autonomous-navigation layer (the rover handles RTK-GPS + path-following internally). |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable on the stock rover (no gripper). The manifest declares `gripper: none`; future tool-mount add-ons would compose. |
| `measure(sensor_id)` | A one-shot read of the rover's onboard sensors (soil-moisture probe, multispectral camera, etc., per the deployment's payload). |
| `wait_for(...)` | A polling loop on the named sensor / event with debounce, mirroring the FarmBot pattern from RFC-0067. |
| `report(status)` | Append to a per-session log file. Optional MQTT publish if the deployment runs a local broker. |

### Proposed capability manifest

```yaml
brand: twisted_fields_acorn
profile: educational
mobility: wheeled_skid_steer  # 4-wheel-drive with skid-steer
workspace_m: outdoor_field
mass_kg: 30.0   # approximate; pending maintainer confirmation
payload_kg: 20.0
transport: python_local
python_package: acorn_precision_farming_rover
controller: rp2040_motor_controller_plus_onboard_compute
solar_powered: true
sensors:
  - rtk_gps
  - imu_6dof
  - soil_moisture_optional
  - multispectral_camera_optional
gripper: none
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
license_alignment: apache_2_0_upstream
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/agriculture-runtime/src/agriculture_runtime/twisted_fields/`. Not built in this PR. RFC-0067 already proposed the parent `reference/agriculture-runtime/` package; AcornAdapter would be the second adapter in it.
- Conformance suite: proposed new `acorn-integration.yml` CI workflow + `URML_ACORN_INTEGRATION` env gate. Hermetic suite first; hardware-in-the-loop deferred.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.** No code in this RFC.
- **Repo cadence is uneven.** Last commit on `acorn-precision-farming-rover` is 2024-07-06; maintainer cadence appears slower than the org's electronics work (rp2040-motor-controller is the highest-starred repo at 413 stars, suggesting the firmware side gets more attention than the application stack). URML's adapter takes on the maintenance risk.
- **Manifest values are approximate pending maintainer confirmation.** Mass, payload, and DOF should come from Twisted Fields' authoritative spec.
- **Solar power introduces operational constraints.** URML's `move_to` should not naively assume always-available power; the manifest's `solar_powered: true` flag is a future-Spec-RFC hook (battery-state-aware execution).

## Alternatives considered

1. **Ship the adapter first, ask Twisted Fields later.** Rejected. The skid-steer-vs-differential question and the manifest mass/payload values are observable choices worth maintainer input.
2. **Fold AcornAdapter into [RFC-0067 (FarmBot)](0067-farmbot-outreach.md) as another ag-runtime example.** Rejected. FarmBot is Cartesian gantry; Acorn is mobile rover. Different mobility, different audience.

## Prior art

- [`Twisted-Fields/acorn-precision-farming-rover`](https://github.com/Twisted-Fields/acorn-precision-farming-rover) (275 stars, Apache-2.0, 7 open issues, last commit 2024-07-06).
- [`Twisted-Fields/acorn-robot-electronics`](https://github.com/Twisted-Fields/acorn-robot-electronics) (79 stars, KiCAD).
- [`Twisted-Fields/acorn-mechanical-designs`](https://github.com/Twisted-Fields/acorn-mechanical-designs) (47 stars).
- [`Twisted-Fields/rp2040-motor-controller`](https://github.com/Twisted-Fields/rp2040-motor-controller) (413 stars, the firmware highest-starred).
- Twisted Fields website + 501(c)(3) status.
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md): URML's first ag-vertical RFC.
- [RFC-0009](0009-legged-humanoid-mobility.md): URML's mobility-capability schema.

## Unresolved questions

For the Twisted Fields maintainers:

1. **Adapter home.** URML repo (`reference/agriculture-runtime/src/agriculture_runtime/twisted_fields/`), Twisted-Fields contributed example, both?
2. **Authoritative manifest values.** Mass, payload, sensor-inventory pending maintainer confirmation.
3. **Repo cadence.** Is `acorn-precision-farming-rover` actively maintained (next planned release), in maintenance-only mode, or paused?
4. **Solar-power / battery-aware execution.** Should URML's static verifier reason about battery state at validation time (a future Spec RFC question raised by this manifest's `solar_powered: true` flag)?
5. **Agriculture-profile co-design.** Interest in coordinating with RFC-0067 (FarmBot) on a future `spec/profiles/agriculture/` Layer-3 vocabulary?
6. **Conformance lane.** Open to a URML conformance line on the rover README?
7. **Anything else.**

## Implementation note

RFC-0092 ships as a single RFC document PR. No adapter code in this PR. First Move #7 RFC; the strongest open-source ag candidate URML has surfaced. Ledger entry in [`examples/lighthouses/outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`Twisted-Fields/acorn-precision-farming-rover` has Issues enabled (7 open, verified 2026-05-26). URML's planned channel: open a single Issue on the rover repo labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Motivation grounded in verified `Twisted-Fields` surface and named repos.
- [x] Apache-2.0 license alignment surfaced.
- [x] Cross-link to RFC-0067 (FarmBot) explicit; first vs second ag-vertical RFC differentiated by morphology.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, repo cadence stale, approximate manifest values, solar-power constraint).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added. Agriculture-profile question deferred to a future Spec RFC.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
