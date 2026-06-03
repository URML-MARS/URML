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

# Move #27 post bodies: manipulation / grasping

Copy-paste-ready bodies for the 10 Tier-A targets. Deferred / folded rows
(NVIDIA cuRobo/Contact-GraspNet/STORM, stale grasp-detection GPD/GQ-CNN/GG-CNN,
IK siblings relaxed_ik/bio_ik/pick_ik, archived/attic Ravens/dm_robotics/
robotiq-attic/moveit_grasps) are recorded in
[`outreach-move27.yaml`](outreach-move27.yaml), not posted.

Shared framing, in every body: URML does NOT solve IK or detect grasps. It
declares the target and the arm/gripper capability, statically validates
admissibility before the substrate runs (target in reachable workspace; grasp
within the gripper's force range and accepted classes), and consumes the result.
The dexterous-hand bodies (LEAP, Shadow) are honest that URML's single-force-range
gripper model is too coarse for a multi-DoF hand, and ask what a richer
declaration should contain.

**No body contains a license-clarification ask** (per the 2026-06-03 guidance:
the boilerplate license question is an AI-tell that triggers hostile closes).

Bodies follow the [AGENTS.md](../../AGENTS.md) rules: concrete hook, "nothing for
you to maintain" up front, one or two real questions, RFC linked as optional
depth, under a two-minute read, zero em-dashes. VIBE disclosure line last.

All 10 repos have Issues enabled (verified 2026-06-03), so each is a single Issue.

**Posting status:** DRAFTED, not yet posted. Post under `idoco2003` only after
RFCs 0352-0361 land on `main`. Then fill `sent_at` / `posted_url` per row and
refresh `outreach.db`.

**Routing summary**

| RFC | Target | Channel | Status |
|---|---|---|---|
| 0352 | TRAC-IK | Issue on `traclabs/trac_ik` | Drafted (post after merge) |
| 0353 | Pink | Issue on `stephane-caron/pink` | Drafted (post after merge) |
| 0354 | mink | Issue on `kevinzakka/mink` | Drafted (post after merge) |
| 0355 | MPlib | Issue on `haosulab/MPlib` | Drafted (post after merge) |
| 0356 | GraspNet | Issue on `graspnet/graspnet-baseline` | Drafted (post after merge) |
| 0357 | LEAP Hand | Issue on `leap-hand/LEAP_Hand_API` | Drafted (post after merge) |
| 0358 | Shadow Robot | Issue on `shadow-robot/sr_interface` | Drafted (post after merge) |
| 0359 | RLBench | Issue on `stepjam/RLBench` | Drafted (post after merge) |
| 0360 | robomimic | Issue on `ARISE-Initiative/robomimic` | Drafted (post after merge) |
| 0361 | PlaCo | Issue on `Rhoban/placo` | Drafted (post after merge) |

---

## RFC-0352: TRAC-IK

**Post to:** https://github.com/traclabs/trac_ik/issues/new
**Title:** URML (open robot intent language): validating a reachability claim before it reaches TRAC-IK, request for comment

```
Hi TRAC-IK maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. URML does not solve IK. It declares a target pose and the arm's reachable workspace, and it expects an IK solver to find the joint configuration. For a great many ROS manipulators, that solver is TRAC-IK.

Nothing here asks TRAC-IK to change or maintain anything. This is a request for comment on the boundary.

The useful idea: URML can statically check a motion request is admissible (the target is inside the declared reachable workspace, within the safety envelope) before it ever forms an IK query, so TRAC-IK is only asked to solve in-capability problems, and a no-solution result feeds back as a URML validation signal rather than a runtime surprise. Two real questions. First, what is the cleanest boundary for "URML target pose plus reachability -> a TRAC-IK query" (base and tip frames, seed, solve type)? Second, is there a stable way to treat a no-solution or timeout as a capability signal URML should surface to the user?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0352-trac-ik-outreach.md

Thanks for TRAC-IK; it is the IK a huge number of arms quietly rely on.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0353: Pink

**Post to:** https://github.com/stephane-caron/pink/issues/new
**Title:** URML (open robot intent language): a validated target as a Pink task, request for comment

```
Hi Pink maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a target and capability; it does not solve IK. Pink solves differential IK as a QP over tasks, built on Pinocchio, which is exactly the kind of solver URML would hand a validated target to.

Nothing here asks Pink to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest way for URML to express a target as a Pink task set (a frame task plus the relevant posture and limit tasks), so URML stays the intent layer and Pink stays the solver? Second, URML declares capability limits (reachable workspace, and with the envelope, joint and velocity limits): how should those map onto Pink's limit configuration so a request URML has validated is one Pink can take as well-posed? For context, I am reaching the MuJoCo-based sibling mink separately, and TRAC-IK for the global pose-to-config case.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0353-pink-outreach.md

Thanks for Pink, and for how readable the task-based formulation is.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0354: mink

**Post to:** https://github.com/kevinzakka/mink/issues/new
**Title:** URML (open robot intent language): a validated target as a mink task, request for comment

```
Hi mink maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a target and capability; it does not solve IK. mink solves differential IK as a task-based QP for MuJoCo models, which is exactly the kind of solver URML would hand a validated target to.

Nothing here asks mink to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest way for URML to express a target as a mink task set (a frame task plus posture and limit tasks)? Second, since mink works against a MuJoCo model, how should URML reference the model so a declared reachable workspace and the solver's notion of the same robot stay consistent? For context, Pink is the Pinocchio-based sibling I am reaching in parallel, and TRAC-IK for the global pose-to-config case.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0354-mink-outreach.md

Thanks for mink; a clean MuJoCo-native differential IK was missing for a while.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0355: MPlib

**Post to:** https://github.com/haosulab/MPlib/issues/new
**Title:** URML (open robot intent language): a validated manipulation goal into an MPlib plan, request for comment

```
Hi MPlib maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a goal and the arm's capability; it does not plan. MPlib plans collision-free manipulation trajectories, which is exactly what URML would hand a validated goal to.

Nothing here asks MPlib to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest boundary for "URML manipulation intent plus capability -> an MPlib planning call" (planning group, the collision-world source, the goal as a pose or a joint target)? Second, MPlib wraps OMPL, which I am engaging separately at the general planning layer: where would you draw the line between the manipulation-specific convenience MPlib provides and the underlying planner, from a URML integration point of view? URML validates the goal is admissible (in the declared reachable workspace, within the envelope) before the plan call.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0355-mplib-outreach.md

Thanks for MPlib; a lightweight manipulation planner with a clean Python API is genuinely useful.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0356: GraspNet

**Post to:** https://github.com/graspnet/graspnet-baseline/issues/new
**Title:** URML (open robot intent language): filtering GraspNet candidates against a declared gripper, request for comment

```
Hi GraspNet maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. For a grasp, URML declares the gripper's capability (its kind, force range, and the object classes it accepts) and a target object. It does not detect grasps. GraspNet is exactly the grasp-pose source URML would draw candidates from.

Nothing here asks GraspNet to change or maintain anything. This is a request for comment.

The shape: GraspNet proposes 6-DoF grasp candidates; URML validates a chosen candidate against the declared gripper (is the width feasible, is the force in range, is the object class accepted) before anything actuates. Two real questions. First, what gripper parameters does URML most need to declare so candidates can be filtered for feasibility (width, approach, force)? Second, does the grasp-pose output have a stable enough interface (poses plus scores plus widths) that a consumer like URML could target it across versions?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0356-graspnet-outreach.md

Thanks for GraspNet and the 1Billion dataset; it set a reference point the field still builds on.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0357: LEAP Hand

**Post to:** https://github.com/leap-hand/LEAP_Hand_API/issues/new
**Title:** URML (open robot intent language): what should a dexterous-hand capability declaration contain? request for comment

```
Hi LEAP Hand maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. Part of that manifest declares a gripper: its kind, a force range, and the object classes it accepts. That describes a parallel-jaw gripper well. It does not describe a 16-DoF hand like the LEAP Hand, and that gap is exactly why I am writing.

Nothing here asks LEAP Hand to change or maintain anything. This is genuinely a request for comment, and you are better placed than most to answer it.

The honest question: what should a minimal-but-useful dexterous-hand capability declaration contain? Per-finger force, named grasp types (power, pinch, tripod) rather than per-joint commands, in-hand-manipulation flags, something else? Today URML can only declare a hand as a coarse gripper (a lower bound it states honestly), and the LEAP API executes the finger commands. I would rather design the richer declaration with input from people who build and use the hand than guess at it.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0357-leap-hand-outreach.md

Thanks for making a low-cost dexterous hand the whole field can actually get hold of.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0358: Shadow Robot

**Post to:** https://github.com/shadow-robot/sr_interface/issues/new
**Title:** URML (open robot intent language): a dexterous-hand capability declaration for a 20-DoF hand, request for comment

```
Hi Shadow Robot team,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML's manifest can declare a gripper as a kind plus a force range plus accepted object classes. For the Shadow Dexterous Hand, with 20-plus actuated degrees of freedom, that is clearly too coarse, which is what brings me here.

Nothing here asks Shadow Robot to change or maintain anything. This is a request for comment, and the Shadow Hand is the richest case I have for getting it right.

The honest question: what should a dexterous-hand capability declaration contain so URML can validate a hand request before it runs? Per-finger force and range, named grasp synergies, tactile-feedback availability, coupled-joint structure? Today URML declares the hand as a coarse gripper (a lower bound, stated honestly) and sr_interface executes. I am asking the LEAP Hand maintainers the same question in parallel, since the open dexterous-hand projects are the right people to shape this with.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0358-shadow-robot-outreach.md

Thanks for keeping a serious dexterous hand's ROS stack open.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0359: RLBench

**Post to:** https://github.com/stepjam/RLBench/issues/new
**Title:** URML (open robot intent language): an RLBench task as a validated URML behavior, request for comment

```
Hi RLBench maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a robot's declared capabilities and a safety envelope -> dispatch, and it composes primitives into behaviors. RLBench defines manipulation tasks with success conditions, which is strikingly close to what a URML behavior describes at the intent level.

Nothing here asks RLBench to change or maintain anything. This is a conceptual request for comment, not a runtime adapter.

The overlap: an RLBench task (open the drawer, stack the blocks) reads like a URML behavior over validated primitives, and URML could add a capability-and-safety-checked description of each task's actions. Two real questions. First, does an RLBench task <-> URML behavior correspondence sound sound, or do the task definitions carry assumptions that would not survive being expressed as portable validated intent? Second, would a capability-checked, substrate-neutral task description be useful to the benchmark, or is the CoppeliaSim/PyRep grounding too load-bearing to abstract over?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0359-rlbench-outreach.md

Thanks for RLBench; a large shared task set moved the field forward.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0360: robomimic

**Post to:** https://github.com/ARISE-Initiative/robomimic/issues/new
**Title:** URML (open robot intent language): bounding a learned manipulation policy with a capability manifest, request for comment

```
Hi robomimic maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. A policy learned with robomimic is a manipulation controller, and that is an interesting thing for URML to sit above: URML's manifest and safety envelope could statically bound what a learned policy is allowed to attempt.

Nothing here asks robomimic to change or maintain anything. I will be upfront that a learned controller as a URML substrate is newer ground for the project, so this is genuinely a request for comment.

Two real questions. First, where is the clean boundary between a high-level URML intent and a robomimic policy: does URML hand the policy a validated goal and a bounded action space, or is the policy better treated as the whole skill behind a single primitive? Second, could a demonstration's task carry a portable, capability-checked URML behavior description alongside the trajectories, so the same task is legible across robots? For context, robomimic builds on robosuite, which I have noted separately.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0360-robomimic-outreach.md

Thanks for robomimic; reproducible imitation-learning baselines are harder to build than they look.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0361: PlaCo

**Post to:** https://github.com/Rhoban/placo/issues/new
**Title:** URML (open robot intent language): a validated target as a PlaCo task set, request for comment

```
Hi PlaCo maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a target and capability; it does not solve kinematics. PlaCo solves whole-body kinematics and control as a QP over tasks and constraints, which is exactly the kind of solver URML would hand a validated target to, with a whole-body emphasis the single-arm IK solvers do not cover.

Nothing here asks PlaCo to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest way for URML to express a target as a PlaCo task and constraint set, so URML stays the intent layer and PlaCo stays the solver? Second, for the whole-body case (a mobile base plus an arm, or a humanoid), how should URML's capability declaration carry the structure PlaCo needs without restating the model? For context, Pink and mink are the single-arm differential-IK siblings I am reaching in parallel.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0361-placo-outreach.md

Thanks for PlaCo; an approachable whole-body QP library lowers a real barrier.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
