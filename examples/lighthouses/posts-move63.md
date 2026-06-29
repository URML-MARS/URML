# Move #63 posts — VLA / robot-foundation mini-wave

Five GitHub Issues, posted under idoco2003. AI-authoring disclosure up front per VIBE.md.
No license-ask anywhere. Titles are em-dash-free. Bodies deliberately vary in shape.

RFC-0641 embodied-CoT, RFC-0642 BAKU, RFC-0643 human2humanoid, RFC-0644 HPT, RFC-0645 RoboPoint.

---

## 1. MichalZawalski/embodied-CoT  (RFC-0641)

**Title:** URML: a capability check on the action your reasoning trace arrives at

**Body:**

Hi, and a disclosure first: this note is AI-assisted prose that I reviewed and approved before posting (background: https://github.com/URML-MARS/URML/blob/main/VIBE.md). Happy to switch to human-only correspondence if you prefer.

I maintain URML (https://urml.dev), a small Apache-2.0 language whose one job is to check an intended robot action against the robot's declared capabilities and a safety envelope before it runs.

What drew me to embodied-CoT specifically is the reasoning trace. Most action heads are a black box, so a pre-actuation check has nothing to read. ECoT writes the plan and the sub-goals down before it acts, which is exactly the legible surface a static check wants. When the model reasons "move to the drawer handle, then close the gripper," URML can ask, while it is still text, whether that handle pose is inside the declared reach and whether the declared gripper can close on it. A plausible but out-of-capability plan gets caught before any motion, and because the trace is explicit, the rejection is explainable rather than opaque.

URML touches none of the policy or the reasoning generation. It is the last checkable step between the emitted action and the hardware.

Two questions I would value your take on:
1. Does an explicit embodied reasoning trace make a capability check meaningfully more useful than it would be on a black-box head, since the intent is already written down?
2. Would a small worked example, mapping one ECoT sub-goal and its action onto a URML manifest and validating it with no execution, be worth having?

Nothing here asks you to adopt, host, or maintain anything. Thanks for the work.

Ido Yahalomi (greenvh@gmail.com)

---

## 2. siddhanthaldar/BAKU  (RFC-0642)

**Title:** URML: a per-robot admissibility check at the action-chunk boundary

**Body:**

Hi. Up front: this is AI-assisted prose I reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md); say the word if you would rather correspond human-only.

I work on URML (https://urml.dev), an Apache-2.0 language that validates an intended action against a robot's declared capability manifest and safety envelope before it reaches the motors.

BAKU is interesting to me precisely because it is multi-task. One policy, many tasks, means the same action-chunk decoder produces motions whose admissible envelope is different from task to task. The chunk for "wipe the counter" and the chunk for "lift the box" land on the same hardware with very different force and reach implications. A single declared-capability check at the chunk boundary stays valid regardless of which task produced the chunk: reach, payload, gripper force from the manifest; keep-out volumes and speed ceiling from the envelope.

To be clear about scope, URML does not touch the policy, the training, or the action representation. It reads the chunk you already emit and answers one question, is this admissible on this robot right now.

Two things I would genuinely like your read on:
1. For a multi-task policy, is a single declared-capability check at the chunk boundary a sensible complement, or does task-conditioning already cover that in practice?
2. Would a small worked example, mapping a BAKU action chunk onto a URML manifest and validating it without executing, be useful to you?

No ask to adopt or host anything. Thanks for BAKU.

Ido Yahalomi (greenvh@gmail.com)

---

## 3. LeCAR-Lab/human2humanoid  (RFC-0643)

**Title:** URML: validating a whole-body command against a declared stability envelope

**Body:**

Hello. A disclosure to start: this note is AI-assisted prose, reviewed and approved by me before posting (https://github.com/URML-MARS/URML/blob/main/VIBE.md). I am glad to go human-only if you prefer.

I maintain URML (https://urml.dev), a small open language for declaring what a robot can do and checking an intended motion against that declaration before it executes.

human2humanoid is the most direct consumer of something URML recently added. We have a whole-body manifest block (kinematic structure plus stability limits: center of mass and support polygon). A learned whole-body controller commands the whole body, which is exactly where a declared stability envelope earns its place: URML can check that a commanded whole-body motion stays inside the declared support polygon and center-of-mass bounds before it executes, as a static admissibility check that sits beside the controller, not inside it.

URML does no balance and runs no control loop. It declares what admissible means for a specific humanoid and checks the command against it; the continuous balancing stays entirely yours.

Two questions:
1. Does a declared whole-body envelope (support polygon, center-of-mass bounds) line up with how a learned humanoid controller already reasons about feasibility, or is the real envelope only knowable at runtime?
2. Would a small worked example, mapping a whole-body command onto that manifest and validating it with no execution, be worth having?

Nothing here asks you to adopt or maintain anything. Thank you for the work on learning humanoid control from human motion.

Ido Yahalomi (greenvh@gmail.com)

---

## 4. liruiw/HPT  (RFC-0644)

**Title:** URML: could a per-embodiment head double as a declared capability surface?

**Body:**

Hi. First, a disclosure: AI-assisted prose, reviewed by me before posting (https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence is available if you would rather.

I maintain URML (https://urml.dev), an Apache-2.0 language built on a premise HPT will recognize from the other side: that the robot-specific surface is a thin declared boundary around a substrate-neutral core. HPT pre-trains a shared trunk and factors the robot-specific part into per-embodiment stems and heads. URML declares a per-robot capability manifest so an intended action can be checked against it before it runs. Same worldview, opposite direction.

The two meet at one seam. HPT's per-embodiment head is where the shared policy becomes a specific robot's actions; URML's manifest is the declaration of what that specific robot can admissibly do. URML would validate the head's output against the manifest for that embodiment, before dispatch, and touch nothing in the trunk, the stems, or the training.

That raises the question I actually want to ask:
1. Since HPT already factors out a per-embodiment stem and head, could that per-embodiment action space double as a declared capability surface the way URML's manifest declares one, or are the two describing genuinely different things?
2. Would a small worked example, mapping one embodiment's head output onto a URML manifest and validating it with no execution, be useful?

No ask to adopt or host anything. Thanks for HPT.

Ido Yahalomi (greenvh@gmail.com)

---

## 5. wentaoyuan/RoboPoint  (RFC-0645)

**Title:** URML: a check that sits one step below your affordance points

**Body:**

Hi. Disclosure up front: this is AI-assisted prose I reviewed before posting (https://github.com/URML-MARS/URML/blob/main/VIBE.md); happy to switch to human-only.

I maintain URML (https://urml.dev), a small Apache-2.0 language that validates an intended robot motion against a declared capability manifest and safety envelope before it runs. Let me be honest about where it sits relative to RoboPoint, because the relationship is layered, not overlapping.

RoboPoint answers where the robot should act, as keypoints. URML does not weigh in on that; predicting the affordance is your model's job. URML's surface opens only one step later, after a point has become a planned motion. At that point a robot's manifest and envelope can check that the motion to the predicted location is in reach, clear of declared keep-out volumes, and within speed and force limits, before the arm moves. So the honest version is that URML validates the motion, not the affordance.

Two questions, and a genuine "no" is a fine answer to the first:
1. Given that RoboPoint stops at the predicted point and a separate step turns it into motion, is a capability and envelope check on that downstream motion a useful guardrail, or does it belong entirely to whatever consumes the points?
2. Would a small worked example, taking a predicted affordance point through to a URML-validated motion with no execution, help show where the line sits?

Nothing here asks you to adopt or maintain anything. Thanks for RoboPoint.

Ido Yahalomi (greenvh@gmail.com)
