---
rfc: 0007
title: "Manufacturer Go-To-Market: URML as an Opportunity and a Channel for Robot OEMs and Component Makers"
author: Ido Yahalomi (greenvh@gmail.com)
state: Draft
created: 2026-05-16
updated: 2026-05-16
supersedes: —
superseded-by: —
---

# RFC-0007: Manufacturer Go-To-Market: URML as an Opportunity and a Channel for Robot OEMs and Component Makers

## Summary

URML adds a manufacturer-facing on-ramp, led by full-robot OEMs and followed by parts and component makers. Today the only adopter entry point is the Compatible Runtimes registry, which serves runtime authors translating URML to a substrate. A robot manufacturer who wants to position a product around URML, or show federal-procurement readiness, has nowhere to land. This RFC ratifies a small set of documentation amendments and authorizes four new manufacturer docs, a self-reported manufacturer/products directory, a new PR template, and a dispatch-workflow trigger. It is purely documentary. It proposes no spec, validator, runtime, or conformance change, and no change to `CORE_COMMITMENT.md` or any artifact it lists. The federal-readiness asset is a *factual, self-reported* statement that a manifest validates clean under the open default policy at a pinned commit. It is explicitly not a certification, an audit, or an endorsement, and the paid `URML-Certified` program remains a separate Phase-4 commercial surface untouched by this RFC.

## Motivation

RFC-0003 and RFC-0004 gave URML regulatory teeth: a bundled US-federal default policy and a validator pass that enforces it before any actuator moves. That work created a concrete reason for a specific audience to care about URML now, and that audience is not currently addressed.

A robot manufacturer's product and business-development function parses an open standard through three lenses: a recognizable trust signal it can put on a product, a channel that routes buyers to it, and co-marketing it can borrow credibility from. URML maps to none of these today:

- The Compatible Runtimes registry (`docs/compatible-runtimes.md`) is for *runtime authors*, not robot makers. Different audience, different claim, different columns. A turtlebot OEM does not "translate URML to a substrate"; it ships a robot whose capability manifest can be validated under URML.
- There is no place for a manufacturer to make the one factual statement that is most valuable in the post-RFC-0003 environment: "our product's manifest validates clean under URML's open US-federal default policy." RFC-0003 §Motivation already establishes that US federal and federal-adjacent procurement is URML's first addressable market. The manufacturer is the party that has to demonstrate that readiness, and URML gives them no artifact to do it with.
- Component and parts makers (actuators, sensors, compute modules) sit a layer below URML and have no guidance on how to document a part so an OEM can drop it into a URML `provenance:` block cleanly.

The status quo leaves the most motivated near-term adopters with no on-ramp at exactly the moment the regulatory cascade described in RFC-0003 makes URML relevant to them.

## Detailed design

This RFC follows the RFC-0003 pattern: it ratifies amendments to existing documents and authorizes follow-up documentation. It designs no mechanism.

### Spec changes

None. This RFC changes no Layer-1/2/3/4 specification, no schema, no grammar, and no profile. It is documentary and strategic, in the mold of RFC-0003.

### Validator changes

None. The federal-readiness self-report is produced by the existing `urml validate` CLI run with the bundled default policy (no `--policy`, no `--no-policy`), exactly as the compliance walkthrough already demonstrates. No new flag, no new output mode, no new schema. If implementation finds the existing CLI cannot express a manifest-scoped pass result suitable for a self-report without an affordance, that is recorded as an unresolved question and deferred to a separate future RFC; it is not designed here.

### Reference runtime changes

None.

### Conformance suite changes

None.

### Documents amended (ratified by this RFC)

- **`README.md`**: add two rows to the "Start here" table ("Position a robot for URML and federal-procurement readiness" → `docs/manufacturers/README.md`; "List a robot or product in the manufacturer directory" → `docs/manufacturers/SUBMISSION.md`) and one short pointer near the existing "Compatible Runtimes" section distinguishing the runtime registry (runtime authors) from the manufacturer directory (robot and product makers).
- **`GOVERNANCE.md`**: add a "Manufacturer Directory Maintenance" subsection mirroring the existing "Default Compliance Policy Maintenance" subsection: owner is the sole maintainer in Phase 0, the directory is self-reported, the maintainer reviews PRs for completeness and not for fitness, and the role delegates to the steering committee in Phase 1+.
- **`TRADEMARK.md`**: extend "What anyone can do" and "What listing in the registry does not grant" to cover the manufacturer directory and the exact permitted federal-readiness phrasing, and restate that `URML-Certified` stays off limits and the directory grants no mark. This is a clarification within the existing stub, not a change to mark categories; the full Phase-4 policy is unaffected.
- **`docs/compatible-runtimes.md`**: add one reciprocal cross-link line pointing readers who make robots (rather than runtimes) to the manufacturer directory.

### Documents authorized as follow-up (created, not ratified inline)

Created in the implementation PR after this RFC reaches Accepted:

