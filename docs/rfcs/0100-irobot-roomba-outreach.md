---
rfc: 0100
title: iRobot / Roomba integration, request for comment from dorita980 + ha-rest980-roomba maintainers
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

# RFC-0100: iRobot / Roomba integration, request for comment from dorita980 + ha-rest980-roomba maintainers

## Summary

URML does not yet ship an iRobot integration. This RFC proposes a `RoombaAdapter` under a new [`reference/home-runtime/`](../../reference/home-runtime/) package targeting the [`koalazak/dorita980`](https://github.com/koalazak/dorita980) (MIT, JavaScript / Node.js, 1.1k stars, 12 open issues, last commit 2026-05-25) community LAN-control SDK plus the [`jeremywillans/ha-rest980-roomba`](https://github.com/jeremywillans/ha-rest980-roomba) Home Assistant wrapper. The adapter routes URML Layer-2 primitives (`move_to`, `measure`, `wait_for`, `report`) onto Roomba's LAN-control surface without proposing upstream changes. No spec change on URML's side. First Move #8 RFC; opens the home-assistance wave.

iRobot itself does not operate a public developer GitHub org or publish an official Roomba REST API. The community surface (`dorita980` + `rest980` + Home Assistant `roomba` integration) is the canonical engagement channel for substrate-neutral integrations.

## Motivation

iRobot Roomba is the highest-share consumer home-robot brand globally (US-domiciled, NDAA-compatible, default-policy pass). URML's natural-language layer maps cleanly to Roomba's local LAN-control surface: a homeowner writes "vacuum the kitchen, then dock" in URML; URML compiles to `move_to(kitchen)` + `report(status)` + `wait_for(dock_complete)`; a `RoombaAdapter` dispatches the primitives onto the local Roomba via `dorita980`'s WebSocket / TLS surface.

Verified surface (2026-05-26):
- [`koalazak/dorita980`](https://github.com/koalazak/dorita980): MIT, 1.1k stars, 12 open issues, Issues enabled, last commit 2026-05-25 (active). Node.js library; LAN-control authentication documented.
- [`jeremywillans/ha-rest980-roomba`](https://github.com/jeremywillans/ha-rest980-roomba): companion REST wrapper for Home Assistant integration.
- Home Assistant `roomba` integration is first-class (the home-assistance ecosystem treats Roomba as a baseline target).
- No iRobot-operated public GitHub org or official REST API; engagement surface is the community SDK.
- HQ: Bedford, MA, USA.

URML's specific value for the Roomba ecosystem:
- **English-to-robot-task path for home users.** The natural-language layer + URML primitive vocabulary is a pedagogical ladder above raw REST / WebSocket calls; a homeowner authoring "vacuum the kitchen after dinner" benefits from URML compiling that into validated primitives plus Roomba dispatch.
- **Cross-platform retargetability.** A URML home-cleaning program written for Roomba retargets to a future open-source vacuum (or to Husqvarna Automower for outdoor cleaning, [RFC-0101](0101-husqvarna-automower-outreach.md)) by manifest swap. The substrate-neutral story is exactly URML's value proposition.
- **Home Assistant composition.** URML primitives compile into Home Assistant automations and scripts (see [RFC-0106](0106-home-assistant-outreach.md) for the orchestration-hub engagement); Roomba is the canonical test target for that composition.

## Detailed design

URML's existing artifacts that feed into a Roomba adapter:

- [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md): the Layer-2 primitives.
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles applicable to home-robot use.
- A new `reference/home-runtime/` package (proposed by this RFC, will be the parent runtime for RoombaAdapter, HusqvarnaAutomowerAdapter, MaytronicsDolphinAdapter, etc.).

### Proposed `RoombaAdapter` shape

```
reference/home-runtime/src/home_runtime/irobot/
├── __init__.py
├── adapter.py             # RoombaAdapter
├── roomba_protocol.py     # wraps dorita980 / rest980 LAN-control surface
└── manifests/
    └── irobot_roomba_j7.yaml
```

The adapter implements URML's substrate Protocol. The transport is `dorita980`'s WebSocket+TLS authentication to the on-network Roomba, with the option of `rest980` proxying for REST consumers.

### Proposed URML v0.1 to Roomba mapping

| URML primitive | Roomba realisation |
|---|---|
| `move_to(pose)` | Dispatched as a room / region command via Roomba's mapping (Spaces). Free-coordinate `move_to(x, y)` is not natively supported; the manifest declares region-based mobility. |
| `grasp(...)` / `release(...)` | Not applicable on the vacuum platform. Manifest declares `gripper: none`. |
| `measure(sensor_id)` | Battery state, dirt-bin status, position estimate, last-clean-time read via the LAN-control API. |
| `wait_for(...)` | Polling loop on the named sensor / event (e.g. `cleaning_complete`, `docked`, `error`). |
| `report(status)` | Append to a per-session log file. Optional MQTT publish for Home Assistant composition (mirrors the [RFC-0067 FarmBot](0067-farmbot-outreach.md) pattern). |

### Proposed capability manifest

```yaml
brand: irobot_roomba
profile: home
mobility: wheeled_differential
workspace_m: indoor_floor
mass_kg: 3.4   # approximate; pending verification per model
mobility_type: region_based   # cannot navigate to free coordinates; navigates to mapped rooms/regions
transport: lan_local
python_package: home_runtime.irobot
controller: dorita980_via_rest980
sensors:
  - bumper
  - cliff
  - dirt_bin_level
  - battery
  - position_estimate
gripper: none
provenance:
  origin: US
  ndaa_section_889_status: not_listed
  default_policy: pass
license_alignment: mit_community_surface
```

### Spec / validator / reference-runtime / conformance changes

- Spec / validator: none.
- Reference runtime: proposed new `reference/home-runtime/` package; RoombaAdapter is the first adapter in it. Not built in this PR.
- Conformance suite: proposed new `irobot-integration.yml` CI workflow + `URML_IROBOT_INTEGRATION` env gate. Hermetic suite first (mock LAN-control surface), hardware-in-the-loop deferred.

## Backward compatibility

Pre-v1.0. Purely additive when implemented. Zero URML code in this RFC.

## Drawbacks

- **Proposal-only.** No code in this RFC.
- **No iRobot-operated public API.** iRobot has not published a developer SDK. URML's adapter targets the community surface (`dorita980`, `rest980`), which depends on continued maintainer attention. URML's RFC acknowledges this dependency honestly.
- **Region-based mobility.** Roomba navigates to mapped rooms / regions, not arbitrary `move_to(x, y)` coordinates. URML's manifest declares `mobility_type: region_based` to surface this in the static verifier.
- **LAN-control authentication is iRobot-specific.** The auth flow (BLID + password retrieval from the iRobot cloud at pairing time) is a one-time setup step; URML's RFC documents this in the adapter onboarding notes.
- **iRobot acquisition history.** Amazon's acquisition of iRobot was terminated in January 2024 after EU regulatory opposition; iRobot remains independent but has been through significant strategic turbulence. URML's RFC posture is that the community surface is durable regardless of corporate ownership.

## Alternatives considered

1. **Ship a `RoombaAdapter` directly against an undocumented private iRobot cloud API.** Rejected. The LAN-control community surface is the documented and audited path; private-cloud reverse-engineering is brittle and non-portable.
2. **Wait for an official iRobot SDK before engaging.** Rejected. The community surface has been stable for years; URML's outreach is to the community maintainers (koalazak, jeremywillans) plus optional courtesy notification to iRobot developer relations.
3. **Fold RoombaAdapter into a generic vacuum-runtime that covers Roborock + Ecovacs.** Rejected on default-policy grounds: Roborock and Ecovacs are PRC-domiciled and out of URML's US-friendly default scope per [RFC-0003](0003-us-alignment.md).

## Prior art

- [`koalazak/dorita980`](https://github.com/koalazak/dorita980) (MIT, 1.1k stars).
- [`jeremywillans/ha-rest980-roomba`](https://github.com/jeremywillans/ha-rest980-roomba).
- Home Assistant `roomba` integration (Apache-2.0, in `home-assistant/core`).
- [RFC-0067 (FarmBot)](0067-farmbot-outreach.md): the agricultural Cartesian-gantry consumer precedent in URML's outreach landscape; same engagement pattern (community Apache/MIT surface for a consumer product without a vendor-operated developer API).
- [RFC-0073 (Robotical Marty)](0073-robotical-marty-outreach.md): the engagement → adapter shipment precedent (Move #5 Tier A vendor template).
- [RFC-0011](0011-educational-profile.md), [RFC-0012](0012-research-profile.md): URML profiles.

## Unresolved questions

For the `dorita980` / `rest980` / Home Assistant `roomba` maintainers (Pablo / Jeremy / community):

1. **Adapter home.** URML repo (`reference/home-runtime/src/home_runtime/irobot/`), `dorita980` contributed example, both?
2. **Authoritative manifest values.** Roomba model-specific mass, dimensions, sensor inventory, mobility model (J7 vs J9 vs i7 etc.). URML's manifest should reflect a primary target model.
3. **Region-based mobility encoding.** Is `region_based` the right manifest term for URML's mobility schema, or should URML extend the schema to model Roomba's "Spaces" semantics directly?
4. **Home-profile co-design.** RFC-0106 (Home Assistant) raises the question of a future `spec/profiles/home/` Layer-3 vocabulary (clean / vacuum / mop / scout / monitor). Interest in coordinating?
5. **Conformance lane.** Open to a URML conformance line on the `dorita980` README?
6. **iRobot developer-relations channel.** Is there a known contact at iRobot to forward this RFC to as a courtesy, or is engagement with the maintainer community the canonical path?
7. **Anything else.**

## Implementation note

RFC-0100 ships as a single RFC document PR. No adapter code in this PR. First Move #8 RFC; opens the home-assistance wave. Ledger entry in [`examples/lighthouses/outreach-move8.yaml`](../../examples/lighthouses/outreach-move8.yaml).

## Requested feedback

Items 1–7 from "Unresolved questions" above.

## How to respond

`koalazak/dorita980` has Issues enabled (12 open, verified 2026-05-26). URML's planned channel: open a single Issue on `koalazak/dorita980` labelled with the closest `enhancement` or `question` equivalent, pointing to this RFC. Optional cross-thread on `jeremywillans/ha-rest980-roomba` if maintainers prefer.

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Motivation grounded in verified `dorita980` / `rest980` / Home Assistant surface.
- [x] Community-surface-versus-no-vendor-API gap surfaced honestly.
- [x] Cross-link to RFC-0067 (consumer-vendor template), RFC-0073 (engagement-to-adapter precedent), RFC-0106 (Home Assistant orchestration hub), RFC-0101 (outdoor home robot sibling).
- [x] At least one alternative considered (three).
- [x] Drawbacks real (proposal-only, no vendor API, region-based mobility, LAN-auth setup, acquisition turbulence).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added. Home-profile question deferred to a future Spec RFC.
- [x] Implementation note explicit.
- [x] Surface verified 2026-05-26.
- [x] Provenance `origin: US`; default policy passes.
- [x] CLAUDE.md compliance check passed.
