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

# Nav2 run, 2026-09-29: a URML scan through `RclpyAdapter` and Nav2's loopback simulator

**Result: a validated URML program with one `scan` step drove Nav2 to all nine waypoints of a serpentine over a 2 m square and photographed each stop, and a listen-only witness saw the robot within 0.23 m of every waypoint.** In the same run, a Nav2 goal off the map came back as `goal_aborted (error_code 204)`, which the adapter used to report as a success, and a spiral scan read the soil probe at all four of its stops. Three runs that day passed.

This is Nav2's loopback simulator on a developer machine: the real Nav2 planner, controller and behavior tree driving a kinematic robot, with no physics and synthetic 16x16 test images. It is not a CI run and not a hardware run.

## What ran

| Item | Value |
|---|---|
| Date (UTC) | 2026-09-29; the recorded cycle ran from 05:35:29 to 05:38:58 |
| Where | Locally, WSL2 on the maintainer's Windows 10 machine (Ubuntu 24.04.4 LTS, kernel 6.18.33.2-microsoft-standard-WSL2, 8 CPUs, 7 GB RAM). Not in CI. |
| ROS 2 | Jazzy from packages.ros.org: `ros-jazzy-ros-base` 0.11.0, rclpy 7.1.12 |
| Nav2 | 1.3.13, launched with `nav2_bringup`'s `tb3_loopback_simulation.launch.py` (`nav2_loopback_sim`), headless: a TurtleBot 3 waffle on the `depot` map, starting at x -3.0, y 0.0, yaw 0 in `map` |
| Nav2 parameters | The bringup's `nav2_params.yaml` with one change: `loopback_simulator.scan_range_max` 30.0 to 3.5, because the stock range held the simulator at 100% CPU. Goal tolerance is the stock 0.25 m and 0.25 rad. |
| Test publishers | [`nav2_loopback/camera_pub.py`](../nav2_loopback/camera_pub.py): 16x16 mono8 images on `/camera/image_raw` at 2 Hz. [`nav2_loopback/soil_probe_pub.py`](../nav2_loopback/soil_probe_pub.py): `std_msgs/Float64` on `/sensor/soil_probe` at 2 Hz. |
| URML | The scan implementation at commit `6177c43`; the test, its adapter config and the publishers are in the commit that adds this record |
| Python | 3.12.3, in a venv that also sees ROS's packages; pytest 9.1.1, pydantic 2.13.5 |
| Test | [`test_scan_nav2_e2e.py`](../test_scan_nav2_e2e.py) with [`adapter_scan_nav2.yaml`](../adapter_scan_nav2.yaml) (`scan.swath_m` 1.0, frame `map`) |

## Commands

The runs used a local wrapper script, not in the repository, that performs these steps and, before the test starts, waits until Nav2's lifecycle managers report active, `/navigate_to_pose` answers, `map` -> `base_link` resolves and both test topics have a publisher.

```bash
# ROS 2 Jazzy from packages.ros.org, then Nav2 without Gazebo or RViz: ros-jazzy-ros-base,
# ros-jazzy-nav2-loopback-sim, and each dependency of ros-jazzy-navigation2 except
# nav2-rviz-plugins. nav2_bringup and nav2_minimal_tb3_sim depend on Gazebo (ros_gz) but hold
# only launch files, parameters, maps and URDF, so their .debs were unpacked with
# `dpkg-deb -x` into an overlay on AMENT_PREFIX_PATH instead of being installed.
source /opt/ros/jazzy/setup.bash   # plus the overlay

ros2 launch nav2_bringup tb3_loopback_simulation.launch.py use_rviz:=False \
  map:=<overlay>/share/nav2_bringup/maps/depot.yaml params_file:=<params with scan_range_max 3.5>

# The loopback simulator publishes map -> odom only after an initial pose; send it until
# map -> base_link resolves.
ros2 topic pub -r 1 -t 5 /initialpose geometry_msgs/msg/PoseWithCovarianceStamped \
  "{header: {frame_id: map}, pose: {pose: {position: {x: -3.0, y: 0.0}, orientation: {w: 1.0}}}}"

cd reference/ros2-runtime
python3 tests/integration/nav2_loopback/camera_pub.py &
python3 tests/integration/nav2_loopback/soil_probe_pub.py &

# Once /navigate_to_pose answers. ROS's launch_testing pytest plugin, seen through the ROS
# site-packages, does not load under pytest 9, so plugin autoload is off.
URML_NAV2_SCAN_E2E=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 \
  python -m pytest tests/integration/test_scan_nav2_e2e.py -v -s -p no:cacheprovider
```

Nav2 reported its lifecycle nodes active 9.1 s after the launch.

## pytest output (the recorded cycle)

