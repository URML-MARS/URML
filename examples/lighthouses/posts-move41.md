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

# Move #41 post bodies: the behavior-tree / FSM / orchestration wave

Seven targets (RFCs 0470-0476; 0469 was taken by a parallel-session RFC). Post
under idoco2003 via the channel noted per row. No license-ask (all permissive).
AI-assisted-authoring disclosure up front. At post time, query each Discussion
repo's real category id (Move #30 procedure) for the three Discussion targets.

---

## RFC-0470: BehaviorTree.CPP

**Post to (Discussion):** https://github.com/BehaviorTree/BehaviorTree.CPP/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated-intent layer that interops with BehaviorTree.CPP — request for comment

```
Hi BehaviorTree.CPP community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes a sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. URML has a Layer-3 of its own -- programs are trees of sequence / parallel / branch / retry over typed, validated primitives -- so I'm writing to the people who build the dominant behavior-tree engine to ask how the two should meet.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment, and genuinely a design question.

Two seams, both honest: (1) URML lowers to a tree -- a validated URML program's sequence/parallel/branch/retry compiles to a BehaviorTree.CPP tree, each primitive a leaf, and URML supplies what BT leaves don't check on their own (typed args, capability match, safety envelope, all verified before the tree runs). (2) A leaf dispatches a validated primitive -- a custom BT.CPP / BT.ROS2 node wraps one URML primitive so a hand-authored tree gets validate-before-actuate per leaf. The acid test holds: a behavior tree is control flow; URML is the typed, capability-checked intent the flow carries.

Two real questions: (1) Which seam is more natural -- URML compiling to a BT.CPP tree, or a BT leaf node that dispatches a validated URML primitive? (2) Does URML's sequence/parallel/branch/retry map cleanly onto BT.CPP control nodes (Sequence/Parallel/Fallback/RetryUntilSuccessful), or are there mismatches?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0470-behaviortree-cpp-outreach.md

Thanks for BehaviorTree.CPP; the de-facto robotics BT engine is exactly where this Layer-3 interop question should be asked.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0471: py_trees

**Post to (Discussion):** https://github.com/splintered-reality/py_trees/discussions/new?category=ideas
**Title:** URML (open robot intent language): lowering a validated program to py_trees — request for comment

```
Hi py_trees community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML has a Layer-3 composition (sequence/parallel/branch/retry over typed, validated primitives), and since both URML's reference tooling and py_trees are Python, py_trees is the most natural target for "validated URML program -> a behavior tree you can execute and introspect."

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) URML lowers to a py_trees composite -- Sequence / Parallel / Selector with URML primitives as leaf behaviours, and URML supplies the typed args + capability match + safety envelope checked before the tree ticks. (2) A leaf behaviour dispatches one validated URML primitive, so a hand-authored tree gets validate-before-actuate per leaf. Because both sides are Python, a thin adapter is small and idiomatic.

Two real questions: (1) Which seam is more natural -- URML compiling to a py_trees composite, or a py_trees behaviour that dispatches a validated URML primitive? (2) Does URML's sequence/parallel/branch/retry map cleanly onto py_trees composites + decorators?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0471-py-trees-outreach.md

Thanks for py_trees; a clean, well-introspected Python BT library is a great place for this.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0472: SMACC2

**Post to (Issue):** https://github.com/robosoft-ai/SMACC2/issues/new
**Title:** URML (open robot intent language): lowering a validated program to a SMACC2 state machine — request for comment

```
Hi SMACC2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML has a Layer-3 composition (sequence/parallel/branch/retry over typed, validated primitives). Where a behavior tree is the tree shape of that, a state machine is the other shape -- and SMACC2's event-driven states look like a natural execution target.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) URML lowers to states/transitions -- sequence -> states in series, branch -> guarded transitions, retry -> a self-transition, with URML primitives dispatched from state onEntry, and the typed args + capability + envelope check verified before the machine runs. (2) A SMACC2 client-behavior wraps one URML primitive so a hand-authored state machine gets validate-before-actuate per action. A state machine is control flow; URML is the typed, capability-checked intent the states carry.

Two real questions: (1) Which seam is more natural -- URML lowering to a SMACC2 state machine, or a SMACC2 client-behavior that dispatches a validated URML primitive? (2) Does URML's sequence/parallel/branch/retry map onto SMACC2 states, orthogonal lines, and transitions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0472-smacc2-outreach.md

Thanks for SMACC2; an actively-developed event-driven ROS 2 state-machine library is a great place to think about validated intent over states.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0473: transitions (pytransitions)

**Post to (Discussion):** https://github.com/pytransitions/transitions/discussions/new?category=ideas
**Title:** URML (open robot intent language): lowering a validated robot program to a transitions FSM — request for comment

```
Hi transitions community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML has a Layer-3 composition (sequence/parallel/branch/retry over typed, validated primitives). transitions isn't robotics-specific, but it's what a great many Python robot stacks reach for when they need an FSM -- which makes it a natural, low-friction target for lowering a validated URML program to a state machine.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment, from a robotics project that would be a downstream user.

