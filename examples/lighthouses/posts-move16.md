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

# Move #16 post bodies — substrate spine (drone autopilot + ROS 2 + middleware + SLAM) (Theme A)

Copy-paste-ready Issue / Discussion bodies for the Move #16 outreach. **Wave shape**: 16 verified Theme A targets (12 Tier A + 4 Tier B), verified 2026-05-28. RFC numbers 0196-0211. **URML's biggest wave so far** — substrate-spine is the broadest market with the most open-source defaults.

Ledger state: [`outreach-move16.yaml`](outreach-move16.yaml). Full research audit: [`move16-research-2026-05-28.md`](move16-research-2026-05-28.md).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("sixteen outreach waves to date") are fine.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #16 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Identity-load-bearing framing.** URML's substrate-neutral claim has been implicit in prior moves; Move #16 makes it explicit by engaging the substrate maintainers themselves. Where Moves #10-15 engaged sensor / VLA / actuator / vertical layers above the substrate, Move #16 engages the substrate-runtime spine URML composes above.

**Special milestones:**
- RFC-0200 ROS 2 core — **the most identity-load-bearing engagement** (URML's primary substrate maintainers).
- ORB-SLAM3 RFC-0206 GPL-3.0 → cross-citation framing.
- Cyclone DDS / Zenoh / iceoryx (Eclipse Foundation × 3) — sibling engagements with shared substrate-license-class concerns.

---

## Tier A — 12 foundation-direct / vendor-direct targets

### Drone autopilot + protocol substrate (4)

### RFC-0196: PX4-Autopilot
**Post to:** https://github.com/PX4/PX4-Autopilot/issues/new (Issues enabled). Body TBD when RFC drafts. The dominant open drone-autopilot stack; foundation-direct via Dronecode.

### RFC-0197: MAVLink
**Post to:** https://github.com/mavlink/mavlink/issues/new (Issues enabled). Body TBD. Drone protocol substrate; LGPL-3.0 + MIT exception.

### RFC-0198: MAVSDK
**Post to:** https://github.com/mavlink/MAVSDK/issues/new (Issues enabled). Body TBD. High-level MAVLink SDK; BSD-3-Clause.

### RFC-0199: DroneCAN
**Post to:** https://github.com/dronecan/libcanard/issues/new (Issues enabled). Body TBD. Alternative CAN-protocol substrate for drone embedded networks.

### ROS 2 + Nav2 + MoveIt 2 (3)

### RFC-0200: ROS 2 core
**Post to:** https://github.com/ros2/ros2/issues/new (Issues enabled). Body TBD. **URML's primary substrate.** Round-200 milestone RFC.

### RFC-0201: Nav2
**Post to:** https://github.com/ros-navigation/navigation2/issues/new (Issues enabled). Body TBD. ROS 2 navigation stack.

### RFC-0202: MoveIt 2
**Post to:** https://github.com/moveit/moveit2/issues/new (Issues enabled). Body TBD. ROS 2 manipulation framework.

### DDS / middleware (2)

### RFC-0203: eProsima Fast DDS
**Post to:** https://github.com/eProsima/Fast-DDS/issues/new (Issues enabled). Body TBD. ROS 2's default DDS implementation.

### RFC-0204: Eclipse Cyclone DDS
**Post to:** https://github.com/eclipse-cyclonedds/cyclonedds/issues/new (Issues enabled). Body TBD. Alternative DDS; EPL-2.0 cross-citation framing.

### SLAM upstreams (3)

### RFC-0205: Google Cartographer
**Post to:** https://github.com/cartographer-project/cartographer/issues/new (Issues enabled). Body TBD. 2D/3D SLAM upstream.

### RFC-0206: ORB-SLAM3
**Post to:** https://github.com/UZ-SLAMLab/ORB_SLAM3/issues/new (Issues enabled). Body TBD. Visual-SLAM canonical reference; GPL-3.0 → cross-citation framing.

### RFC-0207: RTAB-Map
**Post to:** https://github.com/introlab/rtabmap/issues/new (Issues enabled). Body TBD. Visual-inertial SLAM; mixed-license clarification.

---

## Tier B — 4 research-collab / cross-citation targets

### RFC-0208: QGroundControl
**Post to:** https://github.com/mavlink/qgroundcontrol/issues/new (Issues + Discussions enabled). Body TBD. Ground-station / mission-planning UI; operator-control surface.

### RFC-0209: Eclipse Zenoh
**Post to:** https://github.com/eclipse-zenoh/zenoh/issues/new (Issues enabled). Body TBD. Next-gen pub-sub overlay; substrate-emerging.

### RFC-0210: Eclipse iceoryx
**Post to:** https://github.com/eclipse-iceoryx/iceoryx/issues/new (Issues enabled). Body TBD. Zero-copy IPC for ROS 2 intra-process.

### RFC-0211: Stella VSLAM
**Post to:** https://github.com/stella-cv/stella_vslam/issues/new (Issues enabled). Body TBD. Community fork of archived OpenVSLAM; license-clarification.

---

## Tier C (8) — recorded in research file, NOT engaged

See [`move16-research-2026-05-28.md`](move16-research-2026-05-28.md) for the full Tier-C list:

- **Already engaged × 6:** ArduPilot (Move-2 RFC-0041 declined), micro-ROS (Move-13 RFC-0177), Open-RMF (Move-2 RFC-0053), Gazebo (Move-2 RFC-0037), isaac-sim (Move-2 RFC-0050), mujoco_playground (Move-11 RFC-0144).
- **Archived × 1:** OpenVSLAM (Stella VSLAM RFC-0211 is the maintained community fork).
- **Covered via parent governance × 1:** Auterion (commercial PX4 downstream; engagement at PX4 RFC-0196 covers upstream).
