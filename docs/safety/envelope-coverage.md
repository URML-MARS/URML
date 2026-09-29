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

# Envelope coverage

The Layer-2 spec gives every primitive a list of safety-envelope checks, and
says a conformant runtime must reject, before execution, every program that
violates one of them ([spec L1126-1127](../../spec/layer-2-primitives/v0.1.0.md)).
This page lists, for each primitive, what the spec requires, what the reference
validator enforces, and what it does not check statically and why.

Every enforced cell names a rejected conformance fixture. Every deferred cell
cites the RFC or spec line behind it. `conformance/tests/test_envelope_coverage_doc.py`
reads this page and fails when a primitive has no row, when a pinning fixture
does not make the validator emit that code from a step of that primitive, or
when a deferred cell cites nothing. When a spec edit moves the cited lines,
update the line numbers here.

## How the checks work

The validator reads three inputs: the manifest (what the robot can do), the
deployment envelope (what this site allows), and the program. For each numeric
limit it takes the strictest of the manifest value and the envelope value.

Spatial checks run on every place a step names: a pose, a declared location, a
declared area (RFC-0615), a docking station, or a scan area.

- A geofence is an allowlist. Each checked point must lie inside at least one
  declared geofence, and inside its altitude band when the target has an
  altitude.
- A people-occupancy zone is a denylist. A point target may not lie inside one,
  and a scan area may not overlap one. A zone the deployment marks
  `allow_override: true` is skipped.
- A named place carries its own altitude, which must be at or below the
  strictest of the manifest's `service_ceiling` and the envelope's
  `max_altitude`.
- A declared area is checked vertex by vertex against the geofences, because
  the runtime may stop anywhere inside it.
- A geofence or zone in another frame applies when the target resolves into its
  frame through the manifest's frame graph. When no transform connects the
  frames, the check abstains, as RFC-0290 specifies.

The checks judge the targets a program names. The path between two targets is
chosen by the runtime, and the validator does not see it
([spec L136-137](../../spec/layer-2-primitives/v0.1.0.md)).

## The matrix

