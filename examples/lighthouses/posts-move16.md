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

Copy-paste-ready Issue bodies for the Move #16 outreach. **Wave shape**: 16 verified Theme A targets (12 Tier A + 4 Tier B), verified 2026-05-28. RFC numbers 0196-0211. **URML's biggest wave so far** — substrate-spine is the broadest market with the most open-source defaults.

Ledger state: [`outreach-move16.yaml`](outreach-move16.yaml). Full research audit: [`move16-research-2026-05-28.md`](move16-research-2026-05-28.md). RFCs on main via PRs #202 (Batch 1), #203 (Batch 2), #205 (Batch 3).

Voice: founder posts under his GitHub identity. Each post opens with "Hi <team>" and addresses the maintainers directly.

**Confidentiality discipline.** Per the outreach-confidentiality rule, public post bodies do NOT name or link to previously engaged URML maintainers as social proof. URML's own shipped artifacts and RFCs in `docs/rfcs/` are fine to cite. Aggregate counts ("sixteen outreach waves to date") are fine.

**Authoring disclosure.** Per [`AGENTS.md`](../../AGENTS.md) line 67 + [`VIBE.md`](../../VIBE.md), every Move #16 post ends with the shortened authoring-disclosure line.

**Disclosure paragraph (reused verbatim at the bottom of every post body):**

