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

# Move #26 post bodies: motion planning / navigation

Copy-paste-ready bodies for the 10 Tier-A targets. Deferred / folded rows
(do-mpc, OpenRAVE, TOWR, mpc_local_planner under teb, SBPL) are recorded in
[`outreach-move26.yaml`](outreach-move26.yaml), not posted.

Shared framing, in every body: URML does NOT plan. URML declares the goal and
the capability constraints; the target computes the trajectory that realizes the
intent; URML validates admissibility before the planner runs and consumes the
result. For the three low-level backends (Pinocchio, CasADi, acados) the bodies
are honest boundary checks ("you are likely below the layer URML should talk
to"), mirroring the GTSAM / Ceres posts in Move #25. PlanSys2 is framed as a
peer at URML's own layer, not as a substrate.

Bodies follow the [AGENTS.md](../../AGENTS.md) outreach-post-structure rules:
concrete hook, "nothing for you to maintain" up front, one or two real
questions, RFC linked as optional depth, under a two-minute read, zero
em-dashes. VIBE disclosure line last.

All 10 repos have Issues enabled (verified 2026-06-03), so each is a single Issue.

**Posting status:** DRAFTED, not yet posted. Post under `idoco2003` only after
RFCs 0342-0351 land on `main`. Then fill `sent_at` / `posted_url` per row in
`outreach-move26.yaml` and refresh `outreach.db`.

**Routing summary**

| RFC | Target | Channel | Status |
|---|---|---|---|
| 0342 | OMPL | Issue on `ompl/ompl` | Drafted (post after merge) |
| 0343 | Ruckig | Issue on `pantor/ruckig` | Drafted (post after merge) |
| 0344 | TOPP-RA | Issue on `hungpham2511/toppra` | Drafted (post after merge) |
| 0345 | Pinocchio | Issue on `stack-of-tasks/pinocchio` | Drafted (post after merge) |
| 0346 | Crocoddyl | Issue on `loco-3d/crocoddyl` | Drafted (post after merge) |
| 0347 | OCS2 | Issue on `leggedrobotics/ocs2` | Drafted (post after merge) |
| 0348 | CasADi | Issue on `casadi/casadi` | Drafted (post after merge) |
| 0349 | acados | Issue on `acados/acados` | Drafted (post after merge) |
| 0350 | teb_local_planner | Issue on `rst-tu-dortmund/teb_local_planner` | Drafted (post after merge) |
| 0351 | PlanSys2 | Issue on `PlanSys2/ros2_planning_system` | Drafted (post after merge) |

---

## RFC-0342: OMPL

**Post to:** https://github.com/ompl/ompl/issues/new
**Title:** URML (open robot intent language): validating a planning query before it reaches OMPL, request for comment

```
Hi OMPL maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent. A person writes an English sentence, URML translates it to a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. URML does not plan. It declares a goal and the constraints, and it expects a motion planner to compute the path. OMPL is the planner that path most often comes from, directly or through MoveIt.

Nothing here asks OMPL to change or maintain anything. This is a request for comment on the boundary.

The useful idea: URML can statically check that a motion request is admissible (target inside the declared reachable workspace, within the safety envelope) before it ever builds a planning query, so OMPL is only ever asked to solve well-formed, in-capability problems. Two real questions. First, what is the cleanest boundary for "URML goal plus constraints -> an OMPL planning query"? Second, which constraints does URML most need to declare so a query is well-posed for OMPL: state-space bounds, the validity checker inputs, something else?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0342-ompl-outreach.md


Thanks for OMPL; it is the quiet engine under a lot of robot motion.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0343: Ruckig

**Post to:** https://github.com/pantor/ruckig/issues/new
**Title:** URML (open robot intent language): declaring kinematic limits that map onto Ruckig constraints, request for comment

```
Hi Ruckig maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares limits and a goal; it does not generate trajectories. Ruckig is exactly the piece that turns a target state into a smooth, jerk-limited, time-optimal trajectory in real time.

Nothing here asks Ruckig to change or maintain anything. This is a request for comment.

URML's safety envelope already carries velocity, acceleration, and (where declared) jerk limits. Those are precisely Ruckig's input constraints. So one real question: what is the cleanest way for URML to declare per-axis kinematic limits so they map directly onto a Ruckig input, and should URML treat Ruckig's feasibility result as a validation signal (a request that Ruckig cannot satisfy under the declared limits is a request URML should reject earlier)? A second, smaller one: for the offline time-optimal-parameterization case I am talking to toppra separately; is online generation the boundary you would keep Ruckig to?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0343-ruckig-outreach.md


Thanks for Ruckig; jerk-limited online generation done well is rarer than it should be.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0344: TOPP-RA

**Post to:** https://github.com/hungpham2511/toppra/issues/new
**Title:** URML (open robot intent language): declaring the limits TOPP-RA parameterizes against, request for comment

```
Hi toppra maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares limits and a goal; it consumes trajectories, it does not compute them. toppra is the piece that takes a geometric path and adds time-optimal timing under velocity, acceleration, and torque limits.

Nothing here asks toppra to change or maintain anything. This is a request for comment.

In URML's stack, toppra sits after a geometric planner (I am talking to OMPL separately) and is the offline counterpart to online generators like Ruckig. The constraints toppra parameterizes against are exactly what URML declares. So two real questions. First, what is the cleanest way for URML to declare velocity / acceleration / torque limits so they map onto a toppra constraint set? Second, is the input boundary simply "a path plus limits", with the path coming from whatever planner produced it?

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0344-toppra-outreach.md


Thanks for toppra; time-optimal parameterization with a clean API is genuinely useful.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0345: Pinocchio

**Post to:** https://github.com/stack-of-tasks/pinocchio/issues/new
**Title:** URML (open robot intent language): keeping a capability declaration consistent with a Pinocchio model, request for comment

```
Hi Pinocchio maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares what a robot can do (reachable workspace, and in time joint limits) and validates intent against it.

I will be honest about layers: URML does not talk to Pinocchio directly, and Pinocchio is below the layer URML usually addresses (it is the kinematics and dynamics the planners and MPC I am also reaching out to are built on). So this is a boundary and consistency question, not a proposed mapping.

The real question: a URML capability declaration (reachability today, joint and dynamic limits later) is making claims that a Pinocchio model already encodes precisely. Should a URML declaration be derivable from, or checked against, a Pinocchio model so the two cannot drift, and if so at what grain? I would rather URML's manifest stay consistent with the model than restate it badly.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0345-pinocchio-outreach.md


Thanks for Pinocchio; the speed and the clean model API are a real gift to the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0346: Crocoddyl

**Post to:** https://github.com/loco-3d/crocoddyl/issues/new
**Title:** URML (open robot intent language): dynamic-motion intent into a Crocoddyl optimal-control problem, request for comment

```
Hi Crocoddyl maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a goal and constraints; it does not solve optimal control. For dynamic motion (a legged move, a dynamic manipulation), Crocoddyl is exactly the solver that turns intent into a dynamically feasible trajectory.

Nothing here asks Crocoddyl to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest boundary for "URML dynamic-motion intent plus constraints -> a Crocoddyl optimal-control problem", the action-model and cost setup, or something higher? Second, what should URML declare so a request is well-posed: the dynamic limits, contact assumptions, the model (you build on Pinocchio, which I am also asking about consistency for)? URML's job is to validate the request is admissible before you are asked to solve it.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0346-crocoddyl-outreach.md


Thanks for Crocoddyl; fast multi-contact DDP changed what is practical.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0347: OCS2

**Post to:** https://github.com/leggedrobotics/ocs2/issues/new
**Title:** URML (open robot intent language): intent and constraints into an OCS2 MPC problem, request for comment

```
Hi OCS2 maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a goal and constraints; it does not run MPC. OCS2 is exactly the real-time optimal-control toolbox that would realize a continuous-motion intent for a legged or mobile-manipulation platform.

Nothing here asks OCS2 to change or maintain anything. This is a request for comment.

Two real questions. First, what is the cleanest boundary for "URML intent plus constraints -> an OCS2 MPC problem", and where should the receding-horizon setup live relative to a one-shot intent? Second, which constraints and limits does URML most need to declare so the MPC respects the robot's real capability and the safety envelope as hard constraints? For comparison I am talking to Crocoddyl separately about trajectory optimization, whereas OCS2 is where I would put real-time MPC; please correct that framing if it is wrong.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0347-ocs2-outreach.md


Thanks for OCS2; a usable open MPC toolbox for switched systems is a big deal.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0348: CasADi

**Post to:** https://github.com/casadi/casadi/issues/new
**Title:** URML (open robot intent language): boundary check with a general optimization framework, request for comment

```
Hi CasADi maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a goal and constraints and consumes a trajectory.

I will be honest: CasADi is the deepest layer in a round of motion-planning outreach I am doing, and very likely below the layer URML should ever talk to. CasADi is general symbolic optimization and optimal control that the MPC tools I am also reaching (acados, do-mpc) are built on. URML only benefits indirectly, because the controllers built with CasADi produce the trajectories URML's intent eventually drives. So this is mostly a boundary check and an acknowledgement of an important piece of the stack.

One real question: is there any meaningful point of contact between a high-level intent and safety layer like URML and CasADi itself, or is the correct answer simply that URML talks to the controller built on CasADi and never to CasADi directly? I expect the latter, and a confirmation is genuinely useful.

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0348-casadi-outreach.md


Thanks for CasADi; it is load-bearing for a huge amount of optimal control.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0349: acados

**Post to:** https://github.com/acados/acados/issues/new
**Title:** URML (open robot intent language): capability limits as NMPC constraints, request for comment

```
Hi acados maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a goal and the limits a motion must respect; it does not write the solver.

acados is lower-level than URML, but there is one direct point of contact worth a question: constraints. URML declares the capability and safety limits a controller must honor, and an acados NMPC is exactly where those limits become hard constraints in an optimal-control problem. Nothing here asks acados to change or maintain anything.

So the real question: what is the cleanest way for URML to declare its constraints and limits so they map onto an acados OCP's constraint set, and where should the boundary sit, with URML talking to the MPC node or integration rather than to the solver internals? You are built on CasADi, which I am asking about separately as a pure backend.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0349-acados-outreach.md


Thanks for acados; fast embedded NMPC that people can actually deploy is hard-won.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0350: teb_local_planner

**Post to:** https://github.com/rst-tu-dortmund/teb_local_planner/issues/new
**Title:** URML (open robot intent language): declaring mobile-base constraints for a TEB local plan, request for comment

```
Hi teb_local_planner maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a capability manifest and a safety envelope -> dispatch. URML declares a navigation goal and the mobile base's constraints; it does not compute the local trajectory. teb_local_planner is exactly that local planner.

Nothing here asks the project to change or maintain anything. This is a request for comment.

URML's manifest declares mobility (drive type, max velocity) and, with the envelope, footprint and limits. Those are the constraints a local planner needs. Two real questions. First, what is the cleanest way for URML to declare a mobile base (kinematic model, footprint, velocity and acceleration limits) so a navigation goal is well-posed for TEB? Second, you also maintain mpc_local_planner; which is the right surface for this kind of integration conversation, or do they share enough that one thread covers both? For context, Nav2 is the navigation hub I have engaged separately.

Full write-up, with the manifest mapping table: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0350-teb-local-planner-outreach.md


Thanks for teb_local_planner; it has guided a lot of real robots through tight spaces.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0351: PlanSys2

**Post to:** https://github.com/PlanSys2/ros2_planning_system/issues/new
**Title:** URML (open robot intent language): a PDDL action as a validated URML primitive, request for comment

```
Hi PlanSys2 maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: English sentence -> typed primitive -> static validation against a robot's declared capabilities and a safety envelope -> dispatch. PlanSys2 is the closest project to URML's own layer that I have reached out to, so I want to be upfront that this is a peer conversation, not URML claiming to sit above you.

The overlap is striking. PlanSys2 decomposes a goal into a plan of durative PDDL actions and dispatches them; URML composes validated primitives into behaviors (Layer 3) and turns natural language into intent (Layer 4). A PDDL action looks a lot like a URML primitive, and a PlanSys2 plan looks a lot like a URML behavior. The interesting seam: URML could add static capability and safety validation to each action a task planner emits, so a plan is checked against the robot's real manifest before any action is dispatched into a behavior tree.

Two real questions. First, does a PlanSys2 PDDL action <-> URML primitive correspondence sound sound, or do the action models differ in ways that break it? Second, where should the layers divide: task planning (PlanSys2), intent validation (URML), behavior execution (BT.CPP / py-trees, which PlanSys2 already dispatches into)?

Full write-up, with the mapping: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0351-plansys2-outreach.md


Thanks for PlanSys2; a maintained PDDL planning system for ROS 2 is exactly what the ecosystem needed.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
