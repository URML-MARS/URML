---
rfc: 0002
title: Initial Layer-2 Primitive Vocabulary
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-11
updated: 2026-05-17
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

# RFC-0002: Initial Layer-2 Primitive Vocabulary

## Summary

Specify the initial Layer-2 intent primitive vocabulary for URML v0.1: **twelve verbs** that, together with Layer-3 composition, cover the v1.0 home, drone (civilian), and industrial profile use cases without expanding the core beyond a manageable surface.

The twelve: `move_to`, `dock`, `hover`, `wait`, `wait_for`, `grasp`, `release`, `detect`, `scan`, `measure`, `capture`, `report`.

Three principles drive every inclusion and every exclusion: composition over expansion, substrate neutrality, and profile-extensibility.

## Motivation

Layer 2 is the center of gravity of URML. Without a stable initial primitive vocabulary the rest of the project cannot proceed:

- **Layer 1** does not know what capability fields manifests must declare — the manifest schema is *derived* from the primitives' declared requirements.
- **Layer 3** has nothing to compose.
- **Layer 4** has no JSON Schema to ask an LLM to emit.
- The **reference runtimes** have no contract to implement.
- The **conformance suite** has no behaviors to test.
- The first end-to-end example ([`/examples/home/red-mug.urml.yaml`](../../examples/home/red-mug.urml.yaml)) is illustrative-pre-validation until the primitives it uses are normatively specified.

This RFC unblocks Phase 1 by closing the foundational design question. Every later RFC — the per-layer specs, the profile specs, the validator behavior — bolts onto this one.

## Detailed Design

### Design principles applied

The vocabulary is shaped by three principles, in priority order:

**1. Composition over expansion.** [MANIFESTO.md](../../MANIFESTO.md) §Design Principles caps the core at under thirty primitives. The right reading of that ceiling is not "fit as many as possible" but "if a behavior can be composed from existing primitives, it should be." A new primitive is a one-way door. Every verb in this RFC either expresses an intent that cannot be cleanly composed (`hover` actively maintains position against disturbances; `wait` does not), or saves repeated composition so common that the long-tail maintenance cost of the dedicated primitive is worth paying (`scan` over `move_to + capture` per waypoint).

**2. Substrate neutrality.** Per [`CLAUDE.md`](../../CLAUDE.md): *every Layer-2 primitive must be cleanly implementable on a runtime with zero ROS dependencies.* Each per-primitive section below includes both a ROS-2 implementation sketch and a non-ROS implementation sketch (PX4/MAVLink, OPC UA, or a generic vendor SDK). A primitive that fails the non-ROS sketch is leaking substrate assumptions.

**3. Profile-extensibility.** The twelve are the *core* — the verbs meaningful across multiple profiles. Profiles add their own:
- Drone: `take_off`, `land`.
- Home: `speak`, `listen`.
- Industrial: `pick_from(bin|conveyor|pallet)`, `place_at(fixture|station)`, `swap_tool`.
- AV (research-grade): `plan_path` (compute a trajectory), `follow_trajectory` (execute it) ([RFC-0020](0020-autoware-av-substrate.md)).
- Capability-gated (not bound to a profile, enabled by a manifest declaration): `call_program` ([RFC-0015](0015-control-program-invocation.md), manifest-declared programs), `bimanual` ([RFC-0010](0010-whole-body-bimanual-manipulation.md), two-arm manifests), `set_output` ([RFC-0017](0017-digital-io-actuation.md), manifest-declared output lines).

Each profile RFC follows this RFC's template.

### Inventory

| # | Verb | One-sentence purpose |
|---|---|---|
| 1 | `move_to` | Go to a named location or a pose, optionally in a declared frame, optionally carrying something. |
| 2 | `dock` | Return to a declared station and optionally perform a service (park, charge, ...). |
| 3 | `hover` | Actively maintain position against disturbances, for a duration or until a condition. |
| 4 | `wait` | Pause in place passively for a duration. |
| 5 | `wait_for` | Block until an external event, signal, or input. |
| 6 | `grasp` | Close a gripper on a detected target, with a declared force. |
| 7 | `release` | Open a gripper with a declared mode (drop, place, hand_to_user). |
| 8 | `detect` | Find an object matching criteria and bind it to a variable. |
| 9 | `scan` | Survey an area with a declared pattern; produce structured perception data. |
| 10 | `measure` | Take a single reading (distance, temperature, weight, ...) and bind it. |
| 11 | `capture` | Capture a media artifact (photo or video) and bind a handle. |
| 12 | `report` | Send structured information upstream (to user, log, or caller). |

### Common conventions

These conventions apply to every primitive below; they are listed here once to keep the per-primitive sections short.

- **Pose**: A `pose` is `{x: number, y: number, z?: number, yaw?: number, pitch?: number, roll?: number}` paired with a `frame: <declared frame identifier>`. Units are SI (meters, radians). The frame must be declared in the target's Layer-1 capability manifest. Profiles may alias fields for LLM ergonomics — the drone profile aliases `pose.z` as `altitude` and adds `frame: agl | amsl`; an underwater profile would alias as `depth`. Aliasing is a Layer-4 / prompt-contract concern; the canonical spec uses `pose.z`.
- **Location**: A `location` is either a named place from the manifest (`location: kitchen`) or a `pose` with a `frame`. The validator resolves named locations against the manifest's declared-locations vocabulary.
- **Variable bindings**: A primitive that produces a result accepts a `store_as: <name>` argument. Subsequent steps reference the result as `$name`. Type compatibility across producer and consumer is statically checked (Layer-3 territory; see Unresolved Questions).
- **Capability requirements**: Each primitive declares which Layer-1 manifest fields must be present for the validator to accept a program using it. Programs whose target manifest is missing a required field are rejected.
- **Safety-envelope checks**: Each primitive declares which envelope checks the validator runs against it. These are *static*: they reject programs that *must* violate the envelope. Runtime monitoring of dynamic conditions (wind, obstacles, people walking into a cell) is the substrate's job.

### 1. `move_to`

Go to a named location or a pose.

**Signature:**

