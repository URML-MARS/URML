# Research Profile

**Status:** Draft (v0.1)
**Targets:** URML v0.1
**Created:** 2026-05-18
**RFC:** [RFC-0012](../../../docs/rfcs/0012-research-profile.md)

The fifth URML profile: robotics research platforms in attended lab space. Its defining concern is **reproducibility**, not a domain task. It **adds no new primitives** — it loosens where research legitimately needs freedom and *requires* the metadata that makes a run citable and re-runnable by another lab.

> **Documented vs enforced (read this first).** The "must" items below are *documented profile requirements a conformant runtime applies*. v0.1 adds **no new validator-enforced checks**; turning the required-provenance and explicit-error-policy rules into emitted validator errors is a tracked follow-up RFC. Do not read this profile as validator-enforced in v0.1.

## Application domain

A **researcher author, an attended lab, a run that will be cited**. Clearpath Husky/Jackal, Franka, ANYmal, Spot in a lab, custom rigs. The defining shape is *another lab should be able to reproduce this from the artifact alone*.

## In scope

- Arbitrary core-primitive experiments on declared platforms.
- **Pose-based `move_to`** (unnamed coordinates) — permitted and normal here, unlike the industrial profile; experiments live in coordinate space.
- Experimental sensors/effectors declared with `custom` measurement types.
- Benchmark-style repeated runs where the artifact (program + manifest) is the citable unit.

## Out of scope

- Production safety certification. The research profile is explicitly *research-grade*; a research-profile program is not a safety-certified deployment.
- Unattended or public-space operation. Research rigs in this profile are operator-attended in controlled lab space.

## Profile-required Layer-1 manifest fields

A research-profile manifest **must** declare:

- **`mobility`** (any `drive_type`; research spans all substrates URML targets).
- **`provenance:`** per [RFC-0004](../../../docs/rfcs/0004-compliance-policy.md). This is the profile's load-bearing requirement: a cited run must state its hardware origin so another lab knows what it is reproducing.

A research-profile program **must**:

- Set an **explicit `on_error`** at every behavior node. No implicit error policy in a result that will appear in a paper; the failure handling is part of the reported method.

A research-profile manifest **may**:

- Declare experimental capability (`custom` sensor `measurement_type`, non-standard effectors) that the stricter profiles forbid.

## Default safety envelope

Research rigs are operator-attended in controlled space, so the envelope is permissive on *capability* while keeping the hard core-safety floor that no profile may weaken.

```yaml
envelope_version: "0.1"
deployment_id: <free-form>
description: <free-form>

max_velocity: <platform-declared>   # research uses the platform's rating; attended
require_attended: true              # documented: an operator is present
# The core-safety floor still holds: validation is never bypassed, and the
# substrate-neutrality acid test still applies to any primitive used.
```

## Core-primitive notes

- **`move_to`** — pose-based (unnamed) targets are first-class, not discouraged. Frame must still be declared.
- **error policy** — explicit `on_error` is required at every node (the reproducibility rule), not defaulted.
- **`measure` / `detect`** — `custom` measurement types and experimental object classes are permitted; the manifest still declares them so the artifact is self-describing.

## Compliance policy alignment

The bundled [US-federal default policy](../../../docs/rfcs/0004-compliance-policy.md) applies unchanged. Federally-funded labs are routinely procured under NDAA-style rules; the required `provenance:` block is exactly what the compliance pass consumes, so the reproducibility requirement and the compliance posture reinforce each other rather than conflict.

## Conformance points

v0.1 research programs are core-primitive programs covered by the core conformance fixtures. A dedicated `conformance/fixtures/research/` lands with the follow-up RFC that makes the required-provenance and explicit-error-policy rules validator-enforced. Nothing is faked ahead of enforcement.

## Layer-4 (LLM bridge) integration

The research profile is where the bridge's program-as-citable-artifact framing matters: the generated URML, not a transient chat, is the thing a paper should reference. Bridge-side, not normative to this profile.
