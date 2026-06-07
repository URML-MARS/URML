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

# Move #35 post bodies: the mobile-manipulation / service-robot wave

Nine targets, all GitHub Issues (no Discussions enabled on these repos). Post
under idoco2003. No license-ask (state the license). AI-assisted-authoring
disclosure up front.

---

## RFC-0422: Hello Robot Stretch

**Post to (Issue):** https://github.com/hello-robot/stretch_ros2/issues/new
**Title:** URML (open robot intent language): a validated intent layer above Stretch — request for comment

```
Hi Stretch / Hello Robot community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. A mobile manipulator is the cleanest possible exercise of URML — "go to the kitchen and pick up the mug" combines URML's two core primitive families, navigation and manipulation, in one sentence — and Stretch is one of the most accessible open mobile manipulators there is.

Nothing here asks Stretch to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets Stretch on its ROS 2 action/service surface; "go to the kitchen and pick up the mug" lowers onto a move_to (base navigation) followed by a grasp (the arm) — the decide-then-do split made concrete. Validate-before-actuate refuses an undeclared object class or an out-of-reach grasp before the arm moves. The combined nav + manipulation manifest is a rich, honest test of URML's capability model on one platform.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above Stretch? (2) What should a URML capability manifest declare to describe a Stretch-class mobile manipulator honestly — drive type, arm reach/DOF, gripper + graspable classes, navigation bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0422-stretch-outreach.md

Thanks for Stretch; an accessible open mobile manipulator is exactly the right place for this kind of layer to be designed with input.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0423: PAL TIAGo

**Post to (Issue):** https://github.com/pal-robotics/tiago_robot/issues/new
**Title:** URML (open robot intent language): a validated intent layer above TIAGo — request for comment

```
Hi TIAGo / PAL Robotics community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. A mobile manipulator is the cleanest exercise of URML — "go to the table and hand me the bottle" combines navigation and manipulation in one sentence — and TIAGo is one of the most widely-used research mobile manipulators. (I'm anchoring this on tiago_robot and referencing tiago_simulation rather than posting to each.)

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets TIAGo on its ROS 2 action/service surface; "go to the table and hand me the bottle" lowers onto a move_to (the base) plus a grasp (the arm) — the decide-then-do split made concrete. Validate-before-actuate refuses an undeclared object or out-of-reach grasp before the arm moves. The combined base + torso + arm manifest exercises URML's capability model honestly on a standard research platform.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for an external validated-intent layer above TIAGo? (2) What should a URML capability manifest declare to describe a TIAGo-class mobile manipulator honestly — drive type, torso lift, arm reach/DOF, gripper + graspable classes, navigation bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0423-tiago-outreach.md

Thanks for TIAGo; a standard open research mobile manipulator is a great platform for this kind of work.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0424: TidyBot++ (tidybot2)

**Post to (Issue):** https://github.com/jimmyyhwu/tidybot2/issues/new
**Title:** URML (open robot intent language): wrapping a learned mobile-manipulation policy in a validated envelope — request for comment

```
Hi TidyBot++ community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. TidyBot++ is interesting to URML because it is an open, low-cost holonomic mobile manipulator built for robot learning — a clean place to show URML wrapping a learned policy in a validated intent layer.

Nothing here asks TidyBot++ to adopt, host, or maintain anything. This is a request for comment.

The idea is the decide-then-do split applied to learning: a URML intent ("tidy this table: put the cups in the bin") declares the goal and the envelope, a learned policy on TidyBot++ produces the low-level holonomic base + arm control, and URML validates the request against the declared capabilities before the policy acts. The policy is the actuator; URML is the typed, validated intent and the safety envelope around it. A holonomic mobile manipulator is a rich manifest case (omnidirectional base + arm + gripper + object vocabulary).

Two real questions: (1) Is wrapping a learned mobile-manipulation policy in a validated intent layer + envelope interesting in the robot-learning context? (2) What should a URML capability manifest declare to describe a holonomic mobile manipulator honestly — drive type, arm reach/DOF, gripper + graspable classes, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0424-tidybot2-outreach.md

Thanks for TidyBot++; an open, affordable mobile manipulator for learning is a real gift to the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0425: TurtleBot3 Manipulation (ROBOTIS)

**Post to (Issue):** https://github.com/ROBOTIS-GIT/turtlebot3_manipulation/issues/new
**Title:** URML (open robot intent language): a validated intent layer above TurtleBot3 + OpenMANIPULATOR — request for comment

```
Hi ROBOTIS / TurtleBot3 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. A mobile manipulator is the cleanest exercise of URML — "drive to the marker and pick up the block" combines navigation and manipulation in one sentence — and TurtleBot3 + OpenMANIPULATOR is one of the most accessible and widely-taught open mobile manipulators.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the stack on its ROS 2 action/service surface; "drive to the marker and pick up the block" lowers onto a move_to (the base) plus a grasp (the OpenMANIPULATOR arm) — the decide-then-do split made concrete. Validate-before-actuate refuses an out-of-reach grasp or undeclared object before the arm moves. The small, well-documented platform makes the combined nav + manipulation manifest a clean classroom example.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for a validated-intent layer above this platform? (2) What should a URML capability manifest declare to describe a TurtleBot3 + OpenMANIPULATOR honestly — drive type, arm reach/DOF, gripper + graspable classes, navigation bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0425-turtlebot3-manipulation-outreach.md

Thanks for TurtleBot3 Manipulation; an accessible, well-taught open mobile manipulator is a great teaching surface.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0426: Interbotix LoCoBot (Trossen)

**Post to (Issue):** https://github.com/Interbotix/interbotix_ros_rovers/issues/new
**Title:** URML (open robot intent language): a validated intent layer above the LoCoBot — request for comment

```
Hi Interbotix / Trossen Robotics community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. A mobile manipulator is the cleanest exercise of URML — "drive to the shelf and pick up the item" combines navigation and manipulation in one sentence — and the LoCoBot is a popular low-cost open mobile manipulator in education and research.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the Interbotix stack on its ROS 2 surface; "drive to the shelf and pick up the item" lowers onto a move_to (the base) plus a grasp (the Interbotix arm) — the decide-then-do split made concrete. Validate-before-actuate refuses an out-of-reach grasp or undeclared object before the arm moves. The base + arm manifest is a clean, affordable platform example of URML's capability model.

Two real questions: (1) Is URML's ROS 2 surface the right seam for a validated-intent layer above a LoCoBot-class rover? (2) What should a URML capability manifest declare to describe an Interbotix mobile manipulator honestly — drive type, arm reach/DOF, gripper + graspable classes, navigation bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0426-interbotix-locobot-outreach.md

Thanks for the Interbotix stack; an affordable open mobile manipulator is a great on-ramp for education and research.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0427: TidyBot ROS (ROAHM Lab)

**Post to (Issue):** https://github.com/roahmlab/tidybot_ros/issues/new
**Title:** URML (open robot intent language): a validated intent layer above TidyBot ROS — request for comment

```
Hi TidyBot ROS / ROAHM Lab maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches over ROS 2. Your ROS 2 interface for the TidyBot++ mobile manipulator is exactly the surface URML's runtime targets — where the upstream project is the hardware + learning side, this is the ROS 2 stack.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets tidybot_ros on its ROS 2 action/service surface; a "tidy this area" intent lowers onto a move_to (holonomic base) plus grasp/release cycles — the decide-then-do split made concrete. Where the pipeline trains/deploys a learned policy, URML wraps it in a validated envelope (decide-then-do applied to learning). Validate-before-actuate refuses an out-of-capability request before dispatch.

Two real questions: (1) Does URML's typed intent map cleanly onto the tidybot_ros ROS 2 surface, and where should it target it? (2) What should a URML capability manifest declare to describe a holonomic mobile manipulator in ROS 2 honestly — drive type, arm reach/DOF, gripper + graspable classes, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0427-tidybot-ros-outreach.md

Thanks for tidybot_ros; a clean ROS 2 stack for an open mobile manipulator is great to see.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0428: Care-O-bot (Fraunhofer IPA)

**Post to (Issue):** https://github.com/ipa320/cob_robots/issues/new
**Title:** URML (open robot intent language): a validated intent layer above Care-O-bot — request for comment

```
Hi Care-O-bot / Fraunhofer IPA maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Care-O-bot is one of the original open service mobile manipulators, and its design target — assistive tasks in human environments — is exactly the kind of work a validated intent layer is for.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets the cob stack on its ROS surface; "fetch the bottle from the kitchen and bring it here" lowers onto a move_to (the omnidirectional base) plus a grasp (the arm) — the decide-then-do split made concrete. Validate-before-actuate refuses an undeclared object or out-of-reach grasp before the arm moves, which matters for assistive tasks around people. The base + torso + arm + head manifest is a thorough test of URML's capability model.

Two real questions: (1) Is URML's ROS surface the right seam for a validated-intent layer above Care-O-bot? (2) What should a URML capability manifest declare to describe a Care-O-bot-class service manipulator honestly — drive type, torso, arm reach/DOF, gripper + graspable classes, navigation bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0428-care-o-bot-outreach.md

Thanks for Care-O-bot; one of the foundational open service-robot platforms is a meaningful place for this discussion.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0429: PR2 (community)

**Post to (Issue):** https://github.com/PR2/pr2_robot/issues/new
**Title:** URML (open robot intent language): a validated intent layer above PR2 — request for comment

```
Hi PR2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. PR2 is the dual-arm mobile manipulator that defined the "go fetch the mug" demo and seeded much of the modern ROS manipulation ecosystem — the canonical reference for exactly the task URML describes.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS runtime meets the pr2 stack on its ROS surface; "go to the table and pick up the mug" lowers onto a move_to (the base) plus a grasp (an arm) — the very demo PR2 is known for. A two-armed platform exercises URML's bimanual manipulation work: an arm selector and a bimanual primitive for coordinated two-arm tasks. Validate-before-actuate refuses an out-of-reach grasp or undeclared object before an arm moves.

Two real questions: (1) Is URML's ROS surface the right seam for a validated-intent layer above PR2? (2) What should a URML capability manifest declare to describe a PR2-class dual-arm mobile manipulator honestly — drive type, two arms + reach/DOF, grippers + graspable classes, navigation bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0429-pr2-outreach.md

Thanks for keeping PR2 alive; the platform that started "go fetch the mug" is the natural place to talk about a language for exactly that.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0430: Kinova ros2_kortex

**Post to (Issue):** https://github.com/Kinovarobotics/ros2_kortex/issues/new
**Title:** URML (open robot intent language): a validated manipulation-intent layer above the Kinova Gen3 — request for comment

```
Hi Kinova community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. ros2_kortex is interesting to URML as the manipulation half of Kinova's mobile-manipulation platforms — a vendor-maintained, permissively-licensed arm driver, and the arm rides the MOVO mobile base.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS 2 runtime meets ros2_kortex on its ROS 2 action/service surface; a grasp / release (and, on a mobile base, a preceding move_to) lowers onto the Kinova arm interface — the decide-then-do split made concrete. Validate-before-actuate refuses an out-of-reach grasp or an undeclared object class before the arm moves. When the Gen3 is mounted on a mobile base (MOVO), the combined manifest is the natural mobile-manipulation case.

Two real questions: (1) Is URML's ROS 2 action-surface mapping the right seam for a validated manipulation-intent layer above the Gen3 arm? (2) What should a URML capability manifest declare to describe a Kinova arm honestly — reach/DOF, gripper + graspable classes, force limits — and how should that extend when the arm rides a mobile base?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0430-ros2-kortex-outreach.md

Thanks for ros2_kortex; a permissive, vendor-maintained ROS 2 arm driver is a clean place to think about validated intent.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
