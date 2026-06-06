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

# Move #32 post bodies: the marine / underwater wave

Eight targets. Post under idoco2003 via the channel noted per row (Discussion or
Issue). No license-ask (state the license; Stonefish is GPL-3.0, BlueOS
AGPL-3.0+custom — URML integrates over the ROS 2 / MAVLink surface and ships
nothing under those licenses). AI-assisted-authoring disclosure up front. At
post time, query the repo's real Discussion category id (Move #30 procedure).

---

## RFC-0396: blue (Robotic Decision Making Lab)

**Post to (Discussion):** https://github.com/Robotic-Decision-Making-Lab/blue/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above blue (BlueROV2) — request for comment

```
Hi Robotic Decision Making Lab,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches to whatever runs below. blue is the closest external analog to URML's own marine-runtime, which already drives a BlueROV2 over ArduSub/MAVLink — so I am writing because we are building toward the same substrate from two directions.

Nothing here asks the lab to adopt, host, or maintain anything. This is a request for comment, and genuinely a design question.

URML's marine-runtime targets the same BlueROV2 / ArduSub pairing blue orchestrates, and its ROS 2 runtime meets blue on the ROS 2 side. Your auv_controllers (AUV/UVMS on ros2_control) is the control seam URML dispatches validated motion intent to — the same ros2_control framing URML engaged earlier; your angler (vehicle-manipulator systems) is where URML's manipulation primitives extend underwater. The point of the layer is validate-before-actuate: a command outside the declared depth rating, thruster envelope, or comms regime is refused before it reaches a thruster.

Three real questions: (1) What should a URML capability manifest declare to honestly describe an underwater vehicle — depth rating, thruster/actuator configuration, buoyancy/ballast, tether vs untethered comms, current/visibility limits? (2) Is a validated natural-language intent layer above blue interesting for the lab's BlueROV2 / UVMS work? (3) Where is the cleanest seam — the ROS 2 interface, or the auv_controllers ros2_control layer?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0396-blue-rdml-outreach.md

Thanks for blue / auv_controllers / angler; a clean, open ROS 2 underwater stack is exactly what a neutral intent layer wants to sit above honestly.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0397: orca4

**Post to (Issue — Discussions not enabled):** https://github.com/clydemcqueen/orca4/issues/new
**Title:** URML (open robot intent language): a validated intent layer above orca4 — request for comment

```
Hi orca4 maintainer,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it turns an English sentence into a typed primitive, validates it against a capability manifest and a safety envelope, then dispatches. orca4 is the exact vehicle + flight-controller + navigation pairing URML's marine-runtime targets — a BlueROV2 on ArduSub + Nav2 + mavros — so I am writing.

Nothing here asks orca4 to adopt, host, or maintain anything. This is a request for comment.

URML's marine-runtime drives a BlueROV2 over ArduSub/MAVLink; on the ROS 2 side, orca4's Nav2 navigation is reached by URML's move_to (Nav2 is already a URML substrate), so "go to this waypoint at depth and report" maps cleanly. Validate-before-actuate refuses a request outside the declared depth rating or mission envelope before it dispatches — useful for an untethered AUV mission. The split between a URML navigation intent and orca4's mission logic is a genuine design question.

Two real questions: (1) What should a URML manifest declare to describe a BlueROV2-class AUV mission honestly (depth rating, mission/area bounds, battery/endurance, comms regime)? (2) Where is the right seam — URML move_to onto orca4's Nav2, or higher at the mission level?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0397-orca4-outreach.md

Thanks for orca4; one of the cleanest open BlueROV2 autonomy stacks out there.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0398: BlueOS (Blue Robotics)

**Post to (Discussion):** https://github.com/bluerobotics/BlueOS/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer over the MAVLink surface BlueOS hosts — request for comment

