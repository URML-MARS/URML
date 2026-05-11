---
rfc: 0001
title: RFC Process
author: URML Maintainer
state: Accepted
created: 2026-05-11
updated: 2026-05-11
supersedes: —
superseded-by: —
---

# RFC-0001: RFC Process

## Summary

This is the meta-RFC. It documents how URML's RFC process itself works: where RFCs live, how they're numbered, the lifecycle states they pass through, who can advance the state, and what the author must do before an RFC moves from Draft to Open. The standard pattern (Rust, React, Python PEPs) — adapted to URML's Phase-0 solo-maintainer reality without making future scaling harder.

## Motivation

[`MANIFESTO.md`](../../MANIFESTO.md) says: *"Any change to the specification — adding a primitive, changing a schema, modifying behavior semantics — is an RFC, not a PR."* And: *"Open governance from day one. Even when this project is one person, the RFC process is documented and the decision log is public."*

For that to mean anything, the process has to be written down before the first substantive RFC, not after. RFC-0001 is that writing-down step. It is also the first test of the process: a thing the maintainer wrote, reviewed, and merged against a documented checklist.

## Detailed design

### Where RFCs live

[`docs/rfcs/`](.). One Markdown file per RFC, plus this `README.md` (the index) and `0000-template.md` (the template).

### Numbering

