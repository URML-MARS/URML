---
rfc: 0003
title: Strategic Realignment — URML Aligns with US Federal Robotics Regulation
author: Ido Yahalomi (greenvh@gmail.com)
state: Accepted
created: 2026-05-13
updated: 2026-05-13
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

# RFC-0003: Strategic Realignment — URML Aligns with US Federal Robotics Regulation

## Summary

URML repositions from a jurisdictionally-neutral standard to one explicitly aligned with United States federal robotics and uncrewed-systems regulation. The reference frame includes (non-exhaustively) NDAA Section 889 and the FY26 NDAA expansions, the FCC Covered List, Executive Order 14307 ("Unleashing American Drone Dominance"), and the American Security Robotics Act once enacted. URML-compatible runtimes are expected to validate, by default, that a target robot's declared hardware provenance is consistent with these regulations. The validator ships with a default policy file encoding these rules; deployers outside the United States may override the default with their own jurisdiction-appropriate policy via a `--policy` flag.

This RFC is purely documentary. It amends [`MANIFESTO.md`](../../MANIFESTO.md), [`CLAUDE.md`](../../CLAUDE.md), and [`README.md`](../../README.md), and authorizes the creation of [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) with US-default-policy explicitly listed among the items that stay Apache-2.0-forever. The technical mechanism (provenance schema, policy DSL, validator Pass 5, default US policy file) is specified in the follow-up **RFC-0004: Compliance Policy Enforcement**, which this RFC authorizes but does not itself implement.

## Motivation

Between December 2025 and June 2026 the US federal regulatory environment for robotics moved from "incoming" to "enforced":

