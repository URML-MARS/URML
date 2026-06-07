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

# Move #37 post bodies: the medical / surgical research-robotics wave

Seven targets (SurRoL/CUHK deferred per the PRC/HK rule). RESEARCH / SIMULATION
framing ONLY — no clinical claim in any post. Post under idoco2003 via the channel
noted per row. No license-ask (several carry custom academic / LGPL licenses —
state or omit, never ask). AI-assisted-authoring disclosure up front. At post time,
query each Discussion repo's real category id (Move #30 procedure) for the three
Discussion targets.

---

## RFC-0440: Surgical Robotics Challenge

**Post to (Discussion):** https://github.com/surgical-robotics-ai/surgical_robotics_challenge/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated research intent layer above the Surgical Robotics Challenge — request for comment

```
Hi Surgical Robotics Challenge community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes a sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. To be clear up front: this is a research and simulation discussion only — URML makes no clinical claim and is not for patient use, which matches this project's own "not for clinical use" norm. The challenge env is interesting to URML because turning a high-level surgical-subtask description into validated robot action in a research sim is exactly URML's shape.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS runtime meets the challenge environment on its AMBF/ROS surface; a research subtask ("approach the needle, then insert at the entry marker") lowers onto the dVRK PSM/ECM interface as typed primitives — the decide-then-do split. Validate-before-actuate refuses an out-of-workspace pose or an undeclared instrument before motion, a research-grade safety boundary. URML's safety envelope is a place to declare the research constraints a subtask must respect (workspace bounds, instrument set, no-go regions).

Two real questions: (1) Is a validated intent layer above the challenge sim interesting as a way to express and check surgical-subtask intent in research? (2) What should a URML capability manifest declare to describe a research surgical robot honestly — arms/instruments, reach/DOF, workspace bounds, instrument vocabulary?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0440-surgical-robotics-challenge-outreach.md

Thanks for the Surgical Robotics Challenge; an open, active research sim for robot-assisted suturing is exactly where this kind of layer should be designed with input.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0441: AMBF (WPI)

**Post to (Discussion):** https://github.com/WPI-AIM/ambf/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated research intent layer above AMBF — request for comment

```
Hi AMBF community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. To be clear up front: this is a research and simulation discussion only — URML makes no clinical claim and is not for patient use. AMBF is interesting to URML as a high-fidelity research surgical simulator: a place to drive a research robot from validated intent before any hardware.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML research program drives an AMBF-simulated manipulator through the AMBF ROS interface; URML's optional validation block records the simulation-fidelity context a run was checked in, which AMBF's soft-body realism makes concrete. Validate-before-actuate refuses an out-of-workspace or undeclared-instrument request before the simulated robot moves — a research safety seam consistent with the "not for clinical use" norm. The sim-first posture matches URML's own (the reference runtime ships a mock substrate).

Two real questions: (1) Is a validated intent layer above AMBF interesting as a research surface for surgical and multi-body robot scenarios? (2) What should a URML capability manifest declare to describe an AMBF-simulated research robot honestly — bodies/arms, reach/DOF, instrument set, workspace bounds?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0441-ambf-outreach.md

Thanks for AMBF; a real-time soft-body surgical sim is a genuinely valuable research tool.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0442: da Vinci Research Kit (dVRK)

**Post to (Discussion):** https://github.com/jhu-dvrk/sawIntuitiveResearchKit/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated research intent layer above the dVRK — request for comment

```
Hi dVRK community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. To be clear up front: this is a research discussion only — the dVRK is explicitly not for clinical use, and URML makes no clinical claim either. A dual-arm research surgical robot with a mature open control stack is a strong fit for URML's validated, bimanual manipulation intent.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS runtime meets the dVRK on its CRTK / ROS surface; a research subtask lowers onto the PSM/ECM arms as typed primitives, and URML's arm selector + bimanual primitive address the dVRK's two patient-side manipulators. Validate-before-actuate refuses an out-of-workspace pose or an undeclared instrument before motion — a research safety boundary aligned with the dVRK's own norm.

Two real questions: (1) Is URML's CRTK / ROS surface mapping the right seam for a research validated-intent layer above the dVRK? (2) What should a URML capability manifest declare to describe the dVRK honestly — PSM/ECM arms, instrument set, reach/DOF, workspace bounds — and does an arm selector + bimanual primitive map cleanly onto the two patient-side manipulators?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0442-dvrk-outreach.md

Thanks for the dVRK and the cisst/SAW stack; the open research platform that so much surgical-robotics work runs on is the natural place for this discussion.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0443: ORBIT-Surgical

**Post to (Issue):** https://github.com/orbit-surgical/orbit-surgical/issues/new
**Title:** URML (open robot intent language): wrapping a learned surgical-research policy in a validated envelope — request for comment

```
Hi ORBIT-Surgical maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. To be clear up front: this is a research and simulation discussion only — URML makes no clinical claim. ORBIT-Surgical is interesting to URML because its surgical RL/IL sim on Isaac Lab is a clean place to wrap a learned research policy in a validated envelope.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea is the decide-then-do split applied to learning: a URML research intent declares the subtask goal and the envelope, a learned policy in ORBIT-Surgical produces the low-level control, and URML validates the request against the declared research constraints before the policy acts. The policy is the actuator; URML is the typed, validated intent and the research safety envelope around it.

