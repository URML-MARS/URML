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

# Warehouse Profile

**Status:** Draft (v0.1)
**Targets:** URML v0.1
**Created:** 2026-05-21

The sixth URML profile: mobile manipulators and AMRs operating in mixed-traffic warehouse aisles. Constrains and interprets the [twelve core primitives](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) for the dynamic, human-adjacent environment a warehouse aisle actually is, defines a default safety envelope that elevates `people_occupancy_zones` from optional to required, and binds compliance to the [bundled US-federal policy](../../../docs/rfcs/0004-compliance-policy.md) with warehouse-specific provenance notes (the dominant AMR vendors are NDAA-friendly; the lidar / camera supply chain is the risk surface). Specified by [RFC-0022](../../../docs/rfcs/0022-warehouse-domain-profile.md). Zero new Layer-2 primitives; the profile is normative scope plus manifest interpretation.

## Application domain

Mobile manipulators and AMRs operating in **mixed-traffic warehouse aisles**: shelf-to-conveyor picking, AGV-to-AGV handoff, fixed-cell-to-AMR transfer, multi-aisle dispatch. The defining shape of the warehouse profile is *dynamic obstacles (people, forklifts, other AGVs), declared handoff docks, no perimeter interlock, fleet-managed coordination*.

The industrial profile is the sibling: an industrial cell is enclosed and operator-trained; a warehouse aisle is open and operator-untrained. Compositions that mix the two (an AMR rolling into a fixed cell to receive a kitted tray) are explicitly supported via the program schema's multi-profile list (`profile: [warehouse, industrial]`).

## In scope

- **Mobile pick-and-place across aisles.** Canonical example: an AMR carrying a small arm picks from a shelf, transports a tote down an aisle, and places it on a conveyor station.
- **AMR-to-AMR handoff at declared docks.** One AMR places a tote at a handoff dock, a partner AMR picks it up. Coordinated via `wait_for(condition.event: partner_ready)` against declared events.
- **AMR-to-fixed-cell transfer.** AMR delivers a tote to a fixed cell's input station; the cell's industrial-profile program takes over from there.
- **Dynamic obstacle handling.** AMR pauses on `obstacle_detected` and resumes on `path_clear` (declared events). Mixed-traffic zones clamp velocity through the envelope.
- **Fleet reporting.** Status, cycle completion, and exception events are reported `to: fleet_manager`.
- **Charge-dock cycling.** AMRs return to declared charge docks during idle windows; uses `move_to(charge_dock)` and the existing `dock` primitive.

## Out of scope

- **Outdoor yard operation.** Loading-dock approaches, weather-affected motion, and GPS-frame navigation are deferred. A "yard" profile may cover this in a future RFC.
- **Multi-level rack ASRS.** Automated storage and retrieval systems with vertical lifters and high-rack interfaces use substrates URML has not adapted yet. Plausibly its own profile if the substrate need arises.
- **Autonomous forklifts.** Heavy-payload counterbalanced forklifts share aisle space with AMRs but carry different mass and stopping-distance assumptions. Their safety envelope is a strict superset of the warehouse profile's; their inclusion is a future scope decision, not v0.1.
- **Voice UI in the aisle.** `speak` and `listen` are reserved (not rejected) but no warehouse fixture exercises them in v0.1.
- **Mixed-vendor fleet orchestration spec.** The profile assumes a single fleet-management layer above the warehouse AMRs (Open-RMF, vendor-specific, or custom). The orchestration protocol itself is out of scope; URML programs receive coordination events through `wait_for` rather than encoding the fleet protocol.

## Profile-required Layer-1 manifest fields

A warehouse-profile-conformant capability manifest **must** declare:

- **`mobility`** with `drive_type` in (`differential`, `omnidirectional`, `tracked`). Manipulator-base-only is the industrial profile's signature and is rejected here; aerial drive types are rejected by the existing per-primitive checks. The warehouse profile has no objection to `tracked` AMRs in principle.
- **`mobility.max_velocity`** is interpreted as the aisle nominal max. Mixed-traffic zones MUST be capped further in the envelope (see below).
- **`declared_locations`** including aisle waypoints and handoff docks. Pose-based `move_to` is permitted but discouraged; warehouse programs almost always reference named locations.
- **`declared_events`** including `partner_ready`, `partner_unavailable`, `obstacle_detected`, `path_clear`. The partner-coordination and dynamic-obstacle events are the warehouse profile's canonical coordination surface.
- **`docking_stations`** for any conveyor station, handoff dock, or charge dock the AMR cycles through. The `services` field includes `dock` and (where applicable) profile-future `swap_tool` (deferred) and `handshake` (RFC-0017 dependent, deferred).

