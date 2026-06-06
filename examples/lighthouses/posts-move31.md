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

# Move #31 post bodies: the space / planetary wave

Eight targets. Post under idoco2003 via the channel noted per row (Discussion or
Issue). No license-ask (all Apache/BSD/MIT — state the license). AI-assisted-
authoring disclosure up front. At post time, query the repo's real Discussion
category id (see Move #30 procedure) rather than trusting the ?category= hint.

---

## RFC-0388: Space-ROS

**Post to (Discussion):** https://github.com/space-ros/space-ros/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated intent layer above Space-ROS — request for comment

```
Hi Space-ROS community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches to whatever runs below. Space-ROS is the most natural target I can imagine for that layer: it is ROS 2, which URML already runs against, but with the safety and process rigor space demands.

Nothing here asks Space-ROS to adopt, host, or maintain anything. This is a request for comment, and genuinely a design question.

URML's existing ROS 2 runtime targets Space-ROS directly; move_to / detect / measure / report map onto the same action/service surface. The point of the layer is validate-before-actuate: a command that is not expressible under the declared capability manifest, or that violates the safety envelope, never reaches an actuator. The space-ros/demos robots (Curiosity rover, Canadarm2) are the obvious place to show a "one English sentence moves the rover" loop.

Three real questions: (1) Is a validated, human-readable intent layer above Space-ROS interesting, or does existing tooling already cover it? (2) What should a capability manifest declare to honestly describe a space robot beyond mobility/manipulation/perception — radiation or thermal limits, comms-window / light-time constraints, power budgets? (3) Where is the right seam for a demonstration: one of the space-ros/demos robots, or a fresh minimal manifest?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0388-space-ros-outreach.md

Thanks for Space-ROS; a safety-hardened open ROS 2 for space is exactly the kind of substrate a neutral intent layer should sit above honestly.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0389: F´ (F Prime)

**Post to (Discussion):** https://github.com/nasa/fprime/discussions/new?category=ideas
**Title:** URML (open robot intent language): binding F´ commands to a validated intent layer — request for comment

```
Hi F´ community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches to the substrate below. F´ is interesting to URML because it is a clean, component-driven flight-software substrate whose surface is named commands — and URML already has a pattern for exactly that shape.

Nothing here asks F´ to adopt, host, or maintain anything. This is a request for comment.

When a substrate exposes named operations, URML binds them to its call_program verb rather than inventing a new primitive. That is how URML already binds AUTOSAR ara::com service methods (a service/instance/method id triple). For F´, an F´ component command (component + opcode + typed arguments) would be declared in the URML manifest as a program with a binding; URML validates the binding is complete and the args match the declared signature before anything dispatches. F´ rate-group / cyclic execution maps onto URML's descriptive realtime block (period + watchdog, with no claim that URML enforces hard real-time).

Two real questions: (1) Is a declared program plus a command binding (component / opcode / typed args) the right granularity to name an F´ command from an outside intent layer, or is a different handle more natural? (2) Would the command dictionary be the right source for those binding declarations?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0389-fprime-outreach.md

Thanks for F´; a permissively-licensed, component-driven flight-software framework is a genuinely good substrate to reason about.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0390: core Flight System (cFS)

**Post to (Discussion):** https://github.com/nasa/cFS/discussions/new?category=ideas
**Title:** URML (open robot intent language): binding cFS commands to a validated intent layer — request for comment

```
Hi cFS community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches. cFS is interesting to URML as a flight-software substrate whose surface is named app commands over the software bus — the same shape URML binds for AUTOSAR and proposes for F´.

Nothing here asks cFS to adopt, host, or maintain anything. This is a request for comment.

URML binds named substrate operations to its call_program verb rather than adding a primitive. A cFS app command (app + command code + typed message) would be declared in the URML manifest as a program with a binding; URML validates the binding and args before dispatch. The cFS scheduler's cyclic timing maps onto URML's descriptive realtime block (period + watchdog, no enforcement claim).

Two real questions: (1) Is a declared program plus a command binding (app / command code / typed message) the right granularity to name a cFS command from an outside intent layer? (2) Would the command/telemetry database be the right source for those binding declarations?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0390-cfs-outreach.md

Thanks for cFS; a generic, reusable flight-software architecture flown across so many missions is a great thing to have in the open.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0391: ROSA (JPL)

**Post to (Discussion):** https://github.com/nasa-jpl/rosa/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validate-before-dispatch layer beneath ROSA — request for comment

```
Hi ROSA maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it turns a request into a typed primitive, validates it against a capability manifest and a safety envelope, then dispatches. ROSA is the closest neighbor to URML I have found, and I think the relationship is complementary rather than competitive, which is why I am writing.

Nothing here asks ROSA to adopt, host, or maintain anything. This is a request for comment.

ROSA turns language into ROS calls; URML is the typed-intent, capability-manifest, and safety-envelope layer that validates an action before it reaches an actuator. The framing is "ROSA emits, URML validates before dispatch": the agent keeps its reasoning and toolset, and URML adds the typed, inspectable, refuse-if-out-of-capability contract that a flight or research context tends to want. URML is provider-agnostic at the language layer, so it is not competing with ROSA's agent; it sits beneath the agent's output as the guardrail.

Two real questions: (1) Is a typed validate-before-dispatch layer between an LLM agent and ROS useful in your view, or does ROSA's own tool-call validation already cover it? (2) Where would the seam sit — URML validating ROSA's proposed ROS calls, or ROSA targeting URML primitives as its tool surface? And is there interest in a small joint demo (language -> ROSA -> URML validation -> a ROS 2 / Space-ROS robot)?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0391-rosa-outreach.md

Thanks for ROSA; an open LLM-for-ROS agent is exactly the kind of thing a validation layer wants to sit beneath.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0392: Astrobee (NASA)

**Post to (Issue — Discussions not enabled):** https://github.com/nasa/astrobee/issues/new
**Title:** URML (open robot intent language): a validated intent layer above Astrobee — request for comment

```
Hi Astrobee maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a person writes an English sentence, URML turns it into a typed primitive, validates it against the robot's declared capabilities and a safety envelope, then dispatches. Astrobee is a flagship ROS space robot, and exactly the kind of platform a validated intent layer should be able to sit above honestly.

Nothing here asks Astrobee to adopt, host, or maintain anything. This is a request for comment, and genuinely a design question.

URML's ROS runtime targets Astrobee's ROS surface; navigation, perception, and reporting intents map onto the existing command/action interface. The point in a crewed-vehicle context is validate-before-actuate: a request that exceeds the declared capability manifest (a keep-out zone, a propulsion or speed limit, a docking-state precondition) is refused before it dispatches. The free-flyer shape is a genuinely useful stress test for the manifest.

Two real questions: (1) What should a URML capability manifest declare to honestly describe a free-flyer — keep-out zones, propulsion / speed limits, docking-state preconditions, bay constraints? (2) Is a validated natural-language intent layer above Astrobee's stack interesting for ground-side ops or research/education, and where is the right seam for a demonstration in the simulator?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0392-astrobee-outreach.md

Thanks for Astrobee; free-flying robots on the ISS, in the open, are a wonderful thing to be able to point a language layer at.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0393: OmniLRS

**Post to (Issue — Discussions not enabled):** https://github.com/OmniLRS/OmniLRS/issues/new
**Title:** URML (open robot intent language): driving an OmniLRS lunar rover from validated intent — request for comment

```
Hi OmniLRS maintainers,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches to the substrate below. OmniLRS is interesting to URML as a high-fidelity lunar simulation with a ROS 2 / Space-ROS bridge — a place a URML-validated command can drive a rover end to end with no hardware.

Nothing here asks OmniLRS to adopt, host, or maintain anything. This is a request for comment.

A URML program would drive an OmniLRS lunar rover via the simulator's existing ROS 2 / Space-ROS teleop interface — the same ROS surface URML's runtime already targets. URML also has an optional validation block that records the simulation-fidelity context a deployment was checked in (terrain class, simulator target), which your regolith / deformable-terrain modeling makes concrete. The sim-first posture matches URML's own.

Two real questions: (1) Is a validated natural-language intent layer above OmniLRS interesting as a teaching / demonstration surface for lunar-rover scenarios? (2) What should a URML manifest declare to describe a lunar deployment honestly — terrain/regolith class, slope and traction limits, lighting / thermal constraints — and where is the cleanest seam via the ROS 2 / Space-ROS bridge?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0393-omnilrs-outreach.md

Thanks for OmniLRS; an open, high-fidelity lunar simulator that already speaks Space-ROS is a great place to demonstrate honest, validated intent.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0394: JPL Open Source Rover

**Post to (Discussion):** https://github.com/nasa-jpl/open-source-rover/discussions/new?category=ideas
**Title:** URML (open robot intent language): a validated natural-language teaching layer for the Open Source Rover — request for comment

```
Hi Open Source Rover community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: a learner writes "drive to the rock and take a photo", URML turns it into typed move_to / capture primitives, validates them against the rover's declared capability manifest and a safety envelope, then dispatches. The Open Source Rover is a wonderful platform for that loop, and the angle here is education.

Nothing here asks the project to adopt, host, or maintain anything. This is a request for comment.

The validation step is itself a teaching moment: the manifest makes "what can this robot do" explicit and inspectable, and a request outside it is refused with a clear reason. The loop is hermetic-first — URML's mock substrate runs the whole language -> validation -> execution pipeline with no hardware, so a classroom can use it before a physical rover exists, then point the same program at the real one.

Two real questions: (1) Is a validated natural-language intent layer interesting as a teaching add-on for the rover community? (2) What would make a URML manifest for the rover most useful in a classroom — a ready-made example manifest, a tutorial, a "one sentence drives the rover" community example?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0394-jpl-open-source-rover-outreach.md

Thanks for the Open Source Rover; a build-it-yourself JPL rover in the open is one of the best on-ramps in robotics.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```

---

## RFC-0395: Open MCT (NASA)

**Post to (Discussion):** https://github.com/nasa/openmct/discussions/new?category=ideas
**Title:** URML (open robot intent language): surfacing validated-intent + safety-envelope state in Open MCT — request for comment

```
Hi Open MCT community,

URML (urml.dev) is a small, Apache-2.0 language for describing robot intent: it validates a request against a capability manifest and a safety envelope, then dispatches, emitting an audit trail of what was requested, whether it validated, and what it dispatched. Unlike most things I reach out about, URML does not sit above Open MCT — Open MCT is an observability surface, not a substrate. The honest framing here is integration / visibility.

Nothing here asks Open MCT to adopt, host, or maintain anything. This is a request for comment.

URML's validation results, dispatched-intent audit trail, and safety-envelope state (the active caps, whether a request was refused and why) are themselves operational data an operator might want to watch. Surfaced as an Open MCT telemetry source, that becomes "what intent was requested, did it validate, what did it dispatch, did the envelope refuse anything." This is an integration at the observability layer, not a control relationship in either direction.

Two real questions: (1) Would a URML validated-intent / safety-envelope telemetry source be a sensible Open MCT integration, or is that outside the framework's intended scope? (2) What is the cleanest way to expose an external operational-state source to Open MCT — the telemetry adapter / plugin API — and is there interest in a small example plugin?

Full write-up: https://github.com/URML-MARS/URML/blob/main/docs/rfcs/0395-openmct-outreach.md

Thanks for Open MCT; an open mission-control framework is a great place for a validation layer's state to become visible.

Ido Yahalomi (URML, greenvh@gmail.com)

*AI-assisted prose, maintainer-reviewed before posting (see [VIBE.md](https://github.com/URML-MARS/URML/blob/main/VIBE.md)). Human-only correspondence available on request.*
```
