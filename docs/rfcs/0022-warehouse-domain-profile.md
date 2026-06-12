---
rfc: 0022
title: Warehouse domain profile
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-21
updated: 2026-06-12
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

# RFC-0022: Warehouse domain profile

## Summary

Specify a sixth URML domain profile: **warehouse**. The profile covers mobile manipulators and AMRs operating in mixed-traffic warehouse aisles, with multi-agent handoff at declared docks, dynamic-obstacle pause behavior, and a default safety envelope that elevates `people_occupancy_zones` from optional to required. This RFC ships the profile spec, a default safety envelope, eight conformance fixtures, a warehouse manifest fixture, an `urml init` template, and one runnable example.

**Zero new Layer-2 primitives.** Existing primitives (`pick_from`, `place_at`, `move_to`, `wait_for`, `report`, plus the rest of the core twelve) already cover warehouse motion and manipulation. The profile is a normative scope boundary plus a manifest-interpretation set, not a new vocabulary.

**Zero new manifest schema fields.** Existing optional fields (`declared_locations`, `docking_stations`, `outputs`, `mobility.max_velocity`, `perception.sensors`, the envelope's `people_occupancy_zones`) are reused with profile-specific MUST / SHOULD / MUST NOT prose constraints.

**Zero validator code changes.** Per `validator.py:131-132`, profile names are currently informational; profile-level constraints are enforced indirectly through per-primitive checks, schema requirements, and the envelope pass. Since the warehouse profile adds no new primitive, no per-primitive helper is needed. The conformance fixtures and the spec text carry the load.

## Motivation

The industrial profile (RFC-0013) at `spec/profiles/industrial/README.md:41` explicitly calls out warehouse as future scope: *"Mixed-traffic warehouse operation is plausibly its own profile."* That stub has been carried since 2026-05-13. The work it gestures at is real and underspecified: industrial and warehouse are both pick-and-place but their safety envelopes, mobility assumptions, and handoff models differ. Stuffing both into one profile would force the industrial profile to weaken its safety-perimeter assumptions or force warehouse deployments to declare a `safety_door_closed` interlock they do not have.

The hardware ecosystem also points here. URML already ships `mobile-runtime` (Husky / Jackal) and `industrial-arm-runtime` (16 brand adapters) and a `CompositeAdapter` pattern that pairs them; the canonical warehouse robot is exactly that pairing (an AMR base carrying an industrial arm, navigating aisles between fixed cells and conveyor handoffs). The substrate exists. The runtime adapters exist. The primitives exist. The profile constraint set is what is missing.

Federally, US warehouse logistics is a large, growing, NDAA-friendly market (Locus, Symbotic, Fetch / Zebra, Rapid Robotics). The bundled US-federal default policy already accepts the dominant vendors; the warehouse profile gives those vendors a canonical URML target.

## Detailed design

### Profile name and directory

`warehouse`, following the single-word convention of existing profiles (`home`, `drone`, `industrial`, `educational`, `research`). The profile is referenced in URML programs as `profile: warehouse`.

### Spec changes

- New file `spec/profiles/warehouse/README.md` (~200 lines, mirrors `spec/profiles/industrial/README.md` structure): application domain, in/out-of-scope, profile-required and profile-constrained manifest fields, default safety envelope, Layer-2 primitive constraints (no new primitives, only constraints on existing ones), conformance points, deferred items, related documents.
- `spec/profiles/industrial/README.md:41` is updated. The sentence *"Mixed-traffic warehouse operation is plausibly its own profile."* is replaced with a link to `../warehouse/README.md`.

### Scope boundary against industrial

| Aspect | Industrial | Warehouse |
|---|---|---|
| Operating envelope | Enclosed cell, safety perimeter, trained operators | Mixed-traffic aisles, dynamic obstacles, untrained operators may be present |
| Mobility | Fixed-base manipulator + optional rail | Mobile AMR base, optionally carrying an arm; multi-agent coordination |
| Required envelope field | `safety_door_event` interlock | `people_occupancy_zones` (required) and `mixed_traffic_max_velocity` (required if any zone is `people_possible`) |
| Handoff model | Operator places work into the cell | AGV-to-AGV or AGV-to-fixed-cell handoff at declared docking stations |
| Default `max_velocity` interpretation | Tool-center-point speed | AMR aisle speed; mixed-traffic zones require a lower envelope override |
| Canonical link role | Supervisory PLC link, halt-on-loss | Fleet-management link, partner-coordination link |

### Manifest-field interpretation (no schema changes)

The warehouse profile reuses existing optional manifest fields with profile-specific constraints:

- `declared_locations`: includes aisle waypoints, handoff zones, and conveyor stations. Warehouse-profile programs SHOULD use named locations rather than raw poses.
- `docking_stations`: includes conveyor stations, charge stations, and AMR-to-fixed-cell handoff docks. The `accepted_tools` field that RFC-0013 deferred remains deferred; warehouse fixtures do not depend on it.
- `mobility.drive_type`: typically `differential` or `omnidirectional`; never `manipulator_base`-only (that is the industrial profile's signature). A warehouse cell with a fixed arm composes a warehouse-profile AMR manifest with an industrial-profile arm manifest through the existing `CompositeAdapter` pattern.
- `outputs.named_endpoints`: typically includes `fleet_manager` (the supervisory dispatcher) and a partner-AGV identifier per known handoff partner.
- `declared_events`: typically includes `partner_ready`, `partner_unavailable`, `obstacle_detected`, `path_clear`, `dock_acquired`. Programs that reference a handoff MUST declare the partner-AGV identifier in `outputs.named_endpoints` and the `partner_ready` event in `declared_events`.

### Default safety envelope

A warehouse aisle operates with dynamic obstacles (people, forklifts, other AGVs). The default envelope is people-zone-oriented rather than perimeter-oriented:

```yaml
envelope_version: "0.1"
deployment_id: <free-form>
description: <free-form>

# Numeric caps. Strictest-wins against the manifest's declared maxima.
max_velocity: 1.5                  # m/s; aisle nominal max for an AMR class.
mixed_traffic_max_velocity: 0.5    # m/s; clamps velocity while inside any
                                   # zone flagged `people_possible`. REQUIRED
                                   # when any zone has that flag.

# Spatial constraints.
people_occupancy_zones:            # REQUIRED for warehouse profile.
  - name: aisle_3
    polygon: [...]
    flags: [people_possible]
obstacle_stop_distance: 1.0        # m; AMR halts at this distance from a
                                   # detected dynamic obstacle.

# Behavioral defaults.
handoff_zone_pause_on_partner_absent: true   # AMR holds at handoff zone if
                                             # the declared partner is not
                                             # ready; pairs with the
                                             # partner_ready event.
door_interlock_required: false              # Unlike industrial; warehouse
                                             # aisles have no interlock.

# RFC-0006: warehouse AMRs run under a fleet-management link. Loss policy is
# conservative but does NOT halt all motion (an AMR on an aisle should reach
# a safe waiting position, not stop in the middle).
link_loss_policy:
  - role: fleet_link
    action: dock_at_nearest_safe
```

### Mandatory invariants

- A program that routes through a `people_possible` zone MUST be validated against an envelope that sets `mixed_traffic_max_velocity`. Enforcement: the existing envelope velocity check (Pass 3) compares the program's declared or default velocity against the strictest applicable cap; the warehouse profile spec makes the requirement normative.
- A program that references a handoff (a `wait_for(condition.event: partner_ready)` step followed by a `place_at(handoff_dock)` or `pick_from(handoff_dock)` step) MUST have `partner_ready` declared in the manifest's `declared_events`. Enforcement: the existing `_check_wait_for_caps` rejects undeclared events with `capability.missing_event`.
- A program that uses `place_at(target)` where `target` is a conveyor station MUST declare the station in `manifest.docking_stations` (not only in `declared_locations`). Enforcement: documented profile-level convention; in v0.1 the validator does not distinguish, and the requirement is a forward-looking constraint rather than a hard reject.

### Layer-2 primitive constraints (no new primitives)

The profile constrains the existing primitive vocabulary. None of the constraints requires new validator code; they are all enforced through existing per-primitive or envelope checks.

- `move_to`: named locations are the strong norm. Pose-based `move_to` is permitted but discouraged.
- `pick_from` / `place_at`: source / target SHOULD be a docking station name when the operation is a conveyor handshake or handoff. The profile pre-reserves `conveyor`, `handoff_in`, `handoff_out` as common station-name conventions.
- `wait_for`: `partner_ready` is the canonical partner-coordination event; `obstacle_detected` / `path_clear` are the canonical dynamic-obstacle events.
- `report`: `to: fleet_manager` is the canonical output endpoint.
- `take_off` / `land` / `return_to_home`: rejected with `capability.drive_type_not_aerial` (existing check); the warehouse profile is ground-floor.
- `speak` / `listen`: not used in v0.1 warehouse fixtures; not rejected, but reserved for future warehouse-with-voice-UI scope.

### Reference runtime changes

None. Warehouse programs dispatch through existing executors. The `CompositeAdapter` (mobile-runtime + industrial-arm-runtime) already pairs an AMR base with an industrial arm; warehouse use cases sit on that pairing without adapter changes.

### Conformance suite changes

`conformance/fixtures/warehouse/` gains eight fixtures (auto-discovered, no registry edit):

- `01_pick_from_shelf_place_on_conveyor_positive.yaml`. Mobile manipulator picks from shelf, places on conveyor station. Existing primitives, warehouse manifest.
- `02_amr_aisle_dynamic_obstacle_positive.yaml`. AMR navigates aisle with a `wait_for(obstacle_detected)` pause then a `wait_for(path_clear)` resume. No new mechanism; exercises the dynamic-obstacle event convention.
- `03_people_occupancy_speed_reduction_positive.yaml`. Program enters a `people_possible` zone; the envelope's `mixed_traffic_max_velocity` is the binding cap. Documents the envelope clamp.
- `04_envelope_speed_violation_rejected.yaml`. Program declares a velocity above the mixed-zone limit. Rejected by the existing envelope velocity check.
- `05_handoff_partner_event_undeclared_rejected.yaml`. Program uses `wait_for(condition.event: partner_ready)` against a manifest that does not declare `partner_ready` in `declared_events`. Rejected with `capability.missing_event`.
- `06_handoff_failure_recovery_positive.yaml`. Multi-step program with a `branch` that picks a fallback `place_at(reserve_station)` when `partner_unavailable` fires. Exercises Layer-3 composition under warehouse semantics.
- `07_multi_agv_handoff_zone_positive.yaml`. Two coordinated programs sharing a handoff dock, expressed as a sequence with explicit partner-ready waits. Exercises the coordination convention; does not require new primitives.
- `08_compliant_parts_bom_positive.yaml`. A warehouse manifest with a fully Hesai-free, US-aligned BOM (Locus-class AMR, Robotiq gripper, Intel RealSense). All five validator passes accept.

A new manifest fixture `reference/validator/tests/fixtures/manifests/warehouse_cell.yaml` provides the warehouse-shaped reference manifest the fixtures use. Mirrors `industrial_cell.yaml` but with a mobile AMR drive type, a handoff dock, conveyor stations, and the warehouse-specific declared events.

### Example application

`examples/warehouse/pick_to_conveyor.{urml.yaml,manifest.yaml,en.txt}` exercises the canonical warehouse cycle: AMR moves to a shelf, picks a tote, moves to a conveyor station, places the tote, reports to fleet_manager. The example uses only existing primitives.

### `urml init` template

`urml init my-warehouse --profile warehouse` scaffolds the warehouse starter (manifest, program, prompt, README, Makefile). `init_templates.py` gains `warehouse_project()` and a `"warehouse"` entry in the `PROFILE_TO_TEMPLATE` dispatch.

## Backward compatibility

Purely additive and pre-v1.0. No existing primitive, schema, fixture, example, or runtime behavior changes. Existing programs and manifests remain valid. The `spec/profiles/industrial/README.md:41` line that previously said *"plausibly its own profile"* is updated to link to the new profile, which is the only edit to existing spec text.

## Drawbacks

1. **Profile sprawl.** This is the sixth URML profile. Each profile is a normative commitment to maintain spec, fixtures, and examples. The cost is mitigated by the warehouse profile reusing existing primitives and existing validator passes; the marginal maintenance load is the eight fixtures and the spec doc, not new code paths.
2. **Industrial / warehouse overlap.** A "warehouse cell" with a fixed arm and a safety perimeter is plausibly an industrial deployment, not warehouse. The profile boundary is the AMR aisle, not the manipulation. Compositions that pair a warehouse AMR with an industrial cell SHOULD use both profiles (`profile: [warehouse, industrial]` is already supported by the program schema at `schemas/program.py:36`).
3. **Multi-agent coordination is convention, not primitive.** The profile defines `partner_ready` as the canonical event and expects programs to compose `wait_for + place_at` for handoff. If a substrate emerges that exposes atomic multi-agent handoff, a follow-up RFC may add a `handoff_to(partner_id)` primitive. The current convention is composable and substrate-neutral.
4. **Conveyor handshake is deferred.** Raising a digital line and waiting for the conveyor's acknowledgment belongs to RFC-0017 (`set_output`, still Draft). The warehouse profile cites RFC-0017 as the eventual mechanism. Until RFC-0017 lands, warehouse programs that need a real conveyor handshake either compose `report + wait_for` or rely on the substrate driver.
5. **Mixed-traffic speed cap is an envelope convention, not a manifest field.** A deployment that forgets to set `mixed_traffic_max_velocity` in its envelope will validate against the full `mobility.max_velocity`, which may be too fast for mixed traffic. The spec calls this out as a deployment hazard rather than a validator-enforced floor.

## Alternatives considered

- **Fold warehouse into the industrial profile.** Rejected. The safety envelope, the link-loss policy, and the dynamic-obstacle assumptions all differ. Forcing one profile to cover both either weakens the industrial safety perimeter or burdens warehouse deployments with an interlock that does not exist.
- **A "yard" profile instead.** A "yard" profile would cover outdoor warehouse approaches, loading docks, and weather-affected motion. Considered and deferred. Yard adds GPS frames and weather-state to the envelope; that is a larger spec change than warehouse and is plausibly its own future profile. Warehouse is the indoor-aisle scope; yard is the outdoor scope.
- **Ship `handoff_to(partner_id)` as a new primitive.** Rejected. Composes from `move_to(handoff_zone) + wait_for(partner_ready) + place_at(handoff_dock)`. Per CLAUDE.md "prefer fewer primitives", a new primitive is justified only when a substrate exposes an atomic operation. No current warehouse substrate does.
- **Ship `load_conveyor` / `unload_conveyor` as new primitives.** Rejected. Identical in effect to `pick_from(conveyor_station)` / `place_at(conveyor_station)`. The station-vocabulary extension is already in the manifest.
- **Couple warehouse to RFC-0017 acceptance.** Rejected. Coupling forces both RFCs to ship together; warehouse can ship without conveyor-handshake signals and benefit from RFC-0017 later.

## Prior art

- The industrial profile (RFC-0013) established the pattern of profile-extension primitives, per-profile validator helpers, and conformance-fixture-led normative force. Warehouse follows the structure without the primitives.
- The home (`speak`/`listen`, PR #25) and drone (`take_off`/`land`/`return_to_home`, PR #30) profiles established the spec → validator → executor → conformance pattern at a smaller scale.
- The OPC UA Robotics Companion Specification distinguishes between fixed-cell manipulation and warehouse-style mobile fleet operation in its `MachineryItemInformation` / `FleetVehicle` distinction; URML's industrial-vs-warehouse split mirrors that line.
- ROS-Industrial's `industrial_msgs` cover fixed-cell tooling; the open-source AMR community (Open-RMF) covers fleet coordination. URML's two profiles parallel this split.

## Unresolved questions

- Should `mixed_traffic_max_velocity` be promoted to a schema field in `envelope.py`? Today it lives as a free-form key the warehouse profile's envelope passes interpret. A formal schema entry would let the validator reject envelopes that lack it in a warehouse program. Deferred to a follow-up envelope-schema RFC.
- Should the warehouse profile require `connectivity` per RFC-0006? Industrial requires a `command_link`; warehouse plausibly requires a `fleet_link`. The profile spec recommends but does not require; a follow-up may tighten.
- The yard profile (outdoor warehouse approaches) — what frames, what weather model, what envelope. Tracked for v0.2.

## Implementation note

One PR set, mirroring RFC-0013's precedent. Commit order:

1. This RFC at `Draft` state plus an RFC-index row.
2. `spec/profiles/warehouse/README.md`.
3. `reference/validator/tests/fixtures/manifests/warehouse_cell.yaml`.
4. The eight conformance fixtures under `conformance/fixtures/warehouse/`.
5. `examples/warehouse/`.
6. `init_templates.py` warehouse template.
7. Existing-file edits: `spec/profiles/industrial/README.md:41`, `README.md` profile enumeration, `docs/launch/claims-audit.md` conformance count and a new warehouse row.
8. Verification: `urml conformance run` exits 0 with 97 passed; the full unit-test suite remains green; `make demo` / `make demo-run` still exit 0.
9. Flip this RFC `Draft → Open → Accepted → Implemented` per RFC-0001 process.

The Phase-0 seven-day Open-to-Accepted comment window is a founder-triggered calendar step tracked separately; it gates the state flip, not the code.

### Shipped (Draft → Implemented, 2026-06-12)

Landed as the sixth domain profile, **zero new primitives / schema / validator code** (the profile is a normative scope boundary + a manifest-interpretation set carried by spec prose and conformance fixtures):

- **Profile spec**: `spec/profiles/warehouse/README.md` (the normative MUST/SHOULD/MUST NOT set: mixed-traffic aisles, multi-agent handoff at declared docks, dynamic-obstacle pause, `people_occupancy_zones` elevated to required).
- **Fixtures**: `warehouse_cell` manifest + `warehouse_default` / `warehouse_with_occupancy_zone` envelopes (all in `MANIFEST_REGISTRY`), and the eight `conformance/fixtures/warehouse/` cases (pick-from-shelf, AMR aisle obstacle, handoff coordination + undeclared-partner reject, speed-violation reject, occupancy-zone-intrusion reject, multi-step cycle, compliant-BOM) — all green.
- **`urml init` template**: the `warehouse` manifest + envelope + program in `init_templates.py`.
- **Example**: `examples/warehouse/pick-to-conveyor` (runnable trio).

The profile reuses existing optional fields (`declared_locations`, `docking_stations`, `outputs`, `mobility.max_velocity`, `perception.sensors`, the envelope's `people_occupancy_zones`) under profile-specific prose constraints; existing primitives (`pick_from`/`place_at`/`move_to`/`wait_for`/`report` + the core twelve) already cover warehouse motion and manipulation. The three open questions (formal `mixed_traffic_max_velocity` schema field, required `connectivity`, the yard profile) remain deferred to follow-ups as written.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed and what is deliberately not being proposed (no new primitives, no schema, no validator code).
- [x] The Motivation is grounded in concrete artifacts (the industrial profile's line 41 stub, the existing mobile + industrial-arm substrate pairing, the federal market).
- [x] The Detailed design names every affected spec document and reference component, and explicitly identifies what is unchanged (`validator.py`, all runtime adapters).
- [x] At least one alternative is genuinely considered (folding into industrial; the yard profile; the `handoff_to` primitive; the `load_conveyor` pair).
- [x] Drawbacks are listed honestly. Profile sprawl, the mixed-traffic speed-cap convention without schema enforcement, and the conveyor handshake's dependency on RFC-0017 are real downsides.
- [x] Backward compatibility is honest: purely additive, one edit to one existing line in `spec/profiles/industrial/README.md`.
- [x] The substrate-neutrality acid test is trivially satisfied because zero adapters and zero primitives are touched.
- [x] The implementation note explains commit order, not just file list.
- [x] The author re-read CLAUDE.md §What Claude Should Never Do: warehouse is in the canonical civilian scope (`{home, drone, industrial, educational, research}` plus warehouse, all non-military), does not bypass the validator, adds no cloud dependency, embeds no vendor, and stays substrate-neutral.
