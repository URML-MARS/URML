# Move #65 posts — domain-vertical lane (5 clean)

Posted under idoco2003 on 2026-06-29. AI-authoring disclosure (VIBE.md) up front, no license-ask, em-dash-free titles, per-target variation.
RFC-0648 dex-teleop, 0649 spot_bt_ros, 0650 vortex-auv, 0651 kalman_robot, 0652 sailing-robot.

---

## 1. GeneralTrajectory/dex-teleop  (RFC-0648)

**Title:** URML: a capability check on a teleoperated arm-and-hand command

Hi, disclosure first: this is AI-assisted prose I reviewed and approved before posting (background: https://github.com/URML-MARS/URML/blob/main/VIBE.md). Glad to go human-only if you prefer.

I maintain URML (https://urml.dev), a small Apache-2.0 language whose one job is to check an intended motion against a robot's declared capabilities and a safety envelope before it executes.

dex-teleop is an interesting case because a human is in the loop, and that is not by itself a guarantee the commanded pose is reachable or the commanded grasp force is within the hand's limit. URML can declare the arm's reach and the hand's per-finger force and joint limits, and check the relayed command against that declaration before it hits the actuators. A useful side effect: the recorded demonstrations are then admissible by construction, which matters once they become training data.

URML does not do the tracking, the retargeting, or the recording. It is the admissibility check between the retargeted command and the hardware.

Two questions:
1. In a teleop loop with a human driving, is a declared arm-and-hand capability check on the relayed command a useful guardrail, or do the operator plus the retargeting already keep commands in-envelope in practice?
2. Would a small worked example mapping a dex-teleop command onto a URML manifest, validated with no execution, be worth having?

Nothing here asks you to adopt, host, or maintain anything. Thanks for the work.

Ido Yahalomi (greenvh@gmail.com)

---

## 2. sandialabs/spot_bt_ros  (RFC-0649)

**Title:** URML: a per-action admissibility check under each behavior-tree leaf

Hi. Up front: AI-assisted prose I reviewed before posting (https://github.com/URML-MARS/URML/blob/main/VIBE.md); say the word for human-only.

I maintain URML (https://urml.dev), a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs.

A behavior tree is a clean place for that kind of check, because each leaf that commands motion is a discrete action the tree is about to dispatch, which is the granularity URML validates at. Declare the platform's mobility envelope and the mission's keep-out and standoff constraints, and URML can check a traverse or manipulation leaf against that declaration before the tree ticks it into motion. In an inspection setting where the environment may be hazardous, a static admissibility check in front of each dispatched action is a natural complement to the tree's own guard conditions.

URML does not replace the tree, the planner, or the Spot SDK. It is the per-action gate under a leaf that commands motion.

Two questions:
1. For a behavior-tree inspection stack, is a declared-capability and envelope check at the action-leaf boundary a useful layer alongside the tree's own guards, or is that already covered by how the tree is authored?
2. Would a small worked example mapping a Spot inspection action onto a URML manifest, validated with no execution, be worth having?

Nothing here asks you to adopt or maintain anything. Thanks for putting a behavior-tree safety layer on Spot in the open.

Ido Yahalomi (greenvh@gmail.com)

---

## 3. vortexntnu/vortex-auv  (RFC-0650)

**Title:** URML: validating an AUV mission setpoint against the vehicle envelope

Hello. A disclosure to start: AI-assisted prose, reviewed and approved by me before posting (https://github.com/URML-MARS/URML/blob/main/VIBE.md). Glad to go human-only if you prefer.

I maintain URML (https://urml.dev), a small Apache-2.0 language for declaring what a vehicle can do and checking an intended action against that declaration before it runs.

An AUV is a good fit, because underwater the cost of dispatching an inadmissible action (past depth rating, outside a geofence, beyond thruster authority) is high and recovery is hard. A mission is a goal plus constraints: reach this waypoint, hold this depth, stay inside this operating volume. URML can declare the vehicle's depth rating, thruster envelope, and the geofence, and validate a commanded setpoint against that before the GNC stack drives the thrusters.

URML does not do guidance, estimation, or control. It declares the envelope and confirms a commanded action is inside it before dispatch.

Two questions:
1. For your GNC stack, is a declared depth-and-thruster-and-geofence envelope check on a commanded setpoint useful before dispatch, or is that already enforced inside guidance?
2. Would a small worked example mapping an AUV mission setpoint onto a URML manifest, validated with no execution, be worth having?

Nothing here asks you to adopt or maintain anything. Thanks for keeping a full AUV stack open.

Ido Yahalomi (greenvh@gmail.com)

---

## 4. agh-space-systems-rover/kalman_robot  (RFC-0651)

**Title:** URML: validating a rover action against drive, reach, and power limits

Hi. Disclosure up front: AI-assisted prose I reviewed before posting (https://github.com/URML-MARS/URML/blob/main/VIBE.md); human-only is fine if you prefer.

I maintain URML (https://urml.dev), a small Apache-2.0 language for declaring what a robot can do and checking an intended action against that declaration before it runs.

A planetary-analogue rover is a fitting case, because power and terrain bound what is admissible at any moment, and the loop that picks the next action benefits from a separate check that the action is within those bounds. The rover's autonomy decides where to go and what to do; URML answers whether the chosen action is admissible given a declared envelope: drive limits, manipulation reach, and a power-state or terrain constraint the mission declares. The check sits between action selection and the drivers, and leaves perception and the decision loop untouched.

The setting is part of the point: where a wrong action is costly and oversight is intermittent, a static pre-dispatch check earns its place.

Two questions:
1. For your autonomy stack, is a declared drive-and-manipulation-and-power envelope check on a selected action useful before dispatch, or is feasibility already guaranteed inside action selection?
2. Would a small worked example mapping a rover action onto a URML manifest, validated with no execution, be worth having?

Nothing here asks you to adopt or maintain anything. Thanks for the work, and good luck at the next rover competition.

Ido Yahalomi (greenvh@gmail.com)

---

## 5. Maritime-Robotics-Student-Society/sailing-robot  (RFC-0652)

**Title:** URML: validating a helm-and-trim command against the sailing envelope

Hi. Disclosure first: AI-assisted prose I reviewed before posting (https://github.com/URML-MARS/URML/blob/main/VIBE.md); say the word for human-only.

I maintain URML (https://urml.dev), a small Apache-2.0 language for declaring what a vehicle can do and checking an intended action against that declaration before it runs.

A sailing robot is an unusual and instructive case, because the admissible action depends heavily on a declared operating envelope (sea state, no-go zones, sail limits) that shifts with conditions. The autonomy decides a helm and trim command to make progress; URML can check that command against the platform's sail and rudder limits and a mission-declared operating boundary or sea-state ceiling, before it reaches the actuators. It does not touch the wind estimation or the course logic.

URML does not sail, estimate wind, or steer. It declares the envelope and confirms a commanded helm-and-trim action is inside it before dispatch.

Two questions:
1. For a sailing-vessel stack, is a declared envelope check (sail and rudder limits, operating boundary, sea-state ceiling) on a helm-and-trim command useful before dispatch, or is that already handled inside the controller?
2. Would a small worked example mapping a sailing command onto a URML manifest, validated with no execution, be worth having?

Nothing here asks you to adopt or maintain anything. Thanks for keeping an autonomous-sailing stack in the open.

Ido Yahalomi (greenvh@gmail.com)
