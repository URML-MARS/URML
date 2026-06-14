---
rfc: 0604
title: Congatudo integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-14
updated: 2026-06-14
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

# RFC-0604: Congatudo integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. **Completes** the service-robotics wave (Move #56).

## Summary

[`congatudo/Congatudo`](https://github.com/congatudo/Congatudo) (Apache-2.0) is a cloud-free local control plane for Cecotec Conga cleaning robots, in the spirit of Valetudo but for a different vendor family. The seam is the same as Valetudo's: a cleaning intent, validated against a per-model capability picture, dispatched over a local API. This RFC asks whether the mapping is useful for the Conga family.

## The mapping (URML beside Congatudo)

- **A validated cleaning intent over the local control plane.** URML would map a clean-zone / go-to-room / spot-clean intent onto Congatudo's local control, validated against a per-model capability manifest (suction modes, zones, mop) before dispatch. URML adds the typed pre-dispatch check and a natural-language front door; Congatudo stays the Conga control plane.
- **One intent layer, several vendor control planes.** Congatudo, alongside the Valetudo ecosystem, is evidence that the same validated-intent layer could sit above more than one cloud-free cleaning-robot control plane. The interesting question is whether a single capability-manifest shape spans the vendor families cleanly.

## What is asked

1. Is a typed, validated cleaning-intent layer (an intent checked against a per-model capability manifest, then dispatched over Congatudo's local control) useful for the Conga family?
2. Does Congatudo's per-model capability picture map cleanly onto a URML capability manifest, and would it share a shape with the Valetudo side?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the Layer-4 natural-language grammar, and the substrate-neutral dispatch model. Completes Move #56; the second cloud-free cleaning-robot control plane of the wave (with Valetudo RFC-0600).

## Implementation note

Outreach only. The post is a GitHub Issue on `congatudo/Congatudo` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (Apache-2.0). Tracked in `examples/lighthouses/outreach-move56.yaml`.
