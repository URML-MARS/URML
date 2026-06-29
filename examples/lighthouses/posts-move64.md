# Move #64 posts — university research-lab lane (2 clean)

Posted under idoco2003 on 2026-06-29. AI-authoring disclosure (VIBE.md) up front, no license-ask, em-dash-free titles.
RFC-0646 epfl-lasa/iiwa_ros, RFC-0647 utra-robosoccer/soccerbot.

---

## 1. epfl-lasa/iiwa_ros  (RFC-0646)  -> issue #122

**Title:** URML: validating a learning-from-demonstration trajectory against the iiwa envelope

Hi, and a disclosure first: this is AI-assisted prose that I reviewed and approved before posting (background: https://github.com/URML-MARS/URML/blob/main/VIBE.md). Glad to switch to human-only correspondence if you prefer.

I maintain URML (https://urml.dev), a small Apache-2.0 language whose one job is to check an intended robot motion against the robot's declared capabilities and a safety envelope before it runs.

iiwa_ros caught my attention because of the learning-from-demonstration layer on top of the iiwa control. A demonstrated or generalized trajectory still has to be admissible on the specific arm it will run on, and that is exactly the seam URML fits: declare the arm's reach, payload, joint limits, and the active keep-out and speed envelope, and check a generalized trajectory against that declaration before the impedance controller consumes it. The check sits between the learned motion and the joint commands, and it touches neither the demonstration nor the control law.

URML does not do impedance control, does not learn, and does not replace the stack. It is the static admissibility step that answers whether a given trajectory is inside the declared envelope for this arm.

Two questions I would value your take on:
1. For a learning-from-demonstration pipeline, is a declared-capability and envelope check on the generalized trajectory a useful step before the controller runs it, or is feasibility already guaranteed upstream in practice?
2. Would a small worked example mapping an iiwa trajectory onto a URML manifest, validated with no execution, be worth having?

Nothing here asks the project to adopt, host, or maintain anything. Thanks for the work.

Ido Yahalomi (greenvh@gmail.com)

---

## 2. utra-robosoccer/soccerbot  (RFC-0647)  -> issue #921

**Title:** URML: validating a whole-body kick or step against a declared stability envelope

Hi. Up front: this is AI-assisted prose I reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md); say the word if you would rather correspond human-only.

I maintain URML (https://urml.dev), a small Apache-2.0 language for declaring what a robot can do and checking an intended motion against that declaration before it executes.

soccerbot is a good fit for the part of URML written most recently. A humanoid that kicks, walks, and recovers balance is commanding its whole body, which is where a declared stability envelope earns its place. URML has a whole-body manifest block (kinematic structure plus stability limits: center of mass and support polygon), and it can check that a commanded whole-body motion, a kick or a step, stays inside that declared envelope before the locomotion controller executes it. It is a static admissibility check beside the controller, not a balance loop inside it.

URML does not walk, kick, or balance, and it does not replace any part of your stack. It declares what admissible means for the platform and checks the commanded motion against it.

Two questions:
1. Does a declared whole-body envelope (support polygon, center-of-mass bounds) line up with how the soccer stack already reasons about a stable kick or step, or is the real envelope only knowable at runtime?
2. Would a small worked example mapping a soccerbot whole-body motion onto a URML manifest, validated with no execution, be useful, maybe as a teaching artifact for new team members?

Nothing here asks the project to adopt, host, or maintain anything. Thanks for keeping a full open humanoid stack alive; that is rarer than it should be.

Ido Yahalomi (greenvh@gmail.com)
