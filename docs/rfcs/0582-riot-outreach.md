---
rfc: 0582
title: RIOT OS integration — request for comment
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

# RFC-0582: RIOT OS integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the motor-control / RTOS substrate wave (Move #53). Cross-citation only (RIOT is LGPL-2.1), and the same altitude caveat applies.

## Summary

[`RIOT-OS/RIOT`](https://github.com/RIOT-OS/RIOT) (LGPL-2.1) is an operating system for the Internet of Things, strong on low-power networked nodes. URML is interesting here at the point where a networked node is also a small actuator in a larger system: the node executes a pre-validated intent, and a fleet of such nodes is addressable by URML's roster.

## The relationship (URML beside RIOT)

- **Networked nodes as fleet members.** A RIOT node that drives a small actuator can host a minimal URML executor (RFC-0018 minimal_node) and run pre-validated intents. Across many nodes, URML's multi-robot roster and cross-node constraints (RFC-0286 / RFC-0291) give a way to declare and validate intent for the whole networked set, not just one node.
- **No upward dependency, no shared code.** URML targets RIOT as a substrate; given the LGPL-2.1 license this is cross-citation only.

## What is asked

1. For a RIOT node acting as a networked actuator, is a small pre-validated intent executor a sensible component?
2. Does URML's fleet roster map onto how RIOT deployments think about a set of networked nodes?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's minimal_node MCU execution shape (RFC-0018), the multi-robot roster (RFC-0286), and cross-node deconfliction (RFC-0291). Part of Move #53; the IoT-RTOS target of the wave.

## Implementation note

Outreach only. The post is a GitHub Issue on `RIOT-OS/RIOT` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front and no license-ask (the LICENSE is LGPL-2.1; state it, do not ask, no code reuse). Tracked in `examples/lighthouses/outreach-move53.yaml`.
