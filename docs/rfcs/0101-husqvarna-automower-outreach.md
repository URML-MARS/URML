---
rfc: 0101
title: Husqvarna Automower integration, request for comment from aioautomower maintainers
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

# RFC-0101: Husqvarna Automower integration, request for comment from aioautomower maintainers

## Summary

URML does not yet ship a Husqvarna Automower integration. This RFC proposes a `HusqvarnaAutomowerAdapter` under the new [`reference/home-runtime/`](../../reference/home-runtime/) package (proposed by [RFC-0100](0100-irobot-roomba-outreach.md)) targeting Husqvarna's **official Automower Connect API** at `developer.husqvarnagroup.cloud` (OpenAPI 3.0) plus the [`Thomas55555/aioautomower`](https://github.com/Thomas55555/aioautomower) (MIT, Python, 11 stars, 2 open issues, last commit 2026-05-25) community Python wrapper that powers the Home Assistant Husqvarna Automower integration. The adapter routes URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) onto Husqvarna's outdoor-robot surface without proposing upstream changes. No spec change on URML's side. Second Move #8 RFC.

This is the cleanest vendor-API engagement surface in the Move #8 wave: Husqvarna operates a first-class developer portal, publishes an OpenAPI 3.0 specification, and the community Python wrapper carries a permissive license.

## Motivation

Husqvarna Automower is the largest installed base of consumer outdoor home robotics globally (Sweden-domiciled, EU default-policy pass). URML's natural-language layer maps cleanly to Automower's zone + scheduling surface: a homeowner writes "mow the back lawn between 10 AM and 2 PM, but skip if it rains" in URML; URML compiles to `move_to(back_lawn)` + `wait_for(time, 10:00)` + `wait_for(weather, not_raining)` + `report(mowing_complete)`; a `HusqvarnaAutomowerAdapter` dispatches the primitives onto the Automower via the Automower Connect API.

