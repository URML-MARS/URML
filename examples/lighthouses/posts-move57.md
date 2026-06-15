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

# Move #57 post bodies: the soft-robotics / assistive wave

Five targets, all GitHub Issues. Post under idoco2003. No license-ask anywhere
(MIT/BSD stated; SoftRobots is LGPL so cross-citation only). AI-assisted-
authoring disclosure up front. Titles carry no em-dash. PyElastica + gym-
softrobot are one post (on PyElastica, referencing the env). Framing: URML
declares the soft-robot/assistive subtask goal + operating envelope and
consumes the computed control or decoded intent; it does not model FEM,
simulate, train, or decode EMG. Assistive framing is research-scope, no
clinical claim. Bodies are varied per target.

---

## RFC-0605: SOFA SoftRobots (anchor)

**Post to (Issue):** https://github.com/SofaDefrost/SoftRobots/issues/new
**Title:** URML (open robot intent language): a declared subtask goal above SOFA soft-robot inverse control (request for comment)

```
Hi SoftRobots maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a goal becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. Your SOFA plugin models soft robots and computes the actuation to reach a target via inverse control, and URML is a layer that could sit above that: it declares the subtask goal and its envelope, and consumes the actuation your control computes. This is a request for comment (cross-citation only, since SoftRobots is LGPL-3.0).

Nothing here asks the project to adopt, host, or maintain anything.

Let me be honest about the fit, because soft robots are not rigid manipulators. URML does not model deformation and does not compute control; that is entirely SoftRobots' domain. What it could add is narrow: a typed statement of the subtask goal (reach this tip pose) plus the admissible envelope (pressure, curvature, range), checked before the computed actuation is trusted. A soft robot's operating envelope maps onto URML's capability manifest and safety envelope, and the inverse control stays yours. Given the LGPL-3.0 license this proposes no shared code, only a layering relationship.

Two real questions: (1) is a typed, validated subtask-intent layer (declare goal + envelope, validate, consume the computed actuation) useful above your inverse control? (2) Does a soft robot's operating envelope map onto a capability manifest + safety envelope cleanly enough to be worth sharing?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0605-softrobots-outreach.md

Thanks for SoftRobots; FEM-based inverse control of soft structures is genuinely hard work, and the narrow question is only where a declared envelope sits relative to it.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0606: PyElastica (and gym-softrobot)

**Post to (Issue):** https://github.com/GazzolaLab/PyElastica/issues/new
**Title:** URML (open robot intent language): a declared control goal above PyElastica, and a policy that declares its envelope (request for comment)

```
Hi PyElastica maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a goal becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. PyElastica simulates soft and slender structures with Cosserat rods, and gym-softrobot trains control policies on it. URML does not simulate and does not train; it relates to both at the intent layer, and I wanted to ask whether that is useful.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

Two seams, and the second is the more interesting. First: URML can declare a soft-robot control goal plus its admissible envelope as a typed statement above the environment. Second, and more interesting: gym-softrobot produces trained policies, and URML has a direction (LearnedPolicy) where a trained policy declares the operating envelope it was trained for, so an intent can be checked against that envelope before the policy is deployed on a real soft robot rather than in sim. For soft robots, where being out of the trained regime can mean a qualitatively different (and unsafe) deformation, that pre-deployment check is the part I would most want your read on.

Two real questions: (1) is a typed declaration of a control goal + envelope useful above PyElastica / gym-softrobot, or already implicit in the environment definition? (2) Could a gym-softrobot-trained policy declare a training/operating envelope a URML intent is checked against?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0606-pyelastica-outreach.md

Thanks for PyElastica; Cosserat-rod simulation is a lovely foundation, and the policy-envelope question is exactly where sim-trained soft control meets the real world.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0607: LibEMG

**Post to (Issue):** https://github.com/LibEMG/libemg/issues/new
**Title:** URML (open robot intent language): validating the action downstream of a decoded EMG intent (request for comment)

