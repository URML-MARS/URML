---
rfc: 0672
title: "The open/commercial boundary: what stays Apache 2.0 and where commercial work happens"
author: Ido Yahalomi (greenvh@gmail.com)
state: Accepted
created: 2026-08-09
updated: 2026-08-09
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

# RFC-0672: The open/commercial boundary: what stays Apache 2.0 and where commercial work happens

## Summary

`CORE_COMMITMENT.md` names the seven components that stay Apache 2.0 in perpetuity, and lists, in its "What This Commitment Does Not Cover" section, where commercial work may legitimately happen. That boundary is written as a commitment, addressed to the project's own future self. It is not written for the person deciding whether to build on URML, who asks a plainer question: will the parts I depend on ever move behind a paywall, and how does this project intend to make money?

This RFC ratifies a short adopter-facing document, `COMMERCIAL.md`, that restates the existing boundary in plain language, plus one README doc-index cross-link. It is documentary. It proposes no spec, schema, validator, runtime, or conformance change, and it does not modify `CORE_COMMITMENT.md`, which controls.

## Motivation

The open-source community reads any move toward closing a formerly-open core as a betrayal. The re-licensing controversies of the last decade (Elastic, MongoDB, HashiCorp, Redis) are the reference cases, and `CORE_COMMITMENT.md` was written in Phase 0 precisely to draw URML's line before adoption rather than after.

That commitment does its job for the audience it addresses: the project itself. It does less for the audience that matters most for adoption, the roboticist or vendor evaluating whether to depend on URML. That reader wants two things stated plainly and in one place: what will never move behind a paywall, and where the project intends to earn revenue instead. The answer already exists, spread across `CORE_COMMITMENT.md` and the strategic posture in `CLAUDE.md`, but not in an adopter-facing form.

A written open/commercial line is a cheap and durable moat-strengthener. It removes the enclosure fear that makes builders hesitate, and it does so without conceding anything: the commercial surround has always been the plan, and it has always been kept off the open core. Saying so plainly is lower-risk than staying silent and letting adopters guess.

The private strategy that prompted this (how URML earns revenue around the core) stays off the repository, consistent with `CLAUDE.md` keeping commercial surfaces separate. What belongs in the open repository is only the boundary statement, not a business plan.

## Detailed design

This RFC follows the RFC-0007 pattern: it ratifies a documentation addition and designs no mechanism.

### Spec changes

None. No Layer-1/2/3/4 specification, schema, grammar, or profile changes.

### Validator changes

None.

### Reference runtime and conformance changes

None.

### What this authorizes

The addition of `COMMERCIAL.md` at the repository root, styled like `TRADEMARK.md` (the shared masthead, and a `Status` / `Established` / `Authority` header stating that it does not modify `CORE_COMMITMENT.md`, which controls). Its content is:

- the seven free-forever components, restated from the Commitment;
- the sanctioned commercial surfaces (URML-Certified conformance program and trademark, audited policy files, managed and hosted services, premium tooling, training and individual certification), restated from the Commitment's "does not cover" section and `CLAUDE.md` Strategic Posture;
- one plain-language statement of the line: the open core is the standard, the commercial surround is separate and optional, and depending on URML never requires buying anything.

Plus one row in the README doc-index table pointing to `COMMERCIAL.md`.

The document adds no new commitment and grants no new right. Every free item is already committed in `CORE_COMMITMENT.md`; every commercial surface is already carved out there. `COMMERCIAL.md` is a restatement for a different audience, not a new policy.

## Backward compatibility

Documentary. No schema, CLI, or artifact changes. Nothing depends on the new file.

## Drawbacks

A second document that restates the boundary can drift from `CORE_COMMITMENT.md` if edited carelessly. Mitigation: `COMMERCIAL.md` names `CORE_COMMITMENT.md` as controlling and points at it as the binding source, so any conflict resolves to the Commitment.

Publishing a commercial-posture statement invites the "so you are going commercial after all" reading. Mitigation: the document's content is reassurance about what never moves, and the honest frame is that commercial work has always been the plan and has always been kept off the open core. A plain statement is less risky than silence.

## Alternatives considered

Leave `COMMERCIAL.md` as a standalone document without an RFC. Rejected: routing it through the RFC decision-history is consistent with treating public-posture statements as ratified decisions rather than loose docs (the RFC-0007 precedent), and it is what the maintainer chose.

Fold the content into `CORE_COMMITMENT.md`. Rejected: the Commitment is intentionally hard to modify (a 30-day draft period and an extraordinary-justification bar for removals). An adopter FAQ should be freely improvable prose; keeping it separate keeps the binding document stable.

Do nothing. Rejected: the enclosure fear is real, and a written line is a cheap, durable way to answer it before it becomes an objection.

## Prior art

RFC-0003 (US alignment) and RFC-0007 (manufacturer go-to-market) are strategic and documentary RFCs that ratify posture and documentation without touching the normative surface. This RFC is in that mold and reuses RFC-0007's "ratifies a doc, designs no mechanism" structure.

`CORE_COMMITMENT.md` is the binding commitment; `TRADEMARK.md` is the marks policy. `COMMERCIAL.md` sits alongside both.

Distinct from RFC-0262 (`licensing.boundary`) and RFC-0268 (`deployment.commercial_use`): those add normative manifest fields declaring the license constraints of third-party substrate components a deployment uses (GPL-3.0, AGPL-3.0, CC-BY-NC weights). This RFC is about URML's own open/commercial boundary as a project, not about a manifest field. There is no overlap.

## Unresolved questions

Whether the Phase-4 public-launch RFC restates this boundary again with the certification program's concrete terms. Deferred; out of scope here.

## Implementation note

`COMMERCIAL.md` and the README cross-link ship in the same PR as this RFC. No code and no tests beyond the repository's existing markdown-link and writing-style checks. Merge is handed to the maintainer, per the Spec-RFC hand-over convention.

## Self-review (Phase 0)

- Does it touch the normative surface? No.
- Does it modify or weaken `CORE_COMMITMENT.md`? No. It restates the Commitment and defers to it as controlling.
- Could it be read as a step toward enclosure? Only if misread. The content is the opposite: a written guarantee against enclosure.
- Is it provider-neutral and substrate-neutral? Yes. It makes no vendor or substrate commitment.
- DCO sign-off, no em-dashes, smart-non-expert prose. Yes.