```
*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

**Identity-load-bearing framing.** URML's substrate-neutral claim has been implicit in prior moves; Move #16 makes it explicit by engaging the substrate maintainers themselves.

**Schema-extension flags surfaced by this wave** (queued as future Spec RFCs, not part of Move-16 outreach itself):

- `substrate.autopilot_class` enum (PX4 / Ardupilot / Pixhawk)
- `substrate.rmw_implementation` enum (Fast DDS / Cyclone DDS / Zenoh)
- `substrate.ipc_substrate` enum (iceoryx / iceoryx2)
- `substrate.maturity_tier` enum (production / emerging / experimental)
- `perception.slam_substrate` enum (Cartographer / ORB-SLAM3 / RTAB-Map / Stella VSLAM)
- `operator_control_surface` enum (QGroundControl / others)
- `protocol.embedded_class` enum (MAVLink / DroneCAN)
- `perception.slam_substrate.lineage` field (community-fork lineage)

---

## Tier A — 12 foundation-direct / vendor-direct targets

### Drone autopilot + protocol substrate (4)

### RFC-0196: PX4-Autopilot
**Post to:** https://github.com/PX4/PX4-Autopilot/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on PX4 capability-manifest mapping

**Body:**

Hi PX4 team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. It sits above runtime substrates and compiles natural-language sentences into validated, runnable robot programs. PX4 is name-checked as a first-class substrate alongside ROS 2 in URML's architecture document; the drone reference-runtime track is the second after `ros2-runtime`.

This is a **proposal-only** RFC, posted as part of URML's Move #16 outreach (substrate-spine wave, 16 engageable RFCs across drone autopilot + ROS 2 + DDS + SLAM upstreams). Move #16 makes URML's substrate-neutral claim explicit by engaging the substrate maintainers themselves; PX4 / Dronecode-direct engagement is RFC-0196's anchor — the opening RFC of the wave.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0196-px4-autopilot-outreach.md

URML's planned `px4_multirotor_cell.yaml` fixture declares PX4 as the autopilot substrate. URML's drone profile (RFC-0008) dispatches the mobility primitives (`take_off`, `move_to`, `land`) onto PX4 via MAVLink. The engagement is foundation-direct at the Linux Foundation Dronecode layer to cover upstream PX4 and downstream commercial distributions in one conversation.

Asks for the PX4 / Dronecode maintainers (RFC has the full list; the highest-leverage ones below):

1. **Autopilot-substrate-class manifest field.** URML's v0.1 has no autopilot-substrate enum. From the PX4 perspective — preferred enum value (`px4`, `pixhawk`) and how should the field accommodate the Ardupilot parallel set?
2. **Flight-mode enumeration.** Offboard / mission / position / altitude / manual — is the PX4 set the right reference for URML's manifest field, or should the field be substrate-neutral with PX4-specific values?
3. **Geofence + safety-mode binding.** Should URML's `safety_envelope.geofence` bind to PX4's geofence + failsafe modes at validate time, execute time, or both?
4. **Adapter home.** URML repo (`reference/drone-runtime/PX4MAVLinkAdapter`), PX4-maintained, or external?
5. **MAVLink-via-PX4 vs direct MAVLink boundary.** Where should URML's manifest draw the line between "targets PX4" and "targets MAVLink directly" (Ardupilot or custom autopilot) — substrate field vs protocol field semantics?
6. **Conformance listing.** Would PX4 / Dronecode consider a README link to URML's compatible-runtimes registry (RFC-0014) once a working bridge ships?
7. **Anything else.**

Happy to scope down, deepen, or shelve as fits. Thanks for the patient build over the years.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0197: MAVLink
**Post to:** https://github.com/mavlink/mavlink/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on MAVLink protocol-substrate manifest mapping

**Body:**

Hi MAVLink team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's drone runtime track composes onto PX4 / Ardupilot via MAVLink as the protocol substrate; the engagement is at the protocol-grammar layer, not the autopilot stack itself.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling RFCs cover PX4 (RFC-0196 autopilot substrate) and MAVSDK (RFC-0198 high-level SDK).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0197-mavlink-outreach.md

URML's manifest declares MAVLink as the autopilot-control protocol class for drone deployments. The LGPL-3.0 protocol-grammar layer plus the MIT generated-code exception makes URML's adapter pattern clean: URML composes against the generated bindings (MIT) at the API boundary, and the protocol-grammar surface (LGPL-3.0) is referenced rather than embedded.

Asks for the MAVLink maintainers:

1. **Protocol-class enum.** URML's manifest has no protocol-class enum today. Preferred value (`mavlink`, `mavlink_v2`)?
2. **MAVLink version manifest field.** v1 vs v2 — manifest declaration shape, and forward-compat with future revisions?
3. **Dialect declaration.** common / ardupilotmega / development / custom — manifest field shape; should URML declare a single dialect or a dialect-list?
4. **Signing posture.** MAVLink 2 message signing — should URML's `security` block declare signing-enabled and key-management posture at validate time?
5. **Multi-system topology.** system_id / component_id semantics — should URML's manifest declare the topology graph (single-system, ground-station + autopilot, multi-vehicle)?
6. **Conformance listing.** Would the MAVLink project consider a README link to URML's compatible-runtimes registry (RFC-0014) once URML's manifest mapping stabilizes?
7. **Anything else.**

Thanks for the protocol that lets the entire drone ecosystem talk.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0198: MAVSDK
**Post to:** https://github.com/mavlink/MAVSDK/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on MAVSDK SDK-substrate manifest mapping

**Body:**

Hi MAVSDK team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's drone-runtime track targets MAVSDK as the natural high-level SDK boundary for cross-vendor vehicle control.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling RFCs cover PX4 (RFC-0196) and MAVLink protocol (RFC-0197); MAVSDK is the SDK layer where URML's drone-adapter naturally composes.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0198-mavsdk-outreach.md

URML's manifest declares MAVSDK as the SDK substrate. URML's planned `reference/drone-runtime/` composes against the MAVSDK API surface — BSD-3-Clause makes this a clean Apache-2.0 fit at the source level.

Asks for the MAVSDK maintainers:

1. **SDK-substrate enum value.** URML's manifest enum value preference (`mavsdk`, `mavlink_mavsdk`)?
2. **MAVSDK version manifest field.** Per-deployment version pinning — does the MAVSDK team have a recommended version-declaration convention?
3. **Plugin / capability set declaration.** Action / mission / offboard / telemetry / param — should URML's manifest declare which MAVSDK plugin set is expected and let the validator enforce the manifest-vs-runtime check?
4. **Offboard-mode declaration.** Offboard control is the highest-power MAVSDK mode and the most safety-critical; should URML's manifest declare offboard-mode-required as an explicit capability for envelope-binding?
5. **Language-binding manifest field.** MAVSDK supports C++, Python, Go, Swift, Java, Rust bindings — URML's preferred manifest field shape?
6. **Adapter home.** URML repo (`reference/drone-runtime/MAVSDKAdapter`), MAVSDK-maintained, or cross-citation only?
7. **Conformance listing.** Would the MAVSDK project consider a README link to URML's compatible-runtimes registry (RFC-0014) once a working adapter ships?
8. **Anything else.**

Thanks for the SDK that makes cross-vendor drone control real.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0199: DroneCAN libcanard
**Post to:** https://github.com/dronecan/libcanard/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on DroneCAN protocol-substrate manifest mapping

**Body:**

Hi DroneCAN team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's drone-runtime track declares the protocol substrate as a manifest field; DroneCAN is the alternate-protocol substrate for drone embedded networks (CAN-bus) complementary to MAVLink for serial / UDP topologies.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). DroneCAN is one of three protocol-substrate engagements in Batch 1 (PX4 RFC-0196 autopilot, MAVLink RFC-0197 default protocol, DroneCAN RFC-0199 embedded protocol).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0199-dronecan-libcanard-outreach.md

URML's manifest declares `protocol.embedded_class: dronecan` for CAN-bus drone deployments. The MIT license on libcanard makes the URML adapter posture clean. The engagement is at the protocol-grammar layer (DSDL message definitions) and the embedded-network topology declaration.

Asks for the DroneCAN maintainers:

1. **Protocol-substrate enum value.** URML's manifest enum value preference (`dronecan`, `drone_can`)?
2. **DroneCAN version manifest field.** v0 vs v1 (UAVCAN v1 lineage) — manifest field shape for protocol-version declaration?
3. **Node-ID + DSDL dialect declaration.** Manifest field for node-ID space + DSDL dialect (standard / vendor-specific)?
4. **CAN-FD vs classic CAN.** Should URML's manifest declare transport-physical-layer at validate time, or leave it deployment-time?
5. **MAVLink-vs-DroneCAN co-existence.** Mixed-protocol deployments are common (MAVLink autopilot + DroneCAN ESCs); URML's preferred manifest shape for declaring multi-protocol topology?
6. **Adapter home.** Future URML `reference/drone-runtime/DroneCANAdapter` candidate via libcanard; preferred adapter home?
7. **Conformance listing.** Would the DroneCAN project consider a README link to URML's compatible-runtimes registry (RFC-0014) once a working adapter ships?
8. **Anything else.**

Thanks for keeping the embedded-network protocol open and active.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### ROS 2 + Nav2 + MoveIt 2 (3)

### RFC-0200: ROS 2 core
**Post to:** https://github.com/ros2/ros2/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on ROS 2 capability-manifest mapping (URML's primary substrate)

**Body:**

Hi ROS 2 team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. **ROS 2 is URML's primary substrate.** URML ships a ROS 2 reference runtime (`reference/ros2-runtime/`) that translates URML programs into rclpy actions, services, and topics; every URML demo touching a real robot threads through ROS 2.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). **RFC-0200 is the most identity-load-bearing engagement in Move-16** — URML's substrate-neutral claim is only credible if engaged explicitly with the primary substrate's maintainers themselves.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0200-ros2-core-outreach.md

URML's manifest declares `substrate.class: ros2` plus distro + RMW implementation. The reference runtime already exists; this RFC formalizes the engagement-channel upstream at the foundation layer rather than adding new code.

Asks for the ROS 2 / OSRF maintainers:

1. **Distro-evolution manifest semantics.** What does ROS 2 distro lifecycle look like in URML's manifest field? Per-distro EOL signaling needed at validate time?
2. **RMW-implementation substitution surface.** Manifest field, launch param, env var, or per-node component-container? URML's preferred default surface.
3. **Composable-node declaration.** Should URML's manifest declare intent-to-compose, or is composition always launch-time?
4. **Action vs service dispatch.** Per-primitive override at the manifest layer, or always ROS 2-side?
5. **Adapter home.** `reference/ros2-runtime/` lives in URML's repo today; long-term home — OSRF, Open Robotics Foundation, future URML Foundation, or some combination?
6. **REP / PEP cross-link.** Is there an existing REP or PEP that URML's manifest field semantics should align with explicitly?
7. **Conformance listing.** Would the ROS 2 ecosystem consider a `ros.org` link to URML's compatible-runtimes registry (RFC-0014)?
8. **Anything else.**

Sibling Move-16 RFCs cover Nav2 (RFC-0201), MoveIt 2 (RFC-0202), Fast DDS (RFC-0203), Cyclone DDS (RFC-0204), Zenoh (RFC-0209), and iceoryx (RFC-0210) — the ROS 2 stack URML composes onto.

Thanks for the middleware that makes modern robotics composable.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0201: Nav2
**Post to:** https://github.com/ros-navigation/navigation2/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on Nav2 capability-manifest mapping

**Body:**

Hi Nav2 / ROS 2 Navigation Working Group,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's mobility primitives (`move_to`, `dock`, `scan_area`) dispatch via Nav2 in every ROS 2 mobile-base example URML ships.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling RFCs cover ROS 2 core (RFC-0200) and MoveIt 2 (RFC-0202).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0201-nav2-outreach.md

URML's manifest declares `mobility.dispatch: nav2` plus planner / controller / costmap / recovery plugin sets. Nav2's behavior-tree-driven planning composes cleanly with URML's manifest-validated dispatch: URML validates intent before dispatch; Nav2 plans the trajectory and recovers from failure.

Asks for the Nav2 / ROS 2 Navigation Working Group maintainers:

1. **Behavior-tree composition manifest field.** Should URML's manifest declare a Nav2 behavior-tree XML reference, or is composition always Nav2-side?
2. **Plugin-set manifest fields.** Planner / controller / costmap / recovery plugin selection — manifest-level declaration, or always launch-param?
3. **Fleet-coordination layer.** Where does URML's multi-robot fleet manifest (RFC-0006 direction) meet Nav2's per-robot stack?
4. **Failure-mode declaration.** Should URML's manifest declare which Nav2 failure types are recoverable at manifest-validate vs Nav2-runtime time?
5. **Adapter home.** `reference/ros2-runtime/` (URML-maintained) targets Nav2 today; should Nav2-specific manifest mapping live in a Nav2-adjacent companion package?
6. **Conformance listing.** Would Nav2 / the ROS 2 Navigation Working Group consider a README link to URML's compatible-runtimes registry (RFC-0014) once a working Nav2 bridge ships?
7. **Anything else.**

Thanks for the navigation stack that lets mobile robots actually navigate.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0202: MoveIt 2
**Post to:** https://github.com/moveit/moveit2/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on MoveIt 2 capability-manifest mapping

**Body:**

Hi MoveIt 2 / MoveIt Working Group,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's manipulation primitives (`pick_from`, `place_at`, `grasp`, `release`, `swap_tool`) dispatch via MoveIt 2 in URML's industrial-arm, cobot, and humanoid runtime tracks.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling RFCs cover ROS 2 core (RFC-0200) and Nav2 (RFC-0201).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0202-moveit2-outreach.md

URML's manifest declares `manipulation.dispatch: moveit2` plus planning pipeline + planner ID + SRDF reference + collision-object scene. URML's industrial profile (RFC-0013) defines `pick_from` / `place_at` / `swap_tool`; MoveIt 2 is the natural dispatcher.

Asks for the MoveIt 2 / MoveIt Working Group maintainers:

1. **Planning-pipeline manifest field.** OMPL / CHOMP / STOMP / Pilz selection — manifest-level declaration, or always launch-param?
2. **SRDF + URDF reference convention.** Should URML's manifest declare both reference paths, or canonicalize via `robot_description` topic?
3. **Constraint-set envelope binding.** Should URML's `safety_envelope` bind to MoveIt 2 position / orientation / joint constraints at validate time?
4. **Multi-controller dispatch.** Trajectory + gripper controllers per primitive — URML's manifest field shape preference?
5. **Adapter home.** `reference/ros2-runtime/` (URML-maintained) targets MoveIt 2 today; should MoveIt 2-specific manifest mapping live in a MoveIt-adjacent companion package?
6. **MoveIt Task Constructor relationship.** Should URML compose against MoveIt 2 core or Task Constructor for high-level industrial primitives?
7. **Conformance listing.** Would MoveIt / the MoveIt Working Group consider a README link to URML's compatible-runtimes registry (RFC-0014)?
8. **Anything else.**

Thanks for the manipulation stack that makes ROS 2 arms productive.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### DDS / middleware (2)

### RFC-0203: eProsima Fast DDS
**Post to:** https://github.com/eProsima/Fast-DDS/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on Fast DDS RMW-substrate manifest mapping

**Body:**

Hi eProsima Fast DDS team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's ROS 2 reference runtime composes onto the RMW layer; Fast DDS has been the ROS 2 default RMW since Foxy, and URML's manifest needs an explicit RMW-implementation field for production-deployment determinism.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling RFCs cover Cyclone DDS (RFC-0204), Zenoh (RFC-0209), and iceoryx (RFC-0210) — the parallel middleware engagements.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0203-fast-dds-outreach.md

URML's manifest will declare `substrate.rmw_implementation: rmw_fastrtps_cpp` plus QoS profile fields (reliability / durability / history / deadline / lifespan). The Fast DDS team is the right group to validate URML's QoS-field shape against the OMG DDS specification.

Asks for the eProsima Fast DDS maintainers:

1. **RMW-implementation enum manifest field.** First-class manifest field shape — should the field value be `rmw_fastrtps_cpp` (verbose ROS 2-side) or `fastdds` (substrate-class-side)?
2. **QoS profile manifest field set.** Reliability / durability / history / deadline / lifespan — URML's preferred field set for manifest-level declaration?
3. **Discovery-Server topology declaration.** Should URML's manifest declare Simple Discovery vs Discovery Server vs partition-based scaling?
4. **DDS-Security profile manifest field.** Authentication + access-control profile reference — URML's manifest could declare a profile path; the Fast DDS team's preferred shape?
5. **Multi-RMW deployment.** Should URML's manifest support declaring multiple RMW implementations per deployment (Fast DDS for some namespaces, Cyclone DDS for others), or is one-RMW-per-deployment the right constraint?
6. **Conformance listing.** Would eProsima consider an `eprosima.com` link to URML's compatible-runtimes registry (RFC-0014)?
7. **Anything else.**

Thanks for the DDS implementation that powers most production ROS 2 deployments.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0204: Eclipse Cyclone DDS
**Post to:** https://github.com/eclipse-cyclonedds/cyclonedds/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on Cyclone DDS RMW-substrate manifest mapping

**Body:**

Hi Cyclone DDS team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's ROS 2 reference runtime is RMW-agnostic; Cyclone DDS is the principal Fast DDS alternative and the default in some downstream distributions (Autoware, Foxglove). URML's manifest needs to declare Cyclone DDS as the RMW implementation explicitly for these production deployments.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Cyclone DDS is one of three Eclipse Foundation engagements in Move-16 (Cyclone DDS + Zenoh RFC-0209 + iceoryx RFC-0210); the conversation may converge to a Foundation-level discussion.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0204-cyclone-dds-outreach.md

URML's EPL-2.0 → cross-citation framing at the API boundary: URML's Apache-2.0 adapter source does not embed Cyclone DDS source; URML composes at the RMW boundary cleanly.

Asks for the Eclipse Cyclone DDS maintainers:

1. **RMW-implementation enum manifest field.** Preferred value — `rmw_cyclonedds_cpp` (verbose ROS 2-side) or `cyclonedds` (substrate-class-side)?
2. **Cyclone DDS-XML configuration reference.** Should URML's manifest declare an XML reference path, or stay XML-config-agnostic?
3. **Network-partition manifest field.** Cyclone DDS supports partition-based topology; should URML's manifest declare partitions?
4. **Performance-tier hint fields.** `latency-budget` and `throughput-budget` QoS policies are Cyclone DDS strengths; should URML's manifest declare per-deployment performance hints?
5. **Eclipse Foundation-level engagement.** Is per-project Issue engagement the right first-contact channel, or should URML pursue an Eclipse Foundation-level project-collaboration conversation that spans Cyclone DDS + Zenoh + iceoryx?
6. **Cross-citation conventions.** URML proposes EPL-2.0 → API-boundary cross-citation in `reference/ros2-runtime/`; preferred attribution shape from the Cyclone DDS / Eclipse Foundation side?
7. **Conformance listing.** Would Cyclone DDS / the Eclipse Foundation consider a project link to URML's compatible-runtimes registry (RFC-0014)?
8. **Anything else.**

Thanks for the Eclipse Foundation DDS implementation.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### SLAM upstreams (3)

### RFC-0205: Google Cartographer
**Post to:** https://github.com/cartographer-project/cartographer/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on Cartographer SLAM-substrate manifest mapping

**Body:**

Hi Cartographer team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's perception manifest declares lidar, camera, and radar sensors today but does not yet declare a SLAM substrate. **RFC-0205 is URML's first SLAM-substrate engagement** and Cartographer is the anchor — the canonical 2D/3D real-time SLAM reference with native ROS 2 integration.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling RFCs cover ORB-SLAM3 (RFC-0206 visual-SLAM) and RTAB-Map (RFC-0207 visual-inertial); together they define URML's `perception.slam_substrate` enum.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0205-cartographer-outreach.md

URML's manifest will declare `perception.slam_substrate: cartographer` plus 2D vs 3D mode, Lua-configuration reference, sub-map publish cadence, and optimization budget hints.

Asks for the Cartographer maintainers:

1. **SLAM-substrate enum manifest field.** URML's first; Cartographer perspective on the enum value (`cartographer`, `google_cartographer`, `cartographer-2d` / `cartographer-3d`)?
2. **Lua-configuration reference convention.** Manifest-declared path, or always launch-param?
3. **2D vs 3D mode declaration.** Per-deployment mode field, or always Lua-config-side?
4. **Sub-map cadence + loop-closure budget hints.** URML's manifest could declare performance-tier hints; preferred shape from the Cartographer side?
5. **Pose-frame manifest field.** Tracking + published frames — manifest declaration or always TF2-side?
6. **Adapter home.** Future URML `reference/ros2-runtime/CartographerAdapter` candidate via `cartographer_ros`; preferred adapter home?
7. **Conformance listing.** Would the Cartographer project consider a README link to URML's compatible-runtimes registry (RFC-0014) once a working adapter ships?
8. **Anything else.**

Thanks for the SLAM reference everyone ends up benchmarking against.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0206: ORB-SLAM3
**Post to:** https://github.com/UZ-SLAMLab/ORB_SLAM3/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on ORB-SLAM3 visual-SLAM cross-citation

**Body:**

Hi UZ-SLAMLab / ORB-SLAM3 team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's perception manifest needs to declare a visual-SLAM substrate; ORB-SLAM3 is the canonical reference. Engagement is **cross-citation only at the API boundary** — GPL-3.0 prevents URML's Apache-2.0 adapter from embedding ORB-SLAM3 source, but URML's manifest can declare ORB-SLAM3 cleanly as the visual-SLAM substrate.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling RFCs cover Cartographer (RFC-0205 lidar SLAM) and RTAB-Map (RFC-0207 visual-inertial).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0206-orb-slam3-outreach.md

URML's manifest will declare `perception.slam_substrate: orb_slam3` plus the five operation modes (monocular / stereo / RGB-D / monocular-inertial / stereo-inertial), camera-calibration YAML reference, and ORB vocabulary file reference.

Asks for the UZ-SLAMLab / ORB-SLAM3 maintainers:

1. **SLAM-substrate enum value.** URML's manifest enum value preference (`orb_slam3`, `orbslam3`, `uz_orb_slam3`)?
2. **Five-mode enumeration shape.** Monocular / stereo / RGB-D / monocular-inertial / stereo-inertial — URML's manifest field shape: single `slam_mode` enum or `camera_topology` + `inertial_fusion` decomposed?
3. **Camera-calibration YAML reference convention.** Manifest-declared path or always launch-param?
4. **Vocabulary-file declaration.** Manifest field for path + size hint? Checksum-bind URML's validate step?
5. **GPL-3.0 cross-citation declaration.** Should URML's manifest itself declare a `license_bind: GPL-3.0` flag so downstream packagers see the constraint at validate time?
6. **Adapter home.** URML's adapter (if any) would live in a separately-licensed companion package (likely GPL-3.0); URML-side citation only — is this the right boundary?
7. **Conformance listing.** Would UZ-SLAMLab consider a README link to URML's compatible-runtimes registry (RFC-0014) as a cross-citation entry?
8. **Anything else.**

Thanks for the canonical visual-SLAM reference everyone learns from.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0207: RTAB-Map
**Post to:** https://github.com/introlab/rtabmap/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on RTAB-Map visual-inertial SLAM manifest mapping + license clarification

**Body:**

Hi IntRoLab / RTAB-Map team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's perception manifest declares lidar, camera, and radar sensors today but needs to declare a visual-inertial SLAM substrate; RTAB-Map is the production-friendly visual-inertial choice complementing Cartographer (lidar) and ORB-SLAM3 (canonical academic visual-SLAM reference).

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling RFCs cover Cartographer (RFC-0205), ORB-SLAM3 (RFC-0206), and Stella VSLAM (RFC-0211 community-fork).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0207-rtabmap-outreach.md

URML's manifest will declare `perception.slam_substrate: rtabmap` plus sensor-topology mode, database path, loop-closure threshold, and feature-detector selection. The license-clarification ask is gating: the repo is GitHub-classified as Other (mixed LGPL/BSD per README); URML adapter posture depends on per-module license clarity.

Asks for the IntRoLab / RTAB-Map maintainers:

1. **License clarification.** Per-module LGPL / BSD-3 boundary — can the README or LICENSE file declare per-directory licensing for downstream packager clarity?
2. **SLAM-substrate enum value.** URML's manifest enum value preference (`rtabmap`, `rtab_map`)?
3. **Database-path manifest field.** Persistent database is RTAB-Map's memory model; manifest declaration shape?
4. **Loop-closure-threshold field.** Performance-tier hint; preferred manifest shape?
5. **Feature-detector enumeration.** SURF / SIFT / ORB / BRIEF / KAZE / GFTT — manifest-declared, or always launch-param?
6. **Adapter home.** Future URML `reference/ros2-runtime/RTABMapAdapter` (in-repo, pending license clarity), RTAB-Map-side, or cross-citation only?
7. **Conformance listing.** Would IntRoLab consider a README link to URML's compatible-runtimes registry (RFC-0014) once a working adapter ships?
8. **Anything else.**

Thanks for the visual-inertial SLAM that people actually deploy.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

## Tier B — 4 research-collab / cross-citation targets

### RFC-0208: QGroundControl
**Post to:** https://github.com/mavlink/qgroundcontrol/issues/new (Issues + Discussions enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on QGroundControl operator-control-surface manifest mapping

**Body:**

Hi QGroundControl team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's drone runtime stack ends at the autopilot dispatch layer (PX4 / MAVLink / MAVSDK); the operator-control surface — ground-station UI, mission upload, telemetry display, manual override — is where production drone operators interact with the system. QGC is the canonical operator-control surface.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). QGC joins PX4 (RFC-0196), MAVLink (RFC-0197), and MAVSDK (RFC-0198) as the fourth Linux Foundation Dronecode engagement in Move-16. Cross-citation only — URML's runtime doesn't embed QGC; the engagement is at manifest-declaration layer.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0208-qgroundcontrol-outreach.md

URML's manifest will declare `operator_control_surface: qgroundcontrol` plus MAVLink message subset, `.plan` mission-file format, telemetry subset, and manual-override channel availability.

Asks for the QGC / Dronecode maintainers:

1. **Operator-control-surface enum manifest field.** URML's first; QGC perspective on the enum value (`qgroundcontrol`, `qgc`)?
2. **MAVLink message-subset declaration.** Manifest field for operator-side MAVLink subset (different from autopilot full set)?
3. **Plan-format declaration.** QGC `.plan` JSON format reference — manifest declaration shape?
4. **Telemetry-subset declaration.** Operator-displayed telemetry message subset for deployment-tier UI specification?
5. **Manual-override declaration.** Should URML's manifest declare manual-override channel availability as a deployment metadata field?
6. **Cross-citation discipline.** URML proposes cross-citation only (no in-repo adapter); preferred citation form from the QGC side (README link, COMPATIBILITY.md entry)?
7. **Conformance listing.** Would QGC / Dronecode consider a README link to URML's compatible-runtimes registry (RFC-0014) once URML's manifest fields stabilize?
8. **Anything else.**

Thanks for the ground-station that makes drone deployments operable.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0209: Eclipse Zenoh
**Post to:** https://github.com/eclipse-zenoh/zenoh/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on Zenoh substrate-emerging RMW manifest mapping

**Body:**

Hi Eclipse Zenoh team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's primary substrate is ROS 2 with DDS RMW; Zenoh is the substrate-emerging next-generation pub-sub overlay with `rmw_zenoh` under active development. URML's manifest could declare Zenoh as the substrate-emerging RMW choice for WAN-spanning + large-fleet scenarios where DDS discovery becomes a bottleneck.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Zenoh joins Cyclone DDS (RFC-0204) and iceoryx (RFC-0210) as the second of three Eclipse Foundation engagements in Move-16.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0209-zenoh-outreach.md

URML's manifest will declare `substrate.rmw_implementation: rmw_zenoh_cpp` plus a first-class `substrate.maturity_tier: emerging` field, Zenoh topology mode, and multi-protocol-bridge declaration (MQTT / Kafka / WebSocket).

Asks for the Eclipse Zenoh maintainers:

1. **Substrate-maturity-tier enum.** URML's first; preferred manifest value for Zenoh (`emerging`, `experimental`, `production-ready`)?
2. **RMW-implementation enum value.** `rmw_zenoh_cpp` (verbose) or `zenoh` (substrate-class-side)?
3. **Zenoh-mode topology declaration.** peer / client / router — manifest field shape?
4. **Multi-protocol-bridge declaration.** MQTT / Kafka / WebSocket bridges — should URML's manifest declare bridge-set as a list, or as separate fields per bridge?
5. **Router endpoint URI list.** Production router topology requires URI list; URML's preferred field shape?
6. **Eclipse Foundation-level engagement.** Is per-project Issue engagement the right first-contact, or should URML pursue Eclipse Foundation project-collaboration that spans Cyclone DDS + Zenoh + iceoryx?
7. **Conformance listing.** Would Zenoh / Eclipse Foundation consider a project link to URML's compatible-runtimes registry (RFC-0014)?
8. **Anything else.**

Thanks for the next-generation pub-sub that the ROS 2 community is actively evaluating.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0210: Eclipse iceoryx
**Post to:** https://github.com/eclipse-iceoryx/iceoryx/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on iceoryx IPC-sub-substrate manifest mapping

**Body:**

Hi Eclipse iceoryx team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's substrate manifest declares the RMW middleware class today but does not declare the IPC sub-substrate. iceoryx provides true zero-copy IPC for ROS 2 intra-process communication and is the standard transport for high-frequency-large-payload paths (camera images, lidar point clouds). URML's high-throughput deployments need the IPC sub-substrate explicit.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). iceoryx joins Cyclone DDS (RFC-0204) and Zenoh (RFC-0209) as the third of three Eclipse Foundation engagements in Move-16.

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0210-iceoryx-outreach.md

URML's manifest will declare `substrate.ipc_substrate: iceoryx` plus generation (iceoryx1 vs iceoryx2), shared-memory pool budget hints, pub/sub count budgets, and RouDi runtime name.

Asks for the Eclipse iceoryx maintainers:

1. **IPC-substrate enum manifest field.** URML's first; preferred enum value (`iceoryx`, `eclipse_iceoryx`)?
2. **IPC-generation field.** iceoryx1 vs iceoryx2 — manifest field shape, and timing of URML's recommended generation default?
3. **Memory-pool budget hint shape.** Shared-memory budget is deployment-critical; URML's preferred manifest hint format?
4. **RouDi runtime name declaration.** Manifest field for the iceoryx daemon name, or always launch-side?
5. **Per-pub / per-sub limit declaration.** Should URML's manifest declare `max_publisher_count` / `max_subscriber_count` budgets for envelope-validation?
6. **iceoryx2 migration path.** Does the iceoryx team have a position on URML's manifest declaring the migration intent (e.g. `ipc_generation: iceoryx2-preferred-fallback-iceoryx1`)?
7. **Conformance listing.** Would iceoryx / the Eclipse Foundation consider a project link to URML's compatible-runtimes registry (RFC-0014)?
8. **Anything else.**

Thanks for the zero-copy IPC that makes high-throughput ROS 2 possible.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

### RFC-0211: Stella VSLAM
**Post to:** https://github.com/stella-cv/stella_vslam/issues/new (Issues enabled)

**Title:** URML (substrate-neutral robot intent language) — RFC requesting feedback on Stella VSLAM community-fork manifest mapping + license clarification

**Body:**

Hi stella-cv team,

URML (urml.dev) is a small, opinionated, human-readable language for describing robot intent — Apache-2.0, substrate-neutral by design. URML's visual-SLAM enum needs to include Stella VSLAM as an alternative to ORB-SLAM3 because production users with deployed OpenVSLAM infrastructure migrated here when OpenVSLAM was archived; URML's manifest should reflect that lived reality.

This is a **proposal-only** RFC, posted as part of URML's Move #16 substrate-spine wave (16 engageable RFCs). Sibling SLAM RFCs cover Cartographer (RFC-0205), ORB-SLAM3 (RFC-0206), and RTAB-Map (RFC-0207).

Full RFC: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0211-stella-vslam-outreach.md

URML's manifest will declare `perception.slam_substrate: stella_vslam` plus a first-class `lineage: openvslam` field (URML's first lineage-declaration field, capturing community-fork provenance). License clarification on the repo classification is the gating fact — the repo is GitHub-classified as Other, and the OpenVSLAM archive history was license-driven, so explicit OSI declaration would unlock URML's adapter posture.

Asks for the Stella VSLAM / stella-cv maintainers:

1. **License clarification.** Can the repo declare an explicit OSI license (BSD-3-Clause / Apache-2.0 / similar), or is cross-citation-only the right default for now?
2. **Lineage-declaration field.** URML's first `lineage` manifest field — preferred shape for declaring the OpenVSLAM-derived continuation?
3. **SLAM-substrate enum value.** URML's manifest enum value preference (`stella_vslam`, `stella-vslam`, `stellavslam`)?
4. **Three-mode enumeration sharing.** Should URML's `slam_mode` enum be shared across Stella VSLAM and ORB-SLAM3 (single visual-SLAM enum), or per-substrate-specialized?
5. **Vocabulary file declaration.** ORB vocabulary reference — manifest-field convention preference?
6. **AIST / academic-lineage attribution.** Does the Stella VSLAM team want URML to declare AIST academic-lineage attribution in the manifest itself?
7. **Conformance listing.** Would stella-cv consider a README link to URML's compatible-runtimes registry (RFC-0014) once license clarifies?
8. **Anything else.**

Thanks for keeping the OpenVSLAM continuation maintained.

Ido Yahalomi (URML maintainer, urml.dev, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*

---

## Tier C (8) — recorded in research file, NOT engaged

See [`move16-research-2026-05-28.md`](move16-research-2026-05-28.md) for the full Tier-C list:

- **Already engaged x 6:** ArduPilot (Move-2 RFC-0041 declined), micro-ROS (Move-13 RFC-0177), Open-RMF (Move-2 RFC-0053), Gazebo (Move-2 RFC-0037), isaac-sim (Move-2 RFC-0050), mujoco_playground (Move-11 RFC-0144).
- **Archived x 1:** OpenVSLAM (Stella VSLAM RFC-0211 is the maintained community fork).
- **Covered via parent governance x 1:** Auterion (commercial PX4 downstream; engagement at PX4 RFC-0196 covers upstream).
