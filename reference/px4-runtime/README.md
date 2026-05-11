# PX4 Reference Runtime

**Status:** Pre-implementation. Phase 2 target.

## What this is

The **second** URML reference runtime. Targets the [drone profile](../../spec/profiles/drone/) (civilian). Translates a validated URML program into PX4 / MAVLink commands; honors declared altitude, geofence, weather, and people-occupancy envelope checks before any motor spins.

Why a *second* reference runtime exists at all: it is the strongest evidence the URML specification is genuinely substrate-neutral. A single reference runtime — no matter how clean — risks the spec accidentally encoding ROS-2 assumptions. A second runtime on an entirely different substrate (no ROS dependency) keeps the spec honest. This is the substrate-neutrality acid test enforced at the implementation level, not just on paper.

## Substrate

- **PX4 Autopilot** (current stable releases). Tracks PX4's own release cadence.
- **MAVLink** as the command-and-control protocol.
- Optional **uXRCE-DDS** bridge for runtimes that want to share data with ROS-2 components without becoming ROS-2-dependent.

The runtime does **not** require ROS 2 to function. That is by design.

## Language

- **Python** for the URML-to-MAVLink compiler, the validator bridge, tests, and the command dispatcher.
- **C++17** if any per-tick hot-path component is needed; expected to be small (PX4 itself runs the real-time loop).

## Conformance contract

Conformant when it passes the published conformance suite for the supported drone-profile spec versions. Declared conformance lives in a `CONFORMANCE.md` alongside this README when the first version cuts.

## Architecture (planned)

Three responsibilities, mirroring the ROS 2 runtime:

1. **Validate.** Run the program through [`/reference/validator/`](../validator/) against the connected aircraft's capability manifest. Drone-specific manifest fields (service ceiling, endurance, communication-link policy) are checked here.
2. **Translate.** Compile each primitive into MAVLink commands:
   - `take_off(altitude)` → `MAV_CMD_NAV_TAKEOFF` with the altitude clamped to the manifest's declared ceiling.
   - `move_to({lat, lon, alt})` → `MAV_CMD_NAV_WAYPOINT`; validated against the declared geofence.
   - `hover(over: target, duration: t)` → `MAV_CMD_NAV_LOITER_TIME`.
   - `scan(area: polygon, pattern: serpentine, overlap: 0.3)` → a sequence of waypoints with the photo trigger configured (Layer-3 composes the scan; this layer compiles each waypoint).
   - `return_to_home` → `MAV_CMD_NAV_RETURN_TO_LAUNCH`.
   - `land(at: location)` → `MAV_CMD_NAV_LAND`.
3. **Honor composition.** Layer-3 sequence / branch / parallel / retry / on-error mapped to mission protocol + offboard-mode setpoints where the mission protocol is too coarse.

## Drone-profile-specific safety enforcement

Beyond the standard validator pass:

- **Altitude cap.** Every emitted waypoint is clamped to `min(manifest.service_ceiling, deployment.altitude_cap)`. Programs whose declared targets exceed this are rejected.
- **Geofence.** Mission upload is preceded by a polygon check.
- **Weather.** The runtime reads a configured weather source (or refuses takeoff if the source is missing or stale beyond a declared threshold).
- **Link-loss policy.** Honored per manifest declaration; programs cannot override.
- **People-occupancy.** Programs whose declared scan or move-to areas overlap declared people-occupancy zones are rejected unless an explicit operator override is in the manifest.

## Core Commitment

This runtime is part of the [Core Commitment](../../CORE_COMMITMENT.md). It will always be Apache 2.0. No vendor coupling, no cloud dependency, no enterprise edition.

## Related documents

- [`/spec/profiles/drone/`](../../spec/profiles/drone/) — the profile this runtime targets.
- [`/spec/layer-1-hal/`](../../spec/layer-1-hal/) — manifest schema, including drone-specific fields.
- [`/conformance/`](../../conformance/) — the test suite that decides conformance.
- [`MANIFESTO.md`](../../MANIFESTO.md) §Motivating Scenarios — *Drone: the citizen inspector*.