```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: /mnt/c/Users/Ido/URML/.claude/worktrees/ros2-scan/reference/ros2-runtime
configfile: pyproject.toml
collected 3 items

tests/integration/test_scan_nav2_e2e.py scan: 9/9 samples, coverage 1.0, skipped []; witness samples 918
witness: closest approach per waypoint (m) {0: 0.212, 1: 0.056, 2: 0.165, 3: 0.131, 4: 0.0, 5: 0.107, 6: 0.111, 7: 0.019, 8: 0.23}; end pose (-2.729511678813512, 0.48324220496218173)
.goal off the map: success=False reason='goal_aborted (error_code 204)'
.spiral sensor scan: 4 readings, skipped []
.

======================== 3 passed in 180.26s (0:03:00) =========================
```

## What the three tests checked

1. **A validated serpentine photo scan.** The program (profile `home`, one `scan` over the bounding box x -4..-2, y -1..1, overlap 0.3, `media: photo`, camera `oakd_rgb`) was validated against the `turtlebot4_home` manifest and executed by `URMLRuntime`. The adapter planned nine waypoints 0.5 m apart, sent Nav2 one goal per waypoint, each facing the next, and took one image per stop from `/camera/image_raw`. The binding reported 9 samples of 9 and coverage 1.0.
2. **A goal Nav2 aborts.** `send_navigation_goal` to (100, 100): Nav2 accepted the goal, then finished it ABORTED with error code 204, and the adapter returned a failure carrying that code. Before commit `6177c43` the adapter counted any finished goal as a success.
3. **A spiral sensor scan** (adapter level, since the manifest declares no probe): four stops at overlap 0, one `/sensor/soil_probe` reading at each.

## What the witness measured

The witness is a separate node on its own executor that samples the `map` -> `base_link` transform at 10 Hz and sends nothing. Closest approach to each sampled waypoint of the serpentine, in visiting order:

| Waypoint | x, y (m) | Recorded cycle | Run 2 |
|---|---|---|---|
| 0 | -3.5, -0.5 | 0.212 | 0.165 |
| 1 | -3.0, -0.5 | 0.056 | 0.056 |
| 2 | -2.5, -0.5 | 0.165 | 0.178 |
| 3 | -2.5, 0.0 | 0.131 | 0.140 |
| 4 | -3.0, 0.0 | 0.000 | 0.025 |
| 5 | -3.5, 0.0 | 0.107 | 0.089 |
| 6 | -3.5, 0.5 | 0.111 | 0.133 |
| 7 | -3.0, 0.5 | 0.019 | 0.027 |
| 8 | -2.5, 0.5 | 0.230 | 0.232 |

The test requires 0.35 m: Nav2's goal checker stops the robot within 0.25 m of a goal, and the witness samples every 0.1 s. Waypoint 4 is the robot's start pose, so in the recorded cycle, which began from a fresh stack, its 0.000 m was measured before the scan moved; in run 2 the robot started elsewhere, at the end pose of run 1, and reached it at 0.025 m. The robot ended at x -2.730, y 0.483, inside the area, 0.23 m from the last waypoint.

## Other runs the same day

| Run | Stack | Result |
|---|---|---|
| Goal checks | `ros2 action send_goal` from the CLI: a goal 1 m ahead of the start finished SUCCEEDED with the robot stopping at x -2.219, y 0.016; a goal at (100, 100) finished ABORTED with error code 204 and the robot did not move | as expected |
| 1 | the same stack, robot where the goal checks left it | 3 passed in 119.27 s; serpentine 9/9, coverage 1.0 |
| 2 | the same stack, robot where run 1 ended | 3 passed in 100.17 s; the per-waypoint distances above |
| Recorded cycle | a fresh bringup, the test, then a shutdown that left no process running | 3 passed in 180.26 s |

Runs 1 and 2 used the test before two small changes: the per-waypoint distances were printed from run 2 on, and each test's adapter got its own node name for the recorded cycle, after run 2 logged rcl warnings about three adapters reusing one node name in a process.

## Limits

- A kinematic simulator: no physics, no wheel slip, no moving obstacles, and a laser simulated from the map. The robot is a TurtleBot 3 waffle; the manifest the program was validated against is the `turtlebot4_home` manifest, which only had to declare mobility and a photo-capable camera.
- The images are 16x16 synthetic frames. The adapter keeps no image data (`in_memory://` handles, the same as `capture`), so a real camera and image storage were not exercised.
- Only `serpentine` (validated, photo) and `spiral` (adapter level, sensor) ran live, over open floor, so no waypoint was skipped. `grid`, named regions, and skipping a waypoint Nav2 aborts are covered by the unit tests only.
- The program was validated with no safety envelope, so no geofence or occupancy check applied, and with the compliance policy off.
- Nav2 plans the path between waypoints; only the waypoints are checked against the area.
- Not CI. The `gazebo-e2e` job in `.github/workflows/ros2-integration.yml` is a separate test and has not run.
