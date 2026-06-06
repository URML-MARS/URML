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

# Substrate Conformance

**Status:** Normative. The specification is [`v0.1.0.md`](v0.1.0.md) — the
six-clause contract a runtime MUST satisfy to be **URML-compatible**, the two
conformance tiers (self-reported and URML-Certified), and the normative
spec-gap loop. Specified by [RFC-0014](../../docs/rfcs/0014-substrate-conformance.md).

## Purpose

Layers 1–4 define what URML *is*; this layer defines what it means for a
*runtime* to correctly run it. "URML-compatible" was previously folklore — a
runtime felt compatible if it resembled the ROS 2 reference runtime. This
document makes the contract explicit and testable, so the universality claim is
provable and the eventual *URML-Certified* trademark program has a specification
to certify against.

## The two halves

- **The written contract** is [`v0.1.0.md`](v0.1.0.md) (this directory): the
  rationale and the human-readable obligations.
- **The executable contract** is the [conformance suite](../../conformance/):
  the freely runnable tests whose passing is clause 6 of the contract. Both are
  Apache-2.0 under the [Core Commitment](../../CORE_COMMITMENT.md); only the
  certification *service* may be commercial.

A runtime declares the spec versions and profiles it passes in its own
`CONFORMANCE.md` (the self-reported tier).
