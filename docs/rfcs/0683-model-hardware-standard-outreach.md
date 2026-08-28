---
rfc: 0683
title: Model Hardware Standard (Anthropic) — URML as the validation layer above MHS devices
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-08-28
updated: 2026-08-28
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

# RFC-0683: URML as the validation layer above MHS devices

No spec change is proposed here. This is an outreach RFC: it records how URML proposes to sit above Anthropic's Model Hardware Standard, what URML will build once the standard is open, and what it asks of nobody.

## Summary

Anthropic's [Model Hardware Standard](https://www.anthropic.com/news/model-hardware-standard-research-preview) (research preview, 2026-08-27) standardizes the driver layer for AI-operated equipment: read/write primitives, network discovery, and a device reference file declaring what a device measures, what can be adjusted, and what safety limits it enforces. Anthropic will open-source it after "safety evaluations and best practices for AI systems that operate physical equipment".

URML proposes two things, both Apache 2.0, both on URML's side:

1. **Read an MHS reference file as a capability-manifest source**, the way [`examples/urdf-to-manifest/`](../../examples/urdf-to-manifest/) reads a URDF: device limits become `mobility`/`manipulation`/`perception` fields tagged `evidence: derived`. The deployment envelope stays a separate artifact; the validator conjoins the two, strictest wins.
2. **Dispatch validated URML programs through MHS read/write**: an `MhsAdapter` in the RFC-0014 shape, lowering Layer-2 primitives onto the driver primitives, making every MHS device a URML substrate through one adapter. A labeled scaffold with an injectable transport ships in [`examples/physical-ai-safety-eval/`](../../examples/physical-ai-safety-eval/); the wire format waits for the specification.

Alongside, URML contributes the thing Anthropic named as the gate: a hermetic **safety-evaluation harness** that judges agent intents against an MHS-shaped lab-cell manifest and a deployment envelope, reporting refusals with machine-readable reasons, envelope-monitor verdicts over rehearsed traces, and evidence classes.

## Motivation

URML's identity is validate-before-actuate: an intent language whose programs are statically checked against a capability manifest and safety envelope before anything moves. MHS solves the layer below: how an agent finds a device, what the device can do, and what it refuses per call. Neither replaces the other. A per-call limit at the device catches the fifth action of a bad plan; a whole-program check refuses the plan. And a device's own limits are not a deployment's limits: a lab caps an arm below the vendor's maximum, and only a separate envelope can say so.

The Manifesto already fixes the posture (Layer 1 "extends existing standards (URDF, SDF); we do not reinvent robot description"). MHS is the third such standard, with the difference that it will ship with vendor distribution URML cannot match. Competing with it for vendor attention at device description would be a losing move; sitting above it is the design.

## What ships now

- [`docs/integrations/model-hardware-standard.md`](../integrations/model-hardware-standard.md): the layering and a mapping table from the announced reference-file concepts onto manifest and envelope fields.
- [`examples/physical-ai-safety-eval/`](../../examples/physical-ai-safety-eval/): the harness, byte-asserted, with the `MhsAdapter` scaffold.
- The `docs/integrations/urml-for-ai-agents.md` pattern for agents that hold MHS device tools over MCP: programs go through `urml_validate` first; URML's MCP server has no path to an actuator that skips the validator.

## What waits for the open specification

- `mhs-to-manifest` importer (field-level mapping).
- `urml-mhs-runtime` (RFC-0014 conformance), promoted from the scaffold.
- Conformance fixtures for MHS-driven devices, first for Universal Robots and Doosan (URML adapters exist; MHS becomes a second transport).
- Evidence: reference-file-derived limits tagged `derived` with a `ref: {kind: url}` pointer.

## The ask

Of Anthropic: research-preview access, so the importer and adapter are built against the real specification rather than the announcement. Of the preview partners: nothing. Of the MHS specification: nothing; this RFC proposes no change to it.

## Alternatives considered

- **Treat MHS as a competitor and differentiate the manifest.** Rejected. The manifest is not URML's moat; the validator, the envelope split, the conformance suite, and the intent language are.
- **Wait for the open release before saying anything.** Rejected. Anthropic's own gate is safety evaluation, which is URML's shipped competence; the harness is buildable now without touching an unpublished schema.
- **Build an adapter against a guessed wire format.** Rejected. The scaffold's transport is injectable and labeled as pending; nothing claims compatibility.

## Prior art

- URML's URDF-as-manifest precedent (`examples/urdf-to-manifest/`, RFC-0455/0457/0460 threads) and the RFC-0039 stance: the manifest declares what the hardware can do; the driver selects what a deployment does.
- The OPC UA runtime (`reference/opcua-runtime/`), whose intent-to-node lowering is the closest existing analogue of intent-to-read/write.
- The RoboCasa engagement ([[project_robocasa_eval_lens]]): URML as an evaluation lens that flags out-of-distribution instructions.

## Outreach record

- 2026-08-28: research-preview application drafted (`examples/lighthouses/posts-adoption-campaign.md` section 4.1); the founder submits it via the web form. Ledger row `mhs` in `examples/lighthouses/outreach-move71.yaml` stays `sent_at: ""` until then.
