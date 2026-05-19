---
rfc: 0008
title: "Community Discussions: a Public Q&A and Feedback Channel Brought Forward into Phase 0"
author: Ido Yahalomi (greenvh@gmail.com)
state: Implemented
created: 2026-05-16
updated: 2026-05-16
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

# RFC-0008: Community Discussions: a Public Q&A and Feedback Channel Brought Forward into Phase 0

## Summary

URML enables GitHub Discussions now, in Phase 0, with a small set of categories
tailored to its distinct audiences (builders, runtime authors, manufacturers,
the public). This reverses a written deferral in `CONTRIBUTING.md` and
`GOVERNANCE.md` that tied a discussions board to Phase 1 and the permanent
organization. No specification, validator, reference runtime, or conformance
artifact changes. The change is documentary and reversible: it ships category
templates, an issue-to-discussion routing config, and the documentation that
points people at the channel.

## Motivation

The status quo has no async public venue. Issues are scoped to reference-runtime
bugs and the high-bar primitive-proposal funnel. The RFC process is for
specification changes. There is nowhere for a roboticist to ask "how do I write
this manifest", for a runtime author to ask a conformance question, for a
manufacturer to ask about the federal-validation self-report, or for anyone to
register a complaint or a critique of the strategic posture. Today those people
either open a misfiled issue or do not engage at all.

`CONTRIBUTING.md` line 18 and `GOVERNANCE.md` deferred a discussions board until
"the project moves under its permanent GitHub organization" and Phase 1. Two
facts make deferral the wrong call now:

1. Discussions is already enabled on `URML-MARS/URML` (verified: the repository
   reports `hasDiscussionsEnabled: true` with the six GitHub default categories
   and zero discussions). The platform toggle is done; only the tailoring and
   the documentation wiring are missing.
2. The Manifesto's governing principle is "optimize for inevitability, not
   features": adoption is the moat. A GitHub-native Q&A and feedback channel is
   a direct adoption lever, costs little to operate at Phase 0 volume, and is
   fully reversible (Discussions can be disabled and the categories removed
   without touching any normative artifact).

## Detailed design

### Spec changes

None. This is a community-process change and touches no Layer 1 to Layer 4
document or profile.

### Validator changes

None. No check is added or modified.

### Reference runtime changes

None. No runtime behavior is affected.

### Conformance suite changes

None. Conformance is defined against runtime behavior, which is unchanged.

### Category taxonomy

Six categories. GitHub provides no API to create, edit, or delete discussion
categories, so the taxonomy is configured manually in the repository UI by the
maintainer. The net change from the GitHub defaults:

| Action | Category | Format | Purpose |
|---|---|---|---|
| keep | Announcements | Announcement | Maintainer updates |
| keep | Q&A | Q&A (answerable) | How do I build, validate, run, or integrate |
| keep name, enrich description | Ideas | Open-ended | Pre-RFC ideas for primitives, profiles, tooling; graduates to a primitive-proposal issue then an RFC |
| keep | Show and tell | Open-ended | Runtimes, robots, manifests, and demos built on URML |
| add | Builders & Makers | Open-ended | Runtime authors and manufacturers: conformance, the registry, the manufacturer directory, the federal-validation self-report |
| keep name, enrich description | General | Open-ended | Everything else, including complaints and posture critique |
| delete | Polls | — | Not used in Phase 0 |

A category form (`.github/DISCUSSION_TEMPLATE/<slug>.yml`) binds to a category by
the category slug. GitHub derives the slug from the category name. To keep the
form bindings stable, the two enriched categories keep their default names
(`Ideas`, `General`, slugs `ideas` and `general`) and carry the new meaning in
their descriptions rather than in a renamed title. The new category
`Builders & Makers` takes the slug `builders-makers`. Confirmed default slugs:
`announcements`, `general`, `ideas`, `q-a`, `show-and-tell`.

### Category forms

Discussion category forms support only the GitHub issue-forms YAML schema.
Classic Markdown templates, which the repository's issue templates use, are not
an option for discussions; the YAML form is forced by the platform, not chosen.
Three forms are added:

- `.github/DISCUSSION_TEMPLATE/q-a.yml`: prompts for what is being built, the
  profile, the exact command, the error output, and the validator and CLI
  version. Reduces round-trips and keeps usage questions out of Issues.
- `.github/DISCUSSION_TEMPLATE/ideas.yml`: a lightweight pre-issue mirror of
  `.github/ISSUE_TEMPLATE/primitive_proposal.md`. Asks whether the idea is core
  Layer 2, profile-specific, or tooling; whether composition was attempted;
  whether it is substrate-neutral. Links to the primitive-proposal issue and
  `docs/rfcs/0001-rfc-process.md`.
- `.github/DISCUSSION_TEMPLATE/builders-makers.yml`: asks whether the poster is
  a runtime author or a manufacturer and which substrate. Links to
  `docs/registry/SUBMISSION.md`, `docs/manufacturers/README.md`, and
  `conformance/`.

`General` and `Show and tell` deliberately get no form, so complaints, feedback,
and show-and-tell stay low-friction. `Announcements` needs none.

### Issue-to-discussion routing

