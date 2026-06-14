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

# Move #55 post bodies: the inspection-robotics wave

Four targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(MIT/Apache stated; UNav-Sim's license is non-standard, so the post states that
and asks nothing). AI-assisted-authoring disclosure up front. Titles carry no
em-dash. A deliberately small, honest wave: the terrestrial pipe/bridge/
construction-machine open-source surface is mostly stale, so this is the clean
aerial + underwater + off-road inspection surface. Framing: URML declares the
inspection goal + operating envelope, validates against the platform, and
consumes the planned trajectory (RFC-0020); for trained-policy targets, a
policy can declare its envelope (RFC-0383). Bodies are varied per target.

---

## RFC-0596: aerial-autonomy-stack (anchor)

**Post to (Issue):** https://github.com/JacopoPan/aerial-autonomy-stack/issues/new
**Title:** URML (open robot intent language): a validated mission-intent layer for drone inspection (request for comment)

```
Hi,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the craft's declared capabilities and a safety envelope, then dispatched. Your stack simulates and deploys perception-based drones and swarms on PX4/ArduPilot, and aerial inspection is one of its central uses, which is exactly where a declared mission intent fits.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: an inspection mission is a goal plus constraints (survey this structure, hold this standoff and geofence, return on this condition). URML expresses that, validates it against the craft's declared capabilities, then consumes the trajectory the stack plans and flies. URML stays substrate-neutral and already maps onto PX4, so it does not compete with your perception, planning, or control. And because the stack runs swarms, a multi-drone inspection maps onto URML's multi-robot roster with cross-vehicle deconfliction: declare the fleet and its separation constraints, validate the multi-vehicle intent, then drive it through the stack.

Two real questions: (1) is a typed, validated mission-intent layer (declare goal + inspection envelope, validate, consume the trajectory) useful above the stack? (2) Does a multi-drone inspection map onto a fleet roster + cross-vehicle deconfliction in a way that fits how you run swarms?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0596-aerial-autonomy-stack-outreach.md

Thanks for the stack; a real perception-driven PX4 swarm framework is exactly where fleet-level validated inspection intent is easiest to try.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0597: UNav-Sim

**Post to (Issue):** https://github.com/open-airlab/UNav-Sim/issues/new
**Title:** URML (open robot intent language): validated underwater-inspection intent and a policy that declares its envelope (request for comment)

```
Hi UNav-Sim maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the vehicle's declared capabilities and a safety envelope, then dispatched. UNav-Sim does underwater pipe-following inspection with a controller and a trained planner on a BlueROV2 Heavy, and a subsea inspection task is the kind of goal-plus-constraints intent URML is built to declare and validate.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

There are two seams, and the second is the more interesting. First, the obvious one: URML expresses the inspection goal plus its operating envelope, validates it against the vehicle, then consumes the trajectory your controller and planner produce. Second, and more interesting: you use a trained planner, and URML has a direction (LearnedPolicy) where a trained policy declares the operating envelope it was trained for, so an intent can be checked against that envelope before the policy is trusted to drive. For an underwater inspection where being out of distribution is genuinely risky, that pre-trust check is the part I would most want your read on.

Two real questions: (1) is a typed, validated inspection-intent layer (declare goal + envelope, validate, consume the plan) useful above UNav-Sim? (2) Could the trained planner declare a training/operating envelope a URML intent is checked against?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0597-unav-sim-outreach.md

Thanks for UNav-Sim; underwater inspection with a learned planner is exactly the setting where stating and checking an operating envelope up front earns its keep.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0598: CentraleNantesROV/bluerov2

**Post to (Issue):** https://github.com/CentraleNantesROV/bluerov2/issues/new
**Title:** URML (open robot intent language): validated subsea-inspection intent above the bluerov2 ROS 2 stack (request for comment)

```
Hi,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the vehicle's declared capabilities and a safety envelope, then dispatched. URML already ships a marine runtime and a BlueROV adapter, so your ROS 2 description/control/sim for the BlueROV2 is a natural second path to the same vehicle. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: a subsea inspection is a goal plus constraints (follow this pipeline or hull, hold depth and standoff, respect the geofence). URML expresses that, validates against the vehicle's declared capabilities, then dispatches to your bluerov2 ROS 2 control; URML's marine drive type lowers onto the vehicle and you keep control and simulation. One honest note on scope: URML's existing BlueROV adapter targets the BlueRobotics BlueOS/ArduSub stack, and yours is a distinct, academic ROS 2 route to the same hardware, so the interesting question is whether one validated-intent layer can sit cleanly above both.

Two real questions: (1) is a typed, validated inspection-intent layer (declare goal + envelope, validate, dispatch) useful above the bluerov2 ROS 2 stack? (2) Does URML's marine vehicle capability model fit how this package describes the BlueROV2?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0598-bluerov2-cn-outreach.md

Thanks for the package; a clean ROS 2 BlueROV2 stack is a good place to test whether a single intent layer can span both routes to a popular vehicle.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0599: RoboTerrain

**Post to (Issue):** https://github.com/jackvice/RoboTerrain/issues/new
**Title:** URML (open robot intent language): a validated-intent gate over an off-road inspection policy (request for comment)

```
Hi RoboTerrain maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an instruction becomes a typed primitive, validated against the platform's declared capabilities and a safety envelope, then dispatched. RoboTerrain trains off-road navigation policies in ROS 2 + Gazebo, with environments that include industrial inspection and construction sites, which is exactly where a validated-intent gate over a learned policy is worth thinking about.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: URML's decide-then-do split puts a typed, validated intent in front of the policy. Declare the inspection or traversal goal plus the off-road operating bounds (slope, traversability, standoff), validate against the platform's declared capabilities, then let the trained policy drive within that envelope. The training and the policy stay entirely with RoboTerrain. URML also has a direction (LearnedPolicy) where a trained policy declares the conditions it was trained for, so an intent can be checked against that envelope before the policy is trusted on a real inspection rather than in sim.

Two real questions: (1) is a typed, validated intent gate (declare goal + off-road bounds, validate, then let the policy drive) useful above a RoboTerrain-trained policy? (2) Could a trained policy declare a training/operating envelope a URML intent is checked against?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0599-roboterrain-outreach.md

Thanks for RoboTerrain; off-road inspection is exactly where the gap between a sim-trained policy and a trusted real run is widest, and an explicit envelope check speaks to that gap.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
