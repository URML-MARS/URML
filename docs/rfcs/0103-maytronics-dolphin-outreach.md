---
rfc: 0103
title: Maytronics Dolphin integration, request for comment from dolphin-robot HA-integration maintainer
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

# RFC-0103: Maytronics Dolphin integration, request for comment from dolphin-robot HA-integration maintainer

## Summary

URML does not yet ship a Maytronics Dolphin integration. This RFC proposes a `MaytronicsDolphinAdapter` under the new [`reference/home-runtime/`](../../reference/home-runtime/) package (proposed by [RFC-0100](0100-irobot-roomba-outreach.md)) targeting the [`sh00t2kill/dolphin-robot`](https://github.com/sh00t2kill/dolphin-robot) Home Assistant integration (Python, 75 stars, 6 open issues, Issues enabled, last commit 2026-05-25). The adapter routes URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) onto Dolphin's WiFi-API surface without proposing upstream changes. No spec change on URML's side. Fourth Move #8 RFC.

Maytronics is an Israeli-domiciled (IL) pool-cleaning robotics vendor whose Dolphin line is the global leader in consumer pool robotics. The engagement surface is the community Home Assistant integration; Maytronics itself does not publish a developer SDK.

## Motivation

Maytronics Dolphin is the largest consumer pool-cleaning robot brand globally. URML's Move #8 home-assistance wave intentionally includes outdoor home subsystems beyond lawn care: pool cleaning is a real recurring task in homes with pools, and the Dolphin product is widely deployed.

Verified surface (2026-05-26):
- [`sh00t2kill/dolphin-robot`](https://github.com/sh00t2kill/dolphin-robot): Python, 75 stars, 6 open issues, Issues enabled, last commit 2026-05-25 (active). Home Assistant integration; reverse-engineered Dolphin WiFi API.
- License field on the repo not surfaced via the GitHub API (URML's RFC asks the maintainer to clarify; this is a verifiable open question).
- Home Assistant integration is mature; multiple Dolphin models supported.
- HQ: Yavne, Israel (Maytronics). IL-friendly geo (RFC-0003 compliance: IL is US-friendly).

URML's specific value for the Maytronics Dolphin ecosystem:
- **English-to-pool-task path for home users.** A homeowner writes "clean the pool floor and walls, then idle" in URML's natural-language layer; URML compiles to `move_to(pool_floor)` + `move_to(pool_walls)` + `wait_for(cycle_complete)` + `report(...)`; a `MaytronicsDolphinAdapter` dispatches via the WiFi API.
- **Cross-platform retargetability across home-assistance subsystems.** A URML home-cleaning program written for Dolphin (pool) retargets to Roomba (floor, [RFC-0100](0100-irobot-roomba-outreach.md)) or Husqvarna Automower (lawn, [RFC-0101](0101-husqvarna-automower-outreach.md)) by manifest swap. The substrate-neutral story spans the indoor / outdoor / aquatic home robotics continuum.
- **Substrate-niche coverage.** Pool cleaning is a niche URML's outreach has not previously touched; surfacing it explicitly via the home-runtime broadens the home-assistance audience and demonstrates URML's substrate-neutral claim across operating environments (floor / lawn / water).

## Detailed design

URML's existing artifacts that feed into a Maytronics Dolphin adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [RFC-0100](0100-irobot-roomba-outreach.md): proposes the parent `reference/home-runtime/` package. MaytronicsDolphinAdapter is the third proposed adapter in it (after RoombaAdapter and HusqvarnaAutomowerAdapter).

### Proposed `MaytronicsDolphinAdapter` shape

```
reference/home-runtime/src/home_runtime/maytronics/
├── __init__.py
├── adapter.py             # MaytronicsDolphinAdapter
├── dolphin_protocol.py    # wraps sh00t2kill/dolphin-robot WiFi-API surface
└── manifests/
    └── maytronics_dolphin_m700.yaml
```

The adapter implements URML's substrate Protocol. The transport is the Dolphin's WiFi-API surface, accessed via the `dolphin-robot` Python integration.

### Proposed URML v0.1 to Maytronics Dolphin mapping

| URML primitive | Maytronics Dolphin realisation |
|---|---|
| `move_to(region)` | A named-region command (floor / walls / waterline / steps) via the Dolphin's WiFi API. Free-coordinate `move_to(x, y)` is not natively supported. |
| `grasp(...)` / `release(...)` | Not applicable. Manifest declares `gripper: none`. |
| `measure(sensor_id)` | Water temperature, cycle progress, filter status, battery state via the WiFi API. |
| `wait_for(...)` | Polling loop on the named sensor / event (e.g. `cycle_complete`, `filter_full`, `surface_idle`). |
| `report(status)` | Append to a per-session log file. Optional MQTT publish for Home Assistant composition. |

### Proposed capability manifest

```yaml
brand: maytronics_dolphin
profile: home
mobility: tracked_aquatic   # tracks for wall climbing + floor traversal
workspace_m: aquatic_pool
mass_kg: 11.0   # approximate; pending verification per model (M700)
mobility_type: region_based   # floor / walls / waterline / steps
transport: cloud_wifi
python_package: home_runtime.maytronics
controller: dolphin_robot_via_wifi_api
sensors:
  - water_temperature
  - filter_status
  - cycle_progress
  - battery
  - surface_detection
gripper: none
provenance:
  origin: IL
  ndaa_section_889_status: not_listed
  default_policy: pass
license_alignment: community_integration_license_pending
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: extends the proposed `reference/home-runtime/` package from RFC-0100. MaytronicsDolphinAdapter is the third adapter in it. Not built in this PR.
- Conformance suite: proposed new `maytronics-integration.yml` CI workflow + `URML_MAYTRONICS_INTEGRATION` env gate. Hermetic suite first (mock WiFi-API surface), hardware-in-the-loop deferred.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.** No code in this RFC.
- **License field unset on the community integration repo.** GitHub's API did not surface a license SPDX identifier at verification time. URML's RFC asks the maintainer to clarify the license posture before any adapter code reuse.
- **Reverse-engineered WiFi API.** Maytronics has not published an official SDK; the community integration depends on continued reverse-engineering. URML's RFC documents this dependency honestly.
- **Cloud-routed WiFi protocol.** The Dolphin WiFi API routes through Maytronics' cloud (the IoT MyDolphin Plus app). URML programs depending on this adapter require network connectivity.
- **Niche subsystem.** Pool cleaning is a niche; URML's RFC justifies inclusion via the broader home-assistance continuum (floor + lawn + pool) but acknowledges this is the smallest-installed-base target in Move #8.

## Alternatives considered

1. **Skip pool cleaning in Move #8.** Rejected. URML's substrate-neutral claim benefits from explicit aquatic-subsystem coverage; the Dolphin's IL-friendly geo and active community surface make it a low-friction addition.
2. **Fold MaytronicsDolphinAdapter into the marine-runtime instead of home-runtime.** Considered briefly. Rejected; `reference/marine-runtime/` targets underwater research robotics (BlueRovAdapter against ArduSub); pool cleaning is a consumer-home context, not marine-research. The home-runtime placement is correct.
3. **Reverse-engineer a non-Maytronics pool robot instead** (e.g. Beatbot, Aiper). Rejected on RFC-0003 default-policy grounds: those alternatives are PRC-domiciled.

## Prior art

- [`sh00t2kill/dolphin-robot`](https://github.com/sh00t2kill/dolphin-robot) (Python, 75 stars, license TBC, last commit 2026-05-25).
- Home Assistant `dolphin-robot` community integration.
- Maytronics MyDolphin Plus cloud + mobile app.
- [RFC-0100 (iRobot Roomba)](0100-irobot-roomba-outreach.md): the indoor-floor sibling.
- [RFC-0101 (Husqvarna Automower)](0101-husqvarna-automower-outreach.md): the outdoor-lawn sibling.
- [RFC-0106 (Home Assistant)](0106-home-assistant-outreach.md): the orchestration hub where dolphin-robot lives.
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md): the engagement → adapter-shipment pattern URML would follow.

## Unresolved questions

For the `dolphin-robot` maintainer (sh00t2kill / community):

1. **License posture.** Could you clarify the license on the `dolphin-robot` integration? GitHub's API did not surface an SPDX identifier at verification time.
2. **Adapter home.** URML repo (`reference/home-runtime/src/home_runtime/maytronics/`), `dolphin-robot` contributed example, both?
3. **Authoritative manifest values.** Model-specific mass, dimensions, sensor inventory across the Dolphin line (M700, M600, M400, Premier, etc.).
4. **Region-based mobility encoding.** Is `region_based` the right manifest term for URML's mobility schema, or should URML extend the schema to model the Dolphin's floor / walls / waterline / steps semantics directly?
5. **Maytronics developer-relations channel.** Is there a known contact at Maytronics for a courtesy notification, or is the community surface the canonical engagement path?
6. **Home-profile co-design.** Future `spec/profiles/home/` Layer-3 vocabulary interest?
7. **Conformance lane.** Open to a URML conformance line on the `dolphin-robot` README?
8. **Anything else.**

## Implementation note

RFC-0103 ships as a single RFC document PR. No adapter code in this PR. Fourth Move #8 RFC. Ledger entry in [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml).

## Requested feedback

Items 1–8 from "Unresolved questions" above.

## How to respond

`sh00t2kill/dolphin-robot` has Issues enabled (6 open, verified 2026-05-26). URML's planned channel: open a single Issue on `sh00t2kill/dolphin-robot` labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC. Optional courtesy email to Maytronics dev relations.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Motivation grounded in verified `dolphin-robot` HA integration surface.
- [x] License-clarity gap surfaced honestly as the gating item before adapter code.
- [x] Cross-link to RFC-0100 (indoor sibling) + RFC-0101 (outdoor sibling) + RFC-0106 (Home Assistant hub).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, license-unset, reverse-engineered API, cloud-routed, niche subsystem).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added. Home-profile question deferred to a future Spec RFC.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: IL`; IL US-friendly; default policy passes.
- [x] CLAUDE.md compliance check passed.