```
Hi LibEMG maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a recognized intent becomes a typed primitive, validated against a device's declared capabilities and a safety envelope, then dispatched. LibEMG takes EMG signals all the way to an online control decision, and URML is a natural consumer of that output. This is a research-scope note, with no clinical claim, matching your own posture.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The boundary: LibEMG turns muscle activity into a control decision; URML's role is what happens next. Take that decoded intent, validate the resulting action against the assistive device's declared capabilities and an operating envelope, then dispatch. For an assistive device, the "is this action admissible for this device right now" check is exactly where a typed validation layer earns its place, and URML stays entirely out of the decoding. URML does not classify EMG; it consumes the recognized intent.

Two real questions: (1) is a typed, validated action layer downstream of a decoded EMG intent (the action checked against the device's capabilities + envelope, then dispatched) useful for assistive-device research? (2) Does a decoded LibEMG control decision map cleanly onto a recognized-intent input to such a layer?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0607-libemg-outreach.md

Thanks for LibEMG; making myoelectric control accessible and reproducible is real work, and the action-validation step downstream of the decoder seemed worth asking you about.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0608: Bottango

**Post to (Issue):** https://github.com/EvanBottango/Bottango/issues/new
**Title:** URML (open robot intent language): a portable typed-intent layer over animatronic control (request for comment)

```
Hi Bottango maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: an action becomes a typed primitive, validated against the rig's declared capabilities and a safety envelope, then dispatched. Bottango drives animatronics and performance robots through hand-authored or live motion, with a REST API and open drivers, and an animatronic is an articulated robot whose actions are exactly the kind of typed, capability-checkable intent URML declares.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The mapping: Bottango owns the authoring, the timeline, and the device drivers. URML's candidate role is a portable, typed declaration of an animatronic action (move this joint, run this effector, hold this pose), validated against the rig's declared effectors and their limits, then dispatched through your REST API. For an installation that mixes hand-authored animation with triggered or generated behavior, a typed intent layer makes "what is this rig allowed to do" explicit, and URML's natural-language layer means a triggered behavior could start from a plain-language description and become a checked, runnable action.

Two real questions: (1) is a typed, validated intent layer (an animatronic action checked against the rig's declared effectors and limits, then dispatched over the REST API) useful above Bottango? (2) Does a rig's effector configuration map onto a capability manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0608-bottango-outreach.md

Thanks for Bottango; animatronics is a delightful corner of robotics, and a portable typed-intent layer over the REST API seemed like a natural thing to float with you.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```

---

## RFC-0609: o80

**Post to (Issue):** https://github.com/intelligent-soft-robots/o80/issues/new
**Title:** URML (open robot intent language): a validated intent above real-time PAM control (request for comment)

```
Hi o80 maintainers,

URML (urml.dev) is a small, Apache-2.0 language for robot intent: a goal becomes a typed primitive, validated against the robot's declared capabilities and a safety envelope, then dispatched. o80 is a real-time control interface for pneumatic-artificial-muscle soft robots, which is exactly the kind of concrete control substrate URML is designed to declare validated intent above and dispatch to. This is a request for comment.

Nothing here asks the project to adopt, host, or maintain anything.

The mapping: a PAM soft-robot subtask is a goal plus hard operating bounds (pressure limits, rate limits, reachable range). URML expresses that as a typed intent, validates it against the robot's declared capabilities and a safety envelope, then dispatches to o80's real-time interface; o80 keeps the real-time control. Pneumatic muscles have sharp safe-operating limits, which is exactly where an explicit envelope check ahead of the real-time loop is worth something. o80 is a focused research interface rather than a general framework, so the candidate contribution is narrow and specific: the typed admissibility check before the loop.

Two real questions: (1) is a typed, validated intent layer (a subtask checked against the PAM robot's declared limits, then dispatched) useful above o80? (2) Do a PAM robot's operating bounds (pressure, rate, range) map onto a URML safety envelope cleanly?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0609-o80-outreach.md

Thanks for o80; real-time PAM control is a sharp, well-scoped piece of work, and the envelope-check question fits the safety-critical nature of pneumatic muscles.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see https://github.com/URML-MARS/URML/blob/main/VIBE.md). Human-only correspondence available on request.*
```
