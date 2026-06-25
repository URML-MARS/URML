---
rfc: 0633
title: NaVILA (AnjieCheng/NaVILA) integration — request for comment
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-06-25
updated: 2026-06-25
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

# RFC-0633: NaVILA (AnjieCheng/NaVILA) integration — request for comment

**Kind: Outreach.** No spec change is proposed here. This is a per-target request for comment proposing how URML v0.1 relates to an existing target and asking its maintainers for feedback. Part of the VLA / robot-foundation-model wave (Move #61).

## Summary

[`AnjieCheng/NaVILA`](https://github.com/AnjieCheng/NaVILA) (UC San Diego / NVIDIA, US; RSS 2025) is a vision-language-action model for legged-robot navigation. It splits navigation into a VLA that emits high-level, language-grounded commands and a real-time locomotion policy that executes them. That two-level split is exactly where a validation layer belongs: between the high-level command and the locomotion policy. This is a request for comment.

## The relationship (URML beside NaVILA)

- **A check at the seam.** A robot declares a capability manifest and a safety envelope, and URML validates each high-level command against it before the locomotion policy runs. For a legged platform that means checking a command is within the declared mobility (drive type, traversable slope, obstacle height) and the whole-body stability limits URML models (RFC-0384) before it becomes motion.
- **Catch the impossible early.** The check flags a command the platform cannot physically execute before the locomotion policy is asked to try it.

## What is asked

1. Between NaVILA's high-level VLA command and the low-level locomotion policy, is a declared-capability check a useful seam?
2. Would a worked example mapping NaVILA's command interface onto a URML manifest (validated, no execution) be of interest?

Nothing here asks the project to adopt, host, or maintain anything.

## Prior art / context

URML's capability manifest (Layer 1), the safety envelope, the validate-before-actuate gate, and the whole-body kinematic-structure + stability-limits block (RFC-0384), which is the legged-platform fit. Part of Move #61; US-origin legged-navigation target.

## Implementation note

Outreach only. The post is a GitHub Issue on `AnjieCheng/NaVILA` under the maintainer's identity, with the AI-assisted-authoring disclosure (VIBE.md) up front. Tracked in `examples/lighthouses/outreach-move61.yaml`.
