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

# Move #60 post bodies: robotic end-effectors at the grasp-envelope seam

Six targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(Apache-2.0 / MIT stated plainly; aero-hand-open's SDK is Apache-2.0 and its
CAD is CC-BY-NC-SA, URML relates to the SDK). AI-assisted-authoring disclosure
up front. Titles carry no em-dash. The fit lands on RFC-0586 (the dexterous
gripper kind + grasp_type) and the grasp primitive's force/aperture envelope:
URML declares the end-effector and a grasp envelope, validates the grasp, then
leaves actuation to the target. Bodies are varied per target.

---

## RFC-0624: Aero Hand Open (aero-hand-open)

**Post to (Issue):** https://github.com/TetherIA/aero-hand-open/issues/new
**Title:** URML (open robot intent language): a validated grasp envelope above the Aero Hand SDK (request for comment)

```
Hi TetherIA maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, and only then dispatched. A tendon-driven multi-fingered hand is exactly the case we extended URML's grasp model to cover, so the Aero Hand is a natural fit. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: a single-DoF gripper abstraction cannot describe a multi-DoF hand, so URML added a dexterous gripper kind with a dexterity declaration (degrees of freedom, finger count, supported grasp types, whether it does in-hand manipulation) and an optional grasp type on the grasp primitive. A grasp then becomes a typed intent (which grasp type, on which object class, within which force limits) that URML validates against a manifest describing the hand and a grasp-force envelope, before the Aero Hand SDK is asked to move tendons. The SDK keeps the actuation; URML is the static check in front of it.

Two real questions: (1) is a typed grasp-intent layer useful above the SDK, or does your stack already carry that admissibility reasoning? (2) Does the hand's capability set (DoF, finger count, supported grasp types, in-hand support) map onto URML's dexterity declaration cleanly, or is something missing?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0624-aero-hand-outreach.md

Thanks for the Aero Hand; an affordable open multi-DoF hand is exactly the kind of end-effector a typed grasp model should be able to describe.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0625: ORCA Hand (orca_core)

**Post to (Issue):** https://github.com/orcahand/orca_core/issues/new
**Title:** URML (open robot intent language): declaring the 17 DoF once and validating every grasp against them (request for comment)

```
Hi ORCA Hand maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against declared capabilities and a safety envelope, and only then dispatched. orca_core is the control core for a 17-DoF tendon-driven hand, which is well past what a single-DoF gripper abstraction can express, so it is a clean target for the part of URML built for dexterous hands. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: URML has a dexterous gripper kind with a dexterity declaration (DoF, finger count, supported grasp types, in-hand support) and an optional grasp type on the grasp primitive. A grasp intent (a grasp type, a target, a force limit) is validated against a manifest declaring the hand's degrees of freedom and the grasp types it supports, and against a grasp-force envelope, before orca_core is asked to move joints. orca_core keeps the joint-space control, calibration, and tensioning; URML is the static check before it.

Two real questions: (1) is a typed grasp-intent layer useful above orca_core? (2) Does the ORCA hand's joint structure and grasp-type set map onto URML's dexterity declaration cleanly, or do the tendon-coupling details need something the manifest does not yet express?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0625-orca-hand-outreach.md

Thanks for orca_core; an open 17-DoF hand with a clean control core is a great place to test a typed grasp declaration.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0626: BiDexHand

**Post to (Issue):** https://github.com/wengmister/BiDexHand/issues/new
**Title:** URML (open robot intent language): a static grasp-force envelope alongside your fingertip force sensing (request for comment)

