---
rfc: 0442
title: da Vinci Research Kit (dVRK) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-07
updated: 2026-06-07
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

# RFC-0442: da Vinci Research Kit (dVRK) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. It builds on URML's ROS 2 runtime, its manipulation primitive family, and the bimanual work (RFC-0010). **Scope: research only. The dVRK is explicitly not for clinical use, and URML makes no clinical claim.**

## Summary

[`jhu-dvrk/sawIntuitiveResearchKit`](https://github.com/jhu-dvrk/sawIntuitiveResearchKit) (JHU custom academic license, ~158 stars, active, Discussions on) is the cisst/SAW control stack for the da Vinci Research Kit — the de-facto open research platform for surgical-robotics labs worldwide, built on JHU's [`cisst`](https://github.com/jhu-cisst/cisst) toolkit and the CRTK interface. A dual-arm research surgical robot with a mature open control stack is a strong fit for URML's validated, bimanual manipulation intent. This RFC asks whether a research intent layer above it is interesting.

## The mapping (URML above the dVRK)

URML sits above the research robot as a validated intent layer:

- URML's ROS 2 runtime meets the dVRK on its CRTK / ROS surface; a research subtask lowers onto the PSM/ECM arms as typed primitives, and URML's `arm` selector + `bimanual` primitive (RFC-0010) address the dVRK's two patient-side manipulators.
- Validate-before-actuate refuses an out-of-workspace pose or an undeclared instrument before motion — a research safety boundary aligned with the dVRK's "not for clinical use" norm.
- The dVRK manifest (arms, instruments, reach/DOF, workspace) is a thorough test of URML's bimanual capability model.

## What is asked

Request for comment from the dVRK maintainers:

1. Is URML's CRTK / ROS surface mapping the right seam for a research validated-intent layer above the dVRK?
2. What should a URML capability manifest declare to describe the dVRK honestly (PSM/ECM arms, instrument set, reach/DOF, workspace bounds)?
3. Does URML's `arm` selector + `bimanual` primitive map cleanly onto the dVRK's two patient-side manipulators?

Nothing here asks the project to adopt, host, or maintain anything, and nothing here is a clinical proposal.

## Prior art / context

URML's ROS 2 runtime; the manipulation family (Move #27) and the bimanual work (RFC-0010); the surgical-research anchor (RFC-0440). The dVRK is the canonical research-surgical-platform vertex of the medical / surgical research wave.

## Implementation note

Outreach only. The post is a GitHub Discussion on `jhu-dvrk/sawIntuitiveResearchKit` under the maintainer's identity, AI-assisted-authoring disclosure (VIBE.md) up front, no license-ask (JHU custom academic license). The `cisst` toolkit and `crtk_python_client` are referenced, not posted to separately (cluster-anchor; `dvrk-ros` is archived). Research framing only. Tracked in `examples/lighthouses/outreach-move37.yaml`.
