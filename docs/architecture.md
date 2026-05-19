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

# URML Architecture

This document expands the architecture section of [`MANIFESTO.md`](../MANIFESTO.md). The Manifesto names the layers and what each is for; this document goes one level deeper. If the two ever disagree, the Manifesto wins.

URML is five layers. Code and specs are organized to mirror them.

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
        │ home · drone · industrial · ...│
        └────────────────────────────────┘
```

The layers are designed to evolve independently. Any change that requires coordinated edits across three or more layers is suspect and probably needs to be re-decomposed before merging.

---

## The substrate-neutrality acid test

This is the single most important architectural rule in URML, repeated here so no one has to dig for it:

> Every Layer-2 primitive **must** be cleanly implementable on a runtime with **zero** ROS dependencies. If it cannot, it is leaking substrate assumptions and needs rework.

ROS 2 is the first reference runtime because its community is largest, not because it is privileged. PX4, AUTOSAR Adaptive, Autoware, OPC UA Robotics, and vendor SDKs are equal targets in principle. The acid test prevents URML from becoming a thin layer over one OS.

The `.github/ISSUE_TEMPLATE/primitive_proposal.md` template enforces this by asking every proposer to sketch both a ROS-2 implementation and a non-ROS implementation up front.

---

## Layer 1 — Hardware Abstraction

Spec home: [`/spec/layer-1-hal/`](../spec/layer-1-hal/).

### What goes here

- The **capability manifest** schema: what a robot declares it can do. Mobility, manipulation (grippers, arms, DOF), perception sensors, declared limits (max velocity, max payload, reachable workspace), declared coordinate frames.
- Reuse of existing standards where they fit: **URDF** and **SDF** for kinematic/geometric description; standard frame conventions; standard unit conventions (SI).
- The **safety envelope** schema: declared limits the robot will not exceed regardless of intent.

### What does NOT go here

- Robot description as raw URDF/SDF only — URML adds a *capability layer* on top so it can answer "can this robot do X?" without parsing kinematics. URDF is referenced, not duplicated.
- Sensor data, runtime state, world models — those are Layer 0 (substrate) concerns or Layer 2 (intent) concerns; this layer is *declared static capability*.
- Wheel-reinvention of URDF.

### Open questions

- Whether the capability manifest is YAML, JSON-LD, or both. Lean: YAML canonical, JSON-LD published for tooling.
- How dynamic capabilities are declared (e.g., a robot whose payload changes when it picks something up). Probably a small runtime-state extension, not a manifest change.

---

## Layer 2 — Intent Primitives

Spec home: [`/spec/layer-2-primitives/`](../spec/layer-2-primitives/).

### What goes here

The atomic units of URML. Each primitive is a verb — `move_to`, `grasp`, `hover`, `scan`, `detect`, `dock`, `release` — with a typed argument schema, a documented semantics, declared capability requirements, and declared safety-envelope checks. Each primitive carries an *intent*, not a trajectory: `move_to(kitchen)` says go there; the runtime decides how.

The Manifesto target is **under thirty primitives** in the core. Profiles add their own.

### What does NOT go here

- Trajectories, motor commands, control loops — Layer 0.
- Composition (sequence, branch, parallel, retry) — Layer 3. A primitive does one thing.
- Natural-language ambiguity. By the time an LLM emits a primitive, the structured fields are unambiguous; ambiguity belongs in Layer 4's resolution step, not in the primitive.
- Profile-specific verbs. If only one domain uses it, it belongs in a profile, not the core.

### Open questions

- The initial primitive set. Will be drafted as RFC-0002.
- Whether `detect` and `scan` are one primitive with a mode parameter or two distinct primitives. The composition-vs-expansion call lives here.

---

## Layer 3 — Behavior Composition

Spec home: [`/spec/layer-3-behavior/`](../spec/layer-3-behavior/).

### What goes here

The grammar for assembling primitives into behaviors:

- **Sequence** — do A, then B, then C.
- **Branch** — given a condition, do A else B.
- **Parallel** — do A and B simultaneously; declare what "done" means (all, any, first-to-succeed).
- **Retry** — repeat A until it succeeds or a bound is hit.
- **Error handling** — `on_error: abort_and_report | continue | substitute(other_behavior)`.
- **Variables** — store the result of one step (e.g., `store_as: target_mug`) and reference it later (`$target_mug`).

Layer 3 borrows freely from **behavior trees** and **PDDL** but ships its own serialization, optimized for human reading and LLM emission.

### What does NOT go here

- New primitives — that is Layer 2.
- A general-purpose programming language. URML is not Turing-complete by design. No arbitrary user-defined functions, no loops with arbitrary conditions, no closures. Composition is bounded and statically checkable.
- Substrate-specific composition (e.g., ROS lifecycle states, MAVLink modes). Those are runtime concerns.

### Open questions

- Whether Layer 3 needs a `parallel-with-handoff` primitive (one parallel branch can pre-empt another). Initial position: no — compose with branch + abort instead.
- How variables are typed and how the validator checks type compatibility across primitives.

---

## Layer 4 — Natural Language Interface

Spec home: [`/spec/layer-4-nl-grammar/`](../spec/layer-4-nl-grammar/). Reference glue: [`/reference/llm-bridge/`](../reference/llm-bridge/).

### What goes here

A **published prompt contract**: the documented way for any LLM (Anthropic, OpenAI, open-weights, on-device) to translate natural language into a valid URML program. Concretely:

- The JSON Schema URML programs must match.
- A small library of few-shot examples spanning the supported profiles.
- The structured arguments an LLM must request from the user (or from the world model) when the natural-language input is ambiguous.
- A validator that takes an LLM's emission and returns either an accepted URML program or a structured error explanation suitable for the LLM to revise from.

### What does NOT go here

- A specific LLM provider. Vendor lock-in here would forfeit the standard's neutrality.
- A natural-language *parser* in the classical sense. URML does not parse English; it asks an LLM to emit URML, then validates the URML.
- The runtime that executes the URML. That is the substrate.

### Open questions

- Whether the prompt contract is one document per profile or a single document with profile sections. Lean: one document, profile sections.
- How multilingual support is structured. The author works in Hebrew; the manifesto names Spanish, Japanese, Mandarin as additional v0.1 targets *structurally*. Initial coverage is English-only; the file-naming scheme in `/examples` reserves the other languages.

---

## Profiles

Spec home: [`/spec/profiles/`](../spec/profiles/).

A **profile** is a domain-specific extension to the core. The three v1.0 profiles are **home**, **drone** (civilian), and **industrial** (single-arm manipulation, mobile base). Stretch profiles are listed in [`MANIFESTO.md`](../MANIFESTO.md) §Scope.

A profile may:

- Add domain-specific primitives (`hover`, `dock`, `pick_from_pallet`).
- Constrain core primitives (e.g., the drone profile's `move_to` must declare altitude; the industrial profile's `move_to` must declare frame).
- Declare a profile-specific safety envelope class (e.g., drones default to "no flight over people without an explicit override").

A profile may **not** weaken the core's safety guarantees or break the substrate-neutrality acid test.

### Out of scope for canonical maintenance

The canonical URML organization develops profiles only within its declared scope: **civilian, consumer, educational, industrial, research**. Profiles outside that scope are architecturally permitted on top of URML (the Apache 2.0 license is not narrowed) but are not maintained in this repository. See [`CLAUDE.md`](../CLAUDE.md) §What Claude Should Never Do and [`MANIFESTO.md`](../MANIFESTO.md) §Scope.

---

## Layer 0 — Substrate (not part of URML)

URML compiles down to whatever runtime lives below. Layer 0 is **named**, not **specified**. Today's targets:

- **ROS 2** (the first reference runtime — first because the community is largest).
- **PX4 / MAVLink** (the drone reference runtime).
- **OPC UA Robotics** (industrial — future reference runtime).
- **Autoware** (vehicle — research-grade future target).
- **AUTOSAR Adaptive** (vehicle — future target).
- **Vendor SDKs** (anyone may ship a URML-compatible runtime by passing the conformance suite).

URML does **not** define motor control, real-time scheduling, sensor fusion, or message transport. Those are the substrate's job, and the substrates do them well.

---

## Cross-cutting concerns

### Validation

Every URML program is checked against (a) the capability manifest of the target robot and (b) the active safety envelope **before** any actuator moves. The validator is the safety boundary; bypassing it at runtime is rejected on review. The validator is part of the Core Commitment — it stays Apache 2.0 forever. See [`/reference/validator/`](../reference/validator/) and [`CORE_COMMITMENT.md`](../CORE_COMMITMENT.md).

### Versioning

Each spec layer and each profile versions independently per semver. v0.x.y allows breaking changes; v1.0.0 is the first stability commitment. Reference runtimes track which spec versions they implement.

### Conformance

A runtime is "URML-compatible" only if it passes the published conformance suite for the declared spec version. The suite is Apache 2.0 and runnable by anyone. The certification *program* (trademark, mark of conformance) may be paid; the tests themselves are not. See [`/conformance/`](../conformance/) and [`CORE_COMMITMENT.md`](../CORE_COMMITMENT.md).
