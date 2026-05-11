# URML: Universal Robot Language

**A Manifesto**

*Version 0.1 — Draft*  
*Date: [Fill in]*  
*Author: [Your Name]*  
*Status: Pre-public draft — written to be critiqued, not endorsed*

---

## Preamble

Robots are getting capable faster than they are getting usable. A six-year-old can describe what they want a robot to do; a roboticist needs three weeks to make the robot do it. That gap is not, fundamentally, a hardware problem, and it is not a model problem. It is a vocabulary problem. We do not have a shared way for humans, language models, and robots to talk about *what should happen* — only specialized ways for each individual robot, in each individual frame of reference, to talk about how it moves its own motors.

URML — the Universal Robot Language — proposes to close that gap. Not by replacing the robot operating systems that have taken decades to mature, but by sitting above them: a small, opinionated, human-readable language for describing robot *intent*, paired with reference translators that compile that intent down to whatever runtime lives below. This document explains what we are building, what we are not building, why now, and how.

## What URML Is

URML is a **specification**, not a robot operating system. It defines:

1. A small standardized vocabulary of robot intent primitives (`move_to`, `grasp`, `hover`, `detect`, ...).
2. A composition grammar for sequencing those primitives into behaviors with branching, parallelism, and error handling.
3. A hardware abstraction schema describing what a given robot is capable of.
4. A natural-language contract: the documented way for a large language model to translate plain language into a valid URML program.
5. Domain profiles — focused extensions for home, drone, industrial, and other contexts.
6. A conformance test suite: what a robot runtime must pass to claim "URML-compatible."

URML targets existing robot OSes as compilation backends. The first reference runtime targets **ROS 2**; the second targets **PX4** for drones. URML is not in competition with ROS, PX4, or AUTOSAR. It is the layer that lets one sentence run on all three.

## What URML Is Not

URML is **not** a robot operating system. We do not handle real-time scheduling, motor control, sensor fusion, or message transport. ROS 2 and its peers do that, and they do it well.

URML is **not** a generic agent framework. It is opinionated about being a robot intent language: about physical actuators acting in physical space, with physical safety constraints. It is not LangChain for robots.

URML is **not** a single product. It is a specification with reference implementations. Multiple competing runtimes are welcome and expected.

URML is **not** a hidden-state black box. Every URML program is human-readable text. An LLM can write it, a child can read it (with a glossary), a safety reviewer can audit it before a single actuator moves.

URML does **not** narrow what the Apache 2.0 license permits — any third party may build any extension on top of URML. The canonical URML organization, separately, scopes its own development to civilian, consumer, educational, industrial, and research domains. Profiles outside that scope are not maintained here.

## Why Now

Three things changed in the last few years that make URML possible, and the last few months that make it urgent.

**LLMs got good at structured output.** Until roughly 2023, getting a language model to reliably emit a typed, schema-valid program was a research problem. Today it is a documented prompt pattern. The bottleneck has moved from "can a model produce structured robot commands" to "what is the right structure for a model to produce." That second question is what URML answers.

**Robotics got more affordable and more diverse.** A working home robot now costs less than a phone did a decade ago. The number of distinct robot platforms a typical person encounters — vacuums, drones, delivery bots, robot arms in maker spaces, autonomous mowers, warehouse pickers — has multiplied. The cost of *not* having a common language across them has multiplied with it.

**The substrate has stabilized.** ROS 2 LTS releases through Jazzy and beyond have made it realistic to build durable abstractions on top. PX4 and ArduPilot have done the same for drones. The lower layers are ready to be targeted.

**The window is now.** If the standard form for natural-language robot control is left to individual vendors, every robot will speak a slightly different dialect of English-to-action, locked to its manufacturer's cloud. URML proposes the alternative: a shared, open, free vocabulary before the dialects calcify.

## Who URML Is For

Three audiences, in increasing technical depth.

**End users** never see URML directly. They speak or type in their own language to an interface that uses URML as its target. They benefit from URML the way a phone user benefits from USB-C — by not having to think about it.

**Builders** — engineers, hobbyists, students, integrators — write URML programs by hand or via LLM-assisted tooling, run them on URML-compatible robots, extend the vocabulary through proposed primitives, and develop domain profiles for new contexts.

**Robot makers** implement URML runtimes for their hardware. They translate URML programs into their native control language, pass conformance tests, and label their products URML-compatible.

## Design Principles

The following principles take precedence over feature requests, including our own.

**Intent over instruction.** URML describes what should happen, not how. A `move_to` does not specify a trajectory; that is the runtime's job. This is the line between URML and ROS.

**Substrate-agnostic.** No primitive may assume a specific underlying robot OS. If it cannot be implemented cleanly on both ROS 2 and PX4, it does not belong in the core specification.

**Small vocabulary, deep profiles.** The core primitive set will stay under thirty. Domain richness lives in profiles, not in the core.

**Human-readable, LLM-writable.** Every URML program is plain text in a common serialization. If a competent reader cannot understand a program without external documentation, the syntax is wrong.