```
Hi BlueOS / Blue Robotics community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML's marine-runtime already drives a BlueROV over ArduSub/MAVLink — the surface BlueOS hosts on the companion computer — so BlueOS is the onboard layer directly beneath URML's existing BlueROV target, and I want to check where a validated-intent layer should sit relative to it.

Nothing here asks BlueOS to adopt, host, or maintain anything. This is a request for comment.

A validated URML program (navigate, hold depth, capture, report) lowers to the MAVLink commands BlueOS routes to the autopilot. The point is validate-before-actuate: a request outside the declared capability manifest (depth rating, thruster config, tether/comms regime) is refused before a command reaches the vehicle. URML does not replace BlueOS; it sits above the MAVLink BlueOS exposes.

Two real questions: (1) Is the MAVLink/ArduSub surface BlueOS exposes the right seam for an external validated-intent layer, or is there a higher-level BlueOS service interface that is more natural? (2) What should a URML manifest declare to describe a BlueROV / BlueBoat honestly (depth rating, thruster configuration, tether vs untethered, payload sensors)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0398-blueos-outreach.md

Thanks for BlueOS; an open onboard platform for accessible underwater robots is a great thing for the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0399: Stonefish

**Post to (Issue — Discussions not enabled):** https://github.com/patrykcieslak/stonefish/issues/new
**Title:** URML (open robot intent language): driving a Stonefish vehicle from validated intent — request for comment

```
Hi Stonefish maintainer,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches to the substrate below. Stonefish is interesting to URML as a high-fidelity underwater sim with a ROS 2 package (stonefish_ros) — a place a URML-validated command can drive a vehicle before any hardware is involved.

Nothing here asks Stonefish to adopt, host, or maintain anything. This is a request for comment.

A URML program drives a Stonefish vehicle through stonefish_ros, the same ROS 2 surface URML's runtime already targets. The hermetic, sim-first posture matches URML's own (its mock substrate proves the language end to end with no hardware). URML's optional validation block records the simulation-fidelity context a deployment was checked in, which Stonefish's hydrodynamics make concrete; validate-before-actuate behaves identically in sim and on hardware.

Two real questions: (1) Is a validated natural-language intent layer above Stonefish interesting as a demonstration / teaching surface for underwater scenarios? (2) What should a URML manifest declare to describe an underwater deployment honestly (depth rating, buoyancy/ballast, thruster configuration, current and visibility limits)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0399-stonefish-outreach.md

Thanks for Stonefish; a serious open marine-robotics simulator is a real asset.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0400: DAVE (IOES-Lab)

**Post to (Issue):** https://github.com/IOES-Lab/dave/issues/new
**Title:** URML (open robot intent language): driving a DAVE vehicle from validated intent — request for comment

```
Hi IOES-Lab DAVE maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. DAVE is interesting to URML as an open, ROS 2 / Gazebo underwater simulation and test environment for AUVs and manipulators — a place a URML-validated command can drive a vehicle with no hardware.

Nothing here asks DAVE to adopt, host, or maintain anything. This is a request for comment.

A URML program drives a DAVE vehicle through its ROS 2 / Gazebo interface, the same ROS 2 surface URML's runtime already targets; the sim-first posture matches URML's own. URML's optional validation block records the simulation-fidelity context; DAVE's underwater environment and sensor models make it concrete. Validate-before-actuate behaves identically in sim and on hardware.

Two real questions: (1) Is a validated natural-language intent layer above DAVE interesting as a demonstration / test surface for underwater scenarios? (2) What should a URML manifest declare to describe an underwater deployment honestly (depth rating, buoyancy, thruster configuration, current/visibility limits)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0400-dave-outreach.md

Thanks for keeping DAVE alive and on modern ROS 2 / Gazebo; an open underwater test bed is genuinely valuable.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0401: HoloOcean

**Post to (Issue — Discussions not enabled):** https://github.com/byu-holoocean/holoocean-ros/issues/new
**Title:** URML (open robot intent language): driving a HoloOcean AUV from validated intent — request for comment

```
Hi HoloOcean maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. holoocean-ros is interesting to URML as the ROS 2 bridge onto a UE5 underwater simulator (HoloOcean 2.0 adds ROS 2 + Fossen dynamics) — the permissively-licensed seam where a URML-validated command can drive a simulated AUV.

