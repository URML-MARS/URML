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

# Tutorial 4 — Writing your own manifest

**By the end of this tutorial you will:**

- Have a capability manifest that describes *your* robot, not the scaffolded TurtleBot.
- Be able to add a new location, sensor, object class, or docking service from scratch.
- Know which fields are load-bearing (the validator rejects programs without them) versus advisory.

This tutorial assumes you've worked through [Tutorial 2](02-anatomy-of-a-program.md). You should be comfortable reading the structure of a URML program and the layered architecture.

## What a manifest is

A capability manifest is a YAML document that declares **what a robot can do**. The validator uses it to decide which URML programs the robot can execute *before* execution begins. The runtime uses it to translate symbolic locations (`kitchen`) into concrete poses, and to plan against declared limits.

Think of it as the contract between *the robot* and *anyone authoring URML programs for it*. The author writes against the manifest; the validator enforces it; the runtime honors it.

## Start from a scaffold

Open `my-first-robot/manifest.yaml` (the file `urml init` produced in Tutorial 1). Top to bottom, this is what it declares:

```yaml
manifest_version: "0.1"        # Schema version of THIS document
robot_id: turtlebot4_home      # A short, unique identifier
description: ...               # Free-text, for humans

frames: [...]                  # Coordinate frames (URDF-style)
declared_locations: [...]      # Named places the robot can navigate to
declared_events: [...]         # Events the runtime can wait for
mobility: {...}                # Can the robot move? How fast?
manipulation: {...}            # Does it have a gripper? Which?
perception: {...}              # Cameras, sensors, what classes it can detect
docking_stations: [...]        # Charging / tool-swap / etc.
outputs: {...}                 # Where it can `report` to
```

Each block is independently optional — a stationary robot omits `mobility`; a mobile robot without arms omits `manipulation`. But: if a URML program tries to use a capability the manifest doesn't declare, **the validator rejects the program with a stable `capability.missing_*` error code.** This is the safety boundary at work.

## Exercise 1: Add a new location

Suppose your robot needs to navigate to the *living room* in addition to the kitchen. Open `manifest.yaml` and find `declared_locations`. It looks like:

```yaml
declared_locations:
  - name: kitchen
    pose: { x: 3.2, y: 1.0 }
    frame: map
  - name: user
    pose: { x: 0.5, y: 0.5 }
    frame: map
  - name: charging_dock
    pose: { x: 0.0, y: 0.0 }
    frame: map
```

Add a new entry:

```yaml
  - name: living_room
    pose: { x: 1.5, y: 2.0 }
    frame: map
```

Now you can write a program that uses it. Create `living-room.urml.yaml` next to the existing program:

```yaml
profile: home
behavior:
  type: sequence
  steps:
    - move_to:
        location: living_room
```

Validate:

```bash
urml validate living-room.urml.yaml --manifest manifest.yaml --envelope envelope.yaml --profile home
```

Expected: `Validation passed`.

If you forgot to add the location and tried to validate, you'd see:

```
ERROR [capability.missing_location] behavior/steps/0
  field: location
  move_to references undeclared location 'living_room'.
  suggestion: Add 'living_room' to manifest.declared_locations, ...
```

That structured error is what the LLM bridge reads to drive its revision flow (Tutorial 3). It's also what *you* read to know exactly what to add.

## Exercise 2: Add a new object class

Suppose your robot can also detect plates. The manifest's perception block looks like:

```yaml
perception:
  cameras: [...]
  sensors: []
  object_vocabulary:
    - mug
    - cup
    - person
```

Add `plate`:

```yaml
  object_vocabulary:
    - mug
    - cup
    - person
    - plate
```

Now `detect: { object: plate, ... }` passes validation. Without that line, you'd see `capability.missing_object_class` — same structured-error pattern.

The vocabulary list is also what the LLM bridge inlines into its system prompt. If you add `plate` here, the LLM knows it can use `plate` in emitted programs.

