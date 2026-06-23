---
rfc: 0631
title: Per-capability evidence traceability in the manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-23
updated: 2026-06-23
supersedes: —
superseded-by: —
---

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

# RFC-0631: Per-capability evidence traceability in the manifest

**Kind: Spec.** Adds an optional manifest field. Additive and backward-compatible.
This RFC scopes the design and leaves open questions for the maintainer; no code
ships until it is accepted.

## Summary

A URML capability manifest declares what a robot can do, and the validator checks
intent against it before dispatch. But most capability claims are hand-written
assertions. A manifest says "this robot has a movable camera, a 2-finger gripper,
and these joint limits," and URML trusts the line. There is coarse provenance at
the manifest level (`manifest_attestation: self_declared | third_party_audited`,
and the structured hardware bill of materials from RFC-0005), but nothing records
*how a specific capability claim was established*: whether it was derived from a
robot description like USD or URDF, declared by an integrator, or verified by a
smoke test.

This RFC adds an optional, advisory `evidence` tag to capability declarations, so
a claim can carry its source (derived / declared / verified) and a reference to
the evidence. It does not change validation semantics; it makes the manifest a
traceable contract instead of an unverifiable one.

**State: Draft.** Design proposal with open questions (see the end). Nothing is
implemented yet.

## Motivation

The motivation is a specific, high-quality outside review. On
[isaac-sim/IsaacSim#649](https://github.com/isaac-sim/IsaacSim/issues/649),
an NVIDIA Isaac engineer reviewed URML's mapping onto Isaac Sim and made the same
point twice, as the design's most important gap:

> Manifest capabilities should be traceable back to evidence. A claim that a robot
> has a movable camera, a gripper, a mobile base, or certain joint limits should
> ideally be derived from or checked against the USD asset and runtime
> configuration, not simply hand-written as an unverifiable assertion.

And:

> Add traceability to generated manifests. A manifest claim should ideally say
> whether it was derived from USD, declared manually, or verified by a smoke test.

That distinction, between a reviewed contract and an unverifiable assertion, is
exactly what URML's validate-before-actuate gate is supposed to protect. The gate
is only as trustworthy as the manifest it checks against. If a safety-relevant
claim (a gripper force range, a reach limit, a service ceiling) was hand-typed and
never checked, the validator is enforcing a guess. Evidence traceability lets a
reviewer, a policy, or a downstream tool tell the difference.

It also unlocks tooling. A USD-derivation tool can stamp `source: derived` with
the originating prim path; a smoke-test harness can stamp `source: verified` after
a runtime check; an integrator's hand-authored field stays honest as
`source: declared`.

## Why not an existing mechanism

**`manifest_attestation`.** Manifest-level (RFC-0004/0007): it attests the whole
manifest as self-declared or third-party-audited. It cannot say that the gripper
was derived from USD while the object vocabulary was hand-declared. Different
granularity.

**The HBOM (RFC-0005).** Provenance of *hardware components* (country of origin,
vendor, CycloneDX). It answers "where did this part come from," not "how was this
capability claim established." Orthogonal.

**Free-text descriptions.** A `description` can say "derived from USD," but it is
not structured, not queryable, and not enforceable by a future policy. Evidence
needs to be a typed field.

So this is a genuine gap, and the right shape is a small, optional, structured tag.

## Proposal

Add an optional `Evidence` value attachable to capability declarations:

```yaml
evidence:
  source: derived        # derived | declared | verified
  ref: "/World/robot/gripper"   # optional: a USD prim path, a URDF link, a test id/URL
  note: "from UsdPhysics joint limits"   # optional free text
```

`source` is the load-bearing field:

- **derived** — extracted or computed from a structural robot description (USD /
  UsdPhysics, URDF, SDF, a vendor asset). The strongest non-runtime evidence.
- **declared** — asserted by the integrator. Honest default; no external check.
- **verified** — confirmed by a runtime smoke test or measurement.

`ref` is a free-form pointer to the evidence (a USD prim path, a URDF link name, a
test identifier or URL). `note` is optional human context.

The tag attaches to the capability sub-objects most worth tracing: grippers,
cameras, sensors, the mobility block, and joint / kinematic limits. (Exact set is
an open question.)

### Validation semantics

Evidence is **advisory in v0.x**. The validator does not require any claim to be
evidenced, and an unevidenced manifest validates exactly as today (fully backward
compatible). What evidence enables:

- A reviewer or a tool can see, per capability, whether a claim is derived,
  declared, or verified.
- A future, opt-in policy could require `verified` (or at least `derived`)
  evidence for safety-envelope-relevant claims, the same way the US-federal policy
  gates provenance today. That policy is out of scope here; this RFC only lays the
  rail.

Keeping it advisory is deliberate: forcing evidence would break every existing
hand-authored manifest and is a deployment decision, not a language one.

## Prior art

- Software supply-chain provenance: SLSA, in-toto attestations, SBOM. The idea of
  tagging a claim with how it was established, and a reference to the evidence, is
  borrowed directly and pointed at capability claims instead of build artifacts.
- URML's own RFC-0005 (HBOM) and `manifest_attestation`, which this complements at
  a finer grain.
- The motivating review on isaac-sim/IsaacSim#649 (NVIDIA Isaac).

## Implementation plan (only after acceptance)

1. An `Evidence` pydantic model (`source` enum, optional `ref`, optional `note`).
2. An optional `evidence` field on the chosen capability sub-models (Gripper,
   Camera, Sensor, Mobility, and a limits carrier), additive, `extra="forbid"`.
3. No new validator pass for v0.x (advisory). Optionally a Pass-2 info-level note
   when a safety-relevant claim is `declared` only, behind a flag.
4. A worked example: a small manifest with mixed evidence (a gripper `derived`
   from USD, an object vocabulary `declared`, a reach limit `verified`).
5. A conformance fixture pair: an evidenced manifest and a plain one both validate.
6. Docs: a Layer-1 note on evidence, and guidance that a USD/URDF derivation tool
   should stamp `source: derived` with the source ref.

## Open questions (for the maintainer)

1. **Shape.** Inline `evidence` on each capability sub-object (fine-grained,
   slightly invasive), versus a separate top-level `evidence:` block that
   references capabilities by path/name (centralized, decoupled). The RFC leans
   inline.
2. **Coverage.** Which capabilities carry it: a curated set (grippers, cameras,
   sensors, mobility, joint limits), or every declaration?
3. **`source` enum.** Is derived / declared / verified the right set? Add
   `inferred` (e.g. an LLM or heuristic guessed it) as a distinct, weaker class?
4. **`ref` format.** Free string, or a structured `{ kind: usd_prim | urdf_link |
   test | url, value }`?
5. **Policy hook.** Advisory only now (recommended), or define the opt-in policy
   that can require evidence for safety-relevant claims in the same RFC?