```yaml
- move_to:
    location: <name>             # mutually exclusive with `pose`
    pose: {x: ..., y: ..., z?: ..., yaw?: ..., pitch?: ..., roll?: ...}
    frame: <frame_id>            # required if `pose` is used
    carrying: $name              # optional; declares an object the robot is transporting
    speed: <fraction|absolute>   # optional override of manifest default
```

**Semantics.** The robot reaches the declared location or pose. The runtime selects the trajectory; URML does not specify it. Completion is reported when the robot is within the substrate's declared positioning tolerance.

**Capability requirements (Layer 1):** `mobility` declared; the named `location` must resolve against `manifest.declared_locations` or the active world model; if `pose` is used, the declared `frame` must be in `manifest.frames`.

**Safety-envelope checks:** target is within declared geofence / cell perimeter / mapped area; target's altitude (if any) is at or below `manifest.service_ceiling` and the declared deployment cap; `speed` is at or below `manifest.max_velocity` and any active deployment cap.

**Variable bindings:** `move_to` does not produce a result. Errors (`target_unreachable`, `path_blocked`, `envelope_violation`) are surfaced to Layer-3 `on_error`.

**ROS-2 implementation sketch:** Nav2 `NavigateToPose` action with the planned pose; for arm motion, MoveIt 2's `MoveGroup` action with the target pose; goal status maps to URML completion.

**Non-ROS implementation sketch:** PX4 — `MAV_CMD_NAV_WAYPOINT` for global poses or offboard-mode setpoints for local-frame poses; mission protocol uploads the goal and mission progress maps to completion. OPC UA Robotics — `MoveTo` method on the motion service.

### 2. `dock`

Return to a declared station and optionally perform a service.

**Signature:**

```yaml
- dock:
    at: <station_name>           # optional; default: manifest's declared primary dock
    service: <service>           # core: park (default), charge
                                 # profile-extensible: swap_battery, swap_tool,
                                 #   refuel, transfer_payload, download_data,
                                 #   swap_consumable, ...
    until: <full | duration | condition>  # optional; defaults per-service
```

**Semantics.** The robot navigates to the declared station, parks in the station's pose, and (if `service` is non-default) initiates the requested service. The runtime is responsible for the station-specific procedure — engaging a charger contact, opening a payload bay, etc. The primitive blocks until the service is complete or `until` is satisfied.

**Capability requirements (Layer 1):** `mobility` declared; the target station declared in `manifest.docking_stations` with the requested `service` in the station's declared services list.

**Safety-envelope checks:** target station is within the declared operational area; `service` is in the active profile's enum; the robot's current state allows the service (e.g., battery present for `charge`, gripper empty for `swap_tool`).

**Variable bindings:** `dock` does not produce a result by default. Status (`docked`, `service_complete`, `service_aborted`) is available to Layer-3 `on_error`.

**ROS-2 implementation sketch:** Nav2 `DockRobot` action (Iron+) or a custom action that wraps Nav2's docking server; service-specific behaviors via separate action clients (battery-management, tool-changer).

**Non-ROS implementation sketch:** PX4 — `MAV_CMD_NAV_LAND` followed by `MAV_CMD_DO_AUX_FUNCTION` for service triggers, or vendor-specific docking modes. OPC UA Robotics — `Dock` method with a `service` parameter on the docking service.

**Composition vs. expansion.** `dock(service: charge, until: full)` could be expressed as `dock + wait_for(battery: full)`. It is a primitive anyway because (a) the composition cannot express atomic departure ("leave dock as soon as charge crosses 80%" requires the runtime to start the next motion at the instant the threshold is crossed; a separate `wait_for` followed by `move_to` introduces a gap) and (b) several services are not composable as "park-then-wait" at all (battery swap requires the robot to be in a specific pose and the swap mechanism to engage).

### 3. `hover`

Actively maintain position against disturbances.

**Signature:**

```yaml
- hover:
    over: $target | <location>   # optional; default: current position
    duration: <time>             # mutually exclusive with `until`
    until: <condition>           # mutually exclusive with `duration`
    tolerance: <distance>        # optional; default per manifest
```

**Semantics.** The robot actively maintains position (translation and yaw) within the declared tolerance for the declared duration or until the declared condition. Distinct from `wait` in that `hover` *commits* to actively rejecting disturbances; `wait` is passive.

**Capability requirements (Layer 1):** the robot's `mobility.station_keeping` is `true` (multirotor drones, station-keeping underwater vehicles, satellites; ground robots typically have this trivially as "stay parked").

**Safety-envelope checks:** the hover location is within the declared operational area; the duration does not exceed declared endurance (battery, fuel) by more than the declared safety margin; if the active profile sets a no-fly-over-people constraint, the hover pose does not overlap declared people-occupancy zones.

**Variable bindings:** `hover` does not produce a result.

**ROS-2 implementation sketch:** Nav2 spinning or position-hold behavior; for arms, MoveIt 2 trajectory holding.

**Non-ROS implementation sketch:** PX4 — `MAV_CMD_NAV_LOITER_TIME` (timed) or `MAV_CMD_NAV_LOITER_UNLIM` paired with a separate condition watcher (until-mode). OPC UA Robotics — position-hold mode on the motion service.

### 4. `wait`

Pause in place passively for a duration.

**Signature:**

```yaml
- wait:
    duration: <time>             # required
```

**Semantics.** The robot halts active motion intent and waits for the declared duration. Unlike `hover`, the runtime is not required to actively reject disturbances — a drone may drift in wind, a wheeled robot may roll on a slope. Profile constraints (e.g., the drone profile may forbid `wait` in flight) override.

**Capability requirements (Layer 1):** none beyond the general capability to remain idle.

**Safety-envelope checks:** profile-active prohibitions (e.g., drone profile rejects `wait` between `take_off` and `land` — drones must `hover`, not `wait`).

**ROS-2 implementation sketch:** a simple sleep node, or no-op for the duration with action clients held.

**Non-ROS implementation sketch:** PX4 — for ground-stationary contexts only; not used in flight. OPC UA — no-op timer.

### 5. `wait_for`

Block until an external event, signal, or input.

**Signature:**

