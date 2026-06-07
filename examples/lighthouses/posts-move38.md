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

# Move #38 post bodies: the VLA / robot-learning round-2 wave

Eight targets (PRC labs deferred per RFC-0003; already-engaged repos excluded).
Post under idoco2003 via the channel noted per row. No license-ask. AI-assisted-
authoring disclosure up front. At post time, query each Discussion repo's real
category id (Move #30 procedure) for the four Discussion targets.

---

## RFC-0447: LeRobot (Hugging Face)

**Post to (Issue):** https://github.com/huggingface/lerobot/issues/new
**Title:** URML (open robot intent language): wrapping a LeRobot policy in a validated intent + safety envelope — request for comment

```
Hi LeRobot community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes a sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. A learned policy needs exactly what URML provides above it: a typed intent and a validated envelope. LeRobot is the most-starred open robot-learning hub, which makes it a natural place to discuss that pairing.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea is the decide-then-do split applied to learning: a URML intent declares the goal and the envelope, a LeRobot policy (e.g. SmolVLA) produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts. The policy is the actuator; URML is the typed intent and the safety envelope around it. Validate-before-actuate refuses an out-of-capability request (undeclared object, out-of-reach pose, over-limit speed) before motion — a safety seam a learned policy does not provide on its own.

Two real questions: (1) Is wrapping a LeRobot policy in a validated intent layer + safety envelope interesting in the robot-learning context? (2) What should a URML capability manifest declare to describe a LeRobot-driven robot honestly — drive/arm type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0447-lerobot-outreach.md

Thanks for LeRobot; an open end-to-end robot-learning hub is exactly where this kind of layer should be designed with input.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0448: openpi (Physical Intelligence)

**Post to (Discussion):** https://github.com/Physical-Intelligence/openpi/discussions/new?category=ideas
**Title:** URML (open robot intent language): wrapping a pi0 policy in a validated intent + safety envelope — request for comment

```
Hi openpi community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. A state-of-the-art open generalist VLA is exactly the kind of learned policy URML is built to sit above: a typed intent and a validated envelope around the model's actions. openpi (pi0 / pi0-FAST) is one of the strongest open VLAs available, which is why I'm writing.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea is the decide-then-do split applied to learning: a URML intent declares the goal and the envelope, a pi0 policy produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts. The model is the actuator; URML is the typed intent and the safety envelope around it. Validate-before-actuate refuses an out-of-capability request before motion — a safety seam that complements, not replaces, the policy.

Two real questions: (1) Is wrapping a pi0 policy in a validated intent layer + safety envelope interesting? (2) What should a URML capability manifest declare to describe a pi0-driven robot honestly — arm/drive type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0448-openpi-outreach.md

Thanks for openpi; an open release of a frontier VLA is a real gift to the field, and a great place for this discussion.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0449: ManiSkill

**Post to (Discussion):** https://github.com/mani-skill/ManiSkill/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above ManiSkill policies — request for comment

```
Hi ManiSkill community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. ManiSkill is interesting to URML as a high-throughput manipulation benchmark — a clean place to show URML wrapping a learned policy in a validated envelope and to evaluate validated-intent dispatch at scale.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML intent declares the goal and the envelope; a policy trained in ManiSkill produces the low-level action, and URML validates the request against the declared task capabilities before the policy acts (decide-then-do applied to learning). URML drives a ManiSkill task through its Python interface; URML's optional validation block records the simulation-fidelity context a run was checked in. Validate-before-actuate refuses an out-of-capability request before the simulated robot moves.

Two real questions: (1) Is a validated intent layer + envelope above ManiSkill policies interesting for the manipulation-learning community? (2) What should a URML capability manifest declare to describe a ManiSkill task robot honestly — arm/drive type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0449-maniskill-outreach.md

Thanks for ManiSkill; a fast open manipulation benchmark is a great place to think about safety around learned control.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0450: LIBERO

**Post to (Issue):** https://github.com/Lifelong-Robot-Learning/LIBERO/issues/new
**Title:** URML (open robot intent language): a validated intent layer above LIBERO-benchmarked policies — request for comment

```
Hi LIBERO community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. LIBERO is interesting to URML as a standard policy benchmark — a place to evaluate validated-intent dispatch and to express task intent that a learned policy then executes.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML intent declares the goal and the envelope for a LIBERO task; a learned policy produces the low-level action, and URML validates the request against the declared task capabilities before the policy acts — the decide-then-do split applied to learning, evaluated on a standard benchmark. Validate-before-actuate refuses an out-of-capability request before motion, a measurable safety/consistency signal alongside task success.

Two real questions: (1) Is a validated intent layer + envelope above LIBERO-benchmarked policies interesting for the lifelong-learning community? (2) What should a URML capability manifest declare to describe a LIBERO task robot honestly — arm type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0450-libero-outreach.md

Thanks for LIBERO; a widely-used lifelong-learning benchmark is a great place for this discussion.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0451: OpenVLA-OFT

**Post to (Discussion):** https://github.com/moojink/openvla-oft/discussions/new?category=ideas
**Title:** URML (open robot intent language): wrapping an OpenVLA-OFT policy in a validated envelope — request for comment

```
Hi OpenVLA-OFT community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. A fine-tuned VLA is exactly the kind of learned policy URML sits above: a typed intent and a validated envelope around the model's actions. OpenVLA-OFT's optimized fine-tuning is a natural place to discuss that pairing.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea is the decide-then-do split applied to learning: a URML intent declares the goal and the envelope, an OpenVLA-OFT policy produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts. The fine-tuned model is the actuator; URML is the typed intent and the safety envelope around it. Validate-before-actuate refuses an out-of-capability request before motion.

Two real questions: (1) Is wrapping an OpenVLA-OFT policy in a validated intent layer + envelope interesting? (2) What should a URML capability manifest declare to describe an OFT-driven robot honestly — arm type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0451-openvla-oft-outreach.md

Thanks for OpenVLA-OFT; a strong open fine-tuning recipe for VLAs is a great place for this discussion.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0452: RoboCasa

**Post to (Issue):** https://github.com/robocasa/robocasa/issues/new
**Title:** URML (open robot intent language): a validated household-intent layer above RoboCasa — request for comment

```
Hi RoboCasa community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. RoboCasa is interesting to URML as a large-scale everyday-task sim — a natural place to express household intent that a learned policy executes, and to validate that intent against the robot's declared capabilities first.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML household intent ("put the mug in the sink") drives a RoboCasa task, or declares the goal + envelope around a learned policy that produces the low-level action (decide-then-do applied to learning). URML's optional validation block records the simulation-fidelity context a run was checked in. Validate-before-actuate refuses an out-of-capability request before the simulated robot moves.

Two real questions: (1) Is a validated household-intent layer + envelope above RoboCasa interesting for generalist-robot research? (2) What should a URML capability manifest declare to describe a RoboCasa task robot honestly — arm/drive type, reach/DOF, gripper + graspable classes, workspace bounds, object/task vocabulary?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0452-robocasa-outreach.md

Thanks for RoboCasa; a large everyday-task sim is a great place to think about household intent and safety.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0453: BEHAVIOR-1K (Stanford)

**Post to (Discussion):** https://github.com/StanfordVL/BEHAVIOR-1K/discussions/new?category=ideas
**Title:** URML (open robot intent language): a typed, validated intent layer above BEHAVIOR activities — request for comment

```
Hi BEHAVIOR-1K community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. BEHAVIOR-1K is interesting to URML because its activity definitions are essentially structured task intent — a natural place to discuss a typed, validated intent layer above the policies that execute those activities.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML intent expresses a BEHAVIOR activity goal and its envelope; a learned policy produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts. BEHAVIOR's structured activity/predicate definitions and URML's typed intent + manifest are complementary — a place to compare how each expresses task goals and constraints. Validate-before-actuate refuses an out-of-capability request before the simulated robot moves.

Two real questions: (1) Is a typed, validated intent layer above BEHAVIOR activities interesting for embodied-AI research? (2) What should a URML capability manifest declare to describe a BEHAVIOR task robot honestly — arm/drive type, reach/DOF, gripper + graspable classes, workspace bounds, object/activity vocabulary — and how do BEHAVIOR's activity/predicate definitions relate to URML's typed intent + safety envelope?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0453-behavior-1k-outreach.md

Thanks for BEHAVIOR-1K; a thousand-activity embodied-AI benchmark is a fascinating place to compare ways of expressing task intent.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0454: DROID policy learning

**Post to (Issue):** https://github.com/droid-dataset/droid_policy_learning/issues/new
**Title:** URML (open robot intent language): wrapping a DROID-trained policy in a validated envelope — request for comment

```
Hi DROID policy-learning community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. Policies trained on a large real-world dataset are exactly what URML sits above: a typed intent and a validated envelope around the learned action. DROID's in-the-wild dataset and policy-learning code are a natural place to discuss that pairing.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea is the decide-then-do split applied to learning: a URML intent declares the goal and the envelope, a DROID-trained policy produces the low-level action, and URML validates the request against the robot's declared capabilities before the policy acts. The policy is the actuator; URML is the typed intent and the safety envelope around it. Validate-before-actuate refuses an out-of-capability request before motion.

Two real questions: (1) Is wrapping a DROID-trained policy in a validated intent layer + envelope interesting? (2) What should a URML capability manifest declare to describe a DROID-class manipulation robot honestly — arm type, reach/DOF, gripper + graspable classes, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0454-droid-policy-learning-outreach.md

Thanks for the DROID policy-learning code; a large in-the-wild manipulation dataset is a real asset for the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
