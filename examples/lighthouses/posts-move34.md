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

# Move #34 post bodies: the aerial / drone-autonomy wave

Ten targets. Post under idoco2003 via the channel noted per row (Discussion or
Issue). No license-ask (state the license). AI-assisted-authoring disclosure up
front. At post time, query each Discussion repo's real category id (Move #30
procedure) for the five Discussion targets.

---

## RFC-0412: Aerostack2

**Post to (Discussion):** https://github.com/aerostack2/aerostack2/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above Aerostack2 — request for comment

```
Hi Aerostack2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. URML already ships an aerial drive type and a PX4 runtime, and PX4 is a URML substrate — so Aerostack2, which composes autonomous behaviors above the flight controller for one or many drones, sits at exactly the altitude URML targets.

Nothing here asks Aerostack2 to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets Aerostack2 on its behavior/action surface; "take off, fly the perimeter at 5 m, and inspect" becomes a typed primitive, validated against the declared flight envelope, and only then dispatched onto Aerostack2 behaviors. Validate-before-actuate refuses a request outside the declared altitude ceiling / geofence / speed before the drone arms. For multi-drone missions URML's fleet model is a roster with per-drone intent and a barrier for coordinated maneuvers.

Two real questions: (1) Is the ROS 2 behavior surface the right seam for an external validated-intent layer above Aerostack2, or is the mission level a better fit? (2) What should a URML capability manifest declare to describe an Aerostack2 platform honestly — drive type, altitude/speed limits, geofence, sensor/payload set, single vs multi-robot?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0412-aerostack2-outreach.md

Thanks for Aerostack2; an open ROS 2 framework for autonomous multi-aerial systems is exactly the right place for this kind of layer to be designed with input.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0413: MRS UAV System (CTU Prague)

**Post to (Discussion):** https://github.com/ctu-mrs/mrs_uav_system/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above the MRS UAV System — request for comment

```
Hi MRS UAV System maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML ships an aerial drive type and a PX4 runtime, and your system is one of the most complete open aerial-autonomy stacks there is, deployed on real outdoor multi-drone experiments — exactly the kind of platform a validated natural-language layer should sit above.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the MRS UAV manager on its control/tracker surface; "fly to this GPS point at 3 m/s and hold" lowers onto the trajectory/reference interface. Validate-before-actuate refuses a request outside the declared altitude/speed/area envelope before the drone arms. Your real multi-UAV deployment is where URML's fleet model fits: a roster with per-drone intent and a barrier for coordinated maneuvers.

Two real questions: (1) Is the ROS 2 control/tracker surface the right seam for an external validated-intent layer, or is the mission/manager level a better fit? (2) What should a URML capability manifest declare to describe an MRS-class UAV honestly — drive type, control modes, altitude/speed limits, geofence, estimator/positioning, single vs multi?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0413-mrs-uav-system-outreach.md

Thanks for the MRS UAV System; a complete, real-deployment open aerial stack is a rare and valuable thing.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0414: Crazyswarm2

**Post to (Discussion):** https://github.com/IMRCLab/crazyswarm2/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated fleet-intent layer above Crazyswarm2 — request for comment

```
Hi Crazyswarm2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML has an aerial drive type and a multi-robot fleet model, and a swarm of Crazyflie nano-quads is the cleanest possible exercise of that fleet model: many identical agents, one coordinated intent.

Nothing here asks Crazyswarm2 to adopt, host, or maintain anything. This is a request for comment.

URML's fleet model declares a roster of Crazyflies; per-agent aerial intent lowers onto the Crazyswarm2 ROS 2 surface, and a barrier coordinates a synchronized maneuver. Validate-before-actuate refuses a request outside the declared envelope — arena bounds, altitude, count — before any rotor spins. The nano-quad swarm is a high-value teaching and research demonstrator for validated multi-robot intent.

Two real questions: (1) Does URML's fleet model (roster + per-agent intent + barrier) map cleanly onto the Crazyswarm2 ROS 2 surface? (2) What should a URML capability manifest declare to describe a Crazyflie swarm honestly — per-drone drive type, arena geometry, altitude/speed limits, swarm size?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0414-crazyswarm2-outreach.md

Thanks for Crazyswarm2; an open ROS 2 stack for nano-quad swarms is a great demonstrator and teaching platform.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0415: RotorPy

**Post to (Issue — Discussions off):** https://github.com/spencerfolk/rotorpy/issues/new
**Title:** URML (open robot intent language): a validated intent layer above RotorPy — request for comment

```
Hi RotorPy maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML ships an aerial drive type, and RotorPy — a lightweight, hackable Python multirotor sim with realistic aerodynamics — is an ideal place to demonstrate a validated natural-language layer before any hardware.

