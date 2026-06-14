---
rfc: 0593
title: Pycro-Manager integration — request for comment
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

# RFC-0593: Pycro-Manager integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the lab-automation wave (Move #54).

## Summary

[`micro-manager/pycro-manager`](https://github.com/micro-manager/pycro-manager) (BSD-3-Clause, UCSF / UW) is the Python layer over Micro-Manager for automating microscopes: scripted, reproducible acquisitions across stages, cameras, and illumination. A microscope is an instrument with a well-defined set of capabilities and limits, which is exactly the kind of thing a capability manifest describes. This RFC asks whether a validated-instruction layer is useful for acquisition automation.

## The relationship (URML beside Pycro-Manager)

- **A validated instruction, then an acquisition.** An acquisition is a declared intent: image this region, at these channels, within these stage and exposure limits. URML could express that as a typed instruction, validated against the scope's declared capabilities and limits, then dispatched through Pycro-Manager. Pycro-Manager stays the microscope interface; URML adds the typed pre-dispatch check and an optional natural-language path.
- **Scope configuration toward a manifest.** The microscope's available channels, stage travel, and objectives form a capability set an instruction can be checked against before it runs.

## What is asked

1. Is a typed, validated instruction layer (an acquisition checked against the scope's declared capabilities before dispatch) useful above Pycro-Manager?
2. Does a microscope's configuration (channels, stage limits, objectives) map onto a URML-style capability manifest?
3. Which boundary is worth exploring first?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest, the Layer-4 natural-language grammar, and the five-pass validator. Part of Move #54; the microscope-automation instrument of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `micro-manager/pycro-manager` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (BSD-3-Clause). Tracked in `examples/lighthouses/outreach-move54.yaml`.
