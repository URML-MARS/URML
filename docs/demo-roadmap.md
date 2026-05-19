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

# URML Demo Roadmap

Per [`MANIFESTO.md`](../MANIFESTO.md) §Strategic Posture: *"a venture-scale outcome requires URML to become the obvious choice for natural-language robot control... exceptional documentation, demos that travel virally."*

This document is the operational plan for those demos. It maps each phase of the Manifesto roadmap to a concrete substrate, simulator, and scenario, so that "demos" stops being a deliverable label and becomes a build plan with named choices.

A note on scope. This roadmap is **operational**, not normative: changing it is a normal PR, not an RFC. The specifications it points at (the primitives, the profiles, the conformance suite) are normative; those changes go through the RFC process. If this document and any spec disagree, the spec wins.

---

## How the roadmap is structured

Each phase has the same shape: a target substrate, a simulator, a robot, a scenario from the Manifesto, and an honest readiness assessment. Each scenario is intended to be:

- **Recordable** — a single screen-capture or composed video can show the full path from natural-language input to a robot executing in simulation.
- **Reproducible** — anyone can clone the repo, follow a README, and reproduce the demo on a personal machine.
- **Honest** — failures and edge cases are part of the demo. The Manifesto's "abort and report" example is more compelling than a happy-path montage because it shows the validator earning its keep.

The substrate evidence underlying each choice is in [`docs/rfcs/0002-initial-primitive-vocabulary.md`](rfcs/0002-initial-primitive-vocabulary.md) Appendix B.

---

## Phase 1 — Home profile demo

**Manifesto target:** *"Spec v0.1, ROS 2 reference runtime, home profile, first demo"* (months 2–6).

| Field | Choice |
|---|---|
| Substrate | ROS 2 (Humble / Jazzy LTS) |
| Simulator | Gazebo (modern Ignition-derived) |
| Robot | TurtleBot 4 in simulation (with optional matching physical TurtleBot 4 for the hero recording) |
| Scenario | `examples/home/red-mug.urml.yaml` — the *"Bring me the red mug from the kitchen"* example from [`MANIFESTO.md`](../MANIFESTO.md) §A Concrete Example |
| Profile primitives exercised | `move_to`, `detect`, `grasp`, `release` |
| Layer-3 features exercised | `sequence`, `on_error: abort_and_report`, variable bindings |
| Stretch goals | (1) a multilingual variant exercising Hebrew or Spanish NL input; (2) a deliberate-failure variant where the mug is missing and the program aborts with a structured `not_found` |

**Why this scenario:** the Manifesto already centres it, the v0.1 home-profile vocabulary is enough to express it, and TurtleBot 4 is the cheapest physical platform that supports the perception (RGB-D) and manipulation (claw mount or external arm) the scenario needs.

**Readiness:** **High.** Every piece of the toolchain is free, mature, and well-documented. The reference ROS 2 runtime ([`reference/ros2-runtime/`](../reference/ros2-runtime/)) is the long-pole work item; the simulation infrastructure is essentially solved.

**Demo deliverables:**

- A `README.md` in `examples/home/` linking the scenario file to a one-command launch script.
- A 90-second screen-recording showing: user types `"Bring me the red mug from the kitchen"`; the LLM bridge emits URML; the validator accepts; the runtime executes; the robot does the thing.
- A blog post or repository note explaining the substrate-neutrality claim with reference to Appendix A of RFC-0002.

---

## Phase 2 — Drone profile demo (the public-launch flagship)

**Manifesto target:** *"Drone profile, PX4 runtime, flagship demo video, public launch"* (months 6–12).