## Exercise 3: Add a new sensor

Suppose your robot has a temperature sensor on its top. Manifests handle this with the `sensors` block:

```yaml
perception:
  cameras: [...]
  sensors:
    - name: ambient_temp
      measurement_type: temperature
      range_min: -10.0
      range_max: 80.0
      units: C
  object_vocabulary: [...]
```

The `measurement_type` is the load-bearing field — it's what `measure: { what: ... }` matches against. The valid values are in the spec (see [`docs/glossary.md`](../glossary.md) and the validator's `Sensor` schema): `temperature`, `distance`, `weight`, `pressure`, `humidity`, `depth`, `wind_speed`, `current`, `voltage`.

`range_min`/`range_max` and `units` are advisory in v0.1 — they're not enforced statically, but they're inlined into the LLM bridge's prompt so the model knows the sensor's working range when it emits programs.

Now a `measure` step like this works:

```yaml
- measure:
    what: temperature
    sensor: ambient_temp
    store_as: room_temp
```

…and later steps can branch on `$room_temp.value`.

## Exercise 4: Declare an event for `wait_for`

`wait_for` blocks until something external happens. Events the runtime is allowed to surface must be declared:

```yaml
declared_events:
  - user_present
  - emergency_stop
  - phone_rings   # new
```

Then a program can:

```yaml
- wait_for:
    condition: { event: phone_rings }
    timeout: "120s"
```

`condition: { event: phone_rings }` is checked against `declared_events`. Without the declaration, `capability.missing_event` fires.

## Exercise 5: Add a docking service

If your robot can swap consumables (a mop pad, a brush) at its dock, declare the service:

```yaml
docking_stations:
  - name: charging_dock
    pose: { x: 0.0, y: 0.0 }
    frame: map
    services:
      - park
      - charge
      - swap_consumable   # new
```

Then `dock: { at: charging_dock, service: swap_consumable }` passes validation. The runtime is responsible for the actual swap mechanism; URML declares only that the station offers it.

Core URML reserves `park` and `charge`. Other services (`swap_battery`, `swap_tool`, `refuel`, `transfer_payload`, `download_data`, `swap_consumable`) are profile-extensible — you declare them per station.

## Exercise 6: Declare hardware provenance for compliance checks

URML's v0.1 validator runs a fifth pass that checks a manifest's **hardware provenance** against a pluggable compliance policy (see [RFC-0004](../rfcs/0004-compliance-policy.md)). The default policy mirrors US federal procurement rules (NDAA Section 889 / FY26, the FCC Covered List, etc.); deployers outside the US override with `urml validate --policy <file.yaml>`, and `--no-policy` skips Pass 5 entirely.

Manifests **without** a `provenance:` block trigger no Pass 5 errors — policy enforcement is opt-in at the manifest level. Add a `provenance:` block when your deployment needs to *prove* compliance:

```yaml
provenance:
  manifest_attestation: third_party_audited    # self_declared | third_party_audited | cryptographically_signed
  components:
    - id: drive_controller
      role: critical                            # critical | non_critical | informational
      vendor: example_drive_vendor
      country_of_origin: US                     # ISO 3166-1 alpha-2
      country_of_final_assembly: US             # often differs from origin
      hbom_ref:                                 # optional; opaque-by-hash in v0.1
        format: cyclonedx-1.7
        uri: ./hbom/drive_controller.cdx.json
        sha256: "<64-hex-char-integrity-hash>"
```

The selector that policies usually filter on is `role: critical` — most regulatory rules turn on which components are "critical." If you declare provenance on every component as `informational`, the default policy will pass; that's a feature, not a bug — it lets manifests *opt in* to the structure without committing to every component being regulated.

If you write `country_of_origin: CN` on a critical component and run the default policy, the validator emits `policy.country_denied` with structured `detail` (rule ID, component ID, the denied country list, and a `remediation_hint`). The LLM bridge consumes that detail and exits its revision loop rather than asking the model to rewrite the program — programs cannot fix hardware.

