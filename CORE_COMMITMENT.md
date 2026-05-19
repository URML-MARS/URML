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

# URML Core Commitment

**Status:** Draft  
**Established:** Phase 0  
**Authority:** Second only to [`MANIFESTO.md`](MANIFESTO.md) in this repository's precedence order (see [`CLAUDE.md`](CLAUDE.md) §Reference Documents).

---

## What This Document Is

This document names the components of URML that the URML organization commits to keeping under the **Apache License 2.0 in perpetuity**, with no migration to a more restrictive license, no "enterprise edition" fork, and no paywall.

This commitment is being made in **Phase 0** — before any commercial entity exists — precisely because the open-core re-licensing controversies of the last decade (Elastic, MongoDB, HashiCorp, Redis) show that the time to draw this line is *before* adoption, not after. A line drawn after adoption is read by the community as a betrayal of trust; a line drawn before adoption is read as a foundational guarantee.

The full strategic rationale is in [`CLAUDE.md`](CLAUDE.md) §Strategic Posture. The summary: the standard is the moat. Commercial value lives in the surround. Closing the standard would destroy the moat.

## The Commitment

The following components of URML will always be Apache 2.0:

1. **The specification documents.** Every version of every layer (Layer 1 hardware abstraction, Layer 2 intent primitives, Layer 3 behavior composition, Layer 4 natural-language interface) and every domain profile maintained by the URML organization. See [`spec/`](spec/).

2. **The conformance test suite.** The tests that determine whether a runtime is URML-compatible. The certification *program* may be paid; the conformance *tests* are free, public, and runnable by anyone. See [`conformance/`](conformance/).

3. **The ROS 2 reference runtime.** The first reference implementation. See [`reference/ros2-runtime/`](reference/ros2-runtime/).

4. **The PX4 reference runtime.** The second reference implementation, targeting drones. See [`reference/px4-runtime/`](reference/px4-runtime/).

5. **The validator.** The static verification engine that checks a URML program against a capability manifest and safety envelope before execution. URML safety guarantees flow through this component; gating it behind a license would forfeit them. See [`reference/validator/`](reference/validator/).

6. **The LLM prompt contract.** The published schema, examples, and validators that allow language models to reliably emit valid URML. This is the surface by which natural-language interfaces meet URML; making it provider-neutral and free is what prevents the standard from being captured by any single LLM vendor. See [`reference/llm-bridge/`](reference/llm-bridge/).

7. **The default compliance policy file.** Per RFC-0003, URML the standard aligns with US federal robotics regulation. The default policy file the validator loads when no `--policy` is specified — currently `us_federal_default.yaml`, and any successor — remains Apache 2.0 and freely usable. URML's regulatory teeth are a public good. See [`reference/validator/src/urml_validator/policies/`](reference/validator/src/urml_validator/policies/).

## What This Commitment Does Not Cover

The boundary is deliberately explicit, so there is no ambiguity about where commercial work *can* legitimately happen:

- **Commercial products built on top of URML** by the URML organization or any other party — managed services, premium tooling, fleet management platforms, hosted simulation, observability dashboards, training, certification of individuals. These are out of scope of this repository and not subject to this commitment.
- **The URML trademark** and the **URML-Certified conformance mark**, governed by a separate, public trademark policy. Using the marks requires conformance; the conformance tests themselves remain free.
- **Certified or audited policy files.** The default policy in (6) above is free forever. *Audited* policy files — those carrying a third-party legal-audit certification (e.g., "Audited against NDAA §889 and FY26 by an accredited firm as of YYYY-MM-DD") — are a legitimate commercial surface for the URML organization or any other party. The uncertified default is free; certifications, attestations, and the legal opinions that back them are not.
- **Third-party extensions, profiles, and runtimes** that are not maintained by the URML organization. They may choose any license they wish.

## Modifying This Document

This document is intentionally hard to modify. Changes require:

1. A formal RFC, filed in [`docs/rfcs/`](docs/rfcs/).
2. A public draft period of **at least 30 days**.
3. Approval by the URML governance body (currently the sole maintainer; in later phases, the steering committee per [`GOVERNANCE.md`](GOVERNANCE.md)).

**Adding components** to the commitment is encouraged and follows the same process. **Removing components** requires extraordinary justification and is presumed to be a violation of the project's founding intent. A removal RFC must specifically address: (a) why the original commitment was wrong, (b) why no less-drastic alternative suffices, and (c) what existing community trust is being spent.

## Why This File Exists in Phase 0

Phase 0 is the right phase for this commitment because:

- There is no commercial entity yet, so no party can credibly claim to be "constrained" by the commitment.
- There are no users yet, so making the commitment more generous than strictly necessary costs nothing today and buys trust for every future user.
- The author's own future self is the most likely party to want to weaken this document later. Writing it down now binds the author's future self.

This file is referenced by the manifesto's License Direction section, by `CLAUDE.md`'s Strategic Posture section, and by every reference implementation's README. It is the load-bearing wall of URML's openness.
