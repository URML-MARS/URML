# Layer 1 — Hardware Abstraction

**Status:** Pre-draft. The specification document for this layer is targeted for v0.1; see roadmap in [`MANIFESTO.md`](../../MANIFESTO.md).

## Purpose

Layer 1 defines how a robot **declares what it can do**. A URML-compatible robot ships a *capability manifest* — a small, machine-readable document describing its mobility, manipulation, perception, declared coordinate frames, declared physical limits, and the safety envelope it operates within. The validator uses this manifest to decide whether a given URML program can be executed by this robot before any actuator moves.

Layer 1 is intentionally a thin layer **on top of existing standards**. URDF and SDF already describe kinematic and geometric structure; URML reuses them rather than reinventing. The Layer-1 contribution is the *capability layer above URDF* — the abstraction that lets a URML program ask "can this robot grasp?" without parsing kinematics.

## Boundaries

Layer 1 must **not** assume:

- A specific underlying robot operating system. The manifest is substrate-agnostic; a robot running ROS 2, PX4, AUTOSAR, OPC UA Robotics, or a vendor SDK can all declare the same capabilities the same way.
- That a robot's capabilities are static at runtime. The manifest declares *baseline* capabilities; runtime extensions (e.g., a gripper picks up a tool that extends its reach) are a separate concern, addressed at most by a small runtime-state extension.
- Sensor data, runtime state, or world-model contents. Those flow through the substrate, not the manifest.

Layer 1 must also **not** absorb concerns from adjacent layers:

- **From Layer 2:** what a primitive *does*. Layer 1 says the robot has a gripper; Layer 2 defines `grasp(...)`.
- **From Layer 3:** composition. Manifests describe atomic capability, not behavior.

## What goes here when this document is drafted

- The capability manifest schema (YAML canonical; JSON-LD for tooling). Sections: mobility, manipulation, perception, frames, limits, safety envelope.
- The safety-envelope schema: declared maximums (velocity, payload, force), declared forbidden zones, declared required preconditions.
- The relationship to URDF/SDF: how a Layer-1 manifest references the URDF that describes the robot's structure.
- A worked example: the capability manifest for the v0.1 demo robot (likely a TurtleBot 4; see `docs/open-questions.md` Question 5).

## Conformance points

When this layer is drafted, the conformance suite will test:

- Every required field is present.
- Declared limits are internally consistent (e.g., declared `max_velocity` is non-negative and finite).
- The manifest's frame declarations are consistent with the referenced URDF.
- The validator correctly rejects programs that exceed declared capability or violate the safety envelope.

## Related documents

- [`/docs/architecture.md`](../../docs/architecture.md) §Layer 1.
- [`/docs/glossary.md`](../../docs/glossary.md) — capability manifest, frame, safety envelope.
- [`/spec/profiles/`](../profiles/) — each profile may declare additional manifest fields it requires.
