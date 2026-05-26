---
rfc: 0094
title: Burro Robotics integration, request for comment from burro-robotics maintainers
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

# RFC-0094: Burro Robotics integration, request for comment from burro-robotics maintainers

## Summary

URML does not yet ship a Burro integration. This RFC proposes a `BurroAdapter` under [`reference/agriculture-runtime/`](../../reference/agriculture-runtime/) (the new runtime placeholder from RFC-0067) targeting the [`burro-robotics` GitHub org](https://github.com/burro-robotics) (34 public repos, license mix BSD-3-Clause / Apache-2.0 / MIT / ISC / GPL-2.0) and the documented BOSS Cloud API for fleet telemetry + WMS integration. The adapter routes URML Layer-2 primitives onto Burro's fleet-coordination surface without proposing changes upstream. No spec change on URML's side. Third Move #7 RFC.

Burro is URML's first **commercial agriculture-cobot** RFC. Where RFC-0067 (FarmBot) targets DIY raised-bed farming and RFC-0092 (Acorn) targets open-source rover platforms, Burro Robotics is a commercial follow-the-picking-crew autonomous cobot with 300+ units deployed across 40+ customers in 6 countries; proven commercial deployment scale in the agriculture vertical.

## Motivation

Burro fills a specific niche: a US commercial agriculture-cobot vendor with **real deployment scale** (300+ units in operation, $24M Series B in 2024) plus a **public GitHub org with 34 repos** and a **documented BOSS Cloud API** for fleet telemetry. URML's substrate-neutral fleet-coordination layer would sit one level above BOSS; a program described once and dispatched across heterogeneous fleets (Burro cobots + ground rovers + drones) instead of per-vendor.

Verified surface (2026-05-26):
- `burro-robotics` GitHub org: 34 public repos.
- License pattern: BSD-3-Clause + Apache-2.0 + MIT + ISC + GPL-2.0 across the org.
- Star counts on repos are small (top `burro-sdk` 2 stars, `geojson-path-finder2` 1 star, `aubo_robot` 1 star); the org's public surface is small-but-real, complementing the commercial-deployment scale.
- HQ: USA. 300+ units in 6 countries.
- Notable repos: `burro-sdk`, `geojson-path-finder2`, `turf-extensions`, `aubo_robot`, `Mid360_simulation_plugin`, `dwarves`.
- BOSS Cloud API documented on Burro's website for fleet telemetry + WMS integration.

URML's specific value for Burro:
- **BOSS Cloud API + URML composition.** URML programs describe intent ("send the Burro to the next picking station and report when arrived"); BOSS Cloud handles the actual fleet dispatch on Burro hardware. URML's substrate-Protocol abstraction sits at the intent layer above the fleet API.
- **Multi-vendor fleet orchestration.** A URML program targeting `burro_fleet` retargets to a future open-source-rover fleet ([RFC-0092 (Acorn)](0092-twisted-fields-acorn-outreach.md)) or to a research-grade ag rover by manifest swap. The cross-substrate story is the natural value proposition for a customer running mixed-vendor agriculture operations.
- **Cross-link to [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md).** URML's open RFC-0053 outreach targets the multi-robot framework; Burro's BOSS Cloud is the commercial-grade counterpart at the agriculture-specific fleet layer.

## Detailed design

URML's existing artifacts that feed into a Burro adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- A future `reference/agriculture-runtime/` (proposed by RFC-0067; AcornAdapter from RFC-0092 will be the first adapter; BurroAdapter would be the second).
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Twisted Fields Acorn)](0092-twisted-fields-acorn-outreach.md): the agricultural-vertical precedents.
- [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md): URML's multi-robot fleet-management outreach (deployment-grade fleet management); BurroAdapter's BOSS Cloud API composes with this layer.

### Proposed `BurroAdapter` shape

```
reference/agriculture-runtime/src/agriculture_runtime/burro/
├── __init__.py
├── adapter.py             # BurroAdapter
├── boss_cloud_client.py   # BOSS Cloud API wrapper
└── manifests/
    └── burro_robotics_cobot.yaml
```

The adapter implements URML's substrate Protocol against the BOSS Cloud API. The deployment supplies API credentials (URML's policy: no cloud dependency baked into URML itself; the BOSS Cloud is the operator's choice).

### Proposed URML v0.1 to Burro mapping

| URML primitive | Burro realisation |
|---|---|
| `move_to(pose)` | A waypoint or named-station dispatch via the BOSS Cloud API; Burro's onboard autonomy handles the actual navigation. |
| `grasp(gripper_id)` / `release(gripper_id)` | Not applicable on the stock cobot (no gripper). Manifest declares `gripper: none`; the Burro is a "follow the picker" cart, not a manipulator. |
| `measure(sensor_id)` | A telemetry pull via BOSS Cloud (position, battery, load-cell weight if equipped). |
| `wait_for(...)` | Polling the BOSS Cloud telemetry stream with debounce, or webhook subscription. |
| `report(status)` | Append to per-session log + optional WMS-integration update via BOSS Cloud's documented webhook. |

