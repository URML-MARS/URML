---
rfc: 0012
title: Research profile
author: URML Maintainers (maintainers@urml.dev)
state: Draft
created: 2026-05-18
updated: 2026-05-18
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

# RFC-0012: Research profile

## Summary

Add a `research` profile for robotics research platforms (Clearpath Husky/Jackal, Franka, ANYmal, Spot in a lab, custom rigs). Its defining concern is **reproducibility**, not a domain task: a research program should be runnable by another lab from the artifact alone and should record enough to be cited. v0.1 adds no new primitives; it loosens where research legitimately needs freedom (unnamed poses, experimental capability) while *requiring* the provenance and determinism metadata that makes a run reproducible. It is one of the five names in URML's canonical maintenance scope.

## Motivation

Research labs are the other half of the academic flywheel (the educational profile, RFC-0011, is the teaching half). The research ecosystem already standardizes on exactly the platforms URML now has reference adapters for (Clearpath, Franka, ANYmal, Spot). What it lacks, and what URML can uniquely provide, is a substrate-neutral, citable description of *what the robot was asked to do* that survives the lab that produced it. A paper's robot program today is a pile of vendor launch files; a URML research-profile program plus its manifest is a single reproducible artifact. That is a strong reason for a lab to adopt URML and, through papers and students, to spread it.

## Detailed design

A profile spec at `spec/profiles/research/README.md`, structured like the industrial profile. v0.1 scope:

- **No new primitives.** Core vocabulary only (RFC-0002).
- **Loosens, deliberately**: pose-based `move_to` (unnamed coordinates) is *permitted and normal* in research, unlike industrial; experimental sensors/effectors may be declared with `custom` measurement types.
- **Requires, for reproducibility**: a manifest `provenance:` block (so a cited run states its hardware origin) and an explicit `on_error` at every behavior node (no implicit error policy in a result that will be reported in a paper). These are the profile's load-bearing constraints.
- **Default safety envelope**: research rigs are operator-attended in controlled lab space, so the envelope is permissive on capability but keeps the hard core-safety floor (validation is never bypassed; the substrate-neutrality acid test still holds).

### Spec changes

- New `spec/profiles/research/README.md`. Update `spec/profiles/README.md` table. No Layer-1/2/3 schema change for the same reason as RFC-0011 (open profile `Identifier`, zero new primitives/fields in v0.1). The "must declare provenance" and "must set explicit on_error" expectations are documented profile requirements; turning them into validator-enforced errors is a tracked follow-up RFC.

### Validator changes

None in v0.1 (intentional, same staging as RFC-0011 and the industrial profile).

### Conformance suite changes

A later PR adds `conformance/fixtures/research/` when the enforced constraints land. v0.1 research programs are core-primitive programs already covered by core fixtures; nothing is faked.

## Backward compatibility

Fully compatible. Additive new profile name + spec document, pre-v1.0, no code change.

## Drawbacks

"Research" risks becoming the catch-all profile that means "no constraints", which would make it useless as a profile. Mitigation: the profile is defined by what it *requires* (provenance + explicit error policy for reproducibility), not only by what it loosens. If it cannot justify a requirement of its own it should not be a profile; the required-provenance rule is that justification.

## Alternatives considered

- **No research profile; tell labs to use `home`/`industrial`.** Rejected: those profiles forbid exactly what research needs (unnamed poses, experimental capability) and do not require the reproducibility metadata that is the entire point.
- **A `benchmark` profile instead.** Rejected as too narrow: benchmarking is one research activity; the reproducibility requirement generalizes to all of it. A benchmark sub-profile can come later if needed.
- **Ship provenance enforcement in v0.1.** Rejected: same staging argument as RFC-0011; keeps the RFC small.

## Prior art

The existing profile specs; the reproducibility norms of robotics venues (RA-L/ICRA artifact evaluation); ROS-research platform conventions (Clearpath, Franka, ANYmal SDKs). RFC-0004 (provenance) is the mechanism the required-provenance rule reuses; RFC-0002 (primitive economy) is why zero primitives are added.

## Unresolved questions

- The precise enforced form of "explicit on_error everywhere" and "provenance required" for the follow-up RFC. Needs one real published-style program to pin.
- Whether a citation/run-id metadata block belongs in the manifest, the envelope, or a new sidecar. Deferred; v0.1 reuses `provenance` and does not invent a metadata file.

## Implementation note

Ships in one PR with RFC-0011 (the two RFCs + the two profile specs + the `spec/profiles/README.md` table update). No code. Enforcement + `conformance/fixtures/research/` are tracked follow-ups.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is proposed and that v0.1 adds no primitives.
- [x] The Motivation is grounded in a concrete adoption path (papers/students) and the existing reference-adapter ecosystem, not a hypothetical.
- [x] Alternatives are genuinely considered and rejected with reasons.
- [x] Backward compatibility is explicit (additive, pre-v1.0, no code change).
- [x] The "research is not a no-constraint catch-all" risk is met by a required-provenance rule, stated as a drawback-and-mitigation.