`.github/ISSUE_TEMPLATE/config.yml` is added with `blank_issues_enabled: false`
and `contact_links` to Q&A, Ideas, General (complaints and posture critique),
Builders & Makers, and `SECURITY.md` for security and conduct concerns (which
stay private and never become a public thread). The three real issue templates
(bug report, feature request, primitive proposal) are unchanged. This config is
what actually routes "ask, Q&A, complaint, anything else" to Discussions and
keeps Issues scoped to bugs and the primitive funnel.

### Documentation

- `README.md`: the `## Engagement` section becomes `## Community & support`,
  linking the live categories by URL; a "Start here" row is added.
- `CONTRIBUTING.md`: line 18 (the now-false deferral) is rewritten to state that
  Discussions are open in Phase 0 and to describe the routing; the `## Questions`
  section points at Q&A in addition to the existing doc-bug-is-an-issue rule.
- `CODE_OF_CONDUCT.md`: "GitHub Discussions" is added to the enumerated URML
  spaces. This is a clarifying edit, permitted in a normal PR by that file's
  Changes section.
- `GOVERNANCE.md`: a note records that community Discussions are open in Phase 0,
  brought forward, citing this RFC. `GOVERNANCE.md` requires that its own
  changes be a small RFC; this RFC is that vehicle.

No response-time or service-level commitment is made anywhere in the templates,
the descriptions, or the documentation. Per the project's posture, public
commitments are made only with measured numbers behind them; none exist yet.

## Backward compatibility

Not applicable. No versioned specification or schema changes. The only reversal
is of prose in `CONTRIBUTING.md` and `GOVERNANCE.md`, which this RFC supersedes
by record.

## Drawbacks

Moderation and triage land on a single maintainer in Phase 0. An open Q&A
channel creates an implicit expectation of responsiveness even though no SLA is
promised; slow or absent answers on a public board read worse than a quiet
issue tracker. Some traffic that should be a bug report will arrive as a
discussion; the routing config mitigates this but does not eliminate it. These
are real costs accepted in exchange for lowering the barrier to adoption, with
the reversibility of the change as the backstop if the cost proves too high.

## Alternatives considered

**Keep deferring to Phase 1.** Rejected. The platform is already enabled, the
channel is reversible, and adoption is the moat the Manifesto tells us to
optimize for. Deferring a cheap, reversible adoption lever to protect a
process boundary is the wrong trade.

**An off-GitHub channel (Discord or Slack).** Rejected. It fragments the
decision history away from the repository, adds a third-party data-capture
surface the project explicitly refuses, and introduces a vendor the project
would have to vouch for. GitHub Discussions keeps the conversation next to the
code and the RFCs.

**Keep the six default categories unchanged.** Rejected. URML's audiences
(builders, runtime authors, manufacturers, the public) have distinct needs that
map onto existing funnels (the primitive-proposal issue, the runtime registry,
the manufacturer directory). Generic defaults would not route them and would
not connect Discussions to the funnels that already exist.

## Prior art

The `anthropics/skills` repository uses GitHub Discussions as its Q&A and
feedback surface, which is the model this RFC follows. Large open standards and
runtimes (Kubernetes, for example) run tailored Discussions categories
alongside an Issues tracker scoped to defects. Internally, the
`.github/ISSUE_TEMPLATE/primitive_proposal.md` funnel and RFC-0007's
documentary, no-normative-change pattern are the direct precedents this RFC
extends.

## Unresolved questions

The exact slug GitHub assigns to a new `Builders & Makers` category is assumed
to be `builders-makers`. It must be read back from the category URL after the
maintainer creates it; if GitHub assigns a different slug, the
`.github/DISCUSSION_TEMPLATE/` filename is renamed to match in the same PR,
otherwise the form does not bind.

## Implementation note

The maintainer first configures the six categories in the repository UI per the
taxonomy table and confirms the `Builders & Makers` slug. Then one PR, titled
`RFC-0008: community Discussions`, adds this RFC and its index row, the routing
config, the three category forms, and the documentation rewiring, and walks the
RFC state header Draft to Open to Accepted to Implemented. In Phase 0 the author
reviews their own work against the RFC-0001 self-review checklist; the PR is the
comment window. The change carries no CI or normative impact, so the rollback
plan is to revert the PR and remove the categories in the UI; no migration is
required.

## Self-review (Phase 0)

- [x] The Summary alone tells a reader what is being proposed.
- [x] The Motivation is grounded in a concrete gap (no async venue; misfiled
      issues; deferral now false because the platform is already enabled).
- [x] The Detailed design names every affected component and the manual UI step.
- [x] At least one alternative is genuinely considered (three are).
- [x] Drawbacks are listed; the solo-maintainer moderation load and the
      no-SLA expectation gap are real downsides, not humblebrags.
- [x] Backward compatibility is honest: no versioned artifact changes.
- [x] This RFC adds no Layer-2 primitive, so the substrate-neutrality sketch
      requirement does not apply.
- [x] The implementation note explains how this lands, including the manual
      category step and the revert path.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should
      Never Do: no user data or telemetry is gathered, no cloud dependency is
      introduced into any runtime, the channel is provider-neutral, and nothing
      in the Core Commitment moves. This proposal does not violate it.