### Proposed capability manifest

```yaml
brand: burro_robotics_cobot
profile: industrial
mobility: wheeled_skid_steer
mass_kg: 220.0   # approximate; pending maintainer confirmation
payload_kg: 500.0   # approximate
max_velocity: 1.6
transport: boss_cloud_api
boss_cloud:
  endpoint: configurable
  auth: api_key
sensors:
  - rtk_gps
  - imu_6dof
  - load_cell_optional
gripper: none
follow_modes:
  - follow_picker
  - waypoint
  - station
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new sub-package `reference/agriculture-runtime/src/agriculture_runtime/burro/`. Not built in this PR.
- Conformance suite: proposed new `burro-integration.yml` CI workflow + `URML_BURRO_INTEGRATION` env gate.

## Backward compatibility

Pre-v1.0. Purely additive when implemented.

## Drawbacks

- **Proposal-only.**
- **BOSS Cloud is a proprietary cloud service.** URML's "validated programs run offline" rule applies: the adapter's hermetic test suite uses a mock BOSS Cloud responder, and the operator-side decision to use the real cloud is documented in the deployment guide, not baked into URML.
- **Star counts on the GitHub org are small.** The public footprint understates the commercial-deployment scale (300+ units in production). URML's RFC body should not rely on repo stars as a signal.
- **`burro-sdk` license / scope unclear from outside.** The RFC asks the maintainers about the SDK's intended use surface (deployment integrations? hardware drivers? both?).
- **Manifest values are approximate pending maintainer confirmation.**

## Alternatives considered

1. **Ship the adapter first.** Rejected. The BOSS-Cloud-vs-direct-control surface and the manifest authoritative values are maintainer-input questions.
2. **Fold BurroAdapter into RFC-0067 (FarmBot) as a fellow ag platform.** Rejected. FarmBot is DIY Cartesian gantry, Burro is commercial fleet-coordinated cobot. Different audiences, different deployment scales.
3. **Target Burro via RFC-0053 (Open-RMF) as another fleet vendor.** Rejected. RFC-0053 is for the Open-RMF multi-robot framework; Burro's BOSS Cloud is a different fleet-coordination stack. Cross-link, not collapse.

## Prior art

- `burro-robotics` GitHub org (34 public repos, license mix BSD-3-Clause / Apache-2.0 / MIT / ISC / GPL-2.0).
- `burro-robotics/burro-sdk`, `geojson-path-finder2`, `turf-extensions`, `aubo_robot`, `Mid360_simulation_plugin`, `dwarves`.
- Burro Robotics product page + documented BOSS Cloud API.
- $24M Series B (2024); 300+ units, 40+ customers, 6 countries.
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md), [RFC-0092 (Acorn)](0092-twisted-fields-acorn-outreach.md): agriculture-vertical precedents.
- [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md): URML's multi-robot fleet-management cross-link.

## Unresolved questions

For the Burro Robotics maintainers:

1. **Adapter home.** URML repo (`reference/agriculture-runtime/src/agriculture_runtime/burro/`), burro-robotics contributed example, both?
2. **BOSS Cloud API stability.** Is the BOSS API URL + auth model versioned and stable for third-party adapter integration?
3. **`burro-sdk` scope.** What is the intended use surface for `burro-sdk` (deployment integration, hardware drivers, both)?
4. **Manifest authoritative values.** Mass, payload, max velocity, follow-mode inventory pending maintainer confirmation.
5. **Fleet-coordination cross-link.** Is there interest in coordinating with URML's open [RFC-0053 (Open-RMF)](0053-open-rmf-multirobot-integration.md) outreach on fleet-management abstraction?
6. **Conformance lane.** Open to a URML conformance line on `burro-sdk` README or burrorobotics.com docs?
7. **Anything else.**

## Implementation note

RFC-0094 ships as a single RFC document PR. No adapter code in this PR. Third Move #7 RFC; URML's first commercial-agriculture-cobot outreach. Ledger entry in [`examples/lighthouses/outreach-move7.yaml`](../../examples/lighthouses/outreach-move7.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`burro-robotics/burro-sdk` is the most-likely public engagement surface (2 stars; verified 2026-05-26). URML's planned channel: open a single Issue on `burro-robotics/burro-sdk` labelled with the closest `enhancement` / `question` equivalent, pointing to this RFC. Optional courtesy email to Burro's developer-relations team via burrorobotics.com.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Motivation grounded in verified `burro-robotics` surface and stated commercial deployment scale.
- [x] BOSS Cloud API surface acknowledged honestly (proprietary cloud; URML's offline-execution discipline preserved).
- [x] Star-count-vs-deployment-scale gap surfaced in drawbacks.
- [x] Cross-link to RFC-0067 + RFC-0092 (ag verticals) + RFC-0053 (fleet) explicit.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, BOSS Cloud proprietary, small star counts, `burro-sdk` scope unclear, approximate manifest values).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
