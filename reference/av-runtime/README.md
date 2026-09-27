<p align="center">
  <a href="https://urml.dev"><img src="https://urml.dev/favicon.svg" alt="URML" width="72" height="72"></a>
</p>

# urml-av-runtime

**Autonomous-vehicle reference runtime for URML** — `AutowareAdapter`, over the Autoware Universe AD API.

The first substrate to implement URML's `TrajectoryAdapter` Protocol (RFC-0020). Until now only `MockROSAdapter` did; this backs the AV verbs against a real [Autoware](https://autoware.org/) stack through the documented [AD API](https://autowarefoundation.github.io/autoware-documentation/main/design/autoware-interfaces/ad-api/) (`autoware_adapi_v1_msgs`).

## Method coverage

| URML primitive | Autoware AD API | behaviour |
|---|---|---|
| `plan_path` (compute) | `/api/routing/set_route_points` (`SetRoutePoints`) | sets a route to the goal pose; Autoware plans the dense trajectory from the vehicle's localized pose. URML binds a route handle, not raw waypoints |
| `follow_trajectory` (actuate) | `/api/operation_mode/change_to_autonomous` (`ChangeOperationMode`) + a `VelocityLimit` publish | engages autonomous driving under an optional speed cap. The only AV verb that actuates |
| `wait` / `report` | none | passive hold / local report sink, so a full AV program runs |

Everything else in the substrate surface is not implemented: an AV program is `plan_path` then `follow_trajectory` (see [`examples/av/robotaxi-trip.urml.yaml`](../../examples/av/robotaxi-trip.urml.yaml)).

## Honest boundaries

- `start` is ignored: Autoware routes from the vehicle's current localized pose.
- `along` (an HD-map corridor id) is checked by the validator upstream; the AD API routing request takes no such field, so it is not forwarded.
- `max_accel` and `on_off_route` are vehicle- and planning-configured in Autoware; the adapter records the intent, it does not set them per call.
- Every AD API service / topic / message-type name is overridable in `AutowareConfig`, so the adapter tracks a specific Autoware release without a code change.

## Install / use

`rclpy` and the Autoware message packages ship with a ROS 2 + Autoware install, not from PyPI, so there is no installable extra. They are imported lazily, so this module loads on every host (Windows included) and the hermetic suite runs without ROS 2.

```bash
pip install -e reference/av-runtime      # hermetic dev; adapter needs Linux + Autoware to actuate
```

```python
from urml_av_runtime import AutowareAdapter, AutowareConfig, MapPose

cfg = AutowareConfig(location_to_pose={
    "depot":   MapPose(x=0.0,  y=0.0),
    "dropoff": MapPose(x=30.0, y=12.0, yaw=1.57),
})
# rclpy.init() is the caller's responsibility, as with RclpyAdapter.
with AutowareAdapter(cfg) as av:
    plan = av.plan_trajectory(start=None, goal="dropoff", along="city_map")
    av.follow_trajectory_goal(trajectory=plan.payload, max_velocity_mps=12.0)
```

## Status

**v0.1 (this release):**
- `AutowareAdapter` + `AutowareConfig` + `load_av_config`. Hermetic suite green via fake-`rclpy` / fake-message injection (`pytest reference/av-runtime/tests -q`).
- The `av` profile is research-grade, not production safety-certified (RFC-0020). Real-vehicle validation on a Linux + Autoware host is a gated follow-up, never claimed from the hermetic suite.

## Core Commitment

Apache 2.0. Outside the [Core Commitment](../../CORE_COMMITMENT.md) boundary (only ROS 2 + PX4 are named there) but carries the same no-vendor-coupling, no-cloud, no-enterprise-edition posture. `rclpy` and the Autoware messages are imported lazily, never at module load.