Nothing here asks HoloOcean to adopt, host, or maintain anything. This is a request for comment.

A URML program drives a HoloOcean AUV through holoocean-ros, the same ROS 2 surface URML's runtime already targets; the UE5 sim core stays where it is. URML's optional validation block records the simulation-fidelity context, which HoloOcean's Fossen dynamics and sonar/imaging models make concrete. Validate-before-actuate behaves identically in sim and on hardware.

Two real questions: (1) Is a validated natural-language intent layer above HoloOcean interesting as a demonstration / teaching surface for underwater scenarios? (2) What should a URML manifest declare to describe a HoloOcean AUV honestly (depth rating, dynamics class, sensor suite, current limits)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0401-holoocean-outreach.md

Thanks for HoloOcean and the ROS 2 bridge; high-fidelity underwater sim in the open is a great on-ramp.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0402: MARUS (LABUST)

**Post to (Issue — Discussions not enabled):** https://github.com/MARUSimulator/marus-core/issues/new
**Title:** URML (open robot intent language): driving a MARUS vessel from validated intent — request for comment

```
Hi MARUS / LABUST maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. marus-core is interesting to URML as a Unity-based marine simulator with ROS 2 support (via a gRPC adapter), covering surface and underwater vessels — a clean, permissively-licensed seam for a URML demonstration.

Nothing here asks MARUS to adopt, host, or maintain anything. This is a request for comment.

A URML program drives a MARUS surface or underwater vessel through the ROS 2 (grpc_ros_adapter) interface, the same ROS 2 surface URML's runtime already targets. URML's optional validation block records the simulation-fidelity context; MARUS's marine environment makes it concrete. The hermetic sim-first posture matches URML's own; validate-before-actuate behaves identically in sim and on hardware.

Two real questions: (1) Is a validated natural-language intent layer above MARUS interesting as a demonstration / teaching surface for marine scenarios (surface and underwater)? (2) What should a URML manifest declare to describe a marine vessel honestly (vehicle class, depth rating where applicable, thruster configuration, environmental limits)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0402-marus-outreach.md

Thanks for MARUS; an open Unity-based marine simulator that speaks ROS 2 is a great demonstration surface.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0403: ROS Maritime Working Group

**Post to (Issue on maritime_interfaces; or ROS Discourse Maritime category):** https://github.com/ros-maritime/maritime_interfaces/issues/new
**Title:** URML (open robot intent language): aligning a validated-intent layer with maritime_interfaces — request for comment

```
Hi ROS Maritime Working Group,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a natural-language request becomes a typed primitive, is validated against a capability manifest and a safety envelope, and only then dispatches over ROS 2. I am writing to the WG rather than a single vehicle because the interesting question is alignment with the shared maritime interfaces, not any one robot.

Nothing here asks the WG to adopt, host, or maintain anything; this is an alignment conversation.

URML primitives (move_to, detect, measure, report, and the marine vehicle path) lower onto ROS 2 actions/services. Where maritime_interfaces standardizes those messages, URML should target the standard rather than invent its own — exactly as it targets Nav2 and ros2_control elsewhere. URML adds the typed-intent + capability-manifest + safety-envelope validation layer above the interfaces: a request is validated against what a vessel declares it can do before it dispatches.

Two real questions: (1) Does URML's typed-intent layer map cleanly onto maritime_interfaces, and where should it target the standard interfaces rather than a generic ROS surface? (2) What should a URML capability manifest declare to describe a maritime vehicle in a way the WG would consider faithful (depth rating, thruster config, comms regime, environmental limits)? And is this alignment of interest as a Discourse thread or a meeting agenda item?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0403-ros-maritime-wg-outreach.md

Thanks for the Maritime WG; agreeing shared interfaces is exactly the layer a substrate-neutral intent vocabulary wants to align with rather than fragment.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