A warehouse-profile manifest **should** declare:

- **`manipulation`** when the AMR carries an arm. Pure transport AMRs (no arm) MAY omit it; the per-primitive checks on `pick_from` / `place_at` / `grasp` already enforce gripper presence when the program uses them.
- **`perception.sensors`** including a `distance` sensor (lidar, time-of-flight, or equivalent) for dynamic obstacle detection. Programs that wait on `obstacle_detected` implicitly require this; the per-primitive checks do not enforce it in v0.1.
- **`provenance`** per [RFC-0004](../../../docs/rfcs/0004-compliance-policy.md). Warehouse deployments inside US-federal facilities, defense industrial base, and federally-funded research labs trigger NDAA-style procurement rules; the bundled default policy enforces them statically.
- **`outputs.named_endpoints`** including `fleet_manager` and one entry per known handoff partner AGV.

A warehouse-profile manifest **must not** declare:

- **`mobility.service_ceiling`** with a non-trivial value. Warehouse aisles are ground-level. The drone profile owns aerial motion.
- **A `safety_door_event` envelope field tied to perimeter interlocks.** That is the industrial profile's pattern. Warehouse aisles have no continuous perimeter to interlock against; safety comes from `people_occupancy_zones` and dynamic-obstacle events.

## Default safety envelope

A warehouse aisle is **dynamic, human-adjacent, and continuously open**. The default envelope is people-zone-oriented rather than perimeter-oriented:

```yaml
envelope_version: "0.1"
deployment_id: <free-form>
description: <free-form>

# Numeric caps. Strictest-wins against the manifest's declared maxima.
max_velocity: 1.5                  # m/s; aisle nominal max for an AMR class.
mixed_traffic_max_velocity: 0.5    # m/s; clamps velocity inside any zone
                                   # flagged `people_possible`. REQUIRED when
                                   # any such zone exists.

# Spatial constraints.
people_occupancy_zones:            # REQUIRED for warehouse profile.
  - name: aisle_3
    polygon: [...]
    flags: [people_possible]
obstacle_stop_distance: 1.0        # m; AMR halts at this distance from a
                                   # detected dynamic obstacle.

# Behavioral defaults.
handoff_zone_pause_on_partner_absent: true   # AMR holds at handoff zone if
                                             # the declared partner has not
                                             # asserted partner_ready.
door_interlock_required: false              # Unlike industrial; warehouse
                                             # aisles have no interlock.

# RFC-0006: warehouse AMRs run under a fleet-management link. Loss policy
# is conservative but does NOT halt-all-motion in the middle of an aisle.
link_loss_policy:
  - role: fleet_link
    action: dock_at_nearest_safe
```

## Mandatory invariants

- A program that routes through a `people_possible` zone is validated against an envelope that sets `mixed_traffic_max_velocity`. Enforcement: the existing Pass-3 envelope velocity check; programs above the clamp are rejected with `envelope.velocity_exceeded`.
- A program that references a handoff (any `wait_for(condition.event: partner_ready)` step) is validated against a manifest that declares `partner_ready` in `declared_events`. Enforcement: the existing `_check_wait_for_caps` rejects undeclared events with `capability.missing_event`.
- Programs that use `place_at(target)` or `pick_from(source)` against a station name resolve the station against `manifest.docking_stations` or `manifest.declared_locations`. The per-primitive checks already enforce this; the profile spec calls out that conveyor and handoff names SHOULD be docking stations (semantic, not enforced).

## Layer-2 primitives this profile adds

**None.** Existing primitives cover the warehouse domain: `move_to` for aisle navigation, `pick_from` / `place_at` for shelf and conveyor work, `wait_for` for coordination, `dock` for charge cycling, `report` for fleet status. Per RFC-0022, primitives like `handoff_to(partner_id)` and `load_conveyor` / `unload_conveyor` are explicitly rejected as primitives because they compose from existing primitives and no current substrate exposes them as atomic.

If a substrate emerges that exposes atomic multi-agent handoff or conveyor handshake, a follow-up RFC may promote a primitive. RFC-0017 (`set_output`, Draft) is the more likely route for conveyor handshake when it lands.

## Layer-2 primitives this profile constrains

