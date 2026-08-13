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

# URML and Commercial Use

Status: interim statement, Phase 1.
Established: Phase 1.
Authority: ratified by [RFC-0672](docs/rfcs/0672-commercial-boundary.md). Summarizes [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) for adopters and refines [`GOVERNANCE.md`](GOVERNANCE.md). Does not modify [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md), which controls.

## What this is

A plain answer to a fair question from anyone deciding whether to build on URML: will the parts I depend on ever move behind a paywall, and where does this project intend to make money? The binding answer lives in [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md). This page restates it for people evaluating adoption, and draws the line between the open standard and the commercial work that may grow around it.

## What is free, forever

These components are Apache 2.0 in perpetuity. They will never move behind a paywall, a conditional license, or an "enterprise edition" fork. The binding commitment is [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md); this is the short version:

- the specification documents (every layer, every profile),
- the conformance test suite (the tests are free and public; a certification program may be paid, the tests are not),
- the ROS 2 and PX4 reference runtimes,
- the validator (URML's safety guarantees flow through it, so it is never gated),
- the LLM prompt contract (provider-neutral, so no model vendor can capture the standard),
- the default US-federal compliance policy file.

If you build on these, you are building on ground that does not move.

## Where commercial work happens

URML intends to be sustainable. The revenue comes from products and services built on top of the open core, never from closing it. The standard is the reason the surround has value, so closing the standard would destroy the thing that makes the rest worth anything.

Legitimate commercial surfaces, for the URML organization or for anyone else the Apache 2.0 license permits:

- the **URML-Certified** conformance program and the trademark. The conformance tests stay free; the mark and the audit that backs it are the paid program. This is a Phase 4 program and is not in use yet.
- **audited policy files.** The default policy file is free forever. A third-party accredited legal attestation layered on top, and kept current, is a product.
- **managed and hosted services**, for teams that would rather not self-host: hosted validation, a hosted LLM bridge, hosted simulation. The core always runs fully offline once validated, so hosting is a convenience, never a requirement.
- **premium tooling above the standard**, such as fleet management and observability.
- **training and individual certification.**

These live outside this repository. Nothing commercial is merged here.

## The line, stated plainly

The open core is the standard. The commercial surround is separate, optional, and built on top of it. Depending on URML never requires buying anything from anyone.

This guarantee was written in Phase 0, before URML had any adopters, on purpose. The right time to promise that the ground will not move is before anyone has to stand on it, not after.

## Related

- [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) is the binding commitment and controls if this summary and it ever disagree.
- [`TRADEMARK.md`](TRADEMARK.md) covers the URML and URML-Certified marks.
- [`GOVERNANCE.md`](GOVERNANCE.md) covers how decisions are made.
- [`MANIFESTO.md`](MANIFESTO.md) has the phase roadmap; the certification program is Phase 4.