Two real questions: (1) Is wrapping a learned surgical-research policy in a validated intent layer + envelope interesting in the RL/IL-sim context? (2) What should a URML capability manifest declare to describe a simulated surgical robot honestly — arms/instruments, reach/DOF, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0443-orbit-surgical-outreach.md

Thanks for ORBIT-Surgical; a clean open surgical-RL sim on Isaac Lab is a great place to think about safety around learned surgical-research control.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0444: LapGym / sofa_env

**Post to (Issue):** https://github.com/ScheiklP/sofa_env/issues/new
**Title:** URML (open robot intent language): a validated research intent layer above sofa_env (LapGym) — request for comment

```
Hi LapGym / sofa_env maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. To be clear up front: this is a research and simulation discussion only — URML makes no clinical claim. Your SOFA-based laparoscopic-surgery RL envs are a clean place to drive a research robot from validated intent and to wrap a learned policy in a validated envelope.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

A URML research-subtask intent drives a sofa_env laparoscopic scenario, or declares the goal + envelope around a learned policy that produces the low-level control (decide-then-do applied to learning). Validate-before-actuate refuses an out-of-workspace or undeclared-instrument request before motion — a research safety seam. URML's optional validation block records the simulation-fidelity context (SOFA deformable tissue) a run was checked in.

Two real questions: (1) Is a validated research intent layer above sofa_env interesting for laparoscopic-surgery RL/research? (2) What should a URML capability manifest declare to describe a laparoscopic research robot honestly — instruments, reach/DOF, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0444-sofa-env-lapgym-outreach.md

Thanks for LapGym; a permissive deformable-tissue laparoscopic sim is a real asset for surgical-robotics research.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0445: SurgicalGym

**Post to (Issue):** https://github.com/SamuelSchmidgall/SurgicalGym/issues/new
**Title:** URML (open robot intent language): wrapping a learned surgical-research policy in a validated envelope — request for comment

```
Hi SurgicalGym maintainer,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. To be clear up front: this is a research and simulation discussion only — URML makes no clinical claim. SurgicalGym is interesting to URML because its GPU Isaac-Sim surgical RL sandbox is a clean place to wrap a learned research policy in a validated envelope.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The idea is the decide-then-do split applied to learning: a URML research intent declares the subtask goal and the envelope, a learned policy in SurgicalGym produces the low-level control, and URML validates the request against the declared research constraints before the policy acts. Validate-before-actuate refuses an out-of-workspace or undeclared-instrument request before the simulated robot moves.

Two real questions: (1) Is wrapping a learned surgical-research policy in a validated intent layer + envelope interesting in the GPU-RL-sim context? (2) What should a URML capability manifest declare to describe a simulated PSM/ECM or STAR research robot honestly — arms/instruments, reach/DOF, workspace bounds, observation/action assumptions?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0445-surgicalgym-outreach.md

Thanks for SurgicalGym; a fast open GPU surgical-RL sandbox is a useful contribution to the research community.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0446: Raven-II (UW Biorobotics)

**Post to (Issue):** https://github.com/uw-biorobotics/raven2/issues/new
**Title:** URML (open robot intent language): a validated research intent layer above Raven-II — request for comment

```
Hi UW Biorobotics / Raven-II maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. To be clear up front: this is a research discussion only — URML makes no clinical claim. Raven-II is one of the few genuinely open surgical-robot hardware platforms, and a validated research intent layer above a dual-arm open surgical robot is a natural fit.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

URML's ROS runtime meets Raven-II on its control/ROS surface; a research subtask lowers onto the two arms as typed primitives, and URML's arm selector + bimanual primitive address the dual-arm platform. Validate-before-actuate refuses an out-of-workspace pose or an undeclared instrument before motion — a research safety boundary.

Two real questions: (1) Is a validated research intent layer above Raven-II interesting for the lab's surgical-robotics research? (2) What should a URML capability manifest declare to describe Raven-II honestly — two arms, instruments, reach/DOF, workspace bounds — and does an arm selector + bimanual primitive map cleanly onto its two arms?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0446-raven2-outreach.md

Thanks for Raven-II; an open-hardware surgical-research robot is a foundational contribution to the field.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
