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

# URML RFCs

This directory is URML's decision history. Every change to the **specification** — adding or modifying a primitive, changing a schema, modifying behavior semantics, changing a profile, modifying the Core Commitment — happens here, not in a pull request.

The authoritative description of *how* RFCs work is [RFC-0001](0001-rfc-process.md). This file is just the index.

## Index

| # | Title | State | Last updated |
|---|---|---|---|
| [0000](0000-template.md) | RFC template | Template (not an RFC) | — |
| [0001](0001-rfc-process.md) | RFC process | Accepted | Phase 0 |
| [0002](0002-initial-primitive-vocabulary.md) | Initial Layer-2 primitive vocabulary | Implemented | 2026-05-17 |
| [0003](0003-us-alignment.md) | Strategic realignment — URML aligns with US federal robotics regulation | Accepted | 2026-05-13 |
| [0004](0004-compliance-policy.md) | Compliance policy enforcement | Accepted | 2026-05-13 |
| [0005](0005-hbom-parsing.md) | Structured HBOM parsing for Pass 5 | Draft | 2026-05-13 |
| [0006](0006-connectivity-and-link-loss.md) | Connectivity as an abstract capability and link-loss as a validated safety contract | Implemented | 2026-05-16 |
| [0007](0007-manufacturer-go-to-market.md) | Manufacturer go-to-market: URML as an opportunity and a channel for robot OEMs and component makers | Implemented | 2026-05-16 |
| [0008](0008-community-discussions.md) | Community Discussions: a public Q&A and feedback channel brought forward into Phase 0 | Implemented | 2026-05-16 |
| [0013](0013-industrial-layer2-primitives.md) | Industrial-profile Layer-2 primitives — pick_from, place_at, swap_tool | Implemented | 2026-05-19 |

## Lifecycle states

Per RFC-0001:

- **Draft** — Author working on it. Not yet open for review.
- **Open** — Open for review; the comment window is active.
- **Accepted** — Approved by the governance body (Phase 0: sole maintainer; Phase 1+: steering committee). Authoritative; implementation may begin.
- **Implemented** — The RFC's normative changes have landed in the spec and at least the reference implementations required for conformance.
- **Rejected** — Considered and not adopted. Stays in the directory as historical record; the RFC body documents the reasoning.
- **Superseded** — Replaced by a later RFC. Header links to the successor.
- **Withdrawn** — Author withdrew before the decision. Stays as historical record.

State changes are recorded in the RFC's own header, not here; this table reflects the current state at index update.

## How to file an RFC

1. Copy [`0000-template.md`](0000-template.md) to `NNNN-short-kebab-name.md`, where `NNNN` is the next unused number (zero-padded to four digits).
2. Fill in the template. The required sections are non-negotiable; saying "N/A" in one is fine if it's truly N/A and you explain why.
3. Open a PR titled `RFC-NNNN: <short title>`. The PR is the comment window.
4. The maintainer (Phase 0) or a steering-committee reviewer (Phase 1+) advances the state header.

A Phase 0 RFC may be authored, reviewed, and merged by the same person. The author reviews their own work against the self-review checklist in RFC-0001 §Self-review. The discipline matters: future contributors inherit a real decision trail rather than a folkloric one.
