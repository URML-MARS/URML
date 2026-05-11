# URML Governance

**Status as of Phase 0:** One person.

The maintainer is the founder and sole contributor. This file describes the current state honestly and the phased plan for scaling governance as the project grows. The manifesto says of this file: *"It will say 'one person' until that becomes false."* That commitment is in force.

---

## How Decisions Are Made Today

Phase 0 governance is one person plus a documented RFC process. Every change to the specification — adding a primitive, changing a schema, modifying behavior semantics, changing the Core Commitment — is a numbered RFC in [`docs/rfcs/`](docs/rfcs/). See [`docs/rfcs/0001-rfc-process.md`](docs/rfcs/0001-rfc-process.md) for the authoritative process.

Even with one reviewer, the discipline matters. The author reviews their own work against a documented self-review checklist (in the RFC process document). Future contributors will inherit a real decision history rather than a folkloric one.

PRs (as opposed to RFCs) handle *implementation* of accepted RFCs and routine maintenance: tests, documentation, bug fixes, dependency bumps. Anything that changes specification semantics is an RFC.

## Precedence Order

When in doubt about a decision in this repository, authority flows in this order (mirrors [`CLAUDE.md`](CLAUDE.md)):

1. [`MANIFESTO.md`](MANIFESTO.md) — the constitution
2. [`CORE_COMMITMENT.md`](CORE_COMMITMENT.md) — the licensing floor
3. Layer specifications (versioned, in [`spec/`](spec/))
4. Accepted RFCs (in [`docs/rfcs/`](docs/rfcs/))
5. [`CLAUDE.md`](CLAUDE.md) — working conventions
6. The founder's stated preference in chat
7. The contributor's or maintainer's judgment

## Phased Governance Plan

The plan from the manifesto:

| Phase | Governance shape |
|---|---|
| **0** (now) | One maintainer. RFC process documented and followed. Self-review against checklist. |
| **1+** | Small steering committee of 3–5 trusted reviewers. Two-reviewer approval becomes the norm for spec-changing RFCs. |
| **2+** | Working groups per domain profile (home, drone, industrial, ...). A working group has merge authority within its profile, escalating cross-cutting changes to the steering committee. |
| **3+** | Formal foundation membership (Linux Foundation, Open Source Robotics Alliance, or equivalent). Trademark and conformance program transferred to the foundation. The standard outlives its founders. |

Transitions between phases are themselves RFCs.

## Contributor License Posture

URML uses **DCO sign-off**, not a Contributor License Agreement. Every commit must include a `Signed-off-by:` line; the workflow is in [`CONTRIBUTING.md`](CONTRIBUTING.md). The DCO posture is a deliberate strategic choice — see the rationale in [`CLAUDE.md`](CLAUDE.md) §What Claude Should Never Do (last bullet).

## Conflicts of Interest

The founder anticipates eventually being affiliated with a commercial entity that builds on URML. To preempt the obvious conflict:

- No proprietary feature is merged into this repository. The Core Commitment defines what stays open; everything else lives elsewhere.
- The maintainer's commercial activities are disclosed in this file as soon as they exist.
- Once a steering committee exists, conflicted RFCs (those that would benefit a maintainer's commercial entity) require approval from at least one non-conflicted committee member.

## How to Reach the Maintainer

During Phase 0, see [`CONTRIBUTING.md`](CONTRIBUTING.md) for current contact and engagement channels.

## Changing This File

This file is updated as the governance state changes. Each change is a small RFC, even when it is recording a fact (e.g., "the steering committee now exists, with the following members"), so the history of how URML was governed remains auditable.
