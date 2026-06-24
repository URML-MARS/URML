---
rfc: 0631
title: Per-capability evidence traceability in the manifest
author: Ido Yahalomi (greenvh@gmail.com)
state: Accepted
created: 2026-06-23
updated: 2026-06-24
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
Accepted 2026-06-24; the maintainer settled the five open questions (recorded in
the Decisions section) and the implementation shipped with this RFC.

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
a claim can carry its source (inferred / declared / derived / verified) and a
structured reference to the evidence. It does not change validation semantics by
default; it makes the manifest a traceable contract instead of an unverifiable
one, and defines an opt-in policy hook that can require evidence for
safety-relevant claims.

**State: Accepted.** Implemented with this RFC (see the Decisions section for the
settled design).

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
  source: derived                                   # inferred | declared | derived | verified
  ref: { kind: usd_prim, value: "/World/robot/gripper" }   # optional, structured
  note: "from UsdPhysics joint limits"              # optional free text
```

`source` is the load-bearing field, ordered weakest to strongest by how
checkable the claim is:

- **inferred** — an LLM or a heuristic guessed it. No external check; the weakest
  class.
- **declared** — asserted by the integrator. Honest default; no external check.
- **derived** — extracted or computed from a structural robot description (USD /
  UsdPhysics, URDF, SDF, a vendor asset). The strongest non-runtime evidence.
- **verified** — confirmed by a runtime smoke test or measurement.

`ref` is a structured pointer to the evidence: `{ kind, value }`, where `kind` is
one of `usd_prim` / `urdf_link` / `test` / `url`, and `value` is the pointer
itself. URML records the reference, it does not dereference it. `note` is
optional human context.

The tag attaches inline to the curated capability sub-objects most worth tracing:
the `mobility` block, each gripper, each camera, each sensor, and the
`whole_body` block.

### Validation semantics

Evidence is **advisory in v0.x**. The validator does not require any claim to be
evidenced, and an unevidenced manifest validates exactly as today (fully backward
compatible). What evidence enables:

- A reviewer or a tool can see, per capability, whether a claim is inferred,
  declared, derived, or verified.
- An opt-in policy (`Policy.evidence_rules`) requires that every capability of a
  chosen kind carry an `evidence` whose `source` is at least a stated
  `min_source`. A capability below the bar, or with no tag at all, draws
  `policy.evidence_insufficient` (error or warning per the rule). This is the
  same opt-in shape the US-federal policy uses for provenance: no rule, no effect.

Keeping the *default* advisory is deliberate: forcing evidence would break every
existing hand-authored manifest and is a deployment decision, not a language one.
The policy hook is how a specific deployment makes evidence mandatory for its
safety-relevant claims.

## Prior art

- Software supply-chain provenance: SLSA, in-toto attestations, SBOM. The idea of
  tagging a claim with how it was established, and a reference to the evidence, is
  borrowed directly and pointed at capability claims instead of build artifacts.
- URML's own RFC-0005 (HBOM) and `manifest_attestation`, which this complements at
  a finer grain.
- The motivating review on isaac-sim/IsaacSim#649 (NVIDIA Isaac).

## Decisions (settled by the maintainer, 2026-06-24)

The five open questions were settled as follows, and the implementation shipped
with this RFC:

1. **Shape: inline.** `evidence` attaches directly to each capability sub-object,
   not a separate top-level block. Fine-grained and local to the claim it traces.
2. **Coverage: a curated set.** `Mobility`, `Gripper`, `Camera`, `Sensor`, and
   `WholeBody`, the capability blocks whose claims are safety-relevant. Not every
   declaration.
3. **`source` enum: add `inferred`.** The set is `inferred < declared < derived <
   verified`, with `inferred` the distinct, weakest class for a model/heuristic
   guess.
4. **`ref` format: structured.** `{ kind, value }`, `kind` one of `usd_prim` /
   `urdf_link` / `test` / `url`. Queryable, not a free string.
5. **Policy hook: defined.** `Policy.evidence_rules` ship in this RFC: an opt-in
   per-capability requirement (`applies_to`, `min_source`, `on_violation`).

## Implementation (shipped with this RFC)

1. `Evidence` and `EvidenceRef` pydantic models in `schemas/common.py`, with the
   shared `EvidenceSource` literal and `EVIDENCE_SOURCE_RANK` ordering.
2. An optional `evidence` field on `Mobility`, `Gripper`, `Camera`, `Sensor`, and
   `WholeBody`, additive and `extra="forbid"`.
3. `EvidenceRule` + `Policy.evidence_rules` (`schemas/policy.py`), evaluated by
   the policy engine independent of provenance; a sub-bar or absent tag draws
   `policy.evidence_insufficient` (new error code). No default-policy change: an
   empty `evidence_rules` (the default) leaves evidence fully advisory.
4. Worked example [`examples/evidence/`](../../examples/evidence/): a mixed-evidence
   manifest (USD-derived gripper/mobility, smoke-verified lidar, hand-declared
   bumper, LLM-inferred camera), an opt-in policy, and a byte-asserted report
   guarded by `reference/validator/tests/test_evidence_example.py`.
5. Conformance fixtures: `compliance/04_evidence_advisory_accepted` (advisory,
   no policy) and `compliance/05_evidence_required_rejected` (the opt-in gate
   refuses the hand-declared sensor).
6. Layer-1 spec note (`spec/layer-1-hal/v0.2.0.md` §2.21).