The lowering: a validated URML program's control flow maps to a transitions machine -- sequence -> ordered states, branch -> conditional transitions, retry -> a self-loop with a guard -- with URML primitives dispatched from on_enter callbacks. URML supplies what a bare FSM doesn't: typed args, a capability match against the robot's manifest, and a safety-envelope check, all verified before the machine starts stepping.

Two real questions: (1) Is "URML validated program -> a transitions FSM" a sensible lowering, and does the hierarchical (HSM) variant cover URML's nested sequence/branch? (2) What callback shape (on_enter per state) is idiomatic for dispatching a validated action?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0473-transitions-outreach.md

Thanks for transitions; the canonical Python FSM is a natural lowering target for a robot-intent language, and I wanted to ask before assuming the mapping.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0474: FlexBE

**Post to (Issue):** https://github.com/FlexBE/flexbe_behavior_engine/issues/new
**Title:** URML (open robot intent language): validated intent under FlexBE's operator-in-the-loop model — request for comment

```
Hi FlexBE community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. URML has a Layer-3 composition (sequence/parallel/branch/retry over typed, validated primitives). FlexBE's operator-in-the-loop model is a natural complement to URML's validate-before-actuate: a validated typed intent is exactly what an operator wants to see and approve before a state actuates.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams: (1) URML lowers to a FlexBE state machine -- control flow maps to states + outcomes, URML primitives dispatched from state execution, with the typed args + capability + envelope check verified before the behavior starts. (2) A FlexBE state wraps one URML primitive so the engine gets validate-before-actuate per state, and the validation verdict is something the operator UI could surface. The operator gate and the static gate reinforce each other.

Two real questions: (1) Which seam is more natural -- URML lowering to a FlexBE state machine, or a FlexBE state that dispatches a validated URML primitive? (2) Could the validation verdict (accepted / refused + reason) surface in the FlexBE operator UI before a state runs?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0474-flexbe-outreach.md

Thanks for FlexBE; an operator-in-the-loop FSM is a great place to pair human supervision with a static validate-before-actuate gate.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0475: SkiROS2

**Post to (Issue):** https://github.com/RVMI/skiros2/issues/new
**Title:** URML (open robot intent language): URML primitives and SkiROS2 skills — request for comment

```
Hi SkiROS2 community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Of everything in robotics, SkiROS2's skill model is the closest match to URML's posture: a parameterized skill with pre/post-conditions over a world model is very near a URML primitive with a typed signature and a capability/envelope precondition. So I'm writing to ask how the two should meet.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment, and a genuine design question.

The alignment: a URML primitive (move_to / grasp / set_output, with capability preconditions) lines up with a SkiROS2 parameterized skill (parameters + world-model pre/post-conditions); a validated URML program could populate or drive a skill sequence. And URML's manifest checks -- capability match, workspace bounds, safety envelope -- are exactly the kind of precondition SkiROS2 reasons over before executing a skill, so URML's static gate complements SkiROS2's world-model gate.

Two real questions: (1) How close is a URML primitive (typed args + capability/envelope precondition) to a SkiROS2 skill (parameters + world-model conditions) -- and could one drive the other? (2) Could URML's capability/envelope checks serve as (or feed) SkiROS2 skill preconditions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0475-skiros2-outreach.md

Thanks for SkiROS2; a skill-based platform with explicit pre/post-conditions is the nearest neighbour to what URML is trying to do, and I'd value your read.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0476: ROSPlan

**Post to (Issue):** https://github.com/KCL-Planning/ROSPlan/issues/new
**Title:** URML (open robot intent language): ROSPlan plans, URML validates + dispatches — request for comment

```
Hi ROSPlan community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Where URML's Layer-3 is authored control flow, a PDDL planner synthesizes it -- and the two compose. I'm writing to ask how a validated-intent layer should sit next to ROSPlan.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two complementary pieces: (1) ROSPlan plans, URML validates + dispatches -- ROSPlan synthesizes an action sequence from a goal, and each action lowers to a URML primitive that is capability- and envelope-checked before dispatch, so a synthesized plan cannot ask for what the robot cannot honestly do. (2) URML primitives as PDDL actions -- a URML primitive's typed signature + capability precondition maps onto a PDDL durative-action with parameters and preconditions, so the planner reasons over the same capability surface URML validates against. The acid test holds: ROSPlan decides what sequence; URML checks each step is typed, capable, and in-envelope before it runs. (This is distinct from a separate engagement with the PlanSys2 PDDL lineage.)

Two real questions: (1) Is "ROSPlan plans -> URML validates + dispatches each action" a sensible division, and where would the plan-to-primitive lowering live (the plan-dispatch layer)? (2) Could a URML primitive's capability/envelope precondition be expressed as a PDDL action precondition, so planning and validation share a surface?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0476-rosplan-outreach.md

Thanks for ROSPlan; a long-running open PDDL task-planning framework is the right place to think about where planning ends and validated dispatch begins.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