**Safety through static verification.** Every URML program is checkable against the target robot's declared capabilities and the active safety envelope *before* execution begins. LLMs do not talk directly to actuators; they talk to a validator that talks to actuators.

**Profiles over forks.** Domain-specific needs are met by adding profiles, not by forking the standard. The core stays one thing.

**Open governance from day one.** Even when this project is one person, the RFC process is documented and the decision log is public.

**Boring where it matters.** Standards succeed when they get out of the way. URML aims to be uninteresting in the same way TCP is uninteresting.

## Architecture: A Layered Stack

URML is organized as five layers. Each layer is a separable specification document and a separable folder in the repository.

```
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Natural Language Interface                    │
│  Documented prompt contract, grammar, examples for LLMs │
├─────────────────────────────────────────────────────────┤
│  Layer 3: Behavior Composition                          │
│  Sequence, branch, parallel, retry, error handling      │
├─────────────────────────────────────────────────────────┤
│  Layer 2: Intent Primitives                             │
│  move_to, grasp, hover, scan, detect, dock, ...         │
├─────────────────────────────────────────────────────────┤
│  Layer 1: Hardware Abstraction                          │
│  Capabilities, joints, frames, sensors, limits          │
├─────────────────────────────────────────────────────────┤
│  Layer 0: Substrate (existing OSes — not part of URML)  │
│  ROS 2 · PX4 / MAVLink · OPC UA · Autoware · ...        │
└─────────────────────────────────────────────────────────┘
                            +
        ┌────────────────────────────────┐
        │ Domain Profiles                │
        │ home · drone · industrial      │
        │ vehicle · agricultural · ...   │
        └────────────────────────────────┘
```

Layer 1 extends existing standards (URDF, SDF) — we do not reinvent robot description. Layer 2 is the specification's center of gravity. Layer 3 borrows ideas from behavior trees and PDDL but ships its own serialization. Layer 4 is mostly a published prompt contract: schema, few-shot examples, and validators. Profiles attach to whichever layer they need to extend.

## A Concrete Example

A human says, in plain English: *"Bring me the red mug from the kitchen."*

An LLM, prompted with the URML contract and the available robot's capability manifest, emits:

```yaml
# URML v0.1 — generated from natural language
profile: home
behavior:
  type: sequence
  on_error: abort_and_report
  steps:
    - move_to:
        location: kitchen
    - detect:
        object: mug
        attributes:
          color: red
        store_as: target_mug
    - grasp:
        target: $target_mug
        force: gentle
    - move_to:
        location: user
        carrying: $target_mug
    - release:
        mode: hand_to_user
```

The URML validator then checks: does this robot's capability manifest declare `mobility`, `manipulation`, and `vision`? Are `kitchen` and `user` resolvable in the current world model? Is `grasp.force: gentle` within the gripper's declared range? If all checks pass, the ROS 2 reference runtime translates each primitive into its native equivalent — Nav2 goals, MoveIt 2 plans, perception pipelines — and executes. If any check fails, the program is rejected with a human-readable explanation that the LLM can use to revise.

The robot does not execute words. It executes verified, typed, statically checked URML.

## Motivating Scenarios

**Home: the multilingual grandparent.** An elderly user speaks to a home assistant in Hebrew: *"תביא לי את התרופה שעל שולחן המטבח."* The LLM, prompted with the home profile and the robot's manifest, produces a URML program that navigates to the kitchen, identifies a labeled medication container, retrieves it, and returns. The user never learned an app interface; the family did not configure custom commands. The same plain-language flow works on any URML-compatible home robot they upgrade to in five years.

**Drone: the citizen inspector.** A roof contractor needs to inspect storm damage on a client's house. They tell their phone, *"Photograph the entire roof from twenty feet up with thirty percent overlap."* The drone profile constrains altitude to legal limits, the safety envelope refuses flight in wind above a declared threshold, and a serpentine `scan` primitive captures the imagery. The same plain-language command works whether the drone is a hobbyist quadcopter running PX4 or a commercial inspection platform running a vendor SDK — both implement the same URML primitives.

**Industrial: the line reconfiguration.** A small manufacturer needs to change a pick-and-place cell from sorting blue widgets to sorting red ones. Instead of programming the PLC, the line manager types, *"Same as before, but pick red instead of blue, and slow down by twenty percent."* The LLM produces a URML diff, the validator confirms the new program is within the cell's safety envelope, and the line is reconfigured in minutes. The expensive integrator is needed only when introducing a genuinely new capability.

## Scope

**In scope for v0.1 through v1.0:**
- Core specification (Layers 1–4)
- Home profile
- Drone profile (civilian)
- Industrial profile (single-arm manipulation, mobile base)
- ROS 2 reference runtime
- PX4 reference runtime (for drone profile)
- Conformance test suite v1
- LLM bridge: documented prompt contract, validators, example prompts