- `docs/manufacturers/README.md`: manufacturer landing doc. Sections: positioning (OEMs first, components second); an ordered integration path that points at existing assets (`bootstrap.py`, `urml init`, Tutorial 4 including its provenance exercise, the per-profile example manifests, the federal self-report convention, the directory submission) without duplicating them; a secondary "for component makers" section on documenting a part for clean drop-in to a `provenance:` block; and a "Launch partners (Phase 0)" section that is documented intent plus a free directory listing only, with no paid program, mark, fee, SLA, or contact capture.
- `docs/manufacturers/FEDERAL-VALIDATION-SELF-REPORT.md`: the copy-into-your-own-repo template defining a `URML-FEDERAL-VALIDATION.md` file, mirroring the runtime-author `CONFORMANCE.md` + pinned-commit convention. States precisely what the published claim may say and a bold must-not list, and embeds a verbatim "not a legal compliance determination" disclaimer reusing the language already in the `us_federal_default.yaml` header.
- `docs/manufacturers/directory.md`: the self-reported manufacturer/products directory, separate from and cross-linked to the runtime registry.
- `docs/manufacturers/SUBMISSION.md`: the submission flow, mirroring `docs/registry/SUBMISSION.md`.
- `.github/PULL_REQUEST_TEMPLATE/manufacturer-listing.md`: a fielded PR template mirroring `registry-submission.md`, with a trademark acknowledgement extended to cover the federal-readiness phrasing.
- `.github/workflows/dispatch-to-website.yml`: the four `docs/manufacturers/*.md` published files added to the existing `paths:` trigger; no new event type.

### Out of scope / stays commercial

This RFC deliberately does not touch, and explicitly forecloses building in this repository, the following. Each is named so the boundary is auditable:

- The paid `URML-Certified` mark and the certification *program* (`CORE_COMMITMENT.md` §"What This Commitment Does Not Cover"; `TRADEMARK.md` §"What is off limits"). Not built, not sold, not implied.
- Any grant or license of the URML or `URML-Certified` marks beyond the factual-descriptor use already defined in `TRADEMARK.md`.
- Audited or certification-grade policy files and the third-party legal attestations that back them (`CORE_COMMITMENT.md`; `us_federal_default.yaml` header). The federal self-report is uncertified and self-reported only.
- Any claim that passing `us_federal_default.yaml` means "URML-Certified", "NDAA compliant", "certified", "audited", or "approved for federal procurement". RFC-0004 §Unresolved questions item 6 forbids it; the self-report template hard-codes the disallowed phrasings.
- Hosted lead generation, directory-traffic analytics, contact capture, conversion tracking, paid placement, response-time SLAs, and fees. These are out-of-repo and commercial, and any public commitment about them is gated on measured numbers, not promised here.
- Elevating the steward organization to a parent brand. URML remains the face.

## Backward compatibility

Nothing is released and no community joined under a prior manufacturer framing, so there is nothing to break. All in-repo changes are additive documentation plus one workflow `paths:` addition and one new PR template. No specification artifact changes, so no prior URML version is affected.

## Drawbacks

1. **Overclaim risk.** A self-reported federal-readiness statement with no audit invites a manufacturer, or a reader, to round "validates clean under the open default policy" up to "URML-certified NDAA compliant." This is the largest risk. Mitigation is a mandatory factual-phrasing template with a bold must-not list, a hard-coded disclaimer reused from the policy header, and a `TRADEMARK.md` restatement. The risk is reduced, not eliminated; a determined misquoter can still misquote.
2. **Solo maintenance burden.** A manufacturer directory carries the same staleness and delisting cost as the runtime registry, on the same one person, with no new tooling.
3. **Endorsement optics.** A directory listing specific vendors can read as URML endorsing them, the same tension the runtime registry already manages. Mitigation reuses the runtime registry's "factual record of submission, not endorsement" language verbatim.
4. **Perceived compliance assurance.** Publishing a federal-readiness on-ramp at all risks URML being perceived as offering a compliance assurance it explicitly disclaims, in a domain (federal procurement) where the stakes of that misperception are high.

## Alternatives considered

1. **Merge manufacturers into the existing `compatible-runtimes.md` registry.** Rejected: it conflates two different audiences (runtime authors vs. robot makers) and two different claims (translates URML to a substrate vs. ships a product whose manifest validates), with different columns. The registry's clarity is load-bearing and worth keeping.
2. **Positioning doc only; no directory.** Rejected: a channel needs a listable, browsable surface. A positioning page with no directory is the "watch-list item" outcome this RFC exists to avoid.
3. **Build the paid launch-partner / certification-eligibility program now.** Rejected: a Phase-4 commercial surface and a `CORE_COMMITMENT.md` boundary violation. Out of scope by construction.
4. **Defer entirely to Phase 1.** Rejected: the regulatory window RFC-0003 identifies is open now, and the federal-readiness wedge is most valuable while the cascade is fresh. Deferring forfeits the timing advantage that motivated RFC-0003.

## Prior art

