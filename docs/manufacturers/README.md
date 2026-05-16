# URML for Robot Manufacturers and Component Makers

This page is for two audiences, in order: companies that build whole robots, and companies that build the parts inside them. It explains what URML gives you, how to integrate it, and how to list a product so buyers can find it.

URML is an open specification, Apache 2.0. There is no fee here, no contract, and nothing to sign. The paid `URML-Certified` program is a separate Phase-4 surface that does not exist yet; nothing on this page is a certification, an audit, or an endorsement. See [TRADEMARK.md](../../TRADEMARK.md).

## Why this is worth your time

Two concrete reasons, not abstractions.

**You get the intent layer for free.** URML is the natural-language and validated-intent layer your customers increasingly expect. Building one in-house is a cost center outside your core competency. URML is a specification plus working reference implementations you can adopt instead of building. Your engineering stays focused on the robot.

**You can show federal-procurement readiness.** Since RFC-0003 and RFC-0004, URML ships a bundled US-federal compliance policy (NDAA Section 889 / FY26, FCC Covered List, EO 14307, the American Security Robotics Act once enacted). Running the open validator against your product's capability manifest produces a factual, reproducible result. You can publish that result as a self-report. It is not a certification and you must not describe it as one (see [the self-report template](FEDERAL-VALIDATION-SELF-REPORT.md) for exactly what you may and may not say), but it is a concrete artifact a procurement reviewer can re-run, because the policy is free and public.

## Integration path

URML already ships the pieces. This is the order, not a new toolkit. Do not expect new tooling here; each step points at something that exists.

1. **Get it running.** Clone the repo and run `python bootstrap.py` then `make demo`. This validates the canonical example end to end. See [Tutorial 1: Getting started](../tutorials/01-getting-started.md).
2. **Scaffold for your robot.** `urml init my-robot --profile {home|drone|industrial}` generates a starting project for the closest profile.
3. **Write your capability manifest.** Follow [Tutorial 4: Writing your own manifest](../tutorials/04-writing-your-own-manifest.md). Work through its provenance exercise: that is where you declare per-component country of origin, vendor, and role, which is what the federal default policy checks.
4. **Start from a real manifest.** The per-profile examples under [`examples/`](../../examples/) are working manifests to copy from. `examples/home/red-mug.manifest.yaml` is a fully US-compliant reference.
5. **Produce a federal-readiness self-report** if you want the procurement wedge. Follow [FEDERAL-VALIDATION-SELF-REPORT.md](FEDERAL-VALIDATION-SELF-REPORT.md).
6. **List your product** so buyers can find it. Follow [SUBMISSION.md](SUBMISSION.md).

There is no OEM-specific per-profile starter manifest yet, distinct from the demo manifests. If manufacturer demand makes that worthwhile it will be a separate documentation change, not a promise made here.

## For component makers

If you make actuators, sensors, compute modules, or other parts rather than whole robots, URML sits above your layer and you do not implement it. What you can do is make your part easy for an OEM to declare cleanly.

A URML capability manifest carries a `provenance:` block: a list of components, each with an `id`, a `role` (critical, non-critical, or informational), a `vendor`, a `country_of_origin`, an optional `country_of_final_assembly`, and an optional hardware bill-of-materials reference (`hbom_ref`). The shape is specified in RFC-0004 and shown in [Tutorial 4](../tutorials/04-writing-your-own-manifest.md)'s provenance exercise.

A component you document with those fields, ideally with a CycloneDX 1.7 HBOM your OEM can reference by `hbom_ref`, is a component an OEM can drop into a manifest that validates clean under the open default policy. That is the integration story to put in your own developer documentation. [RFC-0005](../rfcs/0005-hbom-parsing.md) (Draft) is the forward path for structured HBOM parsing. This is integration guidance. URML does not certify components, and a clean-provenance component is not a URML endorsement of your part.

## Launch partners (Phase 0)

In Phase 0, "launch partner" means exactly one thing: an early entry in the [manufacturer directory](directory.md), optionally noted in an early-adopters section of that page. That is the whole offer.

There is no paid program, no mark, no fee, no priority placement, no service-level commitment, and no contact form or lead capture. The full launch-partner and certification program is Phase 4 and lives outside this repository (see [CORE_COMMITMENT.md](../../CORE_COMMITMENT.md) and [TRADEMARK.md](../../TRADEMARK.md)). If a future commercial program offers more, it will say so in its own terms, not here.

## What this is and is not

This is a free, self-reported on-ramp. Listing in the directory is a factual record that you submitted, nothing more. URML does not audit, endorse, sponsor, or assume responsibility for any listed product, and listing does not indicate fitness for production, safety-critical, or regulated deployment. The conformance and validation tooling is Apache 2.0 and runnable by anyone, so any claim here is independently checkable. See [TRADEMARK.md](../../TRADEMARK.md) and the runtime-author equivalent at [docs/compatible-runtimes.md](../compatible-runtimes.md).
