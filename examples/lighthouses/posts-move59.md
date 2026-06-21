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

# Move #59 post bodies: physical-actuation consumers at the safety-envelope seam

Six targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(Apache-2.0 / MIT stated plainly; the three copyleft targets, opensourceleg
LGPL-2.1, epically-powerful AGPL-3.0, open_mower_ros GPL-3.0, are cross-citation
/ layering only with no shared code). AI-assisted-authoring disclosure up front.
Titles carry no em-dash. Two sub-lanes share one fit: a manifest declares the
device's actuation limits (joint torque/position for the wearables, drive
envelope for the mobile platforms) and URML validates the intent before the
device moves. Bodies are varied per target.

---

## RFC-0618: CORC (CANOpenRobotController)

**Post to (Issue):** https://github.com/UniMelbHumanRoboticsLab/CANOpenRobotController/issues/new
**Title:** URML (open robot intent language): a validated envelope before CANopen actuation on an exo/rehab device (request for comment)

```
Hi CORC maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a subtask becomes a typed primitive, validated against the device's declared capabilities and a safety envelope, and only then dispatched. CORC is the layer that turns a controller's decision into real CANopen position and torque commands on an exoskeleton or rehab robot, which is exactly the handoff a pre-dispatch check is most worth running. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: on a device coupled to a person, the safety envelope is the whole point. A subtask (move this joint to this position, never exceeding this torque, within these limits) is a goal plus hard constraints. URML's candidate role is to state that envelope once, in a capability manifest, and validate every subtask intent against it in five passes (argument typing, capability, safety envelope, bindings, policy) before the intent reaches CORC's CANopen loop. CORC keeps the real-time control; URML is the static check that runs before the loop is handed an intent.

Two real questions: (1) is a typed, statically-validated intent layer useful above a CANopen control stack like this, or does your control layer already carry that admissibility reasoning? (2) Do a device's per-joint torque ceilings and position ranges map onto a capability manifest and safety envelope cleanly, for something like the X2 or the ArmMotus arms?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0618-corc-exoskeleton-outreach.md

Thanks for CORC; an open CANopen control stack for exo and rehab hardware is exactly where a checked envelope before actuation earns its keep.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0619: opensourceleg

**Post to (Issue):** https://github.com/neurobionics/opensourceleg/issues/new
**Title:** URML (open robot intent language): the leg's declared limits as a checked envelope before the actuator drives (request for comment)

```
Hi Open-Source Leg maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a subtask becomes a typed primitive, validated against a device's declared capabilities and a safety envelope, and only then dispatched. opensourceleg already drives the prosthesis's actuators behind a clean API and knows its joint and torque limits. URML's candidate contribution is to lift those limits into a typed envelope that a subtask intent is validated against before the SDK is asked to drive the actuator. This is a request for comment, and given the LGPL-2.1 license it is a layering relationship, no shared code.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: the SDK knows the leg's joint ranges and torque ceilings; URML turns those into a safety envelope that a gait or assist subtask is checked against statically, so an out-of-envelope command is refused before it reaches the actuator rather than caught (or not) at runtime. The SDK keeps the actuator and sensor handling; URML is the pre-dispatch gate. A prosthesis is coupled to a person, so a typed limit declaration plus a static check is concrete value, not decoration.

Two real questions: (1) is a static safety-envelope check useful above the device API, or does the SDK already refuse inadmissible commands? (2) Do the leg's declared limits map onto a capability manifest and safety envelope cleanly, or do prosthesis dynamics need something a manifest does not yet express? A single joint (knee or ankle) would be a natural first try.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0619-opensourceleg-outreach.md

Thanks for opensourceleg; a widely used open prosthesis SDK is a good place to see whether a typed envelope check adds anything above the device API.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0620: epically-powerful

**Post to (Issue):** https://github.com/gatech-epic-power/epically-powerful/issues/new
**Title:** URML (open robot intent language): a static envelope check alongside your runtime safety monitor (request for comment)