"Not statically checkable" means the value only exists at run time (a detected
pose, the robot's position, the weather). "Needs spec text" means the spec asks
for the check but does not say enough to implement it, or no manifest or
envelope field carries the limit yet.

| Primitive | Spec requires | Enforced (code: pinning fixture) | Not statically checkable or deferred |
|---|---|---|---|
| `move_to` | Target inside the geofence or cell perimeter; target altitude at or below the service ceiling and the active cap; speed at or below the manifest maximum and any active cap, including a speed given as a fraction of the maximum ([spec L141-145](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.velocity_exceeded`: [warehouse/04](../../conformance/fixtures/warehouse/04_envelope_speed_violation_rejected.yaml), [industrial/52](../../conformance/fixtures/industrial/52_move_to_fraction_speed_over_cap_rejected.yaml), [industrial/53](../../conformance/fixtures/industrial/53_move_to_fraction_above_one_rejected.yaml)<br>`envelope.altitude_exceeded`: [drone/26](../../conformance/fixtures/drone/26_named_location_above_ceiling_rejected.yaml)<br>`envelope.geofence_violation`: [drone/07](../../conformance/fixtures/drone/07_geofence_violation_rejected.yaml), [drone/08](../../conformance/fixtures/drone/08_altitude_band_violation_rejected.yaml), [home/33](../../conformance/fixtures/home/33_move_to_area_outside_geofence_rejected.yaml)<br>`envelope.occupancy_zone_intrusion`: [drone/09](../../conformance/fixtures/drone/09_occupancy_zone_intrusion_rejected.yaml), [warehouse/05](../../conformance/fixtures/warehouse/05_people_occupancy_zone_intrusion_rejected.yaml)<br>`envelope.payload_exceeded`: [drone/38](../../conformance/fixtures/drone/38_carrying_mass_over_cap_rejected.yaml) | The path to the target: the runtime selects the trajectory, so zones crossed on the way are not seen ([spec L136-137](../../spec/layer-2-primitives/v0.1.0.md)).<br>Occupancy when the target is a declared area: needs spec text on whether an area that overlaps a zone is refused (RFC-0615).<br>A geofence with a concave outline: vertex containment is exact for convex fences only; an area edge can leave a concave fence between two inside vertices (RFC-0615).<br>Frames with no transform between them: the check abstains (RFC-0290). |
| `drive` | Capability checks (relative motion declared, distance at or below `max_relative_distance`); the declared speed at or below the strictest cap (RFC-0701 §4.1) ([spec L1050](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.velocity_exceeded`: [educational/16](../../conformance/fixtures/educational/16_drive_speed_over_cap_rejected.yaml) | The base's closed-loop velocity and acceleration bounds on the commanded twist stay with the consuming node (RFC-0518); the static check catches only a declared speed already over the cap.<br>Geofences and zones: a relative move has no declared end point, so not statically checkable (RFC-0630). |
| `turn` | Same capability and profile gate as `drive` ([spec L1066](../../spec/layer-2-primitives/v0.1.0.md)) | none | The turn rate is not compared with `max_angular_velocity`: the consuming node enforces base-rate limits (RFC-0518). |
| `dock` | Station inside the operational area; service in the profile's list; robot state allows the service ([spec L178-182](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.geofence_violation`: [warehouse/10](../../conformance/fixtures/warehouse/10_dock_outside_geofence_rejected.yaml)<br>`envelope.occupancy_zone_intrusion`: [warehouse/14](../../conformance/fixtures/warehouse/14_dock_occupancy_zone_rejected.yaml)<br>`envelope.altitude_exceeded`: [warehouse/17](../../conformance/fixtures/warehouse/17_dock_above_reach_cap_rejected.yaml) | The service against the active profile's list: no profile publishes a machine-readable service list; needs spec text ([spec L182-185](../../spec/layer-2-primitives/v0.1.0.md)).<br>Battery present for `charge`, gripper empty for `swap_tool`: robot state at run time, not statically checkable ([spec L182-185](../../spec/layer-2-primitives/v0.1.0.md)). |
| `hover` | Hover location inside the operational area; duration within endurance and margin; no overlap with people-occupancy zones ([spec L212-216](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.geofence_violation`: [drone/23](../../conformance/fixtures/drone/23_hover_over_outside_geofence_rejected.yaml)<br>`envelope.occupancy_zone_intrusion`: [drone/24](../../conformance/fixtures/drone/24_hover_over_occupancy_zone_rejected.yaml)<br>`envelope.altitude_exceeded`: [drone/25](../../conformance/fixtures/drone/25_hover_over_above_ceiling_rejected.yaml) | Duration against endurance: no manifest or envelope field declares endurance or `max_flight_duration`; needs spec text ([spec L216-219](../../spec/layer-2-primitives/v0.1.0.md), [drone profile L216](../../spec/profiles/drone/README.md)).<br>`over: $target` or no `over`: the position is a runtime binding, or the previous motion step's target, which that step's checks already cover ([spec L201](../../spec/layer-2-primitives/v0.1.0.md)). |
| `wait` | Profile prohibitions: the drone profile rejects `wait` in flight ([spec L242-245](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.wait_in_flight`: [drone/40](../../conformance/fixtures/drone/40_wait_in_flight_rejected.yaml) | none |
| `wait_for` | Wait pose inside the operational area; timeout within endurance and margin ([spec L276-280](../../spec/layer-2-primitives/v0.1.0.md)) | none | The wait pose is the current position, which the previous motion step's checks cover ([spec L280-281](../../spec/layer-2-primitives/v0.1.0.md)).<br>Timeout against endurance: no endurance field exists; needs spec text ([spec L280-281](../../spec/layer-2-primitives/v0.1.0.md)). |
| `grasp` | Force within the gripper range and at or below the profile's ceiling; target inside the reachable workspace ([spec L330-342](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.force_exceeded`: [home/12](../../conformance/fixtures/home/12_force_ceiling_envelope.yaml) | The profile's default ceiling with no envelope: the home ceiling (3 N) lives in the deployment envelope. A built-in default would refuse programs accepted today (biped/06 and biped/07 grip `firm` under the home profile with no envelope); needs spec text ([home profile L104](../../spec/profiles/home/README.md)).<br>Target inside the reachable workspace: the target pose comes from a detection at run time ([spec L329-332](../../spec/layer-2-primitives/v0.1.0.md)). |
| `release` | Drop height within the envelope's `max_drop_height` (a winch's `height`, a latch's current altitude); the named `winch`/`latch` `payload_mechanisms` entry declared and matching the mode; for `hand_to_user`, the user location reachable ([spec L379-387](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.drop_height_exceeded`: [drone/37](../../conformance/fixtures/drone/37_drop_height_exceeded_rejected.yaml) | The `hand_to_user` user location inside the reachable workspace: depends on where the robot stands at run time ([spec L379-387](../../spec/layer-2-primitives/v0.1.0.md)).<br>The winch/latch release position's geofence and occupancy are now covered by the current-position target (RFC-0684). |
| `bimanual` | Each side's grasp or release checks, per arm ([spec L915-922](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.force_exceeded`: [biped/15](../../conformance/fixtures/biped/15_bimanual_force_over_envelope_rejected.yaml) | A release side inherits the release gaps above ([spec L364-366](../../spec/layer-2-primitives/v0.1.0.md)). |
| `detect` | Search region inside the operational area ([spec L423-427](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.geofence_violation`: [drone/29](../../conformance/fixtures/drone/29_detect_near_outside_geofence_rejected.yaml), [drone/33](../../conformance/fixtures/drone/33_detect_search_radius_outside_geofence_rejected.yaml) | `near: $reference`, or `within` with no `near`: the region centers on a pose known only at run time ([spec L386-387](../../spec/layer-2-primitives/v0.1.0.md)).<br>Detecting people over an occupancy zone: the drone profile plans a manifest override flag that does not exist yet ([drone profile L230](../../spec/profiles/drone/README.md)). |
| `scan` | Area and pattern path inside the operational envelope; altitude within the ceiling and the active cap; no sample point in a people-occupancy zone ([spec L458-462](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.altitude_exceeded`: [drone/30](../../conformance/fixtures/drone/30_scan_altitude_exceeded_rejected.yaml)<br>`envelope.geofence_violation`: [drone/31](../../conformance/fixtures/drone/31_scan_area_outside_geofence_rejected.yaml)<br>`envelope.occupancy_zone_intrusion`: [drone/27](../../conformance/fixtures/drone/27_scan_area_contains_zone_rejected.yaml) | The pattern path: the substrate generates it at run time ([spec L435-438](../../spec/layer-2-primitives/v0.1.0.md)).<br>A `named_region` that is not a declared area: nothing resolves it; needs spec text on what it must name ([spec L417](../../spec/layer-2-primitives/v0.1.0.md)).<br>A literal polygon or bounding box has no frame field, so it is read in the frame of the first geofence (or zone); a frame field needs spec text ([spec L417](../../spec/layer-2-primitives/v0.1.0.md)).<br>A geofence with a concave outline: the area is checked vertex by vertex (RFC-0615). |
| `measure` | Target within the sensor's declared range ([spec L490-493](../../spec/layer-2-primitives/v0.1.0.md)) | none | The distance from the robot to the target exists only at run time ([spec L466](../../spec/layer-2-primitives/v0.1.0.md)). |
| `capture` | Video duration within the storage and endurance budget; capture in a privacy-restricted zone needs a manifest override ([spec L524-532](../../spec/layer-2-primitives/v0.1.0.md)) | none | Storage budget and privacy-restricted zones: no manifest or envelope field declares either; needs spec text ([spec L505-508](../../spec/layer-2-primitives/v0.1.0.md), [drone profile L234](../../spec/profiles/drone/README.md)). |
| `report` | None beyond destination validity ([spec L564-567](../../spec/layer-2-primitives/v0.1.0.md)) | none | none |
| `speak` | None beyond the capability declaration ([spec L601-604](../../spec/layer-2-primitives/v0.1.0.md)) | none | Do-not-disturb hours are deferred by the spec ([spec L577-578](../../spec/layer-2-primitives/v0.1.0.md)). |
| `listen` | Timeout at or below the envelope's `max_listen_duration` ([spec L633-637](../../spec/layer-2-primitives/v0.1.0.md)) | none | The envelope has no `max_listen_duration` field, and the "declared finite" rule has no error code; needs spec text ([spec L610-611](../../spec/layer-2-primitives/v0.1.0.md)). |
| `look_at` | The envelope's expression block tightens the head and body ranges ([spec L1094-1104](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.head_pose_exceeded`: [social/06](../../conformance/fixtures/social/06_look_at_beyond_envelope_rejected.yaml) | The envelope's `max_angular_velocity` is not checked: the starting head pose is known only at run time (RFC-0698). |
| `gesture` | Gesture duration at or below `max_gesture_duration_s`; name in `gestures_allowed` ([spec L1131-1135](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.gesture_duration_exceeded`: [social/07](../../conformance/fixtures/social/07_gesture_over_envelope_duration_rejected.yaml)<br>`envelope.gesture_not_allowed`: [social/08](../../conformance/fixtures/social/08_gesture_not_allowed_rejected.yaml) | none |
| `take_off` | Altitude at or below the strictest of the service ceiling and `max_altitude`; weather thresholds ([spec L663-667](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.altitude_exceeded`: [drone/02](../../conformance/fixtures/drone/02_altitude_exceeded_rejected.yaml) | Weather: the substrate reports it at run time ([spec L640-642](../../spec/layer-2-primitives/v0.1.0.md)). |
| `land` | Landing location inside the geofence; people-occupancy zones do not intersect the approach ([spec L692-696](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.geofence_violation`: [drone/20](../../conformance/fixtures/drone/20_land_outside_geofence_rejected.yaml)<br>`envelope.occupancy_zone_intrusion`: [drone/21](../../conformance/fixtures/drone/21_land_in_occupancy_zone_rejected.yaml) | The approach path: the substrate flies it; the landing point is checked ([spec L669-670](../../spec/layer-2-primitives/v0.1.0.md)).<br>`land` with no `at` lands below the current position, which the previous motion step's checks cover ([spec L669-670](../../spec/layer-2-primitives/v0.1.0.md)).<br>Occupancy when `at` names a declared area: needs spec text (RFC-0615). |
| `return_to_home` | Declared return altitude at or below `max_altitude` and the service ceiling; the declared return speed at or below the strictest cap (RFC-0701 §4.1) ([spec L723-730](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.altitude_exceeded`: [drone/32](../../conformance/fixtures/drone/32_return_to_home_altitude_exceeded_rejected.yaml)<br>`envelope.velocity_exceeded`: [drone/39](../../conformance/fixtures/drone/39_return_to_home_speed_exceeded_rejected.yaml) | An omitted speed or altitude uses the substrate's RTH settings, which stay within the caps ([spec L703-704](../../spec/layer-2-primitives/v0.1.0.md)). |
| `pick_from` | The inherited `move_to` and `grasp` checks, including the force cap ([spec L760-765](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.force_exceeded`: [industrial/50](../../conformance/fixtures/industrial/50_pick_from_force_over_envelope_rejected.yaml)<br>`envelope.geofence_violation`: [warehouse/12](../../conformance/fixtures/warehouse/12_pick_from_outside_geofence_rejected.yaml)<br>`envelope.occupancy_zone_intrusion`: [warehouse/09](../../conformance/fixtures/warehouse/09_pick_from_occupancy_zone_rejected.yaml)<br>`envelope.altitude_exceeded`: [warehouse/15](../../conformance/fixtures/warehouse/15_pick_from_above_reach_cap_rejected.yaml) | The velocity ceiling: `pick_from` has no speed argument; the runtime picks the speed ([spec L738-740](../../spec/layer-2-primitives/v0.1.0.md)).<br>Occupancy when the source is a declared area: needs spec text (RFC-0615). |
| `place_at` | The inherited `move_to` and `release` checks ([spec L796-799](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.geofence_violation`: [warehouse/13](../../conformance/fixtures/warehouse/13_place_at_outside_geofence_rejected.yaml)<br>`envelope.occupancy_zone_intrusion`: [industrial/55](../../conformance/fixtures/industrial/55_place_at_occupancy_zone_rejected.yaml)<br>`envelope.altitude_exceeded`: [warehouse/16](../../conformance/fixtures/warehouse/16_place_at_above_reach_cap_rejected.yaml) | Drop height for `mode: drop`: `height` is advisory in v0.1 and no field declares a maximum (RFC-0013).<br>The velocity ceiling: `place_at` has no speed argument; the runtime picks the speed ([spec L772](../../spec/layer-2-primitives/v0.1.0.md)).<br>Occupancy when the target is a declared area: needs spec text (RFC-0615). |
| `swap_tool` | None beyond the station being reachable ([spec L826-830](../../spec/layer-2-primitives/v0.1.0.md)) | none | Reachability is a planning question answered at run time; tool membership and reach windows are deferred (RFC-0013). |
| `call_program` | None possible: the program body is opaque ([spec L859-876](../../spec/layer-2-primitives/v0.1.0.md)) | none | The body's motion and force are unknown to URML; only the call's signature is checked (RFC-0015). |
| `plan_path` | None on the plan; it does not actuate ([spec L954-958](../../spec/layer-2-primitives/v0.1.0.md)) | none | none |
| `follow_trajectory` | Speed envelope at or below the strictest of the ODD cap, the mobility maximum and the envelope maximum ([spec L987-991](../../spec/layer-2-primitives/v0.1.0.md)) | `envelope.velocity_exceeded`: [av/03](../../conformance/fixtures/av/03_follow_over_odd_cap_rejected.yaml) | none |
| `set_output` | Capability checks only, at Pass 2: declared line, value type, analog range ([spec L1022](../../spec/layer-2-primitives/v0.1.0.md)) | none | none |

## Named targets resolve first

A spatial check needs coordinates. Every argument that names a place must
resolve against the manifest at Pass 2, so an unknown name is refused instead
of skipping the checks above ([spec L82-83](../../spec/layer-2-primitives/v0.1.0.md)).

| Argument | Code | Pinning fixture |
|---|---|---|
| `move_to.location` | `capability.missing_location` | [home/03](../../conformance/fixtures/home/03_missing_location_rejected.yaml) |
| `pick_from.source` | `capability.missing_location` | [industrial/56](../../conformance/fixtures/industrial/56_pick_from_undeclared_source_rejected.yaml) |
| `place_at.target` | `capability.missing_location` | [industrial/57](../../conformance/fixtures/industrial/57_place_at_undeclared_target_rejected.yaml) |
| `dock.at` | `capability.missing_docking_station` | [warehouse/19](../../conformance/fixtures/warehouse/19_dock_undeclared_station_rejected.yaml) |
| `hover.over` | `capability.missing_location` | [drone/18](../../conformance/fixtures/drone/18_hover_undeclared_location_rejected.yaml) |
| `land.at` | `capability.missing_location` | [drone/17](../../conformance/fixtures/drone/17_land_undeclared_location_rejected.yaml) |
| `detect.where.near` | `capability.missing_location` | [drone/19](../../conformance/fixtures/drone/19_detect_near_undeclared_location_rejected.yaml) |
| `release.at` | `capability.missing_location` | [home/32](../../conformance/fixtures/home/32_release_undeclared_location_rejected.yaml) |

A `$reference` in any of these is a runtime binding; the binding pass checks
that it resolves to an object.

## Whole-envelope checks

Three envelope checks are not tied to one primitive and run once per program:
link-loss rule coherence (RFC-0006), monitorable temporal-logic properties
(RFC-0382), and the learned-policy training envelope (RFC-0383). The envelope's
`max_payload` and `weather` fields are not checked against any step: no
primitive declares the mass it carries, and weather exists only at run time.

## Reproduce

```bash
python -m pytest reference/validator/tests/test_envelope_coverage.py
python -m pytest conformance/tests/test_envelope_coverage_doc.py
python -m urml_conformance
```