Nothing here asks RotorPy to adopt, host, or maintain anything. This is a request for comment.

A URML aerial program (take off, fly a path, hover, land) drives a RotorPy vehicle through its Python control interface; URML's optional validation block records the simulation-fidelity context a run was checked in. Validate-before-actuate refuses an out-of-envelope request (altitude, speed) before the simulated motors spin — the same safety seam that protects real hardware, shown in a classroom-friendly setting. The sim-first posture matches URML's own (the reference runtime ships a mock substrate).

Two real questions: (1) Is a validated natural-language intent layer above RotorPy interesting as a teaching / research surface? (2) What should a URML capability manifest declare to describe a simulated multirotor honestly — drive type, altitude/speed limits, control modes — and is the Python control interface the right seam or is a higher-level mission API a better fit?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0415-rotorpy-outreach.md

Thanks for RotorPy; a clean, hackable Python quad sim is a genuinely useful teaching and research tool.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0416: Pegasus Simulator

**Post to (Discussion):** https://github.com/PegasusSimulator/PegasusSimulator/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above Pegasus Simulator — request for comment

```
Hi Pegasus Simulator maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML ships an aerial drive type and a PX4 runtime, and Pegasus pairs a high-fidelity Isaac Sim environment with the exact flight controller URML already targets — a natural sim-side home for a validated aerial intent layer.

Nothing here asks Pegasus to adopt, host, or maintain anything. This is a request for comment.

URML's aerial drive type and PX4 runtime drive a Pegasus vehicle through PX4 / the ROS 2 bridge inside Isaac Sim; "fly the survey grid at 10 m and return" lowers onto the same PX4 seam URML uses on hardware. URML's optional validation block records the simulation-fidelity context concretely (Isaac Sim + Pegasus dynamics). Validate-before-actuate refuses an out-of-envelope request before the simulated drone arms.

Two real questions: (1) Is the PX4 / ROS 2 bridge the right seam for an external validated-intent layer above Pegasus, given URML already targets PX4? (2) What should a URML capability manifest declare to describe a Pegasus aerial platform honestly — drive type, altitude/speed limits, geofence, payload/sensor set?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0416-pegasus-simulator-outreach.md

Thanks for Pegasus; an open Isaac Sim + PX4 drone framework is a great sim-to-real bridge.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0417: gym-pybullet-drones

**Post to (Discussion):** https://github.com/learnsyslab/gym-pybullet-drones/discussions/new?category=ideas
**Title:** URML (open robot intent language): wrapping a learned drone controller in a validated envelope — request for comment

```
Hi gym-pybullet-drones community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML has an aerial drive type, and your project — the most-starred open drone-RL sandbox — is an ideal place to show URML wrapping a learned controller in a validated intent layer.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea is the decide-then-do split applied to learning: a URML aerial intent declares the goal and the envelope, a learned policy in a gym-pybullet-drones environment produces the low-level control, and URML validates the request against the declared limits before the policy is allowed to act. The policy is the actuator; URML is the typed, validated intent and the safety envelope around it. The RL sandbox is a clean demonstrator for "a natural-language goal, a learned controller, and a validator that refuses out-of-envelope requests."

Two real questions: (1) Is wrapping a learned drone controller in a validated intent layer + envelope interesting in the RL-sandbox context? (2) What should a URML capability manifest declare to describe a learned-controller drone honestly — drive type, altitude/speed limits, observation/action assumptions — and is the Gymnasium env interface the right seam or a higher-level mission wrapper?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0417-gym-pybullet-drones-outreach.md

Thanks for gym-pybullet-drones; a clean, popular open drone-RL suite is a great place to think about safety around learned control.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0418: NTNU ARL (unified autonomy stack)

**Post to (Issue):** https://github.com/ntnu-arl/unified_autonomy_stack/issues/new
**Title:** URML (open robot intent language): a validated intent layer above the NTNU ARL autonomy stack — request for comment