See [`spec/layer-1-hal/policy.md`](../../spec/layer-1-hal/policy.md) for the normative policy file format, and [`examples/home/red-mug.manifest.yaml`](../../examples/home/red-mug.manifest.yaml) for a fully US-compliant illustrative manifest matching the canonical red-mug example.

A note worth repeating from the spec: a policy file passing the validator is **not a legal compliance determination**. The bundled default ships under Apache 2.0 forever per [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) item 7; audited and certified policy files carrying third-party legal attestation are a separate, legitimate commercial surface.

## What the validator does NOT check (yet)

In v0.1, the validator is strict about *declaration* — it rejects programs that reference undeclared anything. It is more permissive about:

- **Geometric containment.** If your manifest declares a `kitchen` at `(3.2, 1.0)` and your envelope declares a 5×5 m geofence at the origin, the validator checks that location-by-name is *declared*; it doesn't (yet) check that the declared pose is inside the polygon. That polygon-vertex math is on the v0.2 roadmap.
- **Per-frame transforms.** The validator checks that named frames exist in the manifest, but doesn't yet compose transforms (e.g., verify that `pose` in frame `cell` is reachable from frame `base_link`). Reuse of existing standards (URDF, SDF) is the v1.0 path here.
- **Dynamic envelope checks.** Wind speed, battery state, occupancy zones — these are *runtime* checks the substrate enforces. The validator catches *static* contradictions (a `scan` with declared altitude > the service ceiling); it can't anticipate weather.

The principle: the validator catches everything it can statically. The runtime catches the rest dynamically. Both are required for safety.

## Where the spec defines all this

Every field in the manifest is defined in `reference/validator/src/urml_validator/schemas/manifest.py` — that's the authoritative pydantic model the validator parses against. Read it directly if you want the full surface; it's about 200 lines.

The eventual normative spec doc lives at [`spec/layer-1-hal/`](../../spec/layer-1-hal/). That directory has a stub README today; the full document lands as part of Phase 1 of the [MANIFESTO roadmap](../../MANIFESTO.md).

You can also export the JSON Schema for any consumer that prefers it:

```bash
urml schema --name manifest > manifest.schema.json
```

— useful for IDE auto-complete, CI checks, or feeding into a non-Python tool.

## What you have now

A manifest tailored to your robot, or at least the muscle memory for shaping one. You know:

- Which fields are required (`mobility`, `manipulation`, `perception`, `declared_locations`, `declared_events` — depending on what your programs use).
- Where to add a new location, object class, sensor, event, or docking service.
- That every `capability.missing_*` error code corresponds to a missing manifest field.
- That the validator's strictness is the contract that protects you.

## Next

You've now seen the whole v0.1 URML surface end to end:

- **Tutorial 1** — install + scaffold + first validate.
- **Tutorial 2** — anatomy of a program.
- **Tutorial 3** — natural-language translation via the LLM bridge.
- **Tutorial 4** — manifests in depth.

The natural next things to explore — when you're ready — are outside the tutorial sequence:

- **The conformance suite** in [`conformance/`](../../conformance/) — every URML-compatible runtime must satisfy these fixtures.
- **The reference runtime** in [`reference/ros2-runtime/`](../../reference/ros2-runtime/) — how primitives become real ROS 2 (or mock) action calls.
- **RFC-0002** in [`docs/rfcs/0002-initial-primitive-vocabulary.md`](../rfcs/0002-initial-primitive-vocabulary.md) — the primitive vocabulary's design rationale plus a 6-substrate prior-art mapping (ROS 2 / PX4 / OPC UA / KUKA KRL / ABB RAPID / IEC 61131-3).
- **The Manifesto** at [`MANIFESTO.md`](../../MANIFESTO.md) — the strategic case.

If you're going to *build* with URML, the conformance suite is the next thing to read; if you're going to *understand* it, the Manifesto is.
