---
rfc: 0093
title: Sentera integration, request for comment from SenteraLLC maintainers
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

# RFC-0093: Sentera integration, request for comment from SenteraLLC maintainers

## Summary

URML does not yet ship a Sentera integration. This RFC proposes a `SenteraAdapter` extending URML's existing [`reference/px4-runtime/`](../../reference/px4-runtime/) (MAVLink + PX4 substrate) for Sentera's PHX fixed-wing platform and multispectral payloads (Double 4K, 6X). The adapter routes URML Layer-2 primitives (`move_to(pose)`, `measure(sensor_id)`, `wait_for(...)`, `report(...)`) onto Sentera's documented MAVLink integration plus the [`SenteraLLC` GitHub org](https://github.com/SenteraLLC) Python utility libraries (`py-radiometric-corrections` Apache-2.0, `py-image-registration`, `py-image-metadata-parser`). No spec change on URML's side. Second Move #7 RFC.

Sentera is URML's first **ag-drone** RFC. Move #4 RFC-0067 covered agricultural ground robotics (FarmBot); RFC-0092 (Move #7, parallel) covers a solar-powered ground rover. RFC-0093 adds the aerial-substrate sibling for the agriculture vertical, on top of URML's existing PX4/MAVLink substrate (which ships via `marine-runtime` BlueRovAdapter against ArduSub today).

## Motivation

Sentera fills a specific niche URML's outreach landscape has been missing: a US-domiciled commercial ag-drone vendor with a **real public Python utility surface** plus documented MAVLink integration for multispectral payloads. The audience overlap is exact: an agronomist authoring an aerial scout mission ("photograph the field on a 10-meter grid and record the multispectral signature at each waypoint") is exactly URML's English-to-primitive use case.

Verified surface (2026-05-26):
- `SenteraLLC` GitHub org: 63 public repos, 26 followers.
- Top-starred Python libs: `ulabel` (27 stars, MIT, JavaScript labelling tool), **`py-radiometric-corrections` (21 stars, Apache-2.0)**, `py-image-registration` (8 stars), `dspic33-servo-can-node.X` (5 stars, archived C), `py-image-metadata-parser` (4 stars).
- **MAVLink ecosystem engagement confirmed:** the org maintains forks of `MAVSDK` and `MAVSDK-Swift` (BSD-3-Clause). Sentera's documented MAVLink integration guide at `support.sentera.com` covers Double 4K and 6X multispectral sensors.
- HQ: Minneapolis, MN, USA.
- Most-active repo (`ulabel`) last updated 2026-05-11.

URML's specific value for Sentera:
- **PX4-runtime composition.** Sentera's MAVLink-compatible payloads dispatch directly through URML's existing `reference/px4-runtime/` substrate without a new transport layer. The adapter is a thin layer above the existing PX4 runtime.
- **English-to-aerial-mission path.** URML's natural-language layer (per [RFC-0021](0021-on-device-llm-bridge.md)) compiles aerial-scout instructions into URML primitive sequences that Sentera's autopilot executes.
- **Multispectral payload abstraction.** URML's `measure` primitive with a typed `payload:` field can target Sentera's Double 4K / 6X output streams as substrate-neutral readings; programs written against one payload retarget to the other by manifest swap.

## Detailed design

URML's existing artifacts that feed into a Sentera adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [`reference/px4-runtime/`](../../reference/px4-runtime/): the existing PX4 / MAVLink substrate (currently consumed by marine-runtime's BlueRovAdapter for ArduSub).
- [RFC-0041 (ArduPilot)](0041-ardupilot-integration.md): institutional context for URML's MAVLink-ecosystem outreach (URML imports `ArduPilot/pymavlink` via px4-runtime; ArduPilot maintainers declined URML's GitHub Issue surface on 2026-05-26 and URML accepted the close, but no functional impact on URML's MAVLink dispatch path).
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Acorn)](0092-twisted-fields-acorn-outreach.md): the agricultural-vertical precedents on ground substrates.
- [RFC-0021](0021-on-device-llm-bridge.md): the on-device LLM bridge that powers URML's English-to-primitive translation.

### Proposed `SenteraAdapter` shape

```
reference/px4-runtime/src/px4_runtime/sentera/
├── __init__.py
├── adapter.py                # SenteraAdapter
├── multispectral_payload.py  # Double 4K / 6X read-side helpers
└── manifests/
    ├── sentera_phx_double4k.yaml
    └── sentera_phx_6x.yaml
```

The adapter implements URML's substrate Protocol against the existing PX4/MAVLink dispatch path. The `multispectral_payload.py` module wraps `SenteraLLC/py-radiometric-corrections` + `py-image-metadata-parser` for the read-side of `measure(multispectral_band_X)`.

### Proposed URML v0.1 to Sentera mapping