- **URML RFC-0003** is the direct precedent: a purely documentary, strategy RFC that amends documents and authorizes follow-up work without designing a mechanism. RFC-0007 copies that shape deliberately, including the explicit Spec/Validator/Runtime/Conformance "None" subsections.
- **The Compatible Runtimes registry plus the `CONFORMANCE.md` self-report convention** (`docs/registry/SUBMISSION.md`, `.github/PULL_REQUEST_TEMPLATE/registry-submission.md`). The manufacturer directory, submission flow, and PR template are deliberately near-clones so the project has one self-report pattern, not two.
- **Blue UAS / Green UAS** as the contrast (see RFC-0003 §Prior art). URML's federal self-report is a *factual statement about a rule-expression result*, not membership in a government allow-list. The distinction is the point: URML records a declaration, it does not certify it.
- **CNCF Certified Service Provider / the CNCF landscape** as the directory-shape prior art that URML deliberately keeps free, self-reported, and uncertified, with the paid certification surface separated out (Phase 4).

## Unresolved questions

1. **Comment window.** This RFC takes the standard window per RFC-0001, not the 30-day Core-Commitment window, because it proposes no change to `CORE_COMMITMENT.md` or any of its seven listed artifacts. The 30-day precedent (RFC-0003) is deliberately not invoked. If review surfaces any edit that touches the Commitment, the window converts to 30 days and this RFC is re-opened.
2. **Federal self-report affordance.** Whether `urml validate` exit-0 on a manifest with a `provenance:` block is, on its own, a clean enough artifact for a self-report, or whether a manifest-scoped summary affordance is eventually wanted. If wanted, it is a separate future RFC, not designed here.
3. **Directory delisting cadence.** Whether the manufacturer directory should reuse the runtime registry's 90-day post-spec-bump staleness window unchanged. Current answer: yes, for one consistent rule.
4. **Maintenance role split.** Whether the manufacturer directory eventually needs a maintainer role separate from the default-policy maintainer. Deferred to the Phase 1+ governance transition.

## Implementation note

Two PRs, in order, matching the RFC-0003 sequencing discipline.

1. **PR-1**: this RFC file at `docs/rfcs/0007-manufacturer-go-to-market.md`, plus the `docs/rfcs/README.md` index row, in one PR. State **Draft** on creation, advanced to **Open** when the author considers it ready, advanced to **Accepted** at or after the close of the standard comment window. No other files in this PR.
2. **PR-2**: the authorized follow-up, landing only after this RFC reaches **Accepted**: the four `docs/manufacturers/*.md` files, `.github/PULL_REQUEST_TEMPLATE/manufacturer-listing.md`, the `dispatch-to-website.yml` `paths:` addition, and the ratified amendments to `README.md`, `GOVERNANCE.md`, `TRADEMARK.md`, and `docs/compatible-runtimes.md`. This RFC advances to **Implemented** and the index row updates in the same PR. Rollback is reverting the one squash commit; the workflow path additions are inert without the docs and no code path changes.

Comment window: the standard window per [`0001-rfc-process.md`](0001-rfc-process.md). Not the 30-day Core-Commitment window, for the reason in Unresolved questions §1. Phase-0-solo: the window is observed for precedent.

## Self-review (Phase 0)

The author has reviewed against the checklist in [`0001-rfc-process.md`](0001-rfc-process.md) §Self-review:

- [x] The **Summary** alone tells a reader what is being proposed: a documentary RFC adding a manufacturer on-ramp (positioning, a self-reported directory, a factual federal-readiness self-report), with the paid program explicitly out of scope.
- [x] The **Motivation** is grounded in a concrete situation, not a hypothetical: RFC-0003/0004 created a federal-readiness audience, and the only existing adopter entry point (the runtime registry) does not serve it.
- [x] The **Detailed design** names every affected document (`README.md`, `GOVERNANCE.md`, `TRADEMARK.md`, `docs/compatible-runtimes.md`) and every authorized follow-up file, and states "None" with a reason for each of Spec / Validator / Runtime / Conformance.
- [x] At least one **alternative** is genuinely considered: four are, including the rejected "merge into the runtime registry" and the boundary-violating "build the paid program now."
- [x] **Drawbacks** lists at least one real downside: overclaim risk is named as the largest, with an honest statement that mitigation reduces rather than eliminates it.
- [x] **Backward compatibility** is honest: nothing released, additive only, no spec artifact changes.
- [x] **Substrate-neutrality acid test** is N/A: this RFC adds no Layer-2 primitive. Stated here per the checklist.
- [x] The **implementation note** explains how this lands (two PRs, sequencing, state transitions, rollback), not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What This Project Is and §What Claude Should Never Do, and confirms this RFC introduces no commercial feature, no paid mark, no audited attestation, no telemetry or lead-gen, no out-of-canonical-scope content, and no modification to `CORE_COMMITMENT.md` or any artifact it lists. The 7 committed artifacts are untouched, which is why the standard comment window applies.