```
Hi NTNU ARL maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML ships an aerial drive type and a ROS 2 runtime, and your lab's autonomy work — the unified autonomy stack here, plus the aerial_gym_simulator where policies are trained — is a natural place for a validated intent layer. I'm anchoring this on the autonomy stack and referencing the simulator rather than posting to each repo.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the unified autonomy stack on its ROS 2 surface; an "explore this volume and return" intent lowers onto the stack's planning/behavior layer. Where aerial_gym_simulator trains a policy, URML wraps the deployed controller in a validated envelope (the decide-then-do split applied to learning). Validate-before-actuate refuses an out-of-envelope request before the drone acts.

Two real questions: (1) Where is the cleanest seam — above the autonomy stack's behavior/planning layer, or wrapping a policy trained in aerial_gym_simulator? (2) What should a URML capability manifest declare to describe an exploration-class aerial robot honestly — drive type, altitude/speed limits, sensor suite, exploration bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0418-ntnu-arl-outreach.md

Thanks for the autonomy stack and aerial_gym; the lab's aerial-exploration work is some of the most interesting in the area.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0419: kr_autonomous_flight (KumarRobotics)

**Post to (Issue — Discussions off):** https://github.com/KumarRobotics/kr_autonomous_flight/issues/new
**Title:** URML (open robot intent language): a validated intent layer above a GPS-denied autonomy stack — request for comment

```
Hi kr_autonomous_flight maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML ships an aerial drive type and a ROS 2 runtime, and your GPS-denied autonomous-flight stack from the Kumar Lab is one of the most credible in aerial autonomy — the kind of platform a validated intent layer should compose with. (For clarity: the repo is under the lab's academic-use software license; URML proposes nothing under it and asks for no license change — this is purely a mapping discussion.)

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the stack on its ROS surface; "fly to this position through the building and report" lowers onto its planning/control layer. The stack's strength is GPS-denied state estimation, and URML consumes that estimate rather than reimplementing it (the same posture URML takes toward SLAM). Validate-before-actuate refuses an out-of-envelope request before the drone acts, which matters in cluttered indoor flight.

Two real questions: (1) Is the ROS surface the right seam for an external validated-intent layer above a GPS-denied autonomy stack? (2) What should a URML capability manifest declare to describe such a platform honestly — drive type, altitude/speed limits, positioning source, operating volume?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0419-kr-autonomous-flight-outreach.md

Thanks for kr_autonomous_flight; the lab's GPS-denied flight work is a real benchmark for the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0420: CERLAB UAV Autonomy (CMU)

**Post to (Issue — Discussions off):** https://github.com/Zhefan-Xu/CERLAB-UAV-Autonomy/issues/new
**Title:** URML (open robot intent language): a validated intent layer above CERLAB UAV Autonomy — request for comment

```
Hi CERLAB UAV Autonomy maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML ships an aerial drive type and a ROS 2 runtime, and your modular UAV autonomy framework — perception, mapping, planning, and control as composable ROS modules — is a natural place to align URML's typed intent with each layer.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the framework on its module surface; "navigate to the target and avoid obstacles" lowers onto the planning/control modules. The perception/mapping modules are the kind of detect source URML consumes: a detection binds a target a downstream action consumes (decide-then-do). Validate-before-actuate refuses an out-of-envelope request before dispatch.

Two real questions: (1) Does URML's typed intent map cleanly onto the framework's modular ROS surface, and where should it target it? (2) What should a URML capability manifest declare to describe a modular autonomy UAV honestly — drive type, altitude/speed limits, sensor suite, operating bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0420-cerlab-uav-autonomy-outreach.md

Thanks for CERLAB UAV Autonomy; a clean modular open UAV autonomy framework is a great reference.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0421: XTDrone

**Post to (Issue — Discussions off):** https://github.com/robin-shaun/XTDrone/issues/new
**Title:** URML (open robot intent language): a validated intent layer above XTDrone — request for comment

```
Hi XTDrone maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML ships an aerial drive type and a PX4 runtime, and XTDrone pairs ROS and the exact flight controller URML targets in a Gazebo sandbox — a convenient sim home for a validated aerial intent layer.

Nothing here asks XTDrone to adopt, host, or maintain anything. This is a request for comment.

URML's aerial drive type and PX4 runtime drive an XTDrone vehicle through PX4 / the ROS bridge in Gazebo; "take off, fly the waypoints, and land" lowers onto the same PX4 seam URML uses on hardware. URML's optional validation block records the simulation-fidelity context a run was checked in. Validate-before-actuate refuses an out-of-envelope request before the simulated drone arms.

Two real questions: (1) Is the PX4 / ROS bridge the right seam for an external validated-intent layer above XTDrone? (2) What should a URML capability manifest declare to describe an XTDrone aerial platform honestly — drive type, altitude/speed limits, sensor set, single vs multi?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0421-xtdrone-outreach.md

Thanks for XTDrone; a widely-used open PX4 + Gazebo teaching sandbox is a real on-ramp for new drone developers.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