- **2025-12-23** — DJI and Autel were added to the FCC Covered List; new equipment authorizations for Chinese drones and critical components are blocked. ([FCC Covered List action](https://thehackernews.com/2025/12/fcc-bans-foreign-made-drones-and-key.html))
- **FY26 NDAA** — Procurement restrictions extended from the Department of Defense to *all* federal agencies, contractors, and federal-grant recipients. "NDAA-compliant" became a defined contracting term: no critical component (flight controller, radio, camera/gimbal, data storage, ground control, OS) manufactured or assembled by an entity in or controlled by China, Russia, Iran, or North Korea.
- **2026-06-30** — DoD prohibition on LiDAR with PRC-supply-chain ties takes effect; Hesai Technology is explicitly named. DoD contracts with listed Chinese Military Companies, or with firms lobbying for them, are barred.
- **2026-03** — Cotton/Schumer **American Security Robotics Act** introduced; companion in the House from Stefanik. Bipartisan federal procurement ban on Chinese-made unmanned ground vehicles and humanoid robots; Unitree explicitly cited. Activation one year after enactment.
- **Executive Order 14307** ("Unleashing American Drone Dominance") — Folds Green UAS into Blue UAS as the unified Department of Defense allow-list managed by the Defense Innovation Unit; ~50 platforms cleared as of early 2026.

The cumulative effect: any robot acquired with US federal funds — directly or as a grant pass-through — now must clear provenance restrictions that are statutorily enforced, growing monthly, and increasingly cross-domain (drones in 2025; ground robots and humanoids in 2026; LiDAR mid-2026).

URML the standard has two choices in this environment:

1. **Stay jurisdictionally neutral.** Ship a generic compliance mechanism; let users encode US rules (or any other jurisdiction's rules) themselves. This preserves global adoption potential but ships URML v0.1 without any built-in regulatory teeth.
2. **Align with US federal regulation.** Ship the mechanism *and* the US-federal rule set as the default. Deployers in other jurisdictions override via `--policy`. URML signals to US federal, defense, and federal-contractor procurement that it is the natural-language robot-intent layer of choice for their context.

The author has chosen option 2. Reasons, ordered:

- **First addressable market is US.** The largest near-term commercial surface for URML deployments is US federal and federal-adjacent procurement (defense, public-safety, infrastructure). A standard that requires deployers to write their own NDAA-compliance enforcement is friction at exactly the moment URML needs to be picked up.
- **Regulatory drift forces a position anyway.** A "neutral" standard whose canonical examples and reference deployments happen to satisfy US rules is *de facto* US-aligned but rhetorically dishonest about it. Aligning explicitly is more honest and easier to defend.
- **Override remains free.** Non-US deployers pay one CLI flag (`--policy their_file.yaml`). The cost of being non-default is low; the cost of having no default at all is high.

The author acknowledges this contradicts the geographic-neutrality clause in `MANIFESTO.md` as written, and has weighed the trade-offs (see *Drawbacks*).

## Detailed design

This RFC ratifies amendments to four documents and the creation of one new document.

### Spec changes

#### MANIFESTO.md

**Remove** the paragraph in "Strategic Posture" / "Geographic neutrality matters" (and any parallel passages in scope sections) asserting jurisdictional neutrality of the eventual foundation.

**Add** a new section titled **"Jurisdictional Alignment"** after "What URML Is Not":

> URML aligns with United States federal robotics and uncrewed-systems regulation as its primary regulatory frame of reference, including (non-exhaustively) NDAA Section 889 and FY26 procurement restrictions, the FCC Covered List, Executive Order 14307, and the American Security Robotics Act once enacted. URML-compatible runtimes validate, by default, that a target robot's declared hardware provenance is consistent with these regulations. Deployers outside the United States may override the default policy with their own jurisdiction-appropriate rule set; URML supplies the mechanism, but the default ships pre-loaded with US federal procurement rules.
>
> The natural-language layer remains multilingual. End users in any country, speaking any language, interact with URML through their own words. The *regulatory frame* is US-federal; the *user interface* is not.
>
> This is a v0.x positioning decision. Major-version increments may revisit it; see RFC-0003 for the reasoning and the trade-offs accepted.

**Edit** "Why Now" — add a fourth-or-fifth bullet (placement at the author's discretion):

> **The regulatory window is now too.** The US federal regulatory cascade between Dec 2025 and June 2026 (FCC Covered List enforcement, FY26 NDAA expansion, DoD LiDAR restrictions, the American Security Robotics Act) defines a default rule set URML can encode and ship. A standard that materializes alongside the regulation it serves accelerates both.

**Edit** "Design Principles" — append to the `Substrate-agnostic` rationale text:

> Substrate-agnosticism is preserved as an architectural principle. Jurisdictional-agnosticism is not: URML's default regulatory frame is US-federal (see "Jurisdictional Alignment"), with overrides available for non-US deployments.

**Edit** Appendix B "Open Questions" — close question (6) on Hebrew localization with a note:

> Resolved. The natural-language testing matrix in v0.1 includes English and Hebrew, with Spanish, Japanese, and Mandarin in v1.x per the existing roadmap. The regulatory-frame question (separate from localization) is resolved by RFC-0003 in favor of US-federal alignment.

#### CLAUDE.md

**Rewrite** the "Geographic neutrality matters" paragraph in the Strategic Posture section. New text:

> **Regulatory alignment is US-federal.** Default provenance and procurement rules embedded in the standard reflect United States statutory and executive frameworks. Documentation remains English-first and the natural-language layer remains multilingual, because end users speak many languages even when the regulatory frame is one country's. Avoid choices that would *additionally* couple URML to a single US vendor, a single US agency, or a single US administration's policy interpretation; the alignment is to enacted law, not to politics.

**Edit** the "Structural separation is coming" paragraph — replace `jurisdictionally neutral` with `US-domiciled and aligned with US federal law`. The DCO-over-CLA guidance is unchanged.

**Edit** "What Claude Should Never Do" — remove the implicit ban on jurisdiction-specific defaults (any wording suggesting URML must remain framework-agnostic on regulation), and add:

> - Never embed a specific US administration's executive-order interpretation in default rules; track enacted statutes, final FCC Covered List entries, and final DoD rules — not draft guidance, not pending bills, not executive-order interpretive memos.

#### README.md

**Add** a one-paragraph "Regulatory alignment" callout above (or immediately following) the existing project description:

> **Regulatory alignment.** URML's default validator policy aligns with United States federal robotics and uncrewed-systems regulation (NDAA Section 889 / FY26, FCC Covered List, EO 14307). Deployments outside the US may override the default via `urml validate --policy <file.yaml>`. See RFC-0003 for the rationale and RFC-0004 for the mechanism.

### Validator changes

This RFC mandates no validator behavior changes by itself. RFC-0004 specifies the provenance schema, policy DSL, default policy file, validator Pass 5, and CLI flags. RFC-0003 authorizes the work; RFC-0004 designs it.

### Reference runtime changes

None directly. The ROS 2 reference runtime passes the manifest dict through to the validator and does not parse it locally; the policy enforcement happens at validation time, before any program reaches a runtime. Runtimes are unaffected by RFC-0003.

### Conformance suite changes

None directly. RFC-0004 will add conformance fixtures exercising the default policy and the override mechanism.

### Core Commitment

This RFC authorizes the creation of [`CORE_COMMITMENT.md`](../../CORE_COMMITMENT.md) at the repository root (the file is referenced by both `README.md` and `0001-rfc-process.md` but has not yet been written). `CORE_COMMITMENT.md` shall enumerate the artifacts that remain Apache-2.0-forever, including:

- The specification documents (all layers and profiles).
- The conformance test suite.
- The ROS 2 and PX4 reference runtimes.
- The validator.
- The LLM prompt contract.
- **The default US-federal policy file** (added by this RFC).

The Core Commitment lists what cannot be moved behind a paywall or conditional license. Adding the default policy file to that list ensures URML's regulatory teeth are public goods — a commercial entity (URML's or a third party's) may sell *audited* or *certification-grade* policy files, but the freely-readable default cannot become a paid feature.

## Backward compatibility

URML has no released specification. The pre-v0.1 manifesto and CLAUDE.md draft are not normative artifacts that downstream users depend on. Editing them is non-breaking by definition.

There are two artifacts that *do* depend on the prior framing:

1. **RFC-0002 (Initial Layer-2 Primitive Vocabulary, Draft).** RFC-0002 references `CLAUDE.md`'s prior posture in passing but does not depend on jurisdictional-neutrality language. No change required.
2. **External communications (none yet).** The manifesto has not been publicly announced. There is no community of contributors who joined under the prior framing whose expectations are broken. This is the optimal moment to make this change; any later is harder.

The RFC is honest about what it *does* foreclose, which is a future option rather than a past commitment: see *Drawbacks* §1.

## Drawbacks

1. **The decision is a one-way door for v0.x.** Any non-US adopter who reads `MANIFESTO.md` after this RFC sees explicit US alignment. Recovery requires a v1.0 manifesto rewrite plus a multi-year community-signaling effort. This is the largest cost and is unrecoverable on a Phase-0 timescale.

2. **EU adopters governed by the AI Act (Aug 2, 2026 deadline) will see a US-aligned standard as a poor fit.** The AI Act creates its own conformity-assessment regime — CE marking, EU database registration, third-party assessment for high-risk AI systems including AI systems operating robots. A US-aligned URML can be made AI-Act-compliant via a `--policy eu_ai_act.yaml` override, but the optics of "the default is the other side of the Atlantic" are bad for EU procurement.

3. **Non-aligned-Asia and BRICS-adjacent markets are foreclosed for the foreseeable future.** Japan and Korea may adopt; China and Russia will not, by definition; India's posture is uncertain and a US-aligned default will not help. This narrows total adoption surface relative to a neutral standard.

4. **The eventual foundation cannot credibly be jurisdictionally neutral.** Expect a US-based 501(c)(6) or similar industry association, not a Linux-Foundation-style global body. This caps the kind of cross-border governance URML can offer.

5. **Compliance theater risk.** A policy file passing the validator is not a legal compliance determination. The shipped default must carry a clear "not legal advice" banner; the spec text must say so. This is straightforward but easy to forget.

6. **Tracking churn.** US federal robotics regulation changes monthly (FCC Covered List grows; American Security Robotics Act may pass or stall; DoD Chinese-Military-Companies list updates quarterly). The default policy file becomes a maintenance burden requiring at least monthly review and an explicit owner.

7. **Vendor-name brittleness.** The default policy will name specific vendors (DJI, Autel, Hesai, Unitree) — all real companies, all on actual US federal lists. Defamation risk is low (they are named in enacted regulation, not speculation) but non-zero; the policy file must cite its statutory sources inline.

8. **Provenance declarations create paper trails.** A robot maker who self-declares `country_of_origin: US` and is later proven wrong has created a discoverable false attestation. The `manifest_attestation` field exists to surface attestation strength; the default policy warns on `self_declared` rather than accepting it silently. URML's role is to *record* the declaration, not to *certify* it.

## Alternatives considered

1. **Stay jurisdictionally neutral; ship a mechanism only.** Ship the provenance schema and the policy DSL; ship *no* default policy. Deployers in any jurisdiction supply their own rule file. **Rejected** for the reasons in *Motivation*: this preserves the option to expand later but ships URML v0.1 without regulatory teeth at exactly the moment the US regulatory cascade defines a clear default. The optionality is real but the cost of being optional is also real — and US federal procurement officers do not pick standards that require them to write their own compliance code.

2. **Stay neutral but ship *example* US, EU, and IL policy files in `/examples/policies/`.** The middle path. **Rejected** as a stable position but kept as a fallback if RFC-0003 is contentious during the comment window: ship the examples *and* the default loaded automatically. The reason the middle path is not chosen as the primary is that "example-but-default" is the worst of both worlds — non-US deployers face the same friction as in option (1), but URML the standard avoids saying out loud what its default actually does. Honesty matters more than optionality here.

3. **Ship multiple defaults — load whichever matches an environment variable (`URML_JURISDICTION=US|EU|IL|...`).** The "multi-default" path. **Rejected** because (a) it pushes the regulatory-frame choice onto a deployer who likely does not understand the differences, and (b) it makes URML's testing surface combinatorial against jurisdictions before any rule set has been audited. Better to have one default everyone understands and override as needed.

4. **Defer the entire regulatory question to a v0.2 or v1.0 RFC.** The "punt" path. **Rejected** because the regulatory cascade is *happening now*; v0.1 ships into the environment that exists in mid-2026, not the one that existed in 2024. A standard that does not address the regulatory frame deployers actually face is a standard deployers ignore.

## Prior art

- **Kubernetes** is the cleanest counter-example: a global standard governed by the Cloud Native Computing Foundation (Linux Foundation umbrella) that explicitly does *not* ship US-federal-procurement rules in the core. URML deliberately diverges. Reason: Kubernetes is operationally neutral (it runs on any cloud); robotics deployments are not (the hardware physically exists in one jurisdiction at a time, and that jurisdiction's procurement rules dominate).
- **Blue UAS / Green UAS (DoD / Defense Innovation Unit)** — A federally-managed allow-list of NDAA-compliant drones. URML's default policy is in the same spirit but is a *rule expression*, not a *device list*: rather than enumerate which robots URML accepts, URML accepts any robot whose declared provenance satisfies the rule expression. The Blue UAS list itself may become a useful comparison source for default-policy validation.
- **NIST Cybersecurity Framework** — A US-government-anchored standard that has nevertheless been adopted internationally. Evidence that "US-anchored" and "globally useful" are not mutually exclusive for technical standards. URML bets on this pattern.
- **OWASP CycloneDX 1.7 Hardware Bill of Materials (HBOM)** — The lingua franca for hardware provenance attestations as of 2025. RFC-0004 will point at CycloneDX 1.7 as the recommended HBOM format without making it normative.
- **The EU AI Act** — The parallel regulatory regime URML's default will *not* match by default. RFC-0004 will ship an example `eu_ai_act_override.yaml` policy file in `examples/policies/` to make the override path concrete.
- **Section 889 / FAR 4.21** — The statutory anchor for the FY20 NDAA covered-foreign-entity rules and the FCC Covered List. The default URML policy will trace its rules to these citations.

## Unresolved questions

1. **Foundation domicile and structure.** The manifesto's prior framing assumed a future Linux-Foundation-style global body. With US alignment baked in, the realistic targets are US-domiciled industry associations (501(c)(6)), an SDO with strong US ties (IEEE-SA, INCITS), or a sponsored project under an existing US-domiciled foundation (Open Source Security Foundation, Cloud Native Computing Foundation). Resolved before any commercial entity is incorporated, not in this RFC.

2. **The DCO-vs-CLA question is unchanged.** This RFC does not affect contributor-licensing posture; DCO sign-off remains the policy.

3. **Does RFC-0003 trigger a re-vote on RFC-0002 (Initial Layer-2 Primitive Vocabulary, currently Draft)?** Recommended: no. RFC-0002 is jurisdictionally agnostic and does not need a re-review under the new frame. The author confirms this in the self-review checklist below.

4. **Naming of the default policy file.** Working name in RFC-0004: `us_federal_default.yaml`. Alternatives: `us_ndaa_default.yaml` (specific to one statute), `us_default.yaml` (under-specifies), `default.yaml` (over-claims neutrality). Final choice in RFC-0004.

5. **Comment-window precedent.** This is the first RFC to invoke the 30-day window per `0001-rfc-process.md` §Comment window for changes touching the Core Commitment. The author proceeds in good faith; the 30-day window in Phase 0 solo is symbolic but its existence is the load-bearing thing — future committee work needs the precedent.

## Implementation note

This RFC is purely documentary. Its **Accepted** state ratifies a set of edits to four documents and authorizes the creation of one new document. Its **Implemented** state is reached when the following land:

1. **PR-0** — this RFC file at `docs/rfcs/0003-us-alignment.md`. State **Draft** on creation; advanced to **Open** when the author considers it ready for the comment window; advanced to **Accepted** at or after day 30 of the window.
2. **PR-0.5** — `CORE_COMMITMENT.md` created at the repository root, enumerating the items listed in *Detailed Design § Core Commitment*. May be a separate PR or bundled with PR-0; either is acceptable. Bundled is faster; separate is cleaner for review.
3. **PR-0.6** — Edits to `MANIFESTO.md`, `CLAUDE.md`, and `README.md` per *Detailed Design § Spec changes*. Lands only after RFC-0003 reaches **Accepted**.

Comment window: **30 days** from advance-to-Open per `0001-rfc-process.md` (any RFC touching the Core Commitment requires the 30-day window; this RFC creates the Core Commitment, so it triggers the window). Phase-0-solo: the window is symbolic but observed for precedent.

The technical implementation that depends on this RFC — provenance schema, policy DSL, validator Pass 5, default policy file, conformance fixtures — is specified in **RFC-0004: Compliance Policy Enforcement**, written separately and gating its own implementation PRs.

## Self-review (Phase 0)

The author has reviewed against the checklist in [`0001-rfc-process.md`](0001-rfc-process.md) §Self-review:

- [x] The **Summary** alone tells a reader what is being proposed.
- [x] The **Motivation** is grounded in concrete external events (FCC Covered List enforcement, FY26 NDAA, EO 14307, American Security Robotics Act) with citations, not in hypothetical needs.
- [x] The **Detailed design** names every affected spec document (`MANIFESTO.md`, `CLAUDE.md`, `README.md`, `CORE_COMMITMENT.md`) and explicitly defers technical mechanism to RFC-0004.
- [x] At least one **alternative** is genuinely considered (four alternatives are documented; one is honestly noted as a fallback if the primary is contentious).
- [x] **Drawbacks** lists at least one real downside; eight are listed, and the first is identified as the largest cost and unrecoverable on Phase-0 timescales.
- [x] **Backward compatibility** is honest about what breaks: nothing released is broken; one future option is foreclosed, and that is named as the largest drawback.
- [x] **Substrate-neutrality acid test** is N/A: this RFC adds no Layer-2 primitive. The technical-mechanism RFC (RFC-0004) will satisfy the acid test on its own.
- [x] The **implementation note** explains how this lands (three PRs, sequencing, comment-window observance), not just what.
- [x] The author has re-read [`CLAUDE.md`](../../CLAUDE.md) §What Claude Should Never Do. This RFC modifies the *content* of §What Claude Should Never Do — specifically the geographic-neutrality assertion — but does so via the documented amendment path (an RFC that explicitly proposes the change), not by silent contradiction. The author confirms the procedural integrity of the amendment.
