# Move #66 posts — the tail of the cold vein (2 clean)

Posted under idoco2003 on 2026-07-02. VIBE.md disclosure up front, no license-ask, em-dash-free titles.
RFC-0653 YanjieZe/GMR (issue #178), RFC-0654 neobotix/neo_mpc_planner2 (issue #43).

Context: a two-agent free-range search found the cold-GitHub surface essentially exhausted after ~630 contacts / 65 waves. One agent returned zero; these two are the clean residue.

---

## 1. YanjieZe/GMR  (RFC-0653)  -> issue #178

**Title:** URML: validating a retargeted humanoid trajectory against the target's whole-body envelope

Hi, disclosure first: this is AI-assisted prose I reviewed and approved before posting (background: https://github.com/URML-MARS/URML/blob/main/VIBE.md). Glad to switch to human-only if you prefer.

I maintain URML (https://urml.dev), a small Apache-2.0 language whose one job is to check an intended motion against a robot's declared capabilities and a safety envelope before it runs.

GMR is a natural fit because retargeting is exactly where a motion valid on the source can land outside the target's limits. URML recently added a whole-body manifest block (kinematic structure plus stability limits: center of mass and support polygon). It can check that a retargeted whole-body trajectory stays inside the target humanoid's declared joint limits and stability envelope before the robot executes it. The check sits between the retargeting output and the controller, and touches neither the retargeting method nor the control loop.

URML does not retarget, does not run a balance loop, and does not replace GMR. It declares what admissible means for the target humanoid and confirms the retargeted motion is inside it.

Two questions:
1. For real-time retargeting, is a declared whole-body envelope check (joint limits, center-of-mass and support-polygon bounds) on the retargeted trajectory useful before it runs on the target robot, or is feasibility already enforced inside the retargeting?
2. Would a small worked example mapping a retargeted humanoid motion onto a URML manifest, validated with no execution, be worth having?

Nothing here asks you to adopt, host, or maintain anything. Thanks for the work.

Ido Yahalomi (greenvh@gmail.com)

---

## 2. neobotix/neo_mpc_planner2  (RFC-0654)  -> issue #43

**Title:** URML: validating the MPC velocity command against the platform envelope before dispatch

Hi. Up front: this is AI-assisted prose I reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md); say the word if you would rather correspond human-only.

I maintain URML (https://urml.dev), a small Apache-2.0 language that checks an intended action against a robot's declared capability manifest and safety envelope before it runs.

A velocity command headed for the wheels is a clean place for that check, because it is the last artifact before motion. neo_mpc_planner2 computes and emits that command; URML can declare the platform's envelope (maximum linear and angular velocity, acceleration bounds, footprint and any keep-out region) and confirm the commanded setpoint is inside that declaration before it reaches the base. It is a static admissibility check on the emitted command, not a planner and not a controller.

URML does not plan, optimize, or drive the wheels. The MPC keeps optimizing the motion; URML only asks whether the command it hands down is within the declared limits for this specific base.

Two questions:
1. For an MPC local planner, is a declared platform-envelope check (velocity, acceleration, footprint) on the emitted command useful before dispatch, or are those limits already fully enforced inside the MPC constraints in practice?
2. Would a small worked example mapping a mobile-base velocity setpoint onto a URML manifest, validated with no execution, be worth having?

Nothing here asks you to adopt, host, or maintain anything. Thanks for keeping the planner open.

Ido Yahalomi (greenvh@gmail.com)
