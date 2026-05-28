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

# Move-16 research — substrate spine (drone autopilot + ROS 2 + middleware + SLAM) (Theme A)

**Research date**: 2026-05-28.
**Audience**: founder review before Move-16 RFCs draft.
**Method**: two Explore agents in parallel covered drone-autopilot + protocol (Agent 1) and ROS 2 + DDS + SLAM (Agent 2), cross-checked each candidate against all prior ledgers (Moves 1-15), verified via `gh repo view` + `gh api orgs/...` for `isArchived: false`, license, recency, Issues, origin.
**Outcome**: **16 verified engageable candidates** (12 Tier A + 4 Tier B); **~8 Tier C excluded with cause** (mostly already-engaged duplicates).

## Why this is URML's biggest wave

Theme A is **URML's identity-load-bearing wave.** URML's substrate-neutral claim depends on engagement with the substrate maintainers themselves: PX4 / MAVLink / Nav2 / MoveIt 2 / DDS / SLAM. Where Moves #10-15 engaged sensor / VLA / actuator / vertical layers above the substrate, Move #16 engages the substrate-runtime spine URML composes above.

Substrate-spine is also the broadest market with the most open-source defaults — Linux Foundation Dronecode (PX4 / MAVLink / QGroundControl), Open Robotics Foundation (ROS 2 / Nav2 / MoveIt 2), Eclipse Foundation (Cyclone DDS / Zenoh / iceoryx), eProsima vendor-direct, Google (Cartographer), university SLAM labs (Zaragoza ORB-SLAM3, Sherbrooke RTAB-Map).

## Tier A (12) — foundation-direct or vendor-direct, adapter-eligible

