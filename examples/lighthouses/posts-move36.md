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

# Move #36 post bodies: the industrial / collaborative arm-driver wave

Nine targets (PRC vendors deferred per RFC-0003). Post under idoco2003 via the
channel noted per row (Discussion or Issue). No license-ask (state license where
present; some repos carry no license file — omit license entirely, do NOT ask).
AI-assisted-authoring disclosure up front. At post time, query each Discussion
repo's real category id (Move #30 procedure) for the three Discussion targets.

---

## RFC-0431: Universal Robots ROS 2 Driver

**Post to (Discussion):** https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above the UR ROS 2 driver — request for comment

```
Hi Universal Robots ROS 2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. A real industrial arm with a clean, vendor-maintained ROS 2 driver is the ideal home for validated manipulation intent, and the UR driver is the most-deployed and most-starred open vendor arm driver there is.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the driver on its ROS 2 action/service surface (and the ros2_control controllers); a "pick the part from bin A and place it in fixture B" becomes a typed primitive (pick_from / place_at / grasp), validated against the declared reach, payload, and graspable classes, and only then dispatched. Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves — a real safety and liability boundary on industrial hardware.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above the UR driver? (2) What should a URML capability manifest declare to describe a UR-class cobot honestly — reach/DOF, payload, joint/speed limits, gripper + graspable classes, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0431-universal-robots-outreach.md

Thanks for the UR ROS 2 driver; the most-deployed open cobot driver is exactly the right place for this kind of layer to be designed with input.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0432: Franka ROS 2

**Post to (Issue):** https://github.com/frankarobotics/franka_ros2/issues/new
**Title:** URML (open robot intent language): a validated intent layer above franka_ros2 — request for comment

```
Hi Franka ROS 2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. The Franka arm is the most widely-used research manipulator there is, and a precise, force-sensitive arm with a permissive vendor-maintained ROS 2 stack is a natural home for validated manipulation intent.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets franka_ros2 on its ROS 2 action/service surface (and the ros2_control controllers); a "pick up the block and place it on the stack" becomes a typed primitive (grasp / pick_from / place_at), validated against the declared reach, payload, and graspable classes, and only then dispatched. Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above franka_ros2? (2) What should a URML capability manifest declare to describe a Franka-class research arm honestly — reach/DOF, payload, joint/force limits, gripper + graspable classes, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0432-franka-outreach.md

Thanks for franka_ros2; the research arm that so much manipulation work runs on is a great platform for this discussion.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0433: Yaskawa motoros2

**Post to (Discussion):** https://github.com/Yaskawa-Global/motoros2/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above motoros2 — request for comment

```
Hi Yaskawa motoros2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Yaskawa is one of the largest industrial-arm makers, and a first-party ROS 2 driver for Motoman controllers is a strong home for validated manipulation intent on production hardware.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets motoros2 on its ROS 2 action/service surface; a "pick the part from the conveyor and place it on the pallet" becomes a typed primitive (pick_from / place_at / grasp), validated against the declared reach, payload, and end-effector, and only then dispatched. Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves — a meaningful boundary in an industrial cell.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above motoros2? (2) What should a URML capability manifest declare to describe a Motoman-class industrial arm honestly — reach/DOF, payload, joint/speed limits, end-effector + graspable classes, cell bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0433-yaskawa-motoros2-outreach.md

Thanks for motoros2; a first-party ROS 2 driver from a major industrial OEM is a great place for this kind of work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0434: ABB ROS 2 driver (PickNik)

**Post to (Issue):** https://github.com/PickNikRobotics/abb_ros2/issues/new
**Title:** URML (open robot intent language): a validated intent layer above abb_ros2 — request for comment

```
Hi abb_ros2 maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. ABB is one of the largest industrial-robot makers, and a permissively-licensed ROS 2 driver for its arms is a strong home for validated manipulation intent.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets abb_ros2 on its ROS 2 action/service surface (and the ros2_control controllers); a "pick the part from bin A and place it in fixture B" becomes a typed primitive (pick_from / place_at / grasp), validated against the declared reach, payload, and end-effector, and only then dispatched. Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above abb_ros2? (2) What should a URML capability manifest declare to describe an ABB-class industrial arm honestly — reach/DOF, payload, joint/speed limits, end-effector + graspable classes, cell bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0434-abb-ros2-outreach.md

Thanks for keeping a clean ROS 2 ABB driver alive; it is the natural home for this discussion.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0435: KUKA LBR iiwa (lbr-stack)

**Post to (Issue):** https://github.com/lbr-stack/lbr_fri_ros2_stack/issues/new
**Title:** URML (open robot intent language): a validated intent layer above the LBR iiwa stack — request for comment