| URML primitive | Sentera realisation |
|---|---|
| `move_to(pose)` | MAVLink waypoint command via `pymavlink` (consumed through URML's px4-runtime); Sentera's autopilot handles fixed-wing approach / loiter / landing. |
| `take_off(altitude)` / `land(at)` | Per-platform MAVLink commands; deployment-side check that the runway / launch profile matches the PHX spec. |
| `measure(sensor_id)` | One-shot read from the Double 4K / 6X multispectral payload via Sentera's documented MAVLink-integration path; output processed through `py-radiometric-corrections` to produce a calibrated band-level reading. |
| `wait_for(...)` | MAVLink message subscriber with debounce, identical pattern to URML's other px4-runtime adapters. |
| `report(status)` | Log + optional `STATUSTEXT` MAVLink message. |
| `scan(area, pattern)` | A grid / serpentine scan compiled to a sequence of `move_to` + `measure` primitives; the deployment's flight planner consumes the URML output. |

### Proposed capability manifest

A condensed shape for `sentera_phx_double4k`:

```yaml
brand: sentera_phx_double4k
profile: research
mobility: fixed_wing
max_velocity: 22.0   # m/s, approximate
service_ceiling: 120.0   # m AGL, regulatory ceiling
station_keeping: false
transport: mavlink_via_px4_runtime
mavlink:
  dialect: ardupilot
  pymavlink_version_min: 2.4
payload:
  type: multispectral
  bands: 4   # Double 4K
  python_helpers: SenteraLLC/py-radiometric-corrections
sensors:
  - rgb_4k
  - multispectral_band_1
  - multispectral_band_2
  - multispectral_band_3
  - multispectral_band_4
  - imu_6dof
  - gps
gripper: none
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/px4-runtime/src/px4_runtime/sentera/`. Not built in this PR.
- Conformance suite: proposed new `sentera-integration.yml` CI workflow + `URML_SENTERA_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **Sentera's GitHub footprint is utility libraries, not the autopilot.** Sentera publishes Python image-processing libs (Apache-2.0); the autopilot side ships as Sentera FieldAgent + the documented MAVLink interface. URML's adapter composes both surfaces.
- **Regulatory ceiling (FAA Part 107 for US deployments).** URML's manifest declares `service_ceiling`, but per-deployment regulatory compliance is the operator's responsibility, not URML's.
- **Multispectral band semantics are payload-specific.** The Double 4K and 6X manifests declare different band inventories; programs written for one are not automatically valid for the other. URML's static validator catches this at manifest-load time.
- **Manifest values are approximate.** Maximum velocity and other parameters need maintainer confirmation against Sentera's published spec.

## Alternatives considered

1. **Ship the adapter first.** Rejected. The Double-4K-vs-6X manifest split and the multispectral-band semantics are observable choices.
2. **Skip ag-drones in Move #7 entirely.** Rejected. The aerial-substrate sibling for agriculture is the missing piece in URML's vertical landscape after RFC-0067 (FarmBot) and RFC-0092 (Acorn).

## Prior art

- `SenteraLLC` GitHub org (63 public repos, 26 followers).
- `SenteraLLC/py-radiometric-corrections` (21 stars, Apache-2.0).
- `SenteraLLC/MAVSDK`, `SenteraLLC/MAVSDK-Swift` (BSD-3-Clause forks).
- Sentera MAVLink integration guide (`support.sentera.com/portal/en/kb/articles/double-4k-single-and-6x-multispectral-sensor-mavlink-integration-guide`).
- [`reference/px4-runtime/`](../../reference/px4-runtime/): URML's PX4 / MAVLink substrate.
- [RFC-0041 (ArduPilot)](0041-ardupilot-integration.md): URML's MAVLink-ecosystem outreach (institutional context only).
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Acorn)](0092-twisted-fields-acorn-outreach.md): ground-substrate ag precedents.
- [RFC-0021](0021-on-device-llm-bridge.md): URML's on-device LLM bridge for natural-language input.

## Unresolved questions

For the SenteraLLC maintainers:

1. **Adapter home.** URML repo (`reference/px4-runtime/src/px4_runtime/sentera/`), SenteraLLC contributed example, both?
2. **Payload manifest granularity.** Per-payload manifests (Double 4K / 6X) or a single parametric `sentera_phx` manifest with a `payload:` field?
3. **Authoritative manifest values.** Maximum velocity, service ceiling, payload band inventories pending maintainer confirmation.
4. **MAVLink dialect / version.** Which ArduPilot / PX4 dialect version does Sentera test against?
5. **Multispectral-band naming.** Should URML adopt Sentera's band naming (NDVI / NDRE / etc.) at the manifest level, or stay generic (`multispectral_band_1..N`)?
6. **Conformance lane.** Open to a URML conformance line on the SenteraLLC org README or `support.sentera.com`?
7. **Anything else.**

## Implementation note

RFC-0093 ships as a single RFC document PR. No adapter code in this PR. Second Move #7 RFC; URML's first ag-drone outreach. Ledger entry in [`examples/lighthouses/outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`SenteraLLC/py-radiometric-corrections` is the most-relevant Apache-2.0 Python library in the SenteraLLC org (21 stars; verified 2026-05-26). URML's planned channel: open a single Issue on `SenteraLLC/py-radiometric-corrections` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional cross-reference on `SenteraLLC/MAVSDK` if maintainers prefer the MAVLink-specific surface.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Motivation grounded in verified `SenteraLLC` surface (63 repos, named libs, MAVLink fork confirmed).
- [x] Composition with existing URML px4-runtime made explicit.
- [x] Cross-link to RFC-0067 (FarmBot) + RFC-0092 (Acorn) explicit; aerial-substrate sibling for ag vertical.
- [x] At least one alternative considered (two).
- [x] Drawbacks real (proposal-only, utility-libs-not-autopilot, FAA Part 107, payload-specific band semantics, approximate manifest values).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