### Drone autopilot + protocol substrate (4)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `px4-autopilot` | [PX4/PX4-Autopilot](https://github.com/PX4/PX4-Autopilot) | BSD-3-Clause | 11.8k | 2026-05-28 (today) | Linux Foundation Dronecode | The dominant open drone-autopilot stack. URML's `reference/ros2-runtime/` composes via MAVLink; URML's manifest declares PX4 as substrate. |
| `mavlink` | [mavlink/mavlink](https://github.com/mavlink/mavlink) | LGPL-3.0 + MIT generated-code exception | 2.3k | 2026-05-28 | Dronecode Foundation | Drone protocol substrate. URML manifest declares MAVLink as the autopilot-control protocol. |
| `mavlink-mavsdk` | [mavlink/MAVSDK](https://github.com/mavlink/MAVSDK) | BSD-3-Clause | 881 | 2026-05-26 | Dronecode Foundation | High-level MAVLink SDK. URML adapter targets this layer for cross-vendor vehicle control. |
| `dronecan-libcanard` | [dronecan/libcanard](https://github.com/dronecan/libcanard) | MIT | 98 | 2026-04-30 | DroneCAN community | Alternative CAN-protocol substrate for drones. URML manifest declares as alternate-protocol to MAVLink. |

### ROS 2 + Nav + MoveIt (3)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `ros2-core` | [ros2/ros2](https://github.com/ros2/ros2) | Multi (BSD/Apache per module) | 5.5k | 2026-05-28 | Open Robotics Foundation / Linux Foundation | URML's primary substrate. Foundation-direct engagement with ROS 2 maintainers. |
| `ros-navigation-nav2` | [ros-navigation/navigation2](https://github.com/ros-navigation/navigation2) | Other (Apache-2.0 / BSD-3 mixed) | 4.3k | 2026-05-28 | OSRF-adjacent | URML's mobility primitives (`move_to`, `dock`) dispatch via Nav2. |
| `moveit-moveit2` | [moveit/moveit2](https://github.com/moveit/moveit2) | BSD-3-Clause | 1.8k | 2026-05-28 | Community / OSRF-adjacent | URML's manipulation primitives (`pick_from`, `place_at`, `grasp`) dispatch via MoveIt 2. |

### DDS / middleware (2)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `eprosima-fast-dds` | [eProsima/Fast-DDS](https://github.com/eProsima/Fast-DDS) | Apache-2.0 | 2.8k | 2026-05-28 | eProsima ES (Tres Cantos) | ROS 2 default DDS implementation. Vendor-direct (commercial). |
| `eclipse-cyclonedds` | [eclipse-cyclonedds/cyclonedds](https://github.com/eclipse-cyclonedds/cyclonedds) | Other (EPL-2.0) | 1.3k | 2026-05-26 | Eclipse Foundation NL | Alternative DDS implementation. Eclipse Foundation governance. |

### SLAM upstreams (3)

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `google-cartographer` | [cartographer-project/cartographer](https://github.com/cartographer-project/cartographer) | Apache-2.0 | 7.9k | 2026-05-28 | Google (US) | 2D/3D SLAM. URML's perception manifests declare Cartographer as the SLAM substrate. |
| `orb-slam3` | [UZ-SLAMLab/ORB_SLAM3](https://github.com/UZ-SLAMLab/ORB_SLAM3) | GPL-3.0 | 8.7k | 2026-05-28 | University of Zaragoza ES | Visual-SLAM canonical reference. GPL-3.0 → cross-citation framing at adapter boundary. |
| `rtabmap` | [introlab/rtabmap](https://github.com/introlab/rtabmap) | Other (LGPL/BSD mixed) | 3.8k | 2026-05-28 | Université de Sherbrooke (Quebec CA) | Visual-inertial SLAM; ROS 2-integrated. |

## Tier B (4) — research-collab / cross-citation framing

| Slug | Repo | License | Stars | Last push | Origin | Notes |
|---|---|---|---|---|---|---|
| `mavlink-qgroundcontrol` | [mavlink/qgroundcontrol](https://github.com/mavlink/qgroundcontrol) | Apache-2.0 | 4.6k | 2026-05-28 | Dronecode Foundation | Ground-station / mission-planning surface. Not autopilot proper; cross-citation eligible for operator-control UI. |
| `eclipse-zenoh` | [eclipse-zenoh/zenoh](https://github.com/eclipse-zenoh/zenoh) | Other (EPL-2.0 / Apache-2.0) | 2.8k | 2026-05-28 | Eclipse Foundation | Next-gen pub-sub overlay; substrate-emerging (not yet default ROS 2). |
| `eclipse-iceoryx` | [eclipse-iceoryx/iceoryx](https://github.com/eclipse-iceoryx/iceoryx) | Apache-2.0 | 2.1k | 2026-05-28 | Eclipse Foundation | Zero-copy IPC for ROS 2 intra-process. Substrate-IPC layer; cross-citation framing. |
| `stella-vslam` | [stella-cv/stella_vslam](https://github.com/stella-cv/stella_vslam) | Other | 1.2k | 2026-05-27 | Community fork (originally JP) | Community fork of archived OpenVSLAM. Cross-citation framing pending license clarity. |

## Tier C — excluded with cause

| Slug | Cause |
|---|---|
| `ardupilot` | **Already engaged Move-2 RFC-0041** — response: declined (IamPete1, 2026-05-25). Do not re-engage. |
| `micro-ros` | **Already engaged Move-13 RFC-0177.** |
| `open-rmf` | **Already engaged Move-2 RFC-0053.** |
| `open-robotics-gazebo` | **Already engaged Move-2 RFC-0037.** |
| `isaac-sim` | **Already engaged Move-2 RFC-0050** (NVIDIA Isaac Sim / Isaac Lab). |
| `mujoco-playground` | **Already engaged Move-11 RFC-0144.** |
| `openvslam` | **Archived** upstream. Stella VSLAM (Tier B RFC-0211) is the maintained community fork. |
| `auterion` | **Covered via PX4 governance.** Auterion is commercial downstream of PX4 (CH Switzerland); engagement at PX4 level covers upstream; Auterion not separate target. |

## Distribution

| Sub-category | Tier A | Tier B | Excluded |
|---|---|---|---|
| Drone autopilot + protocol | 4 (PX4, MAVLink, MAVSDK, DroneCAN) | 1 (QGroundControl) | 2 (ArduPilot, Auterion) |
| ROS 2 + Nav2 + MoveIt 2 | 3 (ROS 2 core, Nav2, MoveIt 2) | 0 | 1 (micro-ROS already engaged) |
| DDS / middleware | 2 (Fast DDS, Cyclone DDS) | 2 (Zenoh, iceoryx) | 0 |
| SLAM upstreams | 3 (Cartographer, ORB-SLAM3, RTAB-Map) | 1 (Stella VSLAM) | 1 (OpenVSLAM archived) |
| Sim + RMF (excluded) | 0 | 0 | 4 (Gazebo, Isaac, mujoco_playground, Open-RMF all already engaged) |
| **Total** | **12** | **4** | **8** |

## Reserved RFC range

RFCs 0196-0211 reserved for Move #16 in `docs/rfcs/README.md`. Move-15 ends at RFC-0195.

## Honest framing notes

- **Identity-load-bearing wave.** URML's substrate-neutral claim has been implicit in prior moves; Move-16 makes it explicit by engaging the substrate maintainers themselves.
- **Linux Foundation Dronecode is one engagement org for 4-5 Move-16 targets.** PX4 / MAVLink / MAVSDK / QGroundControl all under Dronecode governance. Engagement may converge to a Dronecode-level conversation.
- **Eclipse Foundation is the engagement org for 3 Move-16 targets** (Cyclone DDS / Zenoh / iceoryx).
- **eProsima Fast DDS is the only vendor-direct commercial DDS** (ES commercial entity vs Eclipse Foundation governance).
- **ORB-SLAM3 GPL-3.0 → cross-citation framing.** URML's Apache-2.0 adapter cannot embed GPL-3.0 SLAM code; the engagement is at the protocol / API boundary.
- **No license-clarification asks in this wave.** Most substrate-spine targets ship with explicit OSI declarations. Only RTAB-Map (mixed LGPL/BSD) and Stella VSLAM (license unclear on the community fork) carry minor ambiguity.

## Next steps

1. Founder review of this research file.
2. Setup PR ships: `outreach-move16.yaml` + `posts-move16.md` skeleton.
3. Subsequent sessions: draft RFCs 0196-0211 (likely 3 batches: drone-autopilot + protocol; ROS 2 + Nav + MoveIt + DDS; SLAM + Tier B).
4. Posting follows Move-10/11/13/14/15 pattern.
