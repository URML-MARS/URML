# Drone Profile (civilian)

**Status:** Draft (v0.1)
**Targets:** URML v0.1
**Created:** 2026-05-13

The second URML profile to ship: small civilian unmanned aircraft used for inspection, photography, mapping, and similar non-combat tasks. Constrains and extends the [twelve core primitives](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) for outdoor flight in regulated airspace, defines a default safety envelope appropriate to flight (altitude cap, geofence, weather thresholds), and binds the profile's compliance posture to the [bundled US-federal policy](../../../docs/rfcs/0004-compliance-policy.md) — which the drone profile is the most directly exposed to (FCC Covered List entries are drone-heavy).

> **Scope note.** This profile covers **civilian** small unmanned aircraft only: inspection, photography, mapping, agriculture-adjacent surveying, hobbyist flight, search-and-rescue support, and similar non-combat uses. Per [`CLAUDE.md`](../../../CLAUDE.md) §What Claude Should Never Do and [`MANIFESTO.md`](../../../MANIFESTO.md) §Scope, the canonical URML organization restricts its own development to civilian, consumer, educational, industrial, and research domains. Profiles outside that scope are not maintained in this repository.

## Application domain

Small civilian unmanned aircraft (quadcopters, hex/octocopters, fixed-wing, VTOL) used for tasks that benefit from low-altitude aerial perspective. The defining shape of the drone profile is *outdoor flight in regulated airspace, where altitude, geofencing, and weather constraints are first-class primitives in the safety envelope*.

## In scope