`NNNN-short-kebab-name.md`, where `NNNN` is the next unused integer zero-padded to four digits. RFCs are numbered at the moment they reach state **Open** (not at Draft, so Draft RFCs that never reach Open don't consume numbers). The maintainer assigns the number in the PR that advances the RFC from Draft to Open.

`0000` is reserved for the template. `0001` is this document.

### Required sections

Every RFC must contain, in order: Summary, Motivation, Detailed Design, Backward Compatibility, Drawbacks, Alternatives Considered, Prior Art, Unresolved Questions, Implementation Note. The template enforces this. A section may say "N/A" if it is truly N/A and the RFC explains why; "N/A" is itself a piece of evidence the author thought about it.

### Lifecycle states

State is recorded in the YAML frontmatter at the top of each RFC.

| State | Meaning | Who can set it |
|---|---|---|
| **Draft** | Author working on it; not yet open for review. | The author. |
| **Open** | Open for review. Comment window active. | Maintainer (Phase 0) or steering committee (Phase 1+). |
| **Accepted** | Approved. Implementation may begin. | Maintainer (Phase 0) or steering committee (Phase 1+). |
| **Implemented** | Normative changes landed in spec + required reference implementations. | Maintainer (Phase 0) or steering committee (Phase 1+). |
| **Rejected** | Considered and not adopted. RFC stays in the directory; body documents the reasoning. | Maintainer (Phase 0) or steering committee (Phase 1+). |
| **Superseded** | Replaced by a later RFC; frontmatter `superseded-by` links to the successor. | Maintainer (Phase 0) or steering committee (Phase 1+). |
| **Withdrawn** | Author withdrew before the decision. Stays as historical record. | The author. |

### Comment window

For Phase 0 RFCs, the minimum comment window from Open to Accepted is **seven days**. RFC-0001 itself uses a zero-day comment window because there is nothing yet to comment from. Future RFCs that touch the [Core Commitment](../../CORE_COMMITMENT.md) require a **30-day** window per `CORE_COMMITMENT.md` §Modifying This Document.

### Who decides

| Phase | Decision body |
|---|---|
| **0** | Sole maintainer. The author may review and merge their own RFCs against the self-review checklist below. |
| **1+** | Steering committee (3–5 people). Two-reviewer approval becomes the norm for spec-changing RFCs. |
| **2+** | Working groups have merge authority within their profile. Cross-cutting RFCs escalate to the steering committee. |
| **3+** | The standard moves under a foundation; the foundation's governance document supersedes this section. |

### Conflicts of interest

When the maintainer becomes affiliated with a commercial entity that builds on URML (see [`GOVERNANCE.md`](../../GOVERNANCE.md) §Conflicts of Interest), any RFC that would benefit that entity requires approval from at least one non-conflicted steering-committee member. Until the committee exists, the maintainer discloses the conflict in the RFC body and proceeds; the disclosure is the historical record.

### Self-review

In Phase 0, the author reviews their own work. Before advancing an RFC from Draft to Open, the author confirms each item in the self-review checklist embedded in [`0000-template.md`](0000-template.md). The checklist is normative; an Open RFC that fails any item should be moved back to Draft.

The Phase-0 self-review checklist:

- [ ] The **Summary** alone tells a reader what is being proposed.
- [ ] The **Motivation** is grounded in a concrete use case, not hypothetical needs.
- [ ] The **Detailed design** names every affected spec document and reference component.
- [ ] At least one **alternative** is genuinely considered (not a strawman).
- [ ] **Drawbacks** lists at least one real downside.
- [ ] **Backward compatibility** is honest about what breaks.
- [ ] If the RFC adds a Layer-2 primitive, both ROS-2 and non-ROS implementation sketches are present (substrate-neutrality acid test).
- [ ] The **implementation note** explains how this lands, not just what.
- [ ] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do and confirmed the proposal does not violate it.

### Index maintenance

The index in [`README.md`](README.md) is updated in the same PR that advances an RFC's state. If you change the state in the frontmatter, you also bump the index — the inconsistency is a bug.

### Relationship to pull requests

RFCs and PRs do different things:

- An **RFC** decides *whether* and *how* a specification changes.
- A **PR** implements an accepted RFC, or handles routine maintenance (tests, docs, dependency bumps, refactors with no behavior change).

If you cannot tell whether your change needs an RFC, open an issue and ask. The maintainer would rather route a borderline case than discover an unflagged spec change in a merged PR.

## Backward compatibility

This RFC introduces the process. There is nothing prior to break.

## Drawbacks

- **Discipline tax for a one-person project.** Writing RFC frontmatter, alternatives sections, and self-review checklists for trivial spec changes feels like overhead when the reviewer and author are the same person. Counter: the discipline becomes load-bearing the moment a second contributor arrives, and the cost of retrofitting it then is higher than the cost of writing it now.
- **Risk of paper-pushing.** A documented process can become a way to slow real work. Counter: the process is intentionally lightweight (one Markdown file, nine sections, one short checklist). If it ossifies, the right response is to amend RFC-0001, not to skip it.
- **Numbering at Open, not Draft, means RFC numbers are slightly less stable** (a Draft can be referenced before it has its final number). Counter: the alternative — numbering at Draft — means abandoned Drafts permanently consume integers, which is worse for the index.

## Alternatives considered

1. **No RFC process during Phase 0.** Just open PRs; document decisions in commit messages. Rejected: the manifesto explicitly commits to open governance from day one, and commit-message history is hard to read as a decision trail at the granularity of "why did we choose this primitive over that one."
2. **GitHub Discussions for decisions; a `decisions/` directory of one-pagers afterward.** Lighter weight, but the format invites under-specification (it is easy to merge a one-pager without an "Alternatives considered" section). Rejected because the discipline of the required sections is exactly what we want.
3. **A formal spec like IETF RFCs or Python PEPs.** Heavier than URML needs at Phase 0. The chosen process is closer to Rust RFCs in spirit and ceremony.

## Prior art

- **Rust RFCs** (`rust-lang/rfcs`) — the format URML draws most heavily from.
- **React RFCs** (`reactjs/rfcs`) — lighter weight; closer to Phase-0 reality.
- **Python PEPs** — heavier; useful reference for what URML *won't* do (PEP-style normative-language conventions, multi-state workflows beyond what URML needs).
- **IETF RFCs** — the historical anchor; URML deliberately diverges by being more informal.

## Unresolved questions

- **How is RFC numbering coordinated if Phase 1 brings a small steering committee that opens multiple Open RFCs in parallel?** Likely: the maintainer or a designated index-keeper is the single source of truth for "the next number" during the merge of any RFC into Open.
- **Do Implemented RFCs ever get edited?** Lean: no — once Implemented, the RFC is frozen. Subsequent changes happen via a new RFC that supersedes the old one. Confirm with first real Implemented RFC.

## Implementation note

This RFC is Accepted on merge of the PR that creates it (in the same PR that lands the Phase-0 scaffold). The template (`0000-template.md`) and the index (`README.md`) ship at the same time. Future RFCs are filed against this process.

The first substantive RFC after this one is expected to be **RFC-0002: Initial Layer-2 Primitive Vocabulary** (the `move_to`, `grasp`, `hover`, `detect`, ... set named in the Manifesto).