```
Hi EPIC Lab maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a subtask becomes a typed primitive, validated against declared capabilities and a safety envelope, and only then dispatched. epically-powerful commands QDD actuators over CAN for exoskeletons and already has safety monitoring around the actuation it drives. URML's candidate role is the complement to that: declare the admissible envelope up front and validate an intent against it statically, so the same safety properties exist as a pre-dispatch check and a runtime monitor, not only the latter. This is a request for comment, framed as cross-citation given the AGPL-3.0 license.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: a declared limit on actuator torque or speed is a property that can be checked twice. Once statically, when URML validates that a subtask intent stays inside the declared envelope, and once at runtime, by your own monitoring. URML's pre-dispatch validation refuses an inadmissible intent before the actuator sees it; the runtime monitor stays yours. Because the framework speaks to well-defined actuators (AK / RobStride / CyberGear) over CAN, the per-actuator limits are concrete and declarable, which makes the envelope mapping tractable.

Two real questions: (1) is a static pre-dispatch envelope check useful alongside your runtime monitoring, or does the runtime side already cover what a static check would catch? (2) Do per-actuator torque/speed/position limits map onto a capability manifest and safety envelope cleanly for a QDD-over-CAN stack?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0620-epically-powerful-outreach.md

Thanks for epically-powerful; building safety in around QDD actuation is the right instinct, and a static check before dispatch may be a useful second layer.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0621: OpenMower (open_mower_ros)

**Post to (Issue):** https://github.com/ClemensElflein/open_mower_ros/issues/new
**Title:** URML (open robot intent language): declaring a mow job and its envelope, validated before the machine moves (request for comment)

```
Hi OpenMower maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a job becomes a typed primitive, validated against the machine's declared capabilities and a safety envelope, and only then dispatched. OpenMower plans coverage, navigates, and drives a real cutting machine across a yard near people, pets, and obstacles. URML's candidate role is to declare that job and its envelope and validate it before the mower moves or cuts. This is a request for comment, framed as cross-citation given the GPL-3.0 license.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: a mow job is a goal plus constraints, an area to cover, a boundary not to cross, a speed not to exceed, conditions under which the blade may run. URML expresses that as typed intent, validates it against a capability manifest and a safety envelope, and then leaves coverage planning, navigation, and motor control entirely to OpenMower. Boundaries, keep-out zones, and a blade that should only spin under defined conditions are exactly the declarable, checkable constraints URML is built for. The mower's drive type and limits go in the manifest; the job is validated against them before anything spins.

Two real questions: (1) is a typed, validated job-intent layer useful above your coverage-and-navigation stack, or does OpenMower already gate jobs against the machine's limits? (2) Which constraint (boundary, keep-out, speed, blade-engagement) would be the most valuable to check statically before a job runs?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0621-open-mower-outreach.md

Thanks for OpenMower; an open autonomous mower is a great example of an outdoor machine where a checked job envelope before actuation genuinely matters.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0622: Rover Robotics (roverrobotics_ros2)

**Post to (Issue):** https://github.com/RoverRobotics/roverrobotics_ros2/issues/new
**Title:** URML (open robot intent language): a vendor-platform capability manifest, validated before velocity commands (request for comment)

```
Hi Rover Robotics maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a motion subtask becomes a typed primitive, validated against the platform's declared capabilities and a safety envelope, and only then dispatched. Your ROS 2 driver takes velocity commands and drives a real skid-steer rover. A vendor driver is the natural place for a URML capability manifest to attach, because the platform's drive type and limits are known quantities. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: URML lifts the platform's drive type (skid-steer), its speed and acceleration limits, and its motion envelope into a typed manifest, validates a motion intent against them, and only then is the command handed to your driver. The driver keeps the motor and protocol handling; URML is the pre-dispatch check. Because URML is deliberately substrate-agnostic, the same typed intent that validates against a Rover platform validates against any platform that declares an equivalent manifest, so a customer's intent is checked against the real limits of the hardware they bought without coupling the intent to one stack.

Two real questions: (1) is a typed capability manifest plus a validated motion intent useful above a vendor platform driver? (2) Do a skid-steer rover's limits (speed, acceleration, turning constraints) map onto a manifest and safety envelope cleanly? A single platform (Rover Zero, say) would be a natural first manifest.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0622-roverrobotics-outreach.md

Thanks for the rover driver; a clean vendor platform is exactly where a capability manifest has something concrete to describe.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0623: Leo Rover (leo_robot-ros2)

**Post to (Issue):** https://github.com/LeoRover/leo_robot-ros2/issues/new
**Title:** URML (open robot intent language): a teachable capability manifest and a validated motion on a classroom rover (request for comment)

```
Hi Leo Rover maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a motion subtask becomes a typed primitive, validated against the platform's declared capabilities and a safety envelope, and only then dispatched. This driver commands real motion on the Leo Rover, a platform used in research and in classrooms. On a platform built for learning, a typed capability manifest doubles as a clear, readable statement of what the rover can and cannot do. This is a request for comment. (To be clear, this is about the real-robot driver, not the simulation packages.)

Nothing here asks the project to adopt, host, or maintain anything.

The seam: URML declares the rover's drive type, speed limits, and motion envelope in a manifest, then validates a motion intent against it before the driver moves the wheels, so an out-of-envelope command is refused with a typed reason rather than silently attempted. The driver keeps the motion; URML is the pre-dispatch check. URML's headline path is one plain sentence becoming a validated, executable robot action, and a rover used to teach robotics is a good place for that loop to be visible: intent stated, validated against the real platform, then run.

Two real questions: (1) is a typed manifest plus a validated motion intent useful above the Leo Rover driver, in research and in teaching? (2) Would a classroom-facing example (a sentence to a validated rover motion) be worth building together?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0623-leo-rover-outreach.md

Thanks for the Leo Rover; an accessible research-and-education rover is a natural place to make the intent-to-validated-action loop visible.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
