# Drone Profile (civilian)

**Status:** Pre-draft. v1.0 target; second profile to ship. See roadmap in [`MANIFESTO.md`](../../../MANIFESTO.md).

> **Scope note.** This profile covers **civilian** small unmanned aircraft only: inspection, photography, mapping, agriculture-adjacent surveying, hobbyist flight, search-and-rescue, and similar non-combat uses. Per [`CLAUDE.md`](../../../CLAUDE.md) §What Claude Should Never Do and [`MANIFESTO.md`](../../../MANIFESTO.md) §Scope, the canonical URML organization restricts its own development to civilian, consumer, educational, industrial, and research domains. Profiles outside that scope are not maintained in this repository.

## Application domain

Small civilian unmanned aircraft (quadcopters, hex/octocopters, fixed-wing) used for tasks that benefit from low-altitude aerial perspective. The defining shape of the drone profile is *outdoor flight in regulated airspace, where altitude, geofencing, and weather constraints are first-class primitives in the safety envelope*.

## In scope

- **Inspection.** Roofs, towers, solar arrays, wind turbines, bridges, building exteriors. The canonical drone example in [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Drone: the citizen inspector*.
- **Mapping and photogrammetry.** Serpentine `scan` patterns with declared overlap and ground sample distance.
- **Aerial photography.** Single-shot and orbiting captures.
- **Agriculture-adjacent surveying.** Crop-health imagery, area mapping.
- **Hobbyist and educational flight.**
- **Search-and-rescue support.** Subject-detection over declared search areas (the canonical search-and-rescue *profile* is a stretch goal; basic SAR support fits here at v1.0).

## Out of scope

- **Anything outside the canonical organizational scope.** See the scope note above.
- **Beyond-visual-line-of-sight (BVLOS) operations** at v1.0. The v1.0 envelope assumes the operator can see the drone or has authorization-equivalent observation in place; BVLOS adds regulatory and safety requirements URML defers until a later version.
- **Indoor or transitional indoor/outdoor flight at v1.0.** Possibly a stretch goal; pure outdoor flight first.
- **Heavy-lift cargo / aerial-delivery profile-level features at v1.0.** Adjacent and likely to become its own profile.

## Safety envelope class

A drone operates in **regulated airspace shared with other aircraft and the public on the ground**. The default safety envelope:

- **Altitude cap** declared per deployment, defaulting to the local civil aviation authority's maximum (in many jurisdictions, ~120 m / ~400 ft above ground level for uncertified small drones; *the deployment is responsible for setting this correctly*).
- **Geofence**: a declared polygon (or set of polygons) outside which the drone refuses to fly. The validator rejects any URML program whose declared targets fall outside the geofence.
- **Weather thresholds**: declared maximum wind speed, minimum visibility, no-precipitation-required flag. The runtime is expected to refuse takeoff (or to land) if real-time conditions exceed declared envelope.
- **No flight over people without explicit override.** Defaults reject any program whose declared scan area overlaps a declared people-occupancy zone.
- **Mandatory return-to-home** on low battery, communication loss, or geofence breach.

These are *defaults*; deployments may tighten further but never weaken.

## Required manifest fields

When this profile is drafted, the capability manifest of a drone-profile-conformant aircraft will be required to declare at least:

- Aircraft class (multirotor, fixed-wing, VTOL, etc.).
- Service ceiling (the aircraft's own maximum altitude capability).
- Endurance (battery time at hover, at cruise).
- Maximum and recommended cruise/scan velocities.
- Sensor payload (RGB camera, multispectral, LiDAR, thermal, etc.) — at minimum the optical sensor whose `scan` properties the LLM bridge will reference.
- Communication-link characteristics and the policy on link loss.
- Declared coordinate frames (typically WGS-84 lat/lon/alt plus a body frame).

## Layer-2 primitives this profile adds

To be defined. Likely candidates: `take_off(altitude)`, `land(at: location)`, `hover(over: target, duration: t)`, `scan(area: polygon, pattern: serpentine | spiral, overlap: pct)`, `return_to_home`.

## Layer-2 primitives this profile constrains

- `move_to` must declare altitude (relative or absolute). A `move_to` without an altitude is rejected by the validator in the drone profile.
- `detect` over declared people-occupancy zones is rejected unless an explicit operator override is in the manifest.

## Reference runtime

[`/reference/px4-runtime/`](../../../reference/px4-runtime/) is the second reference runtime and targets this profile. It is part of the [Core Commitment](../../../CORE_COMMITMENT.md).

## Conformance points

When this profile is drafted, the conformance suite will include:

- End-to-end test of the `citizen inspector` (roof inspection) scenario.
- Negative tests that the validator rejects programs that violate the altitude cap, the geofence, or the weather thresholds declared in the manifest.
- Negative tests that the validator rejects programs that route the drone over declared people-occupancy zones without an explicit override.

## Related documents

- [`/docs/architecture.md`](../../../docs/architecture.md) §Profiles.
- [`/reference/px4-runtime/`](../../../reference/px4-runtime/) — the reference runtime.
- [`MANIFESTO.md`](../../../MANIFESTO.md) §Motivating Scenarios — *Drone: the citizen inspector*.