Verified surface (2026-05-26):
- **Official Automower Connect API** at `developer.husqvarnagroup.cloud`, OpenAPI 3.0, OAuth 2.0 authentication. Documented mission planning, zone scheduling, status streaming, geofence support.
- [`Thomas55555/aioautomower`](https://github.com/Thomas55555/aioautomower): MIT, 11 stars, 2 open issues, Issues enabled, last commit 2026-05-25 (active). Python async wrapper used by Home Assistant.
- Home Assistant `husqvarna_automower` integration (first-class, in `home-assistant/core`).
- HQ: Huskvarna, Sweden.

URML's specific value for the Husqvarna Automower ecosystem:
- **First-class vendor API + open Python wrapper.** No reverse-engineering risk; Husqvarna's developer portal commits to the API surface. URML's adapter sits cleanly on top of `aioautomower`'s async Python without re-implementing the OAuth or REST layer.
- **English-to-robot-task path for outdoor home robots.** "Mow the front lawn before noon and report when complete" is the audience-native phrasing URML's natural-language layer ([RFC-0021](0021-on-device-llm-bridge.md)) targets directly.
- **Cross-platform retargetability.** A URML outdoor-cleaning program written for Husqvarna Automower retargets to a hypothetical future open-source mower or to indoor cleaning ([RFC-0100](0100-irobot-roomba-outreach.md) Roomba) by manifest swap. The substrate-neutral story is exactly URML's value proposition.
- **Home Assistant composition.** URML primitives compile into Home Assistant automations (see [RFC-0106](0106-home-assistant-outreach.md)); `aioautomower` is the canonical Husqvarna substrate for that composition.

## Detailed design

URML's existing artifacts that feed into a Husqvarna Automower adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [RFC-0100](0100-irobot-roomba-outreach.md): proposes the parent `reference/home-runtime/` package. HusqvarnaAutomowerAdapter is the second adapter in it after `RoombaAdapter`.

### Proposed `HusqvarnaAutomowerAdapter` shape

```
reference/home-runtime/src/home_runtime/husqvarna/
├── __init__.py
├── adapter.py                # HusqvarnaAutomowerAdapter
├── automower_protocol.py     # wraps aioautomower / Automower Connect API
└── manifests/
    └── husqvarna_automower_315x.yaml
```

The adapter implements URML's substrate Protocol. The transport is the Automower Connect API (OAuth 2.0 + REST), accessed via `aioautomower`'s async Python wrapper.

### Proposed URML v0.1 to Husqvarna Automower mapping

| URML primitive | Husqvarna Automower realisation |
|---|---|
| `move_to(zone)` | A mission command to a named geofence zone via the Automower Connect API. Free-coordinate `move_to(x, y)` is not natively supported; the manifest declares `mobility_type: zone_based`. |
| `grasp(...)` / `release(...)` | Not applicable. Manifest declares `gripper: none`. |
| `measure(sensor_id)` | Battery state, mowing time, position, error code via the API. |
| `wait_for(...)` | Polling loop on the named sensor / event (e.g. `mission_complete`, `docked`, `error`, time-of-day, weather predicate). |
| `report(status)` | Append to a per-session log file. Optional MQTT publish for Home Assistant composition. |

### Proposed capability manifest

```yaml
brand: husqvarna_automower
profile: home
mobility: wheeled_differential
workspace_m: outdoor_lawn
mass_kg: 13.0   # approximate; pending verification per model (315X)
mobility_type: zone_based   # geofence zones, not arbitrary coordinates
transport: cloud_oauth2
python_package: home_runtime.husqvarna
controller: aioautomower_via_automower_connect_api
sensors:
  - battery
  - lift
  - tilt
  - position_gps
  - mowing_time
  - error_code
gripper: none
provenance:
  origin: SE
  ndaa_section_889_status: not_listed
  default_policy: pass
license_alignment: mit_community_wrapper
api_terms: husqvarna_developer_portal_tos
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: extends the proposed `reference/home-runtime/` package from RFC-0100. HusqvarnaAutomowerAdapter is the second adapter in it. Not built in this PR.
- Conformance suite: proposed new `husqvarna-integration.yml` CI workflow + `URML_HUSQVARNA_INTEGRATION` env gate. Hermetic suite first (mock Automower Connect surface), hardware-in-the-loop deferred.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.** No code in this RFC.
- **Cloud-only API.** Automower Connect is cloud-based (OAuth 2.0 + REST), not LAN-local. URML programs depending on this adapter require network connectivity. URML's RFC documents this constraint; future on-device Automower variants could compose with URML's offline-execution posture.
- **OAuth 2.0 onboarding step.** First-run setup requires Husqvarna developer-portal credentials; URML's RFC documents this in the adapter onboarding notes.
- **Zone-based mobility.** Automower navigates to named geofence zones, not arbitrary coordinates. URML's manifest declares `mobility_type: zone_based` to surface this constraint to the static verifier (same pattern as RFC-0100's `region_based` for Roomba).
- **API rate limits.** The Husqvarna developer portal imposes per-app rate limits; URML's adapter must batch reads, not poll aggressively.

## Alternatives considered

1. **Reverse-engineer the Automower app's private endpoints instead of using Automower Connect.** Rejected. Husqvarna operates a documented developer portal with stable terms-of-service; reverse-engineering a moving target is brittle.
2. **Fold HusqvarnaAutomowerAdapter into a generic mower-runtime covering Worx Landroid + Ambrogio.** Rejected. Worx Landroid is held back for a possible Move #9 (the wave-scope discipline avoids over-broad runtimes early). Each vendor's API has different shapes; multi-target abstraction follows engagement, not precedes it.
3. **Wait for Husqvarna to publish an MQTT API before engaging.** Rejected. The current OpenAPI 3.0 + OAuth 2.0 surface is sufficient and stable; URML's engagement does not block on hypothetical future protocols.

## Prior art

- [`Thomas55555/aioautomower`](https://github.com/Thomas55555/aioautomower) (MIT, 11 stars, last commit 2026-05-25).
- Husqvarna Automower Connect API (OpenAPI 3.0 at `developer.husqvarnagroup.cloud`).
- Home Assistant `husqvarna_automower` integration (Apache-2.0, in `home-assistant/core`).
- [RFC-0100 (iRobot Roomba)](0100-irobot-roomba-outreach.md): the indoor home-cleaning consumer-vendor sibling; both are Move #8 Tier A targets with community-Python-wrapper engagement surfaces.
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md): the agricultural-cartesian-gantry precedent; consumer-vendor template.
- [RFC-0106 (Home Assistant)](0106-home-assistant-outreach.md): the orchestration-hub engagement; HusqvarnaAutomowerAdapter is one of the targets that lives natively in Home Assistant integrations.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles.

## Unresolved questions

For the `aioautomower` maintainer (Thomas55555 / community):

1. **Adapter home.** URML repo (`reference/home-runtime/src/home_runtime/husqvarna/`), `aioautomower` contributed example, both?
2. **Authoritative manifest values.** Model-specific mass, dimensions, sensor inventory across the Automower line (315X, 430X, 535 AWD, etc.). URML's manifest should target a primary model.
3. **Zone-based mobility encoding.** Is `zone_based` the right manifest term, or should URML extend the schema to model Automower's geofence semantics directly?
4. **Husqvarna developer-relations channel.** Is there a known contact at Husqvarna to forward this RFC to as a courtesy, or is engagement with the `aioautomower` maintainer + Home Assistant community the canonical path?
5. **Home-profile co-design.** Future `spec/profiles/home/` Layer-3 vocabulary (mow / vacuum / clean / scout) interest?
6. **Conformance lane.** Open to a URML conformance line on the `aioautomower` README?
7. **Anything else.**

## Implementation note

RFC-0101 ships as a single RFC document PR. No adapter code in this PR. Second Move #8 RFC. Ledger entry in [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`Thomas55555/aioautomower` has Issues enabled (2 open, verified 2026-05-26). URML's planned channel: open a single Issue on `Thomas55555/aioautomower` labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC. Optional courtesy email to Husqvarna developer relations via the developer portal contact form.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Motivation grounded in verified `aioautomower` + Automower Connect surface.
- [x] First-class vendor API + community Python wrapper acknowledged as the cleanest engagement surface in Move #8.
- [x] Cross-link to RFC-0100 (indoor sibling), RFC-0067 (consumer-vendor template), RFC-0106 (Home Assistant orchestration hub).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, cloud-only, OAuth setup, zone-based mobility, rate limits).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added. Home-profile question deferred to a future Spec RFC.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: SE`; EU US-friendly; default policy passes.
- [x] CLAUDE.md compliance check passed.