```yaml
- wait_for:
    condition:                   # exactly one of:
      event: <event_name>
      signal: <signal_name>
      input: speech | text | gesture | button | external
      sensor_threshold: {sensor: <name>, op: <gt|lt|eq|ne>, value: <number>}
    timeout: <time>              # optional; default per-deployment
    on_timeout: error | continue # optional; default: error
```

**Semantics.** The robot remains in its current state and blocks the program until the declared condition becomes true or the optional timeout fires. Events and signals are declared in the active profile; inputs are mediated by the LLM bridge (Layer 4) for `speech` and `text`, and by the substrate for the rest.

**Capability requirements (Layer 1):** the source of the declared condition must be a declared input/sensor in `manifest.perception` or `manifest.declared_events`.

**Safety-envelope checks:** the wait pose is within the declared operational area; the timeout does not exceed declared endurance by more than the safety margin.

**Variable bindings:** the resolved condition value (e.g., the user's spoken input, the sensor reading at threshold crossing) may be bound via `store_as`.

**ROS-2 implementation sketch:** a subscription to the relevant topic with a predicate matcher; for `input: speech`, a callback into the LLM bridge.

**Non-ROS implementation sketch:** PX4 — parameter-monitor or telemetry-driven event; for `input: speech`, an out-of-band link to the bridge. OPC UA — a subscription on the matching node.

### 6. `grasp`

Close a gripper on a detected target, with a declared force.

**Signature:**

```yaml
- grasp:
    target: $name                # required; reference to a prior `detect` binding
    force: gentle | firm | <number>N   # optional; default per profile
    approach: top | side | front | auto # optional; default: auto
```

**Semantics.** The robot positions the end-effector for the declared approach, closes the gripper on the target until contact is sensed (or the gripper's positional limit is reached), and applies the declared force. Completion is reported when the gripper reports a stable grip.

**Capability requirements (Layer 1):** `manipulation.grippers` declared and includes at least one gripper whose declared force range contains the requested force; the `target` binding's object class is in the gripper's accepted-class list.

**Safety-envelope checks:** requested force is within the gripper's declared range; requested force is at or below the active profile's ceiling (home profile defaults to `gentle`); the target's declared position is within the gripper's reachable workspace.

**Variable bindings:** `grasp` does not produce a result; failure (`no_object_sensed`, `force_exceeded`) is surfaced to Layer-3.

**ROS-2 implementation sketch:** MoveIt 2 grasping with a configured gripper plugin; force control via the gripper's action server.

**Non-ROS implementation sketch:** OPC UA Robotics — `Grasp` method on the manipulation service; force as a method parameter. Vendor SDK — vendor-specific grip API.

### 7. `release`

Open a gripper with a declared mode.

**Signature:**

```yaml
- release:
    mode: drop | place | hand_to_user
    at: <location | pose>        # required iff mode == place
    height: <distance>           # optional; default per profile, for `drop` and `place`
```

**Semantics.** The robot opens the gripper according to the declared mode:
- `drop` — open at the current pose; the object falls under gravity.
- `place` — move to `at` (with a declared `height` offset), open, and verify the object is supported before retreating.
- `hand_to_user` — present the object to a declared `user` location and open only when the substrate signals the user has taken it (or after a profile-declared timeout).

**Capability requirements (Layer 1):** `manipulation.grippers` declared; for `mode: place`, the target location is reachable.

**Safety-envelope checks:** for `drop`, drop height does not exceed profile-declared maximum (home profile defaults to a low ceiling to avoid breakable objects); for `hand_to_user`, the user location is within the reachable workspace.

**ROS-2 implementation sketch:** MoveIt 2 release; for `hand_to_user`, a force-monitoring callback triggers the release.

**Non-ROS implementation sketch:** OPC UA — `Release` method with `mode` parameter. Vendor SDK — vendor-specific grip-open API.

### 8. `detect`

Find an object matching criteria and bind it to a variable.

**Signature:**

```yaml
- detect:
    object: <class_name>         # required; must be in declared object vocabulary
    attributes:                  # optional; class-specific
      color: <name|hex>
      size: small | medium | large | {dim: <number>}
      tag: <id>
      ...
    where:                       # optional; constrain search
      near: $reference | <location>
      within: <distance>
    store_as: <name>             # required if the result is referenced later
```

**Semantics.** The robot's perception pipeline searches for an object matching the declared class and attributes within the declared region (or the full perceivable workspace if `where` is omitted). On success, the result is bound — the bound value includes the object's class, pose, and any reported attributes. On failure, `not_found` surfaces to Layer-3.

**Capability requirements (Layer 1):** `perception` declared with at least one sensor capable of detecting the requested class; the requested class is in the manifest's declared object vocabulary.

**Safety-envelope checks:** the declared search region is within the operational area.

**Variable bindings:** the `store_as` name resolves to a structured object with at least `{class, pose, frame, attributes, confidence}`.

**ROS-2 implementation sketch:** a perception pipeline subscribed to camera or depth-sensor topics, publishing detected-object messages with a request/response action wrapping the query.

**Non-ROS implementation sketch:** PX4 — onboard companion-computer perception with detection results streamed via MAVLink CAMERA_TRIGGER and STATUSTEXT, or via a parallel ROS-less perception service. OPC UA — call the perception service's `FindObject` method.

### 9. `scan`

Survey an area with a declared pattern; produce structured perception data.

**Signature:**

```yaml
- scan:
    area: <polygon | bounding_box | named_region>
    pattern: serpentine | spiral | grid | adaptive
    overlap: <fraction>          # optional; default 0.3, for serpentine/grid
    altitude: <distance>         # optional; for aerial scans (drone profile aliases pose.z)
    media: photo | video | sensor_only  # optional; default: photo
    sensor: <sensor_name>        # optional; default: primary camera
    store_as: <name>             # required
```

**Semantics.** The robot follows the declared pattern over the declared area, collecting structured perception data at each sampling point. The bound result includes the per-sample data (pose, timestamp, sensor output, media handle when applicable) and an aggregated summary (area covered, sample count, anomalies if the substrate's perception flagged any).

**Capability requirements (Layer 1):** `mobility` (the robot moves across the area); `perception` with the declared sensor; for aerial scans, `mobility.flight` and a service ceiling at least the declared altitude.

**Safety-envelope checks:** area is within the operational envelope; pattern-derived path stays within the envelope; for aerial scans, altitude is within both the manifest's service ceiling and the active deployment cap; for declared people-occupancy zones, no sample point overlaps without an explicit override in the manifest.

**Variable bindings:** the `store_as` produces `{samples: [...], coverage: <fraction>, anomalies: [...]}`.

**ROS-2 implementation sketch:** Nav2 path-following along the generated pattern with a perception callback at each waypoint; for arms, MoveIt 2 trajectory with sensor triggers.

**Non-ROS implementation sketch:** PX4 — generate the pattern as a `MISSION` upload (sequence of waypoints with camera triggers via `MAV_CMD_DO_DIGICAM_CONTROL`). OPC UA — `RunScan` method with pattern and area parameters.

### 10. `measure`

Take a single reading and bind it.

**Signature:**

```yaml
- measure:
    what: distance | temperature | weight | pressure | <declared>
    target: $name | <location>   # optional; default: current pose
    sensor: <sensor_name>        # optional; default: declared sensor for `what`
    store_as: <name>             # required
```

**Semantics.** The robot takes a single reading using the declared sensor and binds the result. Distinct from `scan` (which surveys an area and produces a structured collection) and `detect` (which produces an object reference, not a scalar).

**Capability requirements (Layer 1):** `perception` declares a sensor capable of the requested measurement type.

**Safety-envelope checks:** the target is within the sensor's declared range.

**Variable bindings:** the `store_as` produces `{value: <number>, unit: <string>, timestamp: <time>, confidence?: <number>}`.

**ROS-2 implementation sketch:** subscribe to the sensor's topic, take one message, return.

**Non-ROS implementation sketch:** PX4 — read the sensor's MAVLink message stream. OPC UA — `Read` on the relevant node.

### 11. `capture`

Capture a media artifact (photo or video) and bind a handle.

**Signature:**

```yaml
- capture:
    media: photo | video
    target: $name | <location | pose>   # optional; default: current camera view
    duration: <time>                    # required iff media == video
    attributes:                         # optional
      resolution: <e.g., 1080p, 4k>
      format: jpeg | png | mp4 | ...
      frame_rate: <fps>                 # for video
    store_as: <name>                    # required
```

**Semantics.** The robot uses its primary (or declared) camera to capture the requested media. For `media: photo`, a single still is captured. For `media: video`, a recording of the declared duration is captured. If `target` is set and the camera is movable, the camera is pointed at the target before capture; if the camera is fixed and the target is not in frame, the validator rejects the program.

**Capability requirements (Layer 1):** `perception.cameras` declared with at least one camera that supports the requested `media` mode; if `target` is set, `cameras[i].movable: true` (validator catches the fixed-camera case statically).

**Safety-envelope checks:** for video, duration does not exceed declared storage / endurance budget by more than safety margin; for capture in declared privacy-restricted zones (a profile may declare these — e.g., the home profile flags bathrooms and children's rooms as default-restricted), an explicit override is required in the manifest.

**Variable bindings:** the `store_as` produces a media handle `{type, format, size, timestamp, pose, frame, uri}` — the substrate decides where the bytes live (local file, ROS bag, MAVLink ftp endpoint, cloud-mirror configured by the deployment).

**ROS-2 implementation sketch:** `image_transport` for photos; recording to a ROS bag or a configured external sink for video.

**Non-ROS implementation sketch:** PX4 — `MAV_CMD_DO_DIGICAM_CONTROL` for photo, `MAV_CMD_VIDEO_START_CAPTURE`/`STOP_CAPTURE` for bounded video. OPC UA — `TakeImage` / `StartRecording` methods.

**Streaming (deferred):** `media: stream` and continuous open-ended recording are deferred. They require Layer-3 design for unbounded actions — there is no clean way today to express "start capturing and continue until something else says stop." See Unresolved Questions.

### 12. `report`

Send structured information upstream.

**Signature:**

```yaml
- report:
    to: user | log | caller | <named_endpoint>
    facts:                       # required; arbitrary structured content
      <key>: <value>
      ...
    attachments:                 # optional; list of media handles from `capture`
      - $name
      ...
    status: success | partial | failure   # optional; default: success
    severity: info | notice | warning | error  # optional; default: info
```

**Semantics.** The runtime serializes the declared facts (and any attached media handles) and emits to the declared destination. The LLM bridge translates `to: user` into a natural-language utterance through Layer 4; `to: log` writes a structured log entry; `to: caller` returns to whatever invoked the program (the bridge, an upstream orchestrator, etc.).

**Capability requirements (Layer 1):** the declared destination is reachable per the manifest's declared `outputs`.

**Safety-envelope checks:** none beyond destination validity.

**ROS-2 implementation sketch:** publish on a configured topic with a structured message type; for `to: user`, return through the LLM bridge.

**Non-ROS implementation sketch:** PX4 — `STATUSTEXT` for short messages, MAVLink FTP for attachments. OPC UA — write to a configured node, with attachments via the file-transfer service.

### Validator changes

The validator gains a per-primitive validation pass. For each primitive in a program:

1. **Argument type check.** Required arguments are present; optional arguments are well-typed; mutually exclusive arguments are not co-present.
2. **Capability check.** The Layer-1 manifest declares the required capability fields. Missing fields are reported with a structured error naming the primitive, the missing field, and the suggested manifest addition.
3. **Safety-envelope check.** Profile-active envelope constraints are applied. Constraints declared by multiple profiles are conjoined (the strictest wins).
4. **Variable-binding check.** `store_as` names are unique; `$variable` references resolve to a prior `store_as` of compatible type.

The structured error format is the contract the LLM bridge uses to revise emissions. It will be specified in a follow-up RFC (target: RFC-0003 or RFC-0004); for the purpose of this RFC, the format is *"a JSON object containing primitive, field, problem, suggestion."*

### Reference runtime changes

When this RFC is Accepted:

- [`/reference/ros2-runtime/`](../../reference/ros2-runtime/) declares conformance to `layer-2-primitives@0.1.0` only after implementing all twelve primitives per their semantics.
- [`/reference/px4-runtime/`](../../reference/px4-runtime/) declares conformance to the subset of primitives applicable to the drone profile (`move_to`, `hover`, `wait`, `wait_for`, `scan`, `capture`, `report`, plus `dock` for landing-pad services, plus `measure` if the airframe carries the relevant sensor). `grasp`, `release`, and `detect` (in the object-pickup sense) are not part of the drone profile in v1.0 — they remain available in the spec but a drone runtime is not required to implement them.

Both runtimes need their conformance `CONFORMANCE.md` updated when implementation completes.

### Conformance suite changes

[`/conformance/`](../../conformance/) will, when implementation starts (Phase 3 per the manifesto, possibly earlier as the suite grows opportunistically), include:

- **Positive tests** per primitive: given a valid manifest, a program using the primitive executes per the documented semantics in a simulated environment.
- **Negative tests** per primitive: programs that violate each documented safety check are rejected by the validator (and execution never begins).
- **End-to-end** tests reusing [`/examples/home/red-mug.urml.yaml`](../../examples/home/red-mug.urml.yaml). On Implementation, that example becomes the first canonical pass.

## Backward Compatibility

This is the initial vocabulary. Nothing prior to break.

The vocabulary is declared `0.1.0` per the per-artifact semver scheme; pre-`1.0` breaking changes are allowed but should be made through RFCs that update this one.

## Drawbacks

- **Twelve is more than the manifesto's seed of seven.** Four universals (`wait`, `wait_for`, `measure`, `report`) and `capture` were added because the seed underspecified what every program needs in practice. The case for staying at seven is to test whether composition can cover the gap; the case for twelve (chosen) is that the gap is broad enough that the long-tail cost of writing the same composition repeatedly across profile examples outweighs the cost of four extra primitives.
- **`dock(service: ...)` is profile-extensible**, which means the validator's enum check depends on the active profile set. Modest validator complexity. Justified because consolidating into one primitive is much better than ten separate `dock_to_charge`, `dock_to_swap_battery`, etc.
- **`hover` and `wait` overlap conceptually for some platforms.** A satellite "waits" by station-keeping. A wheeled robot "hovers" trivially. The distinction is whether the runtime is *required* to actively maintain position. The line is bright in practice (drones, underwater vehicles vs. ground robots), but it does create a small surface where authors may pick the wrong verb. Profile constraints (drone profile rejects `wait` in flight) mitigate.
- **`capture`'s artifact handles introduce a new value type** that subsequent primitives may want to consume (e.g., `detect` over a captured photo, `report` with attachments). The full type system for handles lives in the Layer-3 RFC; until then, handles are treated as opaque tokens.
- **`scan` is doing a lot of work** (pattern, area, sensor, media). Risks becoming a god-primitive. Counter: the alternative (multiple narrower primitives like `scan_aerial`, `scan_industrial_kit`) duplicates the area/pattern logic across profiles; one parameterized primitive is leaner.

## Alternatives Considered

1. **Manifesto seeds only (seven).** Rejected: the four universals (`wait`, `wait_for`, `measure`, `report`) are not optional in practice. Every program needs at least one. Forcing authors to compose them out of nothing is a tax with no benefit; including them is a single small expansion.
2. **Larger set including `follow`, `pick_up`, `find`, `turn`.** Rejected: each is composable from the twelve (`follow` = `detect + move_to($target)` in `retry`; `pick_up` = `detect + grasp`; `find` = `scan + detect`; `turn` = `move_to(pose: {rotation: ...})`). Adding them sets a precedent that any common composition deserves a primitive — the manifesto cap dissolves.
3. **Collapse `measure` into `detect`.** Rejected: `detect` returns an object reference (`{class, pose, attributes}`); `measure` returns a scalar value (`{value, unit}`). Different output types, different downstream uses, different sensor pathways.
4. **`dock` without a `service` argument; charge via composition (`dock + wait_for(battery: full)`).** Rejected: composition cannot express the atomicity of "leave the dock the instant charge crosses 80%" — a `wait_for` followed by `move_to` introduces a planning gap during which the substrate is no longer commanded to charge or to leave. The `service` + `until` combination keeps the atomicity inside the substrate.
5. **Generic `actuate` primitive that takes a verb as data** (`actuate(verb: grasp, args: ...)`). Rejected: this is a step toward "URML is a programming language with reflective calls," which is exactly what URML is not. Statically checkable typed verbs are the safety mechanism.
6. **No `capture` primitive; treat media as a side effect of `scan`.** Rejected: many use cases want a single photo at a specific moment, with no area-survey semantics. Forcing them through `scan` over a one-point area is awkward and obscures intent.
7. **Add `assert` as the 13th primitive.** Currently OPEN. The case for: an explicit safety-abort verb readable in any program (`- assert: condition: ...`). The case against: Layer-3's `on_error: abort_and_report` covers the same ground with less surface, and `assert` invites authors to do logic in Layer 2 that belongs at Layer 3 (or in the validator's static checks). **Provisional choice: do not add.** If the first six months of Phase 1 produce concrete use cases that `on_error` cannot express, revisit in RFC-0009 or later.

## Prior Art

The vocabulary draws on, and deliberately diverges from, several existing systems.

- **Behavior trees** (BT.CPP, Skiros, py_trees) — informs the Layer-3 composition operators more than the primitives themselves; behavior-tree leaves are typically domain-specific actions with no shared vocabulary across users.
- **PDDL operators** — give the right shape (verb + typed arguments + preconditions + effects) but PDDL is a *planning* language; URML is an *execution* language with no planner required.
- **AUTOSAR Adaptive service interfaces** — show how a substrate-neutral interface can be specified and validated; URML's pose-with-frame convention takes notes from AUTOSAR's coordinate-frame discipline.
- **ROS 2 Nav2 action set** — `NavigateToPose`, `Spin`, `BackUp`, `Wait`, `DockRobot` are the closest substrate-level neighbors to URML's mobility/composition primitives; URML's intent layer sits above these.
- **MoveIt 2 task pipelines** — manipulation reference; the `grasp` / `release` semantics here are deliberately coarser than MoveIt 2's task constructor, because URML is intent, not trajectory.
- **MAVLink `MAV_CMD_*` set** — drone reference; substrate-level neighbors for `move_to` (waypoint), `hover` (loiter), `dock`/`land`, `capture` (digital camera control).
- **OPC UA Robotics Companion Specification** — industrial reference; the manifest-level `Method` surface here informs the dock/manipulation service contracts.
- **PDDLStream, BehaviorTree.CPP "subtree" abstractions** — for how composable behaviors are bound; URML chooses static composition over runtime-decided subtree selection.

## Unresolved Questions

1. **Variable typing across primitives.** The `store_as` / `$variable` pattern works syntactically, but the canonical *type system* — what shape `detect` produces vs. what shape `capture` produces vs. what `grasp(target: $name)` requires — is Layer-3 RFC territory. This RFC names the bindings; RFC-0003 (planned, Layer-3 composition grammar) will specify the type system, and a small follow-up to this RFC may tighten signatures once that lands.
2. **Streaming and unbounded actions.** `capture(media: stream)` and continuous recording are not in this RFC. The right place to resolve them is the Layer-3 composition RFC, where the open-ended action semantics live.
3. **Profile-extensible enums.** `dock(service: ...)` and `wait_for(condition.input: ...)` use enums that profiles extend. The exact registration mechanism (declared in the profile spec, validated by the validator, surfaced in the LLM prompt contract) is a small follow-up; the principle is settled here.
4. **The error vocabulary.** Each primitive lists named errors (`target_unreachable`, `force_exceeded`, `not_found`, ...). These should be enumerated as a closed set in a small companion document, because the LLM bridge's revision flow needs them named. Targeted for a small follow-up RFC after RFC-0003.
5. **Media handle lifecycle.** `capture` produces handles; `report` consumes them. Who owns the bytes? When are they garbage-collected? Deployment configuration is the right place to answer; the spec just says "handles are opaque tokens whose backing is deployment-controlled."
6. **`assert` revisitation.** As noted in Alternatives: provisional choice is no `assert`. Concrete Phase-1 use cases may flip this.

## Implementation Note

This RFC reaches **Accepted** when it is merged. It reaches **Implemented** when all of the following land:

1. **Spec document** at `/spec/layer-2-primitives/v0.1.0.md` containing the normative text for each primitive (transcribed from this RFC's Detailed Design).
2. **Validator implementation** in `/reference/validator/` that runs all four validation passes per primitive and produces the structured error format the LLM bridge consumes.
3. **ROS-2 runtime implementation** in `/reference/ros2-runtime/` that executes the twelve primitives per their documented semantics in a simulated environment (Gazebo, or a profile-appropriate alternative).
4. **Conformance tests** in `/conformance/` — at minimum, the positive and negative tests enumerated per primitive in Detailed Design.
5. **Example update** at `/examples/home/red-mug.urml.yaml` — the header comment is amended to mark the example now validatable.

These five are not required to land in a single PR — they may be sequenced as separate PRs, each referencing this RFC. The RFC stays at `Accepted` until all five are done; only then does it move to `Implemented`.

The expected sequence:

- **Month 1 of Phase 1:** Spec document + validator.
- **Month 2:** ROS-2 runtime implementation for the home-profile subset.
- **Month 3:** Conformance tests + example update; RFC moves to Implemented.

The PX4 runtime's subset implementation tracks the drone profile RFC (a separate RFC, planned as RFC-0005 or thereabouts), not this one.

**Status — Implemented (2026-05-17).** All five criteria are met: (1) the
normative spec document [`spec/layer-2-primitives/v0.1.0.md`](../../spec/layer-2-primitives/v0.1.0.md)
covers all seventeen primitives (twelve core + five profile-scoped); (2) the
five-pass validator; (3) the ros2-runtime implements all seventeen; (4) the
conformance suite carries positive and negative fixtures per primitive; (5)
the runnable examples cover every primitive. The cell-by-cell proof is
[`docs/spec-coverage.md`](../spec-coverage.md). The vocabulary moved faster
than the Phase-1 month-by-month sequence above anticipated; the sequence is
left as written for the decision record.

## Appendix A: Prior-art mapping

This appendix grounds the substrate-neutrality claim in evidence. For each of the twelve core primitives, the table below names the closest existing equivalent in six widely-used robot programming systems. A cell of `—` means the substrate has no direct equivalent at the same level of abstraction — either the concept is irrelevant on that substrate (drones don't grasp) or it is delegated to a vendor-specific extension URML's spec doesn't try to absorb.

The substrates surveyed:

- **ROS 2** — via [Nav2](https://navigation.ros.org/) (mobility) and [MoveIt 2](https://moveit.picknik.ai/) (manipulation). The largest open-source robotics community; default for research, home robots, and many industrial AMRs.
- **PX4 / MAVLink** — the dominant open-source autopilot for small UAS. [`MAV_CMD_*`](https://mavlink.io/en/messages/common.html) names below refer to MAVLink common-message enumerations.
- **OPC UA Robotics** — the [OPC UA Companion Specification 40010](https://reference.opcfoundation.org/Robotics/) for industrial robot integration. Vendor-neutral, increasingly adopted by industrial cells.
- **KUKA KRL** — KUKA Robot Language; runs on KRC controllers. Verbs below are standard KRL 8.x; `$IN[]`/`$OUT[]` refer to digital I/O addressing.
- **ABB RAPID** — ABB's robot programming language; runs on IRC5 / OmniCore controllers. Verbs below are standard RAPID.
- **IEC 61131-3 (PLC)** — the international standard for industrial automation programming, with motion via [PLCopen Motion Control](https://plcopen.org/technical-activities/motion-control) function blocks (`MC_*`). The "no robot, just automation" baseline.

### Summary table

| URML primitive | ROS 2 (Nav2 + MoveIt 2) | PX4 / MAVLink | OPC UA Robotics | KUKA KRL | ABB RAPID | IEC 61131-3 (PLC) |
|---|---|---|---|---|---|---|
| `move_to` | `NavigateToPose`; `MoveGroup.plan`+`execute` | `MAV_CMD_NAV_WAYPOINT`; offboard setpoint | `MotionDevice.MoveTo()` | `PTP`, `LIN`, `CIRC` | `MoveJ`, `MoveL`, `MoveC` | `MC_MoveAbsolute`, `MC_MoveLinearAbsolute` |
| `dock` | Nav2 `DockRobot` (Iron+) | `MAV_CMD_NAV_LAND` + service | `MotionDevice.Dock()` (vendor) | vendor routine + `WAIT FOR` | vendor routine + `WaitDI` | vendor sequence |
| `hover` | position-hold behavior | `MAV_CMD_NAV_LOITER_TIME`, `_LOITER_UNLIM` | position-hold mode | `WAIT SEC` w/ servo-on | implicit between moves | `MC_Halt` + position-hold |
| `wait` | simple sleep / no-op behavior | — (not used in flight) | idle state | `WAIT SEC <n>` | `WaitTime <n>` | `TON` timer |
| `wait_for` | subscription w/ predicate | param-monitor; telemetry event | node subscription w/ filter | `WAIT FOR <signal>` | `WaitDI`, `WaitUntil` | input watch + `TON` |
| `grasp` | MoveIt 2 + gripper action | — (rare on drones) | `Gripper.Grasp(force)` | `$OUT[]` pneumatic, `OPENC`/`CLOSEC` servo | `SetDO`, `GripperCommand` (servo) | `Q_Gripper` boolean, custom FB |
| `release` | MoveIt 2 release / gripper open | `MAV_CMD_DO_SET_SERVO`, `_PARACHUTE` (payload) | `Gripper.Release(mode)` | opposite of grasp | opposite of grasp | opposite of grasp |
| `detect` | perception pipeline + custom action | onboard companion + MAVLink relay | `Perception.FindObject()` (vendor) | `KUKA.VisionTech`, external I/O | `Integrated Vision`, external I/O | external vision via fieldbus |
| `scan` | path follower + per-waypoint perception | mission upload + `MAV_CMD_DO_DIGICAM_CONTROL` | `Perception.RunScan()` (vendor) | path + vision triggers | path + vision triggers | sequence + vision triggers |
| `measure` | one-shot subscription | telemetry read | `Sensor.Read()` | read `$IN[]` / Profinet | read `<signal>` | read `AI_*` / fieldbus |
| `capture` | `image_transport` (photo); `rosbag2` (video) | `MAV_CMD_DO_DIGICAM_CONTROL`; `_VIDEO_START_CAPTURE` | `Camera.TakeImage()`, `StartRecording()` | — (external vision system) | — (external vision system) | — (external vision system) |
| `report` | publish on configured topic | `STATUSTEXT`; MAVLink FTP for attachments | write configured node; file-transfer service | `WRITE` to FTP; OPC UA bridge | `TPWrite`, `WriteVar`, file I/O | HMI write; OPC UA Server FB |

### Per-substrate interpretation notes

#### ROS 2 (Nav2 + MoveIt 2)

The cleanest mapping. Every primitive has at least one direct ROS 2 counterpart. URML's reference runtime is named first because the impedance mismatch is smallest. Two specifics:

- **`detect` is the loosest mapping.** ROS 2 has no canonical perception interface — every project rolls its own. The URML reference runtime will ship a default perception adapter (likely backed by `vision_msgs`/`detectnet_ros`) and a documented contract so deployers can swap in their own.
- **`scan` is not a single ROS 2 action.** Nav2 doesn't ship a "scan a polygon with overlap and trigger the camera at each waypoint" primitive; the reference runtime composes it.

#### PX4 / MAVLink

Covers the **drone subset** of URML well. Three primitives are out of scope on this substrate:

- **`grasp` / `release`** — gripper-equipped drones exist but are rare; the drone profile does not require them. The reference runtime declares partial conformance.
- **`wait`** — not used in flight (a drone never *passively* waits in air); `hover` is the airborne analogue.

`scan` maps especially cleanly: MAVLink missions are sequences of waypoints with per-waypoint commands, exactly the structure `scan` describes.

#### OPC UA Robotics

The most architecturally sympathetic substrate. OPC UA Robotics organizes a robot as a tree of typed services (`MotionDevice`, `Gripper`, `Perception`, `Camera`, `Sensor`), each with methods — close to URML's primitive-per-capability model. Many cells in the table are method names rather than command codes.

Vendor extensions in OPC UA Robotics are first-class (the spec is explicit about extensibility), so profile-specific URML primitives map naturally to vendor-extended OPC UA methods.

#### KUKA KRL

Industrial-arm-shaped. The mobility table cells are about manipulator motion, not mobile-base motion (KUKA KMR — the KRC4-controlled mobile manipulator — uses additional KRL extensions). `WAIT SEC` and `WAIT FOR <signal>` provide `wait`/`wait_for` cleanly; `$IN[]` / `$OUT[]` digital I/O addressing covers the gripper and signal paths.

Native perception is essentially absent: KRL programs delegate vision to `KUKA.VisionTech` or external systems via Profinet/Ethernet. URML's `detect`/`scan`/`capture` map to *external* systems on this substrate.

#### ABB RAPID

Industrial-arm-shaped, very similar in shape to KRL. RAPID's `MoveJ`/`MoveL`/`MoveC` triplet mirrors KRL's `PTP`/`LIN`/`CIRC`. `WaitTime` and `WaitDI`/`WaitUntil` map directly. Gripper I/O via `SetDO`/`GripperCommand` (the latter for servo-controlled grippers).

Like KRL, native perception is external — `Integrated Vision` or third-party systems via fieldbus.

#### IEC 61131-3 (PLC)

The "no robot, just automation" baseline. Most cells here are PLCopen Motion Control function blocks (`MC_*`) for axis-level motion. Strikingly little perception or media capture happens at this layer; in industrial cells where the PLC is the top-level controller, URML's perception primitives live in adjacent systems and PLCs consume their results via fieldbus.

The presence of cleanly-mappable cells here (motion, wait, simple I/O) and the *absence* of perception/capture is itself useful evidence: URML's perception primitives are correctly *above* the substrate level, exactly where the intent layer should sit.

### What the table reveals

Three observations:

1. **All twelve primitives map cleanly onto at least four of the six substrates.** No primitive is "ROS-only." This is concrete evidence — not just assertion — that the substrate-neutrality acid test is satisfied.

2. **`capture` is missing from three substrates** (KRL, RAPID, IEC 61131-3). On those, media capture is delegated to external systems. The drone profile and the home-with-cameras case work; the pure-PLC industrial case treats `capture` as an external-service primitive. This is acceptable: the URML manifest declares the camera regardless of which controller it is wired to; the validator's job is to check the declaration, not the wiring.

3. **No primitive forces a re-design.** Every gap is either an out-of-scope case (drones don't grasp) or a substrate-extension question (OPC UA companion extensions, KRL/RAPID external vision). Nothing in the table is "URML primitive X cannot be implemented at all on substrate Y."

If a future substrate produces a row where five of twelve are `—`, that substrate is genuinely *out of URML's reach* and we should be honest about it rather than warp the spec. Today, no surveyed substrate is in that category.

## Appendix B: Simulator and emulator availability

URML's substrate-neutrality claim is hollow unless we can *demonstrate* programs running across substrates. This appendix names the simulators each substrate offers, the licensing posture, and a one-line judgement on demo readiness.

| Substrate | Simulator | License | Demo readiness |
|---|---|---|---|
| **ROS 2** | [Gazebo (Ignition/modern)](https://gazebosim.org/) | Apache 2.0 | **High.** Mature, integrates natively with ROS 2; canonical for TurtleBot 4 home demos. |
| ROS 2 | [NVIDIA Isaac Sim](https://developer.nvidia.com/isaac-sim) | Free for non-commercial; commercial licensing required | **High** if you have an NVIDIA GPU; photorealistic, great for video. |
| ROS 2 | [Webots](https://cyberbotics.com/) | Apache 2.0 | **High.** Cross-platform, lighter than Gazebo, good for education. |
| **PX4 / MAVLink** | [PX4 SITL + Gazebo](https://docs.px4.io/main/en/simulation/) | BSD-3-Clause + Apache 2.0 | **High.** Official PX4 toolchain; the industry-standard drone-sim path. |
| PX4 / MAVLink | [jMAVSim](https://github.com/PX4/jMAVSim) | BSD-3-Clause | **Medium.** Lightweight, deprecated upstream in favour of Gazebo; still useful for quick smoke tests. |
| **OPC UA Robotics** | [open62541](https://www.open62541.org/) + simulated devices | MPL 2.0 | **Medium.** Open-source OPC UA stack; no turnkey "robotics" simulator — you wire a device sim against an OPC UA endpoint. |
| OPC UA Robotics | Vendor sims (B&R Automation Studio, etc.) | Per-vendor; mostly commercial | **Low.** Vendor-locked, not portable across deployments. |
| **KUKA KRL** | [RoboDK](https://robodk.com/) | Free version (limited); commercial paid | **Medium.** Third-party, simulates KUKA + many vendors; free tier sufficient for short demos. |
| KUKA KRL | KUKA.OfficeLite | Commercial | **Low (for us).** Most accurate KRL emulation but costs and requires KUKA licensing. |
| KUKA KRL | KUKA Sim Pro | Commercial | **Low (for us).** Official sim; expensive. |
| **ABB RAPID** | [ABB RobotStudio](https://new.abb.com/products/robotics/robotstudio) | Free for non-commercial (post-2021) | **High.** Vendor-official, polished, free for the use case URML cares about. |
| ABB RAPID | RoboDK | Free version (limited); commercial paid | **Medium.** Same as KUKA — third-party, multi-vendor. |
| **IEC 61131-3 (PLC)** | [CODESYS](https://www.codesys.com/) | Free Development System + simulator | **Medium-High.** Free, runs the simulated PLC against a virtual machine; integrates with Gazebo via OPC UA bridge. |
| IEC 61131-3 (PLC) | [Beremiz](https://beremiz.org/) | LGPL | **Medium.** Fully open-source IDE + sim; smaller community than CODESYS. |

### Demo-readiness summary

Three substrates are **demo-ready today** with free, mature, polished simulators:

- **ROS 2** via Gazebo. The Phase-1 home demo target.
- **PX4** via PX4 SITL + Gazebo. The Phase-2 drone demo target — and the source of the *flagship* public-launch video.
- **ABB RAPID** via RobotStudio. The cleanest industrial demo target for Phase 3.

Two substrates are **demo-feasible with caveats**:

- **KUKA KRL** via RoboDK (free tier sufficient for short demos; full features require a paid tier).
- **IEC 61131-3** via CODESYS (free Development System + simulator; pair with Gazebo through an OPC UA bridge for a more compelling visual).

One substrate is **demo-blocked without a vendor partnership**:

- **OPC UA Robotics** lacks a turnkey simulator. Demoing across an OPC UA endpoint requires wiring a device sim against an OPC UA stack — feasible (open62541 + a Gazebo-driven device facade) but more engineering than a Phase-1/2 demo can absorb. Defer to Phase 3+ or a vendor partnership.

The detailed mapping from these simulators to specific Manifesto-roadmap demos lives in [`docs/demo-roadmap.md`](../demo-roadmap.md).

## Self-review (Phase 0)

The author has reviewed against the checklist in [`0001-rfc-process.md`](0001-rfc-process.md) §Self-review:

- [x] The **Summary** alone tells a reader what is being proposed.
- [x] The **Motivation** is grounded in concrete needs: Phase 1 is blocked without this RFC.
- [x] The **Detailed design** names every affected spec document and reference component.
- [x] At least one **alternative** (seven; six others; the `actuate` reflective form) is genuinely considered.
- [x] **Drawbacks** lists at least one real downside per area of the design (size, dock complexity, hover/wait overlap, handle typing, scan god-primitive risk).
- [x] **Backward compatibility** is honest: nothing to break.
- [x] Every primitive includes both a ROS-2 implementation sketch and a non-ROS implementation sketch (substrate-neutrality acid test).
- [x] The **implementation note** explains how this lands, not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed nothing in this RFC violates it.
