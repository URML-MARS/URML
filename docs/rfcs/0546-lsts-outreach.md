---
rfc: 0546
title: LSTS toolchain (DUNE / Neptus) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-13
updated: 2026-06-13
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

# RFC-0546: LSTS toolchain (DUNE / Neptus) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 maps onto an existing target and asking its maintainers for feedback. Part of the swarm / multi-robot / alternative-framework wave (Move #49). One RFC for the LSTS toolchain, covering both repos, rather than separate posts.

## Summary

The LSTS toolchain (University of Porto) is a mature, non-ROS stack for networked unmanned vehicles: [`LSTS/dune`](https://github.com/LSTS/dune) (the onboard runtime / unified navigation environment) and [`LSTS/neptus`](https://github.com/LSTS/neptus) (the command-and-control infrastructure for a fleet of networked vehicles). URML is interesting in two ways: DUNE is a non-ROS substrate URML could dispatch validated intent to, and Neptus is fleet C2 that URML's roster + deconfliction model speaks to directly. This RFC asks whether either mapping is useful.

## The mapping (URML beside the LSTS toolchain)

- **A non-ROS substrate.** DUNE is an onboard runtime in the same role URML's reference runtimes play: the thing that executes a validated plan on a vehicle. URML validates intent against the vehicle's declared capabilities and a safety envelope, then dispatches to DUNE. URML stays substrate-neutral; DUNE is one substrate.
- **Fleet C2.** Neptus commands and monitors a fleet of networked vehicles. URML's fleet roster (RFC-0286) and cross-vehicle deconfliction (RFC-0291) are the static-validation complement: declare the fleet and its constraints, validate the multi-vehicle intent, then drive it through Neptus.

## What is asked

Request for comment from the LSTS maintainers:

1. Is DUNE a sensible non-ROS substrate for URML-validated intent to dispatch to?
2. Does URML's fleet roster + deconfliction complement Neptus's fleet command-and-control?
3. Which is the cleaner first seam, DUNE (substrate) or Neptus (fleet)?

Nothing here asks the project to adopt, host, or maintain anything. (DUNE and Neptus are under a modified EUPL-1.1 with a non-commercial restriction; this proposes no code reuse, only a mapping / consumer relationship.)

## Prior art / context

URML's substrate-neutral dispatch model, the multi-robot fleet addressing (RFC-0286), cross-robot deconfliction (RFC-0291), and the marine runtime work. Part of Move #49.

## Implementation note

Outreach only. The post is a single GitHub Issue on `LSTS/dune` (referencing Neptus) under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the license is a modified EUPL-1.1; state it, do not ask). Tracked in `examples/lighthouses/outreach-move49.yaml`.