| Field | Choice |
|---|---|
| Substrate | PX4 (current stable) over MAVLink |
| Simulator | PX4 SITL + Gazebo |
| Aircraft | X500 quadcopter (PX4's default simulated airframe) |
| Scenario | Roof inspection — *"Photograph the entire roof from twenty feet up with thirty percent overlap"* from [`MANIFESTO.md`](../MANIFESTO.md) §Motivating Scenarios |
| Profile primitives exercised | `take_off`, `move_to`, `hover`, `scan`, `capture`, `report`, `land` |
| Layer-3 features exercised | `sequence`, `on_error: abort_and_report`, weather/envelope rejection paths |
| Stretch goals | (1) a programmatic failure (wind exceeds declared envelope → drone refuses takeoff; the LLM bridge reports the structured error back to the user in natural language); (2) a variant where the operator says *"do it again on the south face"* and the LLM bridge produces a diff against the prior URML program |

**Why this is the flagship:** drone footage is inherently compelling for video. A quadcopter executing a serpentine roof scan, captured in screen recording over the simulator, makes for a much more shareable artifact than a TurtleBot wandering a kitchen. The Manifesto's strategic posture explicitly wants the public launch to coincide with a "demo that travels virally" — this is that demo.

**Readiness:** **High.** PX4 SITL + Gazebo is the official PX4 toolchain, free and well-documented. The flight envelope and geofence semantics in the drone profile map directly to MAVLink mission constructs. The reference PX4 runtime ([`reference/px4-runtime/`](../reference/px4-runtime/)) is the long-pole work item.

**Demo deliverables:**

- A polished 2–3 minute video covering the happy-path scan, an envelope-rejection edge case, and a quick "this is URML talking to PX4 with zero ROS dependencies" overlay that lands the substrate-neutrality point.
- A `README.md` in `examples/drone/` with a one-command launch.
- The public-launch announcement references this video as the artifact.

---

## Phase 3 — Industrial profile demo

**Manifesto target:** *"Industrial profile, conformance suite v1, first external profile contribution"* (months 12–18).

| Field | Choice |
|---|---|
| Substrate | ABB RAPID (primary), KUKA KRL (secondary) |
| Simulator (primary) | ABB RobotStudio — free for non-commercial since 2021, vendor-official, polished |
| Simulator (secondary) | RoboDK free tier for the KUKA variant |
| Robot | IRB 1200 (ABB) — compact, six-axis, well-documented in RobotStudio |
| Scenario | Line reconfiguration — *"Same as before, but pick red instead of blue, and slow down by twenty percent"* from [`MANIFESTO.md`](../MANIFESTO.md) §Motivating Scenarios |
| Profile primitives exercised | `move_to` (constrained, must declare frame), `grasp`, `release`, `detect`, profile-extension `pick_from` and `place_at` |
| Layer-3 features exercised | natural-language diff against a stored prior URML program; profile-specific envelope checks (cell perimeter, force ceiling) |
| Stretch goals | (1) the same scenario re-run against KUKA KRL via RoboDK, demonstrating cross-vendor portability of a single URML program; (2) a third run against IEC 61131-3 / CODESYS where the PLC orchestrates the cell |

**Why two vendors:** the cross-vendor run is the strongest evidence the substrate-neutrality acid test holds in practice. *"The same URML program, unchanged, runs on ABB and on KUKA"* is the single most adoption-relevant claim URML can demonstrate, and Phase 3 is where it lands.

**Readiness:** **Medium.** RobotStudio is mature; the URML reference runtime for industrial substrates does not yet exist as of the time of writing. The PLC arm (CODESYS bridge) is a stretch and may slip to Phase 4.

**Demo deliverables:**

- A `README.md` in `examples/industrial/` describing the cell setup, the prior program, and the natural-language reconfiguration step.
- A side-by-side video: ABB on the left, KUKA on the right, same URML program executing on both.
- A short whitepaper or blog post on the cross-vendor result — this is the artifact that opens conversations with industrial integrators.

---

## Stretch / Phase 4+

Roadmap entries beyond Phase 3 are speculative and listed here to make the demo-arc legible, not to commit to them.

| Phase | Target | Substrate / Sim | Manifesto reference |
|---|---|---|---|
| 4 | Autonomous-vehicle profile (research-grade) | Autoware + CARLA — both open-source | Manifesto §Roadmap Snapshot |
| 4+ | Agricultural profile | Gazebo + custom-modeled crop scenes | Manifesto §Scope (stretch) |
| 4+ | Healthcare / assistive profile | Webots or Isaac Sim with humanoid models | Manifesto §Scope (stretch) |
| 4+ | Education profile | Webots + low-cost platforms (TurtleBot, micro:bit, VEX) | Manifesto §Scope (stretch) |
| 4+ | OPC UA Robotics turnkey demo | open62541 + Gazebo-backed device facade, OR a vendor partnership | RFC-0002 Appendix B |
| 4+ | Underwater profile | UUVSim or DAVE | Manifesto §Scope (stretch) |

Search-and-rescue is *not* listed as a standalone phase: the Manifesto names it as a stretch profile, but most search-and-rescue use cases are well-served by the existing drone or vehicle profiles with profile-specific overlays. We will revisit if Phase-1/2 contributors push for a dedicated profile.

---

## What this document is *not*

- **Not a release schedule.** Dates are intentionally absent; the Manifesto roadmap names months 2–6 / 6–12 / 12–18 in broad strokes and that's the right level of precision for Phase 0.
- **Not a contract with users.** "Demo-ready" simulators may change licensing; vendor partnerships may shift availability. Each phase's choices are revisited at the start of that phase.
- **Not a substitute for the reference-runtime READMEs.** Operational details (how to install, how to run the demo) live in [`reference/ros2-runtime/`](../reference/ros2-runtime/), [`reference/px4-runtime/`](../reference/px4-runtime/), etc. This document points at scenarios; the runtime READMEs document the toolchain.

## When this document changes

Add to this document when:

- A demo target moves between phases (escalate or deprioritise).
- A new substrate becomes demo-ready (open-sources, frees a license, ships a usable simulator).
- A planned demo is shipped (mark the entry as **Done** and link to the recording).

All changes are normal PRs.
