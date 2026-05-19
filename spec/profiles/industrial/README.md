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

# Industrial Profile

**Status:** Draft (v0.1)
**Targets:** URML v0.1
**Created:** 2026-05-13

The third URML profile: single-arm manipulators and mobile bases operating in controlled industrial cells. Constrains and extends the [twelve core primitives](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) for predictable physical environments with declared safety perimeters, defines a default safety envelope appropriate to cell operation (perimeter polygons, safety-door interlocks, force ceilings), and binds the profile's compliance posture to the [bundled US-federal policy](../../../docs/rfcs/0004-compliance-policy.md) with industrial-procurement notes (NDAA §889 applies the same way it does to drones, with different exposure vectors).

## Application domain

Single-arm manipulators and mobile bases operating in **controlled industrial cells**: pick-and-place stations, line stations, kitting cells, small-batch reconfiguration. The defining shape of the industrial profile is *predictable physical environment, well-defined safety perimeter, semi-trained operators reconfiguring tasks without re-programming the PLC*.

## In scope

- **Pick-and-place** with declared object types and bins. Canonical example: the line reconfiguration in [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Industrial: the line reconfiguration*.
- **Kitting** — assembling sets of components.
- **Light assembly** within force/torque limits the cell declares.
- **Mobile base operation within a declared cell perimeter** — pallet transport, station-to-station moves.
- **Safety-door-gated motion** — a mandatory interlock where the cell's safety perimeter being open halts motion.
- **Line reconfiguration via natural language** — the high-value use case: a line manager types *"same as before, but pick red instead of blue, and slow down by twenty percent"* and the LLM bridge produces a URML diff.

## Out of scope

- **Welding, painting, machining**, and other process-specialized tasks at v1.0. These are domain-specialized enough to merit their own profiles or to live outside the canonical maintenance scope.
- **Multi-arm coordination** at v1.0. Compose with multiple single-arm cells instead; explicit dual-arm coordination is a v1.x stretch.
- **Heavy-payload manipulation** beyond a declared cell ceiling.
- **Outdoor or human-shared-floor mobile operation.** Industrial mobile bases in this profile operate within a declared cell perimeter, not mixed-traffic warehouse aisles. Mixed-traffic warehouse operation is plausibly its own profile.

## Profile-required Layer-1 manifest fields

An industrial-profile-conformant capability manifest **must** declare:

- **`mobility`** with `drive_type` in (`manipulator_base`, `differential`, `omnidirectional`, `tracked`). VTOL or flight drive types are rejected for the industrial profile.
- **`manipulation`** with at least one declared gripper. `arm_count` must be 1 in v1.0 (multi-arm is v1.x).
- **`manipulation.grippers[].force_max_n`** is the load-bearing field — the envelope's `max_grip_force_n` must respect it, and `grasp.force` arguments are checked against it at Pass 3.
- **`perception.object_vocabulary`** — the closed set of object classes the manifest commits to. Industrial cells typically declare classes like `widget_red`, `widget_blue`, `small_part`, `pallet_id_123`. The validator rejects `detect(object: X)` when X is not declared.
- **`declared_locations`** — at minimum the cell's named stations (`pick_bin`, `kitting_tray_red`, `home_pose`). Industrial programs almost never use unnamed poses.
- **`declared_events`** — at minimum `safety_door_closed`, `line_ready`, `emergency_stop`. The first is the safety-door interlock event the cell asserts; programs use `wait_for(condition.event: safety_door_closed)` before motion.

An industrial-profile manifest **should** declare:

- **`provenance:`** per [RFC-0004](../../../docs/rfcs/0004-compliance-policy.md). Industrial deployments inside the US are routinely procured under federal contracts (defense industrial base, federally-funded labs); the bundled default policy enforces NDAA-style restrictions on critical components.
- **`docking_stations`** for charging mobile bases or for declared kitting stations the arm cycles through.

An industrial-profile manifest **must not** declare:

- **`mobility.service_ceiling`** with a non-trivial value (industrial cells are ground-level).
- **`speech` sensors or `speech` output endpoints** unless the cell has explicit voice-UI hardware (rare in v1.0; speech is the home profile's surface).

## Default safety envelope

An industrial cell operates with **trained operators, a declared physical perimeter, and explicit interlocks**. The default safety envelope is the most explicit-perimeter-oriented of the v1.0 profiles:

```yaml
envelope_version: "0.1"
deployment_id: <free-form>
description: <free-form>

# Numeric caps. Strictest-wins against the manifest's declared maxima.
max_velocity: 0.5                  # m/s; cell-floor motion cap (often slower than manifest's max).
max_grip_force_n: null             # bound by gripper.force_max_n by default; deployments may
                                   # tighten further (e.g., a hand-loading window).

# Spatial constraints.
cell_perimeter: []                 # list of polygons. The cell perimeter declared in the
                                   # manifest is the primary; the envelope may tighten
                                   # (e.g., a tool-change window during which the arm's
                                   # reach is restricted).
people_occupancy_zones: []         # the floor area an operator occupies during manual
                                   # loading windows. Motion is halted while the operator
                                   # is in any of these zones.

# Behavioral defaults.
safety_door_event: safety_door_closed   # must match a declared event on the manifest.
emergency_stop_event: emergency_stop
on_door_open: halt_all_motion           # other options: continue_safe_subset (deferred)

# RFC-0006: an industrial cell runs under a supervisory (operator/PLC) link.
# Loss of that link stops the cell — the conservative posture for machinery
# around trained operators.
link_loss_policy:
  - role: command_link
    action: halt_and_report
```

### Mandatory invariants

- **A program must wait for `safety_door_closed`** at the top of any sequence that includes manipulation or motion. Programs lacking it are accepted in v0.1 (warning, not error) but a follow-up tightening RFC will reject them.
- **`grasp.force` is at or below `gripper.force_max_n` AND at or below `envelope.max_grip_force_n`** when the envelope sets one. The validator already enforces this through the core envelope pass.
- **No motion outside the declared cell perimeter** — runtime invariant.
- **The supervisory link is required for operation (RFC-0006).** The manifest declares a `connectivity` block with a `command_link` that is `required_for_operation: true` (typically `assurance_class: assured`). Loss of that link triggers the declared `link_loss_policy` (default `halt_and_report`); the validator statically verifies the rule is coherent with the manifest.

## Layer-2 primitives this profile adds

[RFC-0002 §Detailed Design](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) authorizes per-profile primitive additions. The industrial profile adds three: `pick_from`, `place_at`, and `swap_tool`. They are **specified and implemented** by [RFC-0013](../../../docs/rfcs/0013-industrial-layer2-primitives.md) (schema + validator Pass-2 checks + ROS-2 executors + conformance fixtures + a runnable example), following the same pattern as the home (`speak`/`listen`) and drone (`take_off`/`land`/`return_to_home`) extensions. The normative per-primitive reference is [`spec/layer-2-primitives/v0.1.0.md`](../../layer-2-primitives/v0.1.0.md) §3.6–3.8; the signatures below are normative and mirror it.

### `pick_from`

Convenience over `move_to + detect + grasp` for the most-common industrial pattern.

**Signature (normative; see Layer-2 §3.6):**

```yaml
- pick_from:
    source: <station_name>           # required; resolved against declared_locations
    object: <class>                  # required; resolved against object_vocabulary
    attributes: { color: red, ... }  # optional; same shape as detect.attributes
    force: gentle | firm | <newtons> # optional; default per gripper
    store_as: <name>                 # required if subsequent steps reference $name
```

**Semantics.** Move to `source`, detect an object matching `object` + `attributes` within the station's pickup zone, grasp it with the declared force, return.

**Compose-vs-primitive.** A user could write `move_to(source) + detect(object) + grasp($target)` instead. The profile adds `pick_from` because (a) the composition is so frequent that the primitive saves visible repetition in every industrial program, and (b) industrial substrates often expose a single atomic "pick at station" operation (e.g., a configured PLC sequence) that maps cleanly to one primitive rather than three.

**ROS-2 implementation sketch:** Nav2 navigate-to + perception query + MoveIt 2 grasp, with the three steps composed in the runtime adapter. Or, when a configured station-controller exists, a single action call to the station service.

**Non-ROS implementation sketch:** OPC UA Robotics — `Manipulation.PickFrom(station, object)` method; the OPC UA station-service binding handles the composition internally. PLC + Ethernet/IP — vendor-specific pick-at-station function block.

### `place_at`

Symmetric to `pick_from`. Convenience over `move_to + release(mode: place)`.

**Signature (normative; see Layer-2 §3.7):**

```yaml
- place_at:
    target: <station_name>           # required
    held: $name                      # required; the object being held (from prior pick_from)
    mode: place | drop               # optional; default: place
    height: <distance>               # optional; for drop mode
```

**Semantics.** Move to `target`, release `held` with the declared mode at the target's declared placement pose.

### `swap_tool`

End-of-arm tool changes for cells with declared tool-change stations.

**Signature (normative; see Layer-2 §3.8):**

```yaml
- swap_tool:
    at: <station_name>               # required; must declare a `swap_tool` service
    to: <tool_name>                  # required; the tool to mount
```

**Semantics.** Move to the tool-change station, execute the substrate's tool-change procedure, return.

**Capability requirements:** `manifest.docking_stations[].services` includes `swap_tool` at the target station. The named tool being in the station's declared `accepted_tools` list is a profile-extension manifest field that remains **deferred** — v0.1 validates only that the station declares the `swap_tool` service, not that `to` is an accepted tool (see [RFC-0013](../../../docs/rfcs/0013-industrial-layer2-primitives.md) Drawbacks). `swap_tool` reuses the `dock` dispatch path (`send_docking_goal`), so no new substrate Protocol method is introduced.

## Layer-2 primitives this profile constrains

### `move_to`

- **Frame must be declared.** Industrial cells almost always declare their own `cell` frame as root; the validator rejects move_to programs that use an unnamed coordinate system.
- **Named locations are the norm.** Pose-based move_to is permitted but discouraged in industrial programs (the line manager edits a station list, not a coordinate file).
- **Velocity ceiling is the envelope's `max_velocity`,** typically 0.5 m/s — tighter than most cell mobility-base maxima.

### `grasp`

- **Force ceiling is bounded by both `gripper.force_max_n` and `envelope.max_grip_force_n`** (when the envelope sets one). The envelope value can tighten further during manual-loading windows.
- **Industrial typical default force is `firm` (8N)**, not `gentle` (1.5N) — the opposite of the home profile.

### `wait`

- **`wait` is permitted at any position,** like home. Industrial programs use `wait` for cycle-time padding when the line cadence requires it.

### `wait_for`

- **`safety_door_closed` is the canonical interlock event.** A program that begins with motion without first waiting for this event is accepted in v0.1 (warning) and will be rejected in a future tightening RFC.

### `detect`

- **Object classes must be in the manifest's declared `object_vocabulary`.** Industrial cells typically declare per-color or per-tag variants (`widget_red`, `widget_blue`, `pallet_id_123`).

### `report`

- **`to: line_controller`** is the conventional industrial output endpoint, declared in `manifest.outputs.named_endpoints`. PLC integration consumes report messages via OPC UA or vendor protocols.

## Layer-4 (LLM bridge) integration

The industrial profile is where the **line-reconfiguration use case** exercises the bridge most heavily:

- The bridge's `industrial_few_shots` ship with the bridge package; loaded automatically when `profiles=("industrial",)` is passed to `Bridge`.
- Programs that reference a prior program (the *"same as before, but..."* pattern) require a mechanism to diff URML programs that the bridge handles by sending the prior program as part of the system prompt. Implementation detail of the bridge; not normative to this profile.
- `report(to: line_controller)` is the canonical output channel for kitting outcomes; the bridge translates the `facts` dict into machine-readable JSON for the PLC.

## Compliance policy alignment

Industrial deployments inside the US are commonly procured under federal contracts (defense industrial base; DOE / NASA / DARPA-funded research). The bundled default policy (RFC-0004) applies the same way it does to home and drone profiles, with industrial-specific considerations:

- **Robot controllers** are typically the critical component for procurement rules. KUKA controllers (German), ABB controllers (Swedish/Swiss), FANUC controllers (Japanese) typically pass; Chinese-origin controllers reject under `policy.country_denied`.
- **End-of-arm tooling** (grippers, fixtures) is often non-critical for procurement rules but may be regulated by other frames (export controls).
- **Vision systems** are more commonly regulatorily-sensitive — Cognex (US), Keyence (JP), Sick (DE) typically pass. The denylist also reaches industrial vision when vendors overlap with FCC Covered List entries.
- **PLC integration software** is typically out of scope of URML's compliance pass but may be a separate procurement concern.

Deployers outside the US should override the default with their own policy.

## Conformance points

The conformance suite at `/conformance/fixtures/industrial/` ships these fixtures:

| Fixture | What it tests |
|---|---|
| `01_pick_red_positive.yaml` | Canonical line scenario written with the **core twelve** (`move_to + detect + grasp + move_to + release`) — the documented composition-equivalent of `pick_from`/`place_at`. |
| `02_type_mismatch_rejected.yaml` | A `measure` result fed to `grasp.target` is rejected with `binding.type_mismatch` (Pass 4). |
| `03_link_outage_relaxed_rejected.yaml` | RFC-0006 link-outage coherence on the connectivity manifest variant. |
| `04_pick_from_positive.yaml` | RFC-0013 happy path: `wait_for(safety_door_closed)` + `pick_from` + `place_at` + `report`; asserts the composed audit-method order and the `pick_from` → `place_at` binding flow. |
| `05_swap_tool_positive.yaml` | RFC-0013: `swap_tool` at a declared `tool_change_station`; asserts the single audit method is `send_docking_goal` (swap_tool rides the docking-service mechanism). |
| `06_swap_tool_undeclared_service_rejected.yaml` | RFC-0013 negative: `swap_tool` targeting a location that is not a docking station is rejected with `capability.missing_docking_station` before execution. |

The runnable `examples/industrial/` programs are `simple-pick-and-place` (the
core-twelve composition) and `pick-place-tool-change` (the RFC-0013 primitives).
Further negatives (force-ceiling, safety-door warning promoted to error, the
bridge line-reconfiguration diff) are tracked follow-ups, not blockers for
RFC-0013.

## Related documents

- [`/docs/architecture.md`](../../../docs/architecture.md) §Profiles.
- [`/spec/layer-1-hal/`](../../layer-1-hal/) — capability manifest reference.
- [`/spec/layer-2-primitives/`](../../layer-2-primitives/) — the core twelve.
- [`/docs/rfcs/0002-initial-primitive-vocabulary.md`](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) — primitive vocabulary, including the §Profile-extensibility clause authorizing `pick_from` / `place_at` / `swap_tool`.
- [`/docs/rfcs/0003-us-alignment.md`](../../../docs/rfcs/0003-us-alignment.md) — strategic alignment.
- [`/docs/rfcs/0004-compliance-policy.md`](../../../docs/rfcs/0004-compliance-policy.md) — compliance policy mechanism.
- [`/spec/profiles/home/`](../home/) — sibling profile spec for comparison.
- [`/spec/profiles/drone/`](../drone/) — sibling profile spec for comparison.
- [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Industrial: the line reconfiguration*.