```
Hi BiDexHand maintainer,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against declared capabilities and a safety envelope, and only then dispatched. BiDexHand is a 16-DoF cable-driven hand with fingertip force sensing, which makes it a particularly clean target: the force sensing is the runtime side of a property URML can also check statically. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: URML has a dexterous gripper kind with a dexterity declaration (DoF, finger count, supported grasp types) and a grasp-force envelope. URML validates that a grasp intent stays inside the declared force envelope before dispatch; your fingertip force sensing is the runtime side of the same property. The static check refuses an over-force grasp before the cables move; the sensors stay yours. A declared envelope plus a hand that measures force is a natural pairing, and the 16 DoF map onto the dexterity declaration directly.

Two real questions: (1) is a typed grasp-intent layer useful above your ROS 2 control modes (PID, Cartesian, shadowing)? (2) Does the hand's DoF and grasp-type set map onto URML's dexterity declaration cleanly, and does the fingertip force sensing line up with a declared grasp-force envelope?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0626-bidexhand-outreach.md

Thanks for BiDexHand; a cable-driven hand that senses fingertip force is exactly where a declared envelope and a runtime monitor reinforce each other.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0627: robotiq_hande_driver (AGH-CEAI)

**Post to (Issue):** https://github.com/AGH-CEAI/robotiq_hande_driver/issues/new
**Title:** URML (open robot intent language): declaring aperture and force, validated before the gripper closes (request for comment)

```
Hi AGH-CEAI maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against the gripper's declared capabilities and a safety envelope, and only then dispatched. Your ros2_control driver actuates a Robotiq Hand-E parallel gripper, which is the original case URML's grasp model handles: a single-DoF gripper with an aperture and a commanded force. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: a close-with-force command on a Hand-E is a typed grasp intent, a target aperture and a force not to exceed. URML validates that against a manifest declaring the gripper's aperture range and maximum force, then leaves the Modbus command and the ros2_control hardware interface to your driver. The driver keeps the actuation; URML is the pre-dispatch check. A parallel gripper does not need the dexterity model, only the simple gripper declaration and a grasp-force envelope, so the mapping is small: the manifest states a few numbers and the validator refuses a grasp that violates them.

Two real questions: (1) is a typed grasp-intent layer useful above a ros2_control gripper driver? (2) Does a Hand-E envelope (aperture range, force limit, speed) map onto a capability manifest cleanly, and does the multi-backend design (fake / serial / UR tool comm) raise anything a layer above it should account for?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0627-robotiq-hande-driver-outreach.md

Thanks for the driver; a clean ros2_control gripper interface is the simplest place to see whether a typed grasp check adds anything.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0628: OnRobot ROS 2 controller (onrobot-ros2)

**Post to (Issue):** https://github.com/ABC-iRobotics/onrobot-ros2/issues/new
**Title:** URML (open robot intent language): one grasp manifest for the simulated and the real gripper (request for comment)

```
Hi ABC-iRobotics maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against the gripper's declared capabilities and a safety envelope, and only then dispatched. Your ROS 2 controller drives OnRobot RG2 and RG6 width-and-force grippers in Isaac Sim and on hardware, which is the base case URML's grasp model handles. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: a grasp on an RG2 or RG6 is a typed intent, a target width and a force not to exceed. URML validates that against a manifest declaring the gripper's width range and maximum force, then leaves the command to your controller. The controller keeps the actuation; URML is the static check in front of it. Because you support both Isaac Sim and hardware, the same manifest and the same validated grasp apply to the simulated and the real gripper, which is the substrate neutrality URML is built around: declare once, validate everywhere the manifest holds.

Two real questions: (1) is a typed grasp-intent layer useful above the controller? (2) Does an RG2/RG6 envelope (width range, force, speed) map onto a capability manifest cleanly, and would the Isaac Sim path be a good place to demonstrate a validated grasp before running it on hardware?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0628-onrobot-ros2-outreach.md

Thanks for the controller; sim-and-hardware on one interface is exactly where a declare-once-validate-everywhere manifest is worth trying.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0629: ros2_RobotiqGripper (IFRA-Cranfield)

**Post to (Issue):** https://github.com/IFRA-Cranfield/ros2_RobotiqGripper/issues/new
**Title:** URML (open robot intent language): a validated grasp above a service call, in one arm-plus-gripper manifest (request for comment)

```
Hi IFRA-Cranfield maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against declared capabilities and a safety envelope, and only then dispatched. Your package opens and closes Robotiq 2F grippers on Universal Robots arms through a ROS 2 service, which puts a grasp at a clean application altitude. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The seam: opening or closing a 2F gripper through your package is a grasp intent expressed as a service call. URML validates that intent against a declared aperture-and-force envelope before the call is made, so an out-of-envelope grasp is refused with a typed reason. The package keeps the service interface and the UR integration; URML is the pre-dispatch check. Because a 2F on a UR arm is a small, well-defined cell, URML declares the gripper alongside the arm in one capability manifest: a grasp validates against the gripper while a motion validates against the arm, in the same typed model.

Two real questions: (1) is a typed grasp-intent layer useful above a service-level gripper interface? (2) Would a combined arm-and-gripper manifest (UR motion plus a 2F grasp) be a useful first example to write together?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0629-ros2-robotiqgripper-outreach.md

Thanks for the package; a 2F-on-UR cell is a natural place to show an arm motion and a gripper grasp validated in one manifest.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
