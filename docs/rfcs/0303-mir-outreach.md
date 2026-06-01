---
rfc: 0303
title: Mobile Industrial Robots (MiR) integration, research-collab proposal (off-GitHub, via the interop layer)
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-01
updated: 2026-06-01
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

# RFC-0303: Mobile Industrial Robots (MiR) integration, research-collab proposal (off-GitHub, via the interop layer)

No spec change is proposed here. This is an Outreach RFC: it proposes a future mapping from URML v0.1 to an existing target, not a change to URML's normative surface. Closes the Move #21 warehouse / intralogistics AMR wave.

## Summary

URML proposes courtesy alignment with Mobile Industrial Robots (MiR, an AMR market leader, Denmark-domiciled, Teradyne-owned). The ask is research-collab + a surface question. **Engagement surface is off-GitHub** (no public developer GitHub org for substantive integration; MiR exposes a product REST/fleet interface to customers, not an open developer community). The likely technical bridge is the **AMR interop layer** ([RFC-0297 VDA5050](0297-vda5050-outreach.md), [RFC-0298 InOrbit / MassRobotics standard](0298-inorbit-ros-amr-interop-outreach.md)). MiR products are documented VDA5050 participants.

## Motivation

MiR (Odense, Denmark; allied, default-policy pass; owned by Teradyne) builds one of the most widely deployed AMR lines (MiR100 through MiR1350) with a MiR Fleet manager. The line's transport/move semantics map cleanly onto URML's warehouse primitives under the warehouse profile ([RFC-0022](0022-warehouse-domain-profile.md)). MiR's documented VDA5050 support makes the interop layer ([RFC-0297](0297-vda5050-outreach.md)) the natural bridge: URML intent → VDA5050 orders → MiR fleet. URML adds natural-language authoring and cross-robot static validation.

Verified surface (2026-06-01):
- Company: mobile-industrial-robots.com (HQ Odense, DK; Teradyne). MiR Fleet + a product REST interface for customers.
- **No open developer GitHub org for community integration located.** Engagement is off-GitHub.
- Interop link: MiR products support VDA5050.

## Detailed design (light, research-collab + off-GitHub)

1. **Courtesy outreach via the MiR company / developer contact surface**, asking whether the VDA5050 interface (or the product REST API) is the recommended path for a substrate-neutral intent layer.
2. **If a surface is confirmed**, URML targets the **interop layer** (VDA5050 via [RFC-0297](0297-vda5050-outreach.md)) rather than a MiR-private adapter: validate ([RFC-0286](0286-multi-robot-fleet-addressing.md) + [RFC-0291](0291-utm-strategic-deconfliction.md)) and emit VDA5050 orders a MiR fleet understands, with no new URML vocabulary.

## Backward compatibility

Pre-v1.0. Purely additive if ever implemented. Zero URML code in this RFC.

## Drawbacks

- **No open developer community surface.** MiR's interfaces are customer/product-facing, not an open developer org; this is a courtesy + question.
- **Allied, not US-domiciled.** MiR is Danish (Teradyne-owned); allied and default-policy pass, like Husqvarna ([RFC-0101](0101-husqvarna-automower-outreach.md)) and MiR's intralogistics peers. Named for provenance accuracy.
- **Light engagement payload.** Depth depends on MiR's response; VDA5050 ([RFC-0297](0297-vda5050-outreach.md)) is the realistic path.

## Alternatives considered

1. **Target the MiR product REST API directly.** Possible, but the VDA5050 path is vendor-neutral and reusable across the whole wave; the RFC asks MiR which it recommends.
2. **Skip MiR.** Rejected; MiR is a global AMR leader and adds the allied-EU data point to a US-heavy vendor set (Locus/Vecna/Seegrid).
3. **Fold into the VDA5050 RFC.** Rejected; MiR is a distinct vendor engagement over the shared VDA5050 bridge.

## Prior art

- mobile-industrial-robots.com; MiR VDA5050 support.
- [RFC-0297 (VDA5050)](0297-vda5050-outreach.md), [RFC-0298 (InOrbit / MassRobotics standard)](0298-inorbit-ros-amr-interop-outreach.md).
- [RFC-0102 (Bear Robotics)](0102-bear-robotics-servi-outreach.md), [RFC-0294 (Labrador)](0294-labrador-systems-outreach.md): off-GitHub courtesy precedents.
- [RFC-0022](0022-warehouse-domain-profile.md), [RFC-0286](0286-multi-robot-fleet-addressing.md), [RFC-0291](0291-utm-strategic-deconfliction.md), [RFC-0300 (Locus)](0300-locus-robotics-outreach.md), [RFC-0301 (Vecna)](0301-vecna-robotics-outreach.md), [RFC-0302 (Seegrid)](0302-seegrid-outreach.md).

## Unresolved questions

For Mobile Industrial Robots:

1. **Recommended path.** Is VDA5050 the recommended integration interface for a substrate-neutral intent layer, or the product REST API?
2. **Engagement channel.** Is there a developer-relations / partnerships contact, or is the company contact form the right surface?
3. **Fleet boundary.** Where does a third party submit transport intent to a MiR fleet?
4. **Natural-language authoring.** Is URML's intent layer of interest to the MiR product side?
5. **Anything else.**

## Implementation note

RFC-0303 ships as a single RFC document PR. No adapter code in this PR. Closes the Move #21 wave. Ledger entry in [`examples/lighthouses/outreach-move21.yaml`](../../examples/lighthouses/outreach-move21.yaml).

## Requested feedback

Items 1–5 from "Unresolved questions" above.

## How to respond

MiR's contact surface is mobile-industrial-robots.com. URML's planned channel: a courtesy message via the company / developer contact surface pointing at this RFC.

This RFC and any accompanying outreach are AI-assisted under the maintainer's direction and review; URML's authoring posture is documented in [`VIBE.md`](../../VIBE.md).

URML's own public Discussions: https://github.com/URML-MARS/URML/discussions

## Self-review (Phase 0)

- [x] Off-GitHub framing explicit; absence of an open developer community surface acknowledged honestly.
- [x] VDA5050 named as the recommended interop bridge (RFC-0297); MiR's VDA5050 support cited.
- [x] Allied-not-US provenance named honestly (DK / Teradyne).
- [x] Zero-new-vocabulary claim grounded in RFC-0022.
- [x] Cross-link to off-GitHub precedents, interop siblings, fleet machinery, RFC-0300/0301/0302.
- [x] At least one alternative considered (three).
- [x] Drawbacks real (no open community surface, allied provenance, light payload).
- [x] Backward compatibility additive.
- [x] No Layer-2 primitive added.
- [x] Implementation note explicit.
- [x] Surface verified 2026-06-01.
- [x] Provenance `origin: DK`; default policy passes.
- [x] Authoring posture disclosed (VIBE.md).
- [x] CLAUDE.md compliance check passed.