**Stretch goals for v1.x:**
- Agricultural profile
- Autonomous vehicle profile (research-grade; not production safety-certified)
- Healthcare / assistive profile
- Search-and-rescue profile
- Education profile (low-cost platforms: TurtleBot, micro:bit, VEX)
- Underwater profile

**Explicitly out of scope:**
- Profiles outside the URML organization's canonical scope (architecturally permitted on top of URML; not maintained here)
- Real-time control loops (the substrate's job)
- Safety certification claims (we provide tooling; certification is per-deployment)
- Closed-source vendor extensions (welcome to exist; not in this repository)

## Non-Goals

URML will never become a general-purpose programming language. It will never aim to replace ROS, PX4, or AUTOSAR. It will never embed a specific LLM. It will never require cloud connectivity to execute a validated program. It will never sell certification — it will offer it, and the certification process will be public.

## Governance

In Phase 0, governance is one person plus a documented RFC process. Every change to the specification is a numbered RFC in `docs/rfcs/`, with a problem statement, proposed change, alternatives considered, and an implementation note. Even when the only reviewer is the author, the discipline matters: future contributors will inherit a documented decision history rather than a black box.

As the project grows:
- **Phase 1+** — Add a small steering committee of trusted reviewers (3–5 people).
- **Phase 2+** — Establish working groups per domain profile.
- **Phase 3+** — Pursue formal foundation membership (Linux Foundation, Open Source Robotics Alliance, or equivalent) so the standard outlives its founders.

The governance file (`GOVERNANCE.md`) describes the current state honestly. It will say "one person" until that becomes false.

## License Direction

The specification, reference implementations, and conformance suite ship under **Apache License 2.0**. This license is permissive enough to enable broad adoption, includes an explicit patent grant to protect against ambush, and is compatible with the licenses of the systems URML targets (ROS 2 under Apache 2.0; PX4 under BSD-3-Clause).

The **URML name and any future conformance mark are trademarked** and governed by a separate, public trademark policy. This is the standard pattern (Kubernetes, OpenStack, Linux): the code is free, the name protects users from incompatible "URML-compatible" claims.

Contributions require a Developer Certificate of Origin (DCO) sign-off on every commit, in the style of the Linux kernel — lightweight enough for hobbyists, sufficient for legal clarity.

## Roadmap Snapshot

| Phase | Months | Output |
|-------|--------|--------|
| 0 | 0–2 | Manifesto (this document), architecture spec, naming finalized, repo scaffolded |
| 1 | 2–6 | Spec v0.1, ROS 2 reference runtime, home profile, first demo |
| 2 | 6–12 | Drone profile, PX4 runtime, flagship demo video, public launch |
| 3 | 12–18 | Industrial profile, conformance suite v1, first external profile contribution |
| 4 | 18–30 | Autonomous vehicle profile, standards body liaison, certification program |

## How to Engage

For the duration of Phase 0, this project is a solo author working in public. The author welcomes:

- Critique of this manifesto — especially of the primitive vocabulary and the layer boundaries
- Pointers to prior art that should be acknowledged or built upon
- Use case descriptions that strain the current architecture
- Naming suggestions if "URML" proves unsuitable

Direct code contributions are welcome once Phase 1 begins. Until then, this document is the artifact under review.

## Closing

The robots that exist today already work. Most people cannot use them. URML is a bet that the missing piece is not better hardware, larger models, or more sensors — it is a shared, simple, honest way to say what we want, and a runtime trustworthy enough to do it. We do not need to invent that vocabulary from scratch. We need to write it down, agree on it, and ship the translators. That is what this project intends to do.

---

## Appendix A: Glossary

- **URML** — Universal Robot Language. Working name; subject to finalization in Phase 0.
- **Primitive** — An atomic intent (`move_to`, `grasp`, etc.) defined in Layer 2.
- **Profile** — A domain-specific extension to the core (home, drone, industrial, ...).
- **Runtime** — An implementation that translates URML programs into a specific substrate (ROS 2, PX4, etc.).
- **Capability manifest** — A Layer 1 document declaring what a given robot can do.
- **Conformance** — The property of a runtime correctly implementing a given URML version.
- **Substrate** — The underlying robot OS that URML compiles to.

## Appendix B: Open Questions for Phase 0

1. **Final name.** URML is provisional. Alternatives include CRL (Common Robot Language), RIDL (Robot Intent Description Language), OpenIntent, RoboLingua.
2. **Serialization.** YAML for human readability, JSON-LD for tooling, or both. Current lean: both supported, YAML canonical.
3. **Versioning.** Semver applied to the spec, or a date-based scheme (URML 2026-Q3)?
4. **LLM prompt contract location.** In the main spec or in a separate companion document?
5. **First demo robot.** TurtleBot 4 (cheapest, widest community), a simulated platform only, or both?
6. **Hebrew localization in v0.1.** The author works in Hebrew; the spec itself is English-first, but the natural-language layer should be tested in at least two languages from the start.

---

*Critique, do not endorse. This document exists to be improved.*