```
Hi lbr-stack maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. The KUKA LBR iiwa is a leading torque-sensitive collaborative arm, widely used in research and medical robotics, and a permissively-licensed ROS 2 stack for it is a strong home for validated, force-aware manipulation intent.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the stack on its ROS 2 / FRI surface (and the ros2_control controllers); a "pick up the tool and place it in the holder" becomes a typed primitive (grasp / pick_from / place_at), validated against the declared reach, payload, and force limits, and only then dispatched. Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload/force over the declared limit before the arm moves — meaningful on a torque-sensitive cobot.

Two real questions: (1) Is URML's ROS 2 / FRI surface the right seam for an external validated-intent layer above the LBR iiwa stack? (2) What should a URML capability manifest declare to describe an LBR iiwa honestly — reach/DOF, payload, joint/force limits, gripper + graspable classes, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0435-kuka-iiwa-lbr-stack-outreach.md

Thanks for the lbr-stack; the most active open iiwa stack is a great place to think about force-aware validated intent.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0436: Doosan Robotics ROS 2

**Post to (Issue):** https://github.com/doosan-robotics/doosan-robot2/issues/new
**Title:** URML (open robot intent language): a validated intent layer above doosan-robot2 — request for comment

```
Hi Doosan Robotics ROS 2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Doosan is a fast-growing cobot maker, and a permissively-licensed vendor-maintained ROS 2 driver is a clean home for validated manipulation intent.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets doosan-robot2 on its ROS 2 action/service surface (and the ros2_control controllers); a "pick the part from the table and place it in the box" becomes a typed primitive (pick_from / place_at / grasp), validated against the declared reach, payload, and graspable classes, and only then dispatched. Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above doosan-robot2? (2) What should a URML capability manifest declare to describe a Doosan-class cobot honestly — reach/DOF, payload, joint/speed limits, gripper + graspable classes, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0436-doosan-outreach.md

Thanks for doosan-robot2; a clean vendor-maintained ROS 2 cobot driver is a great platform for this.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0437: Techman Robot (tmr_ros2)

**Post to (Issue):** https://github.com/TechmanRobotInc/tmr_ros2/issues/new
**Title:** URML (open robot intent language): a validated intent layer above tmr_ros2 — request for comment

```
Hi Techman Robot ROS 2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. TM arms are notable for built-in vision, and a vendor-maintained ROS 2 driver is a clean home for validated manipulation intent that consumes a detection and then acts.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets tmr_ros2 on its ROS 2 action/service surface; a "find the part and pick it up" becomes a typed primitive where a detect step binds a target and a grasp consumes it — the decide-then-do split, and TM's built-in vision is exactly the kind of detect source URML composes with. Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above tmr_ros2? (2) What should a URML capability manifest declare to describe a TM-class cobot honestly — reach/DOF, payload, joint/speed limits, gripper + graspable classes, integrated-vision detection classes, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0437-techman-outreach.md

Thanks for tmr_ros2; a vision-integrated cobot is a great fit for a decide-then-do intent layer.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0438: igus iRC_ROS

**Post to (Issue):** https://github.com/CommonplaceRobotics/iRC_ROS/issues/new
**Title:** URML (open robot intent language): a validated intent layer above iRC_ROS — request for comment

```
Hi iRC_ROS / igus community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. The igus ReBeL is a low-cost cobot, and a permissively-licensed vendor-maintained ROS 2 stack for it is an accessible home for validated manipulation intent.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets iRC_ROS on its ROS 2 action/service surface (and the ros2_control controllers); a "pick the part and place it in the tray" becomes a typed primitive (pick_from / place_at / grasp), validated against the declared reach, payload, and graspable classes, and only then dispatched. Validate-before-actuate refuses an out-of-reach pose, an undeclared object class, or a payload over the declared limit before the arm moves.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above iRC_ROS? (2) What should a URML capability manifest declare to describe an igus ReBeL-class arm honestly — reach/DOF, payload, joint limits, gripper + graspable classes, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0438-igus-irc-ros-outreach.md

Thanks for iRC_ROS; an affordable open cobot stack is a great on-ramp for this kind of layer.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0439: ROS-Industrial (kuka_experimental)

**Post to (Discussion):** https://github.com/ros-industrial/kuka_experimental/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer over ROS-Industrial drivers — request for comment

```
Hi ROS-Industrial community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. ROS-Industrial is the community that brought industrial robots to ROS, and it is the natural place to discuss a validated intent layer that targets standard industrial interfaces rather than inventing parallel ones. (I'm anchoring this one engagement on kuka_experimental and referencing the consortium's broader vendor support; this also follows up on an earlier ROS-Industrial contact, RFC-0038.)

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets ROS-Industrial driver packages on their ROS surface (and the ros2_control controllers); a "pick the part from bin A and place it in fixture B" becomes a typed primitive (pick_from / place_at / grasp), validated against the declared reach, payload, and end-effector, and only then dispatched. URML prefers to target the standard interfaces the consortium defines rather than per-vendor parallel ones — the same posture it takes toward Nav2 and ros2_control. Validate-before-actuate refuses an out-of-reach pose, an undeclared object, or an over-payload request before the arm moves.

Two real questions: (1) Where should URML target standard ROS-Industrial interfaces rather than a generic or per-vendor ROS surface? (2) What should a URML capability manifest declare to describe an industrial arm honestly across vendors — reach/DOF, payload, joint/speed limits, end-effector + graspable classes, cell bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0439-ros-industrial-outreach.md

Thanks for ROS-Industrial; the consortium that standardized industrial robots on ROS is exactly where a cross-vendor intent layer should be discussed.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