- **Inspection.** Roofs, towers, solar arrays, wind turbines, bridges, building exteriors. The canonical drone scenario in [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Drone: the citizen inspector*.
- **Mapping and photogrammetry.** Serpentine `scan` patterns with declared overlap and ground sample distance.
- **Aerial photography.** Single-shot and orbiting captures via `capture(media: photo | video)` with altitude-aware framing.
- **Agriculture-adjacent surveying.** Crop-health imagery, area mapping.
- **Hobbyist and educational flight.**
- **Search-and-rescue support.** Subject-detection over declared search areas. (The canonical search-and-rescue *profile* is a v1.x stretch; basic SAR support fits inside the drone profile at v1.0.)

## Out of scope

- **Beyond-visual-line-of-sight (BVLOS) operations** at v1.0. The default envelope assumes the operator can see the drone or has authorization-equivalent observation in place; BVLOS adds regulatory and safety requirements URML defers until a later version.
- **Indoor or transitional indoor/outdoor flight at v1.0.** Possibly a stretch goal; pure outdoor flight first.
- **Heavy-lift cargo / aerial-delivery profile-level features at v1.0.** Adjacent and likely to become its own profile.
- **Anything outside the canonical organizational scope.** See the scope note above.

## Profile-required Layer-1 manifest fields

A drone-profile-conformant capability manifest **must** declare:

- **`mobility`** with `drive_type` in (`multirotor`, `fixed_wing`, `vtol`). A drone with `drive_type: differential` is rejected by the validator (it's a wheeled robot wearing the wrong profile).
- **`mobility.service_ceiling`** (the aircraft's own maximum altitude capability, in meters). Required; the validator rejects drone-profile manifests without it. The envelope's `max_altitude` is bounded by this value.
- **`mobility.station_keeping: true`** for `multirotor` and `vtol` drones. Fixed-wing drones omit this (they cannot hover without forward motion).
- **`perception.cameras`** — at least one camera. Most drone use cases are vision-driven; a drone manifest without a camera is permitted but rejects programs that use `capture` or `scan(media: photo|video)`.
- **`declared_locations`** in a geographic frame — typically WGS-84 lat/lon/alt poses. Geographic frame declarations are profile-extended (see *Coordinate frames* below).

A drone-profile manifest **should** declare:

- **`provenance:`** per [RFC-0004](../../../docs/rfcs/0004-compliance-policy.md). **The drone profile is the most directly exposed to US federal regulation** — DJI and Autel are on the FCC Covered List effective 2025-12-23; Hesai LiDAR is restricted by FY26 NDAA §164. A drone manifest without provenance can still validate technically, but the deployer cannot claim NDAA-compliance for any federal-procurement context.
- **`mobility.endurance`** (battery time at hover and at cruise) when known — informational; the envelope's `max_flight_duration` cross-checks against it.

A drone-profile manifest **must not** declare:

- **`manipulation`** — drones in v1.0 do not have grippers. Manipulation drones are a v1.x stretch and live outside this profile until specified.
- **`docking_stations`** with non-`park` services. Drones land; they do not dock to a charging station with `charge` semantics in v1.0. (Some commercial drone landing pads do offer charge; profile extension.)

## Coordinate frames

A drone-profile manifest typically declares three frames:

- **`wgs84`** — the WGS-84 geodetic frame. `pose: { x: <longitude>, y: <latitude>, z: <altitude AMSL m> }`. Used for absolute positions and geofences.
- **`agl`** — Above Ground Level frame. `pose.z` is altitude above the terrain at the (x, y) position. The substrate is responsible for the terrain model.
- **`body`** — drone-local body frame, used for relative motions during inspection.

The validator does not (in v0.1) verify transform chains across geographic frames. The substrate handles WGS-84 ↔ AGL conversions. Programs declaring `pose.z` against `frame: agl` are accepted iff `agl` is in `manifest.frames`.

## Default safety envelope

A drone operates in **regulated airspace shared with other aircraft and the public on the ground**. The default safety envelope is the most opinionated of the v1.0 profiles:

```yaml
envelope_version: "0.1"
deployment_id: <free-form>
description: <free-form>

# Numeric caps. Strictest-wins against the manifest's declared maxima.
max_velocity: 15.0                 # m/s; quad cruise default
max_altitude: 120.0                # m AGL; ~400 ft, FAA Part 107 default for uncertified small drones.
                                   # MUST be at or below the local civil aviation authority's cap.
max_payload: null                  # kg; null means use manifest default
max_flight_duration: 1500          # s; 25 minutes default

# Spatial constraints.
geofences: []                      # list of polygons. The drone REFUSES to fly outside any declared polygon.
                                   # Default-empty means no geographic restriction beyond max_altitude;
                                   # deployments are expected to supply at least one polygon.
people_occupancy_zones: []         # list of polygons. The drone REFUSES to scan or hover over these
                                   # without an explicit manifest override.

# Weather thresholds (the substrate refuses takeoff or returns to home if exceeded).
weather:
  max_wind_speed_m_s: 10.0         # ~22 mph; quad limit
  min_visibility_m: 1500.0         # FAA VLOS-equivalent
  precipitation_allowed: false

# Behavioural defaults.
link_loss_policy: return_to_home   # other options: hover, land_now
emergency_stop_event: emergency_stop
```

A reference envelope ships at [`reference/validator/tests/fixtures/envelopes/drone_default.yaml`](../../../reference/validator/tests/fixtures/envelopes/drone_default.yaml) (planned; not yet committed as of profile v0.1 Draft state).

### Mandatory invariants

- **`max_altitude` is at or below the local civil aviation authority's cap.** v0.1 does not enforce this against any authority's data; the deployer is responsible. Future RFC may add a jurisdiction-aware altitude-cap policy file.
- **The drone refuses to fly outside any declared geofence polygon.** Runtime invariant; the validator rejects programs whose declared targets fall outside.
- **No `scan` or `hover` over declared people-occupancy zones** without an explicit manifest override.
- **Link loss triggers the declared `link_loss_policy`.** The validator does not (in v0.1) verify the substrate honors this; it is a runtime contract.

## Layer-2 primitives this profile adds

[RFC-0002 §Detailed Design](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) authorizes per-profile primitive additions. The drone profile adds three: `take_off`, `land`, and `return_to_home`. Each passes the substrate-neutrality acid test below.

### `take_off`

Begin flight: ascend from the current ground position to a declared altitude.

**Signature:**

```yaml
- take_off:
    altitude: <distance>         # required; meters; frame inherited from manifest (default: agl)
    climb_rate: <speed>          # optional; m/s; substrate default if omitted
```

**Semantics.** The drone executes its substrate-specific takeoff procedure (arming, motor spin-up, ascent) and is considered airborne when the declared altitude is reached. Programs that exceed the envelope's `max_altitude` are rejected at validation time, not runtime.

**Capability requirements (Layer 1):** `mobility.drive_type` in (`multirotor`, `vtol`); `mobility.service_ceiling >= altitude`; the appropriate aerial frame (`agl` or `wgs84`) declared in `manifest.frames`.

**Safety-envelope checks:** declared `altitude` is at or below the strictest of (`manifest.mobility.service_ceiling`, `envelope.max_altitude`); the current weather (if available to the substrate at validation time — typically not) does not exceed declared thresholds.

**Variable bindings:** `take_off` does not produce a result.

**ROS-2 implementation sketch:** publish on the `mavros/cmd/takeoff` service or equivalent; alternatively, the `arm` + `takeoff` sequence via `mavros/cmd/arming` and `mavros/cmd/takeoff`.

**Non-ROS implementation sketch:** PX4 — `MAV_CMD_NAV_TAKEOFF` MAVLink command. OPC UA — `Flight.TakeOff(altitude)` method on the flight service.

### `land`

End flight: descend from current position to a declared landing location.

**Signature:**

```yaml
- land:
    at: <location | pose> | null # optional; default: current (x, y) at ground level
    precision: standard | precise  # optional; default: standard
```

**Semantics.** The drone executes its substrate-specific landing procedure at the declared location (or directly below current position if `at` is omitted). `precision: precise` requests fiducial-aided precision landing if the substrate supports it; `precision: standard` is GPS-aided. The drone is considered grounded when the substrate reports motors stopped.

**Capability requirements (Layer 1):** `mobility.drive_type` in (`multirotor`, `vtol`, `fixed_wing`); fixed-wing landing requires a declared runway pose. The `at` location, if named, must resolve against `manifest.declared_locations`.

**Safety-envelope checks:** the declared landing location is within the geofence; declared people-occupancy zones do not intersect the landing approach.

**Variable bindings:** `land` does not produce a result.

**ROS-2 implementation sketch:** `mavros/cmd/land` service. For precision landing, layer the `apriltag_ros` (or equivalent) detector before issuing the land command.

**Non-ROS implementation sketch:** PX4 — `MAV_CMD_NAV_LAND` MAVLink command; `MAV_CMD_NAV_LAND_LOCAL` for body-frame positioning. OPC UA — `Flight.Land(location)` method.

### `return_to_home`

Abort current flight intent and return the drone to its declared home location, then land. The drone profile's canonical safety primitive: a program author can always reach for `return_to_home` to gracefully terminate.

**Signature:**

```yaml
- return_to_home:
    speed: <speed>               # optional; m/s; substrate default if omitted
    altitude: <distance>         # optional; m; substrate's RTH altitude if omitted
```

**Semantics.** The drone aborts the current flight intent, climbs to the declared (or substrate-default) RTH altitude, navigates to the declared home location, descends, and lands. The substrate is responsible for the procedure; URML expresses the intent.

**Capability requirements (Layer 1):** `mobility.drive_type` in (`multirotor`, `vtol`, `fixed_wing`); a declared location named `home` in `manifest.declared_locations` (substrate may use `home` semantics regardless of name; the convention reduces ambiguity).

**Safety-envelope checks:** declared RTH altitude is at or below `envelope.max_altitude` and `manifest.mobility.service_ceiling`.

**Variable bindings:** `return_to_home` does not produce a result. After this primitive completes, the drone is grounded; subsequent flight primitives require an explicit `take_off`.

**ROS-2 implementation sketch:** `mavros/cmd/return_to_launch` service.

**Non-ROS implementation sketch:** PX4 — `MAV_CMD_NAV_RETURN_TO_LAUNCH` MAVLink command. OPC UA — `Flight.ReturnHome()` method.

## Layer-2 primitives this profile constrains

### `move_to`

- **Altitude is mandatory.** A `move_to` without an altitude (either `pose.z` set, or `frame: agl|wgs84` with no z, or the convenience `altitude:` field for drone-profile programs) is rejected by the validator with a profile-specific argument-typing error. Ground robots do not have to declare altitude; drones do.
- **Frame must be aerial.** Programs declaring `frame: map` (a ground-robot frame) are rejected unless `map` happens to be declared as aerial in the manifest's frames list with the appropriate semantics.
- **Velocity is bounded by the envelope's `max_velocity`, not the manifest's typical max** — drone manifests typically declare maximum airframe-capable velocities that exceed reasonable mission velocities; the envelope tightens.

### `hover`

- **Station-keeping is mandatory.** Drones with `mobility.station_keeping: false` (e.g., fixed-wing without VTOL) reject `hover` at Pass 2.
- **Duration is bounded by `envelope.max_flight_duration`.** A `hover(duration: 30m)` against an envelope with `max_flight_duration: 1500` (25 minutes) is rejected.

### `scan`

- **Altitude argument is REQUIRED for drone-profile scans.** Per RFC-0002's `ScanArgs`, the `altitude` field is optional in the core; the drone profile makes it required. Programs omitting it are rejected.
- **Scan area must be within the geofence.** The validator (in v0.2; v0.1 is named-location-only) cross-checks the polygon vertices against declared geofences.
- **Sampling overhead.** `scan(pattern: serpentine, overlap: 0.3)` over a polygon of area A at altitude h, with a camera of footprint W × H, produces approximately `A / (W * (1 - overlap))` waypoints. The substrate decides whether this exceeds runtime budgets; the validator does not.

### `wait`

- **`wait` is PROHIBITED in flight.** Unlike the home profile, drones in air must `hover` (active station-keeping) rather than `wait` (passive). A `wait` step between `take_off` and `land` is rejected by the validator with a profile-specific composition error. On the ground (before takeoff or after land), `wait` is permitted.

### `detect`

- **Subject detection over people-occupancy zones requires explicit manifest override.** A `detect(object: person)` over a polygon declared as a people-occupancy zone is rejected unless the manifest has an `override_people_detection: true` flag (planned; not in v0.1). v0.1 enforces only the spatial constraint at scan/hover; subject detection follows in a tightening RFC.

### `capture`

- **Video capture over declared people-occupancy zones requires the same explicit override.** Privacy posture; the drone profile is opinionated.
- **Photo metadata SHOULD include GPS coordinates from the WGS-84 frame.** v0.1 records intent only; runtime adapters are expected to embed coordinates in the EXIF or equivalent.

## Reference runtime

[`/reference/px4-runtime/`](../../../reference/px4-runtime/) is the second reference runtime and targets this profile. It is part of the [Core Commitment](../../../CORE_COMMITMENT.md). The PX4 runtime ships in Phase 2 per the [manifesto roadmap](../../../MANIFESTO.md) §Roadmap Snapshot.

## Compliance policy alignment

**The drone profile is the most directly exposed to US federal compliance enforcement.** Several reasons:

- **FCC Covered List entries are drone-heavy.** DJI and Autel — the two largest civilian drone vendors — were added effective 2025-12-23 and block new equipment authorizations. A manifest declaring `vendor: dji` on any component will reject under the bundled default policy with `policy.vendor_denied`.
- **FY26 NDAA §164 named Hesai LiDAR specifically.** Drone-mounted LiDAR for mapping and inspection is a common configuration; manifests declaring `vendor: hesai` on a LiDAR component reject.
- **Blue UAS / Green UAS lists.** The DIU maintains positive allow-lists of NDAA-compliant drones (~50 platforms as of early 2026). Future RFC may add a `urml_us_federal_blueuas.yaml` policy file that enforces explicit allow-list membership; v0.1 ships the deny-side only.

Deployments outside the US should override the default with their own policy. The EU AI Act conformity regime applies to AI-enabled drones; an `eu_ai_act_drone.yaml` overlay is a future RFC.

For drone-profile deployers inside the US, the practical guidance:

- Use the `red-mug.manifest.yaml` style of provenance declarations (US/JP/KR/EU origin for critical components) for federal-procurement contexts.
- The `--no-policy` escape hatch is appropriate for hobbyist deployments that do not interact with federal procurement; for any commercial drone-service deployment, leave the default policy active.

## Conformance points

When this profile reaches **Implemented** state, the conformance suite at `/conformance/fixtures/drone/` (not yet created) will include:

| Future fixture | What it tests |
|---|---|
| `01_inspect_roof_positive.yaml` | The canonical citizen-inspector scenario: take_off, scan(serpentine over roof polygon, altitude declared), capture(media: photo) per waypoint, return_to_home, land. Happy path. |
| `02_altitude_exceeded_rejected.yaml` | `take_off(altitude: 200)` against an envelope `max_altitude: 120` rejected with `envelope.altitude_exceeded`. |
| `03_geofence_breach_rejected.yaml` | `move_to` to a pose outside the declared geofence rejected. |
| `04_wait_in_flight_rejected.yaml` | A `wait` step between `take_off` and `land` rejected with a profile-specific error code (TBD; profile-prohibition codes are a follow-up RFC's design). |
| `05_dji_vendor_rejected.yaml` | A drone manifest declaring `vendor: dji` on a camera module rejected by the bundled default policy with `policy.vendor_denied`. |
| `06_hesai_lidar_rejected.yaml` | A drone manifest declaring `vendor: hesai` on a LiDAR component rejected with `policy.vendor_denied`. |
| `07_no_policy_hobbyist.yaml` | Same non-compliant manifest as 05, validated with `--no-policy` accepted (the escape hatch). |

Fixtures and the supporting `examples/drone/` programs follow in separate PRs once the PX4 runtime begins implementation.

## Related documents

- [`/docs/architecture.md`](../../../docs/architecture.md) §Profiles.
- [`/reference/px4-runtime/`](../../../reference/px4-runtime/) — the reference runtime (Phase 2 target).
- [`/spec/layer-1-hal/`](../../layer-1-hal/) — capability manifest reference.
- [`/spec/layer-2-primitives/`](../../layer-2-primitives/) — the core twelve.
- [`/docs/rfcs/0002-initial-primitive-vocabulary.md`](../../../docs/rfcs/0002-initial-primitive-vocabulary.md) — primitive vocabulary, including the §Profile-extensibility clause authorizing `take_off`/`land`/`return_to_home`.
- [`/docs/rfcs/0003-us-alignment.md`](../../../docs/rfcs/0003-us-alignment.md) — strategic alignment to US federal regulation (the drone profile is the most directly exposed surface).
- [`/docs/rfcs/0004-compliance-policy.md`](../../../docs/rfcs/0004-compliance-policy.md) — compliance policy mechanism.
- [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Drone: the citizen inspector*.