### `move_to`

- **Named locations are the strong norm.** Aisle waypoints and handoff docks are declared by name; pose-based `move_to` is permitted but discouraged.
- **Velocity ceiling is the envelope's `max_velocity` outside people zones and `mixed_traffic_max_velocity` inside them.** Strictest-wins applies.

### `pick_from` / `place_at`

- **Source / target SHOULD be a docking station name** when the operation is a conveyor handshake or handoff. The profile reserves the names `conveyor_*`, `handoff_in_*`, `handoff_out_*` as conventional patterns; they are not enforced in v0.1 but are documented for tool authors.
- **`force` defaults to `gentle`** in warehouse use (lower than industrial's `firm`). Warehouse totes and parcels are typically handled less forcefully than rigid widgets.

### `wait_for`

- **`partner_ready` is the canonical partner-coordination event.**
- **`obstacle_detected` and `path_clear` are the canonical dynamic-obstacle events.**
- Programs lacking a `wait_for(obstacle_detected)` handler in routes through a `people_possible` zone are accepted in v0.1 (the AMR's substrate handles the obstacle stop reactively) but a future tightening RFC may require explicit coordination.

### `dock`

- **Charge docks and handoff docks are both expressed through `dock`.** The `service` argument disambiguates (`dock(at: charge_dock_1, service: park)` vs `dock(at: handoff_in_2, service: receive)`). RFC-0013's `swap_tool` mechanism is industrial-only and not used in warehouse v0.1.

### `report`

- **`to: fleet_manager`** is the canonical warehouse output endpoint, declared in `manifest.outputs.named_endpoints`. Per-cycle status and exception events flow through it.

### `take_off` / `land` / `return_to_home`

- **Rejected** by the existing `_check_aerial_caps` (drive type not aerial). Warehouse is ground-floor.

### `speak` / `listen`

- **Not used in v0.1 warehouse fixtures.** Reserved for future voice-UI-in-the-aisle scope; not rejected.

## Layer-4 (LLM bridge) integration

The warehouse profile is well-suited to natural-language line-reconfiguration scenarios similar to industrial's, with a fleet-coordination flavor:

- The bridge ships per-profile few-shots; a `warehouse_few_shots` set lands alongside this profile (tracked in RFC-0022's implementation note as a v0.1 follow-up if not in the initial PR).
- Programs that reference fleet coordination (the *"wait for AGV-7 to finish its drop, then take over"* pattern) lean on the `partner_ready` event and `wait_for` composition rather than a new primitive.
- `report(to: fleet_manager)` is the canonical output channel; the bridge translates the `facts` dict into JSON the fleet manager consumes.

## Compliance policy alignment

US warehouse deployments routinely involve federal procurement (DLA, DoD logistics, USPS automation, federally-funded labs). The bundled default policy ([RFC-0004](../../../docs/rfcs/0004-compliance-policy.md)) applies the same way it does to home, drone, and industrial profiles, with warehouse-specific considerations:

- **AMR base controllers**: the dominant US-friendly vendors (Locus, Symbotic, Fetch / Zebra, Rapid Robotics, Clearpath) typically pass the default policy. Chinese-origin AMR controllers reject under `policy.country_denied`.
- **LIDAR / depth sensing**: the highest-risk component for procurement rules. Hesai (FCC Covered List) is rejected by `policy.vendor_denied` per the existing `mobile/hesai_component_denied` conformance fixture. Velodyne (US), Ouster (US), Sick (DE), Hokuyo (JP) typically pass.
- **End-of-arm tooling**: usually non-critical for procurement rules. Robotiq (CA), Schunk (DE), PIAB (SE), Soft Robotics (US) all typically pass.
- **Vision systems**: Intel RealSense (US), Cognex (US), Keyence (JP), Zivid (NO) typically pass.
- **Fleet management software**: typically out of scope of URML's compliance pass; tracked as a procurement concern at the system-acquisition level.

Deployers outside the US should override the default with their own policy via `urml validate --policy <file.yaml>`.

## Conformance points

The conformance suite at [`/conformance/fixtures/warehouse/`](../../../conformance/fixtures/warehouse/) ships these fixtures:

| Fixture | What it tests |
|---|---|
| `01_pick_from_shelf_place_on_conveyor_positive.yaml` | Canonical warehouse cycle. Mobile manipulator picks a tote from a shelf, places it on a conveyor station. Existing primitives end to end. |
| `02_amr_aisle_dynamic_obstacle_positive.yaml` | AMR navigates an aisle, pauses on `obstacle_detected`, resumes on `path_clear`. Exercises the dynamic-obstacle event convention. |
| `03_people_occupancy_speed_reduction_positive.yaml` | Program enters a `people_possible` zone; the envelope's `mixed_traffic_max_velocity` is the binding cap. Documents the envelope clamp. |
| `04_envelope_speed_violation_rejected.yaml` | Program declares a velocity above the mixed-zone limit. Rejected by the existing envelope velocity check. |
| `05_handoff_partner_event_undeclared_rejected.yaml` | Program uses `wait_for(condition.event: partner_ready)` against a manifest missing the event. Rejected with `capability.missing_event`. |
| `06_handoff_failure_recovery_positive.yaml` | Multi-step program with a `branch` that picks a fallback `place_at(reserve_station)` when `partner_unavailable` fires. Exercises Layer-3 composition under warehouse semantics. |
| `07_multi_agv_handoff_zone_positive.yaml` | Coordinated handoff dock cycle expressed as a `wait_for(partner_ready)` then `place_at(handoff_dock)`. Exercises the coordination convention without new primitives. |
| `08_compliant_parts_bom_positive.yaml` | A warehouse manifest with a Hesai-free, US-aligned BOM (Locus-class AMR, Robotiq gripper, Intel RealSense, Ouster lidar). All five validator passes accept. |

The runnable [`examples/warehouse/pick_to_conveyor.urml.yaml`](../../../examples/warehouse/) is the canonical warehouse cycle.

## Deferred

- **Mixed-traffic schema field.** `mixed_traffic_max_velocity` is a free-form envelope key the warehouse profile interprets; promoting it to a typed `envelope.py` field is a follow-up envelope-schema RFC.
- **Per-station accepted-payload vocabulary.** Industrial's `docking_stations[].accepted_tools` is still deferred; the parallel `accepted_payloads` for warehouse handoff and conveyor stations is also deferred.
- **`fleet_link` requirement.** Industrial requires a `command_link` in `connectivity`; warehouse plausibly requires a `fleet_link`. The profile recommends but does not require. A follow-up may tighten.
- **Conveyor handshake signals.** Belong to [RFC-0017](../../../docs/rfcs/0017-digital-io-actuation.md) (`set_output`, Draft). The warehouse profile cites RFC-0017 as the eventual mechanism for raise-handshake-line / wait-for-acknowledge.
- **Multi-vendor fleet orchestration mapping.** The warehouse profile assumes the orchestration layer above URML is opaque; how Open-RMF or vendor-specific protocols emit `partner_ready` events into a URML program is a substrate concern, not a profile concern.

## Related documents

- [RFC-0022](../../../docs/rfcs/0022-warehouse-domain-profile.md) — this profile's specifying RFC.
- [`/spec/profiles/industrial/`](../industrial/) — the sibling profile; warehouse and industrial compose for mixed cell-and-aisle deployments.
- [`/spec/layer-1-hal/`](../../layer-1-hal/) — capability manifest reference.
- [`/spec/layer-2-primitives/`](../../layer-2-primitives/) — the core twelve.
- [`/docs/rfcs/0002-initial-primitive-vocabulary.md`](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) — primitive vocabulary, with §Profile-extensibility authorizing per-profile primitive additions (warehouse adds none).
- [`/docs/rfcs/0003-us-alignment.md`](../../../docs/rfcs/0003-us-alignment.md) — strategic alignment.
- [`/docs/rfcs/0004-compliance-policy.md`](../../../docs/rfcs/0004-compliance-policy.md) — compliance policy mechanism.
- [`/docs/rfcs/0006-connectivity-and-link-loss.md`](../../../docs/rfcs/0006-connectivity-and-link-loss.md) — link-loss policy framework, used here for the `fleet_link` recommendation.
- [`/docs/rfcs/0017-digital-io-actuation.md`](../../../docs/rfcs/0017-digital-io-actuation.md) — Draft; the future home of conveyor handshake.
- [`/spec/profiles/home/`](../home/), [`/spec/profiles/drone/`](../drone/), [`/spec/profiles/educational/`](../educational/), [`/spec/profiles/research/`](../research/) — sibling profile specs for comparison.
- [`MANIFESTO.md`](../../../MANIFESTO.md) — warehouse pickers are referenced as one of the robot families the project intends to serve.
